"""
Configuration settings using Pydantic Settings
"""

from pydantic_settings import BaseSettings
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
    
    # Twilio
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    TWILIO_VERIFY_SID: str = ""
    
    # Groq API
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "mixtral-8x7b-32768"
    
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
        "http://localhost:5174",
        "http://localhost:8080",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:8080",
        "http://localhost:3000"
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env


# Create global settings instance
settings = Settings()
