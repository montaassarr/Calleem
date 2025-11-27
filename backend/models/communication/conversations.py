from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    CLIENT = "client"
    AI = "ai"
    SYSTEM = "system"

class ConversationIntent(str, Enum):
    GREETING = "greeting"
    BOOK_APPOINTMENT = "book_appointment"
    UPDATE_APPOINTMENT = "update_appointment"
    CANCEL_APPOINTMENT = "cancel_appointment"
    CHECK_AVAILABILITY = "check_availability"
    SERVICE_INFO = "service_info"
    BUSINESS_INFO = "business_info"
    GENERAL_QUESTION = "general_question"
    UNKNOWN = "unknown"

class Message(BaseModel):
    role: MessageRole
    text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None

class ConversationState(BaseModel):
    intent: ConversationIntent = ConversationIntent.UNKNOWN
    collected_info: Dict[str, Any] = Field(default_factory=dict)
    next_question: Optional[str] = None
    completed: bool = False

class Conversation(BaseModel):
    id: str = Field(alias="_id")
    conversation_id: str
    business_id: str
    tenant_id: Optional[str] = None
    client_phone: str # Mapped from phone_number
    phone_number: str # Keeping for backward compatibility
    source: str = "whatsapp"
    messages: List[Message] = [] # Using typed Message list
    state: ConversationState = Field(default_factory=ConversationState)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    appointment_id: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "conv_001",
                "conversation_id": "conv_123456",
                "business_id": "business_123",
                "tenant_id": "business_123",
                "client_phone": "+2169000000",
                "phone_number": "+2169000000",
                "source": "whatsapp",
                "messages": [],
                "last_updated": "2025-01-02T10:00:00"
            }
        }
    )

class ConversationInDB(Conversation):
    pass

class ConversationResponse(Conversation):
    pass

class ConversationSummary(BaseModel):
    id: str
    conversation_id: str
    client_phone: str
    last_message: Optional[str] = None
    last_updated: datetime
    message_count: int
    intent: Optional[ConversationIntent] = None
    completed: bool = False
    appointment_id: Optional[str] = None
