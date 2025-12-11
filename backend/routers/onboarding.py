"""
Onboarding Wizard Router
========================
Guides new users through required voice AI setup (Vapi Edition)

Flow:
1. Check if user has completed onboarding
2. Provision Vapi voice agent
3. Configure agent (prompts, tools, voice)
4. Deploy agent
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
import logging

from routers.users import get_current_user
from database.mongo_config import get_database
from services.vapi_service import vapi_service
from models.agent import AgentStatus

logger = logging.getLogger(__name__)

router = APIRouter()


class OnboardingStatus(BaseModel):
    """User's onboarding status - AUTOMATED"""
    completed: bool
    current_step: int  # 1-7
    has_voice_provider: bool
    voice_provider: Optional[str] = None
    agent_deployed: bool = False
    agent_id: Optional[str] = None
    missing_items: List[str] = []  # What's not completed yet
    is_new_user: bool = False  # True if business info not filled
    completion_percentage: int = 0  # 0-100%


class VoiceProviderChoice(BaseModel):
    """User selects voice provider"""
    provider: str = Field(..., description="Currently 'vapi' is the standard")


class VoiceKeySetup(BaseModel):
    """User adds voice provider API key"""
    provider: str
    api_key: str
    key_name: Optional[str] = None


class AgentConfiguration(BaseModel):
    """Agent configuration choices"""
    ai_engine: str = Field(default="gpt-4o-mini", description="llm model")
    
    voice_provider: str = Field(default="elevenlabs", description="Currently managed by Vapi")
    voice_id: Optional[str] = Field(default=None, description="Specific voice ID if custom")
    
    prompt_template: str = Field(default="friendly_receptionist")
    
    enabled_tools: List[str] = Field(
        default=["book_appointment", "check_availability", "send_confirmation"]
    )
    welcome_call_number: Optional[str] = Field(default=None, description="Phone number for optional welcome test call")
    send_welcome_call: bool = Field(default=True)


@router.get("/onboarding/status", response_model=OnboardingStatus)
async def get_onboarding_status(current_user: dict = Depends(get_current_user)):
    """
    Check if user has completed onboarding - AUTOMATED CHECK
    """
    tenant_id = str(current_user["tenant_id"])
    db = get_database()

    config = await db.business_config.find_one({"tenant_id": tenant_id}) or {}
    services_count = await db.services.count_documents({"tenant_id": tenant_id})
    has_business_name = bool(config.get("business_name"))
    has_business_details = bool(config.get("business_phone")) and bool(config.get("business_email"))
    has_services = services_count > 0
    # Check for Vapi assistant ID in business config or agents collection
    # In Vapi model, we often store assistant_id in business_config or a separate agents doc.
    # We'll check 'agents' collection first.
    agent = await db.agents.find_one({"tenant_id": tenant_id})
    agent_deployed = bool(agent and agent.get("status") == "active")

    missing_items: List[str] = []
    if not has_business_name:
        missing_items.append("business_profile")
    if not has_business_details:
        missing_items.append("business_details")
    if not has_services:
        missing_items.append("services")
    if not config.get("features_enabled", {}).get("voice_agent"):
        missing_items.append("voice_agent_toggle")
    if not agent:
        missing_items.append("agent")
    elif not agent_deployed:
        missing_items.append("agent_deployment")

    completed = len(missing_items) == 0
    step_map = {
        "business_profile": 1,
        "business_details": 2,
        "voice_agent_toggle": 3,
        "services": 4,
        "agent": 5,
        "agent_deployment": 6,
    }
    current_step = 7 if completed else step_map.get(missing_items[0], 1)
    completion_percentage = 100 if completed else int(((6 - min(len(missing_items), 6)) / 6) * 100)

    return OnboardingStatus(
        completed=completed,
        current_step=current_step,
        has_voice_provider=True,
        voice_provider="vapi",
        agent_deployed=agent_deployed,
        agent_id=str(agent["_id"]) if agent else None,
        missing_items=missing_items,
        is_new_user=not has_business_name or not has_business_details,
        completion_percentage=completion_percentage,
    )


