"""
Conversations API Router
Provides access to AI conversation history and Vapi call details
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
import logging

from models.conversation import ConversationResponse
from routers.users import get_current_user
from services.conversation_service import ConversationService

logger = logging.getLogger(__name__)

router = APIRouter()
conversation_service = ConversationService()

@router.get("/", response_model=List[Dict[str, Any]])
async def list_conversations(
    search: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user)
):
    """Return recent conversations ordered by last update"""
    tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
    
    return await conversation_service.list_conversations(
        tenant_id=tenant_id, 
        limit=limit, 
        search=search
    )


@router.get("/{conversation_ref}", response_model=Dict[str, Any])
async def get_conversation(
    conversation_ref: str,
    current_user: dict = Depends(get_current_user)
):
    """Fetch a single conversation by Mongo _id or conversation_id"""
    tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
    
    return await conversation_service.get_conversation(conversation_ref, tenant_id)


@router.get("/{conversation_ref}/details")
async def get_conversation_details(
    conversation_ref: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Fetch comprehensive details for a conversation, including Vapi recording/transcript.
    Useful for 'History' view to play back audio.
    """
    tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
    
    # 1. Get basic info
    conversation = await conversation_service.get_conversation(conversation_ref, tenant_id)
    
    # 2. Try to fetch Vapi details if we have a conversation_id (which usually maps to Vapi Call ID)
    vapi_details = None
    if conversation.get("conversation_id"):
        try:
            vapi_details = await conversation_service.get_vapi_call_details(conversation["conversation_id"])
        except Exception as e:
            logger.warning(f"Could not fetch Vapi details for {conversation_ref}: {e}")
            
    return {
        "conversation": conversation,
        "vapi_details": vapi_details
    }
