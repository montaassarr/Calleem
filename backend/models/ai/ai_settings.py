from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class AiSettings(BaseModel):
    id: str = Field(alias="_id")
    business_id: str
    model: str = "groq/llama3-70b"
    voice_model: str = "vapi"
    temperature: float = 0.3
    system_prompt: str

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "ai_123",
                "business_id": "business_123",
                "model": "groq/llama3-70b",
                "voice_model": "vapi",
                "temperature": 0.3,
                "system_prompt": "You are a friendly barber receptionist..."
            }
        }
    )
