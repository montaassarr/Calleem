"""Voice agent API endpoints"""

from fastapi import APIRouter, HTTPException, Depends, Query, Header
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import logging

from voice_agent.vapi_agent import voice_agent_service
from voice_agent.tools import voice_tools
from models.business_config import VoiceConfiguration
from routers.users import get_current_user
from database.mongo_config import get_database
from services.elevenlabs_service import elevenlabs_service
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


class StartCallRequest(BaseModel):
	customer_number: str = Field(..., description="E.164 phone number")
	customer_name: Optional[str] = None
	metadata: Optional[Dict[str, Any]] = None


class VoiceWebRTCResponse(BaseModel):
	assistant_id: str
	public_key: str
	session_token: str
	expires_at: str
	business_id: str
	session: Optional[Dict[str, Any]] = None


async def get_business_id(x_business_id: Optional[str] = Header(None)) -> str:
	"""Normalize business ID header"""
	return x_business_id or "default"


@router.post("/start-call")
async def start_voice_call(
	payload: StartCallRequest,
	business_id: str = Depends(get_business_id),
	current_user: dict = Depends(get_current_user)
):
	"""Demo: Log call request (not actually making calls in local mode)"""
	try:
		db = get_database()
		if db is None:
			raise HTTPException(status_code=500, detail="Database unavailable")
		
		# Log the call attempt
		call_doc = {
			"call_id": f"demo_{datetime.utcnow().timestamp()}",
			"customer_number": payload.customer_number,
			"customer_name": payload.customer_name,
			"status": "demo_mode",
			"business_id": business_id,
			"created_at": datetime.utcnow(),
			"metadata": payload.metadata or {},
			"note": "Local demo mode - no actual call made"
		}
		
		await db.voice_calls.insert_one(call_doc)
		
		return {
			"status": "demo_logged",
			"call_id": call_doc["call_id"],
			"message": "Call logged in demo mode. In production, this would trigger a real voice call."
		}
	except Exception as exc:
		logger.error("Failed to start voice call: %s", exc, exc_info=True)
		raise HTTPException(status_code=500, detail=str(exc))


@router.get("/test-agent")
async def test_voice_agent(
	business_id: str = Depends(get_business_id),
	current_user: dict = Depends(get_current_user)
):
	"""Test voice agent configuration"""
	try:
		db = get_database()
		if db is None:
			raise HTTPException(status_code=500, detail="Database unavailable")
		
		# Get config
		config = await db.business_configs.find_one({"business_id": business_id})
		voice_config = config.get("voice_config", {}) if config else {}
		
		return {
			"status": "ok",
			"mode": "local",
			"groq_model": voice_config.get("model_name", "llama-3.3-70b-versatile"),
			"voice_provider": voice_config.get("voice_provider", "openai"),
			"voice_id": voice_config.get("voice_id", "alloy"),
			"enabled_tools": voice_config.get("enabled_tools", ["check_availability", "book_appointment"])
		}
	except Exception as exc:
		logger.error("Voice agent test failed: %s", exc, exc_info=True)
		raise HTTPException(status_code=500, detail=str(exc))


@router.get("/test")
async def voice_test(
	business_id: str = Depends(get_business_id),
	current_user: dict = Depends(get_current_user)
):
	"""Simple voice agent test - returns config info for local demo"""
	try:
		db = get_database()
		if db is None:
			raise HTTPException(status_code=500, detail="Database unavailable")
		
		config = await db.business_configs.find_one({"business_id": business_id})
		voice_config = config.get("voice_config", {}) if config else {}
		
		# Return simple test response
		return {
			"status": "ok",
			"mode": "local_demo",
			"message": "Voice agent configured for local testing",
			"config": {
				"model": voice_config.get("model_name", "llama-3.3-70b-versatile"),
				"provider": voice_config.get("model_provider", "groq"),
				"voice": voice_config.get("voice_id", "alloy"),
				"enabled_tools": voice_config.get("enabled_tools", ["check_availability", "book_appointment", "get_services"])
			}
		}
	except Exception as exc:
		logger.error("Voice test failed: %s", exc, exc_info=True)
		raise HTTPException(status_code=500, detail=str(exc))


