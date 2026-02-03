"""
FFmpeg service for video processing and composition
"""
import ffmpeg
import numpy as np
import subprocess
import json
import os
import logging
from typing import List, Tuple, Dict, Optional
from app.models.summary import SceneData

logger = logging.getLogger(__name__)

class FFmpegService:
    """Service for FFmpeg video processing"""
    
    def get_video_duration(self, video_path: str) -> float:
        """
        Get video length in seconds
        
        Args:
            video_path: Path to video file
            
        Returns:
            Duration in seconds
        """
        try:
            probe = ffmpeg.probe(video_path)
            duration = float(probe['streams'][0]['duration'])
            return duration
        except Exception as e:
            logger.error(f"Error getting video duration: {e}")
            raise
    
    def get_video_info(self, video_path: str) -> Dict:
        """
        Get video metadata (fps, duration, resolution, codec)
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video metadata
        """
        try:
            probe = ffmpeg.probe(video_path)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            
            if not video_stream:
                raise ValueError("No video stream found")
            
            # Parse FPS
            fps_parts = video_stream.get('r_frame_rate', '30/1').split('/')
            fps = float(fps_parts[0]) / float(fps_parts[1]) if len(fps_parts) == 2 else 30.0
            
            info = {
                'duration': float(video_stream.get('duration', 0)),
                'width': int(video_stream.get('width', 0)),
                'height': int(video_stream.get('height', 0)),
                'fps': fps,
                'codec': video_stream.get('codec_name', 'unknown'),
                'bit_rate': int(video_stream.get('bit_rate', 0))
            }
            
            return info
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            raise
    
    def get_frame_at_time(self, video_path: str, time_seconds: float) -> np.ndarray:
        """
        Extract frame at timestamp
        
        Args:
            video_path: Path to video file
            time_seconds: Timestamp in seconds
            
        Returns:
            Frame as numpy array (RGB)
        """
        try:
            out, _ = (
                ffmpeg
                .input(video_path, ss=time_seconds)
                .output('pipe:', vframes=1, format='rawvideo', pix_fmt='rgb24')
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )
            
            # Get video dimensions
            probe = ffmpeg.probe(video_path)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            width = int(video_stream['width'])
            height = int(video_stream['height'])
            
            # Convert to numpy array
            frame = np.frombuffer(out, np.uint8).reshape([height, width, 3])
            return frame
            
        except Exception as e:
            logger.error(f"Error extracting frame at time {time_seconds}: {e}")
            raise
    
    def extract_frames_for_sampling(
        self, 
        video_path: str, 
        sample_rate: int = 30
    ) -> List[Tuple[float, np.ndarray]]:
        """
        Extract frames for analysis
        
        Args:
            video_path: Path to video file
            sample_rate: Sample 1 frame every N frames
            
        Returns:
            List of (timestamp, frame_array) tuples
        """
        try:
            info = self.get_video_info(video_path)
            duration = info['duration']
            fps = info['fps']
            width = info['width']
            height = info['height']
            
            # Calculate time between samples
            time_between_samples = sample_rate / fps
            
            frames = []
            current_time = 0
            
            logger.info(f"Extracting frames from video (duration: {duration}s, fps: {fps}, sample_rate: {sample_rate})")
            
            while current_time < duration:
                try:
                    frame = self.get_frame_at_time(video_path, current_time)
                    frames.append((current_time, frame))
                    current_time += time_between_samples
                except Exception as e:
                    logger.warning(f"Skipping frame at {current_time}s: {e}")
                    current_time += time_between_samples
                    continue
            
            logger.info(f"Extracted {len(frames)} frames")
            return frames
            
        except Exception as e:
            logger.error(f"Error extracting frames for sampling: {e}")
            raise
    
    def compose_video_from_scenes(
        self, 
        source_video_path: str, 
        scenes: List[SceneData], 
        output_path: str,
        format: str = 'mp4'
    ) -> bool:
        """
        Create summary video from selected scenes
        
        Args:
            source_video_path: Path to source video
            scenes: List of SceneData objects
            output_path: Path for output video
            format: Output format (default: mp4)
            
        Returns:
            True if successful
        """
        if not scenes:
            logger.error("No scenes provided for composition")
            return False
        
        try:
            # Create a temporary file list for concat demuxer
            temp_dir = os.path.dirname(output_path)
            concat_file = os.path.join(temp_dir, f"concat_{os.path.basename(output_path)}.txt")
            
            # Extract individual scene clips
            scene_files = []
            for i, scene in enumerate(scenes):
                scene_file = os.path.join(temp_dir, f"scene_{i}_{os.path.basename(output_path)}")
                
                # Extract scene
                try:
                    (
                        ffmpeg
                        .input(source_video_path, ss=scene.start_time, t=scene.duration)
                        .output(
                            scene_file, 
                            c='copy',  # Copy codec for speed
                            avoid_negative_ts='make_zero'
                        )
                        .overwrite_output()
                        .run(capture_stdout=True, capture_stderr=True, quiet=True)
                    )
                    scene_files.append(scene_file)
                except Exception as e:
                    logger.warning(f"Error extracting scene {i}: {e}, trying with re-encoding")
                    # Fallback: re-encode if copy fails
                    (
                        ffmpeg
                        .input(source_video_path, ss=scene.start_time, t=scene.duration)
                        .output(scene_file)
                        .overwrite_output()
                        .run(capture_stdout=True, capture_stderr=True, quiet=True)
                    )
                    scene_files.append(scene_file)
            
            # Create concat file
            with open(concat_file, 'w') as f:
                for scene_file in scene_files:
                    f.write(f"file '{scene_file}'\n")
            
            # Concatenate scenes
            (
                ffmpeg
                .input(concat_file, format='concat', safe=0)
                .output(output_path, c='copy')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )
            
            # Cleanup temporary files
            try:
                os.remove(concat_file)
                for scene_file in scene_files:
                    if os.path.exists(scene_file):
                        os.remove(scene_file)
            except Exception as e:
                logger.warning(f"Error cleaning up temp files: {e}")
            
            logger.info(f"Successfully composed video: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error composing video from scenes: {e}")
            # Cleanup on error
            try:
                if os.path.exists(concat_file):
                    os.remove(concat_file)
                for scene_file in scene_files:
                    if os.path.exists(scene_file):
                        os.remove(scene_file)
            except:
                pass
            raise
    
    def convert_video_format(self, input_path: str, output_path: str, format: str) -> bool:
        """
        Convert between video formats
        
        Args:
            input_path: Input video path
            output_path: Output video path
            format: Target format
            
        Returns:
            True if successful
        """
        try:
            (
                ffmpeg
                .input(input_path)
                .output(output_path, format=format)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )
            
            logger.info(f"Successfully converted video to {format}")
            return True
            
        except Exception as e:
            logger.error(f"Error converting video format: {e}")
            raise
    
    def extract_audio_segment(
        self, 
        video_path: str, 
        start: float, 
        end: float, 
        output_path: str
    ) -> bool:
        """
        Extract audio from segment
        
        Args:
            video_path: Path to video file
            start: Start time in seconds
            end: End time in seconds
            output_path: Output audio file path
            
        Returns:
            True if successful
        """
        try:
            duration = end - start
            (
                ffmpeg
                .input(video_path, ss=start, t=duration)
                .output(output_path, acodec='copy')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )
            
            logger.info(f"Successfully extracted audio segment")
            return True
            
        except Exception as e:
            logger.error(f"Error extracting audio segment: {e}")
            raise


# Global instance
ffmpeg_service = FFmpegService()
