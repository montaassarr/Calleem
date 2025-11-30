"""
Appointments API Router
CRUD operations for appointments
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
import logging

from models.appointments.appointments import (
    Appointment, 
    AppointmentCreate, 
    AppointmentUpdate, 
    AppointmentResponse, 
    AppointmentStatus
)
from database.mongo_config import get_database
from utils.datetime_utils import datetime_utils
from utils.text_formatter import text_formatter
from services.whatsapp_cloud import whatsapp_cloud
from services.whatsapp_cloud import whatsapp_cloud
from utils.config import settings
from routers.users import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=AppointmentResponse, status_code=201)
async def create_appointment(
    appointment: AppointmentCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new appointment"""
    try:
        db = get_database()
        
        # Get tenant_id from current user
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            tenant_id = current_user.get("business_id")
        
        # Handle both datetime formats
        if appointment.datetime and appointment.duration_minutes:
            # Option 1: datetime + duration_minutes
            start_time = appointment.datetime
            end_time = start_time + timedelta(minutes=appointment.duration_minutes)
        elif appointment.start_time and appointment.end_time:
            # Option 2: explicit start_time and end_time
            start_time = appointment.start_time
            end_time = appointment.end_time
        else:
            raise HTTPException(
                status_code=400,
                detail="Must provide either (datetime + duration_minutes) OR (start_time + end_time)"
            )
        
        # Validate appointment time
        is_valid, error_msg = datetime_utils.is_valid_appointment_time(start_time)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Get client name and phone (handle both field names)
        client_name = appointment.client_name or appointment.customer_name
        client_phone = appointment.client_phone or appointment.customer_phone
        
        # Prepare appointment document
        appointment_dict = {
            "client_name": client_name,
            "client_phone": client_phone,
            "service": appointment.service or "Service",
            "start_time": start_time,
            "end_time": end_time,
            "datetime": start_time,  # Frontend compatibility
            "duration_minutes": int((end_time - start_time).total_seconds() / 60),  # Frontend compatibility
            "tenant_id": tenant_id,
            "business_id": tenant_id,
            "status": AppointmentStatus.CONFIRMED,
            "source": "api",
            "notes": appointment.notes,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        if appointment.service_id:
            appointment_dict["service_id"] = appointment.service_id
        
        # Insert into database
        result = await db.appointments.insert_one(appointment_dict)
        
        # Retrieve created appointment
        created_appointment = await db.appointments.find_one({"_id": result.inserted_id})
        created_appointment["id"] = str(created_appointment["_id"])
        created_appointment["_id"] = str(created_appointment["_id"])  # Convert ObjectId to string for Pydantic
        
        logger.info(f"✅ Appointment created: {created_appointment['id']}")

        
        # Send confirmation via WhatsApp
        try:
            confirmation_msg = f"""✅ Appointment Confirmed!

{client_name}, your appointment is confirmed for:
📅 {text_formatter.format_datetime_display(start_time)}
⏱️ Duration: {int((end_time - start_time).total_seconds() / 60)} minutes

Looking forward to seeing you! - {settings.BUSINESS_NAME}"""
            
            whatsapp_cloud.send_text_message(client_phone, confirmation_msg)
        except Exception as e:
            logger.warning(f"Failed to send WhatsApp confirmation: {e}")
        
        return AppointmentResponse(**created_appointment)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating appointment: {e}", exc_info=True)
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
    try:
        db = get_database()
        
        # Build query filter
        query = {}
        
        # Filter by tenant_id
        tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
        if tenant_id:
            query["tenant_id"] = tenant_id
        
        if status:
            query["status"] = status
        
        if date_from or date_to:
            query["datetime"] = {}
            if date_from:
                query["datetime"]["$gte"] = date_from
            if date_to:
                query["datetime"]["$lte"] = date_to
        
        if client_phone:
            query["client_phone"] = text_formatter.clean_phone_number(client_phone)
        
        # Fetch appointments
        cursor = db.appointments.find(query).sort("datetime", 1).skip(skip).limit(limit)
        appointments = await cursor.to_list(length=limit)
        
        # Format response
        for appointment in appointments:
            appointment["id"] = str(appointment["_id"])
            appointment["_id"] = str(appointment["_id"])  # Convert ObjectId to string
            
            # Ensure datetime and duration_minutes are present for frontend
            if "start_time" in appointment and "end_time" in appointment:
                appointment["datetime"] = appointment["start_time"]
                appointment["duration_minutes"] = int((appointment["end_time"] - appointment["start_time"]).total_seconds() / 60)
        
        logger.info(f"Retrieved {len(appointments)} appointments")
        
        return [AppointmentResponse(**apt) for apt in appointments]
        
    except Exception as e:
        logger.error(f"Error listing appointments: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve appointments")


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific appointment by ID"""
    try:
        db = get_database()
        
        # Validate ObjectId
        if not ObjectId.is_valid(appointment_id):
            raise HTTPException(status_code=400, detail="Invalid appointment ID")
        
        # Filter by tenant_id
        tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
        query = {"_id": ObjectId(appointment_id)}
        if tenant_id:
            query["tenant_id"] = tenant_id
            
        appointment = await db.appointments.find_one(query)
        
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        appointment["id"] = str(appointment["_id"])
        appointment["_id"] = str(appointment["_id"])  # Convert ObjectId to string
        
        # Ensure datetime and duration_minutes are present
        if "start_time" in appointment and "end_time" in appointment:
            appointment["datetime"] = appointment["start_time"]
            appointment["duration_minutes"] = int((appointment["end_time"] - appointment["start_time"]).total_seconds() / 60)
        
        return AppointmentResponse(**appointment)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting appointment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve appointment")


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: str, 
    update: AppointmentUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an appointment"""
    try:
        db = get_database()
        
        # Validate ObjectId
        if not ObjectId.is_valid(appointment_id):
            raise HTTPException(status_code=400, detail="Invalid appointment ID")
        
        # Check if appointment exists
        # Check if appointment exists and belongs to tenant
        tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
        query = {"_id": ObjectId(appointment_id)}
        if tenant_id:
            query["tenant_id"] = tenant_id
            
        existing = await db.appointments.find_one(query)
        if not existing:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Prepare update data
        update_data = {k: v for k, v in update.dict(exclude_unset=True).items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Validate new datetime if provided
        if "datetime" in update_data or "duration_minutes" in update_data:
            # Get start_time (new or existing)
            start_time = update_data.get("datetime", existing.get("start_time"))
            
            # Get duration (new or existing)
            duration = update_data.get("duration_minutes")
            if duration is None:
                # Calculate from existing
                old_start = existing.get("start_time")
                old_end = existing.get("end_time")
                if old_start and old_end:
                    duration = int((old_end - old_start).total_seconds() / 60)
                else:
                    duration = 30 # Default
            
            # Calculate new end_time
            end_time = start_time + timedelta(minutes=duration)
            
            # Validate time
            is_valid, error_msg = datetime_utils.is_valid_appointment_time(start_time)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error_msg)
                
            update_data["start_time"] = start_time
            update_data["end_time"] = end_time
            update_data["datetime"] = start_time
            update_data["duration_minutes"] = duration
        
        update_data["updated_at"] = datetime.utcnow()
        
        # Update appointment
        await db.appointments.update_one(
            {"_id": ObjectId(appointment_id)},
            {"$set": update_data}
        )
        
        # Retrieve updated appointment
        updated_appointment = await db.appointments.find_one({"_id": ObjectId(appointment_id)})
        updated_appointment["id"] = str(updated_appointment["_id"])
        updated_appointment["_id"] = str(updated_appointment["_id"])  # Convert ObjectId to string
        
        # Ensure datetime and duration_minutes are present
        if "start_time" in updated_appointment and "end_time" in updated_appointment:
            updated_appointment["datetime"] = updated_appointment["start_time"]
            updated_appointment["duration_minutes"] = int((updated_appointment["end_time"] - updated_appointment["start_time"]).total_seconds() / 60)
        
        logger.info(f"✏️ Appointment updated: {appointment_id}")
        
        return AppointmentResponse(**updated_appointment)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating appointment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update appointment")


@router.delete("/{appointment_id}", status_code=204)
async def delete_appointment(
    appointment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Permanently delete an appointment from database"""
    try:
        db = get_database()
        
        # Validate ObjectId
        if not ObjectId.is_valid(appointment_id):
            raise HTTPException(status_code=400, detail="Invalid appointment ID")
        
        # Get appointment before deletion (for logging)
        # Filter by tenant_id
        tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
        query = {"_id": ObjectId(appointment_id)}
        if tenant_id:
            query["tenant_id"] = tenant_id
            
        appointment = await db.appointments.find_one(query)
        
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # PERMANENTLY DELETE from database
        result = await db.appointments.delete_one({"_id": ObjectId(appointment_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        logger.info(f"🗑️ Appointment permanently deleted: {appointment_id}")
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting appointment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete appointment")


@router.post("/{appointment_id}/cancel", response_model=AppointmentResponse)
async def cancel_appointment(
    appointment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Cancel an appointment (updates status to cancelled)"""
    try:
        db = get_database()
        
        # Validate ObjectId
        if not ObjectId.is_valid(appointment_id):
            raise HTTPException(status_code=400, detail="Invalid appointment ID")
        
        # Get appointment before cancellation
        # Filter by tenant_id
        tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
        query = {"_id": ObjectId(appointment_id)}
        if tenant_id:
            query["tenant_id"] = tenant_id
            
        appointment = await db.appointments.find_one(query)
        
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Update status to cancelled
        await db.appointments.update_one(
            {"_id": ObjectId(appointment_id)},
            {
                "$set": {
                    "status": AppointmentStatus.CANCELLED,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Retrieve updated appointment
        cancelled_appointment = await db.appointments.find_one({"_id": ObjectId(appointment_id)})
        cancelled_appointment["id"] = str(cancelled_appointment["_id"])
        cancelled_appointment["_id"] = str(cancelled_appointment["_id"])  # Convert ObjectId to string
        
        # Ensure datetime and duration_minutes are present
        if "start_time" in cancelled_appointment and "end_time" in cancelled_appointment:
            cancelled_appointment["datetime"] = cancelled_appointment["start_time"]
            cancelled_appointment["duration_minutes"] = int((cancelled_appointment["end_time"] - cancelled_appointment["start_time"]).total_seconds() / 60)
        
        logger.info(f"❌ Appointment cancelled: {appointment_id}")
        
        # Send cancellation notification via WhatsApp
        cancellation_msg = f"""🚫 Appointment Cancelled

Your appointment on {text_formatter.format_datetime_display(appointment['datetime'])} has been cancelled.

Feel free to rebook anytime! - {settings.BUSINESS_NAME}"""
        
        whatsapp_cloud.send_text_message(appointment["client_phone"], cancellation_msg)
        
        return AppointmentResponse(**cancelled_appointment)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling appointment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to cancel appointment")


@router.get("/availability/check")
async def check_availability(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    time: Optional[str] = Query(None, description="Time in HH:MM format"),
    duration_minutes: int = Query(30, ge=15, le=240, description="Duration in minutes"),
    current_user: dict = Depends(get_current_user)
):
    """Check if a time slot is available"""
    try:
        db = get_database()
        
        # Parse datetime
        if date and time:
            datetime_str = f"{date}T{time}:00"
            requested_datetime = datetime.fromisoformat(datetime_str)
        else:
            raise HTTPException(status_code=400, detail="Both date and time are required")
        
        # Validate it's not in the past
        is_valid, error_msg = datetime_utils.is_valid_appointment_time(requested_datetime)
        if not is_valid:
            return {
                "available": False,
                "reason": error_msg,
                "requested_datetime": requested_datetime.isoformat()
            }
            
        # Filter by tenant_id
        tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
        
        # Check Business Hours
        if tenant_id:
            config = await db.business_config.find_one({"business_id": tenant_id})
            if config and "business_hours" in config:
                day_name = requested_datetime.strftime("%A").lower()
                day_config = config["business_hours"].get(day_name)
                
                if not day_config or not day_config.get("enabled", True):
                    return {
                        "available": False,
                        "reason": f"Business is closed on {day_name.capitalize()}",
                        "requested_datetime": requested_datetime.isoformat()
                    }
                
                start_str = day_config.get("start", "09:00")
                end_str = day_config.get("end", "17:00")
                
                req_time_str = requested_datetime.strftime("%H:%M")
                
                if req_time_str < start_str or req_time_str >= end_str:
                     return {
                        "available": False,
                        "reason": f"Time is outside business hours ({start_str} - {end_str})",
                        "requested_datetime": requested_datetime.isoformat()
                    }
        
        # Check for overlapping appointments
        end_datetime = requested_datetime.replace(
            minute=requested_datetime.minute + duration_minutes
        )
        
        # Filter by tenant_id
        tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
        query = {
            "status": {"$in": [AppointmentStatus.CONFIRMED, AppointmentStatus.PENDING]},
            "$or": [
                # Existing appointment starts during requested slot
                {
                    "datetime": {
                        "$gte": requested_datetime,
                        "$lt": end_datetime
                    }
                },
                # Existing appointment ends during requested slot
                {
                    "$expr": {
                        "$and": [
                            {"$lte": ["$datetime", requested_datetime]},
                            {
                                "$gte": [
                                    {"$add": ["$datetime", {"$multiply": ["$duration_minutes", 60000]}]},
                                    requested_datetime
                                ]
                            }
                        ]
                    }
                }
            ]
        }
        
        if tenant_id:
            query["tenant_id"] = tenant_id
            
        overlapping = await db.appointments.count_documents(query)
        
        is_available = overlapping == 0
        
        return {
            "available": is_available,
            "requested_datetime": requested_datetime.isoformat(),
            "duration_minutes": duration_minutes,
            "reason": "Time slot is available" if is_available else "Time slot is already booked"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking availability: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to check availability")


@router.get("/stats/summary")
async def get_appointment_stats(current_user: dict = Depends(get_current_user)):
    """Get appointment statistics"""
    try:
        db = get_database()
        
        # Filter by tenant_id
        tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
        match_stage = {}
        if tenant_id:
            match_stage["tenant_id"] = tenant_id
            
        # Count by status
        pipeline = [
            {"$match": match_stage},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        
        status_counts = {}
        async for result in db.appointments.aggregate(pipeline):
            status_counts[result["_id"]] = result["count"]
        
        # Total appointments
        total = await db.appointments.count_documents(match_stage)
        
        # Upcoming appointments
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
        logger.error(f"Error getting stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")
