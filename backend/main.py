from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, videos, summaries
from app.services.clip_service import clip_service
from config import get_settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

@app.on_event("startup")
async def startup_event():
    """Load CLIP model on startup"""
    logger.info("Loading CLIP model...")
    clip_service.load_clip_model()
    logger.info("CLIP model loaded successfully")

# CORS Configuration
origins = [
    "http://localhost:5173",  # Vite default port
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(videos.router, prefix="/videos", tags=["videos"])
app.include_router(summaries.router, prefix="", tags=["summaries"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"message": "Welcome to VDSM API"}
