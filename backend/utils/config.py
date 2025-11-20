"""
Configuration settings using Pydantic Settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "AI Receptionist"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "ai_barber_receptionist"
    
    # WhatsApp Cloud API
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_VERIFY_TOKEN: str = ""
    
    # Groq API
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Vapi Voice Agent
    VAPI_API_KEY: str = ""
    VAPI_PUBLIC_KEY: str = ""
    VAPI_WEBHOOK_URL: str = ""
    VAPI_ASSISTANT_ID: str | None = None
    VOICE_AGENT_ENABLED: bool = False
    VOICE_AGENT_TEMPERATURE: float = 0.6
    VOICE_AGENT_WEBRTC_PUBLIC_KEY: str | None = None
    VOICE_AGENT_WEBRTC_ASSISTANT_ID: str | None = None
    VOICE_AGENT_WEBRTC_SESSION_TTL_MINUTES: int = 10
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_DEFAULT_VOICE: str = "alloy"
    
    # JWT & Security
    SECRET_KEY: str = "REDACTED"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Dashboard Access Control
    MAX_DASHBOARD_USERS: int = 5
    ALLOW_SELF_REGISTRATION: bool = False
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]
    
    # Business Details
    BUSINESS_NAME: str = "Royal Fade Barbershop"
    BUSINESS_PHONE: str = ""
    BUSINESS_EMAIL: str = "info@barbershop.com"
    BUSINESS_ADDRESS: str = ""
    BUSINESS_HOURS: str = "Monday-Saturday 9:00 AM - 8:00 PM"
    TIMEZONE: str = "America/New_York"
    AVAILABLE_SERVICES: str = "Haircut,Beard Trim,Fade,Hot Shave,Hair & Beard Combo"
    DEFAULT_APPOINTMENT_DURATION: int = 30
    
    # Redis (Optional)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    
    # Celery (Optional)
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow",  # Allow extra fields from .env
    )

    @property
    def MONGODB_URL(self) -> str:
        """Backward-compatible alias for scripts expecting MONGODB_URL."""
        return self.MONGO_URI

    @property
    def MONGODB_DB_NAME(self) -> str:
        """Backward-compatible alias for scripts expecting MONGODB_DB_NAME."""
        return self.MONGO_DB_NAME


# Create global settings instance
settings = Settings()
