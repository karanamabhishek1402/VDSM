import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { summaryService } from '../services/api';
import { Summary } from '../types';
import SummaryPlayer from '../components/SummaryPlayer';
import Loading from '../components/Loading';
import { useProgress } from '../hooks/useProgress';

const SummaryDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [summary, setSummary] = useState<Summary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Use progress hook for real-time updates if processing
  const { progress } = useProgress({
    summaryId: id || '',
    enabled: summary?.status === 'processing',
    onComplete: () => {
      // Refresh summary data when complete
      if (id) {
        fetchSummaryData(id);
      }
    }
  });

  useEffect(() => {
    if (id) {
      fetchSummaryData(id);
    }
  }, [id]);

  const fetchSummaryData = async (summaryId: string) => {
    try {
      setLoading(true);
      const summaryData = await summaryService.getSummaryById(summaryId);
      setSummary(summaryData);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load summary or you don't have permission to view it.");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = () => {
    navigate('/dashboard');
  };

  if (loading) {
    return <Loading />;
  }

  if (error || !summary) {
    return (
      <div className="max-w-4xl mx-auto py-12 px-4 text-center">
        <p className="text-red-500 mb-4">{error || "Summary not found"}</p>
        <button 
          onClick={() => navigate('/dashboard')}
          className="text-blue-600 font-medium hover:underline"
        >
          Return to Dashboard
        </button>
      </div>
    );
  }

  // Show processing state
  if (summary.status === 'processing') {
    return (
      <div className="max-w-4xl mx-auto py-12 px-4">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold mb-4">{summary.title}</h2>
          <div className="mb-6">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Processing your summary...</span>
              <span>{progress?.progress_percent || summary.progress_percent}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                style={{ width: `${progress?.progress_percent || summary.progress_percent}%` }}
              ></div>
            </div>
          </div>
          <p className="text-gray-600 mb-4">
            This may take several minutes depending on video length. You can safely leave this page and come back later.
          </p>
          <button
            onClick={() => navigate(`/videos/${summary.video_id}`)}
            className="text-blue-600 hover:text-blue-800"
          >
            ← Back to video
          </button>
        </div>
      </div>
    );
  }

  // Show failed state
  if (summary.status === 'failed') {
    return (
      <div className="max-w-4xl mx-auto py-12 px-4">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold mb-4 text-red-600">Summary Failed</h2>
          <p className="text-gray-600 mb-4">{summary.title}</p>
          {summary.error_message && (
            <div className="bg-red-50 border border-red-200 rounded p-4 mb-6">
              <p className="text-red-700">{summary.error_message}</p>
            </div>
          )}
          <div className="flex space-x-4">
            <button
              onClick={() => navigate(`/videos/${summary.video_id}`)}
              className="text-blue-600 hover:text-blue-800"
            >
              ← Back to video
            </button>
            <button
              onClick={() => summaryService.deleteSummary(summary.id).then(handleDelete)}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Delete Summary
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Show completed summary
  return (
    <div className="max-w-6xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <SummaryPlayer summary={summary} onDelete={handleDelete} />
    </div>
  );
};

export default SummaryDetail;
