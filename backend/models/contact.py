"""
Contact Data Model
==================
Model for storing contact form submissions from the landing page.
"""

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


class ContactStatus(str, Enum):
    """Contact submission status"""
    NEW = "new"
    READ = "read"
    RESPONDED = "responded"
    ARCHIVED = "archived"


class ContactCreate(BaseModel):
    """Model for creating a new contact submission"""
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    business_name: str = Field(..., min_length=2, max_length=100)
    business_type: str = Field(..., max_length=50)
    phone_number: str = Field(..., min_length=5, max_length=20)
    monthly_calls: str = Field(..., max_length=50)
    message: Optional[str] = Field(None, max_length=2000)
    newsletter: bool = False
    privacy_policy: bool = True


class ContactUpdate(BaseModel):
    """Model for updating a contact submission"""
    status: Optional[ContactStatus] = None
    admin_notes: Optional[str] = Field(None, max_length=1000)


class ContactInDB(BaseModel):
    """Model for contact stored in database"""
    id: str = Field(alias="_id")
    full_name: str
    email: EmailStr
    business_name: str
    business_type: str
    phone_number: str
    monthly_calls: str
    message: Optional[str] = None
    newsletter: bool = False
    privacy_policy: bool = True
    status: ContactStatus = ContactStatus.NEW
    admin_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(populate_by_name=True)


class ContactResponse(BaseModel):
    """Model for contact API response"""
    id: str
    full_name: str
    email: EmailStr
    business_name: str
    business_type: str
    phone_number: str
    monthly_calls: str
    message: Optional[str] = None
    newsletter: bool = False
    status: ContactStatus = ContactStatus.NEW
    admin_notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ContactStats(BaseModel):
    """Statistics for contact submissions"""
    total: int = 0
    new: int = 0
    read: int = 0
    responded: int = 0
    archived: int = 0
    today: int = 0
    this_week: int = 0
    this_month: int = 0
