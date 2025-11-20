"""
Vapi AI Voice Assistant Integration Service
"""
import logging
from typing import Dict, List, Optional, Any
import os
from vapi import Vapi
from vapi.types import CreateAssistantDto
from utils.config import settings

logger = logging.getLogger(__name__)


class VapiService:
    """Service for integrating with Vapi AI voice platform"""
    
    def __init__(self):
        self.api_key = settings.VAPI_API_KEY
        self.public_key = settings.VAPI_PUBLIC_KEY
        self.webhook_url = settings.VAPI_WEBHOOK_URL if hasattr(settings, 'VAPI_WEBHOOK_URL') else ""
        
        if not self.api_key:
            logger.warning("VAPI_API_KEY not configured in environment")
            self.client = None
        else:
            try:
                self.client = Vapi(token=self.api_key)
                logger.info("Vapi client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Vapi client: {e}")
                self.client = None
    
    def is_configured(self) -> bool:
        """Check if Vapi is properly configured"""
        return self.client is not None and self.api_key is not None
    
    def create_or_update_assistant(
        self,
        voice_config: Dict[str, Any],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[str]:
        """
        Create or update a Vapi assistant with the given configuration
        
        Args:
            voice_config: Voice configuration from database
            tools: Optional list of tools/functions for the assistant
            
        Returns:
            Assistant ID if successful, None otherwise
        """
        if not self.is_configured():
            logger.error("Vapi not configured, cannot create assistant")
            return None
        
        try:
            # Extract configuration
            model_parts = voice_config.get("model", "groq:llama-3.3-70b-versatile").split(":")
            model_provider = model_parts[0] if len(model_parts) > 1 else "groq"
            model_name = model_parts[1] if len(model_parts) > 1 else model_parts[0]
            
            voice_parts = voice_config.get("voice", "elevenlabs:Rachel").split(":")
            voice_provider_raw = voice_parts[0] if len(voice_parts) > 1 else "elevenlabs"
            voice_id = voice_parts[1] if len(voice_parts) > 1 else voice_parts[0]
            
            # Map provider names to Vapi's expected values
            provider_map = {
                "elevenlabs": "11labs",
                "playht": "playht",
                "openai": "openai",
                "azure": "azure",
                "deepgram": "deepgram"
            }
            voice_provider = provider_map.get(voice_provider_raw.lower(), "11labs")

            # Map friendly ElevenLabs voice names to official IDs when needed
            elevenlabs_voice_map = {
                "rachel": "21m00Tcm4TlvDq8ikWAM",
                "bella": "EXAVITQu4vr4xnSDxMaL",
                "domi": "AZnzlk1XvdvUeBnXmlld",
                "antoni": "ErXwobaYiN019PkySvjV",
                "matthew": "Yko7PKHZNXotIFUBG7I9"
            }

            if voice_provider == "11labs":
                normalized_voice = voice_id.lower()
                if normalized_voice in elevenlabs_voice_map:
                    voice_id = elevenlabs_voice_map[normalized_voice]
            
            # Build assistant configuration using snake_case for Python SDK
            assistant_params = {
                "name": "AI Receptionist",
                "model": {
                    "provider": model_provider,
                    "model": model_name,
                    "temperature": voice_config.get("temperature", 0.7),
                    "messages": [
                        {
                            "role": "system",
                            "content": voice_config.get(
                                "system_prompt",
                                "You are a helpful AI receptionist."
                            )
                        }
                    ]
                },
                "voice": {
                    "provider": voice_provider,
                    "voiceId": voice_id
                },
                "transcriber": {
                    "provider": "deepgram",
                    "model": "nova-2",
                    "language": "en"
                },
                "first_message": voice_config.get(
                    "first_message",
                    "Hello! How can I help you today?"
                ),
            }
            
            # Add server URL for function calling if tools are provided
            if tools and len(tools) > 0 and self.webhook_url:
                assistant_params["server"] = {
                    "url": self.webhook_url,
                    "secret": os.getenv("VAPI_SERVER_SECRET", "")
                }
            
            # Create the assistant
            assistant = self.client.assistants.create(**assistant_params)
            
            if hasattr(assistant, 'id'):
                logger.info(f"Created Vapi assistant with ID: {assistant.id}")
                return assistant.id
            else:
                logger.error("Assistant created but no ID returned")
                return None
                
        except Exception as e:
            logger.error(f"Error creating Vapi assistant: {e}")
            return None
    
    def get_assistant(self, assistant_id: str) -> Optional[Any]:
        """Get assistant details by ID"""
        if not self.is_configured():
            return None
        
        try:
            return self.client.assistants.get(assistant_id)
        except Exception as e:
            logger.error(f"Error getting assistant {assistant_id}: {e}")
            return None
    
    def list_assistants(self) -> List[Any]:
        """List all assistants"""
        if not self.is_configured():
            return []
        
        try:
            assistants = self.client.assistants.list()
            return list(assistants) if assistants else []
        except Exception as e:
            logger.error(f"Error listing assistants: {e}")
            return []
    
    def delete_assistant(self, assistant_id: str) -> bool:
        """Delete an assistant"""
        if not self.is_configured():
            return False
        
        try:
            self.client.assistants.delete(assistant_id)
            logger.info(f"Deleted assistant {assistant_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting assistant {assistant_id}: {e}")
            return False
    
    def get_public_key(self) -> Optional[str]:
        """Get Vapi public key for client-side initialization"""
        return self.public_key
    
    def create_phone_call(
        self,
        assistant_id: str,
        customer_phone: str
    ) -> Optional[str]:
        """
        Create an outbound phone call
        
        Args:
            assistant_id: Vapi assistant ID
            customer_phone: Customer phone number in E.164 format
            
        Returns:
            Call ID if successful, None otherwise
        """
        if not self.is_configured():
            return None
        
        try:
            call = self.client.calls.create(
                assistant_id=assistant_id,
                customer={
                    "number": customer_phone
                }
            )
            
            if hasattr(call, 'id'):
                logger.info(f"Created phone call with ID: {call.id}")
                return call.id
            return None
            
        except Exception as e:
            logger.error(f"Error creating phone call: {e}")
            return None
    
    def get_call(self, call_id: str) -> Optional[Any]:
        """Get call details"""
        if not self.is_configured():
            return None
        
        try:
            return self.client.calls.get(call_id)
        except Exception as e:
            logger.error(f"Error getting call {call_id}: {e}")
            return None


# Global instance
vapi_service = VapiService()
