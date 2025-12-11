"""
Comprehensive Assistant Management Router
Handles all assistant configuration: voice, personality, knowledge base, tools, analytics
"""

import os
import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Request, Header, BackgroundTasks, File, UploadFile, Query
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

from services.vapi_service import vapi_service
from routers.users import get_current_user
from database.mongo_config import get_database
from bson import ObjectId

logger = logging.getLogger(__name__)

router = APIRouter(tags=["assistant"])


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

@router.get("/assistant/me")
async def get_my_assistant(current_user: dict = Depends(get_current_user)):
    """Get current user's tenant assistant configuration"""
    tenant_id = str(current_user.get("tenant_id"))
    if not tenant_id:
        raise HTTPException(400, "User has no tenant")
    
    db = get_database()
    try:
        tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
    except:
        tenant = await db.tenants.find_one({"tenant_id": tenant_id})
    
    if not tenant or not tenant.get("vapi_assistant_id"):
        return {"configured": False}
    
    assistant_id = tenant.get("vapi_assistant_id")
    details = await vapi_service.get_assistant(assistant_id)
    
    if details:
        return {
            "configured": True,
            "assistant_id": details.get("id"),
            "name": details.get("name"),
            "first_message": details.get("firstMessage"),
            "voice": details.get("voice"),
            "model": details.get("model"),
            "transcriber": details.get("transcriber"),
            "tools": details.get("tools", []),
            "metadata": details.get("metadata", {})
        }
    else:
        return {"configured": False, "error": "Assistant not found in Vapi"}


@router.post("/assistant/me", response_model=AssistantResponse)
async def create_my_assistant(
    config: AssistantConfig,
    current_user: dict = Depends(get_current_user)
):
    """Create assistant for current user's tenant"""
    tenant_id = str(current_user.get("tenant_id"))
    if not tenant_id:
        raise HTTPException(400, "User has no tenant")
    
    db = get_database()
    try:
        tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
    except:
        tenant = await db.tenants.find_one({"tenant_id": tenant_id})
    
    if not tenant:
        raise HTTPException(404, "Tenant not found")
    
    company_name = config.company_name or tenant.get("business_name", "Valued Business")
    
    try:
        result = await vapi_service.create_assistant(
            tenant_id=tenant_id,
            company_name=company_name,
            instructions=config.instructions,
            first_message=config.first_message,
            voice=config.voice,
            voice_provider=config.voice_provider,
            voice_speed=config.voice_speed,
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            transcriber_provider=config.transcriber_provider,
            transcriber_model=config.transcriber_model,
            transcriber_language=config.transcriber_language,
            tools=config.tools
        )
        
        # Save to tenant record
        await db.tenants.update_one(
            {"_id": tenant.get("_id")},
            {"$set": {
                "vapi_assistant_id": result["assistant_id"],
                "ai_config.voice": config.voice,
                "ai_config.voice_provider": config.voice_provider,
                "ai_config.system_prompt": config.instructions,
                "ai_config.first_message": config.first_message
            }}
        )
        
        return AssistantResponse(**result)
    except Exception as e:
        logger.error(f"Error creating assistant: {e}")
        raise HTTPException(500, f"Failed to create assistant: {str(e)}")


@router.put("/assistant/me", response_model=AssistantResponse)
async def update_my_assistant(
    config: AssistantConfig,
    current_user: dict = Depends(get_current_user)
):
    """Update current user's tenant assistant"""
    tenant_id = str(current_user.get("tenant_id"))
    if not tenant_id:
        raise HTTPException(400, "User has no tenant")
    
    db = get_database()
    try:
        tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
    except:
        tenant = await db.tenants.find_one({"tenant_id": tenant_id})
    
    if not tenant or not tenant.get("vapi_assistant_id"):
        raise HTTPException(404, "Assistant not found")
    
    assistant_id = tenant.get("vapi_assistant_id")
    company_name = config.company_name or tenant.get("business_name", "Valued Business")
    
    try:
        result = await vapi_service.update_assistant(
            assistant_id=assistant_id,
            company_name=company_name,
            instructions=config.instructions,
            first_message=config.first_message,
            voice=config.voice,
            voice_provider=config.voice_provider,
            voice_speed=config.voice_speed,
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            tools=config.tools
        )
        
        # Update local DB
        await db.tenants.update_one(
            {"_id": tenant.get("_id")},
            {"$set": {
                "ai_config.voice": config.voice,
                "ai_config.voice_provider": config.voice_provider,
                "ai_config.system_prompt": config.instructions,
                "ai_config.first_message": config.first_message
            }}
        )
        
        return AssistantResponse(**result)
    except Exception as e:
        logger.error(f"Error updating assistant: {e}")
        raise HTTPException(500, f"Failed to update assistant: {str(e)}")


