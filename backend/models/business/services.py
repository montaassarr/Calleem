from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class ServiceBase(BaseModel):
    business_id: Optional[str] = "default_business"
    tenant_id: Optional[str] = None
    location_id: Optional[str] = "default_location"
    name: str
    price: float
    duration_minutes: int
    active: bool = True

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    duration_minutes: Optional[int] = None
    active: Optional[bool] = None

class Service(ServiceBase):
    id: str = Field(alias="_id")
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "service_123",
                "business_id": "business_123",
                "tenant_id": "business_123",
                "location_id": "location_001",
                "name": "Haircut",
                "price": 20.0,
                "duration_minutes": 30,
                "active": True
            }
        }
    )

class ServiceResponse(Service):
    id: str = Field()  # Override to remove alias and ensure 'id' is in JSON
    pass
