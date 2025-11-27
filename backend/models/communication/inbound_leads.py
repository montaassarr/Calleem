from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class InboundLead(BaseModel):
    id: str = Field(alias="_id")
    business_id: str
    source: str
    data: dict = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "lead_123",
                "business_id": "business_123",
                "source": "website_form",
                "data": {"name": "John", "phone": "+1234567890"}
            }
        }
    )
