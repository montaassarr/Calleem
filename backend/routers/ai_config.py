"""
AI Configuration Router
Central endpoint for saving AI settings and pushing to LiveKit Cloud instantly
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from database.mongo_config import get_database
from routers.users import get_current_user
from services.livekit_service import livekit_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ai-config",
    tags=["AI Configuration"],
)


class ToolsConfig(BaseModel):
    check_availability: bool = True
    book_appointment: bool = True
    cancel_appointment: bool = True
    update_appointment: bool = False
    get_business_info: bool = True


class VoiceSettings(BaseModel):
    provider: str = "cartesia"
    voice_id: str = "79a125e8-cd45-4c13-8a67-188112f4dd22"


class AIConfigUpdate(BaseModel):
    """Complete AI configuration payload"""
    name: Optional[str] = None
    system_prompt: Optional[str] = None
    llm_model: Optional[str] = None
    stt_model: Optional[str] = None
    tts_model: Optional[str] = None
    voice_id: Optional[str] = None
    voice_provider: Optional[str] = None
    first_message: Optional[str] = None
    tools_config: Optional[ToolsConfig] = None


class AIConfigResponse(BaseModel):
    """Response with current AI configuration"""
    name: str
    system_prompt: str
    llm_model: str
    stt_model: str
    tts_model: str
    voice_id: str
    voice_provider: str
    first_message: str
    tools_config: ToolsConfig
    updated_at: datetime
    livekit_synced: bool = False


@router.get("", response_model=AIConfigResponse)
async def get_ai_config(current_user: dict = Depends(get_current_user)):
    """Get current AI configuration for tenant"""
    db = get_database()
    tenant_id = str(current_user.get("tenant_id"))
    
    if not tenant_id:
        raise HTTPException(status_code=400, detail="User has no tenant_id")
    
    # Get agent config
    agent = await db.agents.find_one({"tenant_id": tenant_id})
    
    if not agent:
        # Return defaults
        return AIConfigResponse(
            name="AI Receptionist",
            system_prompt="You are a friendly AI receptionist. Help customers book appointments and answer questions.",
            llm_model="groq/llama-3.3-70b-versatile",
            stt_model="deepgram/nova-3",
            tts_model="cartesia/sonic-2",
            voice_id="79a125e8-cd45-4c13-8a67-188112f4dd22",
            voice_provider="cartesia",
            first_message="Hello! I'm your AI receptionist. How can I help you today?",
            tools_config=ToolsConfig(),
            updated_at=datetime.utcnow(),
            livekit_synced=False
        )
    
    voice_settings = agent.get("voice_settings", {})
    
    return AIConfigResponse(
        name=agent.get("name", "AI Receptionist"),
        system_prompt=agent.get("system_prompt", ""),
        llm_model=agent.get("llm_model", "groq/llama-3.3-70b-versatile"),
        stt_model=agent.get("stt_model", "deepgram/nova-3"),
        tts_model=agent.get("tts_model", "cartesia/sonic-2"),
        voice_id=voice_settings.get("voice_id", agent.get("voice_id", "")),
        voice_provider=voice_settings.get("provider", "cartesia"),
        first_message=agent.get("greeting_message", "Hello! I'm your AI receptionist."),
        tools_config=ToolsConfig(**agent.get("tools_config", {})) if agent.get("tools_config") else ToolsConfig(),
        updated_at=agent.get("updated_at", datetime.utcnow()),
        livekit_synced=True
    )


@router.put("")
async def update_ai_config(
    config: AIConfigUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update AI configuration and push to LiveKit Cloud instantly.
    
    This updates:
    1. MongoDB agents collection
    2. All active LiveKit rooms for this tenant (via room metadata)
    """
    db = get_database()
    tenant_id = str(current_user.get("tenant_id"))
    
    if not tenant_id:
        raise HTTPException(status_code=400, detail="User has no tenant_id")
    
    # Build update document
    update_fields = {"updated_at": datetime.utcnow()}
    
    if config.name:
        update_fields["name"] = config.name
    if config.system_prompt is not None:
        update_fields["system_prompt"] = config.system_prompt
    if config.llm_model:
        update_fields["llm_model"] = config.llm_model
    if config.stt_model:
        update_fields["stt_model"] = config.stt_model
    if config.tts_model:
        update_fields["tts_model"] = config.tts_model
    if config.voice_id:
        update_fields["voice_id"] = config.voice_id
        update_fields["voice_settings.voice_id"] = config.voice_id
    if config.voice_provider:
        update_fields["voice_settings.provider"] = config.voice_provider
    if config.first_message:
        update_fields["greeting_message"] = config.first_message
    if config.tools_config:
        update_fields["tools_config"] = config.tools_config.model_dump()
    
    # Update MongoDB
    result = await db.agents.update_one(
        {"tenant_id": tenant_id},
        {"$set": update_fields},
        upsert=True
    )
    
    logger.info(f"Updated AI config for tenant {tenant_id}: {list(update_fields.keys())}")
    
    # Push to LiveKit Cloud - update all active rooms for this tenant
    livekit_synced = False
    livekit_rooms_updated = 0
    
    try:
        # Get all active rooms for this tenant
        rooms = await livekit_service.list_rooms(tenant_id=tenant_id)
        
        if rooms:
            # Build new metadata
            new_metadata = {
                "tenant_id": tenant_id,
                "config_version": datetime.utcnow().isoformat(),
                "llm_model": config.llm_model or "groq/llama-3.3-70b-versatile",
                "voice_provider": config.voice_provider or "cartesia",
                "voice_id": config.voice_id or "79a125e8-cd45-4c13-8a67-188112f4dd22",
                "agent_name": livekit_service.config.agent_name,
            }
            
            import json
            metadata_str = json.dumps(new_metadata)
            
            # Update each room
            for room in rooms:
                room_name = room.get("name")
                if room_name:
                    try:
                        await livekit_service.update_room_metadata(room_name, metadata_str)
                        livekit_rooms_updated += 1
                        logger.info(f"Updated LiveKit room {room_name} with new config")
                    except Exception as e:
                        logger.warning(f"Failed to update room {room_name}: {e}")
            
            livekit_synced = livekit_rooms_updated > 0
    except Exception as e:
        logger.warning(f"Failed to sync with LiveKit: {e}")
    
    # Get updated config
    updated_agent = await db.agents.find_one({"tenant_id": tenant_id})
    
    return {
        "success": True,
        "message": "AI configuration updated",
        "livekit_synced": livekit_synced,
        "livekit_rooms_updated": livekit_rooms_updated,
        "updated_fields": list(update_fields.keys()),
        "config": {
            "name": updated_agent.get("name"),
            "llm_model": updated_agent.get("llm_model"),
            "voice_id": updated_agent.get("voice_id"),
            "voice_provider": updated_agent.get("voice_settings", {}).get("provider"),
        }
    }


