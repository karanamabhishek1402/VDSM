import React, { useEffect, useState } from 'react';
import { Play, Download, Trash2, Calendar, Clock, FileVideo, HardDrive } from 'lucide-react';
import { videoService } from '../services/api';
import { Video } from '../types';
import { Link } from 'react-router-dom';

interface VideoListProps {
  refreshTrigger?: number;
}

const VideoList: React.FC<VideoListProps> = ({ refreshTrigger }) => {
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchVideos();
  }, [refreshTrigger]);

  const fetchVideos = async () => {
    try {
      setLoading(true);
      const data = await videoService.getVideos();
      setVideos(data);
      setError(null);
    } catch (err) {
      setError("Failed to load videos");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (videoId: string) => {
    if (!window.confirm("Are you sure you want to delete this video? This action cannot be undone.")) {
      return;
    }

    try {
      await videoService.deleteVideo(videoId);
      setVideos(videos.filter(v => v.id !== videoId));
    } catch (err) {
      alert("Failed to delete video");
    }
  };

  const handleDownload = async (videoId: string) => {
    await videoService.downloadVideo(videoId);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading && videos.length === 0) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3].map(i => (
          <div key={i} className="bg-white rounded-xl shadow-sm border border-gray-100 h-64 animate-pulse"></div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500">{error}</p>
        <button onClick={fetchVideos} className="mt-4 text-blue-600 font-medium">Try again</button>
      </div>
    );
  }

  if (videos.length === 0) {
    return (
      <div className="text-center py-20 bg-gray-50 rounded-xl border-2 border-dashed border-gray-200">
        <FileVideo className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-700">No videos yet</h3>
        <p className="text-gray-500 mt-1">Upload your first video to see it here!</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {videos.map((video) => (
        <div key={video.id} className="bg-white rounded-xl shadow-md border border-gray-100 overflow-hidden hover:shadow-lg transition-shadow">
          <div className="aspect-video bg-gray-900 flex items-center justify-center relative group">
            <FileVideo className="w-12 h-12 text-gray-700" />
            <Link 
              to={`/videos/${video.id}`}
              className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity"
            >
              <div className="bg-white p-3 rounded-full">
                <Play className="w-6 h-6 text-blue-600 fill-blue-600" />
              </div>
            </Link>
            {video.duration_seconds && (
              <div className="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded font-medium">
                {formatDuration(video.duration_seconds)}
              </div>
            )}
          </div>
          
          <div className="p-4">
            <h3 className="font-bold text-gray-800 truncate mb-1" title={video.title}>
              {video.title}
            </h3>
            <p className="text-sm text-gray-500 line-clamp-2 mb-4 h-10">
              {video.description || "No description provided."}
            </p>
            
            <div className="flex flex-wrap gap-y-2 mb-4">
              <div className="flex items-center text-xs text-gray-500 w-1/2">
                <Calendar className="w-3 h-3 mr-1" />
                {new Date(video.created_at).toLocaleDateString()}
              </div>
              <div className="flex items-center text-xs text-gray-500 w-1/2">
                <HardDrive className="w-3 h-3 mr-1" />
                {formatFileSize(video.file_size)}
              </div>
              <div className="flex items-center text-xs text-gray-500 w-1/2">
                <Clock className="w-3 h-3 mr-1" />
                {video.format.toUpperCase()}
              </div>
            </div>

            <div className="flex border-t border-gray-50 pt-4 space-x-2">
              <Link 
                to={`/videos/${video.id}`}
                className="flex-1 flex items-center justify-center space-x-1 py-2 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors text-sm font-medium"
              >
                <Play className="w-4 h-4" />
                <span>Watch</span>
              </Link>
              <button 
                onClick={() => handleDownload(video.id)}
                className="p-2 text-gray-500 hover:text-blue-600 hover:bg-gray-50 rounded-lg transition-colors"
                title="Download"
              >
                <Download className="w-5 h-5" />
              </button>
              <button 
                onClick={() => handleDelete(video.id)}
                className="p-2 text-gray-500 hover:text-red-600 hover:bg-gray-50 rounded-lg transition-colors"
                title="Delete"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default VideoList;
