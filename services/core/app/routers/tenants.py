"""
Tenant Management API Router
Handles tenant configuration and API key management
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
import logging

from models.tenant import Tenant, TenantConfig, ApiKeys
from routers.auth import get_current_tenant  # Import from auth router
from database.mongo_config import get_database
from utils.encryption import encrypt_api_key, decrypt_api_key

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/me", response_model=Tenant)
async def get_my_tenant(current_tenant: dict = Depends(get_current_tenant)):
    """Get current tenant information"""
    try:
        # Remove password from response
        current_tenant.pop("password", None)
        current_tenant.pop("_id", None)
        
        # Decrypt API keys for display (masked)
        if "api_keys" in current_tenant:
            for key, value in current_tenant["api_keys"].items():
                if value:
                    # Show only last 4 characters
                    current_tenant["api_keys"][key] = f"***{value[-4:]}" if len(value) > 4 else "***"
        
        return Tenant(**current_tenant)
        
    except Exception as e:
        logger.error(f"Error fetching tenant: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch tenant")


@router.put("/me/config", response_model=Tenant)
async def update_tenant_config(
    config: TenantConfig,
    current_tenant: dict = Depends(get_current_tenant)
):
    """Update tenant configuration"""
    try:
        db = get_database()
        tenant_id = current_tenant.get("id")
        
        update_data = config.dict()
        update_data["updated_at"] = datetime.utcnow()
        
        await db.tenants.update_one(
            {"_id": ObjectId(tenant_id)},
            {"$set": {"config": update_data}}
        )
        
        updated_tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
        updated_tenant["id"] = str(updated_tenant["_id"])
        updated_tenant.pop("password", None)
        
        logger.info(f"✅ Tenant config updated: {tenant_id}")
        
        return Tenant(**updated_tenant)
        
    except Exception as e:
        logger.error(f"Error updating tenant config: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update tenant config")


@router.put("/me/api-keys", response_model=dict)
async def update_api_keys(
    api_keys: ApiKeys,
    current_tenant: dict = Depends(get_current_tenant)
):
    """Update tenant API keys (encrypted storage)"""
    try:
        db = get_database()
        tenant_id = current_tenant.get("id")
        
        # Encrypt API keys before storage
        encrypted_keys = {}
        for key, value in api_keys.dict().items():
            if value:
                encrypted_keys[key] = encrypt_api_key(value)
        
        await db.tenants.update_one(
            {"_id": ObjectId(tenant_id)},
            {"$set": {
                "api_keys": encrypted_keys,
                "updated_at": datetime.utcnow(),
                "is_configured": True
            }}
        )
        
        logger.info(f"🔐 API keys updated for tenant: {tenant_id}")
        
        return {"message": "API keys updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating API keys: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update API keys")


@router.post("/lookup-by-phone")
async def lookup_tenant_by_phone(phone: str):
    """
    Lookup tenant by phone number (for n8n workflows)
    This is used by n8n to identify which tenant a call belongs to
    """
    try:
        db = get_database()
        
        # Find tenant by their configured phone number
        tenant = await db.tenants.find_one({"phone": phone})
        
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found for this phone number")
        
        tenant["id"] = str(tenant["_id"])
        tenant.pop("password", None)  # Never expose password
        
        # Decrypt API keys for n8n usage
        if "api_keys" in tenant:
            decrypted_keys = {}
            for key, value in tenant["api_keys"].items():
                if value:
                    decrypted_keys[key] = decrypt_api_key(value)
            tenant["api_keys"] = decrypted_keys
        
        return {
            "tenant_id": tenant["id"],
            "fullname": tenant.get("fullname"),
            "config": tenant.get("config", {}),
            "api_keys": tenant.get("api_keys", {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error looking up tenant: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to lookup tenant")


@router.patch("/{tenant_id}/usage")
async def update_tenant_usage(
    tenant_id: str,
    minutes: float = 0,
    calls: int = 0
):
    """
    Update tenant usage statistics (called by n8n after each call)
    """
    try:
        db = get_database()
        
        await db.tenants.update_one(
            {"_id": ObjectId(tenant_id)},
            {
                "$inc": {
                    "total_minutes": minutes,
                    "total_calls": calls
                },
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        logger.info(f"📊 Usage updated for tenant {tenant_id}: +{minutes}min, +{calls} calls")
        
        return {"message": "Usage updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating usage: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update usage")

