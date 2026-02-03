"""
API routes for video summarization
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.summary import (
    TextPromptRequest, 
    CategoryRequest, 
    TimeRangeRequest,
    SummaryResponse,
    SummaryProgressResponse
)
from app.services.summary_service import summary_service
from app.services.video_service import video_service
from app.dependencies import get_current_user
from app.tasks.video_tasks import (
    process_text_prompt_summary,
    process_category_summary,
    process_time_range_summary
)
from config import get_settings, SUMMARIZATION_CATEGORIES
from fastapi.responses import RedirectResponse
from app.services.storage_service import storage_service
from redis import Redis
from rq import Queue
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()

# Redis Queue setup
redis_conn = Redis.from_url(settings.REDIS_URL)
task_queue = Queue(connection=redis_conn)

@router.post("/videos/{video_id}/summaries/text-prompt", response_model=SummaryResponse)
async def create_text_prompt_summary(
    video_id: str,
    request: TextPromptRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a text prompt-based summary
    
    - **video_id**: UUID of the video
    - **title**: Title for the summary
    - **prompt**: Text prompt to match scenes (e.g., "action scenes", "beautiful landscapes")
    """
    user_id = current_user['id']
    
    # Verify video exists and user owns it
    video = video_service.get_video_by_id(video_id, user_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found or access denied"
        )
    
    # Create summary record
    try:
        request_data = {
            'prompt': request.prompt
        }
        
        summary = summary_service.create_summary(
            video_id=video_id,
            user_id=user_id,
            title=request.title,
            request_type='text-prompt',
            request_data=request_data
        )
        
        # Queue processing task
        task_queue.enqueue(
            process_text_prompt_summary,
            summary['id'],
            video_id,
            video['storage_path'],
            request.prompt,
            job_timeout='4h'  # Allow up to 4 hours for processing
        )
        
        logger.info(f"Queued text prompt summary task for {summary['id']}")
        
        return summary
        
    except Exception as e:
        logger.error(f"Error creating text prompt summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create summary: {str(e)}"
        )

@router.post("/videos/{video_id}/summaries/category", response_model=SummaryResponse)
async def create_category_summary(
    video_id: str,
    request: CategoryRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a category-based summary
    
    - **video_id**: UUID of the video
    - **title**: Title for the summary
    - **category**: Category to match (action, dialogue, landscape, people, text, key_moments)
    """
    user_id = current_user['id']
    
    # Verify video exists and user owns it
    video = video_service.get_video_by_id(video_id, user_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found or access denied"
        )
    
    # Validate category
    if request.category not in SUMMARIZATION_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Must be one of: {', '.join(SUMMARIZATION_CATEGORIES.keys())}"
        )
    
    # Create summary record
    try:
        request_data = {
            'category': request.category
        }
        
        summary = summary_service.create_summary(
            video_id=video_id,
            user_id=user_id,
            title=request.title,
            request_type='category',
            request_data=request_data
        )
        
        # Queue processing task
        task_queue.enqueue(
            process_category_summary,
            summary['id'],
            video_id,
            video['storage_path'],
            request.category,
            job_timeout='4h'
        )
        
        logger.info(f"Queued category summary task for {summary['id']}")
        
        return summary
        
    except Exception as e:
        logger.error(f"Error creating category summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create summary: {str(e)}"
        )

@router.post("/videos/{video_id}/summaries/time-range", response_model=SummaryResponse)
async def create_time_range_summary(
    video_id: str,
    request: TimeRangeRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a time range-based summary
    
    - **video_id**: UUID of the video
    - **title**: Title for the summary
    - **ranges**: List of time ranges (start_percent, end_percent)
    """
    user_id = current_user['id']
    
    # Verify video exists and user owns it
    video = video_service.get_video_by_id(video_id, user_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found or access denied"
        )
    
    # Create summary record
    try:
        # Convert TimeRange objects to dicts
        ranges_data = [r.model_dump() for r in request.ranges]
        
        request_data = {
            'ranges': ranges_data
        }
        
        summary = summary_service.create_summary(
            video_id=video_id,
            user_id=user_id,
            title=request.title,
            request_type='time-range',
            request_data=request_data
        )
        
        # Queue processing task
        task_queue.enqueue(
            process_time_range_summary,
            summary['id'],
            video_id,
            video['storage_path'],
            ranges_data,
            job_timeout='4h'
        )
        
        logger.info(f"Queued time range summary task for {summary['id']}")
        
        return summary
        
    except Exception as e:
        logger.error(f"Error creating time range summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create summary: {str(e)}"
        )

@router.get("/videos/{video_id}/summaries", response_model=List[SummaryResponse])
async def get_video_summaries(
    video_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all summaries for a video
    
    - **video_id**: UUID of the video
    """
    user_id = current_user['id']
    
    # Verify video exists and user owns it
    video = video_service.get_video_by_id(video_id, user_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found or access denied"
        )
    
    try:
        summaries = summary_service.get_video_summaries(video_id, user_id)
        return summaries
    except Exception as e:
        logger.error(f"Error getting video summaries: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get summaries: {str(e)}"
        )

@router.get("/summaries/{summary_id}", response_model=SummaryResponse)
async def get_summary(
    summary_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get summary by ID with progress and scene details
    
    - **summary_id**: UUID of the summary
    """
    user_id = current_user['id']
    
    try:
        summary = summary_service.get_summary_by_id(summary_id, user_id)
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Summary not found or access denied"
            )
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get summary: {str(e)}"
        )

@router.get("/summaries/{summary_id}/progress", response_model=SummaryProgressResponse)
async def get_summary_progress(
    summary_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get summary processing progress
    
    - **summary_id**: UUID of the summary
    """
    user_id = current_user['id']
    
    try:
        summary = summary_service.get_summary_by_id(summary_id, user_id)
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Summary not found or access denied"
            )
        
        return SummaryProgressResponse(
            summary_id=summary['id'],
            status=summary['status'],
            progress_percent=summary['progress_percent'],
            error_message=summary.get('error_message')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting summary progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get progress: {str(e)}"
        )

@router.get("/summaries/{summary_id}/download")
async def download_summary(
    summary_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Download summary video (returns signed URL with 24 hour expiry)
    
    - **summary_id**: UUID of the summary
    """
    user_id = current_user['id']
    
    try:
        summary = summary_service.get_summary_by_id(summary_id, user_id)
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Summary not found or access denied"
            )
        
        # Check if summary is completed
        if summary['status'] != 'completed':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Summary is not ready for download. Status: {summary['status']}"
            )
        
        if not summary.get('storage_path'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Summary file not found"
            )
        
        # Generate signed URL (24 hour expiry)
        signed_url = storage_service.get_signed_url(
            settings.SUMMARY_STORAGE_BUCKET,
            summary['storage_path'],
            expires_in=86400  # 24 hours
        )
        
        if not signed_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not generate download link"
            )
        
        return RedirectResponse(url=signed_url)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate download link: {str(e)}"
        )

@router.delete("/summaries/{summary_id}")
async def delete_summary(
    summary_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete summary and associated file
    
    - **summary_id**: UUID of the summary
    """
    user_id = current_user['id']
    
    try:
        success = summary_service.delete_summary(summary_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Summary not found or access denied"
            )
        
        return {"message": "Summary deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete summary: {str(e)}"
        )

@router.get("/categories")
async def get_categories():
    """
    Get list of available summarization categories
    """
    categories = []
    for key, description in SUMMARIZATION_CATEGORIES.items():
        categories.append({
            'id': key,
            'name': key.replace('_', ' ').title(),
            'description': description
        })
    return {"categories": categories}
