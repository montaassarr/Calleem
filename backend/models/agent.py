"""
Voice Agent Data Model
Represents a voice AI agent that can handle calls for a business
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum


class AgentStatus(str, Enum):
    """Agent status enumeration"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"


class VoiceProvider(str, Enum):
    """Voice provider enumeration"""
    ELEVENLABS = "elevenlabs"
    OPENAI = "openai"
    DEEPGRAM = "deepgram"
    CARTESIA = "cartesia"


class WebhookUrls(BaseModel):
    """Webhook URLs for agent tool calling"""
    get_slots: str = "http://localhost:5678/webhook/getslots"
    book: str = "http://localhost:5678/webhook/bookslots"
    update: str = "http://localhost:5678/webhook/updateslots"
    cancel: str = "http://localhost:5678/webhook/cancelslots"


class VoiceSettings(BaseModel):
    """Voice configuration for the agent"""
    provider: VoiceProvider = VoiceProvider.CARTESIA
    voice_id: str = "79a125e8-cd45-4c13-8a67-188112f4dd22"  # Default Cartesia voice
    model: Optional[str] = None  # For providers that support multiple models
    stability: Optional[float] = 0.5
    similarity_boost: Optional[float] = 0.75


class AgentBase(BaseModel):
    """Base agent model"""
    name: str = Field(..., min_length=2, max_length=100, description="Agent name (e.g., 'Sarah - Hair Salon Receptionist')")
    tenant_id: str = Field(..., description="Organization/Business ID")
    system_prompt: str = Field(..., min_length=10, description="System prompt for the agent")
    
    # Voice configuration
    voice_settings: VoiceSettings
    
    # LLM configuration
    llm_model: str = Field(default="llama-3.3-70b-versatile", description="LLM model to use (e.g., llama-3.3-70b-versatile for Groq, gpt-4 for OpenAI)")
    llm_temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    
    # Greeting configuration
    greeting_enabled: bool = Field(default=True, description="Whether to play a greeting message when user connects")
    greeting_message: str = Field(default="Hello! I'm your AI receptionist. How can I help you today?", description="Greeting message to play when user connects")
    
    # Webhook configuration
    webhook_urls: WebhookUrls = Field(default_factory=WebhookUrls)
    
    # Optional fields
    avatar_url: Optional[str] = None
    phone_number: Optional[str] = None
    description: Optional[str] = None
    
    # Status
    status: AgentStatus = AgentStatus.DRAFT


class AgentCreate(AgentBase):
    """Model for creating a new agent"""
    pass


class AgentUpdate(BaseModel):
    """Model for updating an agent"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    system_prompt: Optional[str] = Field(None, min_length=10)
    voice_settings: Optional[VoiceSettings] = None
    llm_model: Optional[str] = None
    llm_temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    greeting_enabled: Optional[bool] = None
    greeting_message: Optional[str] = None
    webhook_urls: Optional[WebhookUrls] = None
    avatar_url: Optional[str] = None
    phone_number: Optional[str] = None
    description: Optional[str] = None
    status: Optional[AgentStatus] = None


class Agent(AgentBase):
    """Agent model with database fields"""
    id: str = Field(alias="_id")

    # LiveKit metadata
    livekit_agent_name: str = Field(default="Parker_165")
    livekit_queue: str = Field(default="voice-agents")
    livekit_room_template: Optional[str] = Field(default=None)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_deployed_at: Optional[datetime] = None
    
    # Analytics
    total_calls: int = 0
    total_minutes: float = 0.0
    successful_calls: int = 0
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "agent_123",
                "name": "Sarah - Hair Salon Receptionist",
                "tenant_id": "tenant_456",
                "system_prompt": "You are Sarah, a friendly receptionist...",
                "voice_settings": {
                    "provider": "elevenlabs",
                    "voice_id": "21m00Tcm4TlvDq8ikWAM",
                    "stability": 0.5,
                    "similarity_boost": 0.75
                },
                "llm_model": "gpt-4",
                "webhook_urls": {
                    "get_slots": "http://localhost:5678/webhook/getslots",
                    "book": "http://localhost:5678/webhook/bookslots",
                    "update": "http://localhost:5678/webhook/updateslots",
                    "cancel": "http://localhost:5678/webhook/cancelslots"
                },
                "status": "active",
                "livekit_agent_name": "Parker_165",
                "created_at": "2025-11-30T10:00:00"
            }
        }
    )


class AgentResponse(BaseModel):
    """Model for agent API response"""
    id: str
    name: str
    tenant_id: str
    system_prompt: str
    voice_settings: VoiceSettings
    llm_model: str
    llm_temperature: float
    greeting_enabled: Optional[bool] = True
    greeting_message: Optional[str] = None
    webhook_urls: WebhookUrls
    avatar_url: Optional[str] = None
    phone_number: Optional[str] = None
    description: Optional[str] = None
    status: AgentStatus
    livekit_agent_name: str
    livekit_queue: str
    livekit_room_template: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_deployed_at: Optional[datetime] = None
    total_calls: int = 0
    total_minutes: float = 0.0
    successful_calls: int = 0
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "agent_123",
                "name": "Sarah - Hair Salon Receptionist",
                "tenant_id": "tenant_456",
                "system_prompt": "You are Sarah...",
                "voice_settings": {
                    "provider": "elevenlabs",
                    "voice_id": "21m00Tcm4TlvDq8ikWAM"
                },
                "llm_model": "gpt-4",
                "status": "active",
                "livekit_agent_name": "Parker_165",
                "total_calls": 150
            }
        }
    )
