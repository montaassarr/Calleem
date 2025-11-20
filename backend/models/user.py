"""
User/Admin Data Model
"""

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration"""
    ADMIN = "admin"
    BARBER = "barber"
    MANAGER = "manager"


class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=2, max_length=100)
    role: UserRole = UserRole.BARBER
    active: bool = True


class UserCreate(UserBase):
    """Model for creating a new user"""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Model for updating a user"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[UserRole] = None
    active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)


class UserInDB(UserBase):
    """Model for user stored in database"""
    id: str = Field(alias="_id")
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "email": "admin@barbershop.com",
                "username": "admin",
                "full_name": "Admin User",
                "role": "admin",
                "active": True,
                "hashed_password": "$2b$12$...",
                "created_at": "2025-11-13T10:00:00",
                "updated_at": "2025-11-13T10:00:00"
            }
        }
    )


class UserResponse(BaseModel):
    """Model for user API response (without sensitive data)"""
    id: str
    email: EmailStr
    username: str
    full_name: str
    role: UserRole
    active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "email": "admin@barbershop.com",
                "username": "admin",
                "full_name": "Admin User",
                "role": "admin",
                "active": True,
                "created_at": "2025-11-13T10:00:00"
            }
        }
    )


class Token(BaseModel):
    """JWT Token response model"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""
    user_id: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request model"""
    username: str
    password: str
