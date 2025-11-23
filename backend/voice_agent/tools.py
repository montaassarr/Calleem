"""
Vapi-compatible tool definitions for voice agent
These tools allow the voice AI to interact with the appointment system
Using NORMALIZED MongoDB schemas for consistency with WhatsApp agent
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import logging

from database.mongo_config import get_database
from models.normalized_schemas import (
    AppointmentNormalized,
    ServiceNormalized,
    AvailabilityNormalized,
    ConversationHistoryNormalized
)
from utils.datetime_utils import datetime_utils
from utils.text_formatter import text_formatter

logger = logging.getLogger(__name__)


class VoiceTools:
    """Voice agent tool definitions in Vapi format"""
    
    @staticmethod
    def get_tool_definitions() -> List[Dict[str, Any]]:
        """Return all available tools in Vapi format"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "check_availability",
                    "description": "Check available time slots for appointments. Use this when a customer asks about availability or wants to know open times.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {
                                "type": "string",
                                "description": "The date to check availability for in YYYY-MM-DD format"
                            },
                            "service_name": {
                                "type": "string",
                                "description": "Optional service name to check availability for specific service duration"
                            }
                        },
                        "required": ["date"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "book_appointment",
                    "description": "Book a new appointment for a customer. Use this after confirming all required details with the customer.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "client_name": {
                                "type": "string",
                                "description": "Full name of the client"
                            },
                            "client_phone": {
                                "type": "string",
                                "description": "Phone number of the client in E.164 format"
                            },
                            "service_name": {
                                "type": "string",
                                "description": "Name of the service requested"
                            },
                            "appointment_date": {
                                "type": "string",
                                "description": "Date of appointment in YYYY-MM-DD format"
                            },
                            "appointment_time": {
                                "type": "string",
                                "description": "Time of appointment in HH:MM format (24-hour)"
                            },
                            "notes": {
                                "type": "string",
                                "description": "Optional notes or special requests"
                            }
                        },
                        "required": ["client_name", "client_phone", "service_name", "appointment_date", "appointment_time"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_services",
                    "description": "Get list of all available services with prices and durations. Use this when customer asks about services offered.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_appointment",
                    "description": "Update an existing appointment (reschedule or modify details). Use this when a customer wants to change their appointment.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "client_phone": {
                                "type": "string",
                                "description": "Phone number of the client"
                            },
                            "new_date": {
                                "type": "string",
                                "description": "New date in YYYY-MM-DD format"
                            },
                            "new_time": {
                                "type": "string",
                                "description": "New time in HH:MM format"
                            }
                        },
                        "required": ["client_phone"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "cancel_appointment",
                    "description": "Cancel an existing appointment. Use this when customer wants to cancel their booking.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "client_phone": {
                                "type": "string",
                                "description": "Phone number of the client"
                            },
                            "appointment_date": {
                                "type": "string",
                                "description": "Optional: date of appointment to cancel in YYYY-MM-DD format"
                            }
                        },
                        "required": ["client_phone"]
                    }
                }
            }
        ]
    
    @staticmethod
    async def execute_tool(
        tool_name: str,
        parameters: Dict[str, Any],
        business_id: str = "default"
    ) -> Dict[str, Any]:
        """Execute a tool and return the result"""
        
        try:
            if tool_name == "check_availability":
                return await VoiceTools._check_availability(parameters, business_id)
            elif tool_name == "book_appointment":
                return await VoiceTools._book_appointment(parameters, business_id)
            elif tool_name == "get_services":
                return await VoiceTools._get_services(business_id)
            elif tool_name == "update_appointment":
                return await VoiceTools._update_appointment(parameters, business_id)
            elif tool_name == "cancel_appointment":
                return await VoiceTools._cancel_appointment(parameters, business_id)
            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }
        except Exception as e:
            logger.error(f"Tool execution failed for {tool_name}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def _check_availability(params: Dict[str, Any], business_id: str) -> Dict[str, Any]:
        """Check available time slots using NORMALIZED schema"""
        db = get_database()
        if db is None:
            return {"success": False, "error": "Database unavailable"}
        
        try:
            date_str = params.get("date")
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            day_of_week = target_date.weekday()
            
            # Get availability from NORMALIZED availability collection
            availability = await db.availability.find_one({
                "businessId": business_id,
                "dayOfWeek": day_of_week
            })
            
            if not availability or not availability.get("isOpen"):
                return {
                    "success": True,
                    "available_slots": [],
                    "message": "The business is closed on this day"
                }
            
            # Get existing appointments for that day using NORMALIZED schema
            start_of_day = datetime.combine(target_date, datetime.min.time())
            end_of_day = datetime.combine(target_date, datetime.max.time())
            
            appointments = await db.appointments.find({
                "businessId": business_id,
                "start": {
                    "$gte": start_of_day,
                    "$lt": end_of_day
                },
                "status": {"$in": ["pending", "confirmed"]}
            }).to_list(length=100)
            
            # Extract booked time slots
            booked_slots = []
            for apt in appointments:
                start_time = apt["start"]
                end_time = apt["end"]
                # Mark all 30-minute slots as booked during this appointment
                current = start_time
                while current < end_time:
                    booked_slots.append(current.strftime("%H:%M"))
                    current += timedelta(minutes=30)
            
            # Generate available slots using NORMALIZED fields
            open_time = availability.get("open", "09:00")
            close_time = availability.get("close", "17:00")
            breaks = availability.get("breaks", [])
            
            available_slots = []
            current_time = datetime.strptime(open_time, "%H:%M")
            end_time = datetime.strptime(close_time, "%H:%M")
            
            while current_time < end_time:
                time_str = current_time.strftime("%H:%M")
                
                # Check if time is during a break
                is_break = False
                for break_period in breaks:
                    break_start = datetime.strptime(break_period.get("start", ""), "%H:%M").time()
                    break_end = datetime.strptime(break_period.get("end", ""), "%H:%M").time()
                    if break_start <= current_time.time() < break_end:
                        is_break = True
                        break
                
                # Add slot if not booked and not during break
                if time_str not in booked_slots and not is_break:
                    available_slots.append(time_str)
                
                current_time += timedelta(minutes=30)
            
            return {
                "success": True,
                "date": date_str,
                "available_slots": available_slots[:10],
                "total_available": len(available_slots)
            }
            
        except Exception as e:
            logger.error(f"Availability check failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def _book_appointment(params: Dict[str, Any], business_id: str) -> Dict[str, Any]:
        """Book an appointment using NORMALIZED schema"""
        db = get_database()
        if db is None:
            return {"success": False, "error": "Database unavailable"}
        
        try:
            # Parse appointment start time
            start_time = datetime.strptime(
                f"{params['appointment_date']} {params['appointment_time']}",
                "%Y-%m-%d %H:%M"
            )
            
            # Get service duration from services collection (NORMALIZED)
            service = await db.services.find_one({
                "businessId": business_id,
                "name": params["service_name"]
            })
            
            duration_minutes = service.get("durationMinutes", 30) if service else 30
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            # Clean phone number
            phone = text_formatter.clean_phone_number(params["client_phone"])
            
            # Create appointment using NORMALIZED schema
            appointment_data = {
                "businessId": business_id,
                "name": params["client_name"],
                "phone": phone,
                "service": params["service_name"],
                "start": start_time,
                "end": end_time,
                "notes": params.get("notes", ""),
                "source": "voice",
                "status": "confirmed",
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
            
            result = await db.appointments.insert_one(appointment_data)
            
            # Log to conversation_history with NORMALIZED schema
            await db.conversation_history.insert_one({
                "businessId": business_id,
                "type": "voice",
                "sender": "agent",
                "message": f"Booked {params['service_name']} for {params['client_name']}",
                "timestamp": datetime.utcnow(),
                "metadata": {
                    "phone": phone,
                    "service": params["service_name"],
                    "appointmentId": str(result.inserted_id)
                }
            })
            
            return {
                "success": True,
                "appointment_id": str(result.inserted_id),
                "message": f"Appointment booked for {params['client_name']} on {params['appointment_date']} at {params['appointment_time']}",
                "details": {
                    "name": params["client_name"],
                    "service": params["service_name"],
                    "date": params["appointment_date"],
                    "time": params["appointment_time"],
                    "duration": duration_minutes
                }
            }
            
        except Exception as e:
            logger.error(f"Appointment booking failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def _get_services(business_id: str) -> Dict[str, Any]:
        """Get available services using NORMALIZED schema"""
        db = get_database()
        if db is None:
            return {"success": False, "error": "Database unavailable"}
        
        try:
            # Query services collection directly with NORMALIZED schema
            services = await db.services.find({
                "businessId": business_id,
                "isActive": True
            }).to_list(length=100)
            
            service_list = []
            for service in services:
                service_list.append({
                    "name": service.get("name"),
                    "duration": service.get("durationMinutes", 30),
                    "price": service.get("price", 0)
                })
            
            return {
                "success": True,
                "services": service_list,
                "count": len(service_list)
            }
            
        except Exception as e:
            logger.error(f"Get services failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def _update_appointment(params: Dict[str, Any], business_id: str) -> Dict[str, Any]:
        """Update appointment using NORMALIZED schema"""
        db = get_database()
        if db is None:
            return {"success": False, "error": "Database unavailable"}
        
        try:
            # Clean phone number for search
            phone = text_formatter.clean_phone_number(params["client_phone"])
            
            # Find most recent appointment using NORMALIZED fields
            appointment = await db.appointments.find_one({
                "businessId": business_id,
                "phone": phone,
                "status": {"$in": ["pending", "confirmed"]},
                "start": {"$gte": datetime.utcnow()}
            }, sort=[("start", 1)])
            
            if not appointment:
                return {"success": False, "error": "No upcoming appointment found for this phone number"}
            
            update_data = {}
            
            if "new_date" in params and "new_time" in params:
                new_start = datetime.strptime(
                    f"{params['new_date']} {params['new_time']}",
                    "%Y-%m-%d %H:%M"
                )
                
                # Calculate new end time based on original duration
                original_duration = (appointment["end"] - appointment["start"]).total_seconds() / 60
                new_end = new_start + timedelta(minutes=original_duration)
                
                update_data["start"] = new_start
                update_data["end"] = new_end
                update_data["updatedAt"] = datetime.utcnow()
            
            if update_data:
                await db.appointments.update_one(
                    {"_id": appointment["_id"]},
                    {"$set": update_data}
                )
                
                # Log to conversation_history
                await db.conversation_history.insert_one({
                    "businessId": business_id,
                    "type": "voice",
                    "sender": "agent",
                    "message": f"Updated appointment to {params['new_date']} at {params['new_time']}",
                    "timestamp": datetime.utcnow(),
                    "metadata": {
                        "phone": phone,
                        "appointmentId": str(appointment["_id"])
                    }
                })
                
                return {
                    "success": True,
                    "message": "Appointment updated successfully",
                    "new_time": update_data.get("start").strftime("%Y-%m-%d %H:%M") if "start" in update_data else None
                }
            
            return {"success": False, "error": "No update parameters provided"}
            
        except Exception as e:
            logger.error(f"Appointment update failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def _cancel_appointment(params: Dict[str, Any], business_id: str) -> Dict[str, Any]:
        """Cancel appointment using NORMALIZED schema"""
        db = get_database()
        if db is None:
            return {"success": False, "error": "Database unavailable"}
        
        try:
            # Clean phone number for search
            phone = text_formatter.clean_phone_number(params["client_phone"])
            
            # Build query using NORMALIZED fields
            query = {
                "businessId": business_id,
                "phone": phone,
                "status": {"$in": ["pending", "confirmed"]},
                "start": {"$gte": datetime.utcnow()}
            }
            
            if "appointment_date" in params:
                target_date = datetime.strptime(params["appointment_date"], "%Y-%m-%d").date()
                start_of_day = datetime.combine(target_date, datetime.min.time())
                end_of_day = datetime.combine(target_date, datetime.max.time())
                query["start"] = {"$gte": start_of_day, "$lt": end_of_day}
            
            appointment = await db.appointments.find_one(query, sort=[("start", 1)])
            
            if not appointment:
                return {"success": False, "error": "No upcoming appointment found"}
            
            # Cancel appointment
            await db.appointments.update_one(
                {"_id": appointment["_id"]},
                {"$set": {
                    "status": "cancelled",
                    "updatedAt": datetime.utcnow()
                }}
            )
            
            # Log to conversation_history
            await db.conversation_history.insert_one({
                "businessId": business_id,
                "type": "voice",
                "sender": "agent",
                "message": f"Cancelled appointment for {appointment['start'].strftime('%Y-%m-%d %H:%M')}",
                "timestamp": datetime.utcnow(),
                "metadata": {
                    "phone": phone,
                    "appointmentId": str(appointment["_id"])
                }
            })
            
            return {
                "success": True,
                "message": f"Appointment cancelled for {appointment['start'].strftime('%Y-%m-%d %H:%M')}"
            }
            
        except Exception as e:
            logger.error(f"Appointment cancellation failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}


# Export singleton instance
voice_tools = VoiceTools()
