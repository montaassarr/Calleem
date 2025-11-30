from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any

class AiLog(BaseModel):
    id: str = Field(alias="_id")
    business_id: str
    action: str
    model: str
    tokens_used: int = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "ai_log_123",
                "business_id": "business_123",
                "action": "generate_response",
                "model": "llama3-70b",
                "tokens_used": 150
            }
        }
    )