@router.post("/sync-livekit")
async def sync_livekit_rooms(current_user: dict = Depends(get_current_user)):
    """
    Force sync all LiveKit rooms with current AI config.
    Call this if rooms weren't updated automatically.
    """
    db = get_database()
    tenant_id = str(current_user.get("tenant_id"))
    
    if not tenant_id:
        raise HTTPException(status_code=400, detail="User has no tenant_id")
    
    # Get current agent config
    agent = await db.agents.find_one({"tenant_id": tenant_id})
    
    if not agent:
        raise HTTPException(status_code=404, detail="No agent configuration found")
    
    voice_settings = agent.get("voice_settings", {})
    
    # Build metadata
    import json
    new_metadata = json.dumps({
        "tenant_id": tenant_id,
        "config_version": datetime.utcnow().isoformat(),
        "llm_model": agent.get("llm_model", "groq/llama-3.3-70b-versatile"),
        "voice_provider": voice_settings.get("provider", "cartesia"),
        "voice_id": voice_settings.get("voice_id", agent.get("voice_id", "")),
        "agent_name": livekit_service.config.agent_name,
    })
    
    # Get and update all rooms
    rooms_updated = 0
    rooms_failed = 0
    
    try:
        rooms = await livekit_service.list_rooms(tenant_id=tenant_id)
        
        for room in rooms:
            room_name = room.get("name")
            if room_name:
                try:
                    await livekit_service.update_room_metadata(room_name, new_metadata)
                    rooms_updated += 1
                except Exception as e:
                    logger.warning(f"Failed to update room {room_name}: {e}")
                    rooms_failed += 1
    except Exception as e:
        logger.error(f"Failed to list rooms: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to sync: {str(e)}")
    
    return {
        "success": True,
        "rooms_updated": rooms_updated,
        "rooms_failed": rooms_failed,
        "metadata": json.loads(new_metadata)
    }
