from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import logging
from datetime import datetime, timedelta
from uuid import uuid4
from bson import ObjectId

from database.mongo_config import get_database
from routers.users import get_current_user
from services.livekit_service import livekit_service
from utils.error_logger import error_logger, ErrorCategory, ErrorLevel

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


class VoiceAgentToggleRequest(BaseModel):
    enabled: bool = True


class PreviewSessionRequest(BaseModel):
    """Optional overrides when creating a LiveKit preview session."""
    identity: Optional[str] = None
    room_name: Optional[str] = None


class OutboundCallRequest(BaseModel):
    to_number: str = Field(..., pattern=r"^\+?[0-9]{7,15}$")
    from_number: Optional[str] = Field(None, pattern=r"^\+?[0-9]{7,15}$")
    metadata: Optional[Dict[str, Any]] = None


class NumberPurchaseRequest(BaseModel):
    country: str = Field(..., min_length=2, max_length=2)
    phone_number: str = Field(..., pattern=r"^\+?[0-9]{7,15}$")


class NumberSearchResponse(BaseModel):
    country: str
    numbers: List[Dict[str, Any]]


@router.get("/tenant-config/{tenant_id}")
async def get_tenant_agent_config(tenant_id: str):
    """
    Get tenant's agent configuration for LiveKit agent workers.
    This endpoint is called by self-hosted LiveKit agents to get tenant-specific settings.
    
    Returns decrypted API keys and agent configuration.
    """
    logger.info(f"🔍 Fetching tenant config for: {tenant_id}")
    db = get_database()
    
    # Get tenant config
    config = await db.business_config.find_one({"tenant_id": tenant_id})
    logger.info(f"📊 Config found: {config is not None}")
    
    # Auto-create business_config if it doesn't exist
    if not config:
        logger.warning(f"⚠️  business_config not found for tenant {tenant_id}, creating default...")
        
        # Try to get tenant info for business name
        try:
            tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
        except:
            # If tenant_id is not a valid ObjectId, try as string
            tenant = await db.tenants.find_one({"tenant_id": tenant_id}) or await db.tenants.find_one({"_id": tenant_id})
        
        business_name = tenant.get("name", "My Business") if tenant else "My Business"
        
        # Create default business_config
        config = {
            "tenant_id": tenant_id,
            "business_name": business_name,
            "timezone": "UTC",
            "api_keys": [],
            "features_enabled": {
                "voice_agent": False
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.business_config.insert_one(config)
        logger.info(f"✅ Created default business_config for tenant {tenant_id}")
    
    # Get agent configuration
    agent = await db.agents.find_one({"tenant_id": tenant_id, "status": "active"})
    
    # Decrypt API keys from the api_keys array
    from utils.encryption import decrypt_value
    
    api_keys = {}
    
    # Check if api_keys array exists (new format)
    if config.get("api_keys") and isinstance(config["api_keys"], list):
        logger.info(f"Found {len(config['api_keys'])} API keys in array format")
        for key_obj in config["api_keys"]:
            provider = key_obj.get("provider", "").lower()
            encrypted_key = key_obj.get("encrypted_key", "")
            
            logger.info(f"Processing {provider}: encrypted_key={encrypted_key[:20] if encrypted_key else None}...")
            
            if encrypted_key and provider:
                try:
                    decrypted_key = decrypt_value(encrypted_key)
                    if decrypted_key:
                        api_keys[provider] = decrypted_key
                        logger.info(f"✅ Successfully decrypted {provider} API key")
                    else:
                        logger.error(f"❌ Decryption returned None for {provider}")
                except Exception as e:
                    logger.warning(f"Failed to decrypt {provider} key for tenant {tenant_id}: {e}")
    
    # Fallback: check old format (direct fields)
    else:
        encrypted_fields = ["groq_api_key", "openai_api_key", "elevenlabs_api_key"]
        for field in encrypted_fields:
            if config.get(field):
                try:
                    api_keys[field.replace("_api_key", "")] = decrypt_value(config[field])
                except Exception as e:
                    logger.warning(f"Failed to decrypt {field} for tenant {tenant_id}: {e}")
    
    # Determine which voice provider to use based on available API keys
    voice_provider = "cartesia"  # Default to Cartesia
    voice_id = None
    
    if agent:
        agent_voice_settings = agent.get("voice_settings", {})
        requested_provider = agent_voice_settings.get("provider", "").lower()
        agent_voice_id = agent_voice_settings.get("voice_id")
        
        # Use agent's requested provider if we have the API key for it
        if requested_provider == "elevenlabs" and "elevenlabs" in api_keys:
            voice_provider = "elevenlabs"
            voice_id = agent_voice_id
        elif requested_provider == "cartesia" or not requested_provider:
            # Cartesia doesn't need an API key (or use default)
            voice_provider = "cartesia"
            voice_id = agent_voice_id or "79a125e8-cd45-4c13-8a67-188112f4dd22"
        elif requested_provider == "openai" and "openai" in api_keys:
            voice_provider = "openai"
            voice_id = agent_voice_id or "alloy"
    else:
        # No agent configured, use Cartesia with default voice
        voice_id = "79a125e8-cd45-4c13-8a67-188112f4dd22"
    
    # Build response with both nested and top-level fields for compatibility
    llm_model = agent.get("llm_model", "openai/gpt-4o-mini") if agent else "openai/gpt-4o-mini"
    stt_model = agent.get("stt_model", "deepgram/nova-3") if agent else "deepgram/nova-3"
    tts_model = agent.get("tts_model", "cartesia/sonic-2") if agent else "cartesia/sonic-2"
    agent_voice_id = agent.get("voice_id", "79a125e8-cd45-4c13-8a67-188112f4dd22") if agent else "79a125e8-cd45-4c13-8a67-188112f4dd22"
    system_prompt = agent.get("system_prompt") if agent else "You are a helpful AI assistant."
    
    # Use agent's voice_id if set, otherwise use provider default
    if not voice_id:
        voice_id = agent_voice_id
    
    return {
        "tenant_id": tenant_id,
        "api_keys": api_keys,
        "business_name": config.get("business_name", ""),
        # Top-level fields for easy access
        "llm_model": llm_model,
        "stt_model": stt_model,
        "tts_model": tts_model,
        "voice_provider": voice_provider,
        "voice_id": voice_id,
        "system_prompt": system_prompt,
        # Nested config for backwards compatibility
        "agent_config": {
            "system_prompt": system_prompt,
            "llm_model": llm_model,
            "stt_model": stt_model,
            "tts_model": tts_model,
            "voice_id": voice_id,
            "voice_provider": voice_provider,
        },
    }


@router.get("/status")
async def get_voice_agent_status(current_user: dict = Depends(get_current_user)):
    """Return LiveKit readiness plus tenant feature toggle."""

    db = get_database()
    tenant_id = str(current_user["tenant_id"])
    config = await db.business_config.find_one({"tenant_id": tenant_id}) or {}
    features = config.get("features_enabled", {})

    status_payload = livekit_service.get_status()
    status_payload.update(
        {
            "voice_agent_enabled": features.get("voice_agent", False),
            "tenant_id": tenant_id,
        }
    )

    primary_number = await db.voice_numbers.find_one(
        {"tenant_id": tenant_id},
        sort=[("status", 1), ("created_at", -1)],
    )
    if primary_number:
        status_payload["phone_number"] = primary_number.get("phone_number")
        status_payload["number_status"] = primary_number.get("status", "unknown")
        status_payload["country"] = primary_number.get("country")
        status_payload["sip_trunks"] = primary_number.get("trunks")

    return status_payload


@router.get("/history")
async def get_voice_history(current_user: dict = Depends(get_current_user)):
    """Return recorded call history from MongoDB voice_calls collection."""

    db = get_database()
    tenant_id = current_user.get("tenant_id")
    cursor = db.voice_calls.find({"tenant_id": tenant_id}).sort("created_at", -1).limit(100)
    calls = await cursor.to_list(None)
    for call in calls:
        call["id"] = str(call.pop("_id"))
    return calls


@router.post("/call")
async def start_outbound_call(
    payload: OutboundCallRequest,
    current_user: dict = Depends(get_current_user),
):
    tenant_id = str(current_user["tenant_id"])
    db = get_database()

    number_doc = await db.voice_numbers.find_one({"tenant_id": tenant_id}, sort=[("status", 1), ("created_at", -1)])
    caller_id = payload.from_number or (number_doc or {}).get("phone_number")

    if not caller_id:
        raise HTTPException(status_code=400, detail="Provision a LiveKit number before placing outbound calls")

    livekit_response = await livekit_service.start_outbound_call(
        tenant_id=tenant_id,
        to_number=payload.to_number,
        from_number=caller_id,
        metadata=payload.metadata,
    )

    call_record = {
        "tenant_id": tenant_id,
        "livekit_room": livekit_response.get("room") or livekit_response.get("call_id"),
        "status": "queued",
        "direction": "outbound",
        "customer_number": payload.to_number,
        "caller_id": caller_id,
        "metadata": payload.metadata or {},
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    await db.voice_calls.insert_one(call_record)

    return {
        "status": "queued",
        "call": livekit_response,
    }


@router.post("/webrtc/test")
async def create_preview_session(
    body: PreviewSessionRequest = PreviewSessionRequest(),
    current_user: dict = Depends(get_current_user),
):
    """Create a temporary LiveKit room + token so the dashboard can run a test call."""
    
    try:
        # Validate tenant_id
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            logger.error("User has no tenant_id", extra={"user_id": current_user.get("id")})
            raise HTTPException(
                status_code=400,
                detail="User account is missing tenant_id. Please contact support."
            )
        
        tenant_id = str(tenant_id)
        user_id = str(current_user.get("id", tenant_id))
        
        logger.info(f"Creating preview session for tenant {tenant_id}, user {user_id}")

        # First, create the room with tenant metadata
        room_name = f"preview-{tenant_id}-{uuid4().hex[:6]}" if not body.room_name else body.room_name
        
        # Try to create room (may already exist, which is fine)
        try:
            await livekit_service.create_room(
                room_name=room_name,
                metadata={
                    "tenant_id": tenant_id,
                    "session_type": "preview",
                    "agent_name": livekit_service.config.agent_name,
                }
            )
            logger.info(f"✅ Created room {room_name} with tenant_id {tenant_id}")
        except Exception as room_error:
            logger.warning(f"⚠️  Room creation warning (may already exist): {room_error}")
            # Continue - room might already exist, which is acceptable

        # Build the session with token
        try:
            session = livekit_service.build_preview_session(tenant_id=tenant_id, user_id=user_id)
            logger.info(f"✅ Built preview session for tenant {tenant_id}")
        except Exception as session_error:
            logger.error(f"❌ Failed to build preview session: {session_error}", exc_info=True)
            await error_logger.log_error(
                error=session_error,
                category=ErrorCategory.VOICE_AGENT,
                level=ErrorLevel.ERROR,
                context={
                    "tenant_id": tenant_id,
                    "user_id": user_id,
                    "endpoint": "/webrtc/test",
                    "action": "build_preview_session"
                }
            )
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create preview session: {str(session_error)}"
            )
        
        # Override with custom values if provided
        if body.room_name:
            session["room_name"] = body.room_name
        else:
            session["room_name"] = room_name

        # Generate custom token if identity provided
        if body.identity:
            try:
                session["token"] = livekit_service.create_access_token(
                    identity=body.identity,
                    room=session["room_name"],
                    ttl_seconds=900,
                    metadata={"tenant_id": tenant_id, "agent_name": livekit_service.config.agent_name},
                )
                logger.info(f"✅ Generated custom token for identity {body.identity}")
            except Exception as token_error:
                logger.error(f"❌ Failed to create access token: {token_error}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to generate access token: {str(token_error)}"
                )

        # Validate session has all required fields
        required_fields = ["room_name", "token", "url"]
        missing_fields = [field for field in required_fields if not session.get(field)]
        if missing_fields:
            logger.error(f"❌ Session missing required fields: {missing_fields}")
            raise HTTPException(
                status_code=500,
                detail=f"Session creation incomplete. Missing: {', '.join(missing_fields)}"
            )

        logger.info(f"✅ Preview session created successfully: {session.get('room_name')}")
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in create_preview_session: {e}", exc_info=True)
        await error_logger.log_error(
            error=e,
            category=ErrorCategory.VOICE_AGENT,
            level=ErrorLevel.CRITICAL,
            context={
                "tenant_id": current_user.get("tenant_id"),
                "user_id": current_user.get("id"),
                "endpoint": "/webrtc/test",
                "action": "create_preview_session"
            }
        )
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while creating preview session: {str(e)}"
        )


@router.post("/enable")
async def toggle_voice_agent(
    payload: VoiceAgentToggleRequest,
    current_user: dict = Depends(get_current_user)
):
    """Enable or disable the voice agent feature flag for the current tenant"""
    tenant_id = str(current_user["tenant_id"])
    db = get_database()

    update_doc = {
        "$set": {
            "tenant_id": tenant_id,
            "features_enabled.voice_agent": payload.enabled,
            "updated_at": datetime.utcnow()
        },
        "$setOnInsert": {
            "business_name": current_user.get("business_name", "My Business"),
            "timezone": "UTC"
        }
    }

    await db.business_config.update_one(
        {"tenant_id": tenant_id},
        update_doc,
        upsert=True
    )

    updated_config = await db.business_config.find_one({"tenant_id": tenant_id})
    if not updated_config:
        raise HTTPException(status_code=500, detail="Failed to update voice agent setting")

    features = updated_config.get("features_enabled", {})

    return {
        "success": True,
        "features_enabled": features,
        "voice_agent": features.get("voice_agent", False)
    }


@router.get("/stats")
async def get_call_stats(current_user: dict = Depends(get_current_user)):
    """
    Get call statistics for tenant dashboard
    """
    db = get_database()
    tenant_id = current_user.get("tenant_id")
    
    # Calculate date ranges
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)
    
    # Get calls from MongoDB
    all_calls = await db.voice_calls.find({"tenant_id": tenant_id}).to_list(None)
    
    # Calculate stats
    today_calls = [c for c in all_calls if c.get("created_at") and c["created_at"] >= today_start]
    week_calls = [c for c in all_calls if c.get("created_at") and c["created_at"] >= week_start]
    month_calls = [c for c in all_calls if c.get("created_at") and c["created_at"] >= month_start]
    
    # Duration calculations
    total_duration = sum(c.get("duration_seconds", 0) for c in all_calls)
    total_duration_minutes = total_duration / 60
    avg_duration = (total_duration / len(all_calls)) / 60 if all_calls else 0
    
    # Success rate (calls that completed successfully)
    successful = len([c for c in all_calls if c.get("status") == "completed"])
    success_rate = (successful / len(all_calls) * 100) if all_calls else 0
    
    return {
        "today": len(today_calls),
        "this_week": len(week_calls),
        "this_month": len(month_calls),
        "total_duration_minutes": round(total_duration_minutes, 2),
        "average_duration_minutes": round(avg_duration, 2),
        "successful_calls": successful,
        "success_rate": round(success_rate, 2)
    }


