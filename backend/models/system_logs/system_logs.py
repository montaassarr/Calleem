from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any

class SystemLog(BaseModel):
    id: str = Field(alias="_id")
    level: str = "INFO"
    message: str
    context: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "log_123",
                "level": "ERROR",
                "message": "Failed to connect to VAPI",
                "context": {"retry_count": 3}
            }
        }
    )
