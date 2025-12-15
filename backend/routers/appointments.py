"""
Appointments API Router
CRUD operations for appointments
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Request
from typing import List, Optional
from datetime import datetime
import logging

from models.appointment import (
    AppointmentCreate, 
    AppointmentUpdate, 
    AppointmentResponse, 
    AppointmentStatus
)
from routers.users import get_current_user
from services.appointments_service import AppointmentsService

logger = logging.getLogger(__name__)

router = APIRouter()

# Instantiate service
appointments_service = AppointmentsService()

# ============================================================================
# INTERNAL ENDPOINTS (Called by n8n workflows, not directly by agent)
# These require X-Tenant-ID header for multi-tenant isolation
# ============================================================================

def get_tenant_from_header(request: Request) -> str:
    """Extract tenant_id from X-Tenant-ID header for n8n/internal calls"""
    tenant_id = request.headers.get("X-Tenant-ID")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID header required")
    return tenant_id


@router.get("/agent/availability")
async def agent_check_availability(
    request: Request,
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    time: Optional[str] = Query(None, description="Time in HH:MM format"),
    duration_minutes: int = Query(30, ge=15, le=240),
):
    """Agent-accessible availability check (no JWT required)"""
    try:
        tenant_id = get_tenant_from_header(request)
        
        result = await appointments_service.check_availability(
            tenant_id=tenant_id,
            date=date,
            time=time,
            duration_minutes=duration_minutes
        )
        return result
        
    except Exception as e:
        logger.error(f"Agent availability check error: {e}")
        return {"available": True, "reason": "Slot appears available"}


@router.post("/agent/book")
async def agent_book_appointment(
    request: Request,
    data: dict,
):
    """Agent-accessible booking endpoint (no JWT required)"""
    try:
        tenant_id = get_tenant_from_header(request)
        
        # Extract details
        customer_name = data.get("customer_name") or data.get("name")
        customer_phone = data.get("customer_phone") or data.get("phone", "")
        customer_email = data.get("customer_email") or data.get("email", "")
        date_str = data.get("date")
        time_str = data.get("time")
        service = data.get("service", "Appointment")
        notes = data.get("notes", "")
        duration = data.get("duration_minutes", 30)

        # Use legacy/agent specific method wrapper in service
        result = await appointments_service.book_appointment_agent_legacy(
            tenant_id=tenant_id,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            date=date_str,
            time=time_str,
            service=service,
            notes=notes,
            duration_minutes=duration
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Agent booking error: {e}")
        return {"success": False, "message": "Failed to book appointment"}

# ============================================================================
# AUTHENTICATED ENDPOINTS (JWT required)
# ============================================================================

@router.post("/", response_model=AppointmentResponse, status_code=201)
async def create_appointment(
    appointment: AppointmentCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new appointment"""
    tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
    try:
        result = await appointments_service.create_appointment(tenant_id, appointment)
        return AppointmentResponse(**result)
    except Exception as e:
        # Re-raise HTTPExceptions from service
        if isinstance(e, HTTPException): raise e
        logger.error(f"Error creating appointment: {e}")
        raise HTTPException(status_code=500, detail="Failed to create appointment")


@router.get("/", response_model=List[AppointmentResponse])
async def list_appointments(
    status: Optional[AppointmentStatus] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    client_phone: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: dict = Depends(get_current_user)
):
    """List appointments with optional filters"""
    tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
    try:
        result = await appointments_service.list_appointments(
            tenant_id=tenant_id,
            skip=skip,
            limit=limit,
            status=status,
            date_from=date_from,
            date_to=date_to,
            client_phone=client_phone
        )
        return [AppointmentResponse(**apt) for apt in result]
    except Exception as e:
        logger.error(f"Error listing appointments: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve appointments")


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific appointment by ID"""
    tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
    try:
        result = await appointments_service.get_appointment(appointment_id, tenant_id)
        return AppointmentResponse(**result)
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        logger.error(f"Error getting appointment: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve appointment")


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: str, 
    update: AppointmentUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an appointment"""
    tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
    try:
        result = await appointments_service.update_appointment(appointment_id, tenant_id, update)
        return AppointmentResponse(**result)
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        logger.error(f"Error updating appointment: {e}")
        raise HTTPException(status_code=500, detail="Failed to update appointment")


@router.delete("/{appointment_id}", status_code=204)
async def delete_appointment(
    appointment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Permanently delete an appointment"""
    tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
    try:
        await appointments_service.delete_appointment(appointment_id, tenant_id)
        return None
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        logger.error(f"Error deleting appointment: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete appointment")


@router.post("/{appointment_id}/cancel", response_model=AppointmentResponse)
async def cancel_appointment(
    appointment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Cancel an appointment"""
    tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
    try:
        result = await appointments_service.cancel_appointment(appointment_id, tenant_id)
        return AppointmentResponse(**result)
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        logger.error(f"Error cancelling appointment: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel appointment")


@router.get("/availability/check")
async def check_availability(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    time: Optional[str] = Query(None, description="Time in HH:MM format"),
    duration_minutes: int = Query(30, ge=15, le=240, description="Duration in minutes"),
    current_user: dict = Depends(get_current_user)
):
    """Check if a time slot is available"""
    tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
    result = await appointments_service.check_availability(
        tenant_id=tenant_id,
        date=date,
        time=time,
        duration_minutes=duration_minutes
    )
    return result


@router.get("/stats/summary")
async def get_appointment_stats(current_user: dict = Depends(get_current_user)):
    """Get appointment statistics"""
    # Note: Stats logic not yet moved to service to keep this concise, 
    # but could be moved to AppointmentsService.get_stats(tenant_id)
    # Maintaining simplified version here for now
    from database.mongo_config import get_database
    try:
        db = get_database()
        tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
        match_stage = {}
        if tenant_id:
            match_stage["tenant_id"] = tenant_id
            
        pipeline = [
            {"$match": match_stage},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        
        status_counts = {}
        async for result in db.appointments.aggregate(pipeline):
            status_counts[result["_id"]] = result["count"]
        
        total = await db.appointments.count_documents(match_stage)
        
        upcoming_query = match_stage.copy()
        upcoming_query.update({
            "datetime": {"$gte": datetime.utcnow()},
            "status": AppointmentStatus.CONFIRMED
        })
        upcoming = await db.appointments.count_documents(upcoming_query)
        
        return {
            "total": total,
            "upcoming": upcoming,
            "by_status": status_counts
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")
