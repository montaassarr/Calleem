from pydantic import BaseModel, Field, ConfigDict
from typing import List

class StaffPermissions(BaseModel):
    id: str = Field(alias="_id")
    staff_id: str
    permissions: List[str] = []

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "perm_001",
                "staff_id": "staff_001",
                "permissions": ["view_calendar", "manage_appointments"]
            }
        }
    )
