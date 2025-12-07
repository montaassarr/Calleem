"""
LiveKit Token Server - Python/FastAPI Implementation
=====================================================

Equivalent to the official LiveKit token-server template but in Python.
Generates LiveKit Access Tokens for multi-tenant AI receptionist rooms.

References:
- https://github.com/livekit/token-server (Node.js original)
- https://docs.livekit.io/home/get-started/authentication/

Author: CallFlow AI Team
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional
from uuid import uuid4

from jose import jwt
from pydantic import BaseModel, Field

from utils.config import settings

logger = logging.getLogger(__name__)


# =============================================================================
# Request/Response Models
# =============================================================================

class TokenRequest(BaseModel):
    """
    Request model for generating a LiveKit access token.
    
    Matches the official LiveKit token-server API format.
    """
    room_name: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Name of the room to join (will be prefixed with tenant_id)"
    )
    participant_identity: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Unique identity for the participant in the room"
    )
    participant_name: Optional[str] = Field(
        None,
        max_length=128,
        description="Display name for the participant"
    )
    participant_metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Custom metadata to attach to the participant (tenant_id auto-added)"
    )
    ttl: int = Field(
        default=900,  # 15 minutes
        ge=60,
        le=86400,  # Max 24 hours
        description="Token time-to-live in seconds (default: 900 = 15 minutes)"
    )
    grants: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Custom video grants to override defaults"
    )


class TokenResponse(BaseModel):
    """
    Response model matching the LiveKit sandbox format.
    
    This is the exact format expected by LiveKit client SDKs.
    """
    server_url: str = Field(
        ...,
        description="LiveKit WebSocket server URL (wss://...)"
    )
    participant_token: str = Field(
        ...,
        description="JWT access token for the participant"
    )


# =============================================================================
# Token Generation Logic
# =============================================================================

@dataclass
class LiveKitTokenConfig:
    """Configuration for LiveKit token generation."""
    url: str
    api_key: str
    api_secret: str
    agent_queue: str
    agent_name: str

    @property
    def is_configured(self) -> bool:
        return bool(self.url and self.api_key and self.api_secret)


def get_livekit_config() -> LiveKitTokenConfig:
    """Get LiveKit configuration from settings."""
    return LiveKitTokenConfig(
        url=settings.LIVEKIT_URL.rstrip("/") if settings.LIVEKIT_URL else "",
        api_key=settings.LIVEKIT_API_KEY,
        api_secret=settings.LIVEKIT_API_SECRET,
        agent_queue=settings.LIVEKIT_AGENT_QUEUE,
        agent_name=settings.LIVEKIT_AGENT_NAME,
    )


def generate_livekit_token(
    *,
    tenant_id: str,
    request: TokenRequest,
    config: Optional[LiveKitTokenConfig] = None,
) -> TokenResponse:
    """
    Generate a LiveKit access token for multi-tenant rooms.
    
    This function implements the same logic as the official LiveKit token-server
    but adapted for our multi-tenant architecture.
    
    Args:
        tenant_id: The tenant ID from the authenticated user
        request: Token request parameters
        config: Optional LiveKit config (uses settings if not provided)
    
    Returns:
        TokenResponse with server_url and participant_token
    
    Raises:
        ValueError: If LiveKit is not configured
    """
    if config is None:
        config = get_livekit_config()
    
    if not config.is_configured:
        raise ValueError(
            "LiveKit is not configured. Set LIVEKIT_URL, LIVEKIT_API_KEY, "
            "and LIVEKIT_API_SECRET in your .env file."
        )
    
    # Build multi-tenant room name
    # Format: tenant_{tenant_id}_{room_name}
    full_room_name = f"tenant_{tenant_id}_{request.room_name}"
    
    # Build participant metadata with tenant_id
    metadata = request.participant_metadata or {}
    metadata["tenant_id"] = tenant_id
    metadata["agent_name"] = config.agent_name
    metadata["agent_queue"] = config.agent_queue
    
    # Add participant name to metadata if provided
    if request.participant_name:
        metadata["participant_name"] = request.participant_name
    
    # Build default grants
    default_grants = {
        "room": full_room_name,
        "roomJoin": True,
        "canPublish": True,
        "canPublishData": True,
        "canSubscribe": True,
        "canPublishSources": ["microphone", "camera", "screen_share"],
    }
    
    # Override with custom grants if provided
    if request.grants:
        default_grants.update(request.grants)
        # Ensure room is always set correctly
        default_grants["room"] = full_room_name
    
    # Build JWT claims
    now = int(time.time())
    claims = {
        "iss": config.api_key,
        "sub": request.participant_identity,
        "nbf": now - 10,  # Allow 10 seconds clock skew
        "iat": now,
        "exp": now + request.ttl,
        "jti": str(uuid4()),
        "video": default_grants,
        "metadata": json.dumps(metadata),
    }
    
    # Add participant name if provided
    if request.participant_name:
        claims["name"] = request.participant_name
    
    # Generate JWT token
    token = jwt.encode(claims, config.api_secret, algorithm="HS256")
    
    logger.info(
        f"Generated LiveKit token for tenant={tenant_id}, "
        f"room={full_room_name}, identity={request.participant_identity}"
    )
    
    return TokenResponse(
        server_url=config.url,
        participant_token=token,
    )


# =============================================================================
# Utility Functions
# =============================================================================

def decode_token(token: str, verify: bool = False) -> Dict[str, Any]:
    """
    Decode a LiveKit token for debugging purposes.
    
    Args:
        token: The JWT token to decode
        verify: Whether to verify the signature (requires secret)
    
    Returns:
        Decoded token claims
    """
    if verify:
        config = get_livekit_config()
        return jwt.decode(token, config.api_secret, algorithms=["HS256"])
    else:
        # Decode without verification (for debugging only)
        return jwt.get_unverified_claims(token)
