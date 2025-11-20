"""
Simple HTTP client for Vapi API (no SDK required)
"""

import httpx
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class VapiHTTPClient:
    """Simple HTTP client for Vapi API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.vapi.ai"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def create_assistant(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new assistant"""
        async with httpx.AsyncClient() as client:
            try:
                logger.info(f"Creating assistant with payload: {payload}")
                response = await client.post(
                    f"{self.base_url}/assistant",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error creating assistant: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Failed to create assistant: {e}")
                raise
    
    async def create_call(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create an outbound call"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/call",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Failed to create call: {e}")
                raise
    
    async def create_session(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a WebRTC session"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/call/web",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error creating session: {e.response.status_code} - {e.response.text}")
                return {}
            except Exception as e:
                logger.error(f"Failed to create session: {e}")
                return {}
