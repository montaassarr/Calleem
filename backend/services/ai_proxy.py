"""
AI Proxy Service - Key management for multi-tenant providers.
"""

import httpx
import logging
from typing import Optional, Tuple
from enum import Enum
from fastapi import HTTPException
from datetime import datetime

from database.mongo_config import get_database
from routers.api_keys import get_decrypted_key
from utils.encryption import decrypt_value

logger = logging.getLogger(__name__)


class ProviderType(str, Enum):
    """Provider requirement level"""
    REQUIRED = "required"    # Must have BYOK, no fallback
    OPTIONAL = "optional"    # BYOK preferred, platform fallback
    PLATFORM = "platform"    # Always use platform key


class ProviderConfig:
    """Configuration for each provider"""
    def __init__(
        self,
        provider_type: ProviderType,
        name: str,
        reason: str,
        setup_url: Optional[str] = None
    ):
        self.provider_type = provider_type
        self.name = name
        self.reason = reason
        self.setup_url = setup_url


# Provider Configuration Map
PROVIDER_CONFIGS = {
    # === AI ENGINES (OPTIONAL BYOK) ===
    "openai": ProviderConfig(
        provider_type=ProviderType.OPTIONAL,
        name="OpenAI",
        reason="Use your own OpenAI key for direct control, or use our platform key (included in subscription).",
        setup_url="https://platform.openai.com/api-keys"
    ),
    "groq": ProviderConfig(
        provider_type=ProviderType.OPTIONAL,
        name="Groq",
        reason="Use your own Groq key for faster responses, or use our platform key (included in subscription).",
        setup_url="https://console.groq.com/keys"
    ),
    "anthropic": ProviderConfig(
        provider_type=ProviderType.OPTIONAL,
        name="Anthropic Claude",
        reason="Use your own Anthropic key for Claude AI, or use our platform key.",
        setup_url="https://console.anthropic.com/settings/keys"
    ),
    
    # === VOICE PROVIDERS (OPTIONAL) ===
    "elevenlabs": ProviderConfig(
        provider_type=ProviderType.OPTIONAL,
        name="ElevenLabs",
        reason="Use your own ElevenLabs key for custom voices, or use default platform voices.",
        setup_url="https://elevenlabs.io/app/settings/api-keys"
    ),
    
    # === INFRASTRUCTURE (PLATFORM ONLY) ===
    "twilio": ProviderConfig(
        provider_type=ProviderType.PLATFORM,
        name="Twilio",
        reason="We manage phone numbers and SMS infrastructure for you.",
        setup_url=None
    ),
    "n8n": ProviderConfig(
        provider_type=ProviderType.PLATFORM,
        name="n8n Workflows",
        reason="We provide pre-built automation workflows as part of your subscription.",
        setup_url=None
    ),
    "livekit": ProviderConfig(
        provider_type=ProviderType.PLATFORM,
        name="LiveKit Voice Agent",
        reason="Voice calls are handled by the platform-managed LiveKit stack.",
        setup_url=None
    )
}


