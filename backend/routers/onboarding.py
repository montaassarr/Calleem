"""
Onboarding Wizard Router
========================
Guides new users through required voice AI setup

Flow:
1. Check if user has completed onboarding
2. Provision managed LiveKit voice agent
3. Guide them to get API key
4. Validate and save key
5. Configure agent (prompts, tools, voice)
6. Deploy agent
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
import logging

from routers.users import get_current_user
from routers.api_keys import add_api_key, ApiKeyCreate, validate_api_key
from services.ai_proxy import ai_proxy
from database.mongo_config import get_database
from services.livekit_service import livekit_service
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
    provider: str = Field(..., description="Currently only 'livekit' is supported")


class VoiceKeySetup(BaseModel):
    """User adds voice provider API key"""
    provider: str
    api_key: str
    key_name: Optional[str] = None


class AgentConfiguration(BaseModel):
    """Agent configuration choices"""
    ai_engine: str = Field(default="groq", description="groq, openai, anthropic")
    use_own_ai_key: bool = Field(default=False)
    ai_key: Optional[str] = None
    
    voice_provider: str = Field(default="elevenlabs", description="elevenlabs, playht, azure")
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
    
    Returns detailed status of what's completed and what's missing:
    - Business information (name, phone, address, hours)
    - API keys (OpenAI, Groq, etc.)
    - Services configured
    - AI Agent created and deployed
    
    Used to automatically show onboarding modal on dashboard
    """
    tenant_id = str(current_user["tenant_id"])
    db = get_database()

    config = await db.business_config.find_one({"tenant_id": tenant_id}) or {}
    services_count = await db.services.count_documents({"tenant_id": tenant_id})
    has_business_name = bool(config.get("business_name"))
    has_business_details = bool(config.get("business_phone")) and bool(config.get("business_email"))
    has_services = services_count > 0
    agent = await db.agents.find_one({"tenant_id": tenant_id})
    agent_deployed = bool(agent and agent.get("status") == AgentStatus.ACTIVE.value)

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
        voice_provider="livekit",
        agent_deployed=agent_deployed,
        agent_id=str(agent["_id"]) if agent else None,
        missing_items=missing_items,
        is_new_user=not has_business_name or not has_business_details,
        completion_percentage=completion_percentage,
    )


@router.get("/onboarding/voice-providers")
async def get_voice_provider_options():
    """Return LiveKit as the managed voice provider option."""

    return {
        "title": "LiveKit Voice Agent",
        "description": "Voice calling is now powered by our managed LiveKit stack. No external provider setup required.",
        "providers": [
            {
                "id": "livekit",
                "name": "CallFlow LiveKit",
                "reason": "Managed voice agent with full control",
                "setup_url": None,
                "instructions": [
                    "1. Configure your prompt, model, and voice inside the dashboard",
                    "2. Use Test Call to try the shared sandbox",
                    "3. Add your own LLM/TTS keys when you're ready to go live"
                ],
                "recommended": True,
                "pricing": "Included"
            }
        ],
        "note": "Third-party voice providers are no longer required while we migrate fully to LiveKit.",
        "recommendation": "Use the built-in LiveKit stack."
    }


@router.post("/onboarding/setup-voice-key", status_code=status.HTTP_201_CREATED)
async def setup_voice_provider_key(
    data: VoiceKeySetup,
    current_user: dict = Depends(get_current_user)
):
    """LiveKit is managed by the platform, so this step just acknowledges completion."""

    return {
        "success": True,
        "message": "LiveKit is provisioned automatically. No external API key is required.",
        "provider": "livekit"
    }


@router.get("/onboarding/agent-options")
async def get_agent_configuration_options():
    """
    Step 3: Show agent configuration options
    """
    optional = ai_proxy.get_optional_providers()
    
    return {
        "title": "Configure Your AI Receptionist",
        "description": "Customize how your agent talks and what it can do. We provide the platform tools!",
        
        "ai_engines": {
            "title": "Choose AI Engine",
            "options": [
                {
                    "id": "groq",
                    "name": "Groq (Recommended)",
                    "description": "Super fast responses, included in your subscription",
                    "cost": "FREE (platform key)",
                    "recommended": True
                },
                {
                    "id": "openai",
                    "name": "OpenAI GPT-4",
                    "description": "Most advanced AI, but slower and more expensive",
                    "cost": "Use our key (FREE) or add your own",
                    "recommended": False
                },
                {
                    "id": "anthropic",
                    "name": "Anthropic Claude",
                    "description": "Great for complex conversations",
                    "cost": "Add your own key (optional)",
                    "recommended": False
                }
            ],
            "optional_providers": optional
        },
        
        "voice_options": {
            "title": "Choose Voice",
            "options": [
                {
                    "id": "default",
                    "name": "Default Voice",
                    "description": "Professional English voice, included",
                    "cost": "FREE",
                    "recommended": True
                },
                {
                    "id": "elevenlabs",
                    "name": "ElevenLabs Custom Voice",
                    "description": "Ultra-realistic voices, add your ElevenLabs key",
                    "cost": "Your ElevenLabs account",
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
            "title": "Enable Tools (Our n8n Workflows)",
            "description": "These are pre-built automations we provide as part of your subscription!",
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
                },
                {
                    "id": "cancel_appointment",
                    "name": "Cancel/Reschedule",
                    "description": "AI can modify existing appointments",
                    "enabled_by_default": True,
                    "included": True
                },
                {
                    "id": "send_confirmation",
                    "name": "Send Confirmations (WhatsApp)",
                    "description": "Automatic booking confirmations via WhatsApp",
                    "enabled_by_default": True,
                    "included": True
                },
                {
                    "id": "update_crm",
                    "name": "Update CRM",
                    "description": "Save customer info to your CRM",
                    "enabled_by_default": False,
                    "included": True
                }
            ]
        }
    }


