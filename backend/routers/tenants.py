from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any, Optional
from pydantic import BaseModel
from database.mongo_config import get_database
from bson import ObjectId
from datetime import datetime
import logging

from routers.users import get_current_user

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/me")
async def get_current_tenant(current_user: dict = Depends(get_current_user)):
    """Get the current user's tenant information"""
    db = get_database()
    tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
    
    if not tenant_id:
        raise HTTPException(status_code=404, detail="No tenant associated with user")
    
    try:
        tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
    except:
        tenant = await db.tenants.find_one({"tenant_id": tenant_id})
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Convert ObjectId to string
    tenant["id"] = str(tenant["_id"])
    tenant["_id"] = str(tenant["_id"])
    
    return tenant


class TenantLookupRequest(BaseModel):
    phone: str

class TenantLookupResponse(BaseModel):
    tenant_id: str
    business_name: str
    phone_number: Optional[str] = None

@router.post("/lookup-by-phone", response_model=TenantLookupResponse)
async def lookup_tenant_by_phone(request: TenantLookupRequest = Body(...)):
    """
    Lookup a tenant by their business phone number.
    Used by N8N workflows to route calls to the correct tenant.
    """
    db = get_database()
    
    # Normalize phone number (basic normalization)
    phone = request.phone.strip()
    if not phone:
        raise HTTPException(status_code=400, detail="Phone number is required")
        
    # Search in business_config
    # We search for the phone number in the business_config collection
    # Note: In a real multi-tenant system, we might need a more robust phone mapping
    # For now, we assume the 'phone_number' field in business_config matches
    
    # Try exact match first
    tenant = await db.business_config.find_one({"phone_number": phone})
    
    # If not found, try to search in users collection (owner's phone)
    if not tenant:
        user = await db.users.find_one({"phone": phone, "role": "owner"})
        if user:
            tenant_id = user.get("tenant_id")
            if tenant_id:
                tenant = await db.business_config.find_one({"tenant_id": tenant_id})
    
    # If still not found, and we are in development/single-tenant mode, 
    # we might want to return the default tenant if it's the only one?
    # But for strict multi-tenancy, we should fail.
    
    # FALLBACK FOR DEMO: If only one tenant exists, return it
    # This is helpful for testing when phone numbers might not match exactly
    if not tenant:
        count = await db.business_config.count_documents({})
        if count == 1:
            tenant = await db.business_config.find_one({})
            logger.info(f"Tenant lookup: Returning default tenant (only 1 found) for phone {phone}")
    
    if not tenant:
        logger.warning(f"Tenant lookup failed for phone: {phone}")
        raise HTTPException(status_code=404, detail="Tenant not found for this phone number")
        
    return TenantLookupResponse(
        tenant_id=tenant.get("tenant_id") or str(tenant.get("_id")),
        business_name=tenant.get("business_name", "Unknown Business"),
        phone_number=tenant.get("phone_number")
    )


class OnboardingCompleteRequest(BaseModel):
    """Request to mark onboarding as complete"""
    groq_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    n8n_url: Optional[str] = None
    n8n_api_key: Optional[str] = None
    business_name: Optional[str] = None
    business_description: Optional[str] = None
    industry: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    timezone: Optional[str] = None


@router.patch("/me/complete-onboarding")
async def complete_onboarding(
    request: OnboardingCompleteRequest,
    tenant_id: str = Depends(lambda: "temp_tenant")  # TODO: Get from auth
):
    """
    Mark tenant onboarding as complete and save configuration.
    Called after user finishes onboarding wizard.
    """
    db = get_database()
    
    # Find tenant
    try:
        tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
    except:
        # If not ObjectId, try as string
        tenant = await db.tenants.find_one({"tenant_id": tenant_id})
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Update tenant with onboarding data
    update_data = {
        "onboarding_completed": True,
        "is_configured": True,
        "updated_at": datetime.utcnow()
    }
    
    # Add optional fields if provided
    if request.business_name:
        update_data["name"] = request.business_name
    if request.business_description:
        update_data["business_description"] = request.business_description
    if request.industry:
        update_data["industry"] = request.industry
    if request.phone:
        update_data["phone"] = request.phone
    if request.website:
        update_data["website"] = request.website
    if request.timezone:
        update_data["timezone"] = request.timezone
    
    # Save API keys to separate encrypted collection (TODO: Implement encryption)
    if request.groq_api_key or request.openai_api_key:
        api_keys = {}
        if request.groq_api_key:
            api_keys["groq"] = request.groq_api_key
        if request.openai_api_key:
            api_keys["openai"] = request.openai_api_key
        
        # Store in api_keys collection (should be encrypted in production)
        await db.api_keys.update_one(
            {"tenant_id": str(tenant["_id"])},
            {
                "$set": {
                    "tenant_id": str(tenant["_id"]),
                    "keys": api_keys,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
    
    # Save n8n config
    if request.n8n_url or request.n8n_api_key:
        n8n_config = {}
        if request.n8n_url:
            n8n_config["url"] = request.n8n_url
        if request.n8n_api_key:
            n8n_config["api_key"] = request.n8n_api_key
        
        update_data["n8n_config"] = n8n_config
    
    # Update tenant
    await db.tenants.update_one(
        {"_id": tenant["_id"]},
        {"$set": update_data}
    )
    
    logger.info(f"Onboarding completed for tenant {tenant_id}")
    
    return {
        "success": True,
        "message": "Onboarding completed successfully",
        "tenant_id": str(tenant["_id"])
    }

