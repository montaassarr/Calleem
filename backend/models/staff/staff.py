from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

class StaffMember(BaseModel):
    id: str = Field(alias="_id")
    business_id: str
    name: str
    services: List[str] = []
    active: bool = True

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "staff_001",
                "business_id": "business_123",
                "name": "Ahmed",
                "services": ["service_123"],
                "active": True
            }
        }
    )
