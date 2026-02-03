import { useState, useEffect, useCallback } from 'react';
import { summaryService } from '../services/api';
import { SummaryProgressResponse } from '../types';

interface UseProgressOptions {
  summaryId: string;
  enabled?: boolean;
  pollInterval?: number; // in milliseconds
  onComplete?: () => void;
  onError?: (error: string) => void;
}

export const useProgress = ({
  summaryId,
  enabled = true,
  pollInterval = 2000,
  onComplete,
  onError
}: UseProgressOptions) => {
  const [progress, setProgress] = useState<SummaryProgressResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProgress = useCallback(async () => {
    if (!enabled) return;

    setLoading(true);
    setError(null);

    try {
      const data = await summaryService.getSummaryProgress(summaryId);
      setProgress(data);

      // Handle completion
      if (data.status === 'completed' && onComplete) {
        onComplete();
      }

      // Handle error
      if (data.status === 'failed' && onError && data.error_message) {
        onError(data.error_message);
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to fetch progress';
      setError(errorMsg);
      if (onError) {
        onError(errorMsg);
      }
    } finally {
      setLoading(false);
    }
  }, [summaryId, enabled, onComplete, onError]);

  useEffect(() => {
    if (!enabled) return;

    // Initial fetch
    fetchProgress();

    // Only poll if status is processing
    const interval = setInterval(() => {
      if (progress?.status === 'processing') {
        fetchProgress();
      }
    }, pollInterval);

    return () => clearInterval(interval);
  }, [summaryId, enabled, pollInterval, progress?.status, fetchProgress]);

  return {
    progress,
    loading,
    error,
    refetch: fetchProgress
  };
};

export default useProgress;
