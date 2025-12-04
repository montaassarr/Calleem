"""
Platform API Keys - Shared keys managed by the platform
=======================================================

These are YOUR keys that customers use when they don't bring their own (BYOK).

Two-tier system:
1. **Tenant BYOK** (business_config.api_keys) - Customer's own keys, no cost to you
2. **Platform Keys** (this file) - Your shared keys, you charge customers for usage

Architecture:
- Platform keys stored encrypted in MongoDB (platform_api_keys collection)
- Auto-failover if one key is rate-limited or unhealthy
- Usage tracking for billing attribution
- Health monitoring and automatic key rotation
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class KeyProvider(str, Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    ELEVENLABS = "elevenlabs"
    DEEPGRAM = "deepgram"
    ASSEMBLYAI = "assemblyai"
    PLAYHT = "playht"
    CARTESIA = "cartesia"


class PlatformKeyTier(str, Enum):
    """Usage tier for rate limiting"""
    FREE = "free"           # Shared key, strict limits
    STANDARD = "standard"   # Dedicated key, moderate limits
    PREMIUM = "premium"     # High-priority key, high limits


class PlatformApiKey(BaseModel):
    """
    Platform-managed API key (stored encrypted)
    These are YOUR keys that customers use by default
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    provider: KeyProvider
    tier: PlatformKeyTier = PlatformKeyTier.STANDARD
    name: str  # e.g., "Production OpenAI Key #1"
    masked_key: str  # Display version
    encrypted_key: str  # AES-256-GCM encrypted
    
    # Rate limiting (per key, not per tenant)
    max_requests_per_minute: int = 60
    max_tokens_per_day: int = 1_000_000
    
    # Cost tracking (for internal accounting)
    cost_per_1k_tokens: float = 0.002  # Adjust per model
    markup_percentage: float = 50.0  # 50% markup on cost
    
    # Health monitoring
    is_active: bool = True
    is_healthy: bool = True  # Set to False if API returns errors
    last_health_check: Optional[datetime] = None
    consecutive_failures: int = 0
    max_failures_before_disable: int = 5
    
    # Usage stats (reset daily)
    total_requests_today: int = 0
    total_tokens_today: int = 0
    total_cost_today: float = 0.0
    last_reset_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None  # Admin user ID
    notes: Optional[str] = None


class PlatformKeyCreate(BaseModel):
    """Request to add a new platform API key"""
    provider: KeyProvider
    name: str
    api_key: str  # Plaintext (will be encrypted)
    tier: PlatformKeyTier = PlatformKeyTier.STANDARD
    max_requests_per_minute: int = 60
    max_tokens_per_day: int = 1_000_000
    cost_per_1k_tokens: float = 0.002
    markup_percentage: float = 50.0
    notes: Optional[str] = None


class PlatformKeyResponse(BaseModel):
    """Response when listing platform keys (no decrypted data)"""
    id: str
    provider: KeyProvider
    tier: PlatformKeyTier
    name: str
    masked_key: str
    is_active: bool
    is_healthy: bool
    total_requests_today: int
    total_tokens_today: int
    total_cost_today: float
    created_at: datetime
    last_health_check: Optional[datetime]


class PlatformKeyUsageLog(BaseModel):
    """
    Track usage of platform keys (for cost attribution & billing)
    One log entry per API call
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    platform_key_id: str  # Reference to PlatformApiKey
    tenant_id: str  # Which tenant used it
    provider: KeyProvider
    
    # Request details
    endpoint: str  # e.g., "/v1/chat/completions"
    model: str  # e.g., "gpt-4o-mini"
    
    # Usage metrics
    tokens_used: int  # Total tokens (input + output)
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    
    # Cost calculation
    cost_to_platform: float  # What we paid to OpenAI/Anthropic
    charged_to_tenant: float  # What we charge tenant (with markup)
    
    # Response metadata
    latency_ms: Optional[int] = None
    status_code: int = 200
    error_message: Optional[str] = None
    
    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PlatformKeyHealthCheck(BaseModel):
    """Health check result for a platform key"""
    key_id: str
    provider: KeyProvider
    is_healthy: bool
    response_time_ms: int
    error_message: Optional[str] = None
    checked_at: datetime = Field(default_factory=datetime.utcnow)
