from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class VapiSettings(BaseModel):
    id: str = Field(alias="_id")
    business_id: str
    api_key: Optional[str] = None
    assistant_id: Optional[str] = None
    phone_number_id: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "vapi_123",
                "business_id": "business_123",
                "api_key": "sk_...",
                "assistant_id": "asst_..."
            }
        }
    )
