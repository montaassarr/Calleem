"""
Appointments API Router
CRUD operations for appointments
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import logging

from models.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentStatus
)
from database.mongo_config import get_database
from utils.datetime_utils import datetime_utils
from utils.text_formatter import text_formatter
from utils.twilio_handler import twilio_handler

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=AppointmentResponse, status_code=201)
async def create_appointment(appointment: AppointmentCreate):
    """Create a new appointment"""
    try:
        db = get_database()
        
        # Validate appointment time
        is_valid, error_msg = datetime_utils.is_valid_appointment_time(appointment.datetime)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Prepare appointment document
        appointment_dict = appointment.dict()
        appointment_dict["status"] = AppointmentStatus.CONFIRMED
        appointment_dict["created_at"] = datetime.utcnow()
        appointment_dict["updated_at"] = datetime.utcnow()
        
        # Insert into database
        result = await db.appointments.insert_one(appointment_dict)
        
        # Retrieve created appointment
        created_appointment = await db.appointments.find_one({"_id": result.inserted_id})
        created_appointment["id"] = str(created_appointment["_id"])
        
        logger.info(f"✅ Appointment created: {created_appointment['id']}")
        
        # Send confirmation SMS
        appointment_details = {
            "client_name": appointment.client_name,
            "service": appointment.service,
            "datetime_formatted": text_formatter.format_datetime_display(appointment.datetime),
            "duration_minutes": appointment.duration_minutes
        }
        
        twilio_handler.send_appointment_confirmation(
            appointment.client_phone,
            appointment_details
        )
        
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
    limit: int = Query(100, ge=1, le=500)
):
    """List appointments with optional filters"""
    try:
        db = get_database()
        
        # Build query filter
        query = {}
        
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
        
        logger.info(f"Retrieved {len(appointments)} appointments")
        
        return [AppointmentResponse(**apt) for apt in appointments]
        
    except Exception as e:
        logger.error(f"Error listing appointments: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve appointments")


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(appointment_id: str):
    """Get a specific appointment by ID"""
    try:
        db = get_database()
        
        # Validate ObjectId
        if not ObjectId.is_valid(appointment_id):
            raise HTTPException(status_code=400, detail="Invalid appointment ID")
        
        appointment = await db.appointments.find_one({"_id": ObjectId(appointment_id)})
        
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        appointment["id"] = str(appointment["_id"])
        
        return AppointmentResponse(**appointment)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting appointment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve appointment")


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(appointment_id: str, update: AppointmentUpdate):
    """Update an appointment"""
    try:
        db = get_database()
        
        # Validate ObjectId
        if not ObjectId.is_valid(appointment_id):
            raise HTTPException(status_code=400, detail="Invalid appointment ID")
        
        # Check if appointment exists
        existing = await db.appointments.find_one({"_id": ObjectId(appointment_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Prepare update data
        update_data = {k: v for k, v in update.dict(exclude_unset=True).items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Validate new datetime if provided
        if "datetime" in update_data:
            is_valid, error_msg = datetime_utils.is_valid_appointment_time(update_data["datetime"])
            if not is_valid:
                raise HTTPException(status_code=400, detail=error_msg)
        
        update_data["updated_at"] = datetime.utcnow()
        
        # Update appointment
        await db.appointments.update_one(
            {"_id": ObjectId(appointment_id)},
            {"$set": update_data}
        )
        
        # Retrieve updated appointment
        updated_appointment = await db.appointments.find_one({"_id": ObjectId(appointment_id)})
        updated_appointment["id"] = str(updated_appointment["_id"])
        
        logger.info(f"✏️ Appointment updated: {appointment_id}")
        
        return AppointmentResponse(**updated_appointment)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating appointment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update appointment")


@router.delete("/{appointment_id}", status_code=204)
async def delete_appointment(appointment_id: str):
    """Delete/Cancel an appointment"""
    try:
        db = get_database()
        
        # Validate ObjectId
        if not ObjectId.is_valid(appointment_id):
            raise HTTPException(status_code=400, detail="Invalid appointment ID")
        
        # Get appointment before deletion
        appointment = await db.appointments.find_one({"_id": ObjectId(appointment_id)})
        
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Mark as cancelled instead of deleting
        await db.appointments.update_one(
            {"_id": ObjectId(appointment_id)},
            {
                "$set": {
                    "status": AppointmentStatus.CANCELLED,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"❌ Appointment cancelled: {appointment_id}")
        
        # Send cancellation notification
        cancellation_msg = f"""Your appointment at {appointment['datetime'].strftime('%b %d at %-I:%M %p')} has been cancelled. 
        
Feel free to rebook anytime! - {appointment.get('business_name', 'Royal Fade Barbershop')}"""
        
        twilio_handler.send_sms(appointment["client_phone"], cancellation_msg)
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting appointment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete appointment")


@router.get("/stats/summary")
async def get_appointment_stats():
    """Get appointment statistics"""
    try:
        db = get_database()
        
        # Count by status
        pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        
        status_counts = {}
        async for result in db.appointments.aggregate(pipeline):
            status_counts[result["_id"]] = result["count"]
        
        # Total appointments
        total = await db.appointments.count_documents({})
        
        # Upcoming appointments
        upcoming = await db.appointments.count_documents({
            "datetime": {"$gte": datetime.utcnow()},
            "status": AppointmentStatus.CONFIRMED
        })
        
        return {
            "total": total,
            "upcoming": upcoming,
            "by_status": status_counts
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")
