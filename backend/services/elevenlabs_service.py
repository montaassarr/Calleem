"""
ElevenLabs Voice API Integration
Fetches and caches available voices for voice agent configuration
"""

import logging
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from utils.config import settings

logger = logging.getLogger(__name__)


class ElevenLabsService:
    """Service for interacting with ElevenLabs API"""
    
    def __init__(self):
        self.api_key = getattr(settings, "ELEVENLABS_API_KEY", None)
        self.base_url = "https://api.elevenlabs.io/v1"
        self._cache: Optional[Dict[str, Any]] = None
        self._cache_time: Optional[datetime] = None
        self._cache_ttl = timedelta(hours=24)
    
    def is_configured(self) -> bool:
        """Check if ElevenLabs is configured"""
        return bool(self.api_key)
    
    async def get_voices(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Get list of available voices from ElevenLabs
        Returns cached result if available and not expired
        """
        if not self.is_configured():
            logger.warning("ElevenLabs API key not configured, returning default voices")
            return self._get_default_voices()
        
        # Check cache
        if not force_refresh and self._cache and self._cache_time:
            if datetime.utcnow() - self._cache_time < self._cache_ttl:
                logger.debug("Returning cached ElevenLabs voices")
                return self._cache.get("voices", [])
        
        # Fetch from API
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/voices",
                    headers={"xi-api-key": self.api_key},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    voices = data.get("voices", [])
                    
                    # Transform to simplified format
                    formatted_voices = []
                    for voice in voices:
                        formatted_voices.append({
                            "voice_id": voice.get("voice_id"),
                            "name": voice.get("name"),
                            "category": voice.get("category", "general"),
                            "description": voice.get("description", ""),
                            "labels": voice.get("labels", {}),
                            "preview_url": voice.get("preview_url"),
                            "accent": voice.get("labels", {}).get("accent", ""),
                            "age": voice.get("labels", {}).get("age", ""),
                            "gender": voice.get("labels", {}).get("gender", ""),
                            "use_case": voice.get("labels", {}).get("use case", "")
                        })
                    
                    # Cache the result
                    self._cache = {"voices": formatted_voices}
                    self._cache_time = datetime.utcnow()
                    
                    logger.info(f"Fetched {len(formatted_voices)} voices from ElevenLabs")
                    return formatted_voices
                else:
                    logger.error(f"ElevenLabs API error: {response.status_code}")
                    return self._get_default_voices()
                    
        except Exception as e:
            logger.error(f"Failed to fetch ElevenLabs voices: {e}", exc_info=True)
            return self._get_default_voices()
    
    async def get_voice_details(self, voice_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific voice"""
        if not self.is_configured():
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/voices/{voice_id}",
                    headers={"xi-api-key": self.api_key},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to fetch voice {voice_id}: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching voice details: {e}", exc_info=True)
            return None
    
    def _get_default_voices(self) -> List[Dict[str, Any]]:
        """Return default voice list when ElevenLabs is not configured"""
        return [
            {
                "voice_id": "rachel",
                "name": "Rachel (OpenAI)",
                "category": "openai",
                "description": "Warm, professional female voice",
                "provider": "openai",
                "accent": "American",
                "gender": "female"
            },
            {
                "voice_id": "alloy",
                "name": "Alloy (OpenAI)",
                "category": "openai",
                "description": "Neutral, balanced voice",
                "provider": "openai",
                "accent": "American",
                "gender": "neutral"
            },
            {
                "voice_id": "echo",
                "name": "Echo (OpenAI)",
                "category": "openai",
                "description": "Clear, articulate male voice",
                "provider": "openai",
                "accent": "American",
                "gender": "male"
            },
            {
                "voice_id": "nova",
                "name": "Nova (OpenAI)",
                "category": "openai",
                "description": "Energetic, friendly female voice",
                "provider": "openai",
                "accent": "American",
                "gender": "female"
            }
        ]
    
    def clear_cache(self):
        """Clear the voice cache"""
        self._cache = None
        self._cache_time = None
        logger.info("ElevenLabs voice cache cleared")


# Singleton instance
elevenlabs_service = ElevenLabsService()