@router.delete("/assistant/me")
async def delete_my_assistant(current_user: dict = Depends(get_current_user)):
    """Delete current user's tenant assistant"""
    tenant_id = str(current_user.get("tenant_id"))
    if not tenant_id:
        raise HTTPException(400, "User has no tenant")
    
    db = get_database()
    try:
        tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
    except:
        tenant = await db.tenants.find_one({"tenant_id": tenant_id})
    
    if not tenant or not tenant.get("vapi_assistant_id"):
        raise HTTPException(404, "Assistant not found")
    
    assistant_id = tenant.get("vapi_assistant_id")
    
    success = await vapi_service.delete_assistant(assistant_id)
    if success:
        await db.tenants.update_one(
            {"_id": tenant.get("_id")},
            {"$unset": {"vapi_assistant_id": "", "ai_config": ""}}
        )
        return {"success": True, "message": "Assistant deleted"}
    else:
        raise HTTPException(500, "Failed to delete assistant")


# ===== VOICE CONFIGURATION =====

@router.get("/assistant/me/voice")
async def get_voice_settings(current_user: dict = Depends(get_current_user)):
    """Get assistant voice settings"""
    tenant_id = str(current_user.get("tenant_id"))
    db = get_database()
    
    try:
        tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
    except:
        tenant = await db.tenants.find_one({"tenant_id": tenant_id})
    
    if not tenant or not tenant.get("vapi_assistant_id"):
        raise HTTPException(404, "Assistant not configured")
    
    details = await vapi_service.get_assistant(tenant.get("vapi_assistant_id"))
    if details:
        return {
            "voice": details.get("voice", {}),
            "transcriber": details.get("transcriber", {})
        }
    raise HTTPException(404, "Assistant not found in Vapi")


@router.put("/assistant/me/voice")
async def update_voice_settings(
    voice_config: VoiceConfig,
    current_user: dict = Depends(get_current_user)
):
    """Update assistant voice settings"""
    tenant_id = str(current_user.get("tenant_id"))
    db = get_database()
    
    try:
        tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
    except:
        tenant = await db.tenants.find_one({"tenant_id": tenant_id})
    
    if not tenant or not tenant.get("vapi_assistant_id"):
        raise HTTPException(404, "Assistant not configured")
    
    result = await vapi_service.update_assistant(
        assistant_id=tenant.get("vapi_assistant_id"),
        voice=voice_config.voice_id,
        voice_provider=voice_config.provider,
        voice_speed=voice_config.speed
    )
    
    # Update local record
    await db.tenants.update_one(
        {"_id": tenant.get("_id")},
        {"$set": {
            "ai_config.voice": voice_config.voice_id,
            "ai_config.voice_provider": voice_config.provider
        }}
    )
    
    return {"success": True, "voice": voice_config.dict()}


