"""Unified Vapi voice-agent orchestration layer.

This module centralizes every integration touchpoint with Vapi so the
WhatsApp/chat flows and the new voice experiences share the exact same
business configuration, appointment logic, and memory system.
"""

from __future__ import annotations

import asyncio
import copy
import json
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ai.brain.prompt_builder import PromptBuilder
from ai.conversation_manager import conversation_manager
from database.mongo_config import get_database
from services.config_loader import config_loader
from voice_agent.tools import voice_tools
from voice_agent.vapi_http_client import VapiHTTPClient
from utils.config import settings
from utils.text_formatter import text_formatter

logger = logging.getLogger(__name__)


@dataclass
class AssistantCacheEntry:
    """Cached assistant metadata per business tenant."""

    assistant_id: str
    updated_at: datetime


class VapiAgentService:
    """High-level façade for every Vapi interaction using HTTP API."""

    def __init__(self) -> None:
        self.api_key = settings.VAPI_API_KEY
        self.base_url = "https://api.vapi.ai"
        self._assistant_cache: Dict[str, AssistantCacheEntry] = {}
        self._http_client = VapiHTTPClient(api_key=self.api_key) if self.api_key else None
        self._server_secret = settings.VAPI_SERVER_SECRET or None

    def _is_configured(self) -> bool:
        """Check if Vapi is configured"""
        return bool(self.api_key)
    
    def _require_client(self) -> VapiHTTPClient:
        """Get HTTP client or raise error"""
        if not self._http_client:
            raise ValueError("VAPI_API_KEY not configured")
        return self._http_client

    def invalidate_assistant_cache(self, business_id: Optional[str] = None) -> None:
        """Clear cached assistant ids so future requests rebuild with new config."""
        if business_id:
            self._assistant_cache.pop(business_id, None)
        else:
            self._assistant_cache.clear()

    async def start_call(
        self,
        customer_number: str,
        metadata: Optional[Dict[str, Any]] = None,
        business_id: str = "default",
    ) -> Dict[str, Any]:
        """Trigger an outbound voice call via Vapi."""

        await self._ensure_voice_agent_enabled(business_id)
        assistant_id = await self._resolve_assistant_id(business_id)
        client = self._require_client()

        metadata_payload = dict(metadata or {})
        metadata_payload.setdefault("business_id", business_id)
        clean_number = text_formatter.clean_phone_number(customer_number)

        payload: Dict[str, Any] = {
            "assistantId": assistant_id,
            "customer": {
                "number": clean_number,
            },
        }
        
        if metadata_payload.get("customer_name"):
            payload["customer"]["name"] = metadata_payload.pop("customer_name")
        
        if metadata_payload:
            payload["metadata"] = metadata_payload

        call = await client.create_call(payload)
        asyncio.create_task(self._persist_and_sync(call, business_id, transport="outbound"))
        return {
            "call_id": call.get("id"),
            "status": call.get("status", "queued"),
            "assistant_id": assistant_id,
        }

    async def test_agent(self, business_id: str = "default") -> Dict[str, Any]:
        """Return diagnostics for dashboard status cards."""

        await self._ensure_voice_agent_enabled(business_id)
        assistant_id = await self._resolve_assistant_id(business_id)
        return {
            "status": "ok",
            "assistant_id": assistant_id,
            "groq_model": settings.GROQ_MODEL,
            "voice_provider": self._voice_provider_name(),
            "webrtc_public_key": settings.VOICE_AGENT_WEBRTC_PUBLIC_KEY,
        }

    async def fetch_call_history(self, business_id: str = "default", limit: int = 20) -> List[Dict[str, Any]]:
        await self._ensure_voice_agent_enabled(business_id)
        db = self._require_database()

        query: Dict[str, Any]
        if business_id == "default":
            query = {"$or": [{"business_id": business_id}, {"business_id": {"$exists": False}}]}
        else:
            query = {"business_id": business_id}

        cursor = (
            db.voice_calls
            .find(query)
            .sort("created_at", -1)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        for doc in docs:
            doc["id"] = str(doc.get("_id")) if doc.get("_id") else doc.get("call_id")
        return docs

    async def ingest_webhook_event(self, payload: Dict[str, Any], business_id: Optional[str] = None) -> Dict[str, Any]:
        """Persist Vapi webhook events and sync them with the shared conversation flow."""

        if not isinstance(payload, dict):
            logger.warning("Ignoring Vapi webhook payload because it is not a dict")
            return {"status": "ignored", "reason": "invalid_payload"}

        message = self._extract_server_message(payload)
        if not isinstance(message, dict):
            logger.warning("Ignoring Vapi webhook envelope without message payload")
            return {"status": "ignored", "reason": "invalid_message"}

        message_type = str(message.get("type") or "").lower()
        if message_type in {"tool-calls", "function-call"}:
            return await self._handle_tool_calls_message(message, business_id)

        call_payload = self._extract_call_payload(message)
        if not call_payload:
            logger.debug("No call payload present in webhook message type %s", message_type or "unknown")
            return {"status": "ignored", "reason": "no_call_payload"}

        metadata = self._as_dict(self._safe_get(call_payload, "metadata", {}))
        if not metadata:
            metadata = self._as_dict(message.get("metadata"))
        resolved_business_id = metadata.get("business_id") or business_id or "default"
        transport = (
            metadata.get("transport")
            or message.get("transport")
            or payload.get("transport")
            or "inbound"
        )

        logger.info(
            "Processing Vapi webhook event for business %s with call_id=%s",
            resolved_business_id,
            call_payload.get("id") or call_payload.get("call_id"),
        )

        doc = await self._persist_call(call_payload, resolved_business_id, transport)
        if doc:
            await self._sync_conversation_from_transcript(doc, resolved_business_id)

        return {
            "status": "processed" if doc else "ignored",
            "call_id": (doc or {}).get("call_id"),
            "business_id": resolved_business_id,
        }

    async def get_webrtc_test_payload(self, business_id: str = "default") -> Dict[str, Any]:
        """Expose the assistant + key needed for WebRTC in-browser sessions."""

        await self._ensure_voice_agent_enabled(business_id)
        public_key = settings.VOICE_AGENT_WEBRTC_PUBLIC_KEY
        
        # Allow a dedicated assistant override for WebRTC demos, else reuse the main assistant.
        preferred_assistant = settings.VOICE_AGENT_WEBRTC_ASSISTANT_ID
        assistant_id = preferred_assistant or await self._resolve_assistant_id(business_id)

        # If no public key, return basic info without session
        if not public_key:
            return {
                "assistant_id": assistant_id,
                "public_key": "",
                "session_token": "",
                "expires_at": (datetime.utcnow() + timedelta(minutes=10)).isoformat() + "Z",
                "business_id": business_id,
                "session": None,
                "error": "VOICE_AGENT_WEBRTC_PUBLIC_KEY not configured. Get it from Vapi dashboard."
            }

        ttl_minutes = max(settings.VOICE_AGENT_WEBRTC_SESSION_TTL_MINUTES, 1)
        expires_at = datetime.utcnow() + timedelta(minutes=ttl_minutes)
        session = await self._create_webrtc_session(assistant_id, business_id)
        session_token = (
            session.get("client_secret")
            or session.get("token")
            or session.get("id")
            or uuid.uuid4().hex
        )

        return {
            "assistant_id": assistant_id,
            "public_key": public_key,
            "session_token": session_token,
            "expires_at": expires_at.isoformat() + "Z",
            "business_id": business_id,
            "session": session or None,
        }

    async def _persist_and_sync(self, call: Any, business_id: str, transport: str) -> None:
        try:
            doc = await self._persist_call(call, business_id, transport)
            if doc:
                await self._sync_conversation_from_transcript(doc, business_id)
        except Exception as exc:
            logger.error("Voice agent persisted call sync failed: %s", exc, exc_info=True)

    async def _persist_call(self, call: Any, business_id: str, transport: str) -> Dict[str, Any]:
        db = self._require_database(optional=True)
        if db is None:
            return {}

        metadata = self._as_dict(self._safe_get(call, "metadata", {}))
        metadata.setdefault("business_id", business_id)

        doc = {
            "call_id": self._safe_get(call, "id", uuid.uuid4().hex),
            "status": self._safe_get(call, "status", "queued"),
            "assistant_id": self._safe_get(call, "assistant_id", None),
            "customer": self._as_dict(self._safe_get(call, "customer", {})),
            "metadata": metadata,
            "cost": self._safe_get(call, "cost", 0),
            "transcript": self._as_list(self._safe_get(call, "transcript", [])),
            "messages": self._as_list(self._safe_get(call, "messages", [])),
            "created_at": self._coerce_datetime(self._safe_get(call, "created_at", datetime.utcnow())),
            "business_id": business_id,
            "transport": transport,
            "synced_with_conversation": False,
        }

        contact_id = self._resolve_call_contact_id(doc)
        if contact_id:
            doc.setdefault("metadata", {})["voice_contact_id"] = contact_id

        await db.voice_calls.update_one({"call_id": doc["call_id"]}, {"$set": doc}, upsert=True)
        return doc

    async def _sync_conversation_from_transcript(self, call_doc: Dict[str, Any], business_id: str) -> None:
        if call_doc.get("synced_with_conversation"):
            return

        transcript = call_doc.get("messages") or call_doc.get("transcript") or []
        if not transcript:
            return

        client_phone = self._resolve_call_contact_id(call_doc)
        if not client_phone:
            logger.info(
                "Voice call %s missing contact identifier – skipping sync",
                call_doc.get("call_id")
            )
            return

        conversation_id: Optional[str] = None
        for entry in transcript:
            role = str((entry or {}).get("role", "")).lower()
            if role not in {"user", "customer", "client"}:
                continue
            text = (entry or {}).get("text") or (entry or {}).get("content")
            if not text:
                continue

            result = await conversation_manager.process_message(
                phone_number=client_phone,
                message_text=text,
                whatsapp_metadata={
                    "source": "voice_agent",
                    "call_id": call_doc.get("call_id"),
                    "business_id": business_id,
                    "transport": call_doc.get("transport"),
                },
            )
            conversation_id = result.get("conversation_id") or conversation_id

        if conversation_id:
            db = self._require_database(optional=True)
            if db is not None:
                await db.voice_calls.update_one(
                    {"call_id": call_doc.get("call_id")},
                    {"$set": {
                        "synced_with_conversation": True,
                        "conversation_id": conversation_id,
                        "synced_at": datetime.utcnow(),
                    }},
                )

    async def _resolve_assistant_id(self, business_id: str) -> str:
        config = await self._get_business_config(business_id)
        voice_config = (config or {}).get("voice_config", {}) or {}
        stored = voice_config.get("vapi_assistant_id")
        if stored:
            return stored

        if settings.VAPI_ASSISTANT_ID:
            return settings.VAPI_ASSISTANT_ID

        cached = self._assistant_cache.get(business_id)
        if cached and (datetime.utcnow() - cached.updated_at).total_seconds() < 86400:
            return cached.assistant_id

        client = self._require_client()
        payload = await self._build_assistant_payload(business_id, config)
        assistant = await client.create_assistant(payload)
        assistant_id = assistant.get("id")
        if not assistant_id:
            raise RuntimeError("Vapi did not return an assistant id")

        entry = AssistantCacheEntry(assistant_id=assistant_id, updated_at=datetime.utcnow())
        self._assistant_cache[business_id] = entry
        await self._persist_assistant_id(business_id, assistant_id)
        return assistant_id

    async def _build_assistant_payload(self, business_id: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if config is None:
            config = await self._get_business_config(business_id)
        voice_config = (config or {}).get("voice_config", {}) or {}
        ai_config = (config or {}).get("ai_config", {}) or {}
        business_name = (config or {}).get("business_name", settings.BUSINESS_NAME)

        # Model configuration (use voice_config first, fallback to ai_config)
        model_provider = voice_config.get("model_provider", "groq")
        model_name = voice_config.get("model_name") or ai_config.get("model") or settings.GROQ_MODEL
        try:
            temperature = float(voice_config.get("temperature", ai_config.get("temperature", 0.7)))
        except (TypeError, ValueError):
            temperature = 0.7
        try:
            max_tokens = int(voice_config.get("max_tokens", ai_config.get("max_tokens", 500)))
        except (TypeError, ValueError):
            max_tokens = 500

        # Voice configuration
        voice_provider_key = str(voice_config.get("voice_provider", "openai")).lower()
        voice_provider_map = {
            "elevenlabs": "11labs",
            "11labs": "11labs",
            "openai": "openai",
            "playht": "playht",
            "azure": "azure",
            "deepgram": "deepgram",
        }
        voice_provider = voice_provider_map.get(voice_provider_key, voice_provider_key)
        voice_id = self._resolve_voice_id(voice_provider, voice_config.get("voice_id", "alloy"))

        # System prompt (use voice_config first, fallback to dynamic generation)
        instructions = voice_config.get("system_prompt")
        if not instructions:
            instructions = PromptBuilder.build_system_prompt(config)
        
        # First message
        first_message = voice_config.get("first_message", 
            f"Hi, this is Ava from {business_name}. How can I help you today?")

        # Build tools array based on enabled_tools
        enabled_tool_names = voice_config.get("enabled_tools", [
            "check_availability", "book_appointment", "get_services"
        ])
        
        all_tools = voice_tools.get_tool_definitions()
        enabled_tools: List[Dict[str, Any]] = []
        server_url = settings.VAPI_WEBHOOK_URL
        if enabled_tool_names and not server_url:
            logger.warning(
                "VAPI_WEBHOOK_URL missing; voice agent tools cannot call backend."
            )
        for tool in all_tools:
            tool_name = tool.get("function", {}).get("name")
            if tool_name not in enabled_tool_names:
                continue
            tool_payload = copy.deepcopy(tool)
            if server_url:
                tool_payload["server"] = {"url": server_url}
                if self._server_secret:
                    tool_payload["server"]["secret"] = self._server_secret
            enabled_tools.append(tool_payload)

        model_payload: Dict[str, Any] = {
            "provider": model_provider,
            "model": model_name,
        }
        if temperature is not None:
            model_payload["temperature"] = temperature
        if max_tokens:
            model_payload["maxTokens"] = max_tokens
        if instructions:
            model_payload["messages"] = [
                {
                    "role": "system",
                    "content": instructions,
                }
            ]
        if enabled_tools:
            model_payload["tools"] = enabled_tools

        payload = {
            "name": f"{business_name} Voice Agent",
            "model": model_payload,
            "voice": {
                "provider": voice_provider,
                "voiceId": voice_id,
            },
            "firstMessage": first_message,
            "metadata": {"business_id": business_id},
        }

        # Route tool-calls to our webhook server
        if server_url:
            payload["server"] = {"url": server_url}
            if self._server_secret:
                payload["server"]["secret"] = self._server_secret

        return payload

    async def _persist_assistant_id(self, business_id: str, assistant_id: str) -> None:
        db = self._require_database(optional=True)
        if db is None:
            return

        await db.business_configs.update_one(
            {"business_id": business_id},
            {"$set": {"voice_config.vapi_assistant_id": assistant_id}}
        )
        config_loader.invalidate_cache(business_id)

    async def reset_assistant(self, business_id: str) -> None:
        """Forcibly drop cached + stored assistant so a new one is created."""

        self.invalidate_assistant_cache(business_id)
        settings.VAPI_ASSISTANT_ID = None

        db = self._require_database(optional=True)
        if db is None:
            return

        await db.business_configs.update_one(
            {"business_id": business_id},
            {"$unset": {"voice_config.vapi_assistant_id": ""}}
        )
        config_loader.invalidate_cache(business_id)

    def _resolve_voice_id(self, provider: str, requested_voice: str) -> str:
        if provider != "11labs":
            return requested_voice

        mapping = {
            "rachel": "21m00Tcm4TlvDq8ikWAM",
            "bella": "EXAVITQu4vr4xnSDxMaL",
            "domi": "AZnzlk1XvdvUeBnXmlld",
            "antoni": "ErXwobaYiN019PkySvjV",
            "matthew": "Yko7PKHZNXotIFUBG7I9",
        }
        normalized = requested_voice.lower()
        return mapping.get(normalized, requested_voice)

    async def _ensure_voice_agent_enabled(self, business_id: str) -> None:
        config = await self._get_business_config(business_id)
        if not config:
            # If no config exists, assume voice agent is enabled from ENV
            if not settings.VOICE_AGENT_ENABLED:
                raise ValueError("Voice agent disabled in environment settings")
            return
            
        features = (config or {}).get("features_enabled") or {}
        if not features.get("voice_agent"):
            raise ValueError("Voice agent disabled for this business")

    async def _get_business_config(self, business_id: str) -> Dict[str, Any]:
        db = self._require_database()
        return await config_loader.get_config(db, business_id)

    def _require_database(self, optional: bool = False):
        db = get_database()
        if db is None and not optional:
            raise ValueError("Mongo database unavailable")
        return db

    def _voice_provider_name(self) -> str:
        return "11labs" if settings.ELEVENLABS_API_KEY else "openai"

    async def _create_webrtc_session(self, assistant_id: str, business_id: str) -> Dict[str, Any]:
        """Best-effort helper that requests a WebRTC session token from Vapi."""

        client = self._require_client()
        try:
            session = await client.create_session({
                "assistantId": assistant_id,
                "device": {
                    "type": "web",
                    "publicKey": settings.VOICE_AGENT_WEBRTC_PUBLIC_KEY,
                },
                "metadata": {"business_id": business_id},
            })
            return session if isinstance(session, dict) else {}
        except Exception as exc:
            logger.warning("Unable to create Vapi WebRTC session token: %s", exc)
            return {}

    async def _handle_tool_calls_message(
        self,
        message: Dict[str, Any],
        business_id: Optional[str],
    ) -> Dict[str, Any]:
        tool_calls = self._as_list(
            message.get("toolCallList")
            or message.get("tool_call_list")
            or message.get("tool_calls")
            or message.get("toolCalls")
            or message.get("functionCallList")
        )
        if not tool_calls:
            logger.warning("Received tool-calls message without toolCallList")
            return {"error": "no_tool_calls"}

        resolved_business_id = self._resolve_business_id_from_message(message, business_id)
        call_context = self._extract_call_payload(message)
        contact_id = self._resolve_call_contact_id(call_context)
        results: List[Dict[str, Any]] = []
        errors: List[str] = []

        for tool_call in tool_calls:
            result = await self._execute_tool_call(
                tool_call,
                resolved_business_id,
                call_context=call_context,
                contact_id=contact_id,
            )
            results.append(result)
            if result.get("error"):
                errors.append(f"{result.get('name', 'unknown')}: {result['error']}")

        response: Dict[str, Any] = {"results": results}
        if errors:
            response["error"] = "; ".join(errors)
        return response

    async def _execute_tool_call(
        self,
        tool_call: Dict[str, Any],
        business_id: str,
        call_context: Optional[Dict[str, Any]] = None,
        contact_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        tool_call_id = str(tool_call.get("id") or tool_call.get("toolCallId") or uuid.uuid4().hex)
        function = self._as_dict(tool_call.get("function"))
        tool_name = function.get("name")

        result_payload: Dict[str, Any] = {
            "toolCallId": tool_call_id,
            "name": tool_name or "unknown",
            "metadata": {"business_id": business_id},
        }

        if not tool_name:
            result_payload["error"] = "Missing tool name"
            return result_payload

        try:
            arguments = self._parse_tool_call_arguments(function.get("arguments"))
        except ValueError as exc:
            result_payload["error"] = str(exc)
            return result_payload

        arguments = self._enrich_tool_arguments(arguments, call_context, contact_id)

        execution = await voice_tools.execute_tool(tool_name, arguments, business_id)
        if execution.get("success", True):
            result_payload["result"] = self._serialize_tool_result(execution)
        else:
            result_payload["error"] = execution.get("error", "Unknown tool error")

        return result_payload

    def _resolve_business_id_from_message(self, message: Dict[str, Any], fallback: Optional[str]) -> str:
        call_payload = self._extract_call_payload(message)
        metadata = self._as_dict(self._safe_get(call_payload, "metadata", {}))
        if not metadata:
            metadata = self._as_dict(message.get("metadata"))
        return metadata.get("business_id") or fallback or "default"

    @staticmethod
    def _parse_tool_call_arguments(raw_arguments: Any) -> Dict[str, Any]:
        if raw_arguments is None:
            return {}
        if isinstance(raw_arguments, dict):
            return raw_arguments
        if isinstance(raw_arguments, str):
            raw_arguments = raw_arguments.strip()
            if not raw_arguments:
                return {}
            try:
                parsed = json.loads(raw_arguments)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid tool arguments JSON: {exc}") from exc
            if isinstance(parsed, dict):
                return parsed
            raise ValueError("Tool arguments must be a JSON object")
        raise ValueError("Unsupported tool arguments format")

    @staticmethod
    def _serialize_tool_result(result: Any) -> str:
        try:
            return json.dumps(result, default=VapiAgentService._json_default)
        except TypeError:
            return json.dumps({"value": str(result)})

    @staticmethod
    def _json_default(value: Any) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, timedelta):
            return value.total_seconds()
        return str(value)

    @staticmethod
    def _extract_server_message(payload: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            return {}
        message = payload.get("message")
        if isinstance(message, dict):
            return message
        return payload

    def _resolve_call_contact_id(self, call_payload: Optional[Dict[str, Any]]) -> Optional[str]:
        if not isinstance(call_payload, dict):
            return None

        metadata = self._as_dict(self._safe_get(call_payload, "metadata", {}))
        customer = self._as_dict(self._safe_get(call_payload, "customer", {}))
        call_id = self._safe_get(call_payload, "call_id") or self._safe_get(call_payload, "id")

        candidates = [
            customer.get("number"),
            customer.get("phone"),
            metadata.get("customer_phone"),
            metadata.get("client_phone"),
            metadata.get("phone_number"),
            metadata.get("voice_contact_id"),
        ]

        for candidate in candidates:
            normalized = self._normalize_phone(candidate)
            if normalized:
                return normalized

        if call_id:
            return f"voice_{call_id}"
        return None

    @staticmethod
    def _normalize_phone(value: Optional[Any]) -> Optional[str]:
        if not value:
            return None
        cleaned = text_formatter.clean_phone_number(str(value))
        return cleaned or None

    def _enrich_tool_arguments(
        self,
        arguments: Dict[str, Any],
        call_context: Optional[Dict[str, Any]],
        contact_id: Optional[str],
    ) -> Dict[str, Any]:
        call_context = call_context or {}
        metadata = self._as_dict(self._safe_get(call_context, "metadata", {}))
        customer = self._as_dict(self._safe_get(call_context, "customer", {}))

        if not arguments.get("client_name"):
            arguments["client_name"] = metadata.get("customer_name") or customer.get("name")

        if not arguments.get("client_phone"):
            phone_candidates = [
                metadata.get("customer_phone"),
                metadata.get("client_phone"),
                customer.get("number"),
                customer.get("phone"),
                contact_id if contact_id and contact_id.startswith("+") else None,
            ]
            for candidate in phone_candidates:
                normalized = self._normalize_phone(candidate)
                if normalized:
                    arguments["client_phone"] = normalized
                    break

        # Preserve a traceable contact for records even if no phone digits exist
        if contact_id and not arguments.get("client_phone"):
            arguments["contact_reference"] = contact_id

        return arguments

    @staticmethod
    def _safe_get(obj: Any, key: str, default: Any = None) -> Any:
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    @staticmethod
    def _as_dict(value: Any) -> Dict[str, Any]:
        if value is None:
            return {}
        if hasattr(value, "model_dump"):
            return value.model_dump()
        if isinstance(value, dict):
            return value
        return dict(value) if hasattr(value, "items") else {}

    @staticmethod
    def _as_list(value: Any) -> List[Dict[str, Any]]:
        if value is None:
            return []
        if hasattr(value, "model_dump"):
            dumped = value.model_dump()
            if isinstance(dumped, list):
                return dumped
        if isinstance(value, list):
            return [item if isinstance(item, dict) else {} for item in value]
        return []

    @staticmethod
    def _extract_call_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            return {}
        if isinstance(payload.get("call"), dict):
            return payload["call"]
        data = payload.get("data")
        if isinstance(data, dict):
            if isinstance(data.get("call"), dict):
                return data["call"]
            return data
        return payload

    @staticmethod
    def _coerce_datetime(value: Any) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                normalized = value.replace("Z", "+00:00")
                return datetime.fromisoformat(normalized)
            except ValueError:
                pass
        return datetime.utcnow()


voice_agent_service = VapiAgentService()
