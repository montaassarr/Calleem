"""
User Data Model
===============
Simplified model: Tenant = User (business owner who signs up)
Admin is platform owner (you), no auth needed for admin panel
"""

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles for access control"""
    OWNER = "owner"           # Business owner (tenant creator)
    ADMIN = "admin"           # Business admin
    STAFF = "staff"           # Staff member
    SUPER_ADMIN = "super_admin"  # Platform admin (you)


class UserCreate(BaseModel):
    """Model for creating a new user (tenant registration)"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8)
    business_name: str = Field(..., min_length=2, max_length=100)


class UserUpdate(BaseModel):
    """Model for updating user profile"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    password: Optional[str] = Field(None, min_length=8)


class UserInDB(BaseModel):
    """Model for user stored in database"""
    id: str = Field(alias="_id")
    email: EmailStr
    username: str
    full_name: str
    hashed_password: str
    tenant_id: str  # Links to tenant document
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(populate_by_name=True)


class UserResponse(BaseModel):
    """Model for user API response (without sensitive data)"""
    id: str
    email: EmailStr
    username: str
    full_name: str
    tenant_id: str
    role: Optional[str] = "owner"
    active: bool = True  # Default to True for backward compatibility
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


class Token(BaseModel):
    """JWT Token response model"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request model"""
    username: str
    password: str