@router.get("/numbers/countries")
async def list_supported_countries(current_user: dict = Depends(get_current_user)):
    return await livekit_service.list_supported_countries()


@router.get("/numbers/available", response_model=NumberSearchResponse)
async def search_available_numbers(
    country: str,
    area_code: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    numbers = await livekit_service.list_available_numbers(country=country, area_code=area_code)
    return {"country": country, "numbers": numbers}


@router.get("/numbers")
async def list_purchased_numbers(current_user: dict = Depends(get_current_user)):
    tenant_id = str(current_user["tenant_id"])
    db = get_database()
    numbers = await db.voice_numbers.find({"tenant_id": tenant_id}).sort("created_at", -1).to_list(None)
    for item in numbers:
        item["id"] = str(item.pop("_id"))
    return numbers


@router.post("/numbers/purchase")
async def purchase_number(
    payload: NumberPurchaseRequest,
    current_user: dict = Depends(get_current_user),
):
    tenant_id = str(current_user["tenant_id"])
    db = get_database()

    config = await db.business_config.find_one({"tenant_id": tenant_id}) or {}
    credits = config.get("voice_minutes_balance", 100)
    if credits <= 0:
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, detail="Add voice credits before purchasing numbers")

    number = await livekit_service.purchase_number(
        tenant_id=tenant_id,
        phone_number=payload.phone_number,
        country=payload.country,
    )

    trunks = await livekit_service.ensure_voice_trunks(tenant_id=tenant_id, phone_number=payload.phone_number)

    record = {
        "tenant_id": tenant_id,
        "phone_number": payload.phone_number,
        "country": payload.country,
        "livekit_number_id": number.get("id") or number.get("number_id"),
        "status": number.get("status", "active"),
        "monthly_cost": number.get("monthly_cost"),
        "setup_cost": number.get("setup_cost"),
        "trunks": trunks or number.get("trunks"),
        "metadata": number.get("metadata", {}),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    await db.voice_numbers.update_one(
        {"tenant_id": tenant_id, "phone_number": payload.phone_number},
        {"$set": record},
        upsert=True,
    )

    return record


