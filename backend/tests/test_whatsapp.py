"""
Tests for WhatsApp (routers/whatsapp.py, services/whatsapp_cloud.py) and the text receptionist
(services/text_agent.py). Meta, Bedrock and Mongo are all replaced by fakes.
"""

import hashlib
import hmac
import json
import os
import sys
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from bson import ObjectId
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo.errors import DuplicateKeyError

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routers import whatsapp  # noqa: E402
from services import text_agent, whatsapp_cloud  # noqa: E402

APP_SECRET = "test-app-secret"
PHONE_NUMBER_ID = "106540352242922"
TENANT_ID = "64b000000000000000000001"


def _sign(body: bytes, secret: str = APP_SECRET) -> str:
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def _payload(phone_number_id=PHONE_NUMBER_ID, text="Hi, are you open tomorrow?", message_id="wamid.1"):
    return {
        "object": "whatsapp_business_account",
        "entry": [{"id": "WABA", "changes": [{"field": "messages", "value": {
            "messaging_product": "whatsapp",
            "metadata": {"display_phone_number": "15550001111", "phone_number_id": phone_number_id},
            "contacts": [{"profile": {"name": "Sam"}, "wa_id": "21650000000"}],
            "messages": [{"from": "21650000000", "id": message_id, "type": "text", "text": {"body": text}}],
        }}]}],
    }


class _Cursor:
    def __init__(self, docs):
        self.docs = docs

    async def to_list(self, length=None):
        return self.docs


@pytest.fixture
def db(monkeypatch):
    fake = MagicMock()
    account = {"_id": TENANT_ID, "tenant_id": TENANT_ID, "phone_number_id": PHONE_NUMBER_ID, "access_token": None}
    fake.whatsapp_accounts.find = MagicMock(
        side_effect=lambda q: _Cursor([account] if PHONE_NUMBER_ID in q["phone_number_id"]["$in"] else [])
    )
    fake.whatsapp_accounts.update_one = AsyncMock()
    fake.whatsapp_messages.insert_one = AsyncMock()
    monkeypatch.setattr(whatsapp, "get_database", lambda: fake)
    return fake


@pytest.fixture
def client(monkeypatch, db):
    monkeypatch.setattr(whatsapp.settings, "WHATSAPP_APP_SECRET", APP_SECRET)
    monkeypatch.setattr(whatsapp.settings, "WHATSAPP_VERIFY_TOKEN", "verify-me")
    monkeypatch.setattr(whatsapp.settings, "ENVIRONMENT", "production")
    app = FastAPI()
    app.state.limiter = whatsapp.limiter
    app.include_router(whatsapp.router, prefix="/api/v1/whatsapp")
    return TestClient(app)


class TestSignature:
    def test_valid_signature(self):
        body = b'{"a":1}'
        assert whatsapp_cloud.signature_valid(body, _sign(body), [APP_SECRET])

    def test_wrong_secret_or_tampered_body(self):
        body = b'{"a":1}'
        assert not whatsapp_cloud.signature_valid(body, _sign(body, "other"), [APP_SECRET])
        assert not whatsapp_cloud.signature_valid(b'{"a":2}', _sign(body), [APP_SECRET])
        assert not whatsapp_cloud.signature_valid(body, "", [APP_SECRET])


class TestWebhookVerification:
    def test_meta_handshake_returns_challenge(self, client):
        r = client.get("/api/v1/whatsapp/webhook", params={
            "hub.mode": "subscribe", "hub.verify_token": "verify-me", "hub.challenge": "12345",
        })
        assert r.status_code == 200
        assert r.text == "12345"

    def test_wrong_verify_token_is_refused(self, client):
        r = client.get("/api/v1/whatsapp/webhook", params={
            "hub.mode": "subscribe", "hub.verify_token": "nope", "hub.challenge": "12345",
        })
        assert r.status_code == 403


