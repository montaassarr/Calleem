from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class WhatsAppSettings(BaseModel):
    id: str = Field(alias="_id")
    business_id: str
    phone_number_id: Optional[str] = None
    access_token: Optional[str] = None
    verify_token: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "wa_123",
                "business_id": "business_123",
                "phone_number_id": "123456789",
                "access_token": "EAA..."
            }
        }
    )
