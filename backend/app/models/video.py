from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class VideoBase(BaseModel):
    title: str
    description: Optional[str] = None

class VideoCreate(VideoBase):
    pass

class VideoMetadata(BaseModel):
    duration_seconds: Optional[int] = None
    resolution: Optional[str] = None
    fps: Optional[float] = None
    video_width: Optional[int] = None
    video_height: Optional[int] = None
    format: str

class VideoUploadResponse(BaseModel):
    id: UUID
    title: str
    file_name: str
    file_size: int
    format: str
    created_at: datetime

    class Config:
        from_attributes = True

class VideoResponse(VideoBase):
    id: UUID
    user_id: UUID
    file_name: str
    storage_path: str
    file_size: int
    duration_seconds: Optional[int] = None
    format: str
    resolution: Optional[str] = None
    video_width: Optional[int] = None
    video_height: Optional[int] = None
    fps: Optional[float] = None
    upload_status: str
    is_processed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
