import React, { useRef, useEffect } from 'react';
import { Summary } from '../types';
import { summaryService } from '../services/api';
import { Link } from 'react-router-dom';

interface SummaryPlayerProps {
  summary: Summary;
  onDelete?: () => void;
}

const SummaryPlayer: React.FC<SummaryPlayerProps> = ({ summary, onDelete }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [downloadUrl, setDownloadUrl] = React.useState<string | null>(null);
  const [deleting, setDeleting] = React.useState(false);

  useEffect(() => {
    if (summary.status === 'completed') {
      const url = summaryService.getDownloadUrl(summary.id);
      setDownloadUrl(url);
    }
  }, [summary]);

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this summary?')) {
      return;
    }

    setDeleting(true);
    try {
      await summaryService.deleteSummary(summary.id);
      if (onDelete) {
        onDelete();
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete summary');
      setDeleting(false);
    }
  };

  const handleDownload = () => {
    summaryService.downloadSummary(summary.id);
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

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">{summary.title}</h2>
        <div className="flex items-center space-x-4 text-sm text-gray-600">
          <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded">
            {summary.request_type.replace('-', ' ').toUpperCase()}
          </span>
          <span>Created: {formatDate(summary.created_at)}</span>
          {summary.completed_at && <span>Completed: {formatDate(summary.completed_at)}</span>}
        </div>
      </div>

      {/* Video Player */}
      {summary.status === 'completed' && downloadUrl && (
        <div className="mb-6">
          <video
            ref={videoRef}
            controls
            className="w-full rounded-lg shadow-lg"
            style={{ maxHeight: '70vh' }}
          >
            <source src={downloadUrl} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        </div>
      )}

      {/* Metadata */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600 mb-1">Duration</div>
          <div className="text-lg font-semibold">{formatDuration(summary.summary_duration_seconds)}</div>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600 mb-1">File Size</div>
          <div className="text-lg font-semibold">{formatFileSize(summary.file_size)}</div>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600 mb-1">Scenes</div>
          <div className="text-lg font-semibold">{summary.selected_scenes?.length || 0}</div>
        </div>
      </div>

      {/* Request Details */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-2">Request Details</h3>
        <div className="bg-gray-50 p-4 rounded-lg">
          {summary.request_type === 'text-prompt' && (
            <div>
              <span className="font-medium">Prompt:</span>{' '}
              {(summary.request_data as any).prompt}
            </div>
          )}
          {summary.request_type === 'category' && (
            <div>
              <span className="font-medium">Category:</span>{' '}
              {(summary.request_data as any).category}
            </div>
          )}
          {summary.request_type === 'time-range' && (
            <div>
              <span className="font-medium">Time Ranges:</span>
              <ul className="mt-2 space-y-1">
                {(summary.request_data as any).ranges?.map((range: any, idx: number) => (
                  <li key={idx} className="text-sm">
                    {range.start_percent}% - {range.end_percent}%
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Selected Scenes (Optional) */}
      {summary.selected_scenes && summary.selected_scenes.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-2">Selected Scenes</h3>
          <div className="bg-gray-50 p-4 rounded-lg max-h-64 overflow-y-auto">
            <div className="space-y-2">
              {summary.selected_scenes.map((scene, idx) => (
                <div key={idx} className="flex justify-between items-center text-sm p-2 bg-white rounded">
                  <div>
                    <span className="font-medium">Scene {idx + 1}:</span>{' '}
                    {scene.start_time.toFixed(1)}s - {scene.end_time.toFixed(1)}s
                    {scene.matched_text && (
                      <span className="ml-2 text-gray-600">({scene.matched_text})</span>
                    )}
                  </div>
                  <div className="text-gray-600">
                    {scene.duration.toFixed(1)}s • {(scene.confidence_score * 100).toFixed(0)}% confidence
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-between items-center">
        <Link
          to={`/videos/${summary.video_id}`}
          className="text-blue-600 hover:text-blue-800 flex items-center"
        >
          ← Back to original video
        </Link>
        <div className="flex space-x-3">
          {summary.status === 'completed' && (
            <button
              onClick={handleDownload}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              Download
            </button>
          )}
          <button
            onClick={handleDelete}
            disabled={deleting}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:bg-gray-400"
          >
            {deleting ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default SummaryPlayer;
