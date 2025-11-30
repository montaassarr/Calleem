from pydantic import BaseModel, Field, ConfigDict
from typing import List

class AvailabilityCache(BaseModel):
    id: str = Field(alias="_id")
    business_id: str
    date: str
    slots: List[str] = []

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "location_001_2025-01-02",
                "business_id": "business_123",
                "date": "2025-01-02",
                "slots": ["09:00", "09:30", "10:00"]
            }
        }
    )
