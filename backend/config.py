from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "VDSM API"
    DEBUG: bool = False
    
    # Supabase Settings
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_STORAGE_BUCKET: str = "videos"

    # Video Settings
    SUPPORTED_VIDEO_FORMATS: list = ["mp4", "mov", "wmv", "avi", "mkv", "webm"]
    MAX_VIDEO_SIZE_MB: int = 4000
    VIDEO_STORAGE_PATH: str = "videos"

    @property
    def MAX_VIDEO_SIZE(self) -> int:
        return self.MAX_VIDEO_SIZE_MB * 1024 * 1024

    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379"
    
    # Auth Settings
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    model_config = SettingsConfigDict(env_file=".env")

@lru_cache()
def get_settings():
    return Settings()
