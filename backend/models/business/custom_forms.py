from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any

class FormField(BaseModel):
    name: str
    type: str
    required: bool = False
    options: List[str] = []

class CustomForm(BaseModel):
    id: str = Field(alias="_id")
    business_id: str
    name: str
    fields: List[FormField] = []

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "form_123",
                "business_id": "business_123",
                "name": "Intake Form",
                "fields": [
                    {"name": "allergies", "type": "text", "required": False}
                ]
            }
        }
    )
