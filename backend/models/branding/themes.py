from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class Theme(BaseModel):
    id: str = Field(alias="_id")
    business_id: str
    primary_color: str = "#000000"
    secondary_color: str = "#ffffff"
    logo_url: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "theme_123",
                "business_id": "business_123",
                "primary_color": "#ff0000",
                "logo_url": "https://example.com/logo.png"
            }
        }
    )
