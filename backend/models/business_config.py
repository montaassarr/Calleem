"""
Business Configuration Model
Dynamic configuration stored in MongoDB per business (for multi-tenancy)
"""

from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import List, Optional, Dict, Any
from datetime import datetime, time


class OpeningHours(BaseModel):
    """Operating hours for a specific day"""
    day_of_week: int = Field(..., ge=0, le=6)
    is_open: bool = True
    open_time: str = "09:00"
    close_time: str = "17:00"

    @model_validator(mode="before")
    @classmethod
    def _legacy_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        day_map = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }

        if "day_of_week" not in data and "day" in data:
            data["day_of_week"] = day_map.get(str(data["day"]).lower(), 0)

        if "open_time" not in data and "open" in data:
            data["open_time"] = data["open"]

        if "close_time" not in data and "close" in data:
            data["close_time"] = data["close"]

        if "is_open" not in data and "closed" in data:
            data["is_open"] = not data.get("closed", False)

        return data


class ServiceDefinition(BaseModel):
    """Service configuration"""
    name: str
    description: str
    duration_minutes: int = 30
    price: float = 0.0
    is_active: bool = True

    @model_validator(mode="before")
    @classmethod
    def _legacy_active(cls, data: Any) -> Any:
        if isinstance(data, dict) and "active" in data and "is_active" not in data:
            data["is_active"] = data.pop("active")
        return data


class AIConfiguration(BaseModel):
    """AI Agent configuration"""
    model: str = "llama-3.3-70b-versatile"  # Groq model
    temperature: float = 0.7
    max_tokens: int = 500
    system_prompt: str = ""
    voice_enabled: bool = False
    voice_model: str = "whisper-large-v3"


class VoiceConfiguration(BaseModel):
    """Voice agent configuration (Vapi-style)"""
    # Model settings
    model_provider: str = "groq"  # groq, openai, anthropic
    model_name: str = "llama-3.3-70b-versatile"
    temperature: float = 0.7
    max_tokens: int = 500
    
    # Voice settings
    voice_provider: str = "openai"  # elevenlabs, openai, vapi
    voice_id: str = "alloy"  # ElevenLabs voice ID or OpenAI voice name
    
    # Conversation settings
    first_message: str = "Hi, this is Ava from the barbershop. How can I help you today?"
    system_prompt: str = ""
    
    # Tools configuration
    enabled_tools: List[str] = Field(default_factory=lambda: [
        "check_availability",
        "book_appointment",
        "get_services"
    ])
    
    # Advanced settings
    end_call_on_goodbye: bool = True
    record_calls: bool = True
    silence_timeout_seconds: int = 30


class WhatsAppConfiguration(BaseModel):
    """WhatsApp Cloud API configuration"""
    phone_number_id: str = ""
    access_token: str = ""
    verify_token: str = ""
    webhook_url: str = ""


class BusinessConfigBase(BaseModel):
    """Base business configuration model"""
    business_id: str = "default"  # For multi-tenancy
    business_name: str
    business_phone: str
    business_email: str
    business_address: str = ""
    timezone: str = "America/New_York"
    
    # Operating hours
    opening_hours: List[OpeningHours] = Field(default_factory=list)
    
    # Services offered
    services: List[ServiceDefinition] = Field(default_factory=list)
    
    # Capacity constraints
    max_clients_per_day: int = 20
    default_appointment_duration: int = 30
    
    # AI Configuration
    ai_config: AIConfiguration = Field(default_factory=AIConfiguration)
    
    # Voice Agent Configuration
    voice_config: VoiceConfiguration = Field(default_factory=VoiceConfiguration)
    
    # WhatsApp Configuration
    whatsapp_config: WhatsAppConfiguration = Field(default_factory=WhatsAppConfiguration)
    
    # Additional settings
    active: bool = True
    features_enabled: Dict[str, bool] = Field(default_factory=dict)


class BusinessConfigCreate(BusinessConfigBase):
    """Model for creating business configuration"""
    pass


class BusinessConfigUpdate(BaseModel):
    """Model for updating business configuration"""
    business_name: Optional[str] = None
    business_phone: Optional[str] = None
    business_email: Optional[str] = None
    business_address: Optional[str] = None
    timezone: Optional[str] = None
    opening_hours: Optional[List[OpeningHours]] = None
    services: Optional[List[ServiceDefinition]] = None
    max_clients_per_day: Optional[int] = None
    default_appointment_duration: Optional[int] = None
    ai_config: Optional[AIConfiguration] = None
    voice_config: Optional[VoiceConfiguration] = None
    whatsapp_config: Optional[WhatsAppConfiguration] = None
    active: Optional[bool] = None
    features_enabled: Optional[Dict[str, bool]] = None


class BusinessConfigInDB(BusinessConfigBase):
    """Business configuration stored in database"""
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(populate_by_name=True)


class BusinessConfigResponse(BaseModel):
    """Business configuration API response"""
    id: str
    business_id: str
    business_name: str
    business_phone: str
    business_email: str
    business_address: str
    timezone: str
    opening_hours: List[OpeningHours]
    services: List[ServiceDefinition]
    max_clients_per_day: int
    default_appointment_duration: int
    ai_config: AIConfiguration
    voice_config: VoiceConfiguration
    whatsapp_config: WhatsAppConfiguration
    active: bool
    features_enabled: Dict[str, bool]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "business_id": "default",
                "business_name": "Royal Fade Barbershop",
                "business_phone": "+1234567890",
                "business_email": "info@barbershop.com",
                "business_address": "123 Main St, New York, NY",
                "timezone": "America/New_York",
                "opening_hours": [
                    {"day_of_week": 0, "is_open": True, "open_time": "09:00", "close_time": "18:00"}
                ],
                "services": [
                    {"name": "Haircut", "description": "Classic", "duration_minutes": 30, "price": 25.0}
                ],
                "max_clients_per_day": 20,
                "default_appointment_duration": 30,
                "ai_config": {"model": "llama-3.3-70b-versatile"},
                "whatsapp_config": {"phone_number_id": "123", "access_token": "***"},
                "active": True,
                "features_enabled": {"voice_agent": True},
                "created_at": "2025-11-13T10:00:00",
                "updated_at": "2025-11-13T10:00:00"
            }
        }
    )
