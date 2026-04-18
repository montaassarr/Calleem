"""Call history API backed by Vapi."""

from __future__ import annotations

import logging
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from database.mongo_config import get_database
from routers.users import get_current_user
from services.vapi_service import vapi_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Calls"])

LIST_CACHE_TTL_SECONDS = 20
_calls_list_cache: Dict[Tuple[str, int, int], Tuple[float, Dict[str, Any]]] = {}


class CallListItem(BaseModel):
    callId: str
    createdAt: Optional[str] = None
    clientPhoneNumber: Optional[str] = None
    durationSeconds: int = 0
    status: Optional[str] = None
    endedReason: Optional[str] = None


class CallMessage(BaseModel):
    role: str
    text: str
    timestamp: Optional[str] = None


class CallDetailResponse(BaseModel):
    callId: str
    clientPhoneNumber: Optional[str] = None
    ourPhoneNumber: Optional[str] = None
    createdAt: Optional[str] = None
    durationSeconds: int = 0
    status: Optional[str] = None
    endedReason: Optional[str] = None
    assistantId: Optional[str] = None
    messages: List[CallMessage] = Field(default_factory=list)


def _cache_key(tenant_id: str, page: int, limit: int) -> Tuple[str, int, int]:
    return tenant_id, page, limit


def _get_cached_list(tenant_id: str, page: int, limit: int) -> Optional[Dict[str, Any]]:
    entry = _calls_list_cache.get(_cache_key(tenant_id, page, limit))
    if not entry:
        return None
    cached_at, payload = entry
    if time.monotonic() - cached_at > LIST_CACHE_TTL_SECONDS:
        _calls_list_cache.pop(_cache_key(tenant_id, page, limit), None)
        return None
    return payload


def _set_cached_list(tenant_id: str, page: int, limit: int, payload: Dict[str, Any]) -> None:
    _calls_list_cache[_cache_key(tenant_id, page, limit)] = (time.monotonic(), payload)


def _get_nested(data: Dict[str, Any], *paths: str) -> Any:
    for path in paths:
        current: Any = data
        for part in path.split("."):
            if not isinstance(current, dict):
                current = None
                break
            current = current.get(part)
        if current not in (None, ""):
            return current
    return None


def _coerce_iso(value: Any) -> Optional[str]:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, (int, float)):
        if value > 10_000_000_000:
            return datetime.fromtimestamp(value / 1000).isoformat()
        return datetime.fromtimestamp(value).isoformat()
    return str(value)


def _normalize_duration_seconds(*values: Any) -> int:
    for value in values:
        if value is None:
            continue
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            continue
        if numeric > 1000 and numeric % 1000 == 0:
            numeric = numeric / 1000
        return int(round(numeric))
    return 0


def _pick_phone(call: Dict[str, Any]) -> Optional[str]:
    return _get_nested(
        call,
        "customer.number",
        "customer.phoneNumber",
        "customer.phone_number",
        "customerPhoneNumber",
        "customerPhone",
        "from",
        "caller",
        "phoneNumber",
        "phone_number",
    )


def _pick_our_number(call: Dict[str, Any]) -> Optional[str]:
    return _get_nested(
        call,
        "phoneNumber",
        "phone_number",
        "to",
        "assistant.phoneNumber",
        "assistant.phone_number",
    )


def _pick_ended_reason(call: Dict[str, Any]) -> Optional[str]:
    return _get_nested(call, "endedReason", "endReason", "reason", "ended_reason")


def _pick_status(call: Dict[str, Any]) -> Optional[str]:
    return _get_nested(call, "status", "callStatus")


def _pick_assistant_id(call: Dict[str, Any]) -> Optional[str]:
    return _get_nested(call, "assistantId", "assistant_id", "assistant.id")


def _pick_call_id(call: Dict[str, Any]) -> Optional[str]:
    return _get_nested(call, "id", "callId", "call_id", "call.id", "call.callId", "call.call_id")


