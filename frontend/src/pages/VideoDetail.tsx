import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { videoService } from '../services/api';
import { Video } from '../types';
import VideoPlayer from '../components/VideoPlayer';
import Loading from '../components/Loading';

const VideoDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [video, setVideo] = useState<Video | null>(null);
  const [videoUrl, setVideoUrl] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      fetchVideoData(id);
    }
  }, [id]);

  const fetchVideoData = async (videoId: string) => {
    try {
      setLoading(true);
      const videoData = await videoService.getVideoById(videoId);
      setVideo(videoData);
      
      const url = await videoService.getDownloadUrl(videoId);
      setVideoUrl(url);
      setError(null);
    } catch (err) {
      setError("Failed to load video or you don't have permission to view it.");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!video || !window.confirm("Are you sure you want to delete this video?")) {
      return;
    }

    try {
      await videoService.deleteVideo(video.id);
      navigate('/dashboard');
    } catch (err) {
      alert("Failed to delete video");
    }
  };

  const handleDownload = async () => {
    if (video) {
      await videoService.downloadVideo(video.id);
    }
  };

  if (loading) {
    return <Loading />;
  }

  if (error || !video) {
    return (
      <div className="max-w-4xl mx-auto py-12 px-4 text-center">
        <p className="text-red-500 mb-4">{error || "Video not found"}</p>
        <button 
          onClick={() => navigate('/dashboard')}
          className="text-blue-600 font-medium hover:underline"
        >
          Return to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <VideoPlayer 
        url={videoUrl}
        title={video.title}
        description={video.description}
        onDelete={handleDelete}
        onDownload={handleDownload}
      />
      
      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h2 className="text-lg font-bold text-gray-800 mb-4">Technical Details</h2>
          <dl className="grid grid-cols-2 gap-y-4 text-sm">
            <dt className="text-gray-500">Resolution</dt>
            <dd className="text-gray-900 font-medium">{video.video_width ? `${video.video_width}x${video.video_height}` : 'N/A'}</dd>
            
            <dt className="text-gray-500">Frame Rate</dt>
            <dd className="text-gray-900 font-medium">{video.fps ? `${video.fps} fps` : 'N/A'}</dd>
            
            <dt className="text-gray-500">Duration</dt>
            <dd className="text-gray-900 font-medium">{video.duration_seconds ? `${Math.floor(video.duration_seconds / 60)}:${(video.duration_seconds % 60).toString().padStart(2, '0')}` : 'N/A'}</dd>
            
            <dt className="text-gray-500">Format</dt>
            <dd className="text-gray-900 font-medium uppercase">{video.format}</dd>
          </dl>
        </div>
        
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h2 className="text-lg font-bold text-gray-800 mb-4">File Information</h2>
          <dl className="grid grid-cols-2 gap-y-4 text-sm">
            <dt className="text-gray-500">Filename</dt>
            <dd className="text-gray-900 font-medium truncate" title={video.file_name}>{video.file_name}</dd>
            
            <dt className="text-gray-500">Size</dt>
            <dd className="text-gray-900 font-medium">{(video.file_size / (1024 * 1024)).toFixed(2)} MB</dd>
            
            <dt className="text-gray-500">Uploaded</dt>
            <dd className="text-gray-900 font-medium">{new Date(video.created_at).toLocaleString()}</dd>
            
            <dt className="text-gray-500">Status</dt>
            <dd className="text-gray-900 font-medium capitalize">Uploaded</dd>
          </dl>
        </div>
      </div>
    </div>
  );
};

export default VideoDetail;
