"""
Background tasks for video processing and summarization
"""
import os
import logging
import tempfile
from typing import List, Dict
from app.services.clip_service import clip_service
from app.services.ffmpeg_service import ffmpeg_service
from app.services.summary_service import summary_service
from app.services.storage_service import storage_service
from app.models.summary import SceneData
from config import get_settings, SUMMARIZATION_CATEGORIES

logger = logging.getLogger(__name__)
settings = get_settings()

def process_upload_task(video_id: str):
    """Process video upload (placeholder for future implementation)"""
    logger.info(f"Processing video {video_id}")
    pass

def process_text_prompt_summary(summary_id: str, video_id: str, video_path_storage: str, prompt: str):
    """
    Process text prompt-based summary request
    
    Args:
        summary_id: UUID of the summary
        video_id: UUID of the video
        video_path_storage: Storage path of the video
        prompt: Text prompt
    """
    temp_video_path = None
    temp_output_path = None
    
    try:
        logger.info(f"Starting text prompt summary for {summary_id}: {prompt}")
        
        # Update progress: downloading
        summary_service.update_summary_progress(summary_id, 10, 'processing')
        
        # Download video from storage to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_video:
            temp_video_path = tmp_video.name
            storage_service.download_file(
                settings.SUPABASE_STORAGE_BUCKET,
                video_path_storage,
                temp_video_path
            )
        
        logger.info(f"Downloaded video to {temp_video_path}")
        
        # Update progress: extracting frames
        summary_service.update_summary_progress(summary_id, 20, 'processing')
        
        # Extract frames for analysis
        frames = ffmpeg_service.extract_frames_for_sampling(
            temp_video_path,
            sample_rate=settings.FRAME_SAMPLE_RATE
        )
        
        # Update progress: computing embeddings
        summary_service.update_summary_progress(summary_id, 40, 'processing')
        
        # Extract frame embeddings
        frame_embeddings = clip_service.extract_frame_embeddings(frames)
        
        # Update progress: matching scenes
        summary_service.update_summary_progress(summary_id, 60, 'processing')
        
        # Compute text embedding
        text_embedding = clip_service.compute_text_embedding(prompt)
        
        # Find matching scenes
        matching_scenes = clip_service.find_matching_scenes(
            frame_embeddings,
            text_embedding,
            matched_text=prompt
        )
        
        if not matching_scenes:
            raise Exception(f"No scenes found matching prompt: {prompt}")
        
        # Select best scenes
        selected_scenes = clip_service.select_best_scenes(
            matching_scenes,
            target_duration=settings.TARGET_SUMMARY_DURATION_SECONDS
        )
        
        logger.info(f"Selected {len(selected_scenes)} scenes for summary")
        
        # Update progress: composing video
        summary_service.update_summary_progress(summary_id, 80, 'processing')
        
        # Compose summary video
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_output:
            temp_output_path = tmp_output.name
        
        success = ffmpeg_service.compose_video_from_scenes(
            temp_video_path,
            selected_scenes,
            temp_output_path
        )
        
        if not success:
            raise Exception("Failed to compose summary video")
        
        # Update progress: uploading
        summary_service.update_summary_progress(summary_id, 90, 'processing')
        
        # Upload to storage
        output_filename = f"{summary_id}.mp4"
        storage_path = f"{settings.SUMMARY_STORAGE_PATH}/{output_filename}"
        
        storage_service.upload_file(
            settings.SUMMARY_STORAGE_BUCKET,
            temp_output_path,
            storage_path
        )
        
        # Get file size and duration
        file_size = os.path.getsize(temp_output_path)
        duration = int(sum(scene.duration for scene in selected_scenes))
        
        # Update summary on completion
        summary_service.update_summary_on_completion(
            summary_id,
            storage_path,
            file_size,
            duration,
            selected_scenes
        )
        
        logger.info(f"Completed text prompt summary: {summary_id}")
        
    except Exception as e:
        logger.error(f"Error processing text prompt summary: {e}")
        summary_service.update_summary_on_error(summary_id, str(e))
        raise
    
    finally:
        # Cleanup temp files
        if temp_video_path and os.path.exists(temp_video_path):
            os.remove(temp_video_path)
        if temp_output_path and os.path.exists(temp_output_path):
            os.remove(temp_output_path)

