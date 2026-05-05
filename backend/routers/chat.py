"""
Chat Router
============
Public API endpoints for the landing page chat widget.
Uses Gemini AI for intelligent responses.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import logging
import uuid
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

from services.gemini_chat_service import gemini_chat_service

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatMessageRequest(BaseModel):
    """Request model for chat messages"""
    message: str
    session_id: Optional[str] = None


class ChatMessageResponse(BaseModel):
    """Response model for chat messages"""
    response: str
    session_id: str


class InitSessionResponse(BaseModel):
    """Response model for session initialization"""
    session_id: str
    welcome_message: str


@router.post("/init", response_model=InitSessionResponse)
@limiter.limit("10/minute")
async def init_chat_session(request: Request):
    """Initialize a new chat session"""
    try:
        session_id = str(uuid.uuid4())
        # Pre-create the session
        gemini_chat_service.get_or_create_session(session_id)
        
        return InitSessionResponse(
            session_id=session_id,
            welcome_message="Hello! 👋 I'm your Calleem AI assistant. How can I help you learn about our AI receptionist services today?"
        )
    except Exception as e:
        logger.error(f"Error initializing chat session: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize chat session")


@router.post("/message", response_model=ChatMessageResponse)
@limiter.limit("20/minute")
async def send_chat_message(http_request: Request, request: ChatMessageRequest):
    """Send a message and get AI response"""
    try:
        # Use provided session_id or create new one
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get response from Gemini
        response = await gemini_chat_service.send_message(session_id, request.message)
        
        return ChatMessageResponse(
            response=response,
            session_id=session_id
        )
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail="Failed to process message")


@router.delete("/session/{session_id}")
async def clear_chat_session(session_id: str):
    """Clear a chat session"""
    try:
        gemini_chat_service.clear_session(session_id)
        return {"status": "success", "message": "Session cleared"}
    except Exception as e:
        logger.error(f"Error clearing chat session: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear session")