@router.get("/voice-providers")
async def list_voice_providers(current_user: dict = Depends(get_current_user)):
    """Get available voice providers and their voices"""
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
async def get_personality_settings(current_user: dict = Depends(get_current_user)):
    """Get assistant personality/system prompt settings"""
    tenant_id = str(current_user.get("tenant_id"))
    db = get_database()
    
    try:
        tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
    except:
        tenant = await db.tenants.find_one({"tenant_id": tenant_id})
    
    if not tenant or not tenant.get("vapi_assistant_id"):
        raise HTTPException(404, "Assistant not configured")
    
    details = await vapi_service.get_assistant(tenant.get("vapi_assistant_id"))
    if details:
        model_config = details.get("model", {})
        messages = model_config.get("messages", [])
        system_prompt = ""
        for msg in messages:
            if msg.get("role") == "system":
                system_prompt = msg.get("content", "")
                break
        
        return {
            "system_prompt": system_prompt,
            "first_message": details.get("firstMessage", ""),
            "model": model_config.get("model", "gpt-4o-mini"),
            "temperature": model_config.get("temperature", 0.7),
            "max_tokens": model_config.get("maxTokens", 525)
        }
        
    # Default fallback if configured but fetch failed, or logic allows
    return {
        "system_prompt": "You are a helpful AI receptionist.",
        "first_message": "Hello! How can I help you?",
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_tokens": 525
    }


@router.put("/assistant/me/personality")
async def update_personality_settings(
    personality: PersonalityConfig,
    current_user: dict = Depends(get_current_user)
):
    """Update assistant personality/system prompt"""
    tenant_id = str(current_user.get("tenant_id"))
    db = get_database()
    
    try:
        tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
    except:
        tenant = await db.tenants.find_one({"tenant_id": tenant_id})
    
    if not tenant:
         raise HTTPException(404, "Tenant not found")

    if not tenant.get("vapi_assistant_id"):
        # Lazy creation if not exists
        from services.provisioning import vapi_provisioning
        logger.info(f"Auto-provisioning assistant for {tenant_id} during personality update")
        assistant = await vapi_provisioning.provision_tenant_assistant(
            tenant_id, 
            tenant.get("business_name", "My Business")
        )
        if not assistant:
             raise HTTPException(500, "Failed to provision assistant")
        
        # Refresh tenant
        tenant = await db.tenants.find_one({"_id": tenant.get("_id")})
    
    company_name = tenant.get("business_name", "Valued Business")
    
    result = await vapi_service.update_assistant(
        assistant_id=tenant.get("vapi_assistant_id"),
        company_name=company_name,
        instructions=personality.system_prompt,
        first_message=personality.first_message,
        temperature=personality.temperature
    )
    
    # Update local
    await db.tenants.update_one(
        {"_id": tenant.get("_id")},
        {"$set": {
            "ai_config.system_prompt": personality.system_prompt,
            "ai_config.first_message": personality.first_message
        }}
    )
    
    return {"success": True, "personality": personality.dict()}


# ===== KNOWLEDGE BASE MANAGEMENT =====

@router.get("/assistant/me/knowledge-base")
async def get_knowledge_base(current_user: dict = Depends(get_current_user)):
    """Get knowledge base documents for the assistant"""
    tenant_id = str(current_user.get("tenant_id"))
    db = get_database()
    
    # Get files from local tracking (since Vapi doesn't filter by tenant)
    kb_docs = await db.knowledge_base.find({"tenant_id": tenant_id}).to_list(100)
    
    return {
        "documents": [
            {
                "id": str(doc.get("_id")),
                "vapi_file_id": doc.get("vapi_file_id"),
                "name": doc.get("name"),
                "type": doc.get("type", "document"),
                "size": doc.get("size"),
                "status": doc.get("status", "processed"),
                "created_at": doc.get("created_at")
            }
            for doc in kb_docs
        ]
    }