class AIProxyService:
    """
    Centralized API key management with provider-specific logic
    """
    
    def __init__(self):
        self.db = None
    
    def _get_db(self):
        """Lazy database connection"""
        if not self.db:
            self.db = get_database()
        return self.db
    
    async def get_api_key(
        self, 
        tenant_id: str, 
        provider: str
    ) -> Tuple[str, bool, Optional[str]]:
        """
        Get API key with provider-specific routing logic
        
        Args:
            tenant_id: Tenant ID
            provider: Provider name (openai, groq, etc.)
            
        Returns:
            Tuple of (api_key, is_tenant_byok, platform_key_id)
            
        Raises:
            HTTPException(428) if REQUIRED provider has no BYOK
            HTTPException(503) if OPTIONAL provider has no keys at all
        """
        config = PROVIDER_CONFIGS.get(provider)
        
        if not config:
            raise ValueError(f"Unknown provider: {provider}")
        
        # === STRATEGY 1: REQUIRED (Voice Providers) ===
        if config.provider_type == ProviderType.REQUIRED:
            tenant_key = await self._get_tenant_key(tenant_id, provider)
            
            if not tenant_key:
                # No BYOK found - this is an error for REQUIRED providers
                setup_guide = f"\n\n📖 Get your key here: {config.setup_url}" if config.setup_url else ""
                
                raise HTTPException(
                    status_code=428,  # Precondition Required
                    detail={
                        "error": "api_key_required",
                        "provider": provider,
                        "message": f"❌ {config.name} API key is required.\n\n"
                                 f"💡 Why? {config.reason}{setup_guide}",
                        "setup_url": config.setup_url,
                        "can_fallback": False
                    }
                )
            
            logger.info(f"✅ Using tenant BYOK for {provider} (tenant: {tenant_id})")
            return (tenant_key, True, None)
        
        # === STRATEGY 2: OPTIONAL (AI Engines) ===
        elif config.provider_type == ProviderType.OPTIONAL:
            # Try tenant BYOK first
            tenant_key = await self._get_tenant_key(tenant_id, provider)
            if tenant_key:
                logger.info(f"✅ Using tenant BYOK for {provider} (tenant: {tenant_id})")
                return (tenant_key, True, None)
            
            # Fallback to platform key
            platform_key, key_id = await self._get_platform_key(provider)
            if platform_key:
                logger.info(f"🔄 Using platform key for {provider} (tenant: {tenant_id})")
                await self._log_platform_usage(tenant_id, provider, key_id)
                return (platform_key, False, key_id)
            
            # No keys available at all
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "no_api_key_available",
                    "provider": provider,
                    "message": f"⚠️ No {config.name} API key available.\n\n"
                             f"You can: 1) Add your own key, or 2) Contact support to enable platform key.",
                    "setup_url": config.setup_url,
                    "can_fallback": False
                }
            )
        
        # === STRATEGY 3: PLATFORM ONLY (Infrastructure) ===
        else:  # ProviderType.PLATFORM
            platform_key, key_id = await self._get_platform_key(provider)
            
            if not platform_key:
                logger.error(f"❌ Platform key missing for {provider}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "platform_configuration_error",
                        "provider": provider,
                        "message": f"Platform {config.name} key not configured. Contact support.",
                        "can_fallback": False
                    }
                )
            
            logger.debug(f"🏢 Using platform key for {provider}")
            return (platform_key, False, key_id)
    
    async def _get_tenant_key(self, tenant_id: str, provider: str) -> Optional[str]:
        """Get tenant's BYOK key"""
        try:
            logger.info(f"🔍 Checking for {provider} key for tenant {tenant_id}")
            key = await get_decrypted_key(tenant_id, provider)
            logger.info(f"✅ Found {provider} key: {key[:20] if key else 'None'}...")
            return key
        except Exception as e:
            logger.warning(f"No tenant BYOK for {provider} (tenant {tenant_id}): {e}")
            return None
    
    async def _get_platform_key(self, provider: str) -> Tuple[Optional[str], Optional[str]]:
        """Get platform key for provider"""
        db = self._get_db()
        
        try:
            platform_key_doc = await db.platform_api_keys.find_one({
                "provider": provider,
                "is_active": True,
                "health_status": {"$ne": "failed"}
            })
            
            if not platform_key_doc:
                return (None, None)
            
            decrypted_key = decrypt_value(platform_key_doc["encrypted_key"])
            key_id = platform_key_doc["key_id"]
            
            return (decrypted_key, key_id)
        
        except Exception as e:
            logger.error(f"Error getting platform key for {provider}: {e}")
            return (None, None)
    
    async def _log_platform_usage(
        self, 
        tenant_id: str, 
        provider: str, 
        platform_key_id: str
    ):
        """Log platform key usage for billing"""
        db = self._get_db()
        
        try:
            usage_log = {
                "tenant_id": tenant_id,
                "platform_key_id": platform_key_id,
                "provider": provider,
                "timestamp": datetime.utcnow(),
                "request_count": 1
            }
            
            await db.platform_key_usage_logs.insert_one(usage_log)
            
            # Update platform key usage count
            await db.platform_api_keys.update_one(
                {"key_id": platform_key_id},
                {
                    "$inc": {"usage_count": 1},
                    "$set": {"last_used_at": datetime.utcnow()}
                }
            )
        
        except Exception as e:
            logger.error(f"Error logging platform usage: {e}")
    
    def get_provider_config(self, provider: str) -> Optional[ProviderConfig]:
        """Get configuration for a provider"""
        return PROVIDER_CONFIGS.get(provider)
    
    def get_required_providers(self) -> list:
        """Get list of providers that require BYOK"""
        return [
            {
                "provider": provider,
                "name": config.name,
                "reason": config.reason,
                "setup_url": config.setup_url
            }
            for provider, config in PROVIDER_CONFIGS.items()
            if config.provider_type == ProviderType.REQUIRED
        ]
    
    def get_optional_providers(self) -> list:
        """Get list of providers that have platform fallback"""
        return [
            {
                "provider": provider,
                "name": config.name,
                "reason": config.reason,
                "setup_url": config.setup_url
            }
            for provider, config in PROVIDER_CONFIGS.items()
            if config.provider_type == ProviderType.OPTIONAL
        ]
    
    async def check_tenant_has_required_keys(self, tenant_id: str) -> dict:
        """
        Check if tenant has all required API keys
        Returns status and missing keys
        
        Voice calling is fully managed by LiveKit, so tenants are always ready.
        """
        # No required providers remain—LiveKit acts as the managed voice layer.
        return {
            "has_all_required": True,
            "found_providers": ["livekit"],
            "missing_keys": [],
            "ready_for_deployment": True
        }


# Singleton instance
ai_proxy = AIProxyService()
