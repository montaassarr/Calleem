
import logging
from typing import Dict, Any, Optional, List
from datetime import timedelta
from fastapi import HTTPException
from bson import ObjectId

from services.vapi_service import vapi_service
from database.mongo_config import get_database
from data.tenants import TenantRepository
from utils.datetime_utils import DateTimeUtils

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

    async def _recover_assistant_id(self, tenant_id: str) -> Optional[str]:
        """Try to recover a missing assistant id from Vapi metadata."""
        assistants = await vapi_service.list_assistants()
        for assistant in assistants:
            metadata = assistant.get("metadata") or {}
            if str(metadata.get("tenant_id")) == str(tenant_id):
                assistant_id = assistant.get("id")
                if assistant_id:
                    await self.tenant_repo.update(tenant_id, {"vapi_assistant_id": assistant_id})
                    return assistant_id
        return None

    async def get_assistant(self, tenant_id: str) -> Dict[str, Any]:
        tenant = await self._get_tenant(tenant_id)
        
        if not tenant.get("vapi_assistant_id"):
            recovered_id = await self._recover_assistant_id(tenant_id)
            if recovered_id:
                tenant["vapi_assistant_id"] = recovered_id
            else:
                return {"configured": False}
        
        assistant_id = tenant.get("vapi_assistant_id")
        details = await vapi_service.get_assistant(assistant_id)

        if not details:
            recovered_id = await self._recover_assistant_id(tenant_id)
            if recovered_id:
                assistant_id = recovered_id
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
            
            # Default-enable built-in tools if none configured
            try:
                enabled_tools = tenant.get("enabled_tools") or []
                if not enabled_tools:
                    built_ins = vapi_service.get_built_in_tools()
                    # Enable core receptionist tools
                    core_ids = {"get_available_services", "get_business_location", "check_availability", "book_appointment"}
                    for tool in built_ins:
                        if tool["id"] in core_ids:
                            enabled_tools.append({
                                "tool_id": tool["id"],
                                "config": tool["config"]
                            })
                    await self.tenant_repo.update(tenant_id, {"enabled_tools": enabled_tools})
                    # Sync to Vapi with server webhook URL
                    await self._sync_tools_to_vapi(tenant_id, enabled_tools)
            except Exception as e:
                logger.warning(f"Failed to default-enable tools: {e}")
            
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
        assistant_id = tenant.get("vapi_assistant_id") or await self._recover_assistant_id(tenant_id)

        details = await vapi_service.get_assistant(assistant_id) if assistant_id else None
        if not details and assistant_id:
            recovered_id = await self._recover_assistant_id(tenant_id)
            if recovered_id:
                details = await vapi_service.get_assistant(recovered_id)

        if details:
            return {
                "configured": True,
                "voice": details.get("voice", {}),
                "transcriber": details.get("transcriber", {})
            }

        return {
            "configured": False,
            "voice": {
                "provider": tenant.get("ai_config", {}).get("voice_provider", "11labs"),
                "voiceId": tenant.get("ai_config", {}).get("voice", "jennifer")
            },
            "transcriber": {"provider": "deepgram", "model": "nova-2", "language": "en"}
        }

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
            "system_prompt": self._inject_current_date("""You are an AI receptionist named Ahmed - friendly, professional, and helpful.

Core behavior:
- Use short, natural sentences. Keep responses brief.
- Ask one question at a time.
- Be warm, friendly, slightly casual.
- Always confirm details before booking.
- Match the client's energy.

Booking flow:
1. Get their name
2. Ask what service they want
3. Ask for preferred date/time
4. Resolve relative dates using the current date context in this prompt
5. Call checkAvailability() with the correct YYYY-MM-DD date
6. Repeat details back for confirmation
7. Call bookAppointment() with CORRECT future date

Important:
- NEVER book appointments in the past
- Use YYYY-MM-DD format for dates
- Use HH:MM (24-hour) format for times (11:00, 14:30)
- Call getAvailableServices when asked about prices/services
- Call getBusinessLocation when asked about address/directions"""),
            "first_message": "Hello! Welcome to the business. This is Ahmed speaking, how can I help you today?",
            "model": "gpt-4o-mini",
            "temperature": 0.7,
            "max_tokens": 525
        }

    def _build_date_context(self) -> str:
        """Build a runtime date context block for prompt injection."""
        current_time = DateTimeUtils.now()
        return (
            f"\n\n**CURRENT DATE: {current_time.strftime('%A, %B %d, %Y')}**\n"
            f"Today is {current_time.strftime('%B %d, %Y')} in the business timezone.\n"
            f"Use this date to resolve relative dates like tomorrow, next week, or Friday."
        )

    def _inject_current_date(self, system_prompt: str) -> str:
        """Prepend runtime date context to the supplied system prompt."""
        if not system_prompt:
            return self._build_date_context().lstrip()

        if "**CURRENT DATE:" in system_prompt:
            import re

            system_prompt = re.sub(
                r'\*\*CURRENT DATE:.*?Use this date to resolve relative dates like tomorrow, next week, or Friday\.',
                '',
                system_prompt,
                flags=re.DOTALL,
            ).strip()

        return f"{system_prompt.strip()}{self._build_date_context()}"
    
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
        
        # Keep the stored prompt free of hardcoded current-date text
        enhanced_prompt = self._inject_current_date(personality.system_prompt)
        
        await vapi_service.update_assistant(
            assistant_id=tenant.get("vapi_assistant_id"),
            company_name=company_name,
            instructions=enhanced_prompt,
            first_message=personality.first_message,
            temperature=personality.temperature
        )
        
        # Store the original prompt (without date injection) in DB
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
            
            document = {
                "tenant_id": tenant_id,
                "vapi_file_id": vapi_result.get("id"),
                "name": filename,
                "type": content_type or "document",
                "size": len(file_content),
                "status": "processed",
                "created_at": datetime.utcnow()
            }
            await self.db.knowledge_base.insert_one(document)

            return {
                "success": True,
                "document": {
                    "id": str(vapi_result.get("id")),
                    "name": filename,
                    "type": content_type or "document",
                    "size": len(file_content),
                    "status": "processed"
                }
            }
        except Exception as e:
            logger.error(f"Error uploading knowledge document: {e}")
            raise HTTPException(500, f"Failed to upload document: {e}")

    async def delete_knowledge_document(self, tenant_id: str, doc_id: str) -> bool:
        doc = await self.db.knowledge_base.find_one({"_id": ObjectId(doc_id), "tenant_id": tenant_id})
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

    def _match_tool_id_from_config(self, config: Dict[str, Any], built_in_tools: List[Dict[str, Any]]) -> Optional[str]:
        config_type = config.get("type")
        config_function_name = (config.get("function") or {}).get("name")

        for tool in built_in_tools:
            candidate = tool.get("config", {})
            candidate_type = candidate.get("type")
            candidate_function_name = (candidate.get("function") or {}).get("name")

            if config_type == "function" and candidate_type == "function":
                if config_function_name and config_function_name == candidate_function_name:
                    return tool.get("id")
            elif config_type == candidate_type:
                return tool.get("id")

        return None

    def _normalize_enabled_tools(self, raw_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        built_in_tools = vapi_service.get_built_in_tools()
        normalized: List[Dict[str, Any]] = []

        for entry in raw_tools or []:
            if not isinstance(entry, dict):
                continue

            if "config" in entry:
                tool_config = entry.get("config") or {}
                tool_id = entry.get("tool_id") or entry.get("id")
            else:
                tool_config = entry
                tool_id = None

            if not tool_id:
                tool_id = self._match_tool_id_from_config(tool_config, built_in_tools)

            if not tool_id:
                continue

            normalized.append({
                "tool_id": tool_id,
                "config": tool_config
            })

        # De-duplicate by tool_id (keep latest)
        dedup: Dict[str, Dict[str, Any]] = {}
        for entry in normalized:
            dedup[entry["tool_id"]] = entry

        return list(dedup.values())

    # ===== TOOLS =====
    async def get_built_in_tools(self) -> List[Dict[str, Any]]:
        return vapi_service.get_built_in_tools()

    async def get_enabled_tools(self, tenant_id: str) -> List[Dict[str, Any]]:
        tenant = await self._get_tenant(tenant_id)
        if not tenant.get("vapi_assistant_id"):
            return []

        normalized = self._normalize_enabled_tools(tenant.get("enabled_tools", []))

        # Self-heal legacy storage format
        await self.tenant_repo.update(tenant_id, {"enabled_tools": normalized})

        return [
            {
                "id": entry.get("tool_id"),
                "tool_id": entry.get("tool_id"),
                **(entry.get("config") or {})
            }
            for entry in normalized
        ]

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
        selected_tool = next((t for t in built_in_tools if t["id"] == tool_id), None)
        tool_config = selected_tool.get("config") if selected_tool else None
        
        if not tool_config:
            raise HTTPException(404, f"Tool {tool_id} not found")
        
        normalized = self._normalize_enabled_tools(tenant.get("enabled_tools", []))

        if not any(t.get("tool_id") == tool_id for t in normalized):
            normalized.append({"tool_id": tool_id, "config": tool_config})

        await self.tenant_repo.update(tenant_id, {"enabled_tools": normalized})

        # Sync to Vapi
        await self._sync_tools_to_vapi(tenant_id, normalized, raise_on_failure=True)

        function_name = (tool_config.get("function") or {}).get("name")
        return {"success": True, "enabled": tool_id, "function_name": function_name or tool_id}

    async def disable_tool(self, tenant_id: str, tool_id: str) -> Dict[str, Any]:
        tenant = await self._get_tenant(tenant_id)
        if not tenant.get("vapi_assistant_id"):
             raise HTTPException(404, "Assistant not configured")

        normalized = self._normalize_enabled_tools(tenant.get("enabled_tools", []))
        new_tools = [t for t in normalized if t.get("tool_id") != tool_id]

        await self.tenant_repo.update(tenant_id, {"enabled_tools": new_tools})
        await self._sync_tools_to_vapi(tenant_id, new_tools, raise_on_failure=True)
        
        return {"success": True, "disabled": tool_id}

    async def _sync_tools_to_vapi(self, tenant_id: str, tools: List[Dict[str, Any]], raise_on_failure: bool = False):
        import os
        from utils.config import settings
        
        tenant = await self._get_tenant(tenant_id)
        
        # Get webhook URL with proper fallback
        webhook_url = os.getenv("VAPI_WEBHOOK_URL") or settings.VAPI_WEBHOOK_URL
        if not webhook_url:
            backend_url = os.getenv("BACKEND_URL") or settings.BACKEND_URL
            webhook_url = f"{backend_url}/api/v1/vapi/webhook"
        
        logger.info(f"Syncing tools to Vapi with webhook URL: {webhook_url}")
        
        normalized = self._normalize_enabled_tools(tools)

        vapi_tools = []
        for entry in normalized:
            tool = entry.get("config") or {}
            tool_type = tool.get("type")

            if tool_type == "function":
                function_def = tool.get("function")
                if function_def:
                    vapi_tools.append({
                        "type": "function",
                        "function": function_def,
                        "server": {"url": webhook_url}
                    })
            elif tool_type in {"transferCall", "endCall"}:
                vapi_tools.append(tool)
        
        try:
            if vapi_tools or not normalized:
                 await vapi_service.update_assistant(
                    tenant.get("vapi_assistant_id"),
                    tools=vapi_tools
                )
        except Exception as e:
            logger.error(f"Failed to sync tools to Vapi: {e}")
            if raise_on_failure:
                raise HTTPException(502, f"Failed to sync tools to Vapi: {str(e)}")

    # ===== ANALYTICS & PROVISIONING =====
    async def get_call_analytics(self, tenant_id: str, days: int) -> Dict[str, Any]:
        from datetime import datetime, timedelta
        
        # Get tenant and assistant info
        tenant = await self._get_tenant(tenant_id)
        assistant_id = tenant.get("vapi_assistant_id")
        
        if not assistant_id:
            return {
                "period_days": days,
                "total_calls": 0,
                "total_duration_minutes": 0,
                "avg_duration_seconds": 0,
                "total_cost_cents": 0,
                "calls_by_status": {},
                "calls_by_day": [],
                "error": "No assistant configured"
            }
        
        # Fetch calls from Vapi API for this specific assistant
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Format dates for Vapi API (ISO 8601)
        created_at_gt = start_date.isoformat()
        created_at_lt = end_date.isoformat()
        
        calls = await vapi_service.list_calls(
            assistant_id=assistant_id,
            limit=1000,
            created_at_gt=created_at_gt,
            created_at_lt=created_at_lt
        )
        
        if not isinstance(calls, list):
            calls = []
        
        total_calls = len(calls)
        total_duration = sum(c.get("duration", 0) or 0 for c in calls)
        total_cost = sum(c.get("cost", 0) or 0 for c in calls)
        
        status_counts = {}
        for call in calls:
            status = call.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        daily_counts = {}
        for call in calls:
            # Parse createdAt from Vapi response
            created_at_str = call.get("createdAt")
            if created_at_str:
                try:
                    if isinstance(created_at_str, str):
                        created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                    else:
                        created_at = created_at_str
                except:
                    created_at = datetime.utcnow()
            else:
                created_at = datetime.utcnow()
            
            day = created_at.strftime("%Y-%m-%d")
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
        # Get tenant and assistant info
        tenant = await self._get_tenant(tenant_id)
        assistant_id = tenant.get("vapi_assistant_id")
        
        if not assistant_id:
            return {
                "conversations": [],
                "total": 0,
                "limit": limit,
                "skip": skip,
                "error": "No assistant configured"
            }
        
        # Fetch calls from Vapi API with pagination
        # Note: Vapi API doesn't support skip/offset, so we fetch more and slice locally
        calls = await vapi_service.list_calls(
            assistant_id=assistant_id,
            limit=limit + skip  # Fetch enough to cover pagination
        )
        
        if not isinstance(calls, list):
            calls = []
        
        total = len(calls)
        # Apply skip/limit to the fetched calls
        paginated_calls = calls[skip:skip + limit]
        
        return {
            "conversations": [
                {
                    "id": call.get("id"),
                    "vapi_call_id": call.get("id"),
                    "customer_phone": call.get("phoneNumber"),
                    "status": call.get("status"),
                    "duration": call.get("duration"),
                    "summary": call.get("summary"),
                    "started_at": call.get("startedAt"),
                    "ended_at": call.get("endedAt"),
                    "created_at": call.get("createdAt")
                }
                for call in paginated_calls
            ],
            "total": total,
            "limit": limit,
            "skip": skip
        }

    async def get_conversation_details(self, tenant_id: str, call_id: str) -> Dict[str, Any]:
        # Fetch call details directly from Vapi API
        vapi_details = await vapi_service.get_call(call_id)
        
        if not vapi_details:
            raise HTTPException(404, "Call not found")
        
        # Verify this call belongs to the tenant's assistant
        tenant = await self._get_tenant(tenant_id)
        assistant_id = tenant.get("vapi_assistant_id")
        
        if assistant_id and vapi_details.get("assistantId") != assistant_id:
            raise HTTPException(403, "Unauthorized: Call does not belong to your assistant")
        
        return {
            "id": vapi_details.get("id"),
            "vapi_call_id": vapi_details.get("id"),
            "customer_phone": vapi_details.get("phoneNumber"),
            "status": vapi_details.get("status"),
            "duration": vapi_details.get("duration"),
            "cost": vapi_details.get("cost"),
            "transcript": vapi_details.get("transcript"),
            "summary": vapi_details.get("summary"),
            "recording_url": vapi_details.get("recordingUrl"),
            "started_at": vapi_details.get("startedAt"),
            "ended_at": vapi_details.get("endedAt"),
            "created_at": vapi_details.get("createdAt")
        }

    async def get_test_config(self, tenant_id: str) -> Dict[str, Any]:
        tenant = await self._get_tenant(tenant_id)
        if not tenant.get("vapi_assistant_id"):
            recovered_id = await self._recover_assistant_id(tenant_id)
            if recovered_id:
                tenant["vapi_assistant_id"] = recovered_id
            else:
                raise HTTPException(404, "Assistant not configured")
        
        return {
            "assistant_id": tenant.get("vapi_assistant_id"),
            "public_key": vapi_service.get_public_key(),
            "test_mode": True
        }

def get_assistant_service():
    return AssistantService()
