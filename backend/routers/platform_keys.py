"""
Platform API Keys Router - Admin-only management of shared API keys
==================================================================
Allows platform admin to manage shared API keys for all tenants.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
from enum import Enum
import uuid
import logging

from database.mongo_config import get_database
from routers.users import get_current_user
from utils.encryption import encrypt_value, mask_api_key
from routers.api_keys import validate_api_key

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/platform-keys", tags=["Platform Keys"])


# ============== INLINE MODELS ==============
class ApiProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    ELEVENLABS = "elevenlabs"
    DEEPGRAM = "deepgram"


class KeyTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class PlatformKeyCreate(BaseModel):
    provider: ApiProvider
    tier: KeyTier = KeyTier.FREE
    name: str
    api_key: str  # Plaintext, will be encrypted
    notes: Optional[str] = None


class PlatformKeyResponse(BaseModel):
    id: str
    provider: ApiProvider
    tier: KeyTier
    name: str
    masked_key: str
    is_active: bool
    created_at: datetime


# ============== ENDPOINTS ==============
@router.get("", response_model=List[PlatformKeyResponse])
async def list_platform_keys(current_user: dict = Depends(get_current_user)):
    """List all platform API keys (masked)"""
    db = get_database()
    keys = await db.platform_api_keys.find().to_list(100)
    
    return [
        PlatformKeyResponse(
            id=k.get("id", str(k.get("_id"))),
            provider=k["provider"],
            tier=k.get("tier", "free"),
            name=k["name"],
            masked_key=k["masked_key"],
            is_active=k.get("is_active", True),
            created_at=k.get("created_at", datetime.utcnow())
        )
        for k in keys
    ]


@router.post("", response_model=PlatformKeyResponse, status_code=201)
async def add_platform_key(
    key_data: PlatformKeyCreate,
    current_user: dict = Depends(get_current_user)
):
    """Add a new platform API key"""
    db = get_database()
    
    # Validate
    is_valid = await validate_api_key(key_data.provider.value, key_data.api_key)
    if not is_valid:
        raise HTTPException(400, f"Invalid {key_data.provider.value} key")
    
    # Encrypt
    encrypted_key = encrypt_value(key_data.api_key)
    masked = mask_api_key(key_data.api_key)
    
    new_key = {
        "id": str(uuid.uuid4()),
        "provider": key_data.provider.value,
        "tier": key_data.tier.value,
        "name": key_data.name,
        "masked_key": masked,
        "encrypted_key": encrypted_key,
        "is_active": True,
        "notes": key_data.notes,
        "created_at": datetime.utcnow(),
        "created_by": current_user.get("id")
    }
    
    await db.platform_api_keys.insert_one(new_key)
    logger.info(f"Added platform key: {key_data.provider.value}")
    
    return PlatformKeyResponse(
        id=new_key["id"],
        provider=key_data.provider,
        tier=key_data.tier,
        name=new_key["name"],
        masked_key=new_key["masked_key"],
        is_active=True,
        created_at=new_key["created_at"]
    )


@router.delete("/{key_id}", status_code=204)
async def delete_platform_key(key_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a platform API key"""
    db = get_database()
    result = await db.platform_api_keys.delete_one({"id": key_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Key not found")
    logger.warning(f"Deleted platform key {key_id}")


@router.patch("/{key_id}/toggle")
async def toggle_platform_key(key_id: str, current_user: dict = Depends(get_current_user)):
    """Toggle key active/inactive"""
    db = get_database()
    key = await db.platform_api_keys.find_one({"id": key_id})
    if not key:
        raise HTTPException(404, "Key not found")
    
    new_status = not key.get("is_active", True)
    await db.platform_api_keys.update_one({"id": key_id}, {"$set": {"is_active": new_status}})
    
    return {"id": key_id, "is_active": new_status}