def _to_message(role: str, text: str, timestamp: Any = None) -> Dict[str, Any]:
    return {
        "role": role,
        "text": text,
        "timestamp": _coerce_iso(timestamp),
    }


def _normalize_role(role: Any) -> Optional[str]:
    if not role:
        return None
    value = str(role).lower()
    if value in {"user", "client", "customer", "caller", "human", "human_agent"}:
        return "client"
    if value in {"assistant", "ai", "agent", "bot"}:
        return "ai"
    if value in {"system", "tool", "toolcall", "tool-call"}:
        return value
    return None


def _messages_from_structured(raw_messages: Any) -> List[Dict[str, Any]]:
    messages: List[Dict[str, Any]] = []
    if not isinstance(raw_messages, list):
        return messages

    for entry in raw_messages:
        if not isinstance(entry, dict):
            continue
        role = _normalize_role(entry.get("role") or entry.get("speaker") or entry.get("type"))
        if role in {"system", "tool", "toolcall", "tool-call"}:
            continue
        if role not in {"client", "ai"}:
            continue

        text = (
            entry.get("text")
            or entry.get("content")
            or entry.get("message")
            or entry.get("transcript")
            or ""
        )
        text = str(text).strip()
        if not text:
            continue
        messages.append(_to_message(role, text, entry.get("timestamp") or entry.get("createdAt") or entry.get("time")))

    return messages


def _messages_from_transcript(transcript: Any) -> List[Dict[str, Any]]:
    if transcript is None:
        return []

    lines: List[str]
    if isinstance(transcript, str):
        lines = [line.strip() for line in transcript.splitlines() if line.strip()]
    elif isinstance(transcript, list):
        lines = [str(line).strip() for line in transcript if str(line).strip()]
    else:
        return []

    messages: List[Dict[str, Any]] = []
    current_role: Optional[str] = None
    current_text: List[str] = []

    def flush_current() -> None:
        nonlocal current_role, current_text
        if current_role and current_text:
            text = " ".join(current_text).strip()
            if text:
                messages.append(_to_message(current_role, text))
        current_role = None
        current_text = []

    for line in lines:
        match = re.match(r"^(User|Assistant|Client|AI|System|Tool)\s*:\s*(.*)$", line, flags=re.IGNORECASE)
        if match:
            flush_current()
            role = _normalize_role(match.group(1))
            if role in {"system", "tool", "toolcall", "tool-call"}:
                current_role = None
                current_text = []
                continue
            current_role = role or "client"
            current_text = [match.group(2).strip()] if match.group(2).strip() else []
        else:
            if current_role:
                current_text.append(line)

    flush_current()
    return messages


def _extract_call_details(payload: Dict[str, Any]) -> Dict[str, Any]:
    call = payload.get("call") or payload.get("message", {}).get("call") or payload
    artifact = call.get("artifact") if isinstance(call, dict) else None
    if not isinstance(artifact, dict):
        artifact = payload.get("artifact") if isinstance(payload.get("artifact"), dict) else {}

    raw_messages = artifact.get("messages")
    messages = _messages_from_structured(raw_messages)
    if not messages:
        messages = _messages_from_transcript(artifact.get("transcript") or call.get("transcript") or payload.get("transcript"))

    return {
        "callId": call.get("id") or payload.get("id"),
        "clientPhoneNumber": _pick_phone(call),
        "ourPhoneNumber": _pick_our_number(call),
        "createdAt": _coerce_iso(call.get("createdAt") or call.get("startedAt") or payload.get("createdAt") or payload.get("startedAt")),
        "durationSeconds": _normalize_duration_seconds(call.get("durationSeconds"), call.get("duration"), payload.get("durationSeconds"), payload.get("duration")),
        "status": _pick_status(call) or payload.get("status"),
        "endedReason": _pick_ended_reason(call) or payload.get("endedReason") or payload.get("endReason"),
        "assistantId": call.get("assistantId") or payload.get("assistantId"),
        "messages": messages,
    }


