import React from 'react';
import { useParams } from 'react-router-dom';
import VideoPlayer from '../components/VideoPlayer';
import SummaryRequest from '../components/SummaryRequest';
import SummaryResult from '../components/SummaryResult';

const VideoDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <h1 className="text-2xl font-semibold text-gray-900 mb-6">Video {id}</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <VideoPlayer url="https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4" />
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-lg font-medium mb-4">Generate Summary</h2>
              <SummaryRequest />
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-medium mb-4">Results</h2>
            <SummaryResult />
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoDetail;
