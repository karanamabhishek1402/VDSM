from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class VideoBase(BaseModel):
    title: str
    description: Optional[str] = None
    duration: Optional[float] = None

class VideoCreate(VideoBase):
    pass

class Video(VideoBase):
    id: str
    file_path: str
    uploaded_at: datetime
    processed: bool = False
    
    class Config:
        from_attributes = True
