"""
Appointment Data Model
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime as dt
from enum import Enum
import re


class AppointmentStatus(str, Enum):
    """Appointment status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


def normalize_phone(phone: str) -> str:
    """Normalize phone number to E.164 format (+digits only), stripping spaces/dashes/parens."""
    if not phone:
        return phone
    # Keep leading + if present, strip everything else that isn't a digit
    cleaned = re.sub(r'[^\d+]', '', phone)
    # If multiple + signs, keep only the leading one
    if cleaned.count('+') > 1:
        cleaned = '+' + cleaned.replace('+', '')
    return cleaned


class AppointmentBase(BaseModel):
    """Base appointment model"""
    client_name: Optional[str] = Field(None, min_length=2, max_length=100)
    # Accept any phone that has 6-15 digits (with optional + prefix, spaces, dashes, parens, dots)
    client_phone: Optional[str] = Field(None)
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

    @field_validator('client_phone', 'customer_phone', mode='before')
    @classmethod
    def validate_and_normalize_phone(cls, v):
        if not v:
            return v
        normalized = normalize_phone(str(v))
        # Validate: 6 to 15 digits required
        digits_only = re.sub(r'[^\d]', '', normalized)
        if len(digits_only) < 6 or len(digits_only) > 15:
            raise ValueError('Phone number must contain 6 to 15 digits')
        return normalized


class AppointmentCreate(AppointmentBase):
    """Model for creating a new appointment"""
    pass


class AppointmentUpdate(BaseModel):
    """Model for updating an appointment"""
    client_name: Optional[str] = Field(None, min_length=2, max_length=100)
    client_phone: Optional[str] = Field(None)
    client_email: Optional[str] = Field(None, pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    service: Optional[str] = None
    datetime: Optional[dt] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=240)
    barber_preference: Optional[str] = None
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None

    @field_validator('client_phone', mode='before')
    @classmethod
    def validate_and_normalize_phone(cls, v):
        if not v:
            return v
        normalized = normalize_phone(str(v))
        digits_only = re.sub(r'[^\d]', '', normalized)
        if len(digits_only) < 6 or len(digits_only) > 15:
            raise ValueError('Phone number must contain 6 to 15 digits')
        return normalized


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
