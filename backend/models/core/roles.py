from pydantic import BaseModel, Field, ConfigDict
from typing import List

class Role(BaseModel):
    id: str = Field(alias="_id")
    business_id: str
    name: str
    permissions: List[str] = []

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "role_manager",
                "business_id": "business_123",
                "name": "Manager",
                "permissions": ["manage_staff", "view_reports"]
            }
        }
    )
