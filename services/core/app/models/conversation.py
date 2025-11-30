"""
Conversation Data Model
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Message role enumeration"""
    CLIENT = "client"
    AI = "ai"
    SYSTEM = "system"


class ConversationIntent(str, Enum):
    """Conversation intent enumeration"""
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
    """Individual message in a conversation"""
    role: MessageRole
    text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "client",
                "text": "Hi, I want to book a haircut",
                "timestamp": "2025-11-13T10:00:00",
                "metadata": {"twilio_message_sid": "SM123456"}
            }
        }


class ConversationState(BaseModel):
    """Current state of the conversation"""
    intent: ConversationIntent = ConversationIntent.UNKNOWN
    collected_info: Dict[str, Any] = Field(default_factory=dict)
    next_question: Optional[str] = None
    completed: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "intent": "book_appointment",
                "collected_info": {
                    "client_name": "John Doe",
                    "service": "Haircut",
                    "preferred_date": "tomorrow"
                },
                "next_question": "What time works best for you?",
                "completed": False
            }
        }


class ConversationBase(BaseModel):
    """Base conversation model"""
    phone_number: str = Field(..., pattern=r'^\+?1?\d{9,15}$')
    messages: List[Message] = Field(default_factory=list)
    state: ConversationState = Field(default_factory=ConversationState)


class ConversationCreate(ConversationBase):
    """Model for creating a new conversation"""
    pass


class ConversationInDB(ConversationBase):
    """Model for conversation stored in database"""
    id: str = Field(alias="_id")
    conversation_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    appointment_id: Optional[str] = None
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "conversation_id": "conv_123456",
                "phone_number": "+1234567890",
                "messages": [
                    {
                        "role": "client",
                        "text": "Hi, I want to book a haircut",
                        "timestamp": "2025-11-13T10:00:00"
                    },
                    {
                        "role": "ai",
                        "text": "Sure! What's your name?",
                        "timestamp": "2025-11-13T10:00:05"
                    }
                ],
                "state": {
                    "intent": "book_appointment",
                    "collected_info": {"service": "Haircut"},
                    "completed": False
                },
                "created_at": "2025-11-13T10:00:00",
                "updated_at": "2025-11-13T10:01:00"
            }
        }


class ConversationResponse(BaseModel):
    """Model for conversation API response"""
    id: str
    conversation_id: str
    phone_number: str
    messages: List[Message]
    state: ConversationState
    appointment_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "conversation_id": "conv_123456",
                "phone_number": "+1234567890",
                "messages": [],
                "state": {"intent": "book_appointment", "completed": False},
                "created_at": "2025-11-13T10:00:00",
                "updated_at": "2025-11-13T10:00:00"
            }
        }


class ConversationSummary(BaseModel):
    """Summary of a conversation for dashboard display"""
    conversation_id: str
    phone_number: str
    intent: ConversationIntent
    message_count: int
    last_message: str
    last_message_time: datetime
    completed: bool
    appointment_id: Optional[str] = None
