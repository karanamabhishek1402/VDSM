import React, { useState } from 'react';
import VideoUpload from '../components/VideoUpload';
import VideoList from '../components/VideoList';
import { useAuth } from '../context/AuthContext';
import { User as UserIcon } from 'lucide-react';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleUploadSuccess = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-8 mb-8 text-white shadow-lg">
        <div className="flex items-center space-x-6">
          <div className="bg-white/20 p-4 rounded-2xl backdrop-blur-sm">
            <UserIcon className="h-10 w-10" />
          </div>
          <div>
            <h1 className="text-3xl font-bold">
              Welcome back, {user?.full_name || user?.username || 'User'}!
            </h1>
            <p className="text-blue-100 mt-2 text-lg">
              Manage your videos and explore their content.
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-12">
        <section>
          <div className="max-w-3xl mx-auto">
            <VideoUpload onUploadSuccess={handleUploadSuccess} />
          </div>
        </section>

        <section>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-800">My Videos</h2>
          </div>
          <VideoList refreshTrigger={refreshTrigger} />
        </section>
      </div>
    </div>
  );
};

export default Dashboard;
