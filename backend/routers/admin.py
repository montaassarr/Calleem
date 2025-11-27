"""
Admin API Router
Superuser endpoints for managing tenants, users, and system configuration
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
import logging

from models.core.tenants import Tenant, TenantStatus, TenantPlan, TenantResponse, TenantCreate, TenantUpdate
from models.core.users import User, UserRole, UserResponse, Token, UserCreate, UserUpdate
from models.appointments.appointments import Appointment, AppointmentStatus, AppointmentCreate, AppointmentUpdate, AppointmentResponse
from models.business.services import Service, ServiceCreate, ServiceUpdate, ServiceResponse
from models.communication.conversations import Conversation, ConversationResponse, ConversationSummary
from models.business.business_config import BusinessConfig
from database.mongo_config import get_database
from routers.users import get_current_admin, get_super_admin, create_access_token, hash_password
from utils.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


# --- Tenant Management ---

@router.get("/tenants", response_model=List[TenantResponse], response_model_by_alias=False)
async def list_tenants(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    current_admin: dict = Depends(get_super_admin)
):
    """List all tenants (Super Admin only)"""
    db = get_database()
    query = {}
    
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
        
    cursor = db.tenants.find(query).skip(skip).limit(limit)
    tenants = await cursor.to_list(length=limit)
    
    results = []
    for t in tenants:
        t["_id"] = str(t["_id"])
        # Inject defaults for missing fields
        if "total_calls" not in t:
            t["total_calls"] = 0
        if "total_minutes" not in t:
            t["total_minutes"] = 0.0
        if "settings" not in t:
            t["settings"] = {
                "business_name": t.get("name", "Unknown"),
                "timezone": "UTC",
                "currency": "USD"
            }
        results.append(t)
        
    return [TenantResponse(**t) for t in results]


@router.post("/tenants", response_model=TenantResponse, status_code=201, response_model_by_alias=False)
async def create_tenant(
    tenant: TenantCreate,
    current_admin: dict = Depends(get_super_admin)
):
    """Create a new tenant (Super Admin only)"""
    db = get_database()
    
    # Check if email exists
    # Check if name exists
    if await db.tenants.find_one({"name": tenant.name}):
        raise HTTPException(status_code=400, detail="Tenant name already exists")
        
    tenant_dict = tenant.model_dump()
    tenant_dict["created_at"] = datetime.utcnow()
    tenant_dict["updated_at"] = datetime.utcnow()
    tenant_dict["total_calls"] = 0
    tenant_dict["total_minutes"] = 0.0
    
    result = await db.tenants.insert_one(tenant_dict)
    
    created_tenant = await db.tenants.find_one({"_id": result.inserted_id})
    created_tenant["_id"] = str(created_tenant["_id"])
    
    return TenantResponse(**created_tenant)


@router.get("/tenants/{tenant_id}", response_model=TenantResponse, response_model_by_alias=False)
async def get_tenant(
    tenant_id: str,
    current_admin: dict = Depends(get_super_admin)
):
    """Get tenant details"""
    if not ObjectId.is_valid(tenant_id):
        raise HTTPException(status_code=400, detail="Invalid tenant ID")
        
    db = get_database()
    tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
        
    tenant["_id"] = str(tenant["_id"])
    return TenantResponse(**tenant)


@router.put("/tenants/{tenant_id}", response_model=TenantResponse, response_model_by_alias=False)
async def update_tenant(
    tenant_id: str,
    update: TenantUpdate,
    current_admin: dict = Depends(get_super_admin)
):
    """Update tenant details"""
    if not ObjectId.is_valid(tenant_id):
        raise HTTPException(status_code=400, detail="Invalid tenant ID")
        
    db = get_database()
    
    update_data = {
        k: v for k, v in update.model_dump(exclude_unset=True).items()
        if v is not None
    }
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
        
    update_data["updated_at"] = datetime.utcnow()
    
    await db.tenants.update_one(
        {"_id": ObjectId(tenant_id)},
        {"$set": update_data}
    )
    
    updated_tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
    updated_tenant["_id"] = str(updated_tenant["_id"])
    
    return TenantResponse(**updated_tenant)


# --- User Management (Global) ---

@router.get("/users", response_model=List[UserResponse])
async def list_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    tenant_id: Optional[str] = None,
    current_admin: dict = Depends(get_current_admin)
):
    """List all users across all tenants"""
    db = get_database()
    query = {}
    
    if tenant_id and current_admin.get("role") == "super_admin":
        query["tenant_id"] = tenant_id
    else:
        # Regular admin can only see their own tenant's users
        query["tenant_id"] = current_admin.get("tenant_id") or current_admin.get("business_id")
        
    cursor = db.users.find(query).skip(skip).limit(limit)
    users = await cursor.to_list(length=limit)
    
    results = []
    for u in users:
        u["id"] = str(u["_id"])
        if "tenant_id" in u and u["tenant_id"]:
            u["tenant_id"] = str(u["tenant_id"])
        results.append(u)
        
    return [UserResponse(**u) for u in results]


@router.post("/users/{user_id}/impersonate", response_model=Token)
async def impersonate_user(
    user_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Generate a login token for a specific user (Impersonation)"""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
        
    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Create token for this user
    access_token = create_access_token(
        data={
            "sub": str(user["_id"]),
            "username": user["username"],
            "role": user["role"],
            "tenant_id": str(user.get("tenant_id")) if user.get("tenant_id") else None,
            "impersonator": current_admin["username"]  # Audit trail
        }
    )
    
    logger.warning(f"Admin {current_admin['username']} impersonating user {user['username']}")
    
    return {"access_token": access_token, "token_type": "bearer"}


