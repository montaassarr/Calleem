"""
Appointment Service
Decoupled business logic for appointment management (API & AI Agent)
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from bson import ObjectId

from database.mongo_config import get_database
from models.appointments.appointments import AppointmentStatus
from utils.datetime_utils import datetime_utils
from services.whatsapp_cloud import whatsapp_cloud
from utils.config import settings
from utils.text_formatter import text_formatter

logger = logging.getLogger(__name__)

class AppointmentsService:
    @staticmethod
    async def check_availability(
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
            db = get_database()
            
            # Parse datetime
            if date and time:
                # Handle time with or without seconds
                time_clean = time if ":" in time else f"{time}:00"
                if len(time_clean.split(":")) == 2:
                    time_clean = f"{time_clean}:00"
                datetime_str = f"{date}T{time_clean}"
                try:
                    requested_datetime = datetime.fromisoformat(datetime_str)
                except ValueError:
                    # Fallback for some formats
                    try:
                        requested_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
                    except:
                         return {"available": False, "reason": "Invalid date/time format"}
            else:
                return {"available": False, "reason": "Date and time are required"}
            
            # Simple validation - not in past
            now = datetime.now()
            if requested_datetime < now:
                return {"available": False, "reason": "Cannot book in the past"}
            
            # Check Business Hours (Logic moved from router)
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
            end_datetime = requested_datetime + timedelta(minutes=duration_minutes)
            
            query = {
                "tenant_id": tenant_id,
                "status": {"$in": ["confirmed", "pending", "CONFIRMED", "PENDING"]},
                "$or": [
                    {"datetime": {"$gte": requested_datetime, "$lt": end_datetime}},
                    {"start_time": {"$gte": requested_datetime, "$lt": end_datetime}},
                     # Overlap logic: Existing starts before requested end AND Existing ends after requested start
                    {
                        "$and": [
                            {"start_time": {"$lt": end_datetime}},
                            {"end_time": {"$gt": requested_datetime}}
                        ]
                    }
                ]
            }
            
            overlapping = await db.appointments.count_documents(query)
            is_available = overlapping == 0
            
            return {
                "available": is_available,
                "slot_available": is_available, # Alias for n8n compatibility
                "requested_datetime": requested_datetime.isoformat(),
                "date": date,
                "time": time,
                "reason": "Available" if is_available else "Time slot is already booked"
            }
            
        except Exception as e:
            logger.error(f"Service availability check error: {e}")
            return {"available": False, "reason": f"Error checking availability: {str(e)}"}

    @staticmethod
    async def book_appointment(
        tenant_id: str,
        customer_name: str,
        customer_email: str,
        date: str,
        time: str,
        customer_phone: str = "",
        service: str = "Appointment",
        notes: str = "",
        duration_minutes: int = 30,
        source: str = "voice_agent"
    ) -> Dict[str, Any]:
        """
        Book an appointment.
        """
        try:
            db = get_database()
            
            if not customer_name:
                return {"success": False, "message": "Customer name is required"}
            if not date or not time:
                return {"success": False, "message": "Date and time are required"}
            
            # Parse datetime
            try:
                 # Handle time with or without seconds
                time_clean = time if ":" in time else f"{time}:00"
                if len(time_clean.split(":")) == 2:
                    time_clean = f"{time_clean}:00"
                start_time = datetime.fromisoformat(f"{date}T{time_clean}")
            except Exception as e:
                logger.error(f"Date parsing error: {e}")
                return {"success": False, "message": "Invalid date/time format"}
            
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            # Create appointment
            appointment_dict = {
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
                "source": source,
                "notes": notes,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await db.appointments.insert_one(appointment_dict)
            appointment_id = str(result.inserted_id)
            
            # Send WhatsApp Confirmation
            if customer_phone:
                try:
                    confirmation_msg = f"✅ Hi {customer_name}, your appointment for {service} is confirmed for {text_formatter.format_datetime_display(start_time)}."
                    whatsapp_cloud.send_text_message(customer_phone, confirmation_msg)
                except Exception as e:
                    logger.warning(f"Failed to send WhatsApp confirmation: {e}")

            logger.info(f"✅ Service booked appointment: {appointment_id}")
            
            # Serialize details for JSON response
            details_serialized = appointment_dict.copy()
            for k, v in details_serialized.items():
                if isinstance(v, datetime):
                    details_serialized[k] = v.isoformat()
                elif isinstance(v, ObjectId):
                    details_serialized[k] = str(v)

            return {
                "success": True,
                "message": f"Appointment booked for {customer_name} on {date} at {time}",
                "appointment_id": appointment_id,
                "details": details_serialized
            }
            
        except Exception as e:
            logger.error(f"Service booking error: {e}")
            return {"success": False, "message": f"Failed to book appointment: {str(e)}"}

    @staticmethod
    async def list_appointments(
        tenant_id: str,
        customer_email: Optional[str] = None,
        date: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        List appointments, optionally filtering by email or date.
        """
        try:
            db = get_database()
            query = {"tenant_id": tenant_id}
            
            if customer_email:
                # Case insensitive email search
                query["client_email"] = {"$regex": f"^{customer_email}$", "$options": "i"}
            
            if date:
                try:
                    date_start = datetime.fromisoformat(f"{date}T00:00:00")
                    date_end = datetime.fromisoformat(f"{date}T23:59:59")
                    query["datetime"] = {"$gte": date_start, "$lte": date_end}
                except:
                    pass
            
            cursor = db.appointments.find(query).sort("datetime", 1).limit(limit)
            appointments = await cursor.to_list(length=limit)
            
            # Serialize
            results = []
            for appt in appointments:
                appt["id"] = str(appt["_id"])
                del appt["_id"]
                results.append(appt)
                
            return results
        except Exception as e:
            logger.error(f"Service list error: {e}")
            return []

    @staticmethod
    async def cancel_appointment_by_email_and_date(
        tenant_id: str,
        customer_email: str,
        date: str
    ) -> Dict[str, Any]:
        """
        Cancel an appointment given email and date (Voice Agent typical flow).
        """
        try:
            db = get_database()
            
            # Find the appointment
            # We look for appointments on that date
            date_start = datetime.fromisoformat(f"{date}T00:00:00")
            date_end = datetime.fromisoformat(f"{date}T23:59:59")
            
            query = {
                "tenant_id": tenant_id,
                "client_email": {"$regex": f"^{customer_email}$", "$options": "i"},
                "datetime": {"$gte": date_start, "$lte": date_end},
                "status": {"$in": ["confirmed", "pending", "CONFIRMED", "PENDING"]}
            }
            
            appointment = await db.appointments.find_one(query)
            
            if not appointment:
                return {"success": False, "message": "No active appointment found for that email and date."}
            
            # Cancel it
            await db.appointments.update_one(
                {"_id": appointment["_id"]},
                {"$set": {"status": AppointmentStatus.CANCELLED, "updated_at": datetime.utcnow()}}
            )
            
            # Notify
            if appointment.get("client_phone"):
                try:
                    whatsapp_cloud.send_text_message(
                        appointment["client_phone"], 
                        f"🚫 Your appointment on {date} has been cancelled as requested."
                    )
                except: 
                    pass
            
            return {"success": True, "message": "Appointment cancelled successfully."}

        except Exception as e:
            logger.error(f"Service cancel error: {e}")
            return {"success": False, "message": f"Error cancelling appointment: {str(e)}"}
