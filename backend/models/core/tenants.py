from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TenantStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"

class TenantPlan(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class TenantBase(BaseModel):
    owner_id: str
    name: str
    country: Optional[str] = None
    timezone: str = "UTC"
    plan: TenantPlan = TenantPlan.FREE
    status: TenantStatus = TenantStatus.ACTIVE
    is_configured: bool = False
    whatsapp_phone_number_id: Optional[str] = None

class TenantCreate(TenantBase):
    pass

class TenantUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    plan: Optional[TenantPlan] = None
    status: Optional[TenantStatus] = None

class Tenant(TenantBase):
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    total_calls: int = 0
    total_minutes: float = 0.0

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "business_123",
                "owner_id": "user_001",
                "name": "Royal Fade Barbershop",
                "country": "Tunisia",
                "timezone": "Africa/Tunis",
                "plan": "premium",
                "status": "active"
            }
        }
    )

class TenantResponse(Tenant):
    pass

class TenantInDB(Tenant):
    pass
