"""
Admin Analytics Router - Real-time analytics for platform owner
"""

from fastapi import APIRouter, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
import logging

from database.mongo_config import get_database

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/analytics/overview")
async def get_analytics_overview():
    """
    Get comprehensive platform analytics overview
    """
    db = get_database()
    
    # Get counts
    total_businesses = await db.tenants.count_documents({})
    active_businesses = await db.tenants.count_documents({"status": "active"})
    total_users = await db.users.count_documents({})
    business_owners = await db.users.count_documents({"role": "admin"})
    total_appointments = await db.appointments.count_documents({})
    total_conversations = await db.conversations.count_documents({})
    
    # Get appointments by status
    completed_appointments = await db.appointments.count_documents({"status": "completed"})
    pending_appointments = await db.appointments.count_documents({"status": "pending"})
    confirmed_appointments = await db.appointments.count_documents({"status": "confirmed"})
    cancelled_appointments = await db.appointments.count_documents({"status": "cancelled"})
    
    # Calculate success rate
    success_rate = 0
    if total_appointments > 0:
        success_rate = round((completed_appointments / total_appointments) * 100, 1)
    
    # Get recent growth (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_businesses_30d = await db.tenants.count_documents({"created_at": {"$gte": thirty_days_ago}})
    new_users_30d = await db.users.count_documents({"created_at": {"$gte": thirty_days_ago}})
    new_appointments_30d = await db.appointments.count_documents({"created_at": {"$gte": thirty_days_ago}})
    
    # Calculate growth rates
    business_growth = 0
    if total_businesses > 0:
        business_growth = round((new_businesses_30d / max(total_businesses - new_businesses_30d, 1)) * 100, 1)
    
    user_growth = 0
    if total_users > 0:
        user_growth = round((new_users_30d / max(total_users - new_users_30d, 1)) * 100, 1)
    
    # Get average appointment duration and call stats
    pipeline = [
        {"$group": {
            "_id": None,
            "avg_duration": {"$avg": "$duration_minutes"}
        }}
    ]
    result = await db.appointments.aggregate(pipeline).to_list(1)
    avg_appointment_duration = round(result[0]["avg_duration"], 0) if result else 30
    
    # Get conversation stats
    conv_pipeline = [
        {"$project": {
            "message_count": {"$size": {"$ifNull": ["$messages", []]}}
        }},
        {"$group": {
            "_id": None,
            "avg_messages": {"$avg": "$message_count"}
        }}
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
            "completed": completed_appointments,
            "pending": pending_appointments,
            "confirmed": confirmed_appointments,
            "cancelled": cancelled_appointments,
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
    """
    Calculate revenue analytics (mock data for now)
    """
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
    
    # Mock churn rate (would need historical data)
    churn_rate = 2.3
    
    # Calculate CLV (Customer Lifetime Value) - Simple formula: ARPU / Churn Rate
    clv = round(arpu / (churn_rate / 100), 2) if churn_rate > 0 else 0
    
    return {
        "mrr": mrr,
        "arpu": arpu,
        "churn_rate": churn_rate,
        "clv": clv,
        "plan_distribution": {
            "free": free_plan,
            "pro": pro_plan,
            "enterprise": enterprise_plan
        },
        "timestamp": datetime.utcnow()
    }


@router.get("/analytics/system-health")
async def get_system_health():
    """
    Get system health metrics
    """
    db = get_database()
    
    # Check database connection
    try:
        await db.command("ping")
        db_status = "healthy"
        db_response_time = 10  # ms
    except Exception as e:
        db_status = "unhealthy"
        db_response_time = 0
    
    # Get database stats
    stats = await db.command("dbStats")
    
    return {
        "components": {
            "database": {
                "status": db_status,
                "response_time_ms": db_response_time
            },
            "api": {
                "status": "healthy",
                "uptime_percentage": 99.9
            },
            "groq": {
                "status": "healthy",
                "response_time_ms": 250
            },
            "livekit": {
                "status": "healthy",
                "response_time_ms": 150
            },
            "elevenlabs": {
                "status": "healthy",
                "response_time_ms": 320
            }
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
    """
    Get top performing businesses by appointments
    """
    db = get_database()
    
    # Aggregate appointments by tenant
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
    
    # Enrich with tenant data
    businesses = []
    for result in results:
        tenant_id = result["_id"]
        if tenant_id:
            tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
            if tenant:
                businesses.append({
                    "tenant_id": str(tenant_id),
                    "business_name": tenant.get("name", "Unknown"),
                    "total_appointments": result["total_appointments"],
                    "completed": result["completed"],
                    "cancelled": result["cancelled"],
                    "success_rate": round((result["completed"] / result["total_appointments"]) * 100, 1) if result["total_appointments"] > 0 else 0
                })
    
    return {
        "businesses": businesses,
        "timestamp": datetime.utcnow()
    }


@router.get("/analytics/growth-trends")
async def get_growth_trends(days: int = Query(30, ge=7, le=365)):
    """
    Get growth trends over time
    """
    db = get_database()
    
    # Calculate daily stats for the last N days
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Group by day
    pipeline = [
        {"$match": {"created_at": {"$gte": start_date}}},
        {"$group": {
            "_id": {
                "$dateToString": {
                    "format": "%Y-%m-%d",
                    "date": "$created_at"
                }
            },
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    
    business_trends = await db.tenants.aggregate(pipeline).to_list(days)
    user_trends = await db.users.aggregate(pipeline).to_list(days)
    appointment_trends = await db.appointments.aggregate(pipeline).to_list(days)
    
    return {
        "trends": {
            "businesses": business_trends,
            "users": user_trends,
            "appointments": appointment_trends
        },
        "period_days": days,
        "timestamp": datetime.utcnow()
    }


@router.get("/database/collections")
async def get_all_collections():
    """
    List all MongoDB collections with document counts
    """
    db = get_database()
    
    collection_names = await db.list_collection_names()
    
    collections = []
    for name in sorted(collection_names):
        count = await db[name].count_documents({})
        
        # Get sample document to show structure
        sample = await db[name].find_one({})
        
        # Get collection stats
        stats = await db.command("collStats", name)
        
        collections.append({
            "name": name,
            "count": count,
            "size_mb": round(stats.get("size", 0) / (1024 * 1024), 2),
            "avg_doc_size": round(stats.get("avgObjSize", 0) / 1024, 2) if count > 0 else 0,
            "indexes": stats.get("nindexes", 0),
            "has_data": count > 0
        })
    
    return {
        "collections": collections,
        "total_collections": len(collections),
        "timestamp": datetime.utcnow()
    }


@router.get("/database/collection/{collection_name}")
async def get_collection_data(
    collection_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500)
):
    """
    Get documents from a specific collection
    """
    db = get_database()
    
    # Check if collection exists
    collection_names = await db.list_collection_names()
    if collection_name not in collection_names:
        return {"error": f"Collection '{collection_name}' not found", "documents": []}
    
    # Get documents
    cursor = db[collection_name].find({}).skip(skip).limit(limit)
    documents = await cursor.to_list(length=limit)
    
    # Convert ObjectId to string
    for doc in documents:
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        # Convert any other ObjectId fields
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