class TestWebhookMessages:
    def test_signed_message_is_answered(self, client, monkeypatch):
        answer = AsyncMock()
        monkeypatch.setattr(whatsapp, "_answer", answer)
        body = json.dumps(_payload()).encode()
        r = client.post("/api/v1/whatsapp/webhook", content=body, headers={
            "Content-Type": "application/json", "X-Hub-Signature-256": _sign(body),
        })
        assert r.status_code == 200
        answer.assert_awaited_once()
        account, message, name = answer.await_args.args
        assert account["tenant_id"] == TENANT_ID
        assert message["text"]["body"] == "Hi, are you open tomorrow?"
        assert name == "Sam"

    def test_bad_signature_is_refused(self, client, monkeypatch):
        answer = AsyncMock()
        monkeypatch.setattr(whatsapp, "_answer", answer)
        body = json.dumps(_payload()).encode()
        r = client.post("/api/v1/whatsapp/webhook", content=body, headers={
            "Content-Type": "application/json", "X-Hub-Signature-256": _sign(body, "attacker"),
        })
        assert r.status_code == 403
        answer.assert_not_awaited()

    def test_unsigned_message_refused_in_production_without_secret(self, client, monkeypatch):
        monkeypatch.setattr(whatsapp.settings, "WHATSAPP_APP_SECRET", "")
        answer = AsyncMock()
        monkeypatch.setattr(whatsapp, "_answer", answer)
        r = client.post("/api/v1/whatsapp/webhook", json=_payload())
        assert r.status_code == 403
        answer.assert_not_awaited()

    def test_number_nobody_connected_is_ignored(self, client, monkeypatch):
        answer = AsyncMock()
        monkeypatch.setattr(whatsapp, "_answer", answer)
        body = json.dumps(_payload(phone_number_id="999999999")).encode()
        r = client.post("/api/v1/whatsapp/webhook", content=body, headers={
            "Content-Type": "application/json", "X-Hub-Signature-256": _sign(body),
        })
        assert r.status_code == 200
        answer.assert_not_awaited()

    def test_status_updates_are_ignored(self, client, monkeypatch):
        answer = AsyncMock()
        monkeypatch.setattr(whatsapp, "_answer", answer)
        payload = _payload()
        del payload["entry"][0]["changes"][0]["value"]["messages"]
        body = json.dumps(payload).encode()
        r = client.post("/api/v1/whatsapp/webhook", content=body, headers={
            "Content-Type": "application/json", "X-Hub-Signature-256": _sign(body),
        })
        assert r.status_code == 200
        answer.assert_not_awaited()


class TestAnswer:
    @pytest.fixture
    def meta(self, monkeypatch):
        monkeypatch.setattr(whatsapp.whatsapp_cloud, "platform_token", lambda: "platform-token")
        monkeypatch.setattr(whatsapp.whatsapp_cloud, "mark_read", AsyncMock())
        send = AsyncMock()
        monkeypatch.setattr(whatsapp.whatsapp_cloud, "send_text", send)
        reply = AsyncMock(return_value=text_agent.AgentReply(text="Yes, we open at 9."))
        monkeypatch.setattr(whatsapp.text_receptionist, "reply", reply)
        return send, reply

    @pytest.mark.asyncio
    async def test_reply_is_sent_from_the_business_number(self, db, meta):
        send, reply = meta
        account = {"_id": TENANT_ID, "tenant_id": TENANT_ID, "phone_number_id": PHONE_NUMBER_ID}
        message = _payload()["entry"][0]["changes"][0]["value"]["messages"][0]
        await whatsapp._answer(account, message, "Sam")
        assert reply.await_args.kwargs["customer_phone"] == "+21650000000"
        assert reply.await_args.kwargs["channel"] == "whatsapp"
        send.assert_awaited_once_with(PHONE_NUMBER_ID, "platform-token", "21650000000", "Yes, we open at 9.")
        assert not whatsapp._conversation_locks  # lock released and forgotten

    @pytest.mark.asyncio
    async def test_meta_retry_of_the_same_message_is_not_answered_twice(self, db, meta):
        send, _ = meta
        db.whatsapp_messages.insert_one = AsyncMock(side_effect=DuplicateKeyError("dup"))
        account = {"_id": TENANT_ID, "tenant_id": TENANT_ID, "phone_number_id": PHONE_NUMBER_ID}
        message = _payload()["entry"][0]["changes"][0]["value"]["messages"][0]
        await whatsapp._answer(account, message, "Sam")
        send.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_voice_notes_get_a_polite_text_only_reply(self, db, meta):
        send, reply = meta
        account = {"_id": TENANT_ID, "tenant_id": TENANT_ID, "phone_number_id": PHONE_NUMBER_ID}
        await whatsapp._answer(account, {"from": "21650000000", "id": "wamid.2", "type": "audio"}, None)
        reply.assert_not_awaited()
        assert send.await_args.args[3] == whatsapp.UNSUPPORTED_MESSAGE_REPLY


