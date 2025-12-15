
import logging
from typing import Dict, Any, Optional, List
from fastapi import HTTPException
from bson import ObjectId

from services.vapi_service import vapi_service
from database.mongo_config import get_database
from data.tenants import TenantRepository

logger = logging.getLogger(__name__)

class AssistantService:
    def __init__(self, db=None):
        self.db = db or get_database()
        self.tenant_repo = TenantRepository(self.db)

    async def _get_tenant(self, tenant_id: str):
        tenant = await self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise HTTPException(404, "Tenant not found")
        return tenant

    async def get_assistant(self, tenant_id: str) -> Dict[str, Any]:
        tenant = await self._get_tenant(tenant_id)
        
        if not tenant.get("vapi_assistant_id"):
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

    async def create_assistant(self, tenant_id: str, config: Any) -> Dict[str, Any]:
        tenant = await self._get_tenant(tenant_id)
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
            
            await self.tenant_repo.update(tenant_id, {
                "vapi_assistant_id": result["assistant_id"],
                "ai_config.voice": config.voice,
                "ai_config.voice_provider": config.voice_provider,
                "ai_config.system_prompt": config.instructions,
                "ai_config.first_message": config.first_message
            })
            
            return result
        except Exception as e:
            logger.error(f"Error creating assistant: {e}")
            raise HTTPException(500, f"Failed to create assistant: {str(e)}")

    async def update_assistant(self, tenant_id: str, config: Any) -> Dict[str, Any]:
        tenant = await self._get_tenant(tenant_id)
        
        if not tenant.get("vapi_assistant_id"):
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
            
            await self.tenant_repo.update(tenant_id, {
                "ai_config.voice": config.voice,
                "ai_config.voice_provider": config.voice_provider,
                "ai_config.system_prompt": config.instructions,
                "ai_config.first_message": config.first_message
            })
            
            return result
        except Exception as e:
            logger.error(f"Error updating assistant: {e}")
            raise HTTPException(500, f"Failed to update assistant: {str(e)}")

    async def delete_assistant(self, tenant_id: str) -> bool:
        tenant = await self._get_tenant(tenant_id)
        
        if not tenant.get("vapi_assistant_id"):
             raise HTTPException(404, "Assistant not found")
        
        assistant_id = tenant.get("vapi_assistant_id")
        
        success = await vapi_service.delete_assistant(assistant_id)
        if success:
             await self.tenant_repo.unset_field(tenant_id, {"vapi_assistant_id": "", "ai_config": ""})
             return True
        else:
             raise HTTPException(500, "Failed to delete assistant")

    # Voice Settings Logic
    async def get_voice_settings(self, tenant_id: str) -> Dict[str, Any]:
        tenant = await self._get_tenant(tenant_id)
        if not tenant.get("vapi_assistant_id"):
            raise HTTPException(404, "Assistant not configured")
        
        details = await vapi_service.get_assistant(tenant.get("vapi_assistant_id"))
        if details:
            return {
                "voice": details.get("voice", {}),
                "transcriber": details.get("transcriber", {})
            }
        raise HTTPException(404, "Assistant not found in Vapi")

    async def update_voice_settings(self, tenant_id: str, voice_config: Any) -> Dict[str, Any]:
        tenant = await self._get_tenant(tenant_id)
        if not tenant.get("vapi_assistant_id"):
            raise HTTPException(404, "Assistant not configured")
        
        await vapi_service.update_assistant(
            assistant_id=tenant.get("vapi_assistant_id"),
            voice=voice_config.voice_id,
            voice_provider=voice_config.provider,
            voice_speed=voice_config.speed
        )
        
        await self.tenant_repo.update(tenant_id, {
            "ai_config.voice": voice_config.voice_id,
            "ai_config.voice_provider": voice_config.provider
        })
        
        return {"success": True, "voice": voice_config.dict()}

    async def get_personality_settings(self, tenant_id: str) -> Dict[str, Any]:
        tenant = await self._get_tenant(tenant_id)
        if not tenant.get("vapi_assistant_id"):
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
        
        return {
            "system_prompt": "You are a helpful AI receptionist.",
            "first_message": "Hello! How can I help you?",
            "model": "gpt-4o-mini",
            "temperature": 0.7,
            "max_tokens": 525
        }

    async def update_personality_settings(self, tenant_id: str, personality: Any) -> Dict[str, Any]:
        tenant = await self._get_tenant(tenant_id)
        
        # Lazy provisioning logic from router
        if not tenant.get("vapi_assistant_id"):
            from services.provisioning import vapi_provisioning
            logger.info(f"Auto-provisioning assistant for {tenant_id} during personality update")
            assistant = await vapi_provisioning.provision_tenant_assistant(
                tenant_id, 
                tenant.get("business_name", "My Business")
            )
            if not assistant:
                 raise HTTPException(500, "Failed to provision assistant")
            # Refresh tenant
            tenant = await self._get_tenant(tenant_id)

        company_name = tenant.get("business_name", "Valued Business")
        
        await vapi_service.update_assistant(
            assistant_id=tenant.get("vapi_assistant_id"),
            company_name=company_name,
            instructions=personality.system_prompt,
            first_message=personality.first_message,
            temperature=personality.temperature
        )
        
        await self.tenant_repo.update(tenant_id, {
            "ai_config.system_prompt": personality.system_prompt,
            "ai_config.first_message": personality.first_message
        })
        
        return {"success": True, "personality": personality.dict()}

    
    # ===== KNOWLEDGE BASE =====
    async def get_knowledge_base(self, tenant_id: str) -> Dict[str, Any]:
        kb_docs = await self.db.knowledge_base.find({"tenant_id": tenant_id}).to_list(100)
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

    async def upload_knowledge_document(self, tenant_id: str, file_content: bytes, filename: str, content_type: str) -> Dict[str, Any]:
        try:
            # Upload to Vapi
            vapi_result = await vapi_service.upload_file(file_content, filename)
            
            # Track locally
            doc = {
                "tenant_id": tenant_id,
                "vapi_file_id": vapi_result.get("id"),
                "name": filename,
                "type": content_type or "document",
                "size": len(file_content),
                "status": "processed",
                # Note: imports for datetime should be handled at top if not present
                "created_at": getattr(vapi_result, 'created_at', None) # Placeholder, fixing in imports
            }
            # Fix imports momentarily
            from datetime import datetime
            doc["created_at"] = datetime.utcnow()

            result = await self.db.knowledge_base.insert_one(doc)
            
            return {
                "id": str(result.inserted_id),
                "vapi_file_id": vapi_result.get("id"),
                "name": filename,
                "status": "processed"
            }
        except Exception as e:
            logger.error(f"Failed to upload KB document: {e}")
            raise HTTPException(500, f"Upload failed: {str(e)}")

    async def delete_knowledge_document(self, tenant_id: str, doc_id: str) -> bool:
        try:
            doc = await self.db.knowledge_base.find_one({
                "_id": ObjectId(doc_id),
                "tenant_id": tenant_id
            })
        except:
            raise HTTPException(400, "Invalid document ID")
        
        if not doc:
            raise HTTPException(404, "Document not found")
        
        if doc.get("vapi_file_id"):
            await vapi_service.delete_file(doc.get("vapi_file_id"))
        
        await self.db.knowledge_base.delete_one({"_id": ObjectId(doc_id)})
        return True

    async def add_faq_entries(self, tenant_id: str, faqs: List[Any]) -> int:
        from datetime import datetime
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
            await self.db.knowledge_base.insert_many(faq_docs)
        
        return len(faq_docs)

    # ===== TOOLS =====
    async def get_built_in_tools(self) -> List[Dict[str, Any]]:
        return vapi_service.get_built_in_tools()

    async def get_enabled_tools(self, tenant_id: str) -> List[Dict[str, Any]]:
        tenant = await self._get_tenant(tenant_id)
        if not tenant.get("vapi_assistant_id"):
            return []
        return tenant.get("enabled_tools", [])

    async def enable_tool(self, tenant_id: str, tool_id: str) -> Dict[str, Any]:
        tenant = await self._get_tenant(tenant_id)
        
        # Lazy creation logic duplication here basically, but assuming tenant exists from _get_tenant
        if not tenant.get("vapi_assistant_id"):
            from services.provisioning import vapi_provisioning
            await vapi_provisioning.provision_tenant_assistant(
                tenant_id, 
                tenant.get("business_name", "My Business")
            )
            tenant = await self._get_tenant(tenant_id)

        built_in_tools = vapi_service.get_built_in_tools()
        tool_config = next((t["config"] for t in built_in_tools if t["id"] == tool_id), None)
        
        if not tool_config:
            raise HTTPException(404, f"Tool {tool_id} not found")
        
        enabled_tools = tenant.get("enabled_tools", [])
        function_name = tool_config.get("function", {}).get("name", tool_id)
        
        if not any(t.get("function", {}).get("name") == function_name for t in enabled_tools):
            enabled_tools.append(tool_config)
            
        await self.tenant_repo.update(tenant_id, {"enabled_tools": enabled_tools})
        
        # Sync to Vapi
        await self._sync_tools_to_vapi(tenant_id, enabled_tools)
        
        return {"success": True, "enabled": tool_id, "function_name": function_name}

    async def disable_tool(self, tenant_id: str, tool_id: str) -> Dict[str, Any]:
        tenant = await self._get_tenant(tenant_id)
        if not tenant.get("vapi_assistant_id"):
             raise HTTPException(404, "Assistant not configured")
             
        built_in_tools = vapi_service.get_built_in_tools()
        function_name = None
        for tool in built_in_tools:
            if tool["id"] == tool_id:
                function_name = tool["config"].get("function", {}).get("name")
                break
        
        enabled_tools = tenant.get("enabled_tools", [])
        new_tools = [t for t in enabled_tools if t.get("function", {}).get("name") != function_name]
        
        await self.tenant_repo.update(tenant_id, {"enabled_tools": new_tools})
        await self._sync_tools_to_vapi(tenant_id, new_tools)
        
        return {"success": True, "disabled": tool_id}

    async def _sync_tools_to_vapi(self, tenant_id: str, tools: List[Dict[str, Any]]):
        import os
        tenant = await self._get_tenant(tenant_id)
        webhook_url = os.getenv("VAPI_WEBHOOK_URL", "")
        vapi_tools = []
        for tool in tools:
            if tool.get("type") == "function":
                vapi_tools.append({
                    "type": "function",
                    "function": tool.get("function"),
                    "server": {"url": webhook_url}
                })
        
        try:
            if vapi_tools or not tools: # Update if empty list too
                 # Wait, if empty list, vapi_tools is empty.
                 await vapi_service.update_assistant(
                    tenant.get("vapi_assistant_id"),
                    tools=vapi_tools
                )
        except Exception as e:
            logger.error(f"Failed to sync tools to Vapi: {e}")

    # ===== ANALYTICS & PROVISIONING =====
    async def get_call_analytics(self, tenant_id: str, days: int) -> Dict[str, Any]:
        from datetime import datetime, timedelta
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        calls = await self.db.call_logs.find({
            "tenant_id": tenant_id,
            "created_at": {"$gte": start_date, "$lte": end_date}
        }).to_list(1000)
        
        total_calls = len(calls)
        total_duration = sum(c.get("duration", 0) or 0 for c in calls)
        total_cost = sum(c.get("cost", 0) or 0 for c in calls)
        
        status_counts = {}
        for call in calls:
            status = call.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
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
    
    async def list_conversations(self, tenant_id: str, limit: int, skip: int) -> Dict[str, Any]:
        calls = await self.db.call_logs.find(
            {"tenant_id": tenant_id}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
        
        total = await self.db.call_logs.count_documents({"tenant_id": tenant_id})
        
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

    async def get_conversation_details(self, tenant_id: str, call_id: str) -> Dict[str, Any]:
        # Try local DB first
        try:
            call = await self.db.call_logs.find_one({
                "_id": ObjectId(call_id),
                "tenant_id": tenant_id
            })
        except:
            call = await self.db.call_logs.find_one({
                "vapi_call_id": call_id,
                "tenant_id": tenant_id
            })
        
        if not call:
            raise HTTPException(404, "Conversation not found")
        
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

    async def get_test_config(self, tenant_id: str) -> Dict[str, Any]:
        tenant = await self._get_tenant(tenant_id)
        if not tenant.get("vapi_assistant_id"):
            raise HTTPException(404, "Assistant not configured")
        
        return {
            "assistant_id": tenant.get("vapi_assistant_id"),
            "public_key": vapi_service.get_public_key(),
            "test_mode": True
        }

def get_assistant_service():
    return AssistantService()
