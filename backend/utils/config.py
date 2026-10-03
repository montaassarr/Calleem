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
    APP_NAME: str = "Calleem"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    API_V1_PREFIX: str = "/api/v1"
    TESTING: bool = False
    
    # Database
    MONGO_URI: str = "mongodb://localhost:27017/calleem"
    MONGO_DB_NAME: str = "calleem"
    
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
    # Webhook auth now uses Vapi Credentials bearer token (server.credentialId), not legacy webhook secrets.
    VAPI_WEBHOOK_BEARER_TOKEN: str = ""
    VAPI_SERVER_CREDENTIAL_ID: str = ""
    VAPI_WEBHOOK_URL: str = ""  # Can be set explicitly or will be constructed from BACKEND_URL
    AGENT_INTERNAL_TOKEN: str = ""
    BACKEND_URL: str = ""  # Set via BACKEND_URL environment variable
    VAPI_ORGANIZATION_ID: str = ""
    VAPI_BASE_URL: str = "https://api.vapi.ai"
    
    # JWT & Security
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Dashboard Access Control
    MAX_DASHBOARD_USERS: int = 5
    ALLOW_SELF_REGISTRATION: bool = False
    # Platform admin API (/api/v1/admin). Set to false on public deployments; the
    # super admin runs it locally with scripts/admin_console.py.
    ADMIN_API_ENABLED: bool = True
    
    # CORS - Can be overridden via environment variable
    # Format: comma-separated list of origins
    # Example: "https://calleem.tech,https://www.calleem.tech,https://aireceptionist-lake.vercel.app"
    CORS_ORIGINS: str = (
        "http://localhost:3000,"
        "http://127.0.0.1:3000,"
        "http://localhost:5173,"
        "http://127.0.0.1:5173,"
        "https://calleem.tech,"
        "https://www.calleem.tech,"
        "https://aireceptionist-lake.vercel.app"
    )
    
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

# 🔒 AGENT_INTERNAL_TOKEN strength check
# Fail closed: in production a weak or missing token disables the internal agent
# endpoints (they answer 503) instead of crashing the whole API or silently
# generating a random token that no caller knows.
_WEAK_AGENT_TOKENS = {"", "sdhcqkuefyqkjsdclzyedsdkfskdjsl", "changeme"}
_RECOMMENDED_AGENT_TOKEN_LENGTH = 32

if settings.AGENT_INTERNAL_TOKEN and len(settings.AGENT_INTERNAL_TOKEN) < _RECOMMENDED_AGENT_TOKEN_LENGTH:
    import logging
    logging.getLogger(__name__).warning(
        "⚠️ AGENT_INTERNAL_TOKEN is shorter than %d characters; consider rotating it.",
        _RECOMMENDED_AGENT_TOKEN_LENGTH,
    )

if settings.AGENT_INTERNAL_TOKEN in _WEAK_AGENT_TOKENS:
    import logging
    logger = logging.getLogger(__name__)
    if settings.ENVIRONMENT in ["production", "prod"]:
        logger.error(
            "🚨 AGENT_INTERNAL_TOKEN is weak or unset in production: internal agent endpoints "
            "are DISABLED (503). Set a strong token (python -c 'import secrets; "
            "print(secrets.token_urlsafe(32))') in the production environment variables."
        )
        settings.AGENT_INTERNAL_TOKEN = ""
    else:
        logger.warning(
            "⚠️ AGENT_INTERNAL_TOKEN is weak or unset. OK for development, "
            "but internal agent endpoints will be disabled in production."
        )
