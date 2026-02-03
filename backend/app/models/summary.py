from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class SceneData(BaseModel):
    """Scene data with timing and confidence information"""
    start_time: float
    end_time: float
    duration: float
    confidence_score: float
    matched_text: Optional[str] = None
    matched_category: Optional[str] = None

class SummaryRequestBase(BaseModel):
    """Base class for summary requests"""
    title: str = Field(..., min_length=1, max_length=255)
    
class TextPromptRequest(SummaryRequestBase):
    """Text prompt-based summary request"""
    prompt: str = Field(..., min_length=1, max_length=500)
    
    @field_validator('prompt')
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Prompt cannot be empty')
        return v.strip()

class CategoryRequest(SummaryRequestBase):
    """Category-based summary request"""
    category: str
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v: str) -> str:
        from config import SUMMARIZATION_CATEGORIES
        if v not in SUMMARIZATION_CATEGORIES:
            raise ValueError(f'Category must be one of: {", ".join(SUMMARIZATION_CATEGORIES.keys())}')
        return v

class TimeRange(BaseModel):
    """Time range specification"""
    start_percent: float = Field(..., ge=0, le=100)
    end_percent: float = Field(..., ge=0, le=100)
    
    @field_validator('end_percent')
    @classmethod
    def validate_end_after_start(cls, v: float, info) -> float:
        if 'start_percent' in info.data and v <= info.data['start_percent']:
            raise ValueError('end_percent must be greater than start_percent')
        return v

class TimeRangeRequest(SummaryRequestBase):
    """Time range-based summary request"""
    ranges: List[TimeRange] = Field(..., min_length=1)
    
    @field_validator('ranges')
    @classmethod
    def validate_no_overlap(cls, v: List[TimeRange]) -> List[TimeRange]:
        # Sort ranges by start_percent
        sorted_ranges = sorted(v, key=lambda r: r.start_percent)
        
        # Check for overlaps
        for i in range(len(sorted_ranges) - 1):
            if sorted_ranges[i].end_percent > sorted_ranges[i + 1].start_percent:
                raise ValueError('Time ranges cannot overlap')
        
        return v

class SummaryResponse(BaseModel):
    """Summary response model"""
    id: UUID
    video_id: UUID
    user_id: UUID
    title: str
    request_type: str
    request_data: Dict[str, Any]
    selected_scenes: Optional[List[SceneData]] = None
    summary_duration_seconds: Optional[int] = None
    output_format: str = "mp4"
    storage_path: Optional[str] = None
    file_size: Optional[int] = None
    status: str
    progress_percent: int = 0
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    updated_at: datetime

    class Config:
        from_attributes = True

class SummaryProgressResponse(BaseModel):
    """Summary progress response"""
    summary_id: UUID
    status: str
    progress_percent: int
    error_message: Optional[str] = None
