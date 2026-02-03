import React from 'react';

interface VideoPlayerProps {
  url: string;
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({ url }) => {
  return (
    <div className="relative pt-[56.25%] bg-black">
      <video
        className="absolute top-0 left-0 w-full h-full"
        controls
        src={url}
      >
        Your browser does not support the video tag.
      </video>
    </div>
  );
};

export default VideoPlayer;
