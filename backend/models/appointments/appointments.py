from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional
from datetime import datetime as dt, timedelta
from enum import Enum

class AppointmentStatus(str, Enum):
    CONFIRMED = "confirmed"
    PENDING = "pending"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"

class AppointmentBase(BaseModel):
    business_id: Optional[str] = "default_business"
    tenant_id: Optional[str] = None
    location_id: Optional[str] = "default_location"
    client_id: Optional[str] = None
    client_name: Optional[str] = None
    client_phone: Optional[str] = None
    service_id: Optional[str] = None
    service: Optional[str] = None  # Service name
    staff_id: Optional[str] = None
    start_time: dt
    end_time: dt
    status: AppointmentStatus = AppointmentStatus.CONFIRMED
    source: str = "whatsapp"
    notes: Optional[str] = None

class AppointmentCreate(BaseModel):
    """
    Flexible appointment creation - accepts EITHER:
    1. datetime + duration_minutes
    2. start_time + end_time
    """
    service_id: Optional[str] = None
    service: Optional[str] = None
    customer_name: Optional[str] = None
    client_name: Optional[str] = None
    customer_phone: Optional[str] = None
    client_phone: Optional[str] = None
    datetime: Optional[dt] = None
    duration_minutes: Optional[int] = None
    start_time: Optional[dt] = None
    end_time: Optional[dt] = None
    notes: Optional[str] = None

class AppointmentUpdate(BaseModel):
    location_id: Optional[str] = None
    client_id: Optional[str] = None
    client_name: Optional[str] = None
    client_phone: Optional[str] = None
    service_id: Optional[str] = None
    service: Optional[str] = None
    staff_id: Optional[str] = None
    start_time: Optional[dt] = None
    end_time: Optional[dt] = None
    datetime: Optional[dt] = None
    duration_minutes: Optional[int] = None
    status: Optional[AppointmentStatus] = None
    source: Optional[str] = None
    notes: Optional[str] = None

class Appointment(AppointmentBase):
    id: str = Field(alias="_id")
    created_at: dt = Field(default_factory=dt.utcnow)
    updated_at: dt = Field(default_factory=dt.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "appointment_123",
                "business_id": "business_123",
                "tenant_id": "business_123",
                "location_id": "location_001",
                "client_id": "client_789",
                "service_id": "service_123",
                "staff_id": "staff_001",
                "start_time": "2025-01-02T10:00:00",
                "end_time": "2025-01-02T10:30:00",
                "status": "confirmed",
                "source": "whatsapp"
            }
        }
    )

class AppointmentResponse(Appointment):
    id: str = Field()  # Override to remove alias and ensure 'id' is in JSON
    datetime: Optional[dt] = None  # Alias for start_time for frontend compatibility
    duration_minutes: Optional[int] = None  # Computed from end_time - start_time
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        json_schema_extra={
            "example": {
                "_id": "appointment_123",
                "business_id": "business_123",
                "tenant_id": "business_123",
                "location_id": "location_001",
                "client_id": "client_789",
                "service_id": "service_123",
                "staff_id": "staff_001",
                "start_time": "2025-01-02T10:00:00",
                "end_time": "2025-01-02T10:30:00",
                "datetime": "2025-01-02T10:00:00",
                "duration_minutes": 30,
                "status": "confirmed",
                "source": "whatsapp"
            }
        }
    )
