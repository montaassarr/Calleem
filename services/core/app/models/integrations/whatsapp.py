from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class WhatsAppIntegration(BaseModel):
    id: str = Field(alias="_id")
    business_id: str
    phone_number_id: str
    waba_id: str
    active: bool = True

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "wa_int_123",
                "business_id": "business_123",
                "phone_number_id": "123456",
                "waba_id": "789012",
                "active": True
            }
        }
    )
