from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class BusinessConfig(BaseModel):
    id: str = Field(alias="_id")
    business_id: str
    language: str = "en"
    timezone: str = "UTC"
    default_duration: int = 30

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "ai_settings_001",
                "business_id": "business_123",
                "language": "en",
                "timezone": "Africa/Tunis",
                "default_duration": 30
            }
        }
    )
