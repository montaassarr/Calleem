"""
Models Package
==============
All Pydantic models for the AI Receptionist platform.

Simplified structure:
- tenant.py: Tenant/Business configuration
- user.py: User authentication (tenant = user)  
- appointment.py: Appointment scheduling
- service.py: Business services
- conversation.py: AI conversations/calls
- agent.py: Voice AI agent configuration
- business/: Business config & API keys
"""

# Tenant models
from models.tenant import (
    PlanTier, TenantStatus, PhoneProvider,
    TenantPhoneConfig, TenantSettings,
    TenantCreate, TenantUpdate, TenantInDB, TenantResponse
)

# User models (simplified - tenant = user)
from models.user import (
    UserCreate, UserUpdate, UserInDB, UserResponse,
    Token, TokenData, LoginRequest
)

# Appointment models
from models.appointment import (
    AppointmentStatus,
    AppointmentCreate, AppointmentUpdate, AppointmentInDB, AppointmentResponse
)

# Service models
from models.service import (
    ServiceCreate, ServiceUpdate, ServiceInDB, ServiceResponse
)

# Conversation models
from models.conversation import (
    MessageRole, ConversationIntent, Message, ConversationState,
    ConversationCreate, ConversationInDB, ConversationResponse
)

# Agent models - Commented out until agent.py is created
# from models.agent import (
#     AgentStatus, VoiceProvider, VoiceSettings, AgentTools,
#     AgentCreate, AgentUpdate, Agent, AgentResponse
# )

# Business config models
from models.business.business_config import BusinessConfig, BusinessConfigUpdate
from models.business.api_keys import ApiKey, ApiKeyCreate, ApiKeyResponse