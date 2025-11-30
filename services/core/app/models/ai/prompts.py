from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class Prompt(BaseModel):
    id: str = Field(alias="_id")
    business_id: str
    type: str = "system"
    content: str

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "prompt_default",
                "business_id": "business_123",
                "type": "system",
                "content": "You are a helpful AI receptionist..."
            }
        }
    )
