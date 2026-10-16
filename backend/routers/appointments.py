"""
Appointments API Router
CRUD operations for appointments
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Request
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import hmac

from models.appointment import (
    AppointmentCreate, 
    AppointmentUpdate, 
    AppointmentResponse, 
    AppointmentStatus
)
from routers.users import get_current_user
from services.appointments_service import AppointmentsService
from utils.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Instantiate service
appointments_service = AppointmentsService()

# ============================================================================
# INTERNAL ENDPOINTS (Called by automations/webhooks, not directly by agent)
# These require X-Tenant-ID header for multi-tenant isolation
# ============================================================================

def get_tenant_from_header(request: Request) -> str:
    """Extract tenant_id from X-Tenant-ID header for internal calls"""
    tenant_id = request.headers.get("X-Tenant-ID")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID header required")
    return tenant_id


def verify_internal_agent_auth(request: Request) -> None:
    """Require static bearer token for internal agent endpoints."""
    expected = settings.AGENT_INTERNAL_TOKEN
    if not expected:
        logger.error("AGENT_INTERNAL_TOKEN not configured for internal agent endpoints")
        raise HTTPException(status_code=503, detail="Internal agent auth not configured")

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer authorization")

    provided = auth_header[len("Bearer "):].strip()
    if not hmac.compare_digest(provided, expected):
        raise HTTPException(status_code=401, detail="Invalid internal agent token")


@router.get("/agent/availability")
async def agent_check_availability(
    request: Request,
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    time: Optional[str] = Query(None, description="Time in HH:MM format"),
    duration_minutes: int = Query(30, ge=15, le=240),
):
    """Agent-accessible availability check (internal token required)."""
    try:
        verify_internal_agent_auth(request)
        tenant_id = get_tenant_from_header(request)
        
        result = await appointments_service.check_availability(
            tenant_id=tenant_id,
            date=date,
            time=time,
            duration_minutes=duration_minutes
        )
        return result
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Agent availability check error: {e}")
        return {"available": False, "reason": "Availability check failed"}


@router.post("/agent/book")
async def agent_book_appointment(
    request: Request,
    data: dict,
):
    """Agent-accessible booking endpoint (internal token required)."""
    try:
        verify_internal_agent_auth(request)
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
        if isinstance(e, HTTPException):
            raise e
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


@router.get("/stats/overview")
async def get_dashboard_overview(current_user: dict = Depends(get_current_user)):
    """
    Dashboard numbers: revenue booked this month (appointments x service price) against last month,
    and bookings per day / week / month. Cancelled and no-show appointments don't count.
    """
    from database.mongo_config import get_database
    import pytz

    db = get_database()
    tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
    tz = await appointments_service._resolve_tenant_timezone(tenant_id)
    now = datetime.now(tz)
    today = tz.localize(datetime(now.year, now.month, now.day))

    def month_start(year: int, month: int) -> datetime:
        """First day of a month; month may run past 12 or below 1."""
        year, month = year + (month - 1) // 12, (month - 1) % 12 + 1
        return tz.localize(datetime(year, month, 1))

    this_month, next_month = month_start(now.year, now.month), month_start(now.year, now.month + 1)
    last_month = month_start(now.year, now.month - 1)
    months = [month_start(now.year, now.month - i) for i in range(5, -1, -1)]  # last 6, oldest first
    since = min(months[0], today - timedelta(days=27))

    services = await db.services.find({"tenant_id": tenant_id}, {"name": 1, "price": 1}).to_list(500)
    price_by_id = {str(s["_id"]): s.get("price") or 0 for s in services}
    price_by_name = {(s.get("name") or "").strip().lower(): s.get("price") or 0 for s in services}
    config = await db.business_config.find_one({"tenant_id": tenant_id}, {"currency": 1}) or {}

    appointments = await db.appointments.find(
        {
            "tenant_id": tenant_id,
            "datetime": {"$gte": since, "$lt": next_month},
            "status": {"$nin": [AppointmentStatus.CANCELLED.value, AppointmentStatus.NO_SHOW.value]},
        },
        {"datetime": 1, "service": 1, "service_id": 1},
    ).to_list(20000)

    revenue = {"this_month": 0.0, "last_month": 0.0}
    unpriced = 0
    days = [0] * 7   # last 7 days, today last
    weeks = [0] * 4  # last 4 weeks of 7 days, this week last
    per_month = [0] * len(months)
    for apt in appointments:
        when = apt["datetime"]
        when = (pytz.utc.localize(when) if when.tzinfo is None else when).astimezone(tz)
        price = price_by_id.get(str(apt.get("service_id"))) or price_by_name.get((apt.get("service") or "").strip().lower())
        if this_month <= when < next_month:
            revenue["this_month"] += price or 0
            unpriced += 0 if price else 1
        elif last_month <= when < this_month:
            revenue["last_month"] += price or 0
        if when < today + timedelta(days=1):
            age_days = (today - tz.localize(datetime(when.year, when.month, when.day))).days
            if 0 <= age_days < 7:
                days[6 - age_days] += 1
            if 0 <= age_days < 28:
                weeks[3 - age_days // 7] += 1
        for i in range(len(months) - 1, -1, -1):
            if when >= months[i]:
                per_month[i] += 1
                break

    change = None
    if revenue["last_month"] > 0:
        change = round((revenue["this_month"] - revenue["last_month"]) / revenue["last_month"] * 100)

    return {
        "currency": config.get("currency") or "USD",
        "revenue": {
            "this_month": round(revenue["this_month"], 2),
            "last_month": round(revenue["last_month"], 2),
            "change_pct": change,
            "unpriced_appointments": unpriced,
        },
        "bookings": {
            "7days": [
                {"label": (today - timedelta(days=6 - i)).strftime("%a")[0], "count": days[i]} for i in range(7)
            ],
            "1month": [{"label": f"W{i + 1}", "count": weeks[i]} for i in range(4)],
            "all": [{"label": m.strftime("%b"), "count": per_month[i]} for i, m in enumerate(months)],
        },
    }


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
