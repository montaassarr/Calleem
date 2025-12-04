"""LiveKit service helpers for issuing access tokens and tracking readiness."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, List
from uuid import uuid4

from fastapi import HTTPException, status
from jose import jwt
import httpx

from utils.config import settings

logger = logging.getLogger(__name__)


@dataclass
class LiveKitConfig:
    url: str
    api_key: str
    api_secret: str
    agent_queue: str
    agent_name: str

    @property
    def is_configured(self) -> bool:
        return bool(self.url and self.api_key and self.api_secret)


class LiveKitService:
    """Central place for LiveKit token generation and metadata."""

    def __init__(self) -> None:
        self._config = LiveKitConfig(
            url=settings.LIVEKIT_URL.rstrip("/") if settings.LIVEKIT_URL else "",
            api_key=settings.LIVEKIT_API_KEY,
            api_secret=settings.LIVEKIT_API_SECRET,
            agent_queue=settings.LIVEKIT_AGENT_QUEUE,
            agent_name=settings.LIVEKIT_AGENT_NAME,
        )
        self._rest_url = self._derive_rest_url(self._config.url)

    @property
    def config(self) -> LiveKitConfig:
        return self._config

    def _derive_rest_url(self, host: str) -> str:
        if not host:
            return ""
        if host.startswith("wss://"):
            return host.replace("wss://", "https://", 1)
        if host.startswith("ws://"):
            return host.replace("ws://", "http://", 1)
        if host.startswith("http"):
            return host
        return f"https://{host}"

    def _generate_api_token(self) -> str:
        """Generate a JWT token for LiveKit API requests."""
        now = int(time.time())
        claims = {
            "iss": self._config.api_key,
            "nbf": now - 10,
            "iat": now,
            "exp": now + 600,  # 10 minutes
            "jti": str(uuid4()),
            "video": {
                "roomCreate": True,
                "roomList": True,
                "roomRecord": True,
                "roomAdmin": True,
            }
        }
        return jwt.encode(claims, self._config.api_secret, algorithm="HS256")
    
    async def _request(self, method: str, path: str, **kwargs: Any) -> Dict[str, Any]:
        self.ensure_ready()
        if not self._rest_url:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="LiveKit REST endpoint missing")
        
        # Generate JWT token for API authentication
        token = self._generate_api_token()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        
        url = f"{self._rest_url}{path}"
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.request(method, url, headers=headers, **kwargs)
            if response.status_code >= 400:
                detail = response.text or "LiveKit API error"
                logger.error("LiveKit API error %s: %s", response.status_code, detail)
                raise HTTPException(status_code=response.status_code, detail=detail)
            if not response.content:
                return {}
            data = response.json()
            return data

    def ensure_ready(self) -> None:
        if not self._config.is_configured:
            logger.error("LiveKit configuration missing")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LiveKit is not configured. Set LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET.",
            )

    def create_access_token(
        self,
        *,
        identity: str,
        room: str,
        ttl_seconds: int = 3600,
        metadata: Optional[Dict[str, Any]] = None,
        grants: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a JWT token that allows connecting to a LiveKit room."""

        self.ensure_ready()
        now = int(time.time())
        claims = {
            "iss": self._config.api_key,
            "sub": identity,
            "nbf": now - 10,
            "iat": now,
            "exp": now + ttl_seconds,
            "jti": str(uuid4()),
            "video": {
                "room": room,
                "roomJoin": True,
                "canPublish": True,
                "canPublishData": True,
                "canSubscribe": True,
            },
        }

        if metadata:
            claims["metadata"] = json.dumps(metadata)

        if grants:
            claims["video"].update(grants)

        token = jwt.encode(claims, self._config.api_secret, algorithm="HS256")
        logger.debug("Issued LiveKit token for room %s", room)
        return token

    def build_preview_session(self, tenant_id: str, user_id: str) -> Dict[str, Any]:
        """Create a disposable room + token so the dashboard can test the agent."""

        room_name = f"preview-{tenant_id}-{uuid4().hex[:6]}"
        identity = f"tenant-{tenant_id}-{user_id}"

        token = self.create_access_token(
            identity=identity,
            room=room_name,
            ttl_seconds=900,
            metadata={
                "tenant_id": tenant_id,
                "agent_name": self._config.agent_name,
                "session_type": "preview",
            },
            grants={
                "canPublishSources": ["microphone"],
                "canSubscribe": True,
            },
        )

        return {
            "room_name": room_name,
            "token": token,
            "url": self._config.url,
            "agent_queue": self._config.agent_queue,
            "agent_name": self._config.agent_name,
        }

    async def create_room(
        self,
        *,
        room_name: str,
        metadata: Optional[Dict[str, Any]] = None,
        empty_timeout: int = 300,
        max_participants: int = 10,
    ) -> Dict[str, Any]:
        """
        Create a LiveKit room with metadata.
        This ensures the room exists before agents join.
        """
        payload = {
            "name": room_name,
            "empty_timeout": empty_timeout,
            "max_participants": max_participants,
        }
        
        if metadata:
            # LiveKit expects metadata as JSON string
            payload["metadata"] = json.dumps(metadata)
        
        try:
            return await self._request("POST", "/twirp/livekit.RoomService/CreateRoom", json=payload)
        except HTTPException as e:
            # Room might already exist, that's okay
            if e.status_code == 409:
                logger.info(f"Room {room_name} already exists")
                return {"name": room_name}
            raise

    def get_status(self) -> Dict[str, Any]:
        return {
            "configured": self._config.is_configured,
            "url": self._config.url,
            "agent_queue": self._config.agent_queue,
            "agent_name": self._config.agent_name,
        }

    async def list_supported_countries(self) -> List[Dict[str, Any]]:
        data = await self._request("GET", "/voice/v1/countries")
        return data.get("countries", data)

    async def list_available_numbers(self, country: str, area_code: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {"country": country}
        if area_code:
            params["area_code"] = area_code
        data = await self._request("GET", "/voice/v1/numbers/available", params=params)
        return data.get("numbers", data)

    async def list_owned_numbers(self) -> List[Dict[str, Any]]:
        data = await self._request("GET", "/voice/v1/numbers")
        return data.get("numbers", data)

    async def purchase_number(
        self,
        *,
        tenant_id: str,
        phone_number: str,
        country: str,
    ) -> Dict[str, Any]:
        payload = {
            "phone_number": phone_number,
            "country": country,
            "metadata": {"tenant_id": tenant_id, "agent_queue": self._config.agent_queue},
        }
        return await self._request("POST", "/voice/v1/numbers", json=payload)

    async def ensure_voice_trunks(self, *, tenant_id: str, phone_number: str) -> Dict[str, Any]:
        payload = {
            "tenant_id": tenant_id,
            "phone_number": phone_number,
            "agent_queue": self._config.agent_queue,
        }
        return await self._request("POST", "/voice/v1/trunks/ensure", json=payload)

    async def start_outbound_call(
        self,
        *,
        tenant_id: str,
        to_number: str,
        from_number: Optional[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "to": to_number,
            "from": from_number,
            "metadata": metadata or {"tenant_id": tenant_id, "agent_queue": self._config.agent_queue},
        }
        return await self._request("POST", "/voice/v1/calls", json=payload)


livekit_service = LiveKitService()