@router.post("/assistant/me/knowledge-base/upload")
async def upload_knowledge_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload a document to knowledge base"""
    tenant_id = str(current_user.get("tenant_id"))
    db = get_database()
    
    content = await file.read()
    
    try:
        # Upload to Vapi
        vapi_result = await vapi_service.upload_file(content, file.filename)
        
        # Track locally
        doc = {
            "tenant_id": tenant_id,
            "vapi_file_id": vapi_result.get("id"),
            "name": file.filename,
            "type": file.content_type or "document",
            "size": len(content),
            "status": "processed",
            "created_at": datetime.utcnow()
        }
        result = await db.knowledge_base.insert_one(doc)
        
        return {
            "id": str(result.inserted_id),
            "vapi_file_id": vapi_result.get("id"),
            "name": file.filename,
            "status": "processed"
        }
    except Exception as e:
        logger.error(f"Failed to upload KB document: {e}")
        raise HTTPException(500, f"Upload failed: {str(e)}")


@router.delete("/assistant/me/knowledge-base/{doc_id}")
async def delete_knowledge_document(
    doc_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a knowledge base document"""
    tenant_id = str(current_user.get("tenant_id"))
    db = get_database()
    
    # Find document
    try:
        doc = await db.knowledge_base.find_one({
            "_id": ObjectId(doc_id),
            "tenant_id": tenant_id
        })
    except:
        raise HTTPException(400, "Invalid document ID")
    
    if not doc:
        raise HTTPException(404, "Document not found")
    
    # Delete from Vapi
    if doc.get("vapi_file_id"):
        await vapi_service.delete_file(doc.get("vapi_file_id"))
    
    # Delete local record
    await db.knowledge_base.delete_one({"_id": ObjectId(doc_id)})
    
    return {"success": True, "message": "Document deleted"}


@router.post("/assistant/me/knowledge-base/faq")
async def add_faq_entries(
    faqs: List[FAQEntry],
    current_user: dict = Depends(get_current_user)
):
    """Add FAQ entries to knowledge base"""
    tenant_id = str(current_user.get("tenant_id"))
    db = get_database()
    
    # Store FAQs in a structured format
    faq_docs = []
    for faq in faqs:
        doc = {
            "tenant_id": tenant_id,
            "type": "faq",
            "question": faq.question,
            "answer": faq.answer,
            "created_at": datetime.utcnow()
        }
        faq_docs.append(doc)
    
    if faq_docs:
        await db.knowledge_base.insert_many(faq_docs)
    
    return {"success": True, "added": len(faq_docs)}


# ===== TOOLS MANAGEMENT =====

@router.get("/tools/built-in")
async def list_built_in_tools(current_user: dict = Depends(get_current_user)):
    """Get available built-in tools"""
    tools = vapi_service.get_built_in_tools()
    return {"tools": tools}


@router.get("/assistant/me/tools")
async def get_enabled_tools(current_user: dict = Depends(get_current_user)):
    """Get tools enabled for the assistant"""
    tenant_id = str(current_user.get("tenant_id"))
    db = get_database()
    
    try:
        tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
    except:
        tenant = await db.tenants.find_one({"tenant_id": tenant_id})
    
    if not tenant or not tenant.get("vapi_assistant_id"):
        # Return empty list instead of 404 to allow page to load
        return {"tools": []}
    
    # Read enabled tools from local DB
    enabled_tools = tenant.get("enabled_tools", [])
    return {"tools": enabled_tools}


