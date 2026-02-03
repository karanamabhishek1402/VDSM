from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SummaryRequest(BaseModel):
    video_id: str
    prompt: Optional[str] = None
    categories: Optional[List[str]] = None
    time_range_start: Optional[float] = None
    time_range_end: Optional[float] = None

class SummaryResponse(BaseModel):
    id: str
    video_id: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True
