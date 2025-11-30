from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any

class ClientPreferences(BaseModel):
    id: str = Field(alias="_id")
    client_id: str
    preferences: Dict[str, Any] = {}

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "pref_123",
                "client_id": "client_789",
                "preferences": {"drink": "coffee", "music": "jazz"}
            }
        }
    )
