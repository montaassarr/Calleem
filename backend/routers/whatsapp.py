"""
WhatsApp API Router
Handles WhatsApp configuration and status checks
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any
from datetime import datetime
import logging

from database.mongo_config import get_database
from routers.users import get_current_user, get_current_admin
from models.business.business_config import BusinessConfig, BusinessConfigUpdate
from utils.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/status")
async def get_whatsapp_status(current_user: dict = Depends(get_current_user)):
    """
    Check WhatsApp integration status
    Returns connection status and configuration details
    """
    try:
        db = get_database()
        tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
        
        # Get business config
        config = await db.business_config.find_one({"tenant_id": tenant_id})
        
        if not config:
            return {
                "configured": False,
                "status": "not_configured",
                "phone_number": None
            }
            
        whatsapp_config = config.get("whatsapp_config", {}) or {}
        
        # Check if credentials exist
        has_token = bool(whatsapp_config.get("access_token"))
        has_phone_id = bool(whatsapp_config.get("phone_number_id"))
        
        is_configured = has_token and has_phone_id
        
        return {
            "configured": is_configured,
            "status": "connected" if is_configured else "not_configured",
            "phone_number": whatsapp_config.get("phone_number")
        }
        
    except Exception as e:
        logger.error(f"Error checking WhatsApp status: {e}")
        raise HTTPException(status_code=500, detail="Failed to check WhatsApp status")

@router.post("/settings")
async def update_whatsapp_settings(
    settings_update: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_admin)
):
    """Update WhatsApp settings"""
    try:
        db = get_database()
        tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
        
        # Update whatsapp_config in business_config
        await db.business_config.update_one(
            {"tenant_id": tenant_id},
            {"$set": {"whatsapp_config": settings_update, "updated_at": datetime.utcnow()}},
            upsert=True
        )
        
        return {"status": "updated", "message": "WhatsApp settings updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating WhatsApp settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to update WhatsApp settings")
