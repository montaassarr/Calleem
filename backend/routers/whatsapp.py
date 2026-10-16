"""
WhatsApp API Router
===================
WhatsApp Cloud API (Meta): a business connects its number, customers' messages arrive on the
webhook and the AI receptionist (services/text_agent.py) answers them. The dashboard Chat Test
talks to the same assistant.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from pymongo.errors import DuplicateKeyError
from slowapi import Limiter
from slowapi.util import get_remote_address

from database.mongo_config import get_database
from routers.users import get_current_admin, get_current_user
from services import whatsapp_cloud
from services.text_agent import text_receptionist
from utils.config import settings
from utils.encryption import decrypt_value, encrypt_value

logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

ADMIN_ROLES = ("owner", "admin", "super_admin")
UNSUPPORTED_MESSAGE_REPLY = "Thanks! I can only read text messages for now. Could you type your question?"


def _tenant_id(current_user: dict) -> str:
    tenant_id = current_user.get("tenant_id") or current_user.get("business_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="User has no business")
    return str(tenant_id)


def _webhook_url() -> str:
    return f"{settings.BACKEND_URL.rstrip('/')}{settings.API_V1_PREFIX}/whatsapp/webhook"


def _account_token(account: Dict[str, Any]) -> Optional[str]:
    if account.get("access_token"):
        return decrypt_value(account["access_token"])
    return whatsapp_cloud.platform_token()


def _account_app_secret(account: Dict[str, Any]) -> Optional[str]:
    if account.get("app_secret"):
        return decrypt_value(account["app_secret"])
    return settings.WHATSAPP_APP_SECRET or None


# ==================== CONNECTION (dashboard) ====================

@router.get("/status")
async def get_whatsapp_status(current_user: dict = Depends(get_current_user)):
    """Is this business's WhatsApp number connected, plus what Meta needs for the webhook."""
    db = get_database()
    tenant_id = _tenant_id(current_user)
    account = await db.whatsapp_accounts.find_one({"_id": tenant_id}) or {}
    is_admin = current_user.get("role") in ADMIN_ROLES
    return {
        "configured": bool(account),
        "status": "connected" if account else "not_configured",
        "phone_number": account.get("display_phone_number"),
        "verified_name": account.get("verified_name"),
        "phone_number_id": account.get("phone_number_id"),
        "waba_id": account.get("waba_id"),
        "uses_own_token": bool(account.get("access_token")),
        "has_app_secret": bool(account.get("app_secret")),
        "connected_at": account.get("connected_at"),
        "last_message_at": account.get("last_message_at"),
        # Calleem's own Meta app is ready to host numbers (no token needed from the business).
        "platform_ready": bool(settings.WHATSAPP_TOKEN and settings.WHATSAPP_APP_SECRET),
        "webhook_url": _webhook_url(),
        # Only needed by a business that uses its own Meta app.
        "verify_token": settings.WHATSAPP_VERIFY_TOKEN if is_admin else None,
    }


class WhatsAppConnection(BaseModel):
    phone_number_id: str = Field(..., pattern=r"^\d{5,25}$")
    waba_id: Optional[str] = Field(None, pattern=r"^(\d{5,25})?$")
    # Leave empty to keep the saved token, or to use Calleem's platform token.
    access_token: Optional[str] = Field(None, max_length=1000)
    app_secret: Optional[str] = Field(None, max_length=200)


