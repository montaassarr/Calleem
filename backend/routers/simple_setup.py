"""
Simple API Key Setup Router
=============================
Simplified endpoints for non-technical users to easily add their API keys.

Features:
- Step-by-step validation
- Clear error messages
- Auto-masking for security
- Test before save
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import logging

from routers.users import get_current_user
from routers.api_keys import (
    add_api_key,
    list_api_keys,
    validate_api_key,
    ApiKeyCreate,
    ApiKeyResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()

class SimpleKeySetup(BaseModel):
    """Simplified key setup for non-technical users"""
    provider: str = Field(..., description="Which service? (openai, groq, anthropic, elevenlabs)")
    api_key: str = Field(..., description="Your API key from the provider")
    key_name: Optional[str] = Field(None, description="Optional: Give it a name (e.g., 'My OpenAI Key')")

class KeySetupResponse(BaseModel):
    """User-friendly response"""
    success: bool
    message: str
    key_id: Optional[str] = None
    provider: str
    masked_key: Optional[str] = None

@router.post("/setup/api-key", response_model=KeySetupResponse)
async def simple_api_key_setup(
    data: SimpleKeySetup,
    current_user: dict = Depends(get_current_user)
):
    """
    🔑 Easy API Key Setup for Non-Technical Users
    
    Just provide:
    1. Which service (openai, groq, anthropic, elevenlabs)
    2. Your API key
    3. Optional name for the key
    
    We'll test it and save it securely!
    """
    tenant_id = str(current_user["tenant_id"])
    
    # Step 1: Validate the API key works
    logger.info(f"Testing {data.provider} API key for tenant {tenant_id}")
    
    try:
        is_valid = await validate_api_key(data.provider, data.api_key)
        
        if not is_valid:
            return KeySetupResponse(
                success=False,
                message=f"❌ The {data.provider.upper()} API key didn't work. Please check:\n"
                        f"1. The key is correct\n"
                        f"2. The key has proper permissions\n"
                        f"3. Your {data.provider.upper()} account is active",
                provider=data.provider
            )
    
    except Exception as e:
        logger.error(f"Error validating {data.provider} key: {e}")
        return KeySetupResponse(
            success=False,
            message=f"❌ Couldn't test the API key. Error: {str(e)}",
            provider=data.provider
        )
    
    # Step 2: Save the key
    key_name = data.key_name or f"My {data.provider.upper()} Key"
    
    try:
        key_data = ApiKeyCreate(
            provider=data.provider,
            key_name=key_name,
            api_key=data.api_key
        )
        
        result = await add_api_key(key_data, current_user)
        
        return KeySetupResponse(
            success=True,
            message=f"✅ Great! Your {data.provider.upper()} API key is saved and working!\n"
                    f"We'll use your key when making {data.provider} API calls.",
            key_id=result.key_id,
            provider=data.provider,
            masked_key=result.masked_key
        )
    
    except Exception as e:
        logger.error(f"Error saving {data.provider} key: {e}")
        return KeySetupResponse(
            success=False,
            message=f"❌ The key works, but we couldn't save it. Error: {str(e)}",
            provider=data.provider
        )

@router.get("/setup/my-keys")
async def get_my_keys(current_user: dict = Depends(get_current_user)):
    """
    📋 See Your API Keys
    
    Shows which keys you've added and their status.
    """
    tenant_id = str(current_user["tenant_id"])
    
    try:
        keys = await list_api_keys(tenant_id)
        
        # Simplify the response for non-technical users
        simplified = []
        for key in keys:
            simplified.append({
                "provider": key.provider.upper(),
                "name": key.key_name,
                "masked_key": key.masked_key,
                "status": "✅ Working" if key.is_valid else "⚠️ Needs attention",
                "added_on": key.created_at.strftime("%B %d, %Y") if key.created_at else "Unknown"
            })
        
        if not simplified:
            return {
                "message": "You haven't added any API keys yet.",
                "keys": [],
                "platform_fallback": "Don't worry! We'll use our platform keys so you can get started immediately."
            }
        
        return {
            "message": f"You have {len(simplified)} API key(s) configured.",
            "keys": simplified,
            "note": "These are your personal API keys. We'll use them first before using platform keys."
        }
    
    except Exception as e:
        logger.error(f"Error fetching keys: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/setup/providers")
async def get_available_providers():
    """
    📖 What Services Can I Add Keys For?
    
    Shows available AI providers and how to get API keys.
    """
    return {
        "providers": [
            {
                "id": "openai",
                "name": "OpenAI",
                "description": "Powers AI conversations (GPT-4, GPT-3.5)",
                "get_key_url": "https://platform.openai.com/api-keys",
                "instructions": [
                    "1. Go to platform.openai.com",
                    "2. Sign in or create account",
                    "3. Go to API Keys section",
                    "4. Create new secret key",
                    "5. Copy and paste it here"
                ],
                "required_for": ["AI conversations", "Smart responses"],
                "priority": "medium"
            },
            {
                "id": "groq",
                "name": "Groq",
                "description": "Fast AI processing (alternative to OpenAI)",
                "get_key_url": "https://console.groq.com/keys",
                "instructions": [
                    "1. Visit console.groq.com",
                    "2. Create free account",
                    "3. Navigate to API Keys",
                    "4. Generate new key",
                    "5. Copy and save here"
                ],
                "required_for": ["AI conversations (faster)", "Cost savings"],
                "priority": "low"
            }
        ],
        "note": "You don't need to add every key immediately. We provide platform fallbacks so you can get started right away!",
        "recommendation": "Start with OpenAI or Groq for conversations. Voice calling now runs on the managed LiveKit stack."
    }

@router.delete("/setup/api-key/{provider}")
async def remove_api_key(
    provider: str,
    current_user: dict = Depends(get_current_user)
):
    """
    🗑️ Remove an API Key
    
    Stop using your own API key. We'll fall back to platform keys.
    """
    tenant_id = str(current_user["tenant_id"])
    
    from database.mongo_config import get_database
    
    try:
        db = await get_database()
        result = await db.api_keys.delete_one({
            "tenant_id": tenant_id,
            "provider": provider
        })
        
        if result.deleted_count == 0:
            return {
                "success": False,
                "message": f"No {provider.upper()} key found to remove."
            }
        
        return {
            "success": True,
            "message": f"✅ Removed your {provider.upper()} API key. We'll use platform keys now.",
            "fallback": "Don't worry, your service will continue working using our platform keys!"
        }
    
    except Exception as e:
        logger.error(f"Error removing {provider} key: {e}")
        raise HTTPException(status_code=500, detail=str(e))
