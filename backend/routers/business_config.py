"""
Business Configuration Router
Manages dynamic business settings (multi-tenant ready)
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
import logging
from datetime import datetime

from models.business_config import (
    BusinessConfigResponse,
    BusinessConfigCreate,
    BusinessConfigUpdate
)
from services.config_loader import config_loader
from database.mongo_config import get_database
from routers.users import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_business_id(x_business_id: Optional[str] = Header(None)) -> str:
    """
    Extract business_id from header (for multi-tenancy)
    Defaults to 'default' for single-tenant mode
    """
    return x_business_id or "default"


@router.get("/config", response_model=BusinessConfigResponse)
async def get_business_config(
    business_id: str = Depends(get_business_id),
    db = Depends(get_database)
):
    """
    Get current business configuration
    
    Headers:
        X-Business-ID: Optional business identifier (for multi-tenant)
    """
    try:
        config = await config_loader.get_config(db, business_id)
        
        if not config:
            raise HTTPException(status_code=404, detail="Business configuration not found")
        
        # Convert _id to id for response
        config["id"] = str(config.get("_id", ""))
        
        return config
        
    except Exception as e:
        logger.error(f"Error fetching business config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/config", response_model=BusinessConfigResponse)
async def update_business_config(
    updates: BusinessConfigUpdate,
    business_id: str = Depends(get_business_id),
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Update business configuration
    
    Requires authentication.
    
    Headers:
        X-Business-ID: Optional business identifier
    """
    try:
        # Only include non-None fields
        update_dict = updates.model_dump(exclude_none=True)
        
        if not update_dict:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        # Update configuration
        updated_config = await config_loader.update_config(db, business_id, update_dict)
        
        # Convert _id to id
        updated_config["id"] = str(updated_config.get("_id", ""))
        
        logger.info(f"Business config updated by {current_user.get('username')}: {list(update_dict.keys())}")
        
        return updated_config
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating business config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config/reload")
async def reload_business_config(
    business_id: str = Depends(get_business_id),
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Force reload of business configuration (clears cache)
    
    Useful after updating WhatsApp tokens or AI settings
    """
    try:
        config_loader.invalidate_cache(business_id)
        
        # Load fresh config
        config = await config_loader.get_config(db, business_id)
        
        return {
            "status": "success",
            "message": "Configuration reloaded",
            "business_id": business_id,
            "updated_at": config.get("updated_at")
        }
        
    except Exception as e:
        logger.error(f"Error reloading config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config/ai-prompt")
async def get_ai_prompt(
    business_id: str = Depends(get_business_id),
    db = Depends(get_database)
):
    """
    Get the current AI system prompt
    """
    try:
        config = await config_loader.get_config(db, business_id)
        ai_config = config.get("ai_config", {})
        
        return {
            "system_prompt": ai_config.get("system_prompt", ""),
            "model": ai_config.get("model", "llama-3.3-70b-versatile"),
            "temperature": ai_config.get("temperature", 0.7),
            "max_tokens": ai_config.get("max_tokens", 500)
        }
        
    except Exception as e:
        logger.error(f"Error fetching AI prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/config/ai-prompt")
async def update_ai_prompt(
    prompt_data: dict,
    business_id: str = Depends(get_business_id),
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Update AI system prompt
    
    Body:
    {
        "system_prompt": "Your custom prompt...",
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.7,
        "max_tokens": 500
    }
    """
    try:
        # Get current config
        config = await config_loader.get_config(db, business_id)
        ai_config = config.get("ai_config", {})
        
        # Update AI config fields
        if "system_prompt" in prompt_data:
            ai_config["system_prompt"] = prompt_data["system_prompt"]
        if "model" in prompt_data:
            ai_config["model"] = prompt_data["model"]
        if "temperature" in prompt_data:
            ai_config["temperature"] = prompt_data["temperature"]
        if "max_tokens" in prompt_data:
            ai_config["max_tokens"] = prompt_data["max_tokens"]
        
        # Update config
        updated_config = await config_loader.update_config(
            db,
            business_id,
            {"ai_config": ai_config}
        )
        
        logger.info(f"AI prompt updated by {current_user.get('username')}")
        
        return {
            "status": "success",
            "message": "AI prompt updated",
            "ai_config": updated_config.get("ai_config", {})
        }
        
    except Exception as e:
        logger.error(f"Error updating AI prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config/services")
async def get_services_config(
    business_id: str = Depends(get_business_id),
    db = Depends(get_database)
):
    """
    Get configured services
    """
    try:
        config = await config_loader.get_config(db, business_id)
        services = config.get("services", [])
        
        return {
            "services": services,
            "count": len(services),
            "active_count": len([s for s in services if s.get("is_active", True)])
        }
        
    except Exception as e:
        logger.error(f"Error fetching services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/config/whatsapp")
async def update_whatsapp_config(
    whatsapp_data: dict,
    business_id: str = Depends(get_business_id),
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Update WhatsApp configuration
    
    Body:
    {
        "phone_number_id": "...",
        "access_token": "...",
        "verify_token": "...",
        "webhook_url": "..."
    }
    """
    try:
        # Get current config
        config = await config_loader.get_config(db, business_id)
        whatsapp_config = config.get("whatsapp_config", {})
        
        # Update WhatsApp config fields
        for key in ["phone_number_id", "access_token", "verify_token", "webhook_url"]:
            if key in whatsapp_data:
                whatsapp_config[key] = whatsapp_data[key]
        
        # Update config
        updated_config = await config_loader.update_config(
            db,
            business_id,
            {"whatsapp_config": whatsapp_config}
        )
        
        logger.info(f"WhatsApp config updated by {current_user.get('username')}")
        
        # Return config without sensitive token (only last 4 chars)
        safe_config = dict(whatsapp_config)
        if "access_token" in safe_config and safe_config["access_token"]:
            token = safe_config["access_token"]
            safe_config["access_token"] = f"...{token[-4:]}" if len(token) > 4 else "***"
        
        return {
            "status": "success",
            "message": "WhatsApp configuration updated",
            "whatsapp_config": safe_config
        }
        
    except Exception as e:
        logger.error(f"Error updating WhatsApp config: {e}")
        raise HTTPException(status_code=500, detail=str(e))
