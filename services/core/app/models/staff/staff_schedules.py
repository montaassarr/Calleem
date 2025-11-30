from pydantic import BaseModel, Field, ConfigDict
from typing import List

class StaffSchedule(BaseModel):
    id: str = Field(alias="_id")
    staff_id: str
    day: str
    start_time: str
    end_time: str

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "sched_001",
                "staff_id": "staff_001",
                "day": "monday",
                "start_time": "09:00",
                "end_time": "17:00"
            }
        }
    )