@router.put("/connection")
async def connect_whatsapp(body: WhatsAppConnection, current_admin: dict = Depends(get_current_admin)):
    """Connect (or update) this business's WhatsApp number after checking the token with Meta."""
    db = get_database()
    tenant_id = _tenant_id(current_admin)
    existing = await db.whatsapp_accounts.find_one({"_id": tenant_id}) or {}
    same_number = existing.get("phone_number_id") == body.phone_number_id

    access_token = (body.access_token or "").strip()
    if not access_token and same_number and existing.get("access_token"):
        access_token = decrypt_value(existing["access_token"])
    token = access_token or whatsapp_cloud.platform_token()
    if not token:
        raise HTTPException(status_code=400, detail="Paste the access token from your Meta app.")

    other = await db.whatsapp_accounts.find_one({"phone_number_id": body.phone_number_id, "_id": {"$ne": tenant_id}})
    if other:
        raise HTTPException(status_code=409, detail="This WhatsApp number is already connected to another business.")

    try:
        number = await whatsapp_cloud.get_phone_number(body.phone_number_id, token)
    except whatsapp_cloud.WhatsAppError as e:
        raise HTTPException(status_code=400, detail=f"Meta refused this number or token: {e}")
    except Exception as e:
        logger.error(f"Could not reach Meta for tenant {tenant_id}: {e}")
        raise HTTPException(status_code=502, detail="Could not reach Meta. Please try again.")

    app_secret = (body.app_secret or "").strip()
    now = datetime.utcnow()
    fields: Dict[str, Any] = {
        "tenant_id": tenant_id,
        "phone_number_id": body.phone_number_id,
        "waba_id": body.waba_id or None,
        "display_phone_number": number.get("display_phone_number"),
        "verified_name": number.get("verified_name"),
        "access_token": encrypt_value(access_token) if access_token else None,
        "updated_at": now,
    }
    if app_secret:
        fields["app_secret"] = encrypt_value(app_secret)
    elif not same_number:
        fields["app_secret"] = None
    try:
        await db.whatsapp_accounts.update_one(
            {"_id": tenant_id}, {"$set": fields, "$setOnInsert": {"connected_at": now}}, upsert=True
        )
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="This WhatsApp number is already connected to another business.")
    logger.info(f"WhatsApp number ***{str(number.get('display_phone_number', ''))[-4:]} connected for tenant {tenant_id}")
    return await get_whatsapp_status(current_admin)


@router.delete("/connection")
async def disconnect_whatsapp(current_admin: dict = Depends(get_current_admin)):
    """Stop answering this business's WhatsApp messages (the number stays in Meta)."""
    await get_database().whatsapp_accounts.delete_one({"_id": _tenant_id(current_admin)})
    return {"success": True}


