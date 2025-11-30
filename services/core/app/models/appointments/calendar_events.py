from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class CalendarEvent(BaseModel):
    id: str = Field(alias="_id")
    business_id: str
    title: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "event_123",
                "business_id": "business_123",
                "title": "Staff Meeting",
                "start_time": "2025-01-02T08:00:00",
                "end_time": "2025-01-02T09:00:00"
            }
        }
    )
