"""
Services API Router
CRUD operations for barber shop services
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Request
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import logging

from models.service import (
    ServiceCreate, 
    ServiceUpdate, 
    ServiceResponse
)
from database.mongo_config import get_database
from routers.users import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


def get_tenant_from_header(request: Request) -> str:
    """Extract tenant_id from X-Tenant-ID header for internal calls"""
    tenant_id = request.headers.get("X-Tenant-ID")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID header required")
    return tenant_id


@router.get("/agent/list")
async def agent_list_services(
    request: Request,
    active_only: bool = Query(True, description="Return only active services")
):
    """
    Agent-accessible service listing (no JWT required)
    Used by AI assistant to fetch available services dynamically
    """
    try:
        tenant_id = get_tenant_from_header(request)
        
        db = get_database()
        query = {"tenant_id": tenant_id}
        if active_only:
            query["active"] = True
        
        services = await db.services.find(query).to_list(length=100)
        
        # Format for AI consumption - simplified response
        result = []
        for svc in services:
            result.append({
                "name": svc.get("name"),
                "description": svc.get("description", ""),
                "price": float(svc.get("price", 0)) if svc.get("price") else 0
            })
        
        logger.info(f"Agent fetched {len(result)} services for tenant {tenant_id}")
        
        return {"services": result, "count": len(result)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in agent services list: {e}", exc_info=True)
        return {"services": [], "count": 0, "error": "Failed to fetch services"}


@router.post("/", response_model=ServiceResponse, status_code=201)
async def create_service(
    service: ServiceCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new service"""
    try:
        db = get_database()
        
        # Get tenant_id
        tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
        
        # Check if service with same name exists for this tenant
        existing = await db.services.find_one({"name": service.name, "tenant_id": tenant_id})
        if existing:
            raise HTTPException(status_code=400, detail="Service with this name already exists")
        
        # Prepare service document
        service_dict = service.dict()
        service_dict["tenant_id"] = tenant_id
        service_dict["business_id"] = tenant_id # Legacy support
        service_dict["created_at"] = datetime.utcnow()
        service_dict["updated_at"] = datetime.utcnow()
        
        # Insert into database
        result = await db.services.insert_one(service_dict)
        
        # Retrieve created service
        created_service = await db.services.find_one({"_id": result.inserted_id})
        created_service["id"] = str(created_service["_id"])
        if "_id" in created_service:
            del created_service["_id"]
        
        logger.info(f"✅ Service created: {created_service['name']}")
        
        return ServiceResponse(**created_service)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating service: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create service")


@router.get("/", response_model=List[ServiceResponse])
async def list_services(
    active_only: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: dict = Depends(get_current_user)
):
    """List all services"""
    try:
        db = get_database()
        
        # Build query
        tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
        query = {"tenant_id": tenant_id}
        if active_only:
            query["active"] = True
        
        # Fetch services
        cursor = db.services.find(query).skip(skip).limit(limit)
        services = await cursor.to_list(length=limit)
        
        # Format response
        for service in services:
            service["id"] = str(service["_id"])
            if "_id" in service:
                del service["_id"]
        
        logger.info(f"Retrieved {len(services)} services")
        
        return [ServiceResponse(**svc) for svc in services]
        
    except Exception as e:
        logger.error(f"Error listing services: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve services")


@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(
    service_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific service by ID"""
    try:
        db = get_database()
        
        if not ObjectId.is_valid(service_id):
            raise HTTPException(status_code=400, detail="Invalid service ID")
        
        # Filter by tenant_id
        tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
        query = {"_id": ObjectId(service_id)}
        if tenant_id:
            query["tenant_id"] = tenant_id
            
        service = await db.services.find_one(query)
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        service["id"] = str(service["_id"])
        if "_id" in service:
            del service["_id"]
        
        return ServiceResponse(**service)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve service")


@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: str, 
    update: ServiceUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a service"""
    try:
        db = get_database()
        
        if not ObjectId.is_valid(service_id):
            raise HTTPException(status_code=400, detail="Invalid service ID")
        
        # Check if exists
        # Check if exists and belongs to tenant
        tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
        query = {"_id": ObjectId(service_id)}
        if tenant_id:
            query["tenant_id"] = tenant_id
            
        existing = await db.services.find_one(query)
        if not existing:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Prepare update
        update_data = {k: v for k, v in update.dict(exclude_unset=True).items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_data["updated_at"] = datetime.utcnow()
        
        # Update service
        await db.services.update_one(
            {"_id": ObjectId(service_id)},
            {"$set": update_data}
        )
        
        # Retrieve updated service
        updated_service = await db.services.find_one({"_id": ObjectId(service_id)})
        updated_service["id"] = str(updated_service["_id"])
        if "_id" in updated_service:
            del updated_service["_id"]
        
        logger.info(f"✏️ Service updated: {service_id}")
        
        return ServiceResponse(**updated_service)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating service: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update service")


@router.delete("/{service_id}", status_code=204)
async def delete_service(
    service_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a service (soft delete by marking as inactive)"""
    try:
        db = get_database()
        
        if not ObjectId.is_valid(service_id):
            raise HTTPException(status_code=400, detail="Invalid service ID")
        
        # Mark as inactive instead of deleting
        # Mark as inactive instead of deleting (verify tenant)
        tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
        query = {"_id": ObjectId(service_id)}
        if tenant_id:
            query["tenant_id"] = tenant_id
            
        result = await db.services.update_one(
            query,
            {"$set": {"active": False, "updated_at": datetime.utcnow()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Service not found")
        
        logger.info(f"❌ Service deactivated: {service_id}")
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting service: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete service")
