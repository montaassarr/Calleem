import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query
from pydantic import BaseModel
from datetime import datetime

from services.vapi_service import vapi_service
from routers.users import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Assistants"])


# ===== PYDANTIC MODELS =====

class VoiceConfig(BaseModel):
    provider: str = "11labs"
    voice_id: str
    voice_name: Optional[str] = None
    speed: float = 1.0
    pitch: Optional[float] = None
    stability: Optional[float] = None
    clarity: Optional[float] = None

class PersonalityConfig(BaseModel):
    system_prompt: str
    first_message: str
    tone: Optional[str] = "professional"  # professional, friendly, casual
    response_style: Optional[str] = "concise"  # concise, detailed
    temperature: float = 0.7

class AssistantConfig(BaseModel):
    name: Optional[str] = None
    voice: Optional[str] = "jennifer"
    voice_provider: str = "11labs"
    voice_speed: float = 1.0
    instructions: str
    first_message: Optional[str] = None
    company_name: Optional[str] = None
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 525
    transcriber_provider: str = "deepgram"
    transcriber_model: str = "nova-2"
    transcriber_language: str = "en"
    tools: Optional[List[Dict[str, Any]]] = None

class AssistantResponse(BaseModel):
    assistant_id: str
    name: Optional[str] = None
    configured: bool = True
    voice: Optional[Dict[str, Any]] = None
    model: Optional[Dict[str, Any]] = None
    first_message: Optional[str] = None
    created: bool = False
    updated: bool = False

class ToolEnableRequest(BaseModel):
    tool_id: str
    config: Optional[Dict[str, Any]] = None

class KnowledgeBaseDocument(BaseModel):
    id: str
    name: str
    type: str
    size: Optional[int] = None
    status: str = "processed"
    created_at: Optional[datetime] = None

class FAQEntry(BaseModel):
    question: str
    answer: str

class CallAnalytics(BaseModel):
    total_calls: int
    total_duration_minutes: float
    avg_duration_seconds: float
    total_cost_cents: int
    calls_by_status: Dict[str, int]
    calls_by_day: List[Dict[str, Any]]


# ===== ASSISTANT CRUD =====

from services.assistant_service import get_assistant_service, AssistantService

@router.get("/assistant/me")
async def get_my_assistant(
    current_user: dict = Depends(get_current_user),
    service: AssistantService = Depends(get_assistant_service)
):
    """Get current user's tenant assistant configuration"""
    tenant_id = str(current_user.get("tenant_id"))
    if not tenant_id:
        raise HTTPException(400, "User has no tenant")
    
    return await service.get_assistant(tenant_id)

@router.post("/assistant/me", response_model=AssistantResponse)
async def create_my_assistant(
    config: AssistantConfig,
    current_user: dict = Depends(get_current_user),
    service: AssistantService = Depends(get_assistant_service)
):
    """Create assistant for current user's tenant"""
    tenant_id = str(current_user.get("tenant_id"))
    if not tenant_id:
        raise HTTPException(400, "User has no tenant")
    
    result = await service.create_assistant(tenant_id, config)
    return AssistantResponse(**result)

@router.put("/assistant/me", response_model=AssistantResponse)
async def update_my_assistant(
    config: AssistantConfig,
    current_user: dict = Depends(get_current_user),
    service: AssistantService = Depends(get_assistant_service)
):
    """Update current user's tenant assistant"""
    tenant_id = str(current_user.get("tenant_id"))
    if not tenant_id:
        raise HTTPException(400, "User has no tenant")
    
    result = await service.update_assistant(tenant_id, config)
    return AssistantResponse(**result)

@router.delete("/assistant/me")
async def delete_my_assistant(
    current_user: dict = Depends(get_current_user),
    service: AssistantService = Depends(get_assistant_service)
):
    """Delete current user's tenant assistant"""
    tenant_id = str(current_user.get("tenant_id"))
    if not tenant_id:
        raise HTTPException(400, "User has no tenant")
    
    success = await service.delete_assistant(tenant_id)
    return {"success": True, "message": "Assistant deleted"}


# ===== VOICE CONFIGURATION =====

@router.get("/assistant/me/voice")
async def get_voice_settings(
    current_user: dict = Depends(get_current_user),
    service: AssistantService = Depends(get_assistant_service)
):
    """Get assistant voice settings"""
    tenant_id = str(current_user.get("tenant_id"))
    return await service.get_voice_settings(tenant_id)

@router.put("/assistant/me/voice")
async def update_voice_settings(
    voice_config: VoiceConfig,
    current_user: dict = Depends(get_current_user),
    service: AssistantService = Depends(get_assistant_service)
):
    """Update assistant voice settings"""
    tenant_id = str(current_user.get("tenant_id"))
    return await service.update_voice_settings(tenant_id, voice_config)

@router.get("/voice-providers")
async def list_voice_providers(current_user: dict = Depends(get_current_user)):
    """Get available voice providers and their voices"""
    # This calls vapi directly, could be moved to service too but is simple enough
    providers = await vapi_service.get_voice_providers()
    return {"providers": providers}

@router.post("/assistant/me/voice/preview")
async def preview_voice(
    text: str = Query(..., description="Text to preview"),
    voice_id: str = Query(...),
    provider: str = Query(default="11labs"),
    current_user: dict = Depends(get_current_user)
):
    """Generate voice preview audio"""
    # For now, return instructions to use Vapi's built-in preview
    return {
        "message": "Use Vapi dashboard or web SDK for voice preview",
        "voice_id": voice_id,
        "provider": provider,
        "text": text
    }


