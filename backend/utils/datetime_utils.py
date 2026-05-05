"""
DateTime Utility Functions
"""

from datetime import datetime, timedelta, time
from typing import Optional, List, Tuple
import pytz
from dateparser import parse as dateparse
from utils.config import settings


class DateTimeUtils:
    """
    Utilities for date and time handling
    """
    
    @staticmethod
    def get_timezone():
        """Get business timezone"""
        return pytz.timezone(settings.TIMEZONE)
    
    @staticmethod
    def now() -> datetime:
        """Get current time in business timezone"""
        tz = DateTimeUtils.get_timezone()
        return datetime.now(tz)
    
    @staticmethod
    def parse_date_natural(text: str, reference_date: Optional[datetime] = None) -> Optional[datetime]:
        """
        Parse natural language date expressions
        
        Args:
            text: Text like "tomorrow", "next monday", "nov 14"
            reference_date: Reference date (defaults to now)
            
        Returns:
            Parsed datetime or None
        """
        if not reference_date:
            reference_date = DateTimeUtils.now()
        
        text = text.lower().strip()
        
        # Today
        if text in ["today", "now"]:
            return reference_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Tomorrow
        if text in ["tomorrow", "tmr", "tmrw"]:
            return (reference_date + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Day after tomorrow
        if text in ["day after tomorrow", "overmorrow"]:
            return (reference_date + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Days of week
        weekdays = {
            "monday": 0, "mon": 0,
            "tuesday": 1, "tue": 1, "tues": 1,
            "wednesday": 2, "wed": 2,
            "thursday": 3, "thu": 3, "thur": 3, "thurs": 3,
            "friday": 4, "fri": 4,
            "saturday": 5, "sat": 5,
            "sunday": 6, "sun": 6
        }
        
        for day_name, day_num in weekdays.items():
            if day_name in text:
                days_ahead = day_num - reference_date.weekday()
                if days_ahead <= 0:  # Target day already passed this week
                    days_ahead += 7
                if "next" in text:
                    days_ahead += 7
                return (reference_date + timedelta(days=days_ahead)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Next week
        if "next week" in text:
            return (reference_date + timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # This weekend
        if "weekend" in text:
            days_ahead = 5 - reference_date.weekday()  # Saturday
            if days_ahead < 0:
                days_ahead += 7
            return (reference_date + timedelta(days=days_ahead)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        return None
    
    @staticmethod
    def parse_time_natural(text: str) -> Optional[time]:
        """
        Parse natural language time expressions
        
        Args:
            text: Text like "3pm", "3:30pm", "noon", "midnight"
            
        Returns:
            Time object or None
        """
        import re
        
        text = text.lower().strip()
        
        # Special cases
        if text in ["noon", "12pm", "12:00pm"]:
            return time(12, 0)
        if text in ["midnight", "12am", "12:00am"]:
            return time(0, 0)
        
        # Match patterns like "3pm", "3:30pm", "15:30"
        patterns = [
            r'(\d{1,2}):(\d{2})\s*(am|pm)?',
            r'(\d{1,2})\s*(am|pm)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2)) if len(match.groups()) > 2 and match.group(2) else 0
                meridiem = match.group(len(match.groups()))
                
                # Convert to 24-hour format
                if meridiem:
                    if meridiem == 'pm' and hour != 12:
                        hour += 12
                    elif meridiem == 'am' and hour == 12:
                        hour = 0
                
                if 0 <= hour < 24 and 0 <= minute < 60:
                    return time(hour, minute)
        
        return None

    @staticmethod
    def parse_datetime_expression(
        date_text: Optional[str],
        time_text: Optional[str] = None,
        reference_date: Optional[datetime] = None
    ) -> Optional[datetime]:
        """
        Parse combined natural language date/time expressions
        """
        if not date_text and not time_text:
            return None

        reference = reference_date or DateTimeUtils.now()
        expression_parts = []

        if date_text:
            expression_parts.append(str(date_text))
        if time_text:
            expression_parts.append(str(time_text))

        expression = " ".join(expression_parts).strip()

        if expression:
            parsed = dateparse(
                expression,
                settings={
                    "TIMEZONE": settings.TIMEZONE,
                    "RETURN_AS_TIMEZONE_AWARE": True,
                    "PREFER_DATES_FROM": "future",
                    "RELATIVE_BASE": reference
                }
            )
            if parsed:
                return parsed

        # Fallback to existing helpers
        date_obj = None
        time_obj = None

        if date_text:
            date_obj = DateTimeUtils.parse_date_natural(date_text, reference)
        if time_text:
            time_obj = DateTimeUtils.parse_time_natural(time_text)

        if not date_obj:
            date_obj = reference

        if date_obj and time_obj:
            return DateTimeUtils.combine_date_time(date_obj, time_obj)

        return date_obj
    
    @staticmethod
    def combine_date_time(
        date_obj: datetime,
        time_obj: time,
        timezone: Optional[pytz.timezone] = None
    ) -> datetime:
        """
        Combine date and time objects
        
        Args:
            date_obj: Date
            time_obj: Time
            timezone: Timezone to use
            
        Returns:
            Combined datetime
        """
        if not timezone:
            timezone = DateTimeUtils.get_timezone()
        
        combined = datetime.combine(date_obj.date(), time_obj)
        return timezone.localize(combined)
    
    @staticmethod
    def is_business_hours(dt: datetime) -> bool:
        """
        Check if datetime falls within business hours
        
        Args:
            dt: Datetime to check
            
        Returns:
            True if within business hours
        """
        # Convert to local timezone before extracting time
        tz = DateTimeUtils.get_timezone()
        dt_local = dt.astimezone(tz) if dt.tzinfo else tz.localize(dt)
        
        # Check day of week (0 = Monday, 6 = Sunday)
        if dt_local.weekday() == 6:  # Sunday
            return False
        
        # Check time
        business_start = time(9, 0)
        business_end = time(20, 0)
        
        return business_start <= dt_local.time() <= business_end
    
    @staticmethod
    def get_available_slots(
        date: datetime,
        duration_minutes: int = 30,
        booked_slots: List[datetime] = None
    ) -> List[datetime]:
        """
        Get available time slots for a given date
        
        Args:
            date: Date to check
            duration_minutes: Appointment duration
            booked_slots: List of already booked datetimes
            
        Returns:
            List of available datetime slots
        """
        if booked_slots is None:
            booked_slots = []
        
        available = []
        
        # Business hours: 9 AM - 8 PM
        current_slot = datetime.combine(date.date(), time(9, 0))
        end_time = datetime.combine(date.date(), time(20, 0))
        
        tz = DateTimeUtils.get_timezone()
        current_slot = tz.localize(current_slot)
        end_time = tz.localize(end_time)
        
        while current_slot < end_time:
            # Check if slot is not booked
            is_booked = any(
                abs((slot - current_slot).total_seconds()) < duration_minutes * 60
                for slot in booked_slots
            )
            
            if not is_booked:
                available.append(current_slot)
            
            current_slot += timedelta(minutes=duration_minutes)
        
        return available
    
    @staticmethod
    def format_duration(minutes: int) -> str:
        """
        Format duration in minutes to readable string
        
        Args:
            minutes: Duration in minutes
            
        Returns:
            Formatted string like "1 hour 30 minutes" or "30 minutes"
        """
        if minutes < 60:
            return f"{minutes} minutes"
        
        hours = minutes // 60
        remaining_minutes = minutes % 60
        
        if remaining_minutes == 0:
            return f"{hours} {'hour' if hours == 1 else 'hours'}"
        
        return f"{hours} {'hour' if hours == 1 else 'hours'} {remaining_minutes} minutes"
    
    @staticmethod
    def get_reminder_time(appointment_time: datetime, hours_before: int = 24) -> datetime:
        """
        Calculate reminder time before appointment
        
        Args:
            appointment_time: Appointment datetime
            hours_before: Hours before appointment to send reminder
            
        Returns:
            Reminder datetime
        """
        return appointment_time - timedelta(hours=hours_before)
    
    @staticmethod
    def is_valid_appointment_time(dt: datetime) -> Tuple[bool, Optional[str]]:
        """
        Validate if datetime is valid for appointment
        
        Args:
            dt: Datetime to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        now = DateTimeUtils.now()
        
        # Ensure both datetimes are timezone-aware for comparison
        if dt.tzinfo is None:
            # Localize naive datetime to configured timezone
            tz = pytz.timezone(settings.TIMEZONE)
            dt = tz.localize(dt)
        
        # Can't book in the past (allow 5-minute buffer)
        if dt < now - timedelta(minutes=5):
            return False, "Cannot book appointments in the past"
        
        # Can't book too far in advance (3 months)
        max_advance = now + timedelta(days=90)
        if dt > max_advance:
            return False, "Cannot book more than 3 months in advance"
        
        # Business hours enforcement is done at the service layer per tenant config.
        # is_valid_appointment_time only validates timing constraints, not hours.
        
        return True, None


# Singleton instance
datetime_utils = DateTimeUtils()