@router.get("/call-history")
async def call_history(
	limit: int = Query(20, ge=1, le=100),
	business_id: str = Depends(get_business_id),
	current_user: dict = Depends(get_current_user)
):
	"""Get voice call history"""
	try:
		db = get_database()
		if db is None:
			raise HTTPException(status_code=500, detail="Database unavailable")
		
		cursor = db.voice_calls.find({"business_id": business_id}).sort("created_at", -1).limit(limit)
		calls = await cursor.to_list(length=limit)
		
		# Convert ObjectId to string
		for call in calls:
			call["id"] = str(call.get("_id", ""))
			if "_id" in call:
				del call["_id"]
		
		return {"items": calls, "count": len(calls)}
	except Exception as exc:
		logger.error("Failed to fetch call history: %s", exc, exc_info=True)
		raise HTTPException(status_code=500, detail=str(exc))


@router.post("/webhook", include_in_schema=False)
async def vapi_webhook(
	payload: Dict[str, Any],
	business_id: str = Depends(get_business_id)
):
	"""Vapi webhook receiver that keeps voice + WhatsApp flows in sync."""
	try:
		result = await voice_agent_service.ingest_webhook_event(payload, business_id=business_id)
		return result
	except Exception as exc:
		logger.error("Voice webhook ingestion failed: %s", exc, exc_info=True)
		# Return 200 so Vapi does not retry endlessly but include error signal.
		return {"status": "error", "detail": str(exc)}


@router.get("/config")
async def get_voice_config(
	business_id: str = Depends(get_business_id),
	current_user: dict = Depends(get_current_user)
):
	"""Get voice agent configuration for this business"""
	try:
		db = get_database()
		if db is None:
			raise HTTPException(status_code=500, detail="Database unavailable")
		
		config = await db.business_configs.find_one({"business_id": business_id})
		if not config:
			# Return default config if none exists
			return {
				"model_provider": "groq",
				"model_name": "llama-3.3-70b-versatile",
				"temperature": 0.7,
				"max_tokens": 500,
				"voice_provider": "openai",
				"voice_id": "alloy",
				"first_message": "Hi, this is Ava from Royal Fade. How can I help you today?",
				"system_prompt": "",
				"enabled_tools": ["check_availability", "book_appointment", "get_services"],
				"end_call_on_goodbye": True,
				"record_calls": True,
				"silence_timeout_seconds": 30
			}
		
		voice_config = config.get("voice_config", {})
		if not voice_config:
			# Return default if empty
			voice_config = {
				"model_provider": "groq",
				"model_name": "llama-3.3-70b-versatile",
				"temperature": 0.7,
				"max_tokens": 500,
				"voice_provider": "openai",
				"voice_id": "alloy",
				"first_message": "Hi, this is Ava from Royal Fade. How can I help you today?",
				"system_prompt": "",
				"enabled_tools": ["check_availability", "book_appointment", "get_services"],
				"end_call_on_goodbye": True,
				"record_calls": True,
				"silence_timeout_seconds": 30
			}
		return voice_config
	except HTTPException:
		raise
	except Exception as exc:
		logger.error("Failed to fetch voice config: %s", exc, exc_info=True)
		raise HTTPException(status_code=500, detail=str(exc))


@router.put("/config")
async def update_voice_config(
	config_update: VoiceConfiguration,
	business_id: str = Depends(get_business_id),
	current_user: dict = Depends(get_current_user)
):
	"""Update voice agent configuration"""
	try:
		db = get_database()
		if db is None:
			raise HTTPException(status_code=500, detail="Database unavailable")
		
		# First, ensure business config exists
		existing = await db.business_configs.find_one({"business_id": business_id})
		if not existing:
			# Create new config document
			await db.business_configs.insert_one({
				"business_id": business_id,
				"voice_config": config_update.model_dump(),
				"created_at": datetime.utcnow(),
				"updated_at": datetime.utcnow()
			})
		else:
			# Update existing
			await db.business_configs.update_one(
				{"business_id": business_id},
				{
					"$set": {
						"voice_config": config_update.model_dump(),
						"updated_at": datetime.utcnow()
					}
				}
			)
		
		return {"status": "success", "message": "Voice configuration updated"}
	except HTTPException:
		raise
	except Exception as exc:
		logger.error("Failed to update voice config: %s", exc, exc_info=True)
		raise HTTPException(status_code=500, detail=str(exc))


