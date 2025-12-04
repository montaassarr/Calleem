"""
Platform API Keys Router - Admin-only management of shared API keys
==================================================================

This router allows SUPER ADMINS to manage platform-wide API keys
that are shared across all tenants (when tenants don't have BYOK).

Security:
- Only accessible by super admins (role check)
- Keys are encrypted at rest (AES-256-GCM)
- Keys are never returned in plaintext (only masked)
- Usage is tracked per tenant for billing

Endpoints:
- GET /platform-keys - List all platform keys (masked)
- POST /platform-keys - Add new platform key
- DELETE /platform-keys/{key_id} - Delete platform key
- POST /platform-keys/{key_id}/health-check - Test key health
- GET /platform-keys/usage - Get usage analytics
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from datetime import datetime, timedelta
import logging

from models.core.platform_api_keys import (
    PlatformApiKey,
    PlatformKeyCreate,
    PlatformKeyResponse,
    PlatformKeyUsageLog,
    PlatformKeyHealthCheck,
)
from database.mongo_config import get_database
from routers.users import get_current_user
from utils.encryption import encrypt_value, mask_api_key
from routers.api_keys import validate_api_key
from services.ai_proxy import ai_proxy

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/platform-keys",
    tags=["Platform API Keys (Admin Only)"],
)


def require_super_admin(current_user: dict = Depends(get_current_user)):
    """
    Dependency to ensure only super admins can access platform keys
    """
    # Check if user is super admin
    # TODO: Implement proper role checking based on your user model
    # For now, check if user has admin role
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can manage platform API keys"
        )
    return current_user


@router.get("", response_model=List[PlatformKeyResponse])
async def list_platform_keys(current_user: dict = Depends(require_super_admin)):
    """
    List all platform API keys (masked for security)
    """
    db = get_database()
    
    keys = await db.platform_api_keys.find().to_list(length=100)
    
    return [
        PlatformKeyResponse(
            id=key["id"],
            provider=key["provider"],
            tier=key["tier"],
            name=key["name"],
            masked_key=key["masked_key"],
            is_active=key["is_active"],
            is_healthy=key.get("is_healthy", True),
            total_requests_today=key.get("total_requests_today", 0),
            total_tokens_today=key.get("total_tokens_today", 0),
            total_cost_today=key.get("total_cost_today", 0.0),
            created_at=key["created_at"],
            last_health_check=key.get("last_health_check"),
        )
        for key in keys
    ]


@router.post("", response_model=PlatformKeyResponse, status_code=status.HTTP_201_CREATED)
async def add_platform_key(
    key_data: PlatformKeyCreate,
    current_user: dict = Depends(require_super_admin)
):
    """
    Add a new platform API key
    
    The key will be validated before storing
    """
    db = get_database()
    
    # Validate the key
    logger.info(f"Validating {key_data.provider.value} key...")
    is_valid = await validate_api_key(key_data.provider.value, key_data.api_key)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid API key for {key_data.provider.value}. Please check the key and try again."
        )
    
    # Encrypt the key
    try:
        encrypted_key = encrypt_value(key_data.api_key)
        masked_key = mask_api_key(key_data.api_key)
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to encrypt API key"
        )
    
    # Create platform key object
    new_key = PlatformApiKey(
        provider=key_data.provider,
        tier=key_data.tier,
        name=key_data.name,
        masked_key=masked_key,
        encrypted_key=encrypted_key,
        max_requests_per_minute=key_data.max_requests_per_minute,
        max_tokens_per_day=key_data.max_tokens_per_day,
        cost_per_1k_tokens=key_data.cost_per_1k_tokens,
        markup_percentage=key_data.markup_percentage,
        is_active=True,
        is_healthy=True,
        created_by=current_user.get("id"),
        notes=key_data.notes,
    )
    
    # Store in database
    await db.platform_api_keys.insert_one(new_key.model_dump())
    
    logger.info(f"✅ Added platform key: {key_data.provider.value} - {key_data.name}")
    
    return PlatformKeyResponse(
        id=new_key.id,
        provider=new_key.provider,
        tier=new_key.tier,
        name=new_key.name,
        masked_key=new_key.masked_key,
        is_active=new_key.is_active,
        is_healthy=new_key.is_healthy,
        total_requests_today=new_key.total_requests_today,
        total_tokens_today=new_key.total_tokens_today,
        total_cost_today=new_key.total_cost_today,
        created_at=new_key.created_at,
        last_health_check=new_key.last_health_check,
    )


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_platform_key(
    key_id: str,
    current_user: dict = Depends(require_super_admin)
):
    """
    Delete a platform API key
    
    WARNING: This will affect all tenants using this key!
    """
    db = get_database()
    
    result = await db.platform_api_keys.delete_one({"id": key_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Platform key not found"
        )
    
    logger.warning(f"🗑️ Deleted platform key {key_id} by admin {current_user.get('id')}")
    
    return None


@router.patch("/{key_id}/toggle", response_model=PlatformKeyResponse)
async def toggle_platform_key(
    key_id: str,
    current_user: dict = Depends(require_super_admin)
):
    """
    Toggle a platform key active/inactive status
    """
    db = get_database()
    
    key = await db.platform_api_keys.find_one({"id": key_id})
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Platform key not found"
        )
    
    new_status = not key["is_active"]
    
    await db.platform_api_keys.update_one(
        {"id": key_id},
        {"$set": {"is_active": new_status, "updated_at": datetime.utcnow()}}
    )
    
    logger.info(f"Platform key {key_id} {'activated' if new_status else 'deactivated'}")
    
    # Fetch updated key
    updated_key = await db.platform_api_keys.find_one({"id": key_id})
    
    return PlatformKeyResponse(
        id=updated_key["id"],
        provider=updated_key["provider"],
        tier=updated_key["tier"],
        name=updated_key["name"],
        masked_key=updated_key["masked_key"],
        is_active=updated_key["is_active"],
        is_healthy=updated_key.get("is_healthy", True),
        total_requests_today=updated_key.get("total_requests_today", 0),
        total_tokens_today=updated_key.get("total_tokens_today", 0),
        total_cost_today=updated_key.get("total_cost_today", 0.0),
        created_at=updated_key["created_at"],
        last_health_check=updated_key.get("last_health_check"),
    )


@router.post("/{key_id}/health-check", response_model=PlatformKeyHealthCheck)
async def health_check_platform_key(
    key_id: str,
    current_user: dict = Depends(require_super_admin)
):
    """
    Perform health check on a platform key
    Tests if the key is still valid by making a test API call
    """
    try:
        result = await ai_proxy.health_check_key(key_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health check failed"
        )


@router.get("/usage/summary")
async def get_usage_summary(
    days: int = 7,
    current_user: dict = Depends(require_super_admin)
):
    """
    Get usage summary for platform keys over the last N days
    
    Returns total costs, most used tenants, etc.
    """
    db = get_database()
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Aggregate usage logs
    pipeline = [
        {"$match": {"timestamp": {"$gte": start_date}}},
        {
            "$group": {
                "_id": {
                    "tenant_id": "$tenant_id",
                    "provider": "$provider",
                    "model": "$model",
                },
                "total_requests": {"$sum": 1},
                "total_tokens": {"$sum": "$tokens_used"},
                "total_cost_to_platform": {"$sum": "$cost_to_platform"},
                "total_charged_to_tenant": {"$sum": "$charged_to_tenant"},
            }
        },
        {"$sort": {"total_cost_to_platform": -1}},
        {"$limit": 50}
    ]
    
    results = await db.platform_key_usage_logs.aggregate(pipeline).to_list(length=50)
    
    # Calculate totals
    total_cost = sum(r["total_cost_to_platform"] for r in results)
    total_revenue = sum(r["total_charged_to_tenant"] for r in results)
    total_profit = total_revenue - total_cost
    
    return {
        "period_days": days,
        "start_date": start_date,
        "end_date": datetime.utcnow(),
        "summary": {
            "total_cost_to_platform": round(total_cost, 2),
            "total_charged_to_tenants": round(total_revenue, 2),
            "total_profit": round(total_profit, 2),
            "profit_margin_percent": round((total_profit / total_cost * 100) if total_cost > 0 else 0, 2),
        },
        "top_usage_by_tenant": results[:20],
    }


@router.get("/usage/by-tenant/{tenant_id}")
async def get_tenant_usage(
    tenant_id: str,
    days: int = 30,
    current_user: dict = Depends(require_super_admin)
):
    """
    Get usage details for a specific tenant
    """
    db = get_database()
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    logs = await db.platform_key_usage_logs.find({
        "tenant_id": tenant_id,
        "timestamp": {"$gte": start_date}
    }).sort("timestamp", -1).to_list(length=100)
    
    total_cost = sum(log.get("cost_to_platform", 0) for log in logs)
    total_charged = sum(log.get("charged_to_tenant", 0) for log in logs)
    total_tokens = sum(log.get("tokens_used", 0) for log in logs)
    
    return {
        "tenant_id": tenant_id,
        "period_days": days,
        "summary": {
            "total_requests": len(logs),
            "total_tokens": total_tokens,
            "total_cost_to_platform": round(total_cost, 4),
            "total_charged": round(total_charged, 4),
        },
        "recent_calls": logs[:20]  # Last 20 calls
    }
