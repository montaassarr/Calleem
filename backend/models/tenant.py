"""
Tenant Data Model
"""

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class PlanTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class TenantStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"

class PhoneProvider(str, Enum):
    """Phone number provider types"""
    VAPI = "vapi"
    TWILIO = "twilio"
    NONE = "none"

class TwilioCredentials(BaseModel):
    """Encrypted Twilio credentials for phone integration"""
    account_sid_encrypted: Optional[str] = None
    auth_token_encrypted: Optional[str] = None
    phone_number: Optional[str] = None  # E.164 format
    number_sid: Optional[str] = None  # Twilio phone number SID
    credential_id: Optional[str] = None  # Vapi SIP credential ID
    
    model_config = ConfigDict(extra="allow")

class TenantPhoneConfig(BaseModel):
    """Phone number configuration for tenant"""
    vapi_phone_number_id: Optional[str] = None  # Vapi phone number resource ID
    phone_number: Optional[str] = None  # Actual phone number (E.164)
    phone_provider: PhoneProvider = PhoneProvider.NONE
    twilio_credentials: Optional[TwilioCredentials] = None  # Encrypted Twilio creds
    is_active: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(extra="allow")

class TenantSettings(BaseModel):
    """Tenant-specific configuration"""
    business_name: str
    timezone: str = "UTC"
    currency: str = "USD"
    
    # Twilio (kept for backward compatibility)
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    
    # Integrations
    google_calendar_connected: bool = False
    slack_webhook_url: Optional[str] = None
    hubspot_api_key: Optional[str] = None
    google_calendar_credentials: Optional[Dict[str, Any]] = None
    
    # Custom prompts
    system_prompt: Optional[str] = None
    
    model_config = ConfigDict(extra="allow")

class TenantBase(BaseModel):
    """Base tenant model"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    plan: PlanTier = PlanTier.FREE
    status: TenantStatus = TenantStatus.ACTIVE
    settings: TenantSettings

class TenantCreate(TenantBase):
    """Model for creating a new tenant"""
    pass

class TenantUpdate(BaseModel):
    """Model for updating a tenant"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    plan: Optional[PlanTier] = None
    status: Optional[TenantStatus] = None
    settings: Optional[TenantSettings] = None

class TenantInDB(TenantBase):
    """Model for tenant stored in database"""
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Phone configuration
    phone_config: TenantPhoneConfig = Field(default_factory=TenantPhoneConfig)
    
    # Usage metrics (simple counters for now)
    total_calls: int = 0
    total_minutes: float = 0.0
    
    # Stripe integration fields
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    subscription_status: Optional[str] = None  # trialing, active, past_due, canceled
    
    # Trial management
    trial_start_date: Optional[datetime] = None
    trial_end_date: Optional[datetime] = None
    trial_minutes_used: float = 0.0
    trial_minutes_limit: float = 100.0
    
    # Billing period
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
    
    # Onboarding status
    is_configured: bool = False
    onboarding_completed: bool = False
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "tenant_123",
                "name": "Cool Barber Shop",
                "email": "owner@coolbarber.com",
                "plan": "pro",
                "status": "active",
                "settings": {
                    "business_name": "Cool Barber Shop",
                    "timezone": "America/New_York"
                },
                "created_at": "2025-11-24T10:00:00",
                "updated_at": "2025-11-24T10:00:00",
                "trial_end_date": "2025-12-08T10:00:00",
                "trial_minutes_used": 43.5,
                "trial_minutes_limit": 100.0
            }
        }
    )

class TenantResponse(BaseModel):
    """Model for tenant API response"""
    id: str
    name: str
    email: EmailStr
    plan: PlanTier
    status: TenantStatus
    settings: TenantSettings
    created_at: datetime
    total_calls: int
    total_minutes: float
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "tenant_123",
                "name": "Cool Barber Shop",
                "email": "owner@coolbarber.com",
                "plan": "pro",
                "status": "active",
                "settings": {
                    "business_name": "Cool Barber Shop"
                },
                "created_at": "2025-11-24T10:00:00",
                "total_calls": 150,
                "total_minutes": 450.5
            }
        }
    )