# ===== PERSONALITY CONFIGURATION =====

@router.get("/assistant/me/personality")
async def get_personality_settings(
    current_user: dict = Depends(get_current_user),
    service: AssistantService = Depends(get_assistant_service)
):
    """Get assistant personality/system prompt settings"""
    tenant_id = str(current_user.get("tenant_id"))
    return await service.get_personality_settings(tenant_id)

@router.put("/assistant/me/personality")
async def update_personality_settings(
    personality: PersonalityConfig,
    current_user: dict = Depends(get_current_user),
    service: AssistantService = Depends(get_assistant_service)
):
    """Update assistant personality/system prompt"""
    tenant_id = str(current_user.get("tenant_id"))
    return await service.update_personality_settings(tenant_id, personality)



# ===== KNOWLEDGE BASE MANAGEMENT =====

@router.get("/assistant/me/knowledge-base")
async def get_knowledge_base(
    current_user: dict = Depends(get_current_user),
    service: AssistantService = Depends(get_assistant_service)
):
    """Get knowledge base documents for the assistant"""
    tenant_id = str(current_user.get("tenant_id"))
    return await service.get_knowledge_base(tenant_id)


@router.post("/assistant/me/knowledge-base/upload")
async def upload_knowledge_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    service: AssistantService = Depends(get_assistant_service)
):
    """Upload a document to knowledge base"""
    tenant_id = str(current_user.get("tenant_id"))
    content = await file.read()
    
    return await service.upload_knowledge_document(
        tenant_id, 
        content, 
        file.filename, 
        file.content_type
    )


@router.delete("/assistant/me/knowledge-base/{doc_id}")
async def delete_knowledge_document(
    doc_id: str,
    current_user: dict = Depends(get_current_user),
    service: AssistantService = Depends(get_assistant_service)
):
    """Delete a knowledge base document"""
    tenant_id = str(current_user.get("tenant_id"))
    await service.delete_knowledge_document(tenant_id, doc_id)
    return {"success": True, "message": "Document deleted"}


@router.post("/assistant/me/knowledge-base/faq")
async def add_faq_entries(
    faqs: List[FAQEntry],
    current_user: dict = Depends(get_current_user),
    service: AssistantService = Depends(get_assistant_service)
):
    """Add FAQ entries to knowledge base"""
    tenant_id = str(current_user.get("tenant_id"))
    added_count = await service.add_faq_entries(tenant_id, faqs)
    return {"success": True, "added": added_count}


# ===== TOOLS MANAGEMENT =====

@router.get("/tools/built-in")
async def list_built_in_tools(
    current_user: dict = Depends(get_current_user),
    service: AssistantService = Depends(get_assistant_service)
):
    """Get available built-in tools"""
    tools = await service.get_built_in_tools()
    return {"tools": tools}


@router.get("/assistant/me/tools")
async def get_enabled_tools(
    current_user: dict = Depends(get_current_user),
    service: AssistantService = Depends(get_assistant_service)
):
    """Get tools enabled for the assistant"""
    tenant_id = str(current_user.get("tenant_id"))
    tools = await service.get_enabled_tools(tenant_id)
    return {"tools": tools}


@router.post("/assistant/me/tools/{tool_id}/enable")
async def enable_tool(
    tool_id: str,
    config: Optional[Dict[str, Any]] = None,
    current_user: dict = Depends(get_current_user),
    service: AssistantService = Depends(get_assistant_service)
):
    """Enable a built-in tool for the assistant"""
    tenant_id = str(current_user.get("tenant_id"))
    return await service.enable_tool(tenant_id, tool_id)


@router.delete("/assistant/me/tools/{tool_id}")
async def disable_tool(
    tool_id: str,
    current_user: dict = Depends(get_current_user),
    service: AssistantService = Depends(get_assistant_service)
):
    """Disable a tool for the assistant"""
    tenant_id = str(current_user.get("tenant_id"))
    return await service.disable_tool(tenant_id, tool_id)


# ===== ANALYTICS & CONVERSATIONS =====

@router.get("/assistant/me/analytics/calls")
async def get_call_analytics(
    days: int = Query(default=30, ge=1, le=365),
    current_user: dict = Depends(get_current_user),
    service: AssistantService = Depends(get_assistant_service)
):
    """Get call analytics for the assistant"""
    tenant_id = str(current_user.get("tenant_id"))
    return await service.get_call_analytics(tenant_id, days)


@router.get("/assistant/me/conversations")
async def list_conversations(
    limit: int = Query(default=50, ge=1, le=200),
    skip: int = Query(default=0, ge=0),
    current_user: dict = Depends(get_current_user),
    service: AssistantService = Depends(get_assistant_service)
):
    """List conversation/call history"""
    tenant_id = str(current_user.get("tenant_id"))
    return await service.list_conversations(tenant_id, limit, skip)


@router.get("/assistant/me/conversations/{call_id}")
async def get_conversation_details(
    call_id: str,
    current_user: dict = Depends(get_current_user),
    service: AssistantService = Depends(get_assistant_service)
):
    """Get full conversation details including transcript"""
    tenant_id = str(current_user.get("tenant_id"))
    return await service.get_conversation_details(tenant_id, call_id)


# ===== TESTING =====

@router.post("/assistant/me/test")
async def test_assistant(
    current_user: dict = Depends(get_current_user),
    service: AssistantService = Depends(get_assistant_service)
):
    """Get test configuration for the assistant"""
    tenant_id = str(current_user.get("tenant_id"))
    return await service.get_test_config(tenant_id)
