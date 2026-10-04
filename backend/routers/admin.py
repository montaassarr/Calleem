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
from pymongo import ReturnDocument
import logging
import os
import re
import uuid

from models.tenant import TenantResponse, TenantCreate, TenantUpdate
from models.user import UserResponse, Token, UserCreate, UserUpdate
from models.appointment import AppointmentStatus, AppointmentCreate, AppointmentUpdate, AppointmentResponse
from models.service import ServiceCreate, ServiceUpdate, ServiceResponse
from models.conversation import ConversationResponse
from routers.users import get_super_admin
from services import industry_templates, usage_billing
from services.admin_service import get_admin_service, AdminService
from database.mongo_config import get_database
from utils.config import settings

logger = logging.getLogger(__name__)

# Secure all endpoints in this router
# Platform-wide admin API: only the platform super admin. Business owners/admins
# manage their own tenant through the regular /api/v1 endpoints.
router = APIRouter(dependencies=[Depends(get_super_admin)])


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
    current_admin: dict = Depends(get_super_admin),
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
    current_admin: dict = Depends(get_super_admin),
    service: AdminService = Depends(get_admin_service)
):
    """Generate a login token for a specific user (Impersonation)"""
    return await service.impersonate_user(user_id, current_admin)


@router.get("/users/pending", response_model=List[UserResponse])
async def list_pending_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_admin: dict = Depends(get_super_admin),
    service: AdminService = Depends(get_admin_service)
):
    """List pending user registrations. Super-admins see all; others see their tenant only."""
    results = await service.list_pending_users(skip, limit, current_admin)
    return [UserResponse(**u) for u in results]


