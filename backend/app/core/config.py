"""
Application Configuration

Centralized configuration management using Pydantic Settings.
Supports environment variables and secure secret management.
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All sensitive values should be set via environment variables
    or secret management systems in production.
    """
    
    # Application
    APP_NAME: str = "Jeevan+ Backend"
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = False
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Security
    SECRET_KEY: str = "CHANGE_THIS_IN_PRODUCTION_USE_ENV_VAR"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Short-lived access tokens
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Encryption
    ENCRYPTION_KEY: str = "CHANGE_THIS_32_BYTE_KEY_IN_PRODUCTION"
    ENCRYPTION_ALGORITHM: str = "AES-256-GCM"
    
    # Firebase / Firestore
    FIREBASE_PROJECT_ID: Optional[str] = None
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    FIREBASE_STORAGE_BUCKET: Optional[str] = None
    
    # AI Services
    AI_SERVICE_ENABLED: bool = True
    AI_SERVICE_TYPE: str = "local"  # local, huggingface, gemini
    HUGGINGFACE_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    AI_FALLBACK_ENABLED: bool = True
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # WebRTC / Signaling
    WEBRTC_SIGNALING_ENABLED: bool = True
    WEBRTC_STUN_SERVER: str = "stun:stun.l.google.com:19302"
    WEBRTC_TURN_SERVER: Optional[str] = None
    
    # IoT
    IOT_DEVICE_AUTH_ENABLED: bool = True
    IOT_ALERT_THRESHOLDS: dict = {
        "heart_rate_min": 60,
        "heart_rate_max": 100,
        "bp_systolic_max": 140,
        "bp_diastolic_max": 90,
        "spo2_min": 95
    }
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json, text
    
    # Cloud Run
    PORT: int = 8080
    HOST: str = "0.0.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance.
    Use this function to get settings throughout the application.
    """
    return Settings()


# Global settings instance
settings = get_settings()

