from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class Client(BaseModel):
    id: str = Field(alias="_id")
    business_id: str
    name: str
    phone: str
    last_visit: Optional[datetime] = None
    visit_count: int = 0
    preferences: Dict[str, Any] = {}

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "client_789",
                "business_id": "business_123",
                "name": "Mohamed",
                "phone": "+216900000",
                "visit_count": 4,
                "preferences": {}
            }
        }
    )
