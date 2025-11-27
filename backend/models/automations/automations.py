from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any

class Automation(BaseModel):
    id: str = Field(alias="_id")
    business_id: str
    name: str
    trigger: Dict[str, Any]
    actions: List[Dict[str, Any]]
    active: bool = True

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "auto_123",
                "business_id": "business_123",
                "name": "New Lead Alert",
                "trigger": {"type": "new_lead"},
                "actions": [{"type": "send_email", "to": "owner@example.com"}],
                "active": True
            }
        }
    )