@router.get("/onboarding/voice-providers")
async def get_voice_provider_options():
    """Return Vapi as the managed voice provider option."""

    return {
        "title": "Vapi Voice AI",
        "description": "Enterprise-grade voice AI powered by Vapi. Low latency, realistic voices.",
        "providers": [
            {
                "id": "vapi",
                "name": "Vapi (Managed)",
                "reason": "Included in Platform",
                "setup_url": None,
                "instructions": [
                    "1. Configure your agent settings",
                    "2. We provision a Vapi assistant for you",
                    "3. Manage phone numbers directly in the dashboard"
                ],
                "recommended": True,
                "pricing": "Included"
            }
        ],
        "note": "We have migrated to Vapi for superior voice quality.",
        "recommendation": "Use Vapi."
    }


@router.post("/onboarding/setup-voice-key", status_code=status.HTTP_201_CREATED)
async def setup_voice_provider_key(
    data: VoiceKeySetup,
    current_user: dict = Depends(get_current_user)
):
    """Vapi is managed by the platform, so this step just acknowledges completion."""

    return {
        "success": True,
        "message": "Vapi is provisioned automatically. No external API key is required.",
        "provider": "vapi"
    }


@router.get("/onboarding/agent-options")
async def get_agent_configuration_options():
    """
    Step 3: Show agent configuration options
    """
    
    return {
        "title": "Configure Your AI Receptionist",
        "description": "Customize how your agent talks and what it can do.",
        
        "ai_engines": {
            "title": "Choose AI Engine",
            "options": [
                {
                    "id": "gpt-4o-mini",
                    "name": "GPT-4o Mini",
                    "description": "Fast & Intelligent (Standard)",
                    "cost": "Included",
                    "recommended": True
                },
                {
                    "id": "gpt-4",
                    "name": "GPT-4",
                    "description": "Most capable, slightly slower",
                    "cost": "Premium",
                    "recommended": False
                }
            ]
        },
        
        "voice_options": {
            "title": "Choose Voice",
            "options": [
                {
                    "id": "jennifer",
                    "name": "Jennifer (US Female)",
                    "description": "Professional and clear",
                    "cost": "Free",
                    "recommended": True
                },
                {
                    "id": "ryan",
                    "name": "Ryan (US Male)",
                    "description": "Deep and calm",
                    "cost": "Free",
                    "recommended": False
                }
            ]
        },
        
        "prompt_templates": {
            "title": "Conversation Style",
            "options": [
                {
                    "id": "friendly_receptionist",
                    "name": "Friendly Receptionist",
                    "description": "Warm, welcoming, and professional",
                    "example": "Hi there! Thanks for calling. How can I help you today?"
                },
                {
                    "id": "professional_assistant",
                    "name": "Professional Assistant",
                    "description": "Formal and efficient",
                    "example": "Good morning. Thank you for calling. How may I assist you?"
                },
                {
                    "id": "casual_helper",
                    "name": "Casual Helper",
                    "description": "Relaxed and conversational",
                    "example": "Hey! What can I do for you today?"
                }
            ]
        },
        
        "available_tools": {
            "title": "Enable Tools (n8n Workflows)",
            "description": "These are pre-built automations!",
            "tools": [
                {
                    "id": "book_appointment",
                    "name": "Book Appointments",
                    "description": "AI can check calendar and book appointments",
                    "enabled_by_default": True,
                    "included": True
                },
                {
                    "id": "check_availability",
                    "name": "Check Availability",
                    "description": "AI can check open time slots",
                    "enabled_by_default": True,
                    "included": True
                }
            ]
        }
    }


