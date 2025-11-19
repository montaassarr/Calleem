"""Voice + WhatsApp shared data store CRUD demo.

This script exercises the same Mongo collections that both the WhatsApp
conversation manager and the Vapi-based voice agent rely on. It shows how
voice configuration settings (prompt, first message, voice, and tool list)
are stored, read, updated, and removed from the `business_configs`
collection, and it also confirms that the reusable tool catalog comes from
`voice_agent.tools` (shared with the WhatsApp workflows).

Run it from the repo root after your `.env` is configured and MongoDB is
running:

```
python backend/scripts/voice_crud_demo.py
```
"""
from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from pprint import pprint
from typing import Any, Dict

import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from database.mongo_config import connect_to_mongo, close_mongo_connection, get_database
from utils.config import settings
from voice_agent.tools import voice_tools

BUSINESS_ID = "voice_crud_demo"


def _voice_payload(name_suffix: str) -> Dict[str, Any]:
    """Return a sample business config document with voice settings."""
    return {
        "business_id": BUSINESS_ID,
        "business_name": f"{settings.BUSINESS_NAME} ({name_suffix})",
        "business_phone": settings.BUSINESS_PHONE,
        "business_email": settings.BUSINESS_EMAIL,
        "timezone": settings.TIMEZONE,
        "features_enabled": {"voice_agent": True},
        "voice_config": {
            "model_provider": "groq",
            "model_name": "llama-3.3-70b-versatile",
            "temperature": 0.6,
            "max_tokens": 400,
            "voice_provider": "openai",
            "voice_id": "alloy",
            "first_message": "Hi! This is the voice demo. How can I help?",
            "system_prompt": "You are the demo receptionist. Always sound cheerful.",
            "enabled_tools": [
                "check_availability",
                "book_appointment",
                "get_services",
            ],
            "end_call_on_goodbye": True,
            "record_calls": True,
            "silence_timeout_seconds": 25,
        },
        "updated_at": datetime.utcnow(),
        "created_at": datetime.utcnow(),
    }


def _updated_voice_fields() -> Dict[str, Any]:
    """Return the payload used in the UPDATE step."""
    return {
        "voice_config": {
            "model_provider": "groq",
            "model_name": "llama-3.3-70b-versatile",
            "temperature": 0.55,
            "max_tokens": 350,
            "voice_provider": "11labs",
            "voice_id": "rachel",
            "first_message": "Hello, this is Ava from the demo line!",
            "system_prompt": "You are Ava. Confirm bookings and keep notes short.",
            "enabled_tools": [
                "check_availability",
                "book_appointment",
                "get_services",
                "update_appointment",
                "cancel_appointment",
            ],
            "end_call_on_goodbye": False,
            "record_calls": False,
            "silence_timeout_seconds": 20,
        },
        "updated_at": datetime.utcnow(),
    }


def _summarize(config: Dict[str, Any]) -> Dict[str, Any]:
    """Compact summary for console output."""
    voice_config = config.get("voice_config", {})
    return {
        "business_id": config.get("business_id"),
        "first_message": voice_config.get("first_message"),
        "system_prompt": voice_config.get("system_prompt"),
        "voice": f"{voice_config.get('voice_provider')}::{voice_config.get('voice_id')}",
        "model": f"{voice_config.get('model_provider')}::{voice_config.get('model_name')}",
        "enabled_tools": voice_config.get("enabled_tools"),
        "advanced": {
            "end_call_on_goodbye": voice_config.get("end_call_on_goodbye"),
            "record_calls": voice_config.get("record_calls"),
            "silence_timeout_seconds": voice_config.get("silence_timeout_seconds"),
        },
    }


async def main() -> None:
    await connect_to_mongo()
    db = get_database()
    if db is None:
        raise RuntimeError("Mongo database unavailable. Start MongoDB and retry.")

    print("\n=== Voice Agent CRUD Demo (shared Mongo collections) ===\n")

    # CREATE / UPSERT
    print("[CREATE] Writing demo voice configuration...")
    await db.business_configs.update_one(
        {"business_id": BUSINESS_ID},
        {"$set": _voice_payload("Initial Config")},
        upsert=True,
    )
    created = await db.business_configs.find_one({"business_id": BUSINESS_ID})
    pprint(_summarize(created))

    # READ
    print("\n[READ] Fetching stored configuration directly from Mongo...")
    stored = await db.business_configs.find_one({"business_id": BUSINESS_ID})
    pprint(_summarize(stored))

    # UPDATE
    print("\n[UPDATE] Switching voice + prompt + tools...")
    await db.business_configs.update_one(
        {"business_id": BUSINESS_ID},
        {"$set": _updated_voice_fields()},
    )
    updated = await db.business_configs.find_one({"business_id": BUSINESS_ID})
    pprint(_summarize(updated))

    # Demonstrate shared tool catalog (WhatsApp + Voice)
    print("\n[TOOLS] Voice agent function catalog (shared with WhatsApp flows):")
    for tool in voice_tools.get_tool_definitions():
        fn = tool.get("function", {})
        print(f" - {fn.get('name')}: {fn.get('description')}")

    # DELETE
    print("\n[DELETE] Cleaning up demo document...")
    await db.business_configs.delete_one({"business_id": BUSINESS_ID})
    remaining = await db.business_configs.find_one({"business_id": BUSINESS_ID})
    print("Remaining document:", remaining)

    print("\nCRUD demo complete — WhatsApp + Voice now read the same collections.\n")

    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())