@router.get("/models")
async def get_available_models(
	current_user: dict = Depends(get_current_user)
):
	"""Get list of available LLM models"""
	return {
		"groq": [
			{"id": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B", "provider": "groq"},
			{"id": "llama-3.1-70b-versatile", "name": "Llama 3.1 70B", "provider": "groq"},
			{"id": "mixtral-8x7b-32768", "name": "Mixtral 8x7B", "provider": "groq"},
		],
		"openai": [
			{"id": "gpt-4o", "name": "GPT-4o", "provider": "openai"},
			{"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "provider": "openai"},
			{"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "provider": "openai"},
		]
	}


@router.get("/tools")
async def get_available_tools(
	current_user: dict = Depends(get_current_user)
):
	"""Get list of available voice agent tools"""
	return {
		"tools": voice_tools.get_tool_definitions()
	}


@router.get("/voices")
async def get_available_voices(
	force_refresh: bool = Query(False),
	current_user: dict = Depends(get_current_user)
):
	"""Get list of available voices (ElevenLabs + OpenAI)"""
	try:
		voices = await elevenlabs_service.get_voices(force_refresh=force_refresh)
		return {
			"voices": voices,
			"count": len(voices),
			"elevenlabs_configured": elevenlabs_service.is_configured()
		}
	except Exception as exc:
		logger.error("Failed to fetch voices: %s", exc, exc_info=True)
		raise HTTPException(status_code=500, detail=str(exc))


@router.get("/vapi-config")
async def get_vapi_config(
	business_id: str = Depends(get_business_id),
	current_user: dict = Depends(get_current_user)
):
	"""Get Vapi configuration for client-side initialization"""
	try:
		from services.vapi_service import vapi_service
		
		if not vapi_service.is_configured():
			raise HTTPException(
				status_code=503,
				detail="Vapi is not configured. Please set VAPI_API_KEY and VAPI_PUBLIC_KEY in .env"
			)
		
		# Get or create assistant based on voice configuration
		db = get_database()
		if db is None:
			raise HTTPException(status_code=500, detail="Database unavailable")
		
		voice_config_doc = await db.business_config.find_one({"business_id": business_id})
		
		if not voice_config_doc or "voice_config" not in voice_config_doc:
			# Return default configuration
			voice_config = {
				"model": "groq:llama-3.3-70b-versatile",
				"voice": "elevenlabs:Rachel",
				"first_message": "Hello! Welcome to our service. How can I help you today?",
				"system_prompt": "You are a helpful AI receptionist. Be friendly, professional, and concise.",
				"temperature": 0.7
			}
		else:
			voice_config = voice_config_doc["voice_config"]
		
		# Get enabled tools
		enabled_tools = voice_config.get("enabled_tools", [])
		tools = [tool for tool in voice_tools if tool["name"] in enabled_tools] if enabled_tools else []
		
		# Check if we already have an assistant ID stored
		assistant_id = voice_config.get("vapi_assistant_id")
		
		# If no assistant ID or it doesn't exist, create one
		if not assistant_id:
			assistant_id = vapi_service.create_or_update_assistant(voice_config, tools)
			
			if assistant_id:
				# Store the assistant ID in the database
				await db.business_config.update_one(
					{"business_id": business_id},
					{"$set": {"voice_config.vapi_assistant_id": assistant_id}},
					upsert=True
				)
			else:
				raise HTTPException(
					status_code=500,
					detail="Failed to create Vapi assistant"
				)
		
		public_key = vapi_service.get_public_key()
		
		if not public_key:
			raise HTTPException(
				status_code=503,
				detail="VAPI_PUBLIC_KEY not configured in .env"
			)
		
		return {
			"publicKey": public_key,
			"assistantId": assistant_id
		}
		
	except HTTPException:
		raise
	except Exception as exc:
		logger.error("Failed to get Vapi config: %s", exc, exc_info=True)
		raise HTTPException(status_code=500, detail=str(exc))


@router.post("/webhook", include_in_schema=False)
async def vapi_webhook(
	payload: Dict[str, Any],
	business_id: str = Depends(get_business_id)
):
	"""Vapi webhook receiver that keeps voice + WhatsApp flows in sync."""
	try:
		result = await voice_agent_service.ingest_webhook_event(payload, business_id=business_id)
		return result
	except Exception as exc:
		logger.error("Voice webhook ingestion failed: %s", exc, exc_info=True)
		# Return 200 so Vapi does not retry endlessly but include error signal.
		return {"status": "error", "detail": str(exc)}
