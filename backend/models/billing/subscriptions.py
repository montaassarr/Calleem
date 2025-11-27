from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"

class Subscription(BaseModel):
    id: str = Field(alias="_id")
    business_id: str
    plan_id: str
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    current_period_end: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "sub_123",
                "business_id": "business_123",
                "plan_id": "plan_pro",
                "status": "active",
                "current_period_end": "2025-02-01T00:00:00"
            }
        }
    )
