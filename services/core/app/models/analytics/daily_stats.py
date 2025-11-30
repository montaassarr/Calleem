from pydantic import BaseModel, Field, ConfigDict
from datetime import date

class DailyStats(BaseModel):
    id: str = Field(alias="_id")
    business_id: str
    date: date
    total_calls: int = 0
    total_appointments: int = 0
    revenue: float = 0.0

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "stats_2025-01-01",
                "business_id": "business_123",
                "date": "2025-01-01",
                "total_calls": 15,
                "total_appointments": 5,
                "revenue": 150.0
            }
        }
    )
