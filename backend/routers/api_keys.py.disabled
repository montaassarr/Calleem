"""
API Keys Router - Multi-tenant BYOK system
Allows users to securely manage their own API keys for various providers
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from datetime import datetime
import httpx
import logging

from models.business.api_keys import ApiKey, ApiKeyCreate, ApiKeyResponse
from models.business.business_config import BusinessConfig
from database.mongo_config import get_database
from routers.users import get_current_user
from utils.encryption import encrypt_value, decrypt_value, mask_api_key

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/keys",
    tags=["API Keys"],
)


# Provider validation endpoints
PROVIDER_VALIDATORS = {
    "openai": {
        "url": "https://api.openai.com/v1/models",
        "headers": lambda key: {"Authorization": f"Bearer {key}"},
        "method": "GET"
    },
    "elevenlabs": {
        "url": "https://api.elevenlabs.io/v1/voices",
        "headers": lambda key: {"xi-api-key": key},
        "method": "GET"
    },
    "groq": {
        "url": "https://api.groq.com/openai/v1/models",
        "headers": lambda key: {"Authorization": f"Bearer {key}"},
        "method": "GET"
    },
    "anthropic": {
        "url": "https://api.anthropic.com/v1/messages",
        "headers": lambda key: {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        "method": "POST",
        "body": {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 1,
            "messages": [{"role": "user", "content": "test"}]
        }
    },
    "deepgram": {
        "url": "https://api.deepgram.com/v1/projects",
        "headers": lambda key: {"Authorization": f"Token {key}"},
        "method": "GET"
    },
    "assemblyai": {
        "url": "https://api.assemblyai.com/v2/transcript",
        "headers": lambda key: {"authorization": key},
        "method": "GET"
    }
}


async def validate_api_key(provider: str, api_key: str) -> bool:
    """
    Validate an API key by making a test request to the provider
    
    Args:
        provider: Provider name (e.g., "openai", "elevenlabs")
        api_key: The API key to validate
        
    Returns:
        True if valid, False otherwise
    """
    if provider not in PROVIDER_VALIDATORS:
        logger.warning(f"No validator for provider: {provider}")
        return True  # Skip validation for unknown providers
    
    validator = PROVIDER_VALIDATORS[provider]
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = validator["headers"](api_key)
            
            if validator["method"] == "GET":
                response = await client.get(validator["url"], headers=headers)
            else:
                response = await client.post(
                    validator["url"],
                    headers=headers,
                    json=validator.get("body", {})
                )
            
            # Accept 2xx or specific error codes that indicate auth worked
            if response.status_code < 300:
                return True
            elif response.status_code == 400 and provider == "anthropic":
                # Anthropic returns 400 for minimal test request, but auth worked
                return True
            else:
                logger.warning(f"Validation failed for {provider}: {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"Error validating {provider} key: {e}")
        return False


@router.get("", response_model=List[ApiKeyResponse])
async def list_api_keys(current_user: dict = Depends(get_current_user)):
    """
    List all API keys for the current user's tenant (masked)
    """
    db = get_database()
    tenant_id = current_user.get("tenant_id")
    
    if not tenant_id:
        raise HTTPException(status_code=400, detail="User has no tenant_id")
    
    # Get business config
    config = await db.business_config.find_one({"tenant_id": tenant_id})
    
    if not config or "api_keys" not in config:
        return []
    
    # Return masked keys only
    return [
        ApiKeyResponse(
            id=key["id"],
            provider=key["provider"],
            name=key["name"],
            masked_key=key["masked_key"],
            created_at=key["created_at"],
            last_used=key.get("last_used"),
            is_valid=key.get("is_valid", True)
        )
        for key in config["api_keys"]
    ]


@router.post("", response_model=ApiKeyResponse, status_code=status.HTTP_201_CREATED)
async def add_api_key(
    key_data: ApiKeyCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Add a new API key for a provider
    Validates the key before storing
    """
    db = get_database()
    tenant_id = current_user.get("tenant_id")
    
    if not tenant_id:
        raise HTTPException(status_code=400, detail="User has no tenant_id")
    
    # Validate the key
    is_valid = await validate_api_key(key_data.provider, key_data.api_key)
    
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid API key for {key_data.provider}. Please check your key and try again."
        )
    
    # Encrypt the key
    try:
        encrypted_key = encrypt_value(key_data.api_key)
        masked_key = mask_api_key(key_data.api_key)
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        raise HTTPException(status_code=500, detail="Failed to encrypt API key")
    
    # Create API key object
    new_key = ApiKey(
        provider=key_data.provider,
        name=key_data.name,
        masked_key=masked_key,
        encrypted_key=encrypted_key,
        is_valid=True
    )
    
    # Get or create business config
    config = await db.business_config.find_one({"tenant_id": tenant_id})
    
    if not config:
        # Create new config
        config = {
            "tenant_id": tenant_id,
            "business_name": "My Business",
            "timezone": "UTC",
            "api_keys": []
        }
    
    # Add key to list
    if "api_keys" not in config:
        config["api_keys"] = []
    
    config["api_keys"].append(new_key.model_dump())
    
    # Update database
    await db.business_config.update_one(
        {"tenant_id": tenant_id},
        {"$set": {"api_keys": config["api_keys"]}},
        upsert=True
    )
    
    logger.info(f"Added {key_data.provider} key for tenant {tenant_id}")
    
    return ApiKeyResponse(
        id=new_key.id,
        provider=new_key.provider,
        name=new_key.name,
        masked_key=new_key.masked_key,
        created_at=new_key.created_at,
        last_used=new_key.last_used,
        is_valid=new_key.is_valid
    )


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete an API key
    """
    db = get_database()
    tenant_id = current_user.get("tenant_id")
    
    if not tenant_id:
        raise HTTPException(status_code=400, detail="User has no tenant_id")
    
    # Get config
    config = await db.business_config.find_one({"tenant_id": tenant_id})
    
    if not config or "api_keys" not in config:
        raise HTTPException(status_code=404, detail="API key not found")
    
    # Remove key
    original_length = len(config["api_keys"])
    config["api_keys"] = [k for k in config["api_keys"] if k["id"] != key_id]
    
    if len(config["api_keys"]) == original_length:
        raise HTTPException(status_code=404, detail="API key not found")
    
    # Update database
    await db.business_config.update_one(
        {"tenant_id": tenant_id},
        {"$set": {"api_keys": config["api_keys"]}}
    )
    
    logger.info(f"Deleted key {key_id} for tenant {tenant_id}")
    
    return None


async def get_decrypted_key(tenant_id: str, provider: str) -> str:
    """
    Internal function to get a decrypted API key for a provider
    Used by other services to proxy requests
    
    Args:
        tenant_id: The tenant ID
        provider: Provider name
        
    Returns:
        Decrypted API key
        
    Raises:
        HTTPException if key not found or decryption fails
    """
    db = get_database()
    config = await db.business_config.find_one({"tenant_id": tenant_id})
    
    if not config or "api_keys" not in config:
        raise HTTPException(
            status_code=404,
            detail=f"No API key configured for {provider}"
        )
    
    # Find the key for this provider
    provider_key = None
    for key in config["api_keys"]:
        if key["provider"] == provider and key.get("is_valid", True):
            provider_key = key
            break
    
    if not provider_key:
        raise HTTPException(
            status_code=404,
            detail=f"No valid API key found for {provider}"
        )
    
    # Decrypt
    try:
        decrypted = decrypt_value(provider_key["encrypted_key"])
        
        # Update last_used timestamp
        await db.business_config.update_one(
            {"tenant_id": tenant_id, "api_keys.id": provider_key["id"]},
            {"$set": {"api_keys.$.last_used": datetime.utcnow()}}
        )
        
        return decrypted
    except Exception as e:
        logger.error(f"Decryption error for {provider}: {e}")
        raise HTTPException(status_code=500, detail="Failed to decrypt API key")
