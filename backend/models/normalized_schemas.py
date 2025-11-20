"""
Normalized MongoDB Schemas
These schemas match the exact field names required for voice and text agent integration
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum


# ============================================================================
# APPOINTMENTS SCHEMA
# ============================================================================

class AppointmentNormalized(BaseModel):
    """
    Normalized appointment schema for MongoDB
    Field names: businessId, name, phone, service, start, end, notes, source
    """
    businessId: str = Field(default="default", description="Business tenant ID")
    name: str = Field(..., min_length=2, max_length=100, description="Client name")
    phone: str = Field(..., description="Client phone number")
    service: str = Field(..., min_length=2, description="Service name")
    start: datetime = Field(..., description="Appointment start time (ISODate)")
    end: datetime = Field(..., description="Appointment end time (ISODate)")
    notes: Optional[str] = Field(default="", description="Additional notes")
    source: Literal["voice", "text"] = Field(..., description="Booking source: voice or text")
    
    # Internal tracking fields
    status: Optional[str] = Field(default="confirmed", description="confirmed, cancelled, completed, no_show")
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "businessId": "default",
                "name": "John Doe",
                "phone": "+21692034689",
                "service": "Haircut",
                "start": "2025-11-20T10:00:00Z",
                "end": "2025-11-20T10:30:00Z",
                "notes": "Prefers fade",
                "source": "voice",
                "status": "confirmed"
            }
        }
    )


# ============================================================================
# AVAILABILITY SCHEMA
# ============================================================================

class BreakPeriod(BaseModel):
    """Break period within a day"""
    start: str = Field(..., description="Break start time HH:MM format")
    end: str = Field(..., description="Break end time HH:MM format")


class AvailabilityNormalized(BaseModel):
    """
    Normalized availability schema for MongoDB
    Field names: businessId, dayOfWeek, open, close, breaks, isOpen
    """
    businessId: str = Field(default="default", description="Business tenant ID")
    dayOfWeek: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    open: str = Field(..., description="Opening time in HH:MM format")
    close: str = Field(..., description="Closing time in HH:MM format")
    breaks: List[BreakPeriod] = Field(default_factory=list, description="Break periods")
    isOpen: bool = Field(default=True, description="Is business open this day")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "businessId": "default",
                "dayOfWeek": 0,
                "open": "09:00",
                "close": "20:00",
                "breaks": [{"start": "13:00", "end": "14:00"}],
                "isOpen": True
            }
        }
    )


# ============================================================================
# SERVICES SCHEMA
# ============================================================================

class ServiceNormalized(BaseModel):
    """
    Normalized service schema for MongoDB
    Field names: businessId, name, durationMinutes, price
    """
    businessId: str = Field(default="default", description="Business tenant ID")
    name: str = Field(..., min_length=2, description="Service name")
    durationMinutes: int = Field(..., ge=15, le=240, description="Service duration in minutes")
    price: float = Field(..., ge=0, description="Service price")
    isActive: bool = Field(default=True, description="Is service currently available")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "businessId": "default",
                "name": "Haircut",
                "durationMinutes": 30,
                "price": 25.0,
                "isActive": True
            }
        }
    )


# ============================================================================
# BUSINESS CONFIG SCHEMA
# ============================================================================

class BusinessConfigNormalized(BaseModel):
    """
    Normalized business config schema for MongoDB
    Field names: businessId, name, phone, timezone, openingHours, services
    """
    businessId: str = Field(default="default", description="Business tenant ID")
    name: str = Field(..., description="Business name")
    phone: str = Field(..., description="Business phone number")
    timezone: str = Field(default="America/New_York", description="Business timezone")
    openingHours: List[AvailabilityNormalized] = Field(default_factory=list, description="Weekly opening hours")
    services: List[ServiceNormalized] = Field(default_factory=list, description="Available services")
    
    # Additional settings
    features: Dict[str, bool] = Field(default_factory=dict, description="Feature flags")
    voiceConfig: Optional[Dict[str, Any]] = Field(default=None, description="Voice agent configuration")
    aiConfig: Optional[Dict[str, Any]] = Field(default=None, description="AI configuration")
    
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "businessId": "default",
                "name": "Royal Fade Barbershop",
                "phone": "+21692034689",
                "timezone": "Africa/Tunis",
                "openingHours": [],
                "services": [],
                "features": {"voiceAgent": True}
            }
        }
    )


# ============================================================================
# CONVERSATION HISTORY SCHEMA
# ============================================================================

class ConversationHistoryNormalized(BaseModel):
    """
    Normalized conversation history schema for MongoDB
    Field names: businessId, type, sender, message, timestamp, metadata
    """
    businessId: str = Field(default="default", description="Business tenant ID")
    type: Literal["voice", "text"] = Field(..., description="Conversation type: voice or text")
    sender: Literal["client", "agent"] = Field(..., description="Message sender: client or agent")
    message: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "businessId": "default",
                "type": "voice",
                "sender": "client",
                "message": "I want to book a haircut",
                "timestamp": "2025-11-20T10:00:00Z",
                "metadata": {
                    "callId": "call_123",
                    "phone": "+21692034689",
                    "service": "Haircut"
                }
            }
        }
    )


# ============================================================================
# HELPER FUNCTIONS FOR SCHEMA CONVERSION
# ============================================================================

def convert_legacy_appointment_to_normalized(legacy: Dict[str, Any]) -> Dict[str, Any]:
    """Convert legacy appointment format to normalized schema"""
    
    # Handle datetime vs start/end
    start_time = legacy.get("start") or legacy.get("datetime") or legacy.get("scheduled_time")
    
    # Calculate end time if not present
    if legacy.get("end"):
        end_time = legacy["end"]
    elif start_time and legacy.get("duration_minutes"):
        from datetime import timedelta
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        end_time = start_time + timedelta(minutes=int(legacy["duration_minutes"]))
    else:
        # Default 30 minutes
        from datetime import timedelta
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        end_time = start_time + timedelta(minutes=30)
    
    # Determine source
    source = legacy.get("source", "text")
    if "voice" in str(legacy.get("metadata", {})).lower():
        source = "voice"
    
    return {
        "businessId": legacy.get("businessId") or legacy.get("business_id") or "default",
        "name": legacy.get("name") or legacy.get("client_name") or "Unknown",
        "phone": legacy.get("phone") or legacy.get("client_phone") or "",
        "service": legacy.get("service") or "General",
        "start": start_time,
        "end": end_time,
        "notes": legacy.get("notes") or "",
        "source": source,
        "status": legacy.get("status") or "confirmed",
        "createdAt": legacy.get("createdAt") or legacy.get("created_at") or datetime.utcnow(),
        "updatedAt": legacy.get("updatedAt") or legacy.get("updated_at") or datetime.utcnow(),
    }


def convert_legacy_service_to_normalized(legacy: Dict[str, Any]) -> Dict[str, Any]:
    """Convert legacy service format to normalized schema"""
    return {
        "businessId": legacy.get("businessId") or legacy.get("business_id") or "default",
        "name": legacy.get("name") or "Unnamed Service",
        "durationMinutes": legacy.get("durationMinutes") or legacy.get("duration_minutes") or 30,
        "price": legacy.get("price") or 0.0,
        "isActive": legacy.get("isActive") if "isActive" in legacy else legacy.get("is_active", True),
    }


def convert_legacy_availability_to_normalized(legacy: Dict[str, Any]) -> Dict[str, Any]:
    """Convert legacy availability/opening hours format to normalized schema"""
    
    # Handle day mapping
    day_of_week = legacy.get("dayOfWeek")
    if day_of_week is None:
        day_of_week = legacy.get("day_of_week")
    if day_of_week is None and "day" in legacy:
        day_map = {
            "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
            "friday": 4, "saturday": 5, "sunday": 6
        }
        day_of_week = day_map.get(str(legacy["day"]).lower(), 0)
    
    return {
        "businessId": legacy.get("businessId") or legacy.get("business_id") or "default",
        "dayOfWeek": day_of_week or 0,
        "open": legacy.get("open") or legacy.get("open_time") or "09:00",
        "close": legacy.get("close") or legacy.get("close_time") or "17:00",
        "breaks": legacy.get("breaks") or [],
        "isOpen": legacy.get("isOpen") if "isOpen" in legacy else legacy.get("is_open", True),
    }
