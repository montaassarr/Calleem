from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

class StaffSettings(BaseModel):
    id: str = Field(alias="_id")
    business_id: str
    allow_staff_login: bool = True
    default_role: str = "staff"

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "staff_settings_123",
                "business_id": "business_123",
                "allow_staff_login": True,
                "default_role": "staff"
            }
        }
    )
