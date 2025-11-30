"""
VAPI Service
Handles creation and management of VAPI assistants
"""

import httpx
import logging
from typing import Dict, Any, Optional, List
from models.agent import Agent, VoiceSettings
from services.tool_schema_generator import generate_tool_schemas, format_for_vapi
from routers.api_keys import get_decrypted_key

logger = logging.getLogger(__name__)

VAPI_API_URL = "https://api.vapi.ai"


async def create_vapi_assistant(
    agent: Agent,
    tenant_id: str
) -> str:
    """
    Create a VAPI assistant for an agent
    
    Args:
        agent: Agent model
        tenant_id: Tenant ID for API key lookup
        
    Returns:
        VAPI assistant ID
    """
    # Get tenant's VAPI API key
    try:
        vapi_key = await get_decrypted_key(tenant_id, "vapi")
    except Exception as e:
        logger.error(f"Failed to get VAPI key for tenant {tenant_id}: {e}")
        raise ValueError("VAPI API key not configured. Please add it in Integrations.")
    
    # Generate tool schemas
    webhook_dict = agent.webhook_urls.model_dump()
    tool_schemas = generate_tool_schemas(webhook_dict)
    vapi_tools = format_for_vapi(tool_schemas)
    
    # Prepare voice configuration
    voice_config = _prepare_voice_config(agent.voice_settings)
    
    # Prepare assistant payload
    payload = {
        "name": agent.name,
        "model": {
            "provider": "openai",
            "model": agent.llm_model,
            "temperature": agent.llm_temperature,
            "messages": [
                {
                    "role": "system",
                    "content": agent.system_prompt
                }
            ]
        },
        "voice": voice_config,
        "firstMessage": f"Hello! I'm {agent.name}. How can I help you today?",
        "serverUrl": None,  # We use function calling instead
        "serverUrlSecret": None,
        "endCallMessage": "Thank you for calling. Have a great day!",
        "endCallPhrases": ["goodbye", "bye", "thank you"],
        "recordingEnabled": True,
        "hipaaEnabled": False,
        "clientMessages": [
            "transcript",
            "hang",
            "function-call",
            "speech-update",
            "metadata",
            "conversation-update"
        ],
        "serverMessages": [
            "end-of-call-report",
            "status-update",
            "hang",
            "function-call"
        ],
        "silenceTimeoutSeconds": 30,
        "maxDurationSeconds": 1800,  # 30 minutes
        "backgroundSound": "office",
        "backchannelingEnabled": True,
        "backgroundDenoisingEnabled": True,
        "modelOutputInMessagesEnabled": True
    }
    
    # Add tools if any
    if vapi_tools:
        payload["model"]["tools"] = vapi_tools
    
    # Create assistant via VAPI API
    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = {
            "Authorization": f"Bearer {vapi_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = await client.post(
                f"{VAPI_API_URL}/assistant",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 201:
                data = response.json()
                assistant_id = data.get("id")
                logger.info(f"Created VAPI assistant {assistant_id} for agent {agent.id}")
                return assistant_id
            else:
                logger.error(f"VAPI API error: {response.status_code} - {response.text}")
                raise ValueError(f"Failed to create VAPI assistant: {response.text}")
                
        except httpx.RequestError as e:
            logger.error(f"VAPI API request error: {e}")
            raise ValueError(f"Failed to connect to VAPI API: {str(e)}")


async def update_vapi_assistant(
    assistant_id: str,
    agent: Agent,
    tenant_id: str
) -> bool:
    """
    Update an existing VAPI assistant
    
    Args:
        assistant_id: VAPI assistant ID
        agent: Updated agent model
        tenant_id: Tenant ID for API key lookup
        
    Returns:
        True if successful
    """
    # Get tenant's VAPI API key
    vapi_key = await get_decrypted_key(tenant_id, "vapi")
    
    # Generate tool schemas
    webhook_dict = agent.webhook_urls.model_dump()
    tool_schemas = generate_tool_schemas(webhook_dict)
    vapi_tools = format_for_vapi(tool_schemas)
    
    # Prepare voice configuration
    voice_config = _prepare_voice_config(agent.voice_settings)
    
    # Prepare update payload
    payload = {
        "name": agent.name,
        "model": {
            "provider": "openai",
            "model": agent.llm_model,
            "temperature": agent.llm_temperature,
            "messages": [
                {
                    "role": "system",
                    "content": agent.system_prompt
                }
            ]
        },
        "voice": voice_config
    }
    
    if vapi_tools:
        payload["model"]["tools"] = vapi_tools
    
    # Update assistant via VAPI API
    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = {
            "Authorization": f"Bearer {vapi_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = await client.patch(
                f"{VAPI_API_URL}/assistant/{assistant_id}",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info(f"Updated VAPI assistant {assistant_id}")
                return True
            else:
                logger.error(f"VAPI API error: {response.status_code} - {response.text}")
                raise ValueError(f"Failed to update VAPI assistant: {response.text}")
                
        except httpx.RequestError as e:
            logger.error(f"VAPI API request error: {e}")
            raise ValueError(f"Failed to connect to VAPI API: {str(e)}")


async def delete_vapi_assistant(
    assistant_id: str,
    tenant_id: str
) -> bool:
    """
    Delete a VAPI assistant
    
    Args:
        assistant_id: VAPI assistant ID
        tenant_id: Tenant ID for API key lookup
        
    Returns:
        True if successful
    """
    # Get tenant's VAPI API key
    vapi_key = await get_decrypted_key(tenant_id, "vapi")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = {
            "Authorization": f"Bearer {vapi_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = await client.delete(
                f"{VAPI_API_URL}/assistant/{assistant_id}",
                headers=headers
            )
            
            if response.status_code in [200, 204]:
                logger.info(f"Deleted VAPI assistant {assistant_id}")
                return True
            else:
                logger.warning(f"VAPI delete returned {response.status_code}: {response.text}")
                return False
                
        except httpx.RequestError as e:
            logger.error(f"VAPI API request error: {e}")
            return False


def _prepare_voice_config(voice_settings: VoiceSettings) -> Dict[str, Any]:
    """
    Prepare voice configuration for VAPI
    
    Args:
        voice_settings: Voice settings from agent
        
    Returns:
        VAPI voice configuration
    """
    if voice_settings.provider.value == "elevenlabs":
        return {
            "provider": "11labs",
            "voiceId": voice_settings.voice_id,
            "stability": voice_settings.stability or 0.5,
            "similarityBoost": voice_settings.similarity_boost or 0.75,
            "model": voice_settings.model or "eleven_turbo_v2"
        }
    elif voice_settings.provider.value == "openai":
        return {
            "provider": "openai",
            "voice": voice_settings.voice_id,  # alloy, echo, fable, onyx, nova, shimmer
            "model": voice_settings.model or "tts-1"
        }
    elif voice_settings.provider.value == "deepgram":
        return {
            "provider": "deepgram",
            "voice": voice_settings.voice_id
        }
    else:
        # Default to ElevenLabs
        return {
            "provider": "11labs",
            "voiceId": voice_settings.voice_id
        }
