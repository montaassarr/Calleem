from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

from typing import Optional, Dict, Any, List
from models.business.api_keys import ApiKey

class BusinessConfig(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    business_id: Optional[str] = None
    # General
    business_name: str = "My Business"
    
    # Localization
    language: Optional[str] = "en"
    timezone: str = "UTC"
    currency: Optional[str] = "USD"
    
    # Configuration
    default_duration: Optional[int] = 30
    is_configured: Optional[bool] = False
    
    # Twilio (kept for backward compatibility, will migrate to api_keys)
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    twilio_verify_sid: Optional[str] = None

    # Integrations
    google_calendar_connected: Optional[bool] = False
    google_calendar_credentials: Optional[Dict[str, Any]] = None
    hubspot_credentials: Optional[Dict[str, Any]] = None
    slack_credentials: Optional[Dict[str, Any]] = None
    stripe_credentials: Optional[Dict[str, Any]] = None
    whatsapp_config: Optional[Dict[str, Any]] = None
    
    # AI Settings
    system_prompt: Optional[str] = None
    
    # Automations
    automations: Optional[Dict[str, bool]] = Field(default_factory=dict)
    
    # API Keys (BYOK)
    api_keys: List[ApiKey] = Field(default_factory=list)
    
    # Scheduling
    business_hours: Optional[dict] = {
        "monday": {"start": "09:00", "end": "17:00", "enabled": True},
        "tuesday": {"start": "09:00", "end": "17:00", "enabled": True},
        "wednesday": {"start": "09:00", "end": "17:00", "enabled": True},
        "thursday": {"start": "09:00", "end": "17:00", "enabled": True},
        "friday": {"start": "09:00", "end": "17:00", "enabled": True},
        "saturday": {"start": "10:00", "end": "14:00", "enabled": True},
        "sunday": {"start": "00:00", "end": "00:00", "enabled": False}
    }

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        json_schema_extra={
            "example": {
                "_id": "ai_settings_001",
                "business_id": "business_123",
                "business_name": "Royal Fade Barbershop",
                "language": "en",
                "timezone": "Africa/Tunis",
                "default_duration": 30
            }
        }
    )

class BusinessConfigUpdate(BaseModel):
    business_name: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None
    default_duration: Optional[int] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    is_configured: Optional[bool] = None
    
    # Twilio (kept for backward compatibility)
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    twilio_verify_sid: Optional[str] = None
    google_calendar_connected: Optional[bool] = None
    whatsapp_config: Optional[Dict[str, Any]] = None
    
    system_prompt: Optional[str] = None
    automations: Optional[Dict[str, bool]] = None
    business_hours: Optional[dict] = None
    
    model_config = ConfigDict(extra="allow")
