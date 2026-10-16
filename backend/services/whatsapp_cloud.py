"""
WhatsApp Cloud API (Meta)
=========================
Sends replies from a business's WhatsApp number and checks webhook signatures.

Each business connects one number (its Phone number ID). Calls use the business's own access token
when it gave one, otherwise Calleem's platform token (WHATSAPP_TOKEN), which works for every number
in a WhatsApp Business Account Calleem manages.
"""

import hashlib
import hmac
import logging
import os
from typing import Any, Dict, Iterable, Optional

import httpx

from utils.config import settings

logger = logging.getLogger(__name__)

GRAPH_API_VERSION = os.getenv("WHATSAPP_GRAPH_VERSION", "v23.0")
GRAPH_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
MAX_TEXT_LENGTH = 4096  # WhatsApp's limit for one text message


class WhatsAppError(Exception):
    """Meta refused the request; the message is safe to show to the business owner."""


def _error_message(response: httpx.Response) -> str:
    try:
        error = response.json().get("error") or {}
        return error.get("error_user_msg") or error.get("message") or response.text[:200]
    except ValueError:
        return response.text[:200]


async def _graph(method: str, path: str, token: str, **kwargs) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.request(
            method, f"{GRAPH_URL}/{path}", headers={"Authorization": f"Bearer {token}"}, **kwargs
        )
    if response.status_code >= 400:
        raise WhatsAppError(_error_message(response))
    return response.json()


async def get_phone_number(phone_number_id: str, token: str) -> Dict[str, Any]:
    """The number's display form and approved business name; proves the token can use this number."""
    return await _graph(
        "GET", phone_number_id, token,
        params={"fields": "display_phone_number,verified_name,quality_rating"},
    )


async def send_text(phone_number_id: str, token: str, to: str, body: str) -> Dict[str, Any]:
    """Free-form text: allowed within 24 hours of the customer's last message (we only ever reply)."""
    return await _graph("POST", f"{phone_number_id}/messages", token, json={
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"preview_url": False, "body": body[:MAX_TEXT_LENGTH]},
    })


async def mark_read(phone_number_id: str, token: str, message_id: str) -> None:
    """Blue ticks plus a typing indicator while the assistant writes its answer."""
    try:
        await _graph("POST", f"{phone_number_id}/messages", token, json={
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
            "typing_indicator": {"type": "text"},
        })
    except (WhatsAppError, httpx.HTTPError) as e:
        logger.info(f"Could not mark WhatsApp message as read: {e}")


def signature_valid(raw_body: bytes, signature_header: str, app_secrets: Iterable[str]) -> bool:
    """Meta signs every webhook with the app secret: X-Hub-Signature-256: sha256=<hex>."""
    if not signature_header.startswith("sha256="):
        return False
    received = signature_header[len("sha256="):]
    for secret in app_secrets:
        expected = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
        if hmac.compare_digest(expected, received):
            return True
    return False


def platform_token() -> Optional[str]:
    return settings.WHATSAPP_TOKEN or None
