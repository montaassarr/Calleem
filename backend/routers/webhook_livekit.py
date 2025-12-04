"""LiveKit webhook handlers for voice automation."""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional, List

import httpx
from fastapi import APIRouter, HTTPException, Request, status

from database.mongo_config import get_database
from models.conversation import MessageRole
from utils.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

LIVEKIT_SIGNATURE_HEADER = "x-livekit-signature"
LIVEKIT_SECRET = settings.LIVEKIT_API_SECRET or ""
N8N_WEBHOOK_BASE = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook").rstrip("/")
N8N_CALL_ENDED_PATH = os.getenv("N8N_CALL_ENDED_PATH", "call-ended-processing")


def _verify_signature(provided: str, body: bytes) -> bool:
    digest = hmac.new(LIVEKIT_SECRET.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest((provided or "").lower(), digest.lower())


def _parse_metadata(raw: Optional[Any]) -> Dict[str, Any]:
    if not raw:
        return {}
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw)
    except Exception:
        return {}


def _tenant_context(payload: Dict[str, Any]) -> Dict[str, Any]:
    room = payload.get("room", {}) or {}
    metadata = _parse_metadata(room.get("metadata"))
    participant = payload.get("participant", {}) or {}
    metadata.update(_parse_metadata(participant.get("metadata")))
    tenant_id = metadata.get("tenant_id") or metadata.get("tenantId")
    if not tenant_id:
        tenant_id = payload.get("tenant_id")
    return {
        "tenant_id": tenant_id,
        "room_name": room.get("name") or metadata.get("room_name") or payload.get("room_name"),
        "metadata": metadata,
    }


