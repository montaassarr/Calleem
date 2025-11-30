from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any, Optional
from pydantic import BaseModel
from database.mongo_config import get_database
import logging

router = APIRouter(
    prefix="/tenants",
    tags=["tenants"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)

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
