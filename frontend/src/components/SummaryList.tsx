import React, { useState, useEffect } from 'react';
import { Summary } from '../types';
import { summaryService } from '../services/api';
import { Link } from 'react-router-dom';

interface SummaryListProps {
  videoId: string;
  refreshTrigger?: number; // Increment this to force refresh
}

const SummaryList: React.FC<SummaryListProps> = ({ videoId, refreshTrigger }) => {
  const [summaries, setSummaries] = useState<Summary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    loadSummaries();
  }, [videoId, refreshTrigger]);

  useEffect(() => {
    // Poll for progress updates on processing summaries
    const interval = setInterval(() => {
      const processingSummaries = summaries.filter(s => s.status === 'processing');
      if (processingSummaries.length > 0) {
        loadSummaries();
      }
    }, 3000); // Poll every 3 seconds

    return () => clearInterval(interval);
  }, [summaries]);

  const loadSummaries = async () => {
    try {
      setError(null);
      const data = await summaryService.getSummaries(videoId);
      setSummaries(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load summaries');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (summaryId: string) => {
    if (!window.confirm('Are you sure you want to delete this summary?')) {
      return;
    }

    setDeletingId(summaryId);
    try {
      await summaryService.deleteSummary(summaryId);
      setSummaries(summaries.filter(s => s.id !== summaryId));
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete summary');
    } finally {
      setDeletingId(null);
    }
  };

  const handleDownload = (summaryId: string) => {
    summaryService.downloadSummary(summaryId);
  };

  const getStatusBadge = (status: string) => {
    const styles = {
      processing: 'bg-yellow-100 text-yellow-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800'
    };
    return styles[status as keyof typeof styles] || 'bg-gray-100 text-gray-800';
  };

  const getRequestTypeLabel = (requestType: string) => {
    const labels = {
      'text-prompt': 'Text Prompt',
      'category': 'Category',
      'time-range': 'Time Range'
    };
    return labels[requestType as keyof typeof labels] || requestType;
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return 'N/A';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return 'N/A';
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(2)} MB`;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  if (summaries.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p className="text-lg">No summaries yet</p>
        <p className="text-sm mt-2">Create your first summary using the form above</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-xl font-bold mb-4">Video Summaries ({summaries.length})</h3>
      {summaries.map((summary) => (
        <div key={summary.id} className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
          <div className="flex justify-between items-start mb-2">
            <div className="flex-1">
              <h4 className="text-lg font-semibold text-gray-900">{summary.title}</h4>
              <div className="flex items-center space-x-2 mt-1">
                <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusBadge(summary.status)}`}>
                  {summary.status.toUpperCase()}
                </span>
                <span className="text-xs text-gray-500">
                  {getRequestTypeLabel(summary.request_type)}
                </span>
              </div>
            </div>
            <div className="flex space-x-2">
              {summary.status === 'completed' && (
                <>
                  <Link
                    to={`/summaries/${summary.id}`}
                    className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                  >
                    View
                  </Link>
                  <button
                    onClick={() => handleDownload(summary.id)}
                    className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700"
                  >
                    Download
                  </button>
                </>
              )}
              <button
                onClick={() => handleDelete(summary.id)}
                disabled={deletingId === summary.id}
                className="px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700 disabled:bg-gray-400"
              >
                {deletingId === summary.id ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>

          {summary.status === 'processing' && (
            <div className="mt-3">
              <div className="flex justify-between text-xs text-gray-600 mb-1">
                <span>Processing...</span>
                <span>{summary.progress_percent}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${summary.progress_percent}%` }}
                ></div>
              </div>
            </div>
          )}

          {summary.status === 'completed' && (
            <div className="mt-3 grid grid-cols-2 gap-2 text-sm text-gray-600">
              <div>
                <span className="font-medium">Duration:</span> {formatDuration(summary.summary_duration_seconds)}
              </div>
              <div>
                <span className="font-medium">Size:</span> {formatFileSize(summary.file_size)}
              </div>
            </div>
          )}

          {summary.status === 'failed' && summary.error_message && (
            <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
              Error: {summary.error_message}
            </div>
          )}

          <div className="mt-2 text-xs text-gray-500">
            Created: {new Date(summary.created_at).toLocaleString()}
          </div>
        </div>
      ))}
    </div>
  );
};

export default SummaryList;
