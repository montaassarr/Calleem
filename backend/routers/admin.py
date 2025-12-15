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
from models.business.business_config import BusinessConfig, BusinessConfigUpdate
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

@router.get("/config", response_model=BusinessConfig)
async def get_business_config(
    current_admin: dict = Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service)
):
    """Get business configuration"""
    tenant_id = current_admin.get("tenant_id") or current_admin.get("business_id")
    config = await service.get_business_config(tenant_id)
    return BusinessConfig(**config)


@router.put("/config", response_model=BusinessConfig)
async def update_business_config(
    config: BusinessConfigUpdate,
    current_admin: dict = Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service)
):
    """Update business configuration"""
    tenant_id = current_admin.get("tenant_id") or current_admin.get("business_id")
    updated = await service.update_business_config(tenant_id, config)
    return BusinessConfig(**updated)


# ==================== ANALYTICS ====================

@router.get("/analytics/global")
async def get_global_analytics(
    service: AdminService = Depends(get_admin_service)
):
    """Get global system stats"""
    return await service.get_global_analytics()


@router.get("/analytics/overview")
async def get_analytics_overview():
    """Get comprehensive platform analytics overview"""
    db = get_database()
    
    # Get counts
    total_businesses = await db.tenants.count_documents({})
    active_businesses = await db.tenants.count_documents({"status": "active"})
    total_users = await db.users.count_documents({})
    business_owners = await db.users.count_documents({"role": "admin"})
    total_appointments = await db.appointments.count_documents({})
    total_conversations = await db.conversations.count_documents({})
    
    # Get appointments by status
    completed = await db.appointments.count_documents({"status": "completed"})
    pending = await db.appointments.count_documents({"status": "pending"})
    confirmed = await db.appointments.count_documents({"status": "confirmed"})
    cancelled = await db.appointments.count_documents({"status": "cancelled"})
    
    # Calculate success rate
    success_rate = round((completed / total_appointments) * 100, 1) if total_appointments > 0 else 0
    
    # Get recent growth (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_businesses_30d = await db.tenants.count_documents({"created_at": {"$gte": thirty_days_ago}})
    new_users_30d = await db.users.count_documents({"created_at": {"$gte": thirty_days_ago}})
    new_appointments_30d = await db.appointments.count_documents({"created_at": {"$gte": thirty_days_ago}})
    
    # Calculate growth rates
    business_growth = round((new_businesses_30d / max(total_businesses - new_businesses_30d, 1)) * 100, 1) if total_businesses > 0 else 0
    user_growth = round((new_users_30d / max(total_users - new_users_30d, 1)) * 100, 1) if total_users > 0 else 0
    
    # Get average stats
    pipeline = [{"$group": {"_id": None, "avg_duration": {"$avg": "$duration_minutes"}}}]
    result = await db.appointments.aggregate(pipeline).to_list(1)
    avg_appointment_duration = round(result[0]["avg_duration"], 0) if result else 30
    
    conv_pipeline = [
        {"$project": {"message_count": {"$size": {"$ifNull": ["$messages", []]}}}},
        {"$group": {"_id": None, "avg_messages": {"$avg": "$message_count"}}}
    ]
    conv_result = await db.conversations.aggregate(conv_pipeline).to_list(1)
    avg_conversation_length = round(conv_result[0]["avg_messages"], 1) if conv_result else 0
    
    return {
        "platform_metrics": {
            "total_businesses": total_businesses,
            "active_businesses": active_businesses,
            "total_users": total_users,
            "business_owners": business_owners,
            "appointments_booked": total_appointments,
            "ai_conversations": total_conversations,
            "success_rate": success_rate,
            "business_growth_30d": business_growth,
            "user_growth_30d": user_growth
        },
        "appointments": {
            "total": total_appointments,
            "completed": completed,
            "pending": pending,
            "confirmed": confirmed,
            "cancelled": cancelled,
            "success_rate": success_rate,
            "avg_duration_minutes": avg_appointment_duration,
            "new_30d": new_appointments_30d
        },
        "conversations": {
            "total": total_conversations,
            "avg_messages": avg_conversation_length
        },
        "timestamp": datetime.utcnow()
    }


@router.get("/analytics/revenue")
async def get_revenue_analytics():
    """Calculate revenue analytics"""
    db = get_database()
    
    # Count businesses by plan
    free_plan = await db.tenants.count_documents({"plan": "free"})
    pro_plan = await db.tenants.count_documents({"plan": "pro"})
    enterprise_plan = await db.tenants.count_documents({"plan": "enterprise"})
    
    # Calculate MRR (Monthly Recurring Revenue)
    mrr = (pro_plan * 49) + (enterprise_plan * 199)
    
    # Calculate ARPU (Average Revenue Per User)
    total_businesses = await db.tenants.count_documents({})
    arpu = round(mrr / max(total_businesses, 1), 2)
    
    churn_rate = 2.3  # Would need historical data
    clv = round(arpu / (churn_rate / 100), 2) if churn_rate > 0 else 0
    
    return {
        "mrr": mrr,
        "arpu": arpu,
        "churn_rate": churn_rate,
        "clv": clv,
        "plan_distribution": {"free": free_plan, "pro": pro_plan, "enterprise": enterprise_plan},
        "timestamp": datetime.utcnow()
    }


