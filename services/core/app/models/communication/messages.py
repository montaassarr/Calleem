from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class Message(BaseModel):
    id: str = Field(alias="_id")
    conversation_id: str
    from_role: str = Field(alias="from") # 'from' is a reserved keyword
    text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "msg_001",
                "conversation_id": "conv_001",
                "from": "client",
                "text": "Hello I want a haircut"
            }
        }
    )
