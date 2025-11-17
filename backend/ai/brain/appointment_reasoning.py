"""
Appointment Reasoning Engine
Validates availability, prevents double-booking, handles complex scheduling logic
"""

import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import pytz
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class AppointmentSlot(BaseModel):
    """Represents an available appointment slot"""
    datetime: datetime
    duration_minutes: int = 30
    available: bool = True
    reason: Optional[str] = None


class BookingRequest(BaseModel):
    """Structured booking request with validation"""
    client_name: str = Field(..., min_length=2)
    client_phone: str
    client_email: Optional[str] = None
    service: str
    requested_datetime: datetime
    duration_minutes: int = 30
    barber_preference: Optional[str] = None
    notes: Optional[str] = None


class BookingResult(BaseModel):
    """Result of booking attempt"""
    success: bool
    appointment_id: Optional[str] = None
    message: str
    suggested_alternatives: List[datetime] = Field(default_factory=list)


class AppointmentReasoner:
    """
    Advanced appointment scheduling logic with reasoning
    """
    
    def __init__(self):
        self.buffer_minutes = 15  # Buffer between appointments
    
    async def validate_booking_request(
        self,
        db: AsyncIOMotorDatabase,
        config: Dict[str, Any],
        booking: BookingRequest
    ) -> Tuple[bool, str]:
        """
        Validate a booking request against business rules
        
        Args:
            db: MongoDB database
            config: Business configuration
            booking: Booking request to validate
            
        Returns:
            (is_valid, error_message)
        """
        # 1. Check if datetime is in the past
        tz = pytz.timezone(config.get("timezone", "America/New_York"))
        now = datetime.now(tz)
        requested_time = booking.requested_datetime
        
        # Make timezone-aware if naive
        if requested_time.tzinfo is None:
            requested_time = tz.localize(requested_time)
        
        if requested_time < now:
            return False, "Cannot book appointments in the past. Please choose a future date and time."
        
        # 2. Check if within business hours
        is_open, open_msg = self._is_within_business_hours(
            requested_time,
            config.get("opening_hours", [])
        )
        if not is_open:
            return False, open_msg
        
        # 3. Check if slot is available (no conflicts)
        is_available, conflict_msg = await self._check_slot_availability(
            db,
            requested_time,
            booking.duration_minutes
        )
        if not is_available:
            return False, conflict_msg
        
        # 4. Check service exists
        service_valid, service_msg = self._validate_service(
            booking.service,
            config.get("services", [])
        )
        if not service_valid:
            return False, service_msg
        
        # All validations passed
        return True, "Booking request is valid"
    
    async def find_available_slots(
        self,
        db: AsyncIOMotorDatabase,
        config: Dict[str, Any],
        date: datetime,
        duration_minutes: int = 30,
        max_slots: int = 5
    ) -> List[AppointmentSlot]:
        """
        Find available appointment slots for a given date
        
        Args:
            db: MongoDB database
            config: Business configuration
            date: Target date
            duration_minutes: Required duration
            max_slots: Maximum slots to return
            
        Returns:
            List of available AppointmentSlot objects
        """
        tz = pytz.timezone(config.get("timezone", "America/New_York"))
        
        # Get business hours for this day
        day_name = date.strftime("%A").lower()
        opening_hours = config.get("opening_hours", [])
        
        day_hours = None
        for hours in opening_hours:
            if hours.get("day", "").lower() == day_name:
                day_hours = hours
                break
        
        if not day_hours or day_hours.get("closed", False):
            return []
        
        # Parse opening and closing times
        open_time_str = day_hours.get("open", "09:00")
        close_time_str = day_hours.get("close", "17:00")
        
        open_hour, open_min = map(int, open_time_str.split(":"))
        close_hour, close_min = map(int, close_time_str.split(":"))
        
        # Create datetime objects for open and close
        start_time = date.replace(hour=open_hour, minute=open_min, second=0, microsecond=0)
        end_time = date.replace(hour=close_hour, minute=close_min, second=0, microsecond=0)
        
        # Make timezone-aware
        if start_time.tzinfo is None:
            start_time = tz.localize(start_time)
            end_time = tz.localize(end_time)
        
        # Get existing appointments for this day
        day_start = start_time.replace(hour=0, minute=0, second=0)
        day_end = day_start + timedelta(days=1)
        
        existing_appointments = await db.appointments.find({
            "datetime": {"$gte": day_start, "$lt": day_end},
            "status": {"$in": ["confirmed", "pending"]}
        }).to_list(length=100)
        
        # Generate potential slots
        available_slots = []
        current_time = start_time
        slot_interval = timedelta(minutes=30)  # Check every 30 minutes
        
        while current_time + timedelta(minutes=duration_minutes) <= end_time:
            # Check if this slot conflicts with existing appointments
            is_free = True
            for apt in existing_appointments:
                apt_start = apt.get("datetime")
                apt_duration = apt.get("duration_minutes", 30)
                apt_end = apt_start + timedelta(minutes=apt_duration + self.buffer_minutes)
                
                slot_end = current_time + timedelta(minutes=duration_minutes + self.buffer_minutes)
                
                # Check for overlap
                if not (current_time >= apt_end or slot_end <= apt_start):
                    is_free = False
                    break
            
            if is_free:
                available_slots.append(AppointmentSlot(
                    datetime=current_time,
                    duration_minutes=duration_minutes,
                    available=True
                ))
                
                if len(available_slots) >= max_slots:
                    break
            
            current_time += slot_interval
        
        return available_slots
    
    async def suggest_alternatives(
        self,
        db: AsyncIOMotorDatabase,
        config: Dict[str, Any],
        requested_datetime: datetime,
        duration_minutes: int = 30,
        days_ahead: int = 7
    ) -> List[datetime]:
        """
        Suggest alternative time slots when requested slot is unavailable
        
        Args:
            db: MongoDB database
            config: Business configuration
            requested_datetime: Originally requested datetime
            duration_minutes: Appointment duration
            days_ahead: How many days ahead to search
            
        Returns:
            List of alternative datetime slots
        """
        alternatives = []
        tz = pytz.timezone(config.get("timezone", "America/New_York"))
        
        # Start with the requested date
        current_date = requested_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
        
        for day_offset in range(days_ahead):
            check_date = current_date + timedelta(days=day_offset)
            
            slots = await self.find_available_slots(
                db,
                config,
                check_date,
                duration_minutes,
                max_slots=3
            )
            
            for slot in slots:
                alternatives.append(slot.datetime)
                
                if len(alternatives) >= 5:
                    return alternatives
        
        return alternatives
    
    def _is_within_business_hours(
        self,
        requested_time: datetime,
        opening_hours: List[Dict[str, Any]]
    ) -> Tuple[bool, str]:
        """
        Check if requested time is within business operating hours
        
        Returns:
            (is_open, message)
        """
        day_name = requested_time.strftime("%A").lower()
        
        # Find hours for this day
        day_hours = None
        for hours in opening_hours:
            if hours.get("day", "").lower() == day_name:
                day_hours = hours
                break
        
        if not day_hours:
            return False, f"We're not open on {day_name.capitalize()}s. Please choose another day."
        
        if day_hours.get("closed", False):
            return False, f"We're closed on {day_name.capitalize()}s. Please choose another day."
        
        # Parse opening and closing times
        open_time_str = day_hours.get("open", "09:00")
        close_time_str = day_hours.get("close", "17:00")
        
        open_hour, open_min = map(int, open_time_str.split(":"))
        close_hour, close_min = map(int, close_time_str.split(":"))
        
        request_hour = requested_time.hour
        request_min = requested_time.minute
        
        # Convert to minutes for easy comparison
        open_minutes = open_hour * 60 + open_min
        close_minutes = close_hour * 60 + close_min
        request_minutes = request_hour * 60 + request_min
        
        if request_minutes < open_minutes:
            return False, f"We open at {open_time_str}. Please choose a time after opening."
        
        if request_minutes >= close_minutes:
            return False, f"We close at {close_time_str}. Please choose an earlier time."
        
        return True, "Within business hours"
    
    async def _check_slot_availability(
        self,
        db: AsyncIOMotorDatabase,
        requested_time: datetime,
        duration_minutes: int
    ) -> Tuple[bool, str]:
        """
        Check if time slot is available (no conflicts)
        
        Returns:
            (is_available, message)
        """
        # Define the time range for this appointment
        appointment_start = requested_time
        appointment_end = requested_time + timedelta(minutes=duration_minutes + self.buffer_minutes)
        
        # Query for conflicting appointments
        conflicts = await db.appointments.find({
            "status": {"$in": ["confirmed", "pending"]},
            "$or": [
                # Existing appointment starts during requested slot
                {
                    "datetime": {
                        "$gte": appointment_start,
                        "$lt": appointment_end
                    }
                },
                # Existing appointment ends during requested slot
                {
                    "$expr": {
                        "$and": [
                            {"$lte": ["$datetime", requested_time]},
                            {
                                "$gt": [
                                    {"$add": ["$datetime", {"$multiply": ["$duration_minutes", 60000]}]},
                                    appointment_start
                                ]
                            }
                        ]
                    }
                }
            ]
        }).to_list(length=10)
        
        if conflicts:
            conflict_time = conflicts[0].get("datetime")
            return False, f"That time slot is already booked. The nearest appointment is at {conflict_time.strftime('%I:%M %p')}."
        
        return True, "Slot is available"
    
    def _validate_service(
        self,
        service_name: str,
        available_services: List[Dict[str, Any]]
    ) -> Tuple[bool, str]:
        """
        Validate that service exists and is active
        
        Returns:
            (is_valid, message)
        """
        service_name_lower = service_name.lower()
        
        for service in available_services:
            if service.get("name", "").lower() == service_name_lower:
                if service.get("active", True):
                    return True, "Service is valid"
                else:
                    return False, f"{service_name} is currently unavailable. Please choose another service."
        
        # Service not found
        available_names = [s.get("name") for s in available_services if s.get("active", True)]
        return False, f"Service '{service_name}' not found. Available services: {', '.join(available_names)}"


# Singleton instance
appointment_reasoner = AppointmentReasoner()
