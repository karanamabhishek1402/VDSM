import React from 'react';
import VideoUpload from '../components/VideoUpload';
import { Link } from 'react-router-dom';

const Dashboard: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <h1 className="text-2xl font-semibold text-gray-900 mb-6">Dashboard</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white p-6 shadow rounded-lg">
            <VideoUpload />
          </div>
          
          <div className="bg-white p-6 shadow rounded-lg">
            <h2 className="text-lg font-medium mb-4">Your Videos</h2>
            <div className="space-y-4">
              {/* List of videos would go here */}
              <div className="border-b pb-2">
                <Link to="/videos/1" className="text-blue-600 hover:text-blue-800">
                  Sample Video 1
                </Link>
                <span className="text-gray-500 text-sm ml-2">- 10:30 mins</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