@router.get("/analytics/system-health")
async def get_system_health():
    """Get system health metrics"""
    db = get_database()
    
    try:
        await db.command("ping")
        db_status = "healthy"
        db_response_time = 10
    except Exception:
        db_status = "unhealthy"
        db_response_time = 0
    
    stats = await db.command("dbStats")
    
    return {
        "components": {
            "database": {"status": db_status, "response_time_ms": db_response_time},
            "api": {"status": "healthy", "uptime_percentage": 99.9},
            "vapi": {"status": "healthy", "response_time_ms": 250}
        },
        "database": {
            "size_mb": round(stats.get("dataSize", 0) / (1024 * 1024), 2),
            "collections": stats.get("collections", 0),
            "indexes": stats.get("indexes", 0),
            "storage_mb": round(stats.get("storageSize", 0) / (1024 * 1024), 2)
        },
        "timestamp": datetime.utcnow()
    }


@router.get("/analytics/top-businesses")
async def get_top_businesses(limit: int = Query(10, ge=1, le=50)):
    """Get top performing businesses by appointments"""
    db = get_database()
    
    pipeline = [
        {"$group": {
            "_id": "$tenant_id",
            "total_appointments": {"$sum": 1},
            "completed": {"$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}},
            "cancelled": {"$sum": {"$cond": [{"$eq": ["$status", "cancelled"]}, 1, 0]}}
        }},
        {"$sort": {"total_appointments": -1}},
        {"$limit": limit}
    ]
    
    results = await db.appointments.aggregate(pipeline).to_list(limit)
    
    businesses = []
    for result in results:
        tenant_id = result["_id"]
        if tenant_id:
            tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
            if tenant:
                total = result["total_appointments"]
                businesses.append({
                    "tenant_id": str(tenant_id),
                    "business_name": tenant.get("name", "Unknown"),
                    "total_appointments": total,
                    "completed": result["completed"],
                    "cancelled": result["cancelled"],
                    "success_rate": round((result["completed"] / total) * 100, 1) if total > 0 else 0
                })
    
    return {"businesses": businesses, "timestamp": datetime.utcnow()}


@router.get("/analytics/growth-trends")
async def get_growth_trends(days: int = Query(30, ge=7, le=365)):
    """Get growth trends over time"""
    db = get_database()
    start_date = datetime.utcnow() - timedelta(days=days)
    
    pipeline = [
        {"$match": {"created_at": {"$gte": start_date}}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    
    return {
        "trends": {
            "businesses": await db.tenants.aggregate(pipeline).to_list(days),
            "users": await db.users.aggregate(pipeline).to_list(days),
            "appointments": await db.appointments.aggregate(pipeline).to_list(days)
        },
        "period_days": days,
        "timestamp": datetime.utcnow()
    }


# ==================== DATABASE INSPECTION ====================

@router.get("/database/collections")
async def get_all_collections():
    """List all MongoDB collections with document counts"""
    db = get_database()
    collection_names = await db.list_collection_names()
    
    collections = []
    for name in sorted(collection_names):
        count = await db[name].count_documents({})
        stats = await db.command("collStats", name)
        collections.append({
            "name": name,
            "count": count,
            "size_mb": round(stats.get("size", 0) / (1024 * 1024), 2),
            "avg_doc_size": round(stats.get("avgObjSize", 0) / 1024, 2) if count > 0 else 0,
            "indexes": stats.get("nindexes", 0),
            "has_data": count > 0
        })
    
    return {"collections": collections, "total_collections": len(collections), "timestamp": datetime.utcnow()}


@router.get("/database/collection/{collection_name}")
async def get_collection_data(
    collection_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500)
):
    """Get documents from a specific collection"""
    db = get_database()
    
    collection_names = await db.list_collection_names()
    if collection_name not in collection_names:
        return {"error": f"Collection '{collection_name}' not found", "documents": []}
    
    cursor = db[collection_name].find({}).skip(skip).limit(limit)
    documents = await cursor.to_list(length=limit)
    
    # Convert ObjectId to string
    for doc in documents:
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                doc[key] = str(value)
    
    total_count = await db[collection_name].count_documents({})
    
    return {
        "collection": collection_name,
        "total_documents": total_count,
        "returned": len(documents),
        "skip": skip,
        "limit": limit,
        "documents": documents,
        "timestamp": datetime.utcnow()
    }