@router.post("/assistant/me/tools/{tool_id}/enable")
async def enable_tool(
    tool_id: str,
    config: Optional[Dict[str, Any]] = None,
    current_user: dict = Depends(get_current_user)
):
    """Enable a built-in tool for the assistant"""
    tenant_id = str(current_user.get("tenant_id"))
    db = get_database()
    
    try:
        tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
    except:
        tenant = await db.tenants.find_one({"tenant_id": tenant_id})
    
    if not tenant:
        raise HTTPException(404, "Tenant not found")

    if not tenant.get("vapi_assistant_id"):
        # Lazy creation if not exists
        from services.provisioning import vapi_provisioning
        logger.info(f"Auto-provisioning assistant for {tenant_id} during tool enable")
        assistant = await vapi_provisioning.provision_tenant_assistant(
            tenant_id, 
            tenant.get("business_name", "My Business")
        )
        if not assistant:
             raise HTTPException(500, "Failed to provision assistant")
        
        tenant = await db.tenants.find_one({"_id": tenant.get("_id")})
    
    # Get built-in tool config
    built_in_tools = vapi_service.get_built_in_tools()
    tool_config = None
    for tool in built_in_tools:
        if tool["id"] == tool_id:
            tool_config = tool["config"]
            break
    
    if not tool_config:
        raise HTTPException(404, f"Tool {tool_id} not found")
    
    # Store enabled tool in local DB
    # Get current enabled tools
    enabled_tools = tenant.get("enabled_tools", [])
    function_name = tool_config.get("function", {}).get("name", tool_id)
    
    # Add new tool if not already present
    if not any(t.get("function", {}).get("name") == function_name for t in enabled_tools):
        enabled_tools.append(tool_config)
    
    # Update tenant record
    await db.tenants.update_one(
        {"_id": tenant.get("_id")},
        {"$set": {"enabled_tools": enabled_tools}}
    )
    
    # CRITICAL: Push tools to Vapi assistant
    webhook_url = os.getenv("VAPI_WEBHOOK_URL", "")
    vapi_tools = []
    for tool in enabled_tools:
        if tool.get("type") == "function":
            vapi_tools.append({
                "type": "function",
                "function": tool.get("function"),
                "server": {"url": webhook_url}
            })
    
    if vapi_tools:
        try:
            await vapi_service.update_assistant(
                tenant.get("vapi_assistant_id"),
                tools=vapi_tools
            )
            logger.info(f"Synced {len(vapi_tools)} tools to Vapi for tenant {tenant_id}")
        except Exception as e:
            logger.error(f"Failed to sync tools to Vapi: {e}")
            # Continue anyway - local DB is updated
    
    return {"success": True, "enabled": tool_id, "function_name": function_name}


