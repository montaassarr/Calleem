"""
AI Receptionist for Barber Shop - Main Application Entry Point
================================================================

This is the FastAPI application that handles:
- Twilio webhook endpoints for SMS/Voice
- RESTful API for appointment management
- WebSocket connections for real-time dashboard updates
- AI-powered conversation management using Groq API

Author: AI Development Team
Date: November 2025
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
from datetime import datetime

# Import routers
from routers import (
    webhook,
    # webhook_livekit,
    appointments,
    services,
    users,
    conversations,
    admin,
    platform_keys,
    simple_setup,
    onboarding,
    monitoring,
)

# Import database connection
from database.mongo_config import connect_to_mongo, close_mongo_connection

# Import settings
from utils.config import settings

# Import custom error handling
from utils.error_logger import set_error_logger_db
from middleware.error_handler import ErrorHandlingMiddleware

# Configure logging
# Use only console logging for production (Railway/Docker)
# File logging only for local development
handlers = [logging.StreamHandler()]

# Add file handler only if logs directory exists (local dev)
if os.path.exists('logs') or os.makedirs('logs', exist_ok=True):
    try:
        handlers.append(logging.FileHandler('logs/app.log'))
    except:
        pass  # Skip file logging if it fails in production

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("🚀 Starting AI Receptionist application...")
    await connect_to_mongo()
    
    # Initialize error logger with database
    from database.mongo_config import get_database
    db = get_database()
    set_error_logger_db(db)
    logger.info("✅ Error logging system initialized")
    
    logger.info("✅ Application startup complete!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down AI Receptionist application...")
    await close_mongo_connection()
    logger.info("✅ Application shutdown complete!")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered receptionist for barber shop appointments via Twilio",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 🔒 RATE LIMITING (FIX #3)
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

# Add error handling middleware
app.add_middleware(ErrorHandlingMiddleware)
logger.info("✅ Error handling middleware enabled")

# CORS Configuration - Allow Vercel frontend and handle preflight requests
# Get CORS origins from environment variable or use defaults
cors_origins_env = os.getenv("CORS_ORIGINS", "")
frontend_url = os.getenv("FRONTEND_URL", "")

# Build CORS origins list
cors_origins = []

# Add from CORS_ORIGINS environment variable (comma-separated)
if cors_origins_env:
    cors_origins.extend([origin.strip() for origin in cors_origins_env.split(",") if origin.strip()])

# Add FRONTEND_URL if provided
if frontend_url:
    cors_origins.append(frontend_url)
    cors_origins.append(frontend_url.rstrip("/"))  # Without trailing slash

# Always include production Vercel domain
cors_origins.extend([
    "https://aireceptionist-lake.vercel.app",
    "https://aireceptionist-lake.vercel.app/",
])

# Add localhost for development (only if not in production)
if os.getenv("ENVIRONMENT", "development") != "production":
    cors_origins.extend([
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ])

# Remove duplicates and empty strings
cors_origins = list(set([origin for origin in cors_origins if origin]))

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

logger.info(f"✅ CORS configured for origins: {', '.join(cors_origins)}")


# Include routers
app.include_router(
    webhook.router,
    prefix=f"{settings.API_V1_PREFIX}/webhook",
    tags=["Twilio Webhook"]
)

# app.include_router(
#     webhook_livekit.router,
#     prefix=f"{settings.API_V1_PREFIX}/webhook",
#     tags=["LiveKit Webhook"]
# )

app.include_router(
    appointments.router,
    prefix=f"{settings.API_V1_PREFIX}/appointments",
    tags=["Appointments"]
)

app.include_router(
    services.router,
    prefix=f"{settings.API_V1_PREFIX}/services",
    tags=["Services"]
)

app.include_router(
    users.router,
    prefix=f"{settings.API_V1_PREFIX}/users",
    tags=["Users & Authentication"]
)

app.include_router(
    conversations.router,
    prefix=f"{settings.API_V1_PREFIX}/conversations",
    tags=["Conversations"]
)

app.include_router(
    admin.router,
    prefix=f"{settings.API_V1_PREFIX}/admin",
    tags=["Admin"]
)

from routers import admin_analytics
app.include_router(
    admin_analytics.router,
    prefix=f"{settings.API_V1_PREFIX}/admin",
    tags=["Admin Analytics"]
)

# Platform API Keys (Admin Only)
app.include_router(
    platform_keys.router,
    prefix=f"{settings.API_V1_PREFIX}",
    tags=["Platform API Keys"]
)

from routers import automations
app.include_router(
    automations.router,
    prefix=f"{settings.API_V1_PREFIX}/automations",
    tags=["Smart Automations"]
)

from routers import whatsapp
app.include_router(
    whatsapp.router,
    prefix=f"{settings.API_V1_PREFIX}/whatsapp",
    tags=["WhatsApp"]
)

from routers import tenants
app.include_router(
    tenants.router,
    prefix=f"{settings.API_V1_PREFIX}/tenants",
    tags=["Tenants"]
)

from routers import phone_numbers
app.include_router(
    phone_numbers.router,
    prefix=f"{settings.API_V1_PREFIX}/phone-numbers",
    tags=["Phone Numbers"]
)

from routers import api_keys
app.include_router(
    api_keys.router,
    prefix=f"{settings.API_V1_PREFIX}",
    tags=["API Keys"]
)

from routers import agents
app.include_router(
    agents.router,
    prefix=f"{settings.API_V1_PREFIX}/agents",
    tags=["Agents"]
)

from routers import billing
app.include_router(
    billing.router,
    prefix=f"{settings.API_V1_PREFIX}/billing",
    tags=["Billing & Subscriptions"]
)

# LiveKit Token Server (equivalent to official livekit/token-server)
# from routers import livekit_token
# app.include_router(
#     livekit_token.router,
#     prefix=f"{settings.API_V1_PREFIX}/livekit",
#     tags=["LiveKit Token"]
# )

# Monitoring endpoints for diagnostics
app.include_router(
    monitoring.router,
    prefix=f"{settings.API_V1_PREFIX}",
    tags=["Monitoring"]
)

# Simple Setup for Non-Technical Users
app.include_router(
    simple_setup.router,
    prefix=f"{settings.API_V1_PREFIX}",
    tags=["Easy Setup"]
)

# Onboarding Wizard (Voice Provider Setup)
app.include_router(
    onboarding.router,
    prefix=f"{settings.API_V1_PREFIX}",
    tags=["Onboarding"]
)


# AI Chat Router (Replaces n8n)
from routers import ai_chat
app.include_router(
    ai_chat.router,
    prefix=f"{settings.API_V1_PREFIX}",
    tags=["AI Chat"]
)

# Chat Completions Router (OpenAI text chat)
from routers import chat
app.include_router(
    chat.router,
    prefix=f"{settings.API_V1_PREFIX}",
    tags=["Chat Completions"]
)

# WebSocket Router
from routers import websocket
app.include_router(websocket.router)

# Vapi Voice Router (Webhooks)
from routers import vapi as vapi_router
app.include_router(
    vapi_router.router,
    prefix=f"{settings.API_V1_PREFIX}/vapi",
    tags=["Vapi Webhooks"]
)

# Comprehensive Assistant Management Router
from routers import assistants as assistants_router
app.include_router(
    assistants_router.router,
    prefix=f"{settings.API_V1_PREFIX}",
    tags=["Assistant Management"]
)



@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "🤖 AI Receptionist API is running!",
        "app_name": settings.APP_NAME,
        "business": settings.BUSINESS_NAME,
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected",  # TODO: Add actual DB health check
        "services": {
            "twilio": "configured",
            "groq": "configured",
            "mongodb": "connected"
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on http://0.0.0.0:8000")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