def process_category_summary(summary_id: str, video_id: str, video_path_storage: str, category: str):
    """
    Process category-based summary request
    
    Args:
        summary_id: UUID of the summary
        video_id: UUID of the video
        video_path_storage: Storage path of the video
        category: Category name
    """
    temp_video_path = None
    temp_output_path = None
    
    try:
        logger.info(f"Starting category summary for {summary_id}: {category}")
        
        if category not in SUMMARIZATION_CATEGORIES:
            raise ValueError(f"Invalid category: {category}")
        
        # Update progress: downloading
        summary_service.update_summary_progress(summary_id, 10, 'processing')
        
        # Download video from storage to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_video:
            temp_video_path = tmp_video.name
            storage_service.download_file(
                settings.SUPABASE_STORAGE_BUCKET,
                video_path_storage,
                temp_video_path
            )
        
        logger.info(f"Downloaded video to {temp_video_path}")
        
        # Update progress: extracting frames
        summary_service.update_summary_progress(summary_id, 20, 'processing')
        
        # Extract frames for analysis
        frames = ffmpeg_service.extract_frames_for_sampling(
            temp_video_path,
            sample_rate=settings.FRAME_SAMPLE_RATE
        )
        
        # Update progress: computing embeddings
        summary_service.update_summary_progress(summary_id, 40, 'processing')
        
        # Extract frame embeddings
        frame_embeddings = clip_service.extract_frame_embeddings(frames)
        
        # Update progress: matching scenes
        summary_service.update_summary_progress(summary_id, 60, 'processing')
        
        # Match category scenes
        matching_scenes = clip_service.match_category_scenes(frame_embeddings, category)
        
        if not matching_scenes:
            raise Exception(f"No scenes found for category: {category}")
        
        # Select best scenes
        selected_scenes = clip_service.select_best_scenes(
            matching_scenes,
            target_duration=settings.TARGET_SUMMARY_DURATION_SECONDS
        )
        
        logger.info(f"Selected {len(selected_scenes)} scenes for summary")
        
        # Update progress: composing video
        summary_service.update_summary_progress(summary_id, 80, 'processing')
        
        # Compose summary video
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_output:
            temp_output_path = tmp_output.name
        
        success = ffmpeg_service.compose_video_from_scenes(
            temp_video_path,
            selected_scenes,
            temp_output_path
        )
        
        if not success:
            raise Exception("Failed to compose summary video")
        
        # Update progress: uploading
        summary_service.update_summary_progress(summary_id, 90, 'processing')
        
        # Upload to storage
        output_filename = f"{summary_id}.mp4"
        storage_path = f"{settings.SUMMARY_STORAGE_PATH}/{output_filename}"
        
        storage_service.upload_file(
            settings.SUMMARY_STORAGE_BUCKET,
            temp_output_path,
            storage_path
        )
        
        # Get file size and duration
        file_size = os.path.getsize(temp_output_path)
        duration = int(sum(scene.duration for scene in selected_scenes))
        
        # Update summary on completion
        summary_service.update_summary_on_completion(
            summary_id,
            storage_path,
            file_size,
            duration,
            selected_scenes
        )
        
        logger.info(f"Completed category summary: {summary_id}")
        
    except Exception as e:
        logger.error(f"Error processing category summary: {e}")
        summary_service.update_summary_on_error(summary_id, str(e))
        raise
    
    finally:
        # Cleanup temp files
        if temp_video_path and os.path.exists(temp_video_path):
            os.remove(temp_video_path)
        if temp_output_path and os.path.exists(temp_output_path):
            os.remove(temp_output_path)

def process_time_range_summary(summary_id: str, video_id: str, video_path_storage: str, time_ranges: List[Dict]):
    """
    Process time range-based summary request
    
    Args:
        summary_id: UUID of the summary
        video_id: UUID of the video
        video_path_storage: Storage path of the video
        time_ranges: List of time range dicts with start_percent and end_percent
    """
    temp_video_path = None
    temp_output_path = None
    
    try:
        logger.info(f"Starting time range summary for {summary_id}")
        
        # Update progress: downloading
        summary_service.update_summary_progress(summary_id, 10, 'processing')
        
        # Download video from storage to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_video:
            temp_video_path = tmp_video.name
            storage_service.download_file(
                settings.SUPABASE_STORAGE_BUCKET,
                video_path_storage,
                temp_video_path
            )
        
        logger.info(f"Downloaded video to {temp_video_path}")
        
        # Update progress: processing
        summary_service.update_summary_progress(summary_id, 30, 'processing')
        
        # Get video duration
        video_duration = ffmpeg_service.get_video_duration(temp_video_path)
        
        # Convert percentage ranges to time ranges
        scenes = []
        for time_range in time_ranges:
            start_percent = time_range['start_percent']
            end_percent = time_range['end_percent']
            
            start_time = (start_percent / 100.0) * video_duration
            end_time = (end_percent / 100.0) * video_duration
            duration = end_time - start_time
            
            scene = SceneData(
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                confidence_score=1.0,  # Manual selection, full confidence
                matched_text=f"{start_percent:.1f}%-{end_percent:.1f}%"
            )
            scenes.append(scene)
        
        logger.info(f"Created {len(scenes)} scenes from time ranges")
        
        # Update progress: composing video
        summary_service.update_summary_progress(summary_id, 60, 'processing')
        
        # Compose summary video
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_output:
            temp_output_path = tmp_output.name
        
        success = ffmpeg_service.compose_video_from_scenes(
            temp_video_path,
            scenes,
            temp_output_path
        )
        
        if not success:
            raise Exception("Failed to compose summary video")
        
        # Update progress: uploading
        summary_service.update_summary_progress(summary_id, 80, 'processing')
        
        # Upload to storage
        output_filename = f"{summary_id}.mp4"
        storage_path = f"{settings.SUMMARY_STORAGE_PATH}/{output_filename}"
        
        storage_service.upload_file(
            settings.SUMMARY_STORAGE_BUCKET,
            temp_output_path,
            storage_path
        )
        
        # Get file size and duration
        file_size = os.path.getsize(temp_output_path)
        duration = int(sum(scene.duration for scene in scenes))
        
        # Update summary on completion
        summary_service.update_summary_on_completion(
            summary_id,
            storage_path,
            file_size,
            duration,
            scenes
        )
        
        logger.info(f"Completed time range summary: {summary_id}")
        
    except Exception as e:
        logger.error(f"Error processing time range summary: {e}")
        summary_service.update_summary_on_error(summary_id, str(e))
        raise
    
    finally:
        # Cleanup temp files
        if temp_video_path and os.path.exists(temp_video_path):
            os.remove(temp_video_path)
        if temp_output_path and os.path.exists(temp_output_path):
            os.remove(temp_output_path)


def generate_summary_task(summary_id: str):
    """Legacy task function (deprecated)"""
    logger.info(f"Generating summary {summary_id} (legacy)")
    pass
