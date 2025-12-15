"""
Configuration settings using Pydantic Settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"  # Allow extra fields from .env
    )
    
    # Application
    APP_NAME: str = "AI Receptionist"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    TESTING: bool = False
    
    # Database
    MONGO_URI: str = "mongodb://REDACTED:REDACTED@localhost:27017/ai_barber_receptionist?authSource=admin"
    MONGO_DB_NAME: str = "ai_barber_receptionist"
    
    # WhatsApp Cloud API
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_VERIFY_TOKEN: str = ""
    
    # Groq API - REMOVED
    # GROQ_API_KEY: str = ""
    # GROQ_MODEL: str = "mixtral-8x7b-32768"

    # Vapi Configuration
    VAPI_API_KEY: str = ""
    VAPI_PRIVATE_API_KEY: str = ""
    VAPI_PUBLIC_KEY: str = ""
    VAPI_WEBHOOK_SECRET: str = ""
    VAPI_WEBHOOK_URL: str = ""
    VAPI_ORGANIZATION_ID: str = ""
    VAPI_BASE_URL: str = "https://api.vapi.ai"

    # n8n Integration
    # NOTE: N8N_API_KEY is the ONLY intentionally hardcoded API key in this application.
    # This is the backend automation engine key and is NOT a client-facing service.
    # All client API keys (OpenAI, Vapi, Twilio, ElevenLabs, etc.) are stored
    # encrypted per-tenant in the MongoDB business_config collection.
    N8N_API_URL: str = "http://n8n:5678/api/v1"
    N8N_API_KEY: str = "REDACTED_JWT"
    
    # JWT & Security
    SECRET_KEY: str = "REDACTED"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Dashboard Access Control
    MAX_DASHBOARD_USERS: int = 5
    ALLOW_SELF_REGISTRATION: bool = False
    
    # CORS - Can be overridden via environment variable
    # Format: comma-separated list of origins
    # Example: "https://aireceptionist-lake.vercel.app,http://localhost:3000"
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173,https://aireceptionist-lake.vercel.app"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to list"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(',') if origin.strip()]
        return self.CORS_ORIGINS

    
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

    # LiveKit Voice Agent
    LIVEKIT_URL: str = ""
    LIVEKIT_API_KEY: str = ""
    LIVEKIT_API_SECRET: str = ""
    LIVEKIT_AGENT_QUEUE: str = "voice-agents"
    LIVEKIT_AGENT_NAME: str = "Parker_165"


# Create global settings instance
settings = Settings()

# 🔒 CRITICAL SECURITY CHECK: Enforce strong SECRET_KEY in production
WEAK_KEYS = [
    "change-this-secret-key-in-production",
    "dev",
    "development",
    "test",
    "secret",
    "supersecretkeyshouldbechangedinprod"
]

if settings.ENVIRONMENT in ["production", "prod"] and settings.SECRET_KEY in WEAK_KEYS:
    raise RuntimeError(
        "🚨 SECURITY ERROR: You MUST set a strong SECRET_KEY in production!\n"
        "Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(32))'\n"
        "Then set it in your .env file: SECRET_KEY=<generated_key>"
    )

# Warn in development too
if settings.SECRET_KEY in WEAK_KEYS and settings.ENVIRONMENT not in ["production", "prod"]:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(
        "⚠️ WARNING: Using default SECRET_KEY. This is OK for development but "
        "MUST be changed before deploying to production!"
    )
