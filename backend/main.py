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
from routers import webhook, appointments, services, users, conversations, admin

# Import database connection
from database.mongo_config import connect_to_mongo, close_mongo_connection

# Import settings
from utils.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
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
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL", "http://localhost:3000"),
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        # Add production URL when deploying
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"✅ CORS configured for: {os.getenv('FRONTEND_URL', 'http://localhost:3000')}")


# Include routers
app.include_router(
    webhook.router,
    prefix=f"{settings.API_V1_PREFIX}/webhook",
    tags=["Twilio Webhook"]
)

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

from routers import voice_agent
app.include_router(
    voice_agent.router,
    prefix=f"{settings.API_V1_PREFIX}/voice-agent",
    tags=["Voice Agent"]
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
