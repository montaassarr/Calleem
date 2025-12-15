from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    OWNER = "owner"
    ADMIN = "admin"
    STAFF = "staff"
    VIEWER = "viewer"
    BARBER = "barber" # Keeping for backward compatibility
    MANAGER = "manager" # Keeping for backward compatibility

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=2, max_length=100)
    role: UserRole = UserRole.STAFF
    business_id: Optional[str] = None # Optional for now to support legacy
    tenant_id: Optional[str] = None # New standard field for multi-tenancy
    permissions: List[str] = []
    active: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    business_name: Optional[str] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[UserRole] = None
    active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)
    permissions: Optional[List[str]] = None

class User(UserBase):
    id: str = Field(alias="_id")
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "user_001",
                "business_id": "business_123",
                "email": "owner@example.com",
                "username": "owner",
                "full_name": "Owner User",
                "role": "owner",
                "permissions": ["manage_ai", "view_reports"]
            }
        }
    )

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    username: str
    full_name: str
    role: UserRole
    active: bool
    business_id: Optional[str] = None
    tenant_id: Optional[str] = None
    permissions: List[str] = []
    created_at: datetime
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(
        populate_by_name=True
    )

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str
