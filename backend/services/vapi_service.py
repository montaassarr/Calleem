"""
Vapi Voice AI Service - Comprehensive Integration
Manages tenant assistant through Vapi API with full configuration support
"""

import os
import logging
import hmac
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class VapiService:
    """
    Comprehensive Vapi AI integration service.
    Handles assistant management, voice config, knowledge base, tools, and analytics.
    """
    ALLOWED_SERVER_MESSAGES = {
        "assistant.started",
        "conversation-update",
        "end-of-call-report",
        "function-call",
        "hang",
        "language-changed",
        "language-change-detected",
        "model-output",
        "phone-call-control",
        "speech-update",
        "status-update",
        "tool-calls",
        "transcript",
        'transcript[transcriptType="final"]',
        "transfer-destination-request",
        "handoff-destination-request",
        "transfer-update",
        "user-interrupted",
        "voice-input",
        "chat.created",
        "chat.deleted",
        "session.created",
        "session.updated",
        "session.deleted",
        "call.deleted",
        "call.delete.failed"
    }

    DEFAULT_SERVER_MESSAGES = [
        "assistant.started",
        "conversation-update",
        "function-call",
        "tool-calls",
        "status-update",
        "transcript",
        'transcript[transcriptType="final"]',
        "end-of-call-report",
        "user-interrupted",
        "voice-input"
    ]
    
    def __init__(self):
        self.api_key = (
            os.getenv("VAPI_PRIVATE_KEY")
            or os.getenv("VAPI_PRIVATE_API_KEY")
            or os.getenv("VAPI_API_KEY")
        )
        self.public_key = os.getenv("VAPI_PUBLIC_KEY")
        self.webhook_bearer_token = os.getenv("VAPI_WEBHOOK_BEARER_TOKEN", "")
        self.organization_id = os.getenv("VAPI_ORGANIZATION_ID", "")
        self.base_url = os.getenv("VAPI_BASE_URL", "https://api.vapi.ai")
        
        if not self.api_key:
            logger.warning("VAPI_API_KEY not configured - Vapi features disabled")
        else:
            logger.info("Vapi service initialized successfully")
    
    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def is_configured(self) -> bool:
        return bool(self.api_key)
    
    # ===== ASSISTANT MANAGEMENT =====
    
    async def create_assistant(
        self,
        tenant_id: str,
        company_name: str,
        instructions: str,
        first_message: Optional[str] = None,
        voice: str = "jennifer",
        model: str = "gpt-4o-mini",
        voice_provider: str = "11labs",
        voice_speed: float = 1.0,
        temperature: float = 0.7,
        max_tokens: int = 525,
        transcriber_provider: str = "deepgram",
        transcriber_model: str = "nova-2",
        transcriber_language: str = "en",
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new Vapi assistant for a tenant"""
        if not self.is_configured():
            raise ValueError("Vapi not configured")
        
        system_prompt = f"""You are an AI receptionist for {company_name}. You are Ahmed, the friendly and professional AI receptionist at {company_name} — a premium business that offers welcoming service, clear communication, and easy booking.

{instructions}

    ### Core Rules (always follow):
    - Use short, natural sentences. Keep responses brief and easy to understand.
    - Be polite, patient, enthusiastic, and slightly casual/friendly.
    - Ask only one question at a time to keep the conversation smooth.
    - Always confirm details clearly before booking.
    - Match the client's energy and language style.

    ### Greeting (First message - use this exactly):
    "Hello! Welcome to {company_name}. This is Ahmed speaking, how can I help you today?"

    ### How to handle calls (smooth flow):
    1. Booking an appointment:
    - Ask for their name.
    - Ask what service they want.
    - Ask for preferred date and time.
    - ALWAYS call getCurrentDateTime() before resolving relative dates like today/tomorrow/next Friday.
    - Convert relative dates to YYYY-MM-DD using the timezone returned by getCurrentDateTime().
    - Check availability with checkAvailability(date) using the CORRECT future date
    - Ask for confirmation.
    - Book with bookAppointment using the CORRECT date format

    2. Other common requests:
    - Prices or services: Give clear info and then offer to book a slot.
    - Reschedule or cancel: Ask for name and original appointment details first.
    - Same-day / walk-in: Be honest about availability and offer options.
    - General questions: Answer helpfully and gently guide back to booking.

    3. Booking confirmation (after they confirm):
    "Perfect! Your appointment is confirmed for [Date] at [Time] for a [Service] under the name [Name]. We'll send you a reminder the day before. Looking forward to seeing you at {company_name}!"

    ### Tone & Style:
    - Warm and welcoming: Use words like "Awesome!", "No problem at all!", "Sounds good!", "Great choice!", "Happy to help!"
    - Positive and solution-oriented.
    - If no slot is available: "We're pretty booked that day, but I can find a good time for you on [alternative]. Does that work?"
    - Make every client feel valued and comfortable.
    - If the client is in a hurry, keep it quick and efficient.

    ### Tools:
    - getCurrentDateTime(): MUST call this first whenever a user gives relative date/time terms (today, tomorrow, this Friday, next week).
    - getAvailableServices(): Fetch current service offerings when the customer asks about services or pricing.
    - getBusinessLocation(): Fetch the exact business location/address when the customer asks where the business is located.
    - checkAvailability(date): Check available appointment slots. Date must be in YYYY-MM-DD format.
    - bookAppointment(date, time, name, phone, email, service): Book an appointment. Date must be YYYY-MM-DD, time must be HH:MM (24-hour).

    ### Critical Guidelines:
    - NEVER book appointments in the past.
    - ALWAYS resolve relative dates by calling getCurrentDateTime() first.
    - ALWAYS use YYYY-MM-DD format for dates (examples: 2026-04-19, 2026-04-25)
    - ALWAYS use HH:MM format for times in 24-hour time (11:00, 14:30, 09:00)
    - ALWAYS call getAvailableServices() when customer asks about services or pricing.
    - ALWAYS call getBusinessLocation() when customer asks about location/address/directions.
    - Be professional, friendly, and helpful.
    - Speak naturally and conversationally.
    - If you need to book an appointment, collect: name, phone, email, preferred date/time.
    - If you don't know something, offer to have someone call back.
    - Keep responses concise for voice conversation.
    """
        
        requested_server_messages = kwargs.pop("server_messages", self.DEFAULT_SERVER_MESSAGES)
        valid_server_messages = [
            msg for msg in requested_server_messages
            if msg in self.ALLOWED_SERVER_MESSAGES
        ]
        if not valid_server_messages:
            logger.warning("No valid serverMessages provided; falling back to defaults")
            valid_server_messages = self.DEFAULT_SERVER_MESSAGES

        assistant_config = {
            "name": f"AI Receptionist - {company_name}"[:40],
            "firstMessage": first_message or f"Hello! Welcome to {company_name}. This is Ahmed speaking, how can I help you today?",
            "model": {
                "provider": "openai",
                "model": model,
                "temperature": temperature,
                "maxTokens": max_tokens,
                "messages": [
                    {"role": "system", "content": system_prompt}
                ]
            },
            "voice": {
                "provider": voice_provider,
                "voiceId": self._get_voice_id(voice, voice_provider),
                "speed": voice_speed
            },
            "transcriber": {
                "provider": transcriber_provider,
                "model": transcriber_model,
                "language": transcriber_language
            },
            "serverUrl": os.getenv("VAPI_WEBHOOK_URL", ""),
            # Ensure webhook events are delivered to our server per Vapi docs
            # https://docs.vapi.ai/api-reference/webhooks/server-message
            "serverMessages": valid_server_messages,
            "metadata": {
                "tenant_id": tenant_id,
                "company_name": company_name
            }
        }
        
        # Add tools if provided
        if tools:
            assistant_config["tools"] = self._normalize_tool_definitions(tools)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/assistant",
                    headers=self.headers,
                    json=assistant_config
                )
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"Created Vapi assistant {result.get('id')} for tenant {tenant_id}")
                
                return {
                    "assistant_id": result.get("id"),
                    "name": result.get("name"),
                    "voice": voice,
                    "model": model,
                    "created": True
                }
        except httpx.HTTPError as e:
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Vapi API Error Body: {e.response.text}")
            logger.error(f"Failed to create Vapi assistant: {e}")
            raise
    
    async def update_assistant(
        self,
        assistant_id: str,
        company_name: Optional[str] = None,
        instructions: Optional[str] = None,
        first_message: Optional[str] = None,
        voice: Optional[str] = None,
        voice_provider: str = "11labs",
        voice_speed: Optional[float] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Update an existing Vapi assistant"""
        if not self.is_configured():
            raise ValueError("Vapi not configured")
        
        # Fetch current assistant to preserve model config if needed
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                current = await client.get(
                    f"{self.base_url}/assistant/{assistant_id}",
                    headers=self.headers
                )
                if current.status_code == 200:
                    current_data = current.json()
                    current_model = current_data.get("model", {})
                else:
                    logger.warning(f"Could not fetch assistant {assistant_id} for merge, assuming defaults")
                    current_model = {
                        "provider": "openai",
                        "model": "gpt-4o-mini",
                        "messages": []
                    }
            except Exception as e:
                logger.error(f"Error fetching assistant for merge: {e}")
                current_model = {
                    "provider": "openai", 
                    "model": "gpt-4o-mini"
                }

        update_data = {}
        
        if first_message:
            update_data["firstMessage"] = first_message
        
        if instructions and company_name:
            system_prompt = f"""You are an AI receptionist for {company_name}. You are Ahmed, the friendly and professional AI receptionist at {company_name}.

{instructions}

Core behavior:
- Use short, natural sentences.
- Be polite, patient, enthusiastic, and slightly casual/friendly.
- Ask only one question at a time.
- Always confirm details clearly before booking.
- Match the client's energy and language style.

Greeting:
"Hello! Welcome to {company_name}. This is Ahmed speaking, how can I help you today?"

Tone:
- Warm and welcoming.
- Positive and solution-oriented.
- Keep responses concise for voice conversation.

Important guidelines:
 - ALWAYS call getCurrentDateTime() before resolving relative dates (today/tomorrow/next week).
- ALWAYS call getAvailableServices() when customer asks about services or pricing.
- ALWAYS call getBusinessLocation() when customer asks about location/address/directions.
- If you need to book an appointment, collect: name, phone, email, preferred date/time.
- If you don't know something, offer to have someone call back.
"""
            # Start with current model config
            new_model = current_model.copy()
            new_model["messages"] = [{"role": "system", "content": system_prompt}]
            new_model["provider"] = "openai" # Ensure provider is set
            new_model["model"] = model or "gpt-4o-mini"
            
            if temperature is not None:
                new_model["temperature"] = temperature
            if max_tokens is not None:
                new_model["maxTokens"] = max_tokens
                
            update_data["model"] = new_model
        
        if voice:
            update_data["voice"] = {
                "provider": voice_provider,
                "voiceId": self._get_voice_id(voice, voice_provider)
            }
            if voice_speed is not None:
                update_data["voice"]["speed"] = voice_speed
        
        if tools is not None:
            # Vapi expects tools under the model config on PATCH requests
            if "model" not in update_data:
                update_data["model"] = current_model.copy()
            update_data["model"]["tools"] = self._normalize_tool_definitions(tools)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.patch(
                    f"{self.base_url}/assistant/{assistant_id}",
                    headers=self.headers,
                    json=update_data
                )
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"Updated Vapi assistant {assistant_id}")
                
                return {
                    "assistant_id": result.get("id"),
                    "name": result.get("name"),
                    "updated": True
                }
        except httpx.HTTPError as e:
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Vapi API Update Error Body: {e.response.text}")
            logger.error(f"Failed to update Vapi assistant: {e}")
            raise
    
    async def get_assistant(self, assistant_id: str) -> Optional[Dict[str, Any]]:
        """Get assistant details from Vapi"""
        if not self.is_configured():
            return None
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/assistant/{assistant_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            if e.response is not None and e.response.status_code == 404:
                logger.warning(f"Assistant {assistant_id} not found in Vapi (404)")
                return None
            logger.error(f"Failed to get assistant {assistant_id}: {e}")
            return None
        except httpx.HTTPError as e:
            logger.error(f"Failed to get assistant {assistant_id}: {e}")
            return None

    async def list_assistants(self) -> List[Dict[str, Any]]:
        """List assistants from Vapi"""
        if not self.is_configured():
            return []

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/assistant",
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()

                if isinstance(data, list):
                    return data
                if isinstance(data, dict):
                    return data.get("assistants") or data.get("data") or []
                return []
        except httpx.HTTPError as e:
            logger.error(f"Failed to list assistants: {e}")
            return []

    async def delete_assistant(self, assistant_id: str) -> bool:
        """Delete a Vapi assistant"""
        if not self.is_configured():
            raise ValueError("Vapi not configured")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.delete(
                    f"{self.base_url}/assistant/{assistant_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                logger.info(f"Deleted Vapi assistant {assistant_id}")
                return True
        except httpx.HTTPError as e:
            logger.error(f"Failed to delete assistant: {e}")
            return False
    
    # ===== VOICE MANAGEMENT =====
    
    async def get_voice_providers(self) -> List[Dict[str, Any]]:
        """Get available voice providers and their voices from Vapi API"""
        if not self.is_configured():
            logger.warning("Vapi not configured, returning default voices")
            return self._get_fallback_voice_providers()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/voice",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    voices = response.json()
                    return self._group_voices_by_provider(voices)
                else:
                    logger.warning(f"Failed to fetch voices from Vapi: {response.status_code}")
                    return self._get_fallback_voice_providers()
                    
        except Exception as e:
            logger.error(f"Error fetching voices from Vapi: {e}")
            return self._get_fallback_voice_providers()
    
    def _group_voices_by_provider(self, voices: List[Dict]) -> List[Dict[str, Any]]:
        """Group voices by their provider"""
        providers = {}
        
        provider_meta = {
            "11labs": {"name": "ElevenLabs", "description": "High-quality AI voices with emotion"},
            "azure": {"name": "Azure Cognitive Services", "description": "Microsoft Azure TTS"},
            "openai": {"name": "OpenAI TTS", "description": "OpenAI text-to-speech"},
            "vapi": {"name": "Vapi Voices", "description": "Curated high-quality voices"},
            "cartesia": {"name": "Cartesia", "description": "Ultra-low latency voices"},
            "deepgram": {"name": "Deepgram", "description": "Fast and accurate TTS"},
            "playht": {"name": "PlayHT", "description": "AI voice generator"},
            "lmnt": {"name": "LMNT", "description": "Expressive AI voices"},
            "rime-ai": {"name": "Rime AI", "description": "Conversational AI voices"},
        }
        
        for voice in voices:
            provider_id = voice.get("provider", "unknown")
            
            if provider_id not in providers:
                meta = provider_meta.get(provider_id, {"name": provider_id.title(), "description": f"{provider_id} voices"})
                providers[provider_id] = {
                    "id": provider_id,
                    "name": meta["name"],
                    "description": meta["description"],
                    "voices": []
                }
            
            voice_entry = {
                "id": voice.get("voiceId") or voice.get("id"),
                "name": voice.get("name", "Unknown"),
                "gender": voice.get("gender", "neutral"),
                "accent": voice.get("accent", ""),
                "language": voice.get("language", "en"),
                "preview_url": voice.get("previewUrl"),
            }
            
            # Add additional metadata if available
            if voice.get("description"):
                voice_entry["description"] = voice.get("description")
            
            providers[provider_id]["voices"].append(voice_entry)
        
        # Sort providers by name and return as list
        return sorted(providers.values(), key=lambda x: x["name"])
    
    def _get_fallback_voice_providers(self) -> List[Dict[str, Any]]:
        """Fallback voice providers when Vapi API is unavailable"""
        return [
            {
                "id": "vapi",
                "name": "Vapi Voices",
                "description": "Curated high-quality voices - Recommended",
                "voices": [
                    {"id": "Elliot", "name": "Elliot", "gender": "male", "accent": "American", "description": "Professional male voice"},
                    {"id": "Lily", "name": "Lily", "gender": "female", "accent": "American", "description": "Warm female voice"},
                    {"id": "Rohan", "name": "Rohan", "gender": "male", "accent": "Indian", "description": "Friendly male voice"},
                    {"id": "Savannah", "name": "Savannah", "gender": "female", "accent": "American", "description": "Clear female voice"},
                    {"id": "Cole", "name": "Cole", "gender": "male", "accent": "American", "description": "Calm male voice"},
                    {"id": "Harry", "name": "Harry", "gender": "male", "accent": "British", "description": "British male voice"},
                    {"id": "Sally", "name": "Sally", "gender": "female", "accent": "American", "description": "Energetic female voice"},
                ]
            },
            {
                "id": "11labs",
                "name": "ElevenLabs",
                "description": "High-quality AI voices with emotion",
                "voices": [
                    {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Sarah", "gender": "female", "accent": "American"},
                    {"id": "pNInz6obpgDQGcFmaJgB", "name": "Adam", "gender": "male", "accent": "American"},
                    {"id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel", "gender": "female", "accent": "American"},
                    {"id": "TxGEqnHWrfWFTfGW9XjX", "name": "Josh", "gender": "male", "accent": "American"},
                    {"id": "AZnzlk1XvdvUeBnXmlld", "name": "Domi", "gender": "female", "accent": "American"},
                    {"id": "MF3mGyEYCl7XYWbV9V6O", "name": "Elli", "gender": "female", "accent": "American"},
                    {"id": "jBpfuIE2acCO8z3wKNLl", "name": "Gigi", "gender": "female", "accent": "American"},
                    {"id": "onwK4e9ZLuTAKqWW03F9", "name": "Daniel", "gender": "male", "accent": "British"},
                ]
            },
            {
                "id": "cartesia",
                "name": "Cartesia",
                "description": "Ultra-low latency voices - Best for real-time",
                "voices": [
                    {"id": "a0e99841-438c-4a64-b679-ae501e7d6091", "name": "Barbershop Man", "gender": "male", "accent": "American"},
                    {"id": "156fb8d2-335b-4950-9cb3-a2d33f6b3c11", "name": "British Woman", "gender": "female", "accent": "British"},
                    {"id": "79a125e8-cd45-4c13-8a67-188112f4dd22", "name": "California Girl", "gender": "female", "accent": "American"},
                    {"id": "c8605446-247c-4d39-acd4-8f4c28aa363c", "name": "Classy British Man", "gender": "male", "accent": "British"},
                    {"id": "5619d38c-cf51-4d8e-9575-48f61a280413", "name": "Confident Woman", "gender": "female", "accent": "American"},
                    {"id": "87748186-23bb-4f8c-a6b8-9e61e5d8f0bc", "name": "Friendly Australian Man", "gender": "male", "accent": "Australian"},
                    {"id": "bf991597-6c23-4e41-bd1e-41952ff5a5bc", "name": "Warm Woman", "gender": "female", "accent": "American"},
                ]
            },
            {
                "id": "openai",
                "name": "OpenAI TTS",
                "description": "OpenAI text-to-speech",
                "voices": [
                    {"id": "alloy", "name": "Alloy", "gender": "neutral", "accent": "American"},
                    {"id": "echo", "name": "Echo", "gender": "male", "accent": "American"},
                    {"id": "fable", "name": "Fable", "gender": "neutral", "accent": "British"},
                    {"id": "onyx", "name": "Onyx", "gender": "male", "accent": "American"},
                    {"id": "nova", "name": "Nova", "gender": "female", "accent": "American"},
                    {"id": "shimmer", "name": "Shimmer", "gender": "female", "accent": "American"},
                ]
            },
            {
                "id": "azure",
                "name": "Azure Cognitive Services",
                "description": "Microsoft Azure TTS - Enterprise grade",
                "voices": [
                    {"id": "en-US-JennyNeural", "name": "Jenny", "gender": "female", "accent": "American"},
                    {"id": "en-US-GuyNeural", "name": "Guy", "gender": "male", "accent": "American"},
                    {"id": "en-GB-SoniaNeural", "name": "Sonia", "gender": "female", "accent": "British"},
                    {"id": "en-GB-RyanNeural", "name": "Ryan", "gender": "male", "accent": "British"},
                    {"id": "en-AU-NatashaNeural", "name": "Natasha", "gender": "female", "accent": "Australian"},
                    {"id": "en-IN-NeerjaNeural", "name": "Neerja", "gender": "female", "accent": "Indian"},
                ]
            },
            {
                "id": "deepgram",
                "name": "Deepgram",
                "description": "Fast and accurate TTS",
                "voices": [
                    {"id": "aura-asteria-en", "name": "Asteria", "gender": "female", "accent": "American"},
                    {"id": "aura-luna-en", "name": "Luna", "gender": "female", "accent": "American"},
                    {"id": "aura-stella-en", "name": "Stella", "gender": "female", "accent": "American"},
                    {"id": "aura-athena-en", "name": "Athena", "gender": "female", "accent": "British"},
                    {"id": "aura-hera-en", "name": "Hera", "gender": "female", "accent": "American"},
                    {"id": "aura-orion-en", "name": "Orion", "gender": "male", "accent": "American"},
                    {"id": "aura-arcas-en", "name": "Arcas", "gender": "male", "accent": "American"},
                    {"id": "aura-perseus-en", "name": "Perseus", "gender": "male", "accent": "American"},
                ]
            },
            {
                "id": "playht",
                "name": "PlayHT",
                "description": "AI voice generator with cloning",
                "voices": [
                    {"id": "jennifer", "name": "Jennifer", "gender": "female", "accent": "American"},
                    {"id": "michael", "name": "Michael", "gender": "male", "accent": "American"},
                    {"id": "emma", "name": "Emma", "gender": "female", "accent": "British"},
                    {"id": "james", "name": "James", "gender": "male", "accent": "British"},
                ]
            }
        ]
    
    async def preview_voice(self, voice_id: str, text: str, provider: str = "11labs") -> Optional[bytes]:
        """Generate voice preview audio (returns audio bytes)"""
        # This would typically call the TTS provider's API directly
        # For now, return None - frontend can use Vapi's built-in preview
        logger.info(f"Voice preview requested for {voice_id} with provider {provider}")
        return None
    
    # ===== PHONE NUMBER MANAGEMENT =====
    
    async def create_sip_credential(
        self,
        account_sid: str,
        auth_token: str,
        name: str = "Twilio SIP Trunk"
    ) -> Dict[str, Any]:
        """
        Create SIP credential in Vapi for Twilio integration
        
        Args:
            account_sid: Twilio Account SID
            auth_token: Twilio Auth Token
            name: Credential name
            
        Returns:
            Vapi credential object with ID
        """
        if not self.is_configured():
            raise ValueError("Vapi not configured")
        
        payload = {
            "provider": "twilio",
            "twilioAccountSid": account_sid,
            "twilioAuthToken": auth_token,
            "name": name
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/credential",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                logger.info(f"Created Vapi SIP credential: {result.get('id')}")
                return result
        except httpx.HTTPError as e:
            logger.error(f"Failed to create SIP credential: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise
    
    async def import_twilio_number(
        self,
        phone_number: str,
        assistant_id: str,
        credential_id: str,
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Import an existing Twilio number to Vapi
        
        Args:
            phone_number: Phone number in E.164 format (+1234567890)
            assistant_id: Vapi assistant ID to assign to this number
            credential_id: Vapi credential ID (from create_sip_credential)
            name: Optional friendly name for the phone number
            
        Returns:
            Vapi phone number object with ID
        """
        if not self.is_configured():
            raise ValueError("Vapi not configured")
        
        payload = {
            "provider": "twilio",
            "number": phone_number,
            "credentialId": credential_id,
            "assistantId": assistant_id,
            "name": name or f"Phone {phone_number}"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/phone-number",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                logger.info(f"Imported Twilio number {phone_number} to Vapi: {result.get('id')}")
                return result
        except httpx.HTTPError as e:
            logger.error(f"Failed to import Twilio number: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise
    
    async def create_phone_number(self, provider: str = "twilio", area_code: str = "415") -> Dict[str, Any]:
        """Purchase/create a phone number in Vapi"""
        if not self.is_configured():
            raise ValueError("Vapi not configured")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/phone-number",
                    headers=self.headers,
                    json={
                        "provider": provider,
                        "areaCode": area_code
                    }
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to create phone number: {e}")
            raise
    
    async def assign_phone_number(self, phone_number_id: str, assistant_id: str) -> Dict[str, Any]:
        """Assign an assistant to a phone number"""
        if not self.is_configured():
            raise ValueError("Vapi not configured")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.patch(
                    f"{self.base_url}/phone-number/{phone_number_id}",
                    headers=self.headers,
                    json={"assistantId": assistant_id}
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to assign phone number: {e}")
            raise
    
    async def list_phone_numbers(self) -> List[Dict[str, Any]]:
        """List all phone numbers in the organization"""
        if not self.is_configured():
            return []
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/phone-number",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to list phone numbers: {e}")
            return []
    
    # ===== CALL MANAGEMENT =====
    
    async def make_outbound_call(
        self,
        assistant_id: str,
        customer_number: str,
        phone_number_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make an outbound call"""
        if not self.is_configured():
            raise ValueError("Vapi not configured")
        
        call_data = {
            "assistantId": assistant_id,
            "customer": {
                "number": customer_number
            }
        }
        
        if phone_number_id:
            call_data["phoneNumberId"] = phone_number_id
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/call",
                    headers=self.headers,
                    json=call_data
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to make outbound call: {e}")
            raise
    
    async def get_call(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Get call details including transcript"""
        if not self.is_configured():
            return None
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/call/{call_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get call {call_id}: {e}")
            return None
    
    async def list_calls(
        self,
        assistant_id: Optional[str] = None,
        limit: int = 100,
        created_at_gt: Optional[str] = None,
        created_at_lt: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List calls with optional filtering"""
        if not self.is_configured():
            return []
        
        params = {"limit": limit}
        if assistant_id:
            params["assistantId"] = assistant_id
        if created_at_gt:
            params["createdAtGt"] = created_at_gt
        if created_at_lt:
            params["createdAtLt"] = created_at_lt
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/call",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to list calls: {e}")
            return []
    
    # ===== FILE/KNOWLEDGE BASE MANAGEMENT =====
    
    async def upload_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Upload a file to Vapi for Knowledge Base"""
        if not self.is_configured():
            raise ValueError("Vapi not configured")
        
        import tempfile
        
        suffix = os.path.splitext(filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                with open(tmp_path, 'rb') as f:
                    files = {"file": (filename, f)}
                    headers = {"Authorization": f"Bearer {self.api_key}"}
                    response = await client.post(
                        f"{self.base_url}/file",
                        headers=headers,
                        files=files
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    logger.info(f"Uploaded file {filename} to Vapi: {result.get('id')}")
                    return {
                        "id": result.get("id"),
                        "name": result.get("name", filename),
                        "url": result.get("url"),
                        "size": result.get("bytes"),
                        "status": result.get("status", "processed")
                    }
        finally:
            os.unlink(tmp_path)
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete a file from Vapi"""
        if not self.is_configured():
            raise ValueError("Vapi not configured")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.delete(
                    f"{self.base_url}/file/{file_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                logger.info(f"Deleted file {file_id}")
                return True
        except httpx.HTTPError as e:
            logger.error(f"Failed to delete file: {e}")
            return False
    
    async def list_files(self) -> List[Dict[str, Any]]:
        """List all files in the organization"""
        if not self.is_configured():
            return []
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/file",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to list files: {e}")
            return []
    
    # ===== TOOLS MANAGEMENT =====
    
    def get_built_in_tools(self) -> List[Dict[str, Any]]:
        """Get list of built-in tools available"""
        return [
            {
                "id": "get_current_datetime",
                "name": "Get Current Date Time",
                "description": "Fetch current date and time in the tenant business timezone",
                "category": "information",
                "config": {
                    "type": "function",
                    "function": {
                        "name": "getCurrentDateTime",
                        "description": "Get current date/time in business timezone. Use this before converting relative dates like today, tomorrow, next Friday.",
                        "parameters": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }
                }
            },
            {
                "id": "check_availability",
                "name": "Check Availability",
                "description": "Check available appointment slots for a given date; use the backend-injected current date context for relative dates",
                "category": "scheduling",
                "config": {
                    "type": "function",
                    "function": {
                        "name": "checkAvailability",
                        "description": "Check available time slots for appointments. Use the backend-injected current date context when the customer asks about today, tomorrow, or other relative dates.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "date": {
                                    "type": "string",
                                    "description": "Date to check in YYYY-MM-DD format"
                                }
                            },
                            "required": ["date"]
                        }
                    }
                }
            },
            {
                "id": "book_appointment",
                "name": "Book Appointment",
                "description": "Book an appointment for the caller",
                "category": "scheduling",
                "config": {
                    "type": "function",
                    "function": {
                        "name": "bookAppointment",
                        "description": "Book an appointment for the caller",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "date": {"type": "string", "description": "Appointment date (YYYY-MM-DD)"},
                                "time": {"type": "string", "description": "Appointment time (HH:MM)"},
                                "name": {"type": "string", "description": "Customer name"},
                                "phone": {"type": "string", "description": "Customer phone number"},
                                "email": {"type": "string", "description": "Customer email (optional)"},
                                "service": {"type": "string", "description": "Service requested (optional)"}
                            },
                            "required": ["date", "time", "name", "phone"]
                        }
                    }
                }
            },
            {
                "id": "get_available_services",
                "name": "Get Available Services",
                "description": "Fetch the current list of services offered by the business",
                "category": "information",
                "config": {
                    "type": "function",
                    "function": {
                        "name": "getAvailableServices",
                        "description": "Get list of services with prices and descriptions. Call this when customer asks about services or pricing.",
                        "parameters": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }
                }
            },
            {
                "id": "get_business_location",
                "name": "Get Business Location",
                "description": "Fetch the exact current business location/address",
                "category": "information",
                "config": {
                    "type": "function",
                    "function": {
                        "name": "getBusinessLocation",
                        "description": "Get the exact business location/address and directions note when customer asks where the business is located.",
                        "parameters": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }
                }
            },
            {
                "id": "transfer_call",
                "name": "Transfer Call",
                "description": "Transfer the call to a human agent",
                "category": "call_control",
                "config": {
                    "type": "transferCall",
                    "destinations": []
                }
            },
            {
                "id": "end_call",
                "name": "End Call",
                "description": "End the current call",
                "category": "call_control",
                "config": {
                    "type": "endCall"
                }
            }
        ]

    def _normalize_tool_definitions(self, tools: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Convert wrapped backend tool definitions into Vapi-ready payloads."""
        if not tools:
            return []

        webhook_url = os.getenv("VAPI_WEBHOOK_URL", "")
        webhook_credential_id = os.getenv("VAPI_SERVER_CREDENTIAL_ID", "").strip()
        normalized_tools: List[Dict[str, Any]] = []

        for tool in tools:
            if not isinstance(tool, dict):
                continue

            if "config" in tool and isinstance(tool.get("config"), dict):
                tool_payload = dict(tool["config"])
            else:
                tool_payload = dict(tool)

            if tool_payload.get("type") == "function":
                server_config = dict(tool_payload.get("server") or {})
                if webhook_url and "url" not in server_config:
                    server_config["url"] = webhook_url
                if webhook_credential_id and "credentialId" not in server_config:
                    server_config["credentialId"] = webhook_credential_id
                if server_config:
                    tool_payload["server"] = server_config

            normalized_tools.append(tool_payload)

        return normalized_tools
    
    # ===== WEBHOOK VERIFICATION =====
    
    def verify_webhook_request(self, payload: bytes, headers: Dict[str, str]) -> bool:
        """Verify webhook request using Vapi Credential Bearer auth only."""
        normalized_headers = {k.lower(): v for k, v in headers.items()}

        expected_token = self.webhook_bearer_token
        auth_header = normalized_headers.get("authorization", "")
        if not expected_token:
            logger.error("❌ VAPI_WEBHOOK_BEARER_TOKEN is not configured")
            return False
        if not auth_header.startswith("Bearer "):
            logger.warning("⚠️  Missing/invalid Authorization Bearer header on Vapi webhook")
            return False
        provided_token = auth_header[len("Bearer "):].strip()
        return hmac.compare_digest(provided_token, expected_token)

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Deprecated: backwards compatibility wrapper for signature-only checks."""
        return self.verify_webhook_request(payload, {"x-vapi-signature": signature})
    
    # ===== HELPER METHODS =====
    
    def _get_voice_id(self, voice_name: str, provider: str = "11labs") -> str:
        """Map friendly voice name to provider-specific voice ID"""
        voice_map = {
            "11labs": {
                "jennifer": "EXAVITQu4vr4xnSDxMaL",
                "sarah": "EXAVITQu4vr4xnSDxMaL",
                "rachel": "21m00Tcm4TlvDq8ikWAM",
                "adam": "pNInz6obpgDQGcFmaJgB",
                "ryan": "pNInz6obpgDQGcFmaJgB",
                "josh": "TxGEqnHWrfWFTfGW9XjX",
            },
            "openai": {
                "alloy": "alloy",
                "echo": "echo",
                "fable": "fable",
                "onyx": "onyx",
                "nova": "nova",
                "shimmer": "shimmer",
            },
            "azure": {
                "jenny": "en-US-JennyNeural",
                "guy": "en-US-GuyNeural",
                "sonia": "en-GB-SoniaNeural",
            }
        }
        
        provider_voices = voice_map.get(provider, voice_map["11labs"])
        return provider_voices.get(voice_name.lower(), voice_name)
    
    def get_public_key(self) -> Optional[str]:
        return self.public_key


# Singleton instance
vapi_service = VapiService()
