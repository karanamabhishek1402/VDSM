"""
Summary service for managing video summaries
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from app.services.db_service import db_service
from app.services.storage_service import storage_service
from app.models.summary import SummaryResponse, SceneData
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class SummaryService:
    """Service for managing video summaries"""
    
    def create_summary(
        self, 
        video_id: str, 
        user_id: str, 
        title: str, 
        request_type: str, 
        request_data: dict
    ) -> Dict[str, Any]:
        """
        Create summary record
        
        Args:
            video_id: UUID of the video
            user_id: UUID of the user
            title: Title for the summary
            request_type: Type of request (text-prompt, category, time-range)
            request_data: Request-specific data
            
        Returns:
            Summary record as dictionary
        """
        try:
            data = {
                'video_id': video_id,
                'user_id': user_id,
                'title': title,
                'request_type': request_type,
                'request_data': request_data,
                'selected_scenes': [],
                'status': 'processing',
                'progress_percent': 0
            }
            
            response = db_service.client.table('summaries').insert(data).execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"Created summary: {response.data[0]['id']}")
                return response.data[0]
            
            raise Exception("Failed to create summary")
            
        except Exception as e:
            logger.error(f"Error creating summary: {e}")
            raise
    
    def get_summary_by_id(self, summary_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get summary by ID (verify ownership)
        
        Args:
            summary_id: UUID of the summary
            user_id: UUID of the user
            
        Returns:
            Summary record or None
        """
        try:
            response = db_service.client.table('summaries')\
                .select('*')\
                .eq('id', summary_id)\
                .eq('user_id', user_id)\
                .execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting summary: {e}")
            raise
    
    def get_video_summaries(self, video_id: str, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all summaries for a video
        
        Args:
            video_id: UUID of the video
            user_id: UUID of the user
            
        Returns:
            List of summary records
        """
        try:
            response = db_service.client.table('summaries')\
                .select('*')\
                .eq('video_id', video_id)\
                .eq('user_id', user_id)\
                .order('created_at', desc=True)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Error getting video summaries: {e}")
            raise
    
    def update_summary_progress(
        self, 
        summary_id: str, 
        progress: int, 
        status: str
    ) -> Dict[str, Any]:
        """
        Update summary progress
        
        Args:
            summary_id: UUID of the summary
            progress: Progress percentage (0-100)
            status: Status string
            
        Returns:
            Updated summary record
        """
        try:
            data = {
                'progress_percent': progress,
                'status': status
            }
            
            response = db_service.client.table('summaries')\
                .update(data)\
                .eq('id', summary_id)\
                .execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            
            raise Exception("Failed to update summary progress")
            
        except Exception as e:
            logger.error(f"Error updating summary progress: {e}")
            raise
    
    def update_summary_on_completion(
        self, 
        summary_id: str, 
        storage_path: str, 
        file_size: int, 
        duration: int,
        selected_scenes: List[SceneData]
    ) -> Dict[str, Any]:
        """
        Update summary when processing completes
        
        Args:
            summary_id: UUID of the summary
            storage_path: Path in storage
            file_size: Size of the summary video file
            duration: Duration in seconds
            selected_scenes: List of selected scenes
            
        Returns:
            Updated summary record
        """
        try:
            # Convert SceneData objects to dicts
            scenes_json = [scene.model_dump() for scene in selected_scenes]
            
            data = {
                'storage_path': storage_path,
                'file_size': file_size,
                'summary_duration_seconds': duration,
                'selected_scenes': scenes_json,
                'status': 'completed',
                'progress_percent': 100,
                'completed_at': datetime.utcnow().isoformat()
            }
            
            response = db_service.client.table('summaries')\
                .update(data)\
                .eq('id', summary_id)\
                .execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"Summary {summary_id} completed")
                return response.data[0]
            
            raise Exception("Failed to update summary on completion")
            
        except Exception as e:
            logger.error(f"Error updating summary on completion: {e}")
            raise
    
    def update_summary_on_error(self, summary_id: str, error_message: str) -> Dict[str, Any]:
        """
        Update summary when processing fails
        
        Args:
            summary_id: UUID of the summary
            error_message: Error description
            
        Returns:
            Updated summary record
        """
        try:
            data = {
                'status': 'failed',
                'error_message': error_message
            }
            
            response = db_service.client.table('summaries')\
                .update(data)\
                .eq('id', summary_id)\
                .execute()
            
            if response.data and len(response.data) > 0:
                logger.error(f"Summary {summary_id} failed: {error_message}")
                return response.data[0]
            
            raise Exception("Failed to update summary on error")
            
        except Exception as e:
            logger.error(f"Error updating summary on error: {e}")
            raise
    
    def delete_summary(self, summary_id: str, user_id: str) -> bool:
        """
        Delete summary and associated file
        
        Args:
            summary_id: UUID of the summary
            user_id: UUID of the user
            
        Returns:
            True if successful
        """
        try:
            # Get summary to find storage path
            summary = self.get_summary_by_id(summary_id, user_id)
            
            if not summary:
                return False
            
            # Delete from storage if exists
            if summary.get('storage_path'):
                try:
                    storage_service.delete_file(
                        settings.SUMMARY_STORAGE_BUCKET,
                        summary['storage_path']
                    )
                except Exception as e:
                    logger.warning(f"Error deleting summary file from storage: {e}")
            
            # Delete from database
            db_service.client.table('summaries')\
                .delete()\
                .eq('id', summary_id)\
                .eq('user_id', user_id)\
                .execute()
            
            logger.info(f"Deleted summary: {summary_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting summary: {e}")
            raise


# Global instance
summary_service = SummaryService()