async def _ensure_call_record(context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    tenant_id = context.get("tenant_id")
    room_name = context.get("room_name")
    if not (tenant_id and room_name):
        logger.warning("LiveKit webhook missing tenant or room metadata: %s", context)
        return None
    db = get_database()
    record = await db.voice_calls.find_one({"tenant_id": tenant_id, "livekit_room": room_name})
    if record:
        return record
    now = datetime.utcnow()
    doc = {
        "tenant_id": tenant_id,
        "livekit_room": room_name,
        "agent_queue": context["metadata"].get("agent_queue"),
        "status": "in-progress",
        "started_at": now,
        "transcript": [],
        "participant_events": [],
        "metadata": context["metadata"],
        "created_at": now,
        "updated_at": now,
    }
    await db.voice_calls.insert_one(doc)
    return doc


def _map_role(raw_role: Optional[str]) -> str:
    normalized = (raw_role or "").lower()
    if normalized in {"user", "caller", "participant", "customer", "client"}:
        return MessageRole.CLIENT.value
    return MessageRole.AI.value


def _summarize(transcript: List[Dict[str, Any]]) -> str:
    if not transcript:
        return "No transcript available"
    combined = " ".join(entry.get("text", "") for entry in transcript).strip()
    if not combined:
        return "No transcript available"
    return combined[:1000]


async def _persist_transcript(context: Dict[str, Any], payload: Dict[str, Any]) -> None:
    tenant_id = context.get("tenant_id")
    room_name = context.get("room_name")
    if not (tenant_id and room_name):
        return
    transcription = payload.get("transcription") or payload.get("data") or {}
    text = transcription.get("text") or transcription.get("value")
    if not text:
        return
    speaker = transcription.get("participant") or transcription.get("speaker")
    role = _map_role(speaker if isinstance(speaker, str) else transcription.get("role"))
    db = get_database()
    entry = {
        "role": role,
        "text": text,
        "timestamp": datetime.utcnow(),
    }
    await db.voice_calls.update_one(
        {"tenant_id": tenant_id, "livekit_room": room_name},
        {"$push": {"transcript": entry}, "$set": {"updated_at": datetime.utcnow()}},
    )


async def _persist_participant_event(context: Dict[str, Any], payload: Dict[str, Any], event_type: str) -> None:
    tenant_id = context.get("tenant_id")
    room_name = context.get("room_name")
    if not (tenant_id and room_name):
        return
    participant = payload.get("participant") or {}
    event = {
        "type": event_type,
        "identity": participant.get("identity"),
        "name": participant.get("name"),
        "timestamp": datetime.utcnow(),
        "tracks": participant.get("tracks"),
    }
    db = get_database()
    await db.voice_calls.update_one(
        {"tenant_id": tenant_id, "livekit_room": room_name},
        {"$push": {"participant_events": event}, "$set": {"updated_at": datetime.utcnow()}},
    )


async def _handle_room_ended(context: Dict[str, Any], payload: Dict[str, Any]) -> None:
    tenant_id = context.get("tenant_id")
    room_name = context.get("room_name")
    if not (tenant_id and room_name):
        return
    db = get_database()
    room = payload.get("room", {})
    ended_at = datetime.utcnow()
    started_at_iso = room.get("createdAt") or room.get("created_at")
    started_at = None
    if started_at_iso:
        try:
            started_at = datetime.fromisoformat(started_at_iso.replace("Z", "+00:00"))
        except ValueError:
            started_at = None
    call = await db.voice_calls.find_one({"tenant_id": tenant_id, "livekit_room": room_name})
    duration_seconds = int((ended_at - (started_at or call.get("started_at", ended_at))).total_seconds()) if call else 0
    transcript = call.get("transcript", []) if call else []
    summary = _summarize(transcript)
    update_doc = {
        "status": "completed",
        "ended_at": ended_at,
        "duration_seconds": duration_seconds,
        "summary": summary,
        "updated_at": ended_at,
    }
    await db.voice_calls.update_one({"tenant_id": tenant_id, "livekit_room": room_name}, {"$set": update_doc}, upsert=True)
    await _persist_conversation(context, transcript, summary, call)
    call_record = await db.voice_calls.find_one({"tenant_id": tenant_id, "livekit_room": room_name})
    if call_record:
        await _trigger_n8n(call_record)


async def _persist_conversation(
    context: Dict[str, Any], transcript: List[Dict[str, Any]], summary: str, call: Optional[Dict[str, Any]]
) -> None:
    tenant_id = context.get("tenant_id")
    room_name = context.get("room_name")
    if not (tenant_id and room_name):
        return
    caller = context["metadata"].get("caller_number") or context["metadata"].get("customer_number") or "+10000000000"
    messages = []
    for entry in transcript:
        messages.append(
            {
                "role": entry.get("role", MessageRole.AI.value),
                "text": entry.get("text", ""),
                "timestamp": entry.get("timestamp", datetime.utcnow()),
            }
        )
    now = datetime.utcnow()
    document = {
        "conversation_id": room_name,
        "tenant_id": tenant_id,
        "phone_number": caller,
        "messages": messages,
        "state": {
            "intent": "voice_call",
            "collected_info": {},
            "next_question": None,
            "completed": True,
        },
        "summary": summary,
        "created_at": call.get("started_at", now) if call else now,
        "updated_at": now,
    }
    db = get_database()
    await db.conversations.update_one(
        {"conversation_id": room_name, "tenant_id": tenant_id},
        {"$set": document},
        upsert=True,
    )


async def _trigger_n8n(call_record: Dict[str, Any]) -> None:
    url = f"{N8N_WEBHOOK_BASE}/{N8N_CALL_ENDED_PATH}"
    payload = {
        "livekit_room": call_record.get("livekit_room"),
        "tenant_id": call_record.get("tenant_id"),
        "duration_seconds": call_record.get("duration_seconds"),
        "transcript": call_record.get("transcript", []),
        "summary": call_record.get("summary"),
        "metadata": call_record.get("metadata", {}),
    }
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            logger.info("Triggered n8n call-ended workflow for room %s", call_record.get("livekit_room"))
    except Exception as exc:
        logger.error("Failed to trigger n8n call-ended workflow: %s", exc)


@router.post("/livekit")
async def livekit_webhook(request: Request):
    if not LIVEKIT_SECRET:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="LiveKit secret not configured")
    body = await request.body()
    signature = request.headers.get(LIVEKIT_SIGNATURE_HEADER)
    if not _verify_signature(signature or "", body):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid LiveKit signature")
    payload = await request.json()
    context = _tenant_context(payload)
    await _ensure_call_record(context)
    event = (payload.get("event") or "").lower()
    if event in {"participant_joined", "participant_left"}:
        await _persist_participant_event(context, payload, event)
    elif event == "track_published":
        await _persist_participant_event(context, payload, event)
    elif event in {"transcription", "data_track", "speech_update"}:
        await _persist_transcript(context, payload)
    elif event == "room_ended":
        await _handle_room_ended(context, payload)
    else:
        logger.debug("LiveKit webhook event %s ignored", event)
    return {"status": "ok"}
