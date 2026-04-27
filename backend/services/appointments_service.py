"""
Appointment Service
Decoupled business logic for appointment management (API & AI Agent)
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any, Tuple
from bson import ObjectId
from fastapi import HTTPException
import pytz

from database.mongo_config import get_database
from models.appointment import AppointmentStatus, AppointmentCreate, AppointmentUpdate
from utils.datetime_utils import datetime_utils
# from services.whatsapp_cloud import whatsapp_cloud # Disabled as per user request
from utils.config import settings
from utils.text_formatter import text_formatter

logger = logging.getLogger(__name__)

class AppointmentsService:
    def __init__(self):
        pass

    @property
    def db(self):
        return get_database()

    async def _resolve_tenant_timezone(self, tenant_id: str) -> pytz.BaseTzInfo:
        """Resolve tenant timezone from business config, then tenant profile."""
        timezone_name = settings.TIMEZONE

        if tenant_id:
            config = await self.db.business_config.find_one({"tenant_id": tenant_id})
            timezone_name = (config or {}).get("timezone") or timezone_name

            if not (config or {}).get("timezone"):
                tenant = None
                try:
                    if ObjectId.is_valid(tenant_id):
                        tenant = await self.db.tenants.find_one({"_id": ObjectId(tenant_id)})
                except Exception:
                    tenant = None
                if tenant is None:
                    tenant = await self.db.tenants.find_one({"_id": tenant_id}) or await self.db.tenants.find_one({"_id": str(tenant_id)})
                timezone_name = (tenant or {}).get("timezone") or timezone_name

        try:
            return pytz.timezone(timezone_name)
        except Exception:
            logger.warning(f"Invalid timezone '{timezone_name}' for tenant {tenant_id}, using {settings.TIMEZONE}")
            return pytz.timezone(settings.TIMEZONE)

    async def check_availability(
        self,
        tenant_id: str,
        date: str,
        time: str,
        duration_minutes: int = 30
    ) -> Dict[str, Any]:
        """
        Check if a time slot is available for a given tenant.
        Used by both API and AI Agent.
        """
        try:
            # Parse datetime
            if date and time:
                tenant_tz = await self._resolve_tenant_timezone(tenant_id)
                # Handle time with or without seconds
                time_clean = time if ":" in time else f"{time}:00"
                if len(time_clean.split(":")) == 2:
                    time_clean = f"{time_clean}:00"
                datetime_str = f"{date}T{time_clean}"
                try:
                    requested_datetime = datetime.fromisoformat(datetime_str)
                    # Interpret naive datetime in tenant timezone (business local time).
                    if requested_datetime.tzinfo is None:
                        requested_datetime = tenant_tz.localize(requested_datetime)
                except ValueError:
                    # Fallback for some formats
                    try:
                        requested_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
                        requested_datetime = tenant_tz.localize(requested_datetime)
                    except:
                         return {"available": False, "reason": "Invalid date/time format"}
            else:
                return {"available": False, "reason": "Date and time are required"}
            
            # Simple validation - not in past
            # now = datetime.now() # Allow checking availability slightly in past/present
            
            # Check Business Hours (Logic moved from router)
            config = await self.db.business_config.find_one({"business_id": tenant_id})
            # Fallback
            if not config:
                 config = await self.db.business_config.find_one({"tenant_id": tenant_id})

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
            end_datetime = requested_datetime + timedelta(minutes=duration_minutes)
            
            query = {
                "tenant_id": tenant_id,
                "status": {"$in": [AppointmentStatus.CONFIRMED, AppointmentStatus.PENDING, "confirmed", "pending"]},
                "$or": [
                    {"datetime": {"$gte": requested_datetime, "$lt": end_datetime}},
                    {"start_time": {"$gte": requested_datetime, "$lt": end_datetime}},
                    {
                        "$and": [
                            {"start_time": {"$lt": end_datetime}},
                            {"end_time": {"$gt": requested_datetime}}
                        ]
                    }
                ]
            }
            
            overlapping = await self.db.appointments.count_documents(query)
            is_available = overlapping == 0
            
            return {
                "available": is_available,
                "slot_available": is_available, # Alias for API compatibility
                "requested_datetime": requested_datetime.isoformat(),
                "date": date,
                "time": time,
                "reason": "Available" if is_available else "Time slot is already booked"
            }
            
        except Exception as e:
            logger.error(f"Service availability check error: {e}")
            return {"available": False, "reason": f"Error checking availability: {str(e)}"}

    async def create_appointment(
        self, 
        tenant_id: str, 
        appointment: AppointmentCreate
    ) -> Dict[str, Any]:
        """Create a new appointment"""
        
        # Calculate start/end times
        if appointment.datetime and appointment.duration_minutes:
            start_time = appointment.datetime
            end_time = start_time + timedelta(minutes=appointment.duration_minutes)
        elif appointment.start_time and appointment.end_time:
            start_time = appointment.start_time
            end_time = appointment.end_time
        else:
             raise HTTPException(
                status_code=400, 
                detail="Must provide either (datetime + duration_minutes) OR (start_time + end_time)"
            )

        # Validate time
        is_valid, error_msg = datetime_utils.is_valid_appointment_time(start_time)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        # Basic fields
        client_name = appointment.client_name or appointment.customer_name
        client_phone = appointment.client_phone or appointment.customer_phone

        if not client_name or not client_phone:
            raise HTTPException(status_code=400, detail="Client name and phone are required")

        # Prepare document
        doc = {
            "client_name": client_name,
            "client_phone": client_phone,
            "service": appointment.service or "Service",
            "start_time": start_time,
            "end_time": end_time,
            "datetime": start_time,
            "duration_minutes": int((end_time - start_time).total_seconds() / 60),
            "tenant_id": tenant_id,
            "business_id": tenant_id, # Legacy
            "status": AppointmentStatus.CONFIRMED,
            "source": "api",
            "notes": appointment.notes,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        if appointment.service_id:
            doc["service_id"] = appointment.service_id

        # Insert
        result = await self.db.appointments.insert_one(doc)
        
        # Retrieve and return
        created = await self.db.appointments.find_one({"_id": result.inserted_id})
        created["id"] = str(created["_id"])
        created["_id"] = str(created["_id"])
        
        logger.info(f"✅ Appointment created: {created['id']}")
        
        return created

    async def list_appointments(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        client_phone: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        
        query = {}
        if tenant_id:
            query["tenant_id"] = tenant_id
        if status:
            query["status"] = status
        
        if date_from or date_to:
            query["datetime"] = {}
            if date_from: query["datetime"]["$gte"] = date_from
            if date_to: query["datetime"]["$lte"] = date_to
            
        if client_phone:
             query["client_phone"] = {"$regex": client_phone, "$options": "i"}

        cursor = self.db.appointments.find(query).sort("datetime", 1).skip(skip).limit(limit)
        appointments = await cursor.to_list(length=limit)

        # Format
        results = []
        for apt in appointments:
            apt["id"] = str(apt["_id"])
            apt["_id"] = str(apt["_id"])
            # Ensure fields exist
            if "start_time" in apt and "end_time" in apt:
                apt["datetime"] = apt["start_time"]
                apt["duration_minutes"] = int((apt["end_time"] - apt["start_time"]).total_seconds() / 60)
            results.append(apt)
            
        return results

    async def get_appointment(self, appointment_id: str, tenant_id: str) -> Dict[str, Any]:
        if not ObjectId.is_valid(appointment_id):
            raise HTTPException(400, "Invalid ID")
            
        query = {"_id": ObjectId(appointment_id)}
        if tenant_id:
            query["tenant_id"] = tenant_id

        apt = await self.db.appointments.find_one(query)
        if not apt:
            raise HTTPException(404, "Appointment not found")
            
        apt["id"] = str(apt["_id"])
        apt["_id"] = str(apt["_id"])
        if "start_time" in apt and "end_time" in apt:
            apt["datetime"] = apt["start_time"]
            apt["duration_minutes"] = int((apt["end_time"] - apt["start_time"]).total_seconds() / 60)
            
        return apt

    async def update_appointment(
        self, 
        appointment_id: str, 
        tenant_id: str, 
        update: AppointmentUpdate
    ) -> Dict[str, Any]:
        if not ObjectId.is_valid(appointment_id):
            raise HTTPException(400, "Invalid ID")

        # Check existence
        query = {"_id": ObjectId(appointment_id)}
        if tenant_id:
            query["tenant_id"] = tenant_id
            
        existing = await self.db.appointments.find_one(query)
        if not existing:
             raise HTTPException(404, "Appointment not found")

        update_data = {k: v for k,v in update.dict(exclude_unset=True).items() if v is not None}
        if not update_data:
            raise HTTPException(400, "No fields to update")

        # Handle time updates
        if "datetime" in update_data or "duration_minutes" in update_data:
            start_time = update_data.get("datetime", existing.get("start_time"))
            duration = update_data.get("duration_minutes")
            
            if duration is None:
                old_start = existing.get("start_time")
                old_end = existing.get("end_time")
                if old_start and old_end:
                    duration = int((old_end - old_start).total_seconds() / 60)
                else:
                    duration = 30
            
            end_time = start_time + timedelta(minutes=duration)
            
            # Recalculate validity if time changed
            is_valid, error_msg = datetime_utils.is_valid_appointment_time(start_time)
            if not is_valid:
                 raise HTTPException(400, error_msg)
                 
            update_data["start_time"] = start_time
            update_data["end_time"] = end_time
            update_data["datetime"] = start_time
            update_data["duration_minutes"] = duration

        update_data["updated_at"] = datetime.now(timezone.utc)

        await self.db.appointments.update_one(
            {"_id": ObjectId(appointment_id)},
            {"$set": update_data}
        )
        
        # Return updated
        return await self.get_appointment(appointment_id, tenant_id)

    async def delete_appointment(self, appointment_id: str, tenant_id: str):
        if not ObjectId.is_valid(appointment_id):
            raise HTTPException(400, "Invalid ID")
            
        query = {"_id": ObjectId(appointment_id)}
        if tenant_id:
            query["tenant_id"] = tenant_id
            
        result = await self.db.appointments.delete_one(query)
        if result.deleted_count == 0:
            raise HTTPException(404, "Appointment not found")

    async def cancel_appointment(self, appointment_id: str, tenant_id: str) -> Dict[str, Any]:
        if not ObjectId.is_valid(appointment_id):
            raise HTTPException(400, "Invalid ID")
            
        query = {"_id": ObjectId(appointment_id)}
        if tenant_id:
             query["tenant_id"] = tenant_id
             
        # Check exists
        existing = await self.db.appointments.find_one(query)
        if not existing:
            raise HTTPException(404, "Appointment not found")
            
        await self.db.appointments.update_one(
            {"_id": ObjectId(appointment_id)},
            {
                "$set": {
                    "status": AppointmentStatus.CANCELLED,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return await self.get_appointment(appointment_id, tenant_id)

    # Legacy method for Agent compatibility (book_appointment used by Agent router)
    # The signature below matches what is called in routers/appointments.py:93
    async def book_appointment_agent_legacy(
        self,
        tenant_id: str,
        customer_name: str,
        customer_email: str,
        customer_phone: str,
        date: str,
        time: str,
        service: str,
        notes: str,
        duration_minutes: int
    ) -> Dict[str, Any]:
        # Adapt to create_appointment logic or use simplified flow
        try:
             # Parse datetime
            time_clean = time if ":" in time else f"{time}:00"
            if len(time_clean.split(":")) == 2:
                time_clean = f"{time_clean}:00"
            start_time = datetime.fromisoformat(f"{date}T{time_clean}")
            # Interpret naive datetime in tenant local timezone for consistency.
            if start_time.tzinfo is None:
                tenant_tz = await self._resolve_tenant_timezone(tenant_id)
                start_time = tenant_tz.localize(start_time)
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            doc = {
                "client_name": customer_name,
                "client_phone": customer_phone,
                "client_email": customer_email,
                "service": service,
                "start_time": start_time,
                "end_time": end_time,
                "datetime": start_time,
                "duration_minutes": duration_minutes,
                "tenant_id": tenant_id,
                "business_id": tenant_id,
                "status": AppointmentStatus.CONFIRMED,
                "source": "voice_agent",
                "notes": notes,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            res = await self.db.appointments.insert_one(doc)
            return {
                "success": True,
                "message": f"Appointment booked for {customer_name}",
                "appointment_id": str(res.inserted_id)
            }
        except Exception as e:
            logger.error(f"Agent booking error: {e}")
            return {"success": False, "message": str(e)}
