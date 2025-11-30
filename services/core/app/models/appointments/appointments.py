from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional
from datetime import datetime, timedelta
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
    start_time: datetime
    end_time: datetime
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
    datetime: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    notes: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def check_times(cls, values):
        """Validate that we have either datetime+duration OR start_time+end_time"""
        if isinstance(values, dict):
            has_datetime = values.get('datetime') and values.get('duration_minutes')
            has_times = values.get('start_time') and values.get('end_time')
            
            if has_datetime or has_times:
                return values
            
            raise ValueError("Must provide either (datetime + duration_minutes) OR (start_time + end_time)")
        return values

class AppointmentUpdate(BaseModel):
    location_id: Optional[str] = None
    client_id: Optional[str] = None
    service_id: Optional[str] = None
    staff_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[AppointmentStatus] = None
    source: Optional[str] = None

class Appointment(AppointmentBase):
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

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
    pass