@router.post("/onboarding/configure-agent")
async def configure_and_deploy_agent(
    config: AgentConfiguration,
    current_user: dict = Depends(get_current_user)
):
    """Finalize onboarding by auto-deploying the managed LiveKit agent."""

    tenant_id = str(current_user["tenant_id"])
    db = get_database()

    await ai_proxy.check_tenant_has_required_keys(tenant_id)

    agent_id = await _ensure_default_agent(db, tenant_id, config)
    await _enable_voice_agent(db, tenant_id)

    preview_session = livekit_service.build_preview_session(
        tenant_id=tenant_id,
        user_id=str(current_user.get("id", tenant_id)),
    )

    welcome_call = await _maybe_place_welcome_call(db, tenant_id, config, current_user)

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
        "message": "🎉 Your AI Receptionist is live!",
        "agent_id": agent_id,
        "preview_session": preview_session,
        "welcome_call": welcome_call,
        "voice_agent_enabled": True,
    }


PROMPT_LIBRARY: Dict[str, str] = {
    "friendly_receptionist": "You are Parker, a cheerful receptionist who answers every caller within two rings. Keep responses tight, confirm details, and summarize next steps before ending the call.",
    "professional_assistant": "You are Parker, a precise operations assistant. Speak clearly, confirm spelling of names, and ensure every booking includes date, time, and contact information.",
    "casual_helper": "You are Parker, a relaxed concierge for busy service businesses. Mirror the caller's energy, keep things light, and always check if they need anything else before hanging up.",
}

DEFAULT_WEBHOOKS = {
    "get_slots": "http://n8n:5678/webhook/getslots",
    "book": "http://n8n:5678/webhook/bookslots",
    "update": "http://n8n:5678/webhook/updateslots",
    "cancel": "http://n8n:5678/webhook/cancelslots",
}


async def _ensure_default_agent(db, tenant_id: str, config: AgentConfiguration) -> str:
    existing = await db.agents.find_one({"tenant_id": tenant_id})
    prompt = PROMPT_LIBRARY.get(config.prompt_template, PROMPT_LIBRARY["friendly_receptionist"])
    agent_payload = {
        "name": "Parker Receptionist",
        "tenant_id": tenant_id,
        "system_prompt": prompt,
        "voice_settings": {
            "provider": config.voice_provider,
            "voice_id": config.voice_id or "parker_default",
            "model": "eleven_monolingual_v1" if config.voice_provider == "elevenlabs" else None,
            "stability": 0.5,
            "similarity_boost": 0.75,
        },
        "llm_model": {
            "groq": "groq/llama3-70b",
            "openai": "gpt-4.1-mini",
            "anthropic": "claude-3-haiku",
        }.get(config.ai_engine, "groq/llama3-70b"),
        "llm_temperature": 0.4,
        "webhook_urls": DEFAULT_WEBHOOKS,
        "enabled_tools": config.enabled_tools,
        "status": AgentStatus.ACTIVE.value,
        "livekit_agent_name": livekit_service.config.agent_name,
        "livekit_queue": livekit_service.config.agent_queue,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "last_deployed_at": datetime.utcnow(),
        "total_calls": 0,
        "total_minutes": 0.0,
        "successful_calls": 0,
    }

    if existing:
        await db.agents.update_one(
            {"_id": existing["_id"]},
            {"$set": {**agent_payload, "created_at": existing.get("created_at", datetime.utcnow())}},
        )
        return str(existing["_id"])

    result = await db.agents.insert_one(agent_payload)
    return str(result.inserted_id)


async def _enable_voice_agent(db, tenant_id: str) -> None:
    await db.business_config.update_one(
        {"tenant_id": tenant_id},
        {
            "$set": {
                "tenant_id": tenant_id,
                "features_enabled.voice_agent": True,
                "updated_at": datetime.utcnow(),
            }
        },
        upsert=True,
    )


async def _maybe_place_welcome_call(db, tenant_id: str, config: AgentConfiguration, current_user: dict) -> Dict[str, Any]:
    if not config.send_welcome_call:
        return {"status": "skipped", "reason": "disabled"}

    business = await db.business_config.find_one({"tenant_id": tenant_id}) or {}
    target = config.welcome_call_number or business.get("business_phone") or current_user.get("phone")
    if not target:
        return {"status": "skipped", "reason": "missing_target"}

    caller = await db.voice_numbers.find_one(
        {"tenant_id": tenant_id, "status": {"$in": ["active", "provisioning"]}},
        sort=[("status", 1), ("created_at", -1)],
    )
    if not caller:
        return {"status": "skipped", "reason": "no_livekit_number"}

    try:
        call = await livekit_service.start_outbound_call(
            tenant_id=tenant_id,
            to_number=target,
            from_number=caller.get("phone_number"),
            metadata={"kind": "welcome-test"},
        )
        return call
    except HTTPException as exc:
        return {"status": "failed", "reason": exc.detail}
    except Exception as exc:  # pragma: no cover
        logger.error("Welcome call failed: %s", exc)
        return {"status": "failed", "reason": "unexpected_error"}


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
