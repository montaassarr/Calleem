"""
Business Configuration Model
Dynamic configuration stored in MongoDB per business (for multi-tenancy)
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, time


class OpeningHours(BaseModel):
    """Operating hours for a specific day"""
    day: str  # monday, tuesday, etc.
    open: str  # e.g., "09:00"
    close: str  # e.g., "17:00"
    closed: bool = False


class ServiceDefinition(BaseModel):
    """Service configuration"""
    name: str
    description: str
    duration_minutes: int = 30
    price: float = 0.0
    active: bool = True


class AIConfiguration(BaseModel):
    """AI Agent configuration"""
    model: str = "llama-3.3-70b-versatile"  # Groq model
    temperature: float = 0.7
    max_tokens: int = 500
    system_prompt: str = ""
    voice_enabled: bool = False
    voice_model: str = "whisper-large-v3"


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
    whatsapp_config: Optional[WhatsAppConfiguration] = None
    active: Optional[bool] = None
    features_enabled: Optional[Dict[str, bool]] = None


class BusinessConfigInDB(BusinessConfigBase):
    """Business configuration stored in database"""
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


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
    whatsapp_config: WhatsAppConfiguration
    active: bool
    features_enabled: Dict[str, bool]
    created_at: datetime
    updated_at: datetime
