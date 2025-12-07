"""
LiveKit Token Router - API Endpoint for Token Generation
=========================================================

Provides POST /api/v1/livekit/token endpoint for generating LiveKit access tokens.
This is the FastAPI equivalent of the official LiveKit token-server template.

Author: CallFlow AI Team
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
import logging

from livekit.token_server import (
    TokenRequest,
    TokenResponse,
    generate_livekit_token,
    get_livekit_config,
)
from routers.users import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Extended Response Model (includes room info)
# =============================================================================

class TokenResponseExtended(TokenResponse):
    """Extended response with additional room information."""
    room_name: str = Field(
        ...,
        description="Full room name including tenant prefix"
    )
    agent_queue: Optional[str] = Field(
        None,
        description="Agent queue for this room"
    )


# =============================================================================
# API Endpoints
# =============================================================================

@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Generate LiveKit Access Token",
    description="""
    Generate a LiveKit access token for joining a room.
    
    This endpoint is equivalent to the official LiveKit token-server but integrated
    with our multi-tenant architecture. The room name will be automatically prefixed
    with the tenant ID.
    
    **Multi-tenant Room Naming:**
    - Input room_name: `my-room`
    - Output room: `tenant_{tenant_id}_my-room`
    
    **Default Grants:**
    - roomJoin: true
    - canPublish: true
    - canPublishData: true
    - canSubscribe: true
    - canPublishSources: ["microphone", "camera", "screen_share"]
    
    **Response Format (matches LiveKit sandbox):**
    ```json
    {
      "server_url": "wss://...",
      "participant_token": "eyJ..."
    }
    ```
    """,
    responses={
        200: {
            "description": "Token generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "server_url": "wss://aireceptionist-iqt10ym2.livekit.cloud",
                        "participant_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                    }
                }
            }
        },
        401: {"description": "Not authenticated"},
        503: {"description": "LiveKit not configured"},
    }
)
async def create_token(
    request: TokenRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Generate a LiveKit access token for the authenticated user's tenant.
    
    The token allows the participant to join the specified room with the
    configured grants. The room name is automatically prefixed with the
    tenant ID to ensure multi-tenant isolation.
    """
    try:
        # Get tenant_id from authenticated user
        tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
        
        if not tenant_id:
            logger.error(
                f"User {current_user.get('id')} has no tenant_id",
                extra={"user_id": current_user.get("id")}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is missing tenant_id. Please contact support."
            )
        
        tenant_id = str(tenant_id)
        
        # Generate the token
        response = generate_livekit_token(
            tenant_id=tenant_id,
            request=request,
        )
        
        logger.info(
            f"Generated token for tenant={tenant_id}, "
            f"room={request.room_name}, "
            f"identity={request.participant_identity}"
        )
        
        return response
        
    except ValueError as e:
        # LiveKit not configured
        logger.error(f"LiveKit configuration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating token: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate token: {str(e)}"
        )


@router.post(
    "/token/extended",
    response_model=TokenResponseExtended,
    summary="Generate LiveKit Access Token (Extended)",
    description="Same as /token but returns additional room information.",
)
async def create_token_extended(
    request: TokenRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Generate a LiveKit access token with extended response information.
    
    Returns the full room name and agent queue in addition to the standard
    token response.
    """
    try:
        tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
        
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is missing tenant_id."
            )
        
        tenant_id = str(tenant_id)
        config = get_livekit_config()
        
        # Generate the token
        response = generate_livekit_token(
            tenant_id=tenant_id,
            request=request,
        )
        
        # Build extended response
        full_room_name = f"tenant_{tenant_id}_{request.room_name}"
        
        return TokenResponseExtended(
            server_url=response.server_url,
            participant_token=response.participant_token,
            room_name=full_room_name,
            agent_queue=config.agent_queue,
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating extended token: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate token: {str(e)}"
        )


@router.get(
    "/status",
    summary="Check LiveKit Configuration Status",
    description="Returns whether LiveKit is properly configured.",
)
async def livekit_status():
    """
    Check if LiveKit is configured and ready to generate tokens.
    
    This endpoint does not require authentication and is useful for
    health checks and debugging.
    """
    config = get_livekit_config()
    
    return {
        "configured": config.is_configured,
        "server_url": config.url if config.is_configured else None,
        "agent_queue": config.agent_queue,
        "agent_name": config.agent_name,
    }


# =============================================================================
# Room Management Endpoints
# =============================================================================

from services.livekit_service import livekit_service
from routers.users import get_current_admin
from typing import List


class RoomCreateRequest(BaseModel):
    """Request model for creating a room."""
    room_name: str = Field(..., min_length=1, max_length=128)
    empty_timeout: int = Field(default=600, ge=60, le=86400)
    max_participants: int = Field(default=20, ge=2, le=100)
    metadata: Optional[Dict[str, Any]] = None


class RoomResponse(BaseModel):
    """Response model for room details."""
    sid: Optional[str] = None
    name: str
    num_participants: int = 0
    max_participants: int = 20
    created_at: Optional[int] = None
    empty_timeout: int = 600
    metadata: Optional[str] = None


class ParticipantResponse(BaseModel):
    """Response model for participant details."""
    sid: Optional[str] = None
    identity: str
    name: Optional[str] = None
    state: Optional[str] = None
    joined_at: Optional[int] = None
    metadata: Optional[str] = None
    is_publisher: bool = False


@router.get(
    "/rooms",
    response_model=List[RoomResponse],
    summary="List All Rooms",
    description="List all active LiveKit rooms for the authenticated user's tenant.",
)
async def list_rooms(
    current_user: dict = Depends(get_current_user),
):
    """
    List all active rooms for the current tenant.
    
    Only rooms matching the tenant's prefix are returned.
    """
    tenant_id = str(current_user.get("tenant_id") or current_user.get("business_id"))
    
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is missing tenant_id."
        )
    
    rooms = await livekit_service.list_rooms(tenant_id=tenant_id)
    return rooms


@router.get(
    "/rooms/all",
    response_model=List[RoomResponse],
    summary="List All Rooms (Admin)",
    description="List all active LiveKit rooms across all tenants. Admin only.",
)
async def list_all_rooms(
    current_user: dict = Depends(get_current_admin),
):
    """
    List all active rooms across all tenants.
    
    Requires admin privileges.
    """
    rooms = await livekit_service.list_rooms()
    return rooms


@router.post(
    "/rooms",
    response_model=RoomResponse,
    summary="Create Room",
    description="Create a new LiveKit room with tenant prefix.",
)
async def create_room(
    request: RoomCreateRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new room with the tenant prefix.
    
    Room name will be: tenant_{tenant_id}_{room_name}
    """
    tenant_id = str(current_user.get("tenant_id") or current_user.get("business_id"))
    
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is missing tenant_id."
        )
    
    # Build full room name with tenant prefix
    full_room_name = f"tenant_{tenant_id}_{request.room_name}"
    
    # Build metadata with tenant info
    metadata = request.metadata or {}
    metadata["tenant_id"] = tenant_id
    
    room = await livekit_service.create_room(
        room_name=full_room_name,
        empty_timeout=request.empty_timeout,
        max_participants=request.max_participants,
        metadata=metadata,
    )
    
    return RoomResponse(
        name=room.get("name", full_room_name),
        sid=room.get("sid"),
        num_participants=room.get("num_participants", 0),
        max_participants=request.max_participants,
        empty_timeout=request.empty_timeout,
        metadata=room.get("metadata"),
    )


