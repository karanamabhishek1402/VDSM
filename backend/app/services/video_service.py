import ffmpeg
import os
from typing import List, Optional
from app.models.video import VideoMetadata
from app.services.storage_service import storage_service
from app.services.db_service import supabase
from config import get_settings

settings = get_settings()

class VideoService:
    def create_video_metadata(self, user_id: str, title: str, description: Optional[str], 
                              file_name: str, storage_path: str, file_size: int, format: str):
        video_data = {
            "user_id": user_id,
            "title": title,
            "description": description,
            "file_name": file_name,
            "storage_path": storage_path,
            "file_size": file_size,
            "format": format,
            "upload_status": "uploaded",
            "is_processed": False
        }
        response = supabase.table("videos").insert(video_data).execute()
        return response.data[0] if response.data else None

    def get_video_by_id(self, video_id: str, user_id: str) -> Optional[dict]:
        response = supabase.table("videos").select("*").eq("id", video_id).eq("user_id", user_id).execute()
        return response.data[0] if response.data else None

    def get_user_videos(self, user_id: str, skip: int = 0, limit: int = 20) -> List[dict]:
        response = supabase.table("videos")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", {"ascending": False})\
            .range(skip, skip + limit - 1)\
            .execute()
        return response.data

    def delete_video(self, video_id: str, user_id: str) -> bool:
        video = self.get_video_by_id(video_id, user_id)
        if not video:
            return False
        
        # Delete from storage
        storage_service.delete_file(settings.SUPABASE_STORAGE_BUCKET, video['storage_path'])
        
        # Delete from DB
        supabase.table("videos").delete().eq("id", video_id).execute()
        return True

    def update_video_metadata(self, video_id: str, metadata: VideoMetadata):
        update_data = metadata.model_dump(exclude_unset=True)
        update_data["is_processed"] = True
        response = supabase.table("videos").update(update_data).eq("id", video_id).execute()
        return response.data[0] if response.data else None

    def upload_file_to_supabase(self, file_bytes: bytes, storage_path: str) -> str:
        return storage_service.upload_file(settings.SUPABASE_STORAGE_BUCKET, storage_path, file_bytes)

    def get_video_metadata_from_file(self, file_path: str) -> VideoMetadata:
        try:
            probe = ffmpeg.probe(file_path)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            
            duration = float(probe['format'].get('duration', 0))
            width = int(video_stream['width']) if video_stream and 'width' in video_stream else None
            height = int(video_stream['height']) if video_stream and 'height' in video_stream else None
            
            fps = None
            if video_stream and 'avg_frame_rate' in video_stream:
                avg_frame_rate = video_stream['avg_frame_rate']
                if '/' in avg_frame_rate:
                    num, den = avg_frame_rate.split('/')
                    if float(den) != 0:
                        fps = float(num) / float(den)
                else:
                    try:
                        fps = float(avg_frame_rate)
                    except ValueError:
                        fps = None

            format_name = probe['format'].get('format_name', 'unknown').split(',')[0]

            return VideoMetadata(
                duration_seconds=int(duration),
                resolution=f"{width}x{height}" if width and height else None,
                fps=round(fps, 2) if fps else None,
                video_width=width,
                video_height=height,
                format=format_name
            )
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            return VideoMetadata(format="unknown")

    def validate_video_format(self, file_name: str) -> bool:
        if not file_name or '.' not in file_name:
            return False
        ext = file_name.split('.')[-1].lower()
        return ext in settings.SUPPORTED_VIDEO_FORMATS

video_service = VideoService()
