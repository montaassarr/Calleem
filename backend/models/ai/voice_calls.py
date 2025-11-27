from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any

class VoiceCall(BaseModel):
    id: str = Field(alias="_id")
    business_id: str
    client_phone: str
    status: str = "completed"
    duration_seconds: int = 0
    transcription: List[Dict[str, Any]] = []
    recording_url: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "call_001",
                "business_id": "business_123",
                "client_phone": "+216900000",
                "status": "completed",
                "duration_seconds": 180,
                "transcription": [],
                "recording_url": "https://api.vapi.ai/recordings/..."
            }
        }
    )