async def _resolve_tenant_assistant_id(tenant_id: str) -> Optional[str]:
    db = get_database()
    tenant = await db.tenants.find_one({"_id": tenant_id})
    if not tenant:
        return None
    return tenant.get("vapi_assistant_id")


async def _fetch_tenant_calls(tenant_id: str, page: int, limit: int) -> Dict[str, Any]:
    assistant_id = await _resolve_tenant_assistant_id(tenant_id)
    if not assistant_id:
        return {"items": [], "page": page, "limit": limit, "hasMore": False}

    # Fetch enough Vapi pages to assemble the requested tenant-scoped page.
    target_count = page * limit
    collected: List[Dict[str, Any]] = []
    seen_ids = set()
    current_page = 1
    max_pages = max(page + 3, 5)

    while len(collected) < target_count and current_page <= max_pages:
        raw = await vapi_service.list_calls(page=current_page, limit=max(limit * 2, 20))
        raw_items = raw.get("results") or raw.get("data") or raw.get("calls") or raw.get("items") or []
        if not isinstance(raw_items, list):
            raw_items = []

        if not raw_items:
            break

        for item in raw_items:
            if not isinstance(item, dict):
                continue
            call_blob = item.get("call") if isinstance(item.get("call"), dict) else item
            item_assistant_id = _pick_assistant_id(call_blob) or _pick_assistant_id(item)
            if assistant_id and item_assistant_id and str(item_assistant_id) != str(assistant_id):
                continue

            call_id = _pick_call_id(item) or _pick_call_id(call_blob)
            if not call_id or call_id in seen_ids:
                continue

            seen_ids.add(call_id)
            collected.append({
                "callId": call_id,
                "createdAt": _coerce_iso(
                    _get_nested(call_blob, "createdAt", "startedAt", "created_at")
                    or _get_nested(item, "createdAt", "startedAt", "created_at")
                ),
                "clientPhoneNumber": _pick_phone(call_blob) or _pick_phone(item),
                "durationSeconds": _normalize_duration_seconds(
                    _get_nested(call_blob, "durationSeconds", "duration")
                    or _get_nested(item, "durationSeconds", "duration")
                ),
                "status": _pick_status(call_blob) or _pick_status(item),
                "endedReason": _pick_ended_reason(call_blob) or _pick_ended_reason(item),
                "assistantId": item_assistant_id,
            })

            if len(collected) >= target_count:
                break

        if len(raw_items) < limit:
            break
        current_page += 1

    start = (page - 1) * limit
    end = start + limit
    page_items = collected[start:end]

    payload = {
        "items": page_items,
        "page": page,
        "limit": limit,
        "hasMore": len(collected) > end,
    }

    logger.info(
        "Calls list (tenant=%s page=%s limit=%s): collected=%s returned=%s",
        tenant_id,
        page,
        limit,
        len(collected),
        len(page_items),
    )
    return payload


async def _fetch_tenant_calls_from_db(tenant_id: str, page: int, limit: int) -> Dict[str, Any]:
    db = get_database()
    skip = (page - 1) * limit

    cursor = db.call_logs.find({"tenant_id": tenant_id}).sort("updated_at", -1).skip(skip).limit(limit + 1)
    docs = await cursor.to_list(length=limit + 1)

    has_more = len(docs) > limit
    docs = docs[:limit]

    items: List[Dict[str, Any]] = []
    for doc in docs:
        items.append({
            "callId": doc.get("vapi_call_id") or str(doc.get("_id")),
            "createdAt": _coerce_iso(doc.get("started_at") or doc.get("created_at") or doc.get("updated_at")),
            "clientPhoneNumber": doc.get("customer_phone"),
            "durationSeconds": _normalize_duration_seconds(doc.get("duration"), doc.get("duration_seconds")),
            "status": doc.get("status"),
            "endedReason": doc.get("ended_reason") or doc.get("end_reason"),
            "assistantId": doc.get("assistant_id"),
        })

    payload = {
        "items": items,
        "page": page,
        "limit": limit,
        "hasMore": has_more,
    }

    logger.info(
        "Calls DB fallback (tenant=%s page=%s limit=%s): returned=%s",
        tenant_id,
        page,
        limit,
        len(items),
    )
    return payload


