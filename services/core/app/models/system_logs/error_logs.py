from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any

class ErrorLog(BaseModel):
    id: str = Field(alias="_id")
    business_id: Optional[str] = None
    error_code: str
    message: str
    stack_trace: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "err_123",
                "business_id": "business_123",
                "error_code": "DB_CONN_FAIL",
                "message": "Connection timeout",
                "stack_trace": "..."
            }
        }
    )