@router.get("/conversations")
async def list_whatsapp_conversations(
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    """Latest WhatsApp conversations the assistant handled, with their transcripts."""
    docs = await get_database().text_conversations.find(
        {"tenant_id": _tenant_id(current_user), "channel": "whatsapp"},
        {"messages": 0},
    ).sort("updated_at", -1).limit(limit).to_list(limit)
    return [
        {
            "id": doc["_id"],
            "customer_phone": doc.get("customer_phone"),
            "customer_name": doc.get("customer_name"),
            "updated_at": doc.get("updated_at"),
            "transcript": (doc.get("transcript") or [])[-50:],
        }
        for doc in docs
    ]


# ==================== CHAT TEST (dashboard) ====================

class TestChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(..., pattern=r"^[A-Za-z0-9-]{8,64}$")


def _test_conversation_id(current_user: dict, session_id: str) -> str:
    user_id = current_user.get("id") or current_user.get("_id") or current_user.get("username")
    return f"test:{_tenant_id(current_user)}:{user_id}:{session_id}"


@router.post("/test-chat")
@limiter.limit("30/minute")
async def test_chat(request: Request, body: TestChatMessage, current_user: dict = Depends(get_current_user)):
    """The owner chats with their assistant exactly as a customer would on WhatsApp."""
    reply = await text_receptionist.reply(
        _tenant_id(current_user),
        _test_conversation_id(current_user, body.session_id),
        body.message.strip(),
        channel="test",
    )
    return {"response": reply.text, "tools_used": reply.tools_used, "appointment_id": reply.appointment_id}


@router.delete("/test-chat/{session_id}")
async def reset_test_chat(session_id: str, current_user: dict = Depends(get_current_user)):
    await get_database().text_conversations.delete_one({"_id": _test_conversation_id(current_user, session_id)})
    return {"success": True}


# ==================== META WEBHOOK ====================

@router.get("/webhook")
async def verify_webhook(
    mode: str = Query("", alias="hub.mode"),
    verify_token: str = Query("", alias="hub.verify_token"),
    challenge: str = Query("", alias="hub.challenge"),
):
    """Meta calls this once when the callback URL is saved in the app dashboard."""
    expected = settings.WHATSAPP_VERIFY_TOKEN
    if mode == "subscribe" and expected and verify_token == expected:
        return PlainTextResponse(challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


# One reply at a time per customer, so quick successive messages don't race on the history.
_conversation_locks: Dict[str, asyncio.Lock] = {}
_lock_users: Dict[str, int] = {}


async def _answer(account: Dict[str, Any], message: Dict[str, Any], customer_name: Optional[str]) -> None:
    """Reply to one customer message. Runs after Meta got its 200, one message at a time per customer."""
    db = get_database()
    message_id = message.get("id")
    customer = message.get("from")
    if not message_id or not customer:
        return
    try:
        await db.whatsapp_messages.insert_one({
            "_id": message_id,
            "tenant_id": account["tenant_id"],
            "customer_phone": customer,
            "type": message.get("type"),
            "created_at": datetime.utcnow(),
        })
    except DuplicateKeyError:
        return  # Meta retried a message we already answered
    if message.get("type") == "reaction":
        return  # an emoji on one of our messages needs no answer

    try:
        token = _account_token(account)
    except ValueError as e:
        logger.error(f"Cannot read the WhatsApp token of tenant {account['tenant_id']}: {e}")
        return
    phone_number_id = account["phone_number_id"]
    await whatsapp_cloud.mark_read(phone_number_id, token, message_id)

    conversation_id = f"wa:{account['tenant_id']}:{customer}"
    lock = _conversation_locks.setdefault(conversation_id, asyncio.Lock())
    _lock_users[conversation_id] = _lock_users.get(conversation_id, 0) + 1
    try:
        async with lock:
            if message.get("type") == "text":
                reply = await text_receptionist.reply(
                    account["tenant_id"],
                    conversation_id,
                    (message.get("text") or {}).get("body", ""),
                    channel="whatsapp",
                    customer_phone=f"+{customer}",
                    customer_name=customer_name,
                )
                text = reply.text
            else:
                text = UNSUPPORTED_MESSAGE_REPLY
            await whatsapp_cloud.send_text(phone_number_id, token, customer, text)
            await db.whatsapp_accounts.update_one(
                {"_id": account["_id"]}, {"$set": {"last_message_at": datetime.utcnow()}}
            )
    except Exception as e:
        logger.error(f"WhatsApp reply failed for tenant {account['tenant_id']}: {e}")
    finally:
        _lock_users[conversation_id] -= 1
        if not _lock_users[conversation_id]:
            del _lock_users[conversation_id], _conversation_locks[conversation_id]


@router.post("/webhook")
@limiter.limit("120/minute")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    """Customers' messages from Meta (signed with the Meta app secret). Answered in the background."""
    raw_body = await request.body()
    try:
        payload = json.loads(raw_body)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # value.metadata.phone_number_id says which business number each change is for.
    changes: List[Dict[str, Any]] = [
        change.get("value") or {}
        for entry in payload.get("entry") or []
        for change in entry.get("changes") or []
        if change.get("field") == "messages"
    ]
    phone_number_ids = {(value.get("metadata") or {}).get("phone_number_id") for value in changes} - {None}
    if not phone_number_ids:
        return {"success": True}

    db = get_database()
    accounts = {
        account["phone_number_id"]: account
        for account in await db.whatsapp_accounts.find({"phone_number_id": {"$in": list(phone_number_ids)}}).to_list(50)
    }

    signature = request.headers.get("X-Hub-Signature-256", "")
    verified: Dict[str, bool] = {}
    for phone_number_id, account in accounts.items():
        secret = _account_app_secret(account)
        if secret:
            verified[phone_number_id] = whatsapp_cloud.signature_valid(raw_body, signature, [secret])
        else:
            # No app secret anywhere: only acceptable while developing locally.
            verified[phone_number_id] = settings.ENVIRONMENT not in ("production", "prod")
            logger.warning(f"No WhatsApp app secret for number {phone_number_id}: signature not checked")
    if accounts and not any(verified.values()):
        logger.warning("Rejected WhatsApp webhook: invalid signature")
        raise HTTPException(status_code=403, detail="Invalid signature")

    for value in changes:
        phone_number_id = (value.get("metadata") or {}).get("phone_number_id")
        account = accounts.get(phone_number_id)
        if not account:
            logger.info(f"WhatsApp message for number {phone_number_id}, which no business has connected")
            continue
        if not verified.get(phone_number_id):
            continue
        names = {c.get("wa_id"): (c.get("profile") or {}).get("name") for c in value.get("contacts") or []}
        for message in value.get("messages") or []:
            background_tasks.add_task(_answer, account, message, names.get(message.get("from")))
    return {"success": True}
