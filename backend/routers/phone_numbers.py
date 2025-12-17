"""
Phone Number Management Router
Handles phone number provisioning, status checks, and removal for tenants
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Body
from pydantic import BaseModel, Field
from datetime import datetime

from database.mongo_config import get_database
from services.vapi_service import VapiService
from services.twilio_service import twilio_service
from models.tenant import PhoneProvider, TwilioCredentials, TenantPhoneConfig
from bson import ObjectId

# Helper to find tenant
async def find_tenant(db, tenant_id_str: str):
    # Try finding by email
    tenant = await db.tenants.find_one({"email": tenant_id_str})
    if tenant:
        return tenant
        
    # Try finding by ObjectId
    try:
        tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id_str)})
        if tenant:
            return tenant
    except:
        pass
    
    # Try finding by string ID (if stored as string)
    return await db.tenants.find_one({"_id": tenant_id_str})

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Phone Numbers"]
)


class ProvisionPhoneRequest(BaseModel):
    """Request model for provisioning a phone number"""
    twilio_account_sid: str = Field(..., description="Twilio Account SID")
    twilio_auth_token: str = Field(..., description="Twilio Auth Token")
    phone_number: str = Field(..., description="Phone number in E.164 format (+1234567890)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "twilio_account_sid": "REDACTED_TWILIO_SID",
                "twilio_auth_token": "your_auth_token_here",
                "phone_number": "+1234567890"
            }
        }


class PhoneStatusResponse(BaseModel):
    """Response model for phone status"""
    has_phone: bool
    phone_number: Optional[str] = None
    provider: Optional[str] = None
    vapi_phone_id: Optional[str] = None
    is_active: bool = False
    created_at: Optional[datetime] = None


@router.post("/provision/{tenant_id}")
async def provision_phone_number(
    tenant_id: str,
    request: ProvisionPhoneRequest = Body(...)
):
    """
    Provision a phone number for a tenant with their Twilio credentials.
    
    This endpoint:
    1. Validates the phone number format
    2. Encrypts the Twilio credentials
    3. Creates a SIP credential in Vapi
    4. Imports the Twilio number to Vapi
    5. Assigns it to the tenant's assistant
    6. Stores encrypted credentials in MongoDB
    """
    db = get_database()
    
    # Find tenant
    tenant = await find_tenant(db, tenant_id)
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Check if tenant already has an active phone
    phone_config = tenant.get("phone_config", {})
    if phone_config.get("is_active"):
        raise HTTPException(
            status_code=400,
            detail=f"Tenant already has an active phone number: {phone_config.get('phone_number')}"
        )
    
    # Validate phone number format
    if not twilio_service.validate_phone_number(request.phone_number):
        raise HTTPException(
            status_code=400,
            detail="Invalid phone number format. Must be E.164 format (+1234567890)"
        )
    
    # Get tenant's Vapi assistant ID
    vapi_assistant_id = tenant.get("vapi_assistant_id")
    if not vapi_assistant_id:
        raise HTTPException(
            status_code=400,
            detail="Tenant does not have a Vapi assistant configured"
        )
    
    vapi_service = VapiService()
    
    try:
        # Step 1: Encrypt Twilio credentials
        logger.info(f"Encrypting Twilio credentials for tenant {tenant_id}")
        encrypted_creds = twilio_service.encrypt_credentials(
            request.twilio_account_sid,
            request.twilio_auth_token
        )
        
        # Step 2: Create SIP credential in Vapi
        logger.info(f"Creating SIP credential in Vapi for tenant {tenant_id}")
        credential_result = await vapi_service.create_sip_credential(
            account_sid=request.twilio_account_sid,
            auth_token=request.twilio_auth_token,
            name=f"Twilio - {tenant.get('name', tenant.get('email'))}"
        )
        credential_id = credential_result.get("id")
        
        # Step 3: Import Twilio number to Vapi
        logger.info(f"Importing Twilio number {request.phone_number} to Vapi")
        phone_result = await vapi_service.import_twilio_number(
            phone_number=request.phone_number,
            assistant_id=vapi_assistant_id,
            credential_id=credential_id,
            name=f"{tenant.get('name', 'Tenant')} Phone"
        )
        vapi_phone_id = phone_result.get("id")
        
        # Step 4: Store encrypted credentials and phone config in MongoDB
        phone_config_data = {
            "vapi_phone_number_id": vapi_phone_id,
            "phone_number": request.phone_number,
            "phone_provider": PhoneProvider.TWILIO.value,
            "twilio_credentials": {
                "account_sid_encrypted": encrypted_creds["account_sid_encrypted"],
                "auth_token_encrypted": encrypted_creds["auth_token_encrypted"],
                "phone_number": request.phone_number,
                "credential_id": credential_id
            },
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Update tenant in database
        await db.tenants.update_one(
            {"_id": tenant["_id"]},
            {
                "$set": {
                    "phone_config": phone_config_data,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Successfully provisioned phone number for tenant {tenant_id}")
        
        return {
            "success": True,
            "phone_number": request.phone_number,
            "provider": PhoneProvider.TWILIO.value,
            "vapi_phone_id": vapi_phone_id,
            "message": f"Phone number {request.phone_number} successfully provisioned"
        }
        
    except ValueError as e:
        # Validation or encryption error
        logger.error(f"Validation error provisioning phone: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        # Vapi API or other errors
        logger.error(f"Error provisioning phone number: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to provision phone number: {str(e)}"
        )


@router.get("/status/{tenant_id}", response_model=PhoneStatusResponse)
async def get_phone_status(tenant_id: str):
    """
    Get the current phone number status for a tenant.
    Returns phone configuration and Vapi status.
    """
    db = get_database()
    
    # Find tenant
    tenant = await find_tenant(db, tenant_id)
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    phone_config = tenant.get("phone_config", {})
    
    # If no phone configured
    if not phone_config or not phone_config.get("is_active"):
        return PhoneStatusResponse(
            has_phone=False,
            is_active=False
        )
    
    # Return phone status
    return PhoneStatusResponse(
        has_phone=True,
        phone_number=phone_config.get("phone_number"),
        provider=phone_config.get("phone_provider"),
        vapi_phone_id=phone_config.get("vapi_phone_number_id"),
        is_active=phone_config.get("is_active", False),
        created_at=phone_config.get("created_at")
    )


@router.delete("/{tenant_id}")
async def remove_phone_number(tenant_id: str, delete_from_vapi: bool = False):
    """
    Remove/deactivate phone number from tenant.
    
    Args:
        tenant_id: Tenant identifier (email or ID)
        delete_from_vapi: If True, also delete the phone number from Vapi
    """
    db = get_database()
    
    # Find tenant
    tenant = await find_tenant(db, tenant_id)
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    phone_config = tenant.get("phone_config", {})
    
    if not phone_config or not phone_config.get("is_active"):
        raise HTTPException(status_code=400, detail="No active phone number to remove")
    
    try:
        # Optionally delete from Vapi
        if delete_from_vapi and phone_config.get("vapi_phone_number_id"):
            vapi_service = VapiService()
            vapi_phone_id = phone_config["vapi_phone_number_id"]
            logger.info(f"Deleting phone number {vapi_phone_id} from Vapi")
            await vapi_service.delete_phone_number(vapi_phone_id)
        
        # Deactivate in database
        await db.tenants.update_one(
            {"_id": tenant["_id"]},
            {
                "$set": {
                    "phone_config.is_active": False,
                    "phone_config.updated_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Removed phone number for tenant {tenant_id}")
        
        return {
            "success": True,
            "message": "Phone number removed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error removing phone number: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to remove phone number: {str(e)}"
        )


@router.post("/sync/{tenant_id}")
async def sync_phone_number(tenant_id: str):
    """
    Sync tenant phone configuration from Vapi.
    Useful when numbers are linked manually in the Vapi dashboard.
    """
    db = get_database()

    # Find tenant
    tenant = await find_tenant(db, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    assistant_id = tenant.get("vapi_assistant_id")
    if not assistant_id:
        raise HTTPException(status_code=400, detail="Tenant has no assistant")

    vapi = VapiService()
    try:
        numbers = await vapi.list_phone_numbers()
        # Find a number assigned to this assistant
        match = next((n for n in numbers if n.get("assistantId") == assistant_id), None)

        if not match:
            # No number found; mark inactive
            await db.tenants.update_one(
                {"_id": tenant["_id"]},
                {"$set": {"phone_config.is_active": False, "updated_at": datetime.utcnow()}}
            )
            return {"success": True, "synced": False, "message": "No phone linked in Vapi"}

        phone_number = match.get("number") or match.get("customer", {}).get("number")
        phone_config_data = {
            "vapi_phone_number_id": match.get("id"),
            "phone_number": phone_number,
            "phone_provider": PhoneProvider.TWILIO.value,
            "is_active": True,
            "created_at": tenant.get("phone_config", {}).get("created_at") or datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        await db.tenants.update_one(
            {"_id": tenant["_id"]},
            {"$set": {"phone_config": phone_config_data, "updated_at": datetime.utcnow()}}
        )

        return {
            "success": True,
            "synced": True,
            "phone_number": phone_number,
            "vapi_phone_id": match.get("id")
        }

    except Exception as e:
        logger.error(f"Failed to sync phone number: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")
