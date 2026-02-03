from fastapi import APIRouter

router = APIRouter()

@router.post("/")
async def create_summary():
    return {"message": "Create summary endpoint"}

@router.get("/{summary_id}")
async def get_summary(summary_id: str):
    return {"message": f"Get summary {summary_id} endpoint"}