PROMPT_LIBRARY: Dict[str, str] = {
    "friendly_receptionist": "You are a cheerful receptionist who answers every caller within two rings. Keep responses tight, confirm details, and summarize next steps before ending the call.",
    "professional_assistant": "You are a precise operations assistant. Speak clearly, confirm spelling of names, and ensure every booking includes date, time, and contact information.",
    "casual_helper": "You are a relaxed concierge for busy service businesses. Mirror the caller's energy, keep things light, and always check if they need anything else before hanging up.",
}


@router.post("/onboarding/configure-agent")
async def configure_and_deploy_agent(
    config: AgentConfiguration,
    current_user: dict = Depends(get_current_user)
):
    """Finalize onboarding by auto-deploying the managed Vapi agent."""

    tenant_id = str(current_user["tenant_id"])
    company_name = str(current_user.get("business_name", "Your Business"))
    db = get_database()

    # 1. Create agent in Vapi
    instructions = PROMPT_LIBRARY.get(config.prompt_template, PROMPT_LIBRARY["friendly_receptionist"])
    
    try:
        if not vapi_service.is_configured():
             logger.warning("Vapi not configured, skipping actual Vapi creation for onboarding test")
             agent_details = {"assistant_id": "mock_vapi_id", "created": False}
        else:
            agent_details = await vapi_service.create_assistant(
                tenant_id=tenant_id,
                company_name=company_name,
                instructions=instructions,
                voice=config.voice_id or "jennifer",
                model=config.ai_engine
            )
    except Exception as e:
        logger.error(f"Vapi creation failed: {e}")
        raise HTTPException(500, f"Failed to provision voice agent: {str(e)}")

    # 2. Save agent to DB
    existing = await db.agents.find_one({"tenant_id": tenant_id})
    agent_payload = {
        "name": f"{company_name} - Receptionist",
        "tenant_id": tenant_id,
        "vapi_assistant_id": agent_details.get("assistant_id"),
        "provider": "vapi",
        "system_prompt": instructions,
        "voice_id": config.voice_id or "jennifer",
        "llm_model": config.ai_engine,
        "status": "active",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    if existing:
        await db.agents.update_one(
            {"_id": existing["_id"]},
            {"$set": agent_payload}
        )
        agent_id = str(existing["_id"])
    else:
        result = await db.agents.insert_one(agent_payload)
        agent_id = str(result.inserted_id)

    # 3. Enable feature flag
    await db.business_config.update_one(
        {"tenant_id": tenant_id},
        {
            "$set": {
                "features_enabled.voice_agent": True,
                "updated_at": datetime.utcnow(),
            }
        },
        upsert=True,
    )

    # 4. Mark onboarding complete
    await db.onboarding_status.update_one(
        {"tenant_id": tenant_id},
        {
            "$set": {
                "completed": True,
                "completed_at": datetime.utcnow(),
                "completed_by": str(current_user.get("id")),
            }
        },
        upsert=True,
    )
    
    await db.users.update_many(
        {"tenant_id": tenant_id},
        {
            "$set": {
                "onboarding_skipped": False,
                "onboarding_completed_at": datetime.utcnow(),
            }
        },
    )

    return {
        "success": True,
        "message": "🎉 Your Vapi AI Receptionist is live!",
        "agent_id": agent_id,
        "vapi_assistant_id": agent_details.get("assistant_id"),
        "voice_agent_enabled": True,
    }


@router.post("/onboarding/skip")
async def skip_onboarding(current_user: dict = Depends(get_current_user)):
    """
    Allow user to skip onboarding (but they won't be able to use voice features)
    """
    tenant_id = str(current_user["tenant_id"])
    
    db = get_database()
    await db.users.update_one(
        {"tenant_id": tenant_id},
        {"$set": {"onboarding_skipped": True, "onboarding_skipped_at": datetime.utcnow()}}
    )
    
    return {
        "success": True,
        "message": "⚠️ Onboarding skipped. You can complete it anytime from Settings.",
        "warning": "Voice features won't work until you add a voice provider API key."
    }
