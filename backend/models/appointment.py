"""
Appointment Data Model
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime as dt
from enum import Enum


class AppointmentStatus(str, Enum):
    """Appointment status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class AppointmentBase(BaseModel):
    """Base appointment model"""
    client_name: Optional[str] = Field(None, min_length=2, max_length=100)
    client_phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')
    client_email: Optional[str] = Field(None, pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    service: Optional[str] = Field(None, min_length=2)
    datetime: Optional[dt] = None
    duration_minutes: int = Field(default=30, ge=15, le=240)
    barber_preference: Optional[str] = None
    notes: Optional[str] = None
    # Alternative field names (for compatibility)
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    # Service reference
    service_id: Optional[str] = None
    # Alternative time fields
    start_time: Optional[dt] = None
    end_time: Optional[dt] = None


class AppointmentCreate(AppointmentBase):
    """Model for creating a new appointment"""
    pass


class AppointmentUpdate(BaseModel):
    """Model for updating an appointment"""
    client_name: Optional[str] = Field(None, min_length=2, max_length=100)
    client_phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')
    client_email: Optional[str] = Field(None, pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    service: Optional[str] = None
    datetime: Optional[dt] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=240)
    barber_preference: Optional[str] = None
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None


class AppointmentInDB(AppointmentBase):
    """Model for appointment stored in database"""
    id: str = Field(alias="_id")
    status: AppointmentStatus = AppointmentStatus.CONFIRMED
    conversation_id: Optional[str] = None
    created_at: dt = Field(default_factory=dt.utcnow)
    updated_at: dt = Field(default_factory=dt.utcnow)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "client_name": "John Doe",
                "client_phone": "+1234567890",
                "client_email": "john@example.com",
                "service": "Haircut",
                "datetime": "2025-11-14T15:00:00",
                "duration_minutes": 30,
                "barber_preference": "Mike",
                "status": "confirmed",
                "conversation_id": "conv_123456",
                "notes": "Prefers short fade",
                "created_at": "2025-11-13T10:00:00",
                "updated_at": "2025-11-13T10:00:00"
            }
        }


class AppointmentResponse(BaseModel):
    """Model for appointment API response"""
    id: str
    client_name: str
    client_phone: str
    client_email: Optional[str] = None
    service: str
    datetime: dt
    duration_minutes: int
    barber_preference: Optional[str] = None
    status: AppointmentStatus
    conversation_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: dt
    updated_at: dt
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "client_name": "John Doe",
                "client_phone": "+1234567890",
                "service": "Haircut",
                "datetime": "2025-11-14T15:00:00",
                "duration_minutes": 30,
                "status": "confirmed"
            }
        }
