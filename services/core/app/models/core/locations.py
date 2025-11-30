from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class OpeningHours(BaseModel):
    day: str
    open: str
    close: str
    closed: bool = False

class Location(BaseModel):
    id: str = Field(alias="_id")
    business_id: str
    name: str
    timezone: str = "UTC"
    opening_hours: List[OpeningHours] = []

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "location_001",
                "business_id": "business_123",
                "name": "Main Branch",
                "timezone": "Africa/Tunis",
                "opening_hours": [
                    { "day": "monday", "open": "09:00", "close": "19:00", "closed": False }
                ]
            }
        }
    )
