"""
Admin API Router
Platform owner endpoints for managing tenants, users, system configuration, and analytics.
Single page admin dashboard - no authentication required.
"""

from fastapi import APIRouter, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
import logging

from models.tenant import TenantResponse, TenantCreate, TenantUpdate
from models.user import UserResponse, Token, UserCreate, UserUpdate
from models.appointment import AppointmentStatus, AppointmentCreate, AppointmentUpdate, AppointmentResponse
from models.service import ServiceCreate, ServiceUpdate, ServiceResponse
from models.conversation import ConversationResponse
from routers.users import get_current_admin
from services.admin_service import get_admin_service, AdminService
from database.mongo_config import get_database

logger = logging.getLogger(__name__)

router = APIRouter()


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
    """Refresh assistant system prompt with current date - fixes hardcoded dates"""
    from services.vapi_service import vapi_service
    from utils.datetime_utils import DateTimeUtils
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
    
    # Generate new date header
    now = DateTimeUtils.now()
    current_date_str = now.strftime("%B %d, %Y")
    tomorrow = now + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%B %d, %Y")
    
    date_header = f"""**CURRENT DATE: {current_date_str} - Use this for all date calculations**
When customers say 'tomorrow', they mean {tomorrow_str}.

"""
    
    # Remove old date header if present
    updated_prompt = re.sub(
        r'\*\*CURRENT DATE:.*?\*\*\n.*?tomorrow.*?\n\n?',
        '',
        system_prompt,
        flags=re.DOTALL
    )
    
    # Inject new date header
    lines = updated_prompt.split('\n')
    if lines and lines[0].strip().startswith('You are'):
        # Insert after the "You are..." line
        updated_prompt = lines[0] + '\n\n' + date_header + '\n'.join(lines[1:])
    else:
        # Insert at the very beginning
        updated_prompt = date_header + updated_prompt
    
    # Update assistant
    result = await vapi_service.update_assistant(
        assistant_id=assistant_id,
        instructions=updated_prompt
    )
    
    if result.get("updated"):
        return {
            "success": True,
            "message": f"Assistant date updated to {current_date_str}",
            "current_date": current_date_str,
            "tomorrow": tomorrow_str,
            "assistant_id": assistant_id
        }
    else:
        return {"error": "Failed to update assistant", "details": result}