async def _fetch_call_from_db(tenant_id: str, call_id: str) -> Optional[Dict[str, Any]]:
    db = get_database()
    doc = await db.call_logs.find_one({"tenant_id": tenant_id, "vapi_call_id": call_id})
    if not doc:
        return None

    messages: List[Dict[str, Any]] = []
    raw_messages = doc.get("messages") or []
    if isinstance(raw_messages, list):
        for message in raw_messages:
            if not isinstance(message, dict):
                continue
            role = _normalize_role(message.get("role"))
            if role in {"system", "tool", "toolcall", "tool-call"}:
                continue
            if role not in {"client", "ai"}:
                role = "ai"
            text = str(message.get("text") or "").strip()
            if not text:
                continue
            messages.append(_to_message(role, text, message.get("timestamp")))

    if not messages:
        messages = _messages_from_transcript(doc.get("transcript"))

    if not messages and doc.get("summary"):
        messages = [_to_message("ai", str(doc.get("summary")), doc.get("updated_at") or doc.get("ended_at"))]

    return {
        "callId": doc.get("vapi_call_id") or str(doc.get("_id")),
        "clientPhoneNumber": doc.get("customer_phone"),
        "ourPhoneNumber": None,
        "createdAt": _coerce_iso(doc.get("started_at") or doc.get("created_at") or doc.get("updated_at")),
        "durationSeconds": _normalize_duration_seconds(doc.get("duration"), doc.get("duration_seconds")),
        "status": doc.get("status"),
        "endedReason": doc.get("ended_reason") or doc.get("end_reason"),
        "assistantId": doc.get("assistant_id"),
        "messages": messages,
    }


@router.get("/calls")
async def list_calls(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="User has no tenant_id")

    cached = _get_cached_list(str(tenant_id), page, limit)
    if cached:
        return cached

    if not vapi_service.is_configured():
        raise HTTPException(status_code=503, detail="Vapi is not configured")

    try:
        payload = await _fetch_tenant_calls(str(tenant_id), page, limit)
        if not payload.get("items"):
            payload = await _fetch_tenant_calls_from_db(str(tenant_id), page, limit)
        _set_cached_list(str(tenant_id), page, limit, payload)
        return payload
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Failed to list calls for tenant {tenant_id}: {exc}", exc_info=True)
        raise HTTPException(status_code=502, detail="Unable to load call history right now. Please try again.")


@router.get("/calls/{call_id}")
async def get_call(call_id: str, current_user: dict = Depends(get_current_user)):
    tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="User has no tenant_id")

    if not vapi_service.is_configured():
        raise HTTPException(status_code=503, detail="Vapi is not configured")

    assistant_id = await _resolve_tenant_assistant_id(str(tenant_id))

    # Fast path: if we already have call details in tenant call_logs, return them first.
    db_fallback = await _fetch_call_from_db(str(tenant_id), call_id)
    if db_fallback and db_fallback.get("messages"):
        return db_fallback

    try:
        raw = await vapi_service.get_call(call_id)
        detail = _extract_call_details(raw)

        call_assistant_id = detail.get("assistantId")
        if assistant_id and call_assistant_id and str(call_assistant_id) != str(assistant_id):
            raise HTTPException(status_code=404, detail="Call not found")

        if not detail.get("messages"):
            if db_fallback:
                return db_fallback

        return detail
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning(f"Vapi detail fetch failed for {call_id}, trying DB fallback: {exc}")
        fallback = db_fallback or await _fetch_call_from_db(str(tenant_id), call_id)
        if fallback:
            return fallback
        logger.error(f"Failed to fetch call {call_id} for tenant {tenant_id}: {exc}", exc_info=True)
        raise HTTPException(status_code=502, detail="Unable to load call details right now. Please try again.")
