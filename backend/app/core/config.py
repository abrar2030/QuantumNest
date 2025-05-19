from pydantic import BaseSettings
from typing import Optional, Dict, Any, List
import os
from functools import lru_cache

class Settings(BaseSettings):
    """
    Application settings with environment variable support
    
    This class centralizes all configuration settings for the application
    and supports loading from environment variables.
    """
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "QuantumNest Capital API"
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./quantumnest.db")
    
    # Celery settings
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]  # In production, replace with specific origins
    
    # AI model settings
    AI_MODELS_DIR: str = os.getenv("AI_MODELS_DIR", "./models")
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings with caching
    
    Returns a cached instance of the Settings class to avoid
    reloading environment variables on each call.
    """
    return Settings()
