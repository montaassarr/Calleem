from datetime import datetime, timedelta
import logging
from typing import Optional, Dict, Any, List
from database.mongo_config import get_database

logger = logging.getLogger(__name__)

async def check_availability(
    tenant_id: str,
    date: str,
    duration_minutes: int = 30
) -> Dict[str, Any]:
    """
    Check availability for a given date.
    Returns free slots.
    """
    db = get_database()
    
    # Mock Availability Logic
    # In a real app, this would query Google Calendar or existing appointments
    
    # Standard business hours 9am - 5pm
    slots = []
    start_hour = 9
    end_hour = 17
    
    # Parse date
    try:
        check_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD"}

    # Mock: All slots are open except lunch
    now = datetime.utcnow()
    
    for hour in range(start_hour, end_hour):
        time_str = f"{hour:02d}:00"
        
        # Create a mock slot
        slot_start = datetime.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M")
        
        # Simple Logic: Only show slots in future if checking today
        if check_date.date() == now.date() and slot_start.time() <= now.time():
            continue
            
        slots.append(time_str)
        
    return {
        "available": True,
        "date": date,
        "slots": slots
    }

async def book_appointment(
    tenant_id: str,
    date: str,
    time: str,
    customer_name: str,
    customer_phone: str,
    service_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Book an appointment.
    """
    db = get_database()
    
    try:
        start_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        end_datetime = start_datetime + timedelta(minutes=30) # Default 30 mins
    except ValueError:
        return {"error": "Invalid date/time format"}

    appointment = {
        "tenant_id": tenant_id,
        "client_name": customer_name,
        "client_phone": customer_phone,
        "start_time": start_datetime,
        "end_time": end_datetime,
        "datetime": start_datetime, # Frontend compat
        "duration_minutes": 30, # Frontend compat
        "service_id": service_id,
        "status": "confirmed",
        "created_at": datetime.utcnow()
    }
    
    result = await db.appointments.insert_one(appointment)
    
    return {
        "success": True,
        "appointment_id": str(result.inserted_id),
        "message": f"Appointment confirmed for {date} at {time}."
    }
