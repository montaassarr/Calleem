"""
AI Receptionist - Main Application Entry Point
==============================================
FastAPI backend for B2B AI Receptionist SaaS Platform

Features:
- Multi-tenant architecture (each tenant = business user)
- Vapi voice AI integration
- Appointment scheduling
- Real-time WebSocket updates
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
from datetime import datetime

from database.mongo_config import connect_to_mongo, close_mongo_connection, get_database
from utils.config import settings
from utils.error_logger import set_error_logger_db
from middleware.error_handler import ErrorHandlingMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown"""
    logger.info("🚀 Starting AI Receptionist...")
    await connect_to_mongo()
    set_error_logger_db(get_database())
    logger.info("✅ Application ready!")
    yield
    logger.info("🛑 Shutting down...")
    await close_mongo_connection()


# Initialize FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="AI Receptionist SaaS Platform API",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    redirect_slashes=False  # Prevent 307 redirects
)

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Configuration - MUST be added FIRST (processed LAST in middleware stack)
cors_origins = settings.cors_origins_list

# Always include production frontends (explicit list, no wildcard)
production_origins = [
    # New custom domains
    "https://calleem.tech",
    "https://www.calleem.tech",
    # Existing Vercel deployment (kept for safety)
    "https://aireceptionist-lake.vercel.app",
    # Historical alias retained (if still used)
    "https://www.aireceptionist-lake.vercel.app",
]
cors_origins.extend(production_origins)

# Add localhost for development
if os.getenv("ENVIRONMENT") != "production":
    cors_origins.extend(["http://localhost:3000", "http://localhost:5173"])

# De-duplicate
cors_origins = list(set(cors_origins))
logger.info(f"🌐 CORS allowed origins: {cors_origins}")

# Use explicit methods/headers for credentialed requests and proper preflight handling
ALLOWED_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
ALLOWED_HEADERS = [
    "Authorization",
    "Content-Type",
    "Accept",
    "Origin",
    "X-Requested-With",
    "X-CSRF-Token",
    "Cache-Control",
    "Pragma",
    "X-Tenant-ID",  # Custom header for multi-tenant isolation
]

# Headers exposed to browser JavaScript in responses
EXPOSED_HEADERS = [
    "Content-Length",
    "Content-Type",
    "X-Request-ID",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
    expose_headers=EXPOSED_HEADERS,
    max_age=3600,
)

# Error handling middleware - added after CORS so CORS wraps it
app.add_middleware(ErrorHandlingMiddleware)


# ============== ROUTERS ==============
from routers import (
    users,
    appointments,
    services,
    conversations,
    calls,
    tenants,
    assistants,
    phone_numbers,
    billing,
    vapi,
    whatsapp,
    websocket,
    admin,
    monitoring,
    contacts,
    chat,
    webhook,
)

# Auth & Users
app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["Auth"])

# Core Business
app.include_router(appointments.router, prefix=f"{settings.API_V1_PREFIX}/appointments", tags=["Appointments"])
app.include_router(services.router, prefix=f"{settings.API_V1_PREFIX}/services", tags=["Services"])
app.include_router(conversations.router, prefix=f"{settings.API_V1_PREFIX}/conversations", tags=["Conversations"])
app.include_router(calls.router, prefix="/api", tags=["Calls"])

# Tenant Management
app.include_router(tenants.router, prefix=f"{settings.API_V1_PREFIX}/tenants", tags=["Tenants"])

# AI Assistant (Vapi) - tags defined in router
app.include_router(assistants.router, prefix=f"{settings.API_V1_PREFIX}")

# API Keys removed - not using BYOK system

# Phone & Voice - tags defined in routers
app.include_router(phone_numbers.router, prefix=f"{settings.API_V1_PREFIX}/phone-numbers")
app.include_router(vapi.router, prefix=f"{settings.API_V1_PREFIX}/vapi")

# Billing
app.include_router(billing.router, prefix=f"{settings.API_V1_PREFIX}/billing", tags=["Billing"])

# WhatsApp
app.include_router(whatsapp.router, prefix=f"{settings.API_V1_PREFIX}/whatsapp", tags=["WhatsApp"])

# Webhooks (Twilio SMS/WhatsApp inbound, status checks)
app.include_router(webhook.router, prefix=f"{settings.API_V1_PREFIX}/webhook", tags=["Webhooks"])

# WebSocket
app.include_router(websocket.router)

# Admin (Platform Owner - all admin endpoints including analytics)
app.include_router(admin.router, prefix=f"{settings.API_V1_PREFIX}/admin", tags=["Admin"])

# Monitoring
app.include_router(monitoring.router, prefix=f"{settings.API_V1_PREFIX}", tags=["Monitoring"])

# Contacts (public + admin)
app.include_router(contacts.router, prefix=f"{settings.API_V1_PREFIX}/contacts", tags=["Contacts"])

# Chat Widget (public, uses Gemini AI)
app.include_router(chat.router, prefix=f"{settings.API_V1_PREFIX}/chat", tags=["Chat"])


# ============== ROOT ENDPOINTS ==============
@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "running",
        "app": settings.APP_NAME,
        "version": "2.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check for load balancers"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc) if settings.DEBUG else None}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
