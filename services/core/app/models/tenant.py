from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class TenantConfig(BaseModel):
    business_name: str
    timezone: str = "UTC"
    currency: str = "USD"
    language: str = "en"
    
class ApiKeys(BaseModel):
    openai_key: Optional[str] = None
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    vapi_private_key: Optional[str] = None
    vapi_public_key: Optional[str] = None
    elevenlabs_key: Optional[str] = None  # ElevenLabs API key for voice AI


class Tenant(BaseModel):
    """
    Tenant model - represents a business owner with their own dashboard
    Each tenant is a separate business with isolated data
    """
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    
    # Authentication fields
    fullname: str  # Business owner's full name
    email: EmailStr  # Used for login (unique)
    password: str  # Hashed password
    phone: str  # Business phone number (used for n8n tenant lookup, unique)
    
    # Business configuration
    config: TenantConfig = Field(default_factory=TenantConfig)
    api_keys: ApiKeys = Field(default_factory=ApiKeys)
    
    # Subscription & Usage
    plan: str = "free"  # free, basic, pro
    status: str = "active"  # active, suspended, canceled
    total_calls: int = 0
    total_minutes: float = 0.0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_configured: bool = False  # True when API keys are set

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class TenantCreate(BaseModel):
    """Schema for creating a new tenant (signup)"""
    fullname: str
    email: EmailStr
    password: str
    phone: str
    business_name: str  # Will be used in config


class TenantLogin(BaseModel):
    """Schema for tenant login"""
    email: EmailStr
    password: str


class TenantResponse(BaseModel):
    """Schema for tenant responses (without password)"""
    id: str
    fullname: str
    email: EmailStr
    phone: str
    config: TenantConfig
    plan: str
    status: str
    total_calls: int
    total_minutes: float
    created_at: datetime
    is_configured: bool

