from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from typing import List, Optional
from app.models.video import VideoUploadResponse, VideoResponse, VideoMetadata
from app.services.video_service import video_service
from app.services.storage_service import storage_service
from app.dependencies import get_current_user
from config import get_settings
import uuid
import os
import tempfile
from fastapi.responses import RedirectResponse

router = APIRouter()
settings = get_settings()

@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    # Validation
    if not video_service.validate_video_format(file.filename):
        raise HTTPException(status_code=400, detail="Unsupported video format")
    
    # Title validation
    if not title or len(title) > 255:
        raise HTTPException(status_code=400, detail="Title is required and must be less than 255 characters")

    user_id = current_user['id']
    video_id = str(uuid.uuid4())
    file_ext = file.filename.split('.')[-1] if '.' in file.filename else ""
    storage_path = f"users/{user_id}/videos/{video_id}/{file.filename}"
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.MAX_VIDEO_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Max size is {settings.MAX_VIDEO_SIZE / (1024*1024*1024)}GB")

    # Upload to Supabase Storage
    uploaded_path = video_service.upload_file_to_supabase(content, storage_path)
    if not uploaded_path:
        raise HTTPException(status_code=500, detail="Failed to upload file to storage")

    # Create record in database
    video_record = video_service.create_video_metadata(
        user_id=user_id,
        title=title,
        description=description,
        file_name=file.filename,
        storage_path=storage_path,
        file_size=file_size,
        format=file_ext
    )

    if not video_record:
        # Cleanup uploaded file if DB insert fails
        storage_service.delete_file(settings.SUPABASE_STORAGE_BUCKET, storage_path)
        raise HTTPException(status_code=500, detail="Failed to create video record")

    # Extract metadata (needs physical file)
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        metadata = video_service.get_video_metadata_from_file(tmp_path)
        video_service.update_video_metadata(video_record['id'], metadata)
        # Refresh record
        updated_video = video_service.get_video_by_id(video_record['id'], user_id)
        if updated_video:
            video_record = updated_video
    except Exception as e:
        print(f"Metadata extraction failed: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return video_record

@router.get("/", response_model=List[VideoResponse])
async def list_videos(
    skip: int = 0,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    limit = min(limit, 100)
    videos = video_service.get_user_videos(current_user['id'], skip, limit)
    return videos

@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: str,
    current_user: dict = Depends(get_current_user)
):
    video = video_service.get_video_by_id(video_id, current_user['id'])
    if not video:
        raise HTTPException(status_code=404, detail="Video not found or access denied")
    return video

@router.get("/{video_id}/download")
async def download_video(
    video_id: str,
    current_user: dict = Depends(get_current_user)
):
    video = video_service.get_video_by_id(video_id, current_user['id'])
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    signed_url = storage_service.get_signed_url(settings.SUPABASE_STORAGE_BUCKET, video['storage_path'])
    if not signed_url:
        raise HTTPException(status_code=500, detail="Could not generate download link")
    
    return RedirectResponse(url=signed_url)

@router.delete("/{video_id}")
async def delete_video(
    video_id: str,
    current_user: dict = Depends(get_current_user)
):
    success = video_service.delete_video(video_id, current_user['id'])
    if not success:
        raise HTTPException(status_code=404, detail="Video not found or access denied")
    
    return {"message": "Video deleted successfully"}
