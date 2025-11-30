from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class ClientNote(BaseModel):
    id: str = Field(alias="_id")
    client_id: str
    author_id: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "note_123",
                "client_id": "client_789",
                "author_id": "user_001",
                "content": "Prefers short sides."
            }
        }
    )