# --- System Management ---

@router.get("/analytics/global")
async def get_global_analytics(current_admin: dict = Depends(get_super_admin)):
    """Get global system stats"""
    db = get_database()
    
    total_tenants = await db.tenants.count_documents({})
    active_tenants = await db.tenants.count_documents({"status": TenantStatus.ACTIVE})
    total_users = await db.users.count_documents({})
    total_appointments = await db.appointments.count_documents({})
    total_conversations = await db.conversations.count_documents({})
    
    return {
        "tenants": {
            "total": total_tenants,
            "active": active_tenants
        },
        "users": total_users,
        "appointments": total_appointments,
        "conversations": total_conversations,
        "timestamp": datetime.utcnow()
    }


@router.post("/data/clean")
async def trigger_data_cleaning(current_admin: dict = Depends(get_current_admin)):
    """Trigger manual data cleaning job"""
    # TODO: Implement actual cleaning logic
    return {"message": "Data cleaning job started", "job_id": "mock_job_123"}


# --- User Management (CRUD) ---

@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    user: UserCreate,
    current_admin: dict = Depends(get_current_admin)
):
    """Create a new user (Admin)"""
    db = get_database()
    
    if await db.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
        
    if await db.users.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already taken")
    
    user_dict = user.dict(exclude={"password"})
    user_dict["hashed_password"] = hash_password(user.password)
    user_dict["created_at"] = datetime.utcnow()
    user_dict["updated_at"] = datetime.utcnow()
    user_dict["last_login"] = None
    user_dict["tenant_id"] = current_admin.get("tenant_id") or current_admin.get("business_id")
    user_dict["business_id"] = user_dict["tenant_id"]
    
    result = await db.users.insert_one(user_dict)
    
    created_user = await db.users.find_one({"_id": result.inserted_id})
    created_user["id"] = str(created_user["_id"])
    
    return UserResponse(**created_user)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    update: UserUpdate,
    current_admin: dict = Depends(get_current_admin)
):
    """Update user details"""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
        
    db = get_database()
    
    update_data = {k: v for k, v in update.dict(exclude_unset=True).items() if v is not None}
    
    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))
        
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
        
    update_data["updated_at"] = datetime.utcnow()
    
    # Ensure user belongs to admin's tenant (unless super admin)
    query = {"_id": ObjectId(user_id)}
    if current_admin.get("role") != "super_admin":
        query["tenant_id"] = current_admin.get("tenant_id") or current_admin.get("business_id")
        
    result = await db.users.update_one(
        query,
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
        
    updated_user = await db.users.find_one({"_id": ObjectId(user_id)})
    updated_user["id"] = str(updated_user["_id"])
    
    return UserResponse(**updated_user)


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Delete a user"""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
        
    db = get_database()
    # Ensure user belongs to admin's tenant (unless super admin)
    query = {"_id": ObjectId(user_id)}
    if current_admin.get("role") != "super_admin":
        query["tenant_id"] = current_admin.get("tenant_id") or current_admin.get("business_id")
        
    result = await db.users.delete_one(query)
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")


# --- Appointments Management ---

@router.get("/appointments", response_model=List[AppointmentResponse], response_model_by_alias=False)
async def list_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[AppointmentStatus] = None,
    current_admin: dict = Depends(get_current_admin)
):
    """List all appointments"""
    db = get_database()
    query = {}
    
    # Filter by tenant_id
    if current_admin.get("role") != "super_admin":
        query["tenant_id"] = current_admin.get("tenant_id") or current_admin.get("business_id")
        
    if status:
        query["status"] = status
        
    cursor = db.appointments.find(query).sort("datetime", -1).skip(skip).limit(limit)
    appointments = await cursor.to_list(length=limit)
    
    results = []
    for appt in appointments:
        appt["_id"] = str(appt["_id"])
        results.append(appt)
        
    return [AppointmentResponse(**appt) for appt in results]


@router.post("/appointments", response_model=AppointmentResponse, status_code=201, response_model_by_alias=False)
async def create_appointment(
    appointment: AppointmentCreate,
    current_admin: dict = Depends(get_current_admin)
):
    """Create a new appointment"""
    db = get_database()
    
    appt_dict = appointment.dict()
    appt_dict["status"] = AppointmentStatus.CONFIRMED
    appt_dict["created_at"] = datetime.utcnow()
    appt_dict["updated_at"] = datetime.utcnow()
    appt_dict["tenant_id"] = current_admin.get("tenant_id") or current_admin.get("business_id")
    appt_dict["business_id"] = appt_dict["tenant_id"]
    
    result = await db.appointments.insert_one(appt_dict)
    
    created_appt = await db.appointments.find_one({"_id": result.inserted_id})
    created_appt["_id"] = str(created_appt["_id"])
    
    return AppointmentResponse(**created_appt)


@router.put("/appointments/{appointment_id}", response_model=AppointmentResponse, response_model_by_alias=False)
async def update_appointment(
    appointment_id: str,
    update: AppointmentUpdate,
    current_admin: dict = Depends(get_current_admin)
):
    """Update appointment"""
    if not ObjectId.is_valid(appointment_id):
        raise HTTPException(status_code=400, detail="Invalid appointment ID")
        
    db = get_database()
    
    update_data = {k: v for k, v in update.dict(exclude_unset=True).items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
        
    update_data["updated_at"] = datetime.utcnow()
    
    # Filter by tenant_id
    query = {"_id": ObjectId(appointment_id)}
    if current_admin.get("role") != "super_admin":
        query["tenant_id"] = current_admin.get("tenant_id") or current_admin.get("business_id")
        
    result = await db.appointments.update_one(
        query,
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Appointment not found")
        
    updated_appt = await db.appointments.find_one({"_id": ObjectId(appointment_id)})
    updated_appt["_id"] = str(updated_appt["_id"])
    
    return AppointmentResponse(**updated_appt)


@router.delete("/appointments/{appointment_id}", status_code=204)
async def delete_appointment(
    appointment_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Delete an appointment"""
    if not ObjectId.is_valid(appointment_id):
        raise HTTPException(status_code=400, detail="Invalid appointment ID")
        
    db = get_database()
    # Filter by tenant_id
    query = {"_id": ObjectId(appointment_id)}
    if current_admin.get("role") != "super_admin":
        query["tenant_id"] = current_admin.get("tenant_id") or current_admin.get("business_id")
        
    result = await db.appointments.delete_one(query)
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Appointment not found")


# --- Services Management ---

@router.get("/services", response_model=List[ServiceResponse], response_model_by_alias=False)
async def list_services(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_admin: dict = Depends(get_current_admin)
):
    """List all services"""
    db = get_database()
    db = get_database()
    
    # Filter by tenant_id
    query = {}
    if current_admin.get("role") != "super_admin":
        query["tenant_id"] = current_admin.get("tenant_id") or current_admin.get("business_id")
        
    cursor = db.services.find(query).skip(skip).limit(limit)
    services = await cursor.to_list(length=limit)
    
    results = []
    for s in services:
        s["_id"] = str(s["_id"])
        results.append(s)
        
    return [ServiceResponse(**s) for s in results]


@router.post("/services", response_model=ServiceResponse, status_code=201, response_model_by_alias=False)
async def create_service(
    service: ServiceCreate,
    current_admin: dict = Depends(get_current_admin)
):
    """Create a new service"""
    db = get_database()
    
    service_dict = service.dict()
    service_dict["created_at"] = datetime.utcnow()
    service_dict["updated_at"] = datetime.utcnow()
    service_dict["tenant_id"] = current_admin.get("tenant_id") or current_admin.get("business_id")
    service_dict["business_id"] = service_dict["tenant_id"]
    
    result = await db.services.insert_one(service_dict)
    
    created_service = await db.services.find_one({"_id": result.inserted_id})
    created_service["_id"] = str(created_service["_id"])
    
    return ServiceResponse(**created_service)


@router.put("/services/{service_id}", response_model=ServiceResponse, response_model_by_alias=False)
async def update_service(
    service_id: str,
    update: ServiceUpdate,
    current_admin: dict = Depends(get_current_admin)
):
    """Update service"""
    if not ObjectId.is_valid(service_id):
        raise HTTPException(status_code=400, detail="Invalid service ID")
        
    db = get_database()
    
    update_data = {k: v for k, v in update.dict(exclude_unset=True).items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
        
    update_data["updated_at"] = datetime.utcnow()
    
    # Filter by tenant_id
    query = {"_id": ObjectId(service_id)}
    if current_admin.get("role") != "super_admin":
        query["tenant_id"] = current_admin.get("tenant_id") or current_admin.get("business_id")
        
    result = await db.services.update_one(
        query,
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Service not found")
        
    updated_service = await db.services.find_one({"_id": ObjectId(service_id)})
    updated_service["_id"] = str(updated_service["_id"])
    
    return ServiceResponse(**updated_service)


@router.delete("/services/{service_id}", status_code=204)
async def delete_service(
    service_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Delete a service"""
    if not ObjectId.is_valid(service_id):
        raise HTTPException(status_code=400, detail="Invalid service ID")
        
    db = get_database()
    db = get_database()
    
    # Filter by tenant_id
    query = {"_id": ObjectId(service_id)}
    if current_admin.get("role") != "super_admin":
        query["tenant_id"] = current_admin.get("tenant_id") or current_admin.get("business_id")
        
    result = await db.services.delete_one(query)
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Service not found")


# --- Conversations Management ---

@router.get("/conversations", response_model=List[ConversationResponse], response_model_by_alias=False)
async def list_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    phone: Optional[str] = None,
    current_admin: dict = Depends(get_current_admin)
):
    """List all conversations"""
    db = get_database()
    query = {}
    
    # Filter by tenant_id
    if current_admin.get("role") != "super_admin":
        query["tenant_id"] = current_admin.get("tenant_id") or current_admin.get("business_id")
        
    if phone:
        query["phone_number"] = {"$regex": phone}
        
    cursor = db.conversations.find(query).sort("updated_at", -1).skip(skip).limit(limit)
    conversations = await cursor.to_list(length=limit)
    
    results = []
    for conv in conversations:
        conv["_id"] = str(conv["_id"])
        results.append(conv)
        
    return [ConversationResponse(**conv) for conv in results]


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Delete a conversation"""
    if not ObjectId.is_valid(conversation_id):
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
        
    db = get_database()
    # Filter by tenant_id
    query = {"_id": ObjectId(conversation_id)}
    if current_admin.get("role") != "super_admin":
        query["tenant_id"] = current_admin.get("tenant_id") or current_admin.get("business_id")
        
    result = await db.conversations.delete_one(query)
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")


# --- Business Config Management ---

from pydantic import BaseModel, Field

class BusinessConfig(BaseModel):
    """Business configuration model"""
    business_name: str
    timezone: str = "UTC"
    currency: str = "USD"
    phone_number: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    tenant_id: Optional[str] = None
    is_configured: bool = False
    
    # API Keys
    vapi_api_key: Optional[str] = None
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    
    # AI Settings
    system_prompt: Optional[str] = None
    
    class Config:
        extra = "allow"

@router.get("/config", response_model=BusinessConfig)
async def get_business_config(current_admin: dict = Depends(get_current_admin)):
    """Get business configuration"""
    db = get_database()
    
    # Filter by tenant_id
    tenant_id = current_admin.get("tenant_id") or current_admin.get("business_id")
    query = {}
    if tenant_id:
        query["tenant_id"] = tenant_id
        
    config = await db.business_config.find_one(query)
    
    # Fetch tenant status
    is_configured = False
    if tenant_id:
        tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
        if tenant:
            is_configured = tenant.get("is_configured", False)
    
    if not config:
        # Return defaults if not found
        return BusinessConfig(
            business_name="My Business",
            timezone="UTC",
            currency="USD",
            is_configured=is_configured
        )
        
    if "_id" in config:
        del config["_id"]
        
    # Inject is_configured from tenant
    config["is_configured"] = is_configured
    
    return BusinessConfig(**config)


@router.put("/config", response_model=BusinessConfig)
async def update_business_config(
    config: BusinessConfig,
    current_admin: dict = Depends(get_current_admin)
):
    """Update business configuration"""
    db = get_database()
    
    config_dict = config.dict(exclude_unset=True)
    config_dict["updated_at"] = datetime.utcnow()
    
    # Filter by tenant_id
    tenant_id = current_admin.get("tenant_id") or current_admin.get("business_id")
    query = {}
    if tenant_id:
        query["tenant_id"] = tenant_id
        config_dict["tenant_id"] = tenant_id
        
    await db.business_config.update_one(
        query,
        {"$set": config_dict},
        upsert=True
    )
    
    updated_config = await db.business_config.find_one(query)
    if "_id" in updated_config:
        del updated_config["_id"]
    return BusinessConfig(**updated_config)
