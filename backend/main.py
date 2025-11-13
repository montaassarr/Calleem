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
from datetime import datetime

# Import routers
from routers import webhook, appointments, services, users

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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
