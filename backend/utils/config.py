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
    MONGO_URI: str = "mongodb://REDACTED:REDACTED@localhost:27017/ai_barber_receptionist?authSource=admin"
    MONGO_DB_NAME: str = "ai_barber_receptionist"
    
    # WhatsApp Cloud API
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_VERIFY_TOKEN: str = ""
    
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
        "http://localhost:3000",
        "http://127.0.0.1:3000",
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
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env


# Create global settings instance
settings = Settings()
