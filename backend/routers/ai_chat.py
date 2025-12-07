from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import logging

from ai.agent import receptionist_agent

# Use "ai" as prefix so the final URL is /api/v1/ai/chat
router = APIRouter(prefix="/ai", tags=["AI Chat"])
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    message: str
    session_id: str
    tenant_id: str

class ChatResponse(BaseModel):
    response: str

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Chat with the AI Receptionist.
    Replaces n8n workflow.
    """
    try:
        response_text = await receptionist_agent.chat(
            session_id=request.session_id,
            tenant_id=request.tenant_id,
            message=request.message
        )
        return ChatResponse(response=response_text)
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        # Return a polite error to the user instead of 500 if possible, 
        # but for API 500 is locally appropriate if connection fails.
        # However, the agent.chat method already catches errors and returns a polite message.
        # So we shouldn't actually reach here unless validation fails.
        # But if we receive a string from agent.chat, we return it.
        # If agent.chat raised, we are here.
        raise HTTPException(status_code=500, detail="Internal AI error")
