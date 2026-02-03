from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_videos():
    return {"message": "List videos endpoint"}

@router.post("/upload")
async def upload_video():
    return {"message": "Upload video endpoint"}

@router.get("/{video_id}")
async def get_video(video_id: str):
    return {"message": f"Get video {video_id} endpoint"}
