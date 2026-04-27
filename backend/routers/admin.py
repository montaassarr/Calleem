"""
Admin API Router
Platform owner endpoints for managing tenants, users, system configuration, and analytics.
Secured: Requires valid Admin/Owner/SuperAdmin authentication.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
import logging
import os

from models.tenant import TenantResponse, TenantCreate, TenantUpdate
from models.user import UserResponse, Token, UserCreate, UserUpdate
from models.appointment import AppointmentStatus, AppointmentCreate, AppointmentUpdate, AppointmentResponse
from models.service import ServiceCreate, ServiceUpdate, ServiceResponse
from models.conversation import ConversationResponse
from routers.users import get_current_admin, get_super_admin
from services.admin_service import get_admin_service, AdminService
from database.mongo_config import get_database

logger = logging.getLogger(__name__)

# Secure all endpoints in this router
router = APIRouter(dependencies=[Depends(get_current_admin)])


# ==================== TENANT MANAGEMENT ====================

@router.get("/tenants", response_model=List[TenantResponse], response_model_by_alias=False)
async def list_tenants(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    service: AdminService = Depends(get_admin_service)
):
    """List all tenants"""
    results = await service.list_tenants(skip, limit, search)
    return [TenantResponse(**t) for t in results]


@router.post("/tenants", response_model=TenantResponse, status_code=201, response_model_by_alias=False)
async def create_tenant(
    tenant: TenantCreate,
    service: AdminService = Depends(get_admin_service)
):
    """Create a new tenant"""
    created = await service.create_tenant(tenant)
    return TenantResponse(**created)


@router.get("/tenants/{tenant_id}", response_model=TenantResponse, response_model_by_alias=False)
async def get_tenant(
    tenant_id: str,
    service: AdminService = Depends(get_admin_service)
):
    """Get tenant details"""
    tenant = await service.get_tenant(tenant_id)
    return TenantResponse(**tenant)


@router.put("/tenants/{tenant_id}", response_model=TenantResponse, response_model_by_alias=False)
async def update_tenant(
    tenant_id: str,
    update: TenantUpdate,
    service: AdminService = Depends(get_admin_service)
):
    """Update tenant details"""
    updated = await service.update_tenant(tenant_id, update)
    return TenantResponse(**updated)


@router.delete("/tenants/{tenant_id}", status_code=204)
async def delete_tenant(
    tenant_id: str,
    service: AdminService = Depends(get_admin_service)
):
    """Delete a tenant and all associated data"""
    await service.delete_tenant(tenant_id)


# ==================== USER MANAGEMENT ====================

@router.get("/users", response_model=List[UserResponse])
async def list_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    tenant_id: Optional[str] = None,
    service: AdminService = Depends(get_admin_service)
):
    """List all users across all tenants"""
    results = await service.list_all_users(skip, limit, tenant_id)
    return [UserResponse(**u) for u in results]


@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    user: UserCreate,
    current_admin: dict = Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service)
):
    """Create a new user"""
    tenant_id = current_admin.get("tenant_id") or current_admin.get("business_id")
    created = await service.create_user(user, tenant_id)
    return UserResponse(**created)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    update: UserUpdate,
    service: AdminService = Depends(get_admin_service)
):
    """Update user details"""
    updated = await service.update_user(user_id, update)
    return UserResponse(**updated)


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: str,
    service: AdminService = Depends(get_admin_service)
):
    """Delete a user"""
    await service.delete_user(user_id)


@router.post("/users/{user_id}/impersonate", response_model=Token)
async def impersonate_user(
    user_id: str,
    current_admin: dict = Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service)
):
    """Generate a login token for a specific user (Impersonation)"""
    return await service.impersonate_user(user_id, current_admin["username"])


@router.get("/users/pending", response_model=List[UserResponse])
async def list_pending_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: AdminService = Depends(get_admin_service)
):
    """List all pending user registrations awaiting approval"""
    results = await service.list_pending_users(skip, limit)
    return [UserResponse(**u) for u in results]


@router.post("/users/{user_id}/approve", response_model=UserResponse)
async def approve_user(
    user_id: str,
    current_admin: dict = Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service)
):
    """Approve a pending user registration"""
    from services.user_service import UserService
    user_service = UserService()
    approved = await user_service.approve_user(user_id)
    logger.info(f"👤 User {user_id} approved by {current_admin.get('username')}")
    return UserResponse(**approved)


@router.post("/users/{user_id}/reject", response_model=UserResponse)
async def reject_user(
    user_id: str,
    current_admin: dict = Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service)
):
    """Reject a pending user registration"""
    from services.user_service import UserService
    user_service = UserService()
    rejected = await user_service.reject_user(user_id)
    logger.info(f"👤 User {user_id} rejected by {current_admin.get('username')}")
    return UserResponse(**rejected)


# ==================== APPOINTMENTS MANAGEMENT ====================

@router.get("/appointments", response_model=List[AppointmentResponse], response_model_by_alias=False)
async def list_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[AppointmentStatus] = None,
    service: AdminService = Depends(get_admin_service)
):
    """List all appointments"""
    results = await service.list_appointments(skip, limit, status)
    return [AppointmentResponse(**appt) for appt in results]


@router.post("/appointments", response_model=AppointmentResponse, status_code=201, response_model_by_alias=False)
async def create_appointment(
    appointment: AppointmentCreate,
    current_admin: dict = Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service)
):
    """Create a new appointment"""
    tenant_id = current_admin.get("tenant_id") or current_admin.get("business_id")
    created = await service.create_appointment(appointment, tenant_id)
    return AppointmentResponse(**created)


@router.put("/appointments/{appointment_id}", response_model=AppointmentResponse, response_model_by_alias=False)
async def update_appointment(
    appointment_id: str,
    update: AppointmentUpdate,
    service: AdminService = Depends(get_admin_service)
):
    """Update appointment"""
    updated = await service.update_appointment(appointment_id, update)
    return AppointmentResponse(**updated)


@router.delete("/appointments/{appointment_id}", status_code=204)
async def delete_appointment(
    appointment_id: str,
    service: AdminService = Depends(get_admin_service)
):
    """Delete an appointment"""
    await service.delete_appointment(appointment_id)


# ==================== SERVICES MANAGEMENT ====================

@router.get("/services", response_model=List[ServiceResponse], response_model_by_alias=False)
async def list_services(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: AdminService = Depends(get_admin_service)
):
    """List all services"""
    results = await service.list_services(skip, limit)
    return [ServiceResponse(**s) for s in results]


@router.post("/services", response_model=ServiceResponse, status_code=201, response_model_by_alias=False)
async def create_service(
    svc_data: ServiceCreate,
    current_admin: dict = Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service)
):
    """Create a new service"""
    tenant_id = current_admin.get("tenant_id") or current_admin.get("business_id")
    created = await service.create_service(svc_data, tenant_id)
    return ServiceResponse(**created)


@router.put("/services/{service_id}", response_model=ServiceResponse, response_model_by_alias=False)
async def update_service(
    service_id: str,
    update: ServiceUpdate,
    service: AdminService = Depends(get_admin_service)
):
    """Update service"""
    updated = await service.update_service(service_id, update)
    return ServiceResponse(**updated)


@router.delete("/services/{service_id}", status_code=204)
async def delete_service(
    service_id: str,
    service: AdminService = Depends(get_admin_service)
):
    """Delete a service"""
    await service.delete_service(service_id)


# ==================== CONVERSATIONS MANAGEMENT ====================

@router.get("/conversations", response_model=List[ConversationResponse], response_model_by_alias=False)
async def list_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    phone: Optional[str] = None,
    service: AdminService = Depends(get_admin_service)
):
    """List all conversations"""
    results = await service.list_conversations(skip, limit, phone)
    return [ConversationResponse(**conv) for conv in results]


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: str,
    service: AdminService = Depends(get_admin_service)
):
    """Delete a conversation"""
    await service.delete_conversation(conversation_id)


# ==================== BUSINESS CONFIG ====================

@router.get("/config")
async def get_business_config(
    current_admin: dict = Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service)
):
    """Get business configuration (tenant settings)"""
    tenant_id = current_admin.get("tenant_id") or current_admin.get("business_id")
    config = await service.get_business_config(tenant_id)
    return config


@router.put("/config")
async def update_business_config(
    config: dict,
    current_admin: dict = Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service)
):
    """Update business configuration (tenant settings)"""
    tenant_id = current_admin.get("tenant_id") or current_admin.get("business_id")
    updated = await service.update_business_config(tenant_id, config)
    return updated


# ==================== ANALYTICS ====================

@router.get("/analytics/global")
async def get_global_analytics(
    service: AdminService = Depends(get_admin_service)
):
    """Get global system stats"""
    return await service.get_global_analytics()


# ==================== ASSISTANT MANAGEMENT ====================

@router.post("/assistants/{tenant_id}/refresh-date")
async def refresh_assistant_date(tenant_id: str):
    """Remove any hardcoded current-date text from the assistant system prompt."""
    from services.vapi_service import vapi_service
    import re
    
    db = get_database()
    
    # Get tenant
    tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
    if not tenant:
        return {"error": "Tenant not found"}
    
    assistant_id = tenant.get("vapi_assistant_id")
    if not assistant_id:
        return {"error": "No assistant configured"}
    
    # Get current assistant config
    assistant = await vapi_service.get_assistant(assistant_id)
    if not assistant:
        return {"error": "Could not fetch assistant"}
    
    # Extract system prompt
    model_config = assistant.get("model", {})
    messages = model_config.get("messages", [])
    system_prompt = ""
    for msg in messages:
        if msg.get("role") == "system":
            system_prompt = msg.get("content", "")
            break
    
    if not system_prompt:
        return {"error": "No system prompt found"}
    
    # Remove old date header if present
    updated_prompt = re.sub(
        r'\*\*CURRENT DATE:.*?\*\*\n.*?tomorrow.*?\n\n?',
        '',
        system_prompt,
        flags=re.DOTALL
    )
    
    # Update assistant directly with the model config
    # Can't use update_assistant because it wraps instructions with a template
    # Need to use the Vapi API directly
    import httpx
    from utils.config import settings
    
    vapi_api_key = settings.VAPI_API_KEY or settings.VAPI_PRIVATE_API_KEY
    if not vapi_api_key:
        return {"error": "Vapi API key not configured"}
    
    headers = {
        "Authorization": f"Bearer {vapi_api_key}",
        "Content-Type": "application/json"
    }
    
    # Get current model config
    current_model = model_config.copy()
    current_model["messages"] = [{"role": "system", "content": updated_prompt}]
    
    update_payload = {"model": current_model}
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.patch(
                f"https://api.vapi.ai/assistant/{assistant_id}",
                headers=headers,
                json=update_payload
            )
            response.raise_for_status()
            
        return {
            "success": True,
            "message": "Assistant prompt cleaned of hardcoded current-date text",
            "assistant_id": assistant_id
        }
    except Exception as e:
        logger.error(f"Failed to update assistant: {e}")
        return {"error": f"Failed to update assistant: {str(e)}"}


# ==================== BILLING OVERVIEW ====================

@router.get("/billing/overview")
async def admin_billing_overview(db=Depends(get_database)):
    """
    Platform-level billing overview.

    For each tenant: subscription revenue, Vapi usage cost, credit balance,
    and per-assistant breakdown.  Also returns platform-wide totals so the
    platform owner can see gross margin in one call.
    """
    tenants = await db.tenants.find({}).to_list(length=2000)

    # Aggregate billing_ledger by tenant_id and assistant_id in one pass
    pipeline = [
        {"$match": {"type": "call_debit"}},
        {
            "$group": {
                "_id": {
                    "tenant_id": "$tenant_id",
                    "assistant_id": "$assistant_id",
                },
                "total_calls": {"$sum": 1},
                "total_cost_usd": {"$sum": "$amount_usd"},
                "total_duration_seconds": {"$sum": "$duration_seconds"},
            }
        },
    ]
    ledger_rows = await db.billing_ledger.aggregate(pipeline).to_list(length=10000)

    # Index ledger rows by tenant_id
    usage_by_tenant: Dict[str, Dict[str, Any]] = {}
    for row in ledger_rows:
        tid = row["_id"]["tenant_id"]
        aid = row["_id"]["assistant_id"]
        if tid not in usage_by_tenant:
            usage_by_tenant[tid] = {"assistants": {}, "total_calls": 0, "total_cost_usd": 0.0, "total_duration_seconds": 0}

        usage_by_tenant[tid]["assistants"][aid] = {
            "assistant_id": aid,
            "total_calls": row["total_calls"],
            "total_cost_usd": round(row["total_cost_usd"], 4),
            "total_minutes": round((row["total_duration_seconds"] or 0) / 60, 2),
        }
        usage_by_tenant[tid]["total_calls"] += row["total_calls"]
        usage_by_tenant[tid]["total_cost_usd"] += row["total_cost_usd"]
        usage_by_tenant[tid]["total_duration_seconds"] += row.get("total_duration_seconds") or 0

    tenant_summaries: List[Dict[str, Any]] = []
    for tenant in tenants:
        tid = str(tenant.get("_id"))
        usage = usage_by_tenant.get(tid, {})
        monthly_sub = float(tenant.get("monthly_subscription_amount_usd") or 0)
        credit_balance = float(tenant.get("credit_balance") or tenant.get("vapi_credit_balance") or 0)
        total_cost = round(float(usage.get("total_cost_usd") or 0), 4)
        total_minutes = round((usage.get("total_duration_seconds") or 0) / 60, 2)

        tenant_summaries.append({
            "tenant_id": tid,
            "name": tenant.get("name"),
            "email": tenant.get("email"),
            "plan": tenant.get("plan", "free"),
            "subscription_status": tenant.get("subscription_status", "inactive"),
            "monthly_subscription_usd": round(monthly_sub, 2),
            "credit_balance": round(credit_balance, 2),
            "total_calls": usage.get("total_calls", 0),
            "total_minutes": total_minutes,
            "total_vapi_cost_usd": total_cost,
            "profit_usd": round(monthly_sub - total_cost, 4),
            "assistants": list(usage.get("assistants", {}).values()),
        })

    # Platform-wide totals
    platform_revenue = sum(t["monthly_subscription_usd"] for t in tenant_summaries)
    platform_cost = sum(t["total_vapi_cost_usd"] for t in tenant_summaries)

    return {
        "tenants": tenant_summaries,
        "platform_summary": {
            "total_tenants": len(tenant_summaries),
            "active_tenants": sum(1 for t in tenant_summaries if t["subscription_status"] == "active"),
            "total_subscription_revenue_usd": round(platform_revenue, 2),
            "total_vapi_cost_usd": round(platform_cost, 4),
            "platform_margin_usd": round(platform_revenue - platform_cost, 4),
        },
    }


class AddCreditsRequest(BaseModel):
    amount_usd: float
    note: Optional[str] = None


@router.post("/billing/add-credits/{tenant_id}")
async def admin_add_credits(
    tenant_id: str,
    body: AddCreditsRequest,
    db=Depends(get_database),
):
    """Add credits to a tenant's balance (manual top-up by admin)."""
    from datetime import datetime as dt
    from bson import ObjectId

    if body.amount_usd <= 0:
        raise HTTPException(status_code=400, detail="amount_usd must be positive")

    tenant_query = (
        {"_id": ObjectId(tenant_id)} if ObjectId.is_valid(tenant_id)
        else {"_id": tenant_id}
    )
    tenant = await db.tenants.find_one(tenant_query)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    await db.tenants.update_one(
        tenant_query,
        {
            "$inc": {"credit_balance": body.amount_usd},
            "$set": {"updated_at": dt.utcnow()},
        },
    )

    new_balance = float(tenant.get("credit_balance") or 0) + body.amount_usd

    await db.billing_ledger.insert_one({
        "key": f"admin_topup:{tenant_id}:{dt.utcnow().isoformat()}",
        "type": "admin_topup",
        "tenant_id": tenant_id,
        "amount_usd": body.amount_usd,
        "note": body.note or "Manual admin top-up",
        "created_at": dt.utcnow(),
    })

    return {
        "success": True,
        "tenant_id": tenant_id,
        "added_usd": round(body.amount_usd, 2),
        "new_balance": round(new_balance, 2),
    }