class TestTextReceptionist:
    @pytest.fixture
    def agent(self, monkeypatch):
        fake_db = MagicMock()
        fake_db.text_conversations.find_one = AsyncMock(return_value=None)
        fake_db.text_conversations.update_one = AsyncMock()
        fake_db.appointments.update_one = AsyncMock()
        fake_db.tenants.find_one = AsyncMock(return_value={"phone_config": {"phone_number": "+21670000000"}})
        monkeypatch.setattr(text_agent, "get_database", lambda: fake_db)
        agent = text_agent.TextReceptionist()
        monkeypatch.setattr(agent, "_system_prompt", AsyncMock(return_value="prompt"))
        return agent, fake_db

    @pytest.mark.asyncio
    async def test_runs_tools_then_answers_without_thinking_tags(self, agent, monkeypatch):
        agent, fake_db = agent
        responses = [
            {"stopReason": "tool_use", "output": {"message": {"role": "assistant", "content": [
                {"text": "<thinking>check the slot</thinking>"},
                {"toolUse": {"toolUseId": "t1", "name": "checkAvailability", "input": {"date": "2026-10-05", "time": "14:00"}}},
            ]}}},
            {"stopReason": "end_turn", "output": {"message": {"role": "assistant", "content": [
                {"text": "<thinking>it is free</thinking>Good news, 2pm tomorrow is free! What's your name?"},
            ]}}},
        ]
        monkeypatch.setattr(agent, "_converse", AsyncMock(side_effect=responses))
        run_tool = AsyncMock(return_value={"available": True})
        monkeypatch.setattr(agent, "_run_tool", run_tool)

        reply = await agent.reply(TENANT_ID, "test:1", "Can I come tomorrow at 2pm?", channel="test")

        assert reply.text == "Good news, 2pm tomorrow is free! What's your name?"
        assert reply.tools_used == ["checkAvailability"]
        saved = fake_db.text_conversations.update_one.await_args.args[1]["$set"]["messages"]
        assert [m["role"] for m in saved] == ["user", "assistant", "user", "assistant"]
        assert saved[2]["content"][0]["toolResult"]["toolUseId"] == "t1"

    @pytest.mark.asyncio
    async def test_bedrock_failure_gives_a_fallback_and_keeps_history_valid(self, agent, monkeypatch):
        agent, fake_db = agent
        monkeypatch.setattr(agent, "_converse", AsyncMock(side_effect=RuntimeError("throttled")))
        reply = await agent.reply(TENANT_ID, "test:1", "Hello", channel="test")
        assert reply.text == text_agent.FALLBACK_REPLY
        assert fake_db.text_conversations.update_one.await_args.args[1]["$set"]["messages"] == []

    @pytest.mark.asyncio
    async def test_whatsapp_booking_uses_the_sender_number(self, agent, monkeypatch):
        agent, fake_db = agent
        appointment_id = str(ObjectId())
        monkeypatch.setattr(agent.appointments, "check_availability", AsyncMock(return_value={
            "available": True, "requested_datetime": "2030-10-05T14:00:00+01:00",
        }))
        create = AsyncMock(return_value={"id": appointment_id})
        monkeypatch.setattr(agent.appointments, "create_appointment", create)

        result = await agent._run_tool(
            TENANT_ID, "bookAppointment",
            {"name": "Sam Ali", "service": "Haircut", "date": "2030-10-05", "time": "14:00"},
            "whatsapp", "+21650000000",
        )

        assert result["success"] and result["appointment_id"] == appointment_id
        booked = create.await_args.args[1]
        assert booked.client_phone == "+21650000000"
        assert booked.datetime == datetime.fromisoformat("2030-10-05T14:00:00+01:00")
        fake_db.appointments.update_one.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_booking_a_taken_slot_is_refused(self, agent, monkeypatch):
        agent, _ = agent
        monkeypatch.setattr(agent.appointments, "check_availability", AsyncMock(return_value={
            "available": False, "reason": "Time slot is already booked",
        }))
        create = AsyncMock()
        monkeypatch.setattr(agent.appointments, "create_appointment", create)
        result = await agent._run_tool(
            TENANT_ID, "bookAppointment",
            {"name": "Sam", "service": "Haircut", "date": "2030-10-05", "time": "14:00", "phone": "+21650000000"},
            "test", None,
        )
        assert "already booked" in result["error"]
        create.assert_not_awaited()
