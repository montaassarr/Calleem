from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import httpx
import logging
from datetime import datetime

from database.mongo_config import get_database
from routers.users import get_current_user
from models.business.business_config import BusinessConfig
from utils.security import security

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

class CallRequest(BaseModel):
    customer_number: str
    customer_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

async def get_vapi_api_key(tenant_id: str) -> str:
    db = get_database()
    config = await db.business_config.find_one({"tenant_id": tenant_id})
    
    if not config:
        raise HTTPException(status_code=404, detail="Business configuration not found")
        
    api_key = config.get("vapi_api_key")
    if not api_key:
        raise HTTPException(status_code=400, detail="Vapi API key not configured")
        
    # Decrypt the API key (all keys are now encrypted)
    from utils.security import security
    decrypted_key = security.decrypt(api_key)
    if not decrypted_key:
        # If decryption fails, assume it's a legacy unencrypted key
        logger.warning(f"Failed to decrypt vapi_api_key for tenant {tenant_id}, using as-is (legacy)")
        return api_key
    
    return decrypted_key

@router.get("/status")
async def get_agent_status(current_user: dict = Depends(get_current_user)):
    """Get Voice Agent status and details"""
    tenant_id = str(current_user["tenant_id"])
    api_key = await get_vapi_api_key(tenant_id)
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {api_key}"}
        
        # 1. Get Assistant
        # We'll fetch the first assistant for now, or use a stored ID if we had one.
        # Vapi API: GET /assistant
        try:
            resp = await client.get("https://api.vapi.ai/assistant", headers=headers)
            if resp.status_code != 200:
                logger.error(f"Vapi API Error: {resp.text}")
                raise HTTPException(status_code=resp.status_code, detail="Failed to fetch Vapi assistants")
            
            assistants = resp.json()
            if not assistants:
                return {"status": "not_configured", "message": "No assistants found in Vapi account"}
                
            # Use the first assistant
            assistant = assistants[0]
            
            return {
                "status": "active",
                "assistant_id": assistant.get("id"),
                "groq_model": assistant.get("model", {}).get("model", "unknown"),
                "voice_provider": assistant.get("voice", {}).get("provider", "unknown")
            }
            
        except httpx.RequestError as e:
            logger.error(f"Vapi connection error: {e}")
            raise HTTPException(status_code=503, detail="Failed to connect to Vapi API")

@router.get("/history")
async def get_call_history(limit: int = 25, current_user: dict = Depends(get_current_user)):
    """Get call history from Vapi"""
    tenant_id = str(current_user["tenant_id"])
    api_key = await get_vapi_api_key(tenant_id)
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {api_key}"}
        
        try:
            resp = await client.get(f"https://api.vapi.ai/call?limit={limit}", headers=headers)
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail="Failed to fetch call history")
            
            calls = resp.json()
            
            # Transform to match frontend expectation if needed
            # Frontend expects: items: VoiceCallHistoryItem[]
            # VoiceCallHistoryItem: { id, status, created_at, customer: { name, number }, metadata: { notes } }
            
            items = []
            for call in calls:
                items.append({
                    "id": call.get("id"),
                    "status": call.get("status"),
                    "created_at": call.get("createdAt"),
                    "customer": {
                        "name": call.get("customer", {}).get("name"),
                        "number": call.get("customer", {}).get("number")
                    },
                    "metadata": call.get("metadata", {}) # Assuming metadata is passed through
                })
                
            return {"items": items}
            
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail="Failed to connect to Vapi API")

@router.post("/call")
async def start_outbound_call(data: CallRequest, current_user: dict = Depends(get_current_user)):
    """Start an outbound call"""
    tenant_id = str(current_user["tenant_id"])
    api_key = await get_vapi_api_key(tenant_id)
    
    # Get assistant ID (reuse logic or fetch again)
    # Ideally we should store this in DB to avoid extra API call
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {api_key}"}
        
        # Fetch assistant first
        resp = await client.get("https://api.vapi.ai/assistant", headers=headers)
        assistants = resp.json()
        if not assistants:
            raise HTTPException(status_code=400, detail="No assistants found")
        assistant_id = assistants[0].get("id")
        
        # Start Call
        payload = {
            "assistantId": assistant_id,
            "customer": {
                "number": data.customer_number,
                "name": data.customer_name
            },
            "metadata": data.metadata or {}
        }
        
        # If we have a phone number ID configured, use it.
        # For now, let Vapi use default or configured in assistant.
        
        logger.info(f"Initiating Vapi call to {data.customer_number}")
        call_resp = await client.post("https://api.vapi.ai/call", json=payload, headers=headers)
        
        if call_resp.status_code != 201:
            logger.error(f"Vapi Call Error: {call_resp.text}")
            raise HTTPException(status_code=call_resp.status_code, detail=f"Failed to start call: {call_resp.text}")
            
        return call_resp.json()

@router.post("/webrtc/test")
async def webrtc_test(current_user: dict = Depends(get_current_user)):
    """Test WebRTC endpoint (placeholder)"""
    return {"status": "ready"}
