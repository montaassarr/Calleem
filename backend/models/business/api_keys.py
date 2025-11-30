"""
API Key models for multi-tenant BYOK system
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class ApiKey(BaseModel):
    """Individual API key stored per tenant"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    provider: str  # "openai", "elevenlabs", "groq", etc.
    name: str  # User-friendly name
    masked_key: str  # Display version: "sk-••••••••1234"
    encrypted_key: str  # "iv:ciphertext" format
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None
    is_valid: bool = True  # Set to False if validation fails


class ApiKeyCreate(BaseModel):
    """Request to add a new API key"""
    provider: str
    name: str
    api_key: str  # Plaintext key (will be encrypted)


class ApiKeyResponse(BaseModel):
    """Response when listing keys (no encrypted data)"""
    id: str
    provider: str
    name: str
    masked_key: str
    created_at: datetime
    last_used: Optional[datetime]
    is_valid: bool