@router.post("/users/{user_id}/approve", response_model=UserResponse)
async def approve_user(
    user_id: str,
    current_admin: dict = Depends(get_super_admin),
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
    current_admin: dict = Depends(get_super_admin),
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
    current_admin: dict = Depends(get_super_admin),
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
    current_admin: dict = Depends(get_super_admin),
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


# ==================== BILLING ====================

@router.get("/billing/overview")
async def admin_billing_overview(db=Depends(get_database)):
    """
    Platform billing for the super admin: every business's minutes wallet plus its calls,
    Vapi cost and payments over the last 30 days, and platform totals (margin, minutes owed).
    """
    since = datetime.utcnow() - timedelta(days=30)
    tenants = await db.tenants.find({}).to_list(length=2000)

    usage_rows = await db.billing_ledger.aggregate([
        {"$match": {"type": "call_debit", "created_at": {"$gte": since}}},
        {"$group": {
            "_id": "$tenant_id",
            "calls": {"$sum": 1},
            "seconds": {"$sum": "$duration_seconds"},
            "cost": {"$sum": "$amount_usd"},
        }},
    ]).to_list(length=10000)
    revenue_rows = await db.billing_ledger.aggregate([
        {"$match": {"type": "minutes_credit", "created_at": {"$gte": since}, "currency": "USD", "amount_paid": {"$gt": 0}}},
        {"$group": {"_id": "$tenant_id", "revenue": {"$sum": "$amount_paid"}}},
    ]).to_list(length=10000)
    usage_by_tenant = {row["_id"]: row for row in usage_rows}
    revenue_by_tenant = {row["_id"]: row["revenue"] for row in revenue_rows}

    rows: List[Dict[str, Any]] = []
    for tenant in tenants:
        tid = str(tenant.get("_id"))
        usage = usage_by_tenant.get(tid, {})
        cost = round(float(usage.get("cost") or 0), 2)
        revenue = round(float(revenue_by_tenant.get(tid) or 0), 2)
        period_end = tenant.get("billing_period_end")
        rows.append({
            "tenant_id": tid,
            "name": tenant.get("name"),
            "email": tenant.get("email"),
            "billing_plan": tenant.get("billing_plan") or "trial",
            "subscription_status": tenant.get("subscription_status") or "inactive",
            "minutes_balance": round(float(tenant.get("minutes_balance") or 0), 1),
            "billing_period_end": period_end.isoformat() if isinstance(period_end, datetime) else period_end,
            "calls_paused": bool(tenant.get("calls_paused")),
            "billing_exempt": bool(tenant.get("billing_exempt")),
            "fallback_number": tenant.get("billing_fallback_number"),
            "has_phone_number": bool((tenant.get("phone_config") or {}).get("is_active")),
            "calls_30d": usage.get("calls", 0),
            "minutes_30d": usage_billing.minutes_for_seconds(usage.get("seconds")),
            "vapi_cost_30d_usd": cost,
            "revenue_30d_usd": revenue,
            "margin_30d_usd": round(revenue - cost, 2),
        })
    rows.sort(key=lambda r: (-r["revenue_30d_usd"], -r["calls_30d"]))

    revenue_total = round(sum(r["revenue_30d_usd"] for r in rows), 2)
    cost_total = round(sum(r["vapi_cost_30d_usd"] for r in rows), 2)
    return {
        "tenants": rows,
        "platform_summary": {
            "total_tenants": len(rows),
            "paying_tenants": sum(1 for r in rows if r["billing_plan"] != "trial"),
            "paused_tenants": sum(1 for r in rows if r["calls_paused"]),
            "revenue_30d_usd": revenue_total,
            "vapi_cost_30d_usd": cost_total,
            "margin_30d_usd": round(revenue_total - cost_total, 2),
            "minutes_owed": round(sum(max(r["minutes_balance"], 0) for r in rows), 1),
            "enforcement_enabled": settings.BILLING_ENFORCEMENT_ENABLED,
        },
        "pricing": usage_billing.PRICING,
        "topup_price_per_minute_usd": usage_billing.topup_price_per_minute(),
    }


class AddMinutesRequest(BaseModel):
    plan: Optional[str] = None  # monthly | custom; also starts a 30-day billing period
    calls: Optional[int] = None  # monthly plan usage level; minutes default to calls x avg_minutes
    avg_minutes: Optional[float] = None
    minutes: Optional[float] = None
    amount_paid: Optional[float] = None
    currency: str = "USD"
    reference: Optional[str] = None  # invoice or bank transfer reference; the same one can't be recorded twice
    note: Optional[str] = None


@router.post("/billing/tenants/{tenant_id}/minutes")
async def admin_add_minutes(
    tenant_id: str,
    body: AddMinutesRequest,
    current_super_admin: dict = Depends(get_super_admin),
    db=Depends(get_database),
):
    """Record a payment received outside Stripe (e.g. a bank transfer) and add its minutes."""
    if body.plan is not None and body.plan not in ("monthly", "custom"):
        raise HTTPException(status_code=400, detail="Unknown plan")
    plan_fields: Dict[str, Any] = {}
    if body.plan == "monthly" and body.calls is not None and body.avg_minutes is not None:
        try:
            calls, avg_minutes = usage_billing.validate_usage(body.calls, body.avg_minutes)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        quote = usage_billing.quote(calls, avg_minutes)
        plan_fields = usage_billing.plan_fields(calls, avg_minutes, body.amount_paid or quote["price_usd"])
    minutes = body.minutes if body.minutes is not None else plan_fields.get("plan_minutes")
    if not minutes or minutes <= 0 or minutes > 100000:
        raise HTTPException(status_code=400, detail="minutes must be between 0 and 100000")
    if body.amount_paid is not None and body.amount_paid < 0:
        raise HTTPException(status_code=400, detail="amount_paid cannot be negative")

    reference = (body.reference or "").strip() or None
    key = f"manual:{tenant_id}:{reference}" if reference else f"manual:{uuid.uuid4().hex}"
    tenant = await usage_billing.credit_minutes(
        db,
        tenant_id,
        minutes,
        source="manual",
        key=key,
        plan=body.plan,
        amount_paid=body.amount_paid,
        currency=body.currency.strip().upper() or "USD",
        reference=reference,
        note=body.note or f"Added by {current_super_admin.get('email')}",
        period_end=datetime.utcnow() + usage_billing.BILLING_PERIOD if body.plan else None,
    )
    if tenant is None:
        if not await db.tenants.find_one(usage_billing.tenant_query(tenant_id), {"_id": 1}):
            raise HTTPException(status_code=404, detail="Tenant not found")
        raise HTTPException(status_code=409, detail="This payment reference was already recorded")
    if plan_fields:
        await db.tenants.update_one({"_id": tenant["_id"]}, {"$set": plan_fields})
        tenant.update(plan_fields)
    return {"success": True, "wallet": usage_billing.wallet_summary(tenant)}


class BillingSettingsRequest(BaseModel):
    billing_exempt: Optional[bool] = None  # never pause this business (e.g. your own demo)
    fallback_number: Optional[str] = None  # E.164 number that takes calls while paused; "" clears it


@router.patch("/billing/tenants/{tenant_id}")
async def admin_update_billing_settings(
    tenant_id: str,
    body: BillingSettingsRequest,
    db=Depends(get_database),
):
    fields: Dict[str, Any] = {}
    if body.billing_exempt is not None:
        fields["billing_exempt"] = body.billing_exempt
    if body.fallback_number is not None:
        try:
            fields["billing_fallback_number"] = usage_billing.normalize_fallback_number(body.fallback_number)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    if not fields:
        raise HTTPException(status_code=400, detail="Nothing to update")

    tenant = await db.tenants.find_one_and_update(
        usage_billing.tenant_query(tenant_id),
        {"$set": fields},
        return_document=ReturnDocument.AFTER,
    )
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    if "billing_fallback_number" in fields:
        await usage_billing.apply_fallback_number(tenant)
    await usage_billing.sync_call_access(db, tenant)
    tenant = await db.tenants.find_one({"_id": tenant["_id"]})
    return {"success": True, "wallet": usage_billing.wallet_summary(tenant)}


@router.post("/billing/sync")
async def admin_sync_billing(db=Depends(get_database)):
    """Re-apply pause/resume and call caps to every business, e.g. after switching enforcement on."""
    tenants = await db.tenants.find({}).to_list(length=2000)
    paused = resumed = 0
    for tenant in tenants:
        tenant = await usage_billing.ensure_wallet(db, tenant)
        changes = await usage_billing.sync_call_access(db, tenant)
        if changes.get("calls_paused") is True:
            paused += 1
        elif changes.get("calls_paused") is False:
            resumed += 1
    return {
        "tenants": len(tenants),
        "paused": paused,
        "resumed": resumed,
        "enforcement_enabled": settings.BILLING_ENFORCEMENT_ENABLED,
    }


# ==================== INDUSTRY TEMPLATES ====================

@router.get("/templates")
async def admin_list_templates():
    return [
        {"id": template_id, "label": t["label"], "description": t["description"], "services": [s["name"] for s in t["services"]]}
        for template_id, t in industry_templates.TEMPLATES.items()
    ]


class ApplyTemplateRequest(BaseModel):
    template: str


@router.post("/tenants/{tenant_id}/template")
async def admin_apply_template(tenant_id: str, body: ApplyTemplateRequest, db=Depends(get_database)):
    """
    Set up a business for its niche: the template becomes its AI instructions and greeting
    (pushed to its Vapi assistant, still editable by the owner) and missing starter services are added.
    """
    from routers.assistants import PersonalityConfig
    from services.assistant_service import AssistantService

    if body.template not in industry_templates.TEMPLATES:
        raise HTTPException(status_code=400, detail="Unknown template")
    tenant = await db.tenants.find_one(usage_billing.tenant_query(tenant_id))
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant_id = str(tenant["_id"])

    business_name = (
        tenant.get("business_name")
        or (tenant.get("settings") or {}).get("business_name")
        or tenant.get("name")
        or "our office"
    )
    template = industry_templates.render(body.template, business_name)
    await AssistantService(db).update_personality_settings(
        tenant_id,
        PersonalityConfig(
            system_prompt=template["system_prompt"],
            first_message=template["first_message"],
            temperature=template["temperature"],
        ),
    )

    added = 0
    now = datetime.utcnow()
    for service in template["services"]:
        if await db.services.find_one({"tenant_id": tenant_id, "name": service["name"]}):
            continue
        await db.services.insert_one({
            **service,
            "price": None,
            "active": True,
            "tenant_id": tenant_id,
            "business_id": tenant_id,
            "created_at": now,
            "updated_at": now,
        })
        added += 1

    await db.tenants.update_one({"_id": tenant["_id"]}, {"$set": {"industry": body.template, "updated_at": now}})
    return {"success": True, "template": body.template, "services_added": added}