@router.delete("/assistant/me/tools/{tool_id}")
async def disable_tool(
    tool_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Disable a tool for the assistant"""
    tenant_id = str(current_user.get("tenant_id"))
    db = get_database()
    
    try:
        tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
    except:
        tenant = await db.tenants.find_one({"tenant_id": tenant_id})
    
    if not tenant or not tenant.get("vapi_assistant_id"):
        raise HTTPException(404, "Assistant not configured")
    
    # Map tool_id to function name
    built_in_tools = vapi_service.get_built_in_tools()
    function_name = None
    for tool in built_in_tools:
        if tool["id"] == tool_id:
            function_name = tool["config"].get("function", {}).get("name")
            break
    
    # Remove tool from local DB
    enabled_tools = tenant.get("enabled_tools", [])
    new_tools = [t for t in enabled_tools if t.get("function", {}).get("name") != function_name]
    
    await db.tenants.update_one(
        {"_id": tenant.get("_id")},
        {"$set": {"enabled_tools": new_tools}}
    )
    
    # Sync remaining tools to Vapi
    webhook_url = os.getenv("VAPI_WEBHOOK_URL", "")
    vapi_tools = []
    for tool in new_tools:
        if tool.get("type") == "function":
            vapi_tools.append({
                "type": "function",
                "function": tool.get("function"),
                "server": {"url": webhook_url}
            })
    
    try:
        await vapi_service.update_assistant(
            tenant.get("vapi_assistant_id"),
            tools=vapi_tools if vapi_tools else []
        )
        logger.info(f"Synced {len(vapi_tools)} tools to Vapi after disabling {tool_id}")
    except Exception as e:
        logger.error(f"Failed to sync tools to Vapi: {e}")
    
    return {"success": True, "disabled": tool_id}


# ===== ANALYTICS & CONVERSATIONS =====

@router.get("/assistant/me/analytics/calls")
async def get_call_analytics(
    days: int = Query(default=30, ge=1, le=365),
    current_user: dict = Depends(get_current_user)
):
    """Get call analytics for the assistant"""
    tenant_id = str(current_user.get("tenant_id"))
    db = get_database()
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get calls from local DB
    calls = await db.call_logs.find({
        "tenant_id": tenant_id,
        "created_at": {"$gte": start_date, "$lte": end_date}
    }).to_list(1000)
    
    # Calculate metrics
    total_calls = len(calls)
    total_duration = sum(c.get("duration", 0) or 0 for c in calls)
    total_cost = sum(c.get("cost", 0) or 0 for c in calls)
    
    # Status breakdown
    status_counts = {}
    for call in calls:
        status = call.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Daily breakdown
    daily_counts = {}
    for call in calls:
        day = call.get("created_at", datetime.utcnow()).strftime("%Y-%m-%d")
        if day not in daily_counts:
            daily_counts[day] = {"date": day, "count": 0, "duration": 0}
        daily_counts[day]["count"] += 1
        daily_counts[day]["duration"] += call.get("duration", 0) or 0
    
    return {
        "period_days": days,
        "total_calls": total_calls,
        "total_duration_minutes": round(total_duration / 60, 2),
        "avg_duration_seconds": round(total_duration / total_calls, 2) if total_calls > 0 else 0,
        "total_cost_cents": total_cost,
        "calls_by_status": status_counts,
        "calls_by_day": list(daily_counts.values())
    }


@router.get("/assistant/me/conversations")
async def list_conversations(
    limit: int = Query(default=50, ge=1, le=200),
    skip: int = Query(default=0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """List conversation/call history"""
    tenant_id = str(current_user.get("tenant_id"))
    db = get_database()
    
    calls = await db.call_logs.find(
        {"tenant_id": tenant_id}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    total = await db.call_logs.count_documents({"tenant_id": tenant_id})
    
    return {
        "conversations": [
            {
                "id": str(call.get("_id")),
                "vapi_call_id": call.get("vapi_call_id"),
                "customer_phone": call.get("customer_phone"),
                "status": call.get("status"),
                "duration": call.get("duration"),
                "summary": call.get("summary"),
                "started_at": call.get("started_at"),
                "ended_at": call.get("ended_at"),
                "created_at": call.get("created_at")
            }
            for call in calls
        ],
        "total": total,
        "limit": limit,
        "skip": skip
    }


@router.get("/assistant/me/conversations/{call_id}")
async def get_conversation_details(
    call_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get full conversation details including transcript"""
    tenant_id = str(current_user.get("tenant_id"))
    db = get_database()
    
    # Try local DB first
    try:
        call = await db.call_logs.find_one({
            "_id": ObjectId(call_id),
            "tenant_id": tenant_id
        })
    except:
        call = await db.call_logs.find_one({
            "vapi_call_id": call_id,
            "tenant_id": tenant_id
        })
    
    if not call:
        raise HTTPException(404, "Conversation not found")
    
    # Get full details from Vapi if available
    vapi_call_id = call.get("vapi_call_id")
    vapi_details = None
    if vapi_call_id:
        vapi_details = await vapi_service.get_call(vapi_call_id)
    
    return {
        "id": str(call.get("_id")),
        "vapi_call_id": vapi_call_id,
        "customer_phone": call.get("customer_phone"),
        "status": call.get("status"),
        "duration": call.get("duration"),
        "cost": call.get("cost"),
        "transcript": vapi_details.get("transcript") if vapi_details else call.get("transcript"),
        "summary": vapi_details.get("summary") if vapi_details else call.get("summary"),
        "recording_url": vapi_details.get("recordingUrl") if vapi_details else None,
        "started_at": call.get("started_at"),
        "ended_at": call.get("ended_at"),
        "created_at": call.get("created_at")
    }


# ===== TESTING =====

@router.post("/assistant/me/test")
async def test_assistant(current_user: dict = Depends(get_current_user)):
    """Get test configuration for the assistant"""
    tenant_id = str(current_user.get("tenant_id"))
    db = get_database()
    
    try:
        tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
    except:
        tenant = await db.tenants.find_one({"tenant_id": tenant_id})
    
    if not tenant or not tenant.get("vapi_assistant_id"):
        raise HTTPException(404, "Assistant not configured")
    
    return {
        "assistant_id": tenant.get("vapi_assistant_id"),
        "public_key": vapi_service.get_public_key(),
        "test_mode": True
    }
