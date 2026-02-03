import React from 'react';
import { Download, Trash2, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';

interface VideoPlayerProps {
  url: string;
  title: string;
  description?: string;
  onDelete?: () => void;
  onDownload?: () => void;
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({ url, title, description, onDelete, onDownload }) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <Link to="/dashboard" className="flex items-center text-blue-600 hover:text-blue-700 font-medium">
          <ArrowLeft className="w-4 h-4 mr-1" />
          Back to Dashboard
        </Link>
        <div className="flex space-x-2">
          {onDownload && (
            <button 
              onClick={onDownload}
              className="flex items-center space-x-1 px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium"
            >
              <Download className="w-4 h-4" />
              <span>Download</span>
            </button>
          )}
          {onDelete && (
            <button 
              onClick={onDelete}
              className="flex items-center space-x-1 px-3 py-1.5 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors text-sm font-medium"
            >
              <Trash2 className="w-4 h-4" />
              <span>Delete</span>
            </button>
          )}
        </div>
      </div>

      <div className="bg-black rounded-xl overflow-hidden shadow-2xl aspect-video">
        <video
          className="w-full h-full"
          controls
          autoPlay
          src={url}
        >
          Your browser does not support the video tag.
        </video>
      </div>

      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">{title}</h1>
        <p className="text-gray-600 whitespace-pre-wrap">
          {description || "No description provided."}
        </p>
      </div>
    </div>
  );
};

export default VideoPlayer;