@router.get(
    "/rooms/{room_name}",
    response_model=Optional[RoomResponse],
    summary="Get Room Details",
    description="Get details of a specific room.",
)
async def get_room(
    room_name: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Get details of a specific room.
    
    The room_name should include the tenant prefix.
    """
    tenant_id = str(current_user.get("tenant_id") or current_user.get("business_id"))
    
    # Build full room name if not already prefixed
    if not room_name.startswith(f"tenant_{tenant_id}_") and not room_name.startswith(f"preview-{tenant_id}-"):
        full_room_name = f"tenant_{tenant_id}_{room_name}"
    else:
        full_room_name = room_name
    
    room = await livekit_service.get_room(full_room_name)
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room '{room_name}' not found"
        )
    
    return room


@router.delete(
    "/rooms/{room_name}",
    summary="Delete Room",
    description="Delete a room and disconnect all participants.",
)
async def delete_room(
    room_name: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Delete a room and disconnect all participants.
    
    The room_name should include the tenant prefix.
    """
    tenant_id = str(current_user.get("tenant_id") or current_user.get("business_id"))
    
    # Build full room name if not already prefixed
    if not room_name.startswith(f"tenant_{tenant_id}_") and not room_name.startswith(f"preview-{tenant_id}-"):
        full_room_name = f"tenant_{tenant_id}_{room_name}"
    else:
        full_room_name = room_name
    
    success = await livekit_service.delete_room(full_room_name)
    
    return {
        "success": success,
        "message": f"Room '{full_room_name}' deleted" if success else "Failed to delete room"
    }


@router.get(
    "/rooms/{room_name}/participants",
    response_model=List[ParticipantResponse],
    summary="List Participants",
    description="List all participants in a room.",
)
async def list_participants(
    room_name: str,
    current_user: dict = Depends(get_current_user),
):
    """
    List all participants in a room.
    """
    tenant_id = str(current_user.get("tenant_id") or current_user.get("business_id"))
    
    # Build full room name if not already prefixed
    if not room_name.startswith(f"tenant_{tenant_id}_") and not room_name.startswith(f"preview-{tenant_id}-"):
        full_room_name = f"tenant_{tenant_id}_{room_name}"
    else:
        full_room_name = room_name
    
    participants = await livekit_service.list_participants(full_room_name)
    return participants


@router.delete(
    "/rooms/{room_name}/participants/{identity}",
    summary="Remove Participant",
    description="Remove a participant from a room.",
)
async def remove_participant(
    room_name: str,
    identity: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Remove a participant from a room.
    """
    tenant_id = str(current_user.get("tenant_id") or current_user.get("business_id"))
    
    # Build full room name if not already prefixed
    if not room_name.startswith(f"tenant_{tenant_id}_") and not room_name.startswith(f"preview-{tenant_id}-"):
        full_room_name = f"tenant_{tenant_id}_{room_name}"
    else:
        full_room_name = room_name
    
    success = await livekit_service.remove_participant(full_room_name, identity)
    
    return {
        "success": success,
        "message": f"Participant '{identity}' removed" if success else "Failed to remove participant"
    }
