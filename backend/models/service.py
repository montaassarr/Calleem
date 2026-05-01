"""
Service Data Model
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ServiceBase(BaseModel):
    """Base service model"""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, ge=0)
    active: bool = True


class ServiceCreate(ServiceBase):
    """Model for creating a new service"""
    pass


class ServiceUpdate(BaseModel):
    """Model for updating a service"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, ge=0)
    active: Optional[bool] = None


class ServiceInDB(ServiceBase):
    """Model for service stored in database"""
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "name": "Haircut",
                "description": "Classic men's haircut with styling",
                "price": 25.00,
                "active": True,
                "created_at": "2025-11-13T10:00:00",
                "updated_at": "2025-11-13T10:00:00"
            }
        }


class ServiceResponse(BaseModel):
    """Model for service API response"""
    id: str
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "name": "Haircut",
                "description": "Classic men's haircut",
                "price": 25.00,
                "active": True
            }
        }
