"""
Tests for the SMS sent after a call (routers/vapi.send_sms_confirmation): only when the assistant
booked something during that call, with the real appointment details, never twice.
"""

import copy
import os
import sys
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytz
from bson import ObjectId

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routers import vapi  # noqa: E402
from services import provisioning  # noqa: E402
from utils.phone import to_e164  # noqa: E402

TENANT_ID = "64b000000000000000000001"
TZ = pytz.timezone("Africa/Tunis")


class _Cursor:
    def __init__(self, docs):
        self.docs = docs

    async def to_list(self, length=None):
        return self.docs


def _appointment(**extra):
    return {
        "_id": ObjectId(),
        "client_name": "Sam Ali",
        "client_phone": "55123456",
        "service": "Haircut",
        "datetime": datetime(2030, 10, 5, 13, 30),  # naive UTC, as Mongo returns it -> 14:30 in Tunis
        **extra,
    }


@pytest.fixture
def env(monkeypatch):
    db = MagicMock()
    db.appointments.find = MagicMock(return_value=_Cursor([_appointment()]))
    db.appointments.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
    db.business_config.find_one = AsyncMock(return_value={})
    db.tenants.find_one = AsyncMock(return_value={
        "_id": ObjectId(TENANT_ID), "name": "Salon Sam",
        "phone_config": {"phone_number": "+21670000000", "is_active": True},
    })
    db.sms_confirmations.insert_one = AsyncMock()
    monkeypatch.setattr(vapi, "get_database", lambda: db)
    monkeypatch.setattr(vapi.AppointmentsService, "_resolve_tenant_timezone", AsyncMock(return_value=TZ))
    send = AsyncMock(return_value={"success": True, "message_sid": "SM1"})
    monkeypatch.setattr(vapi.twilio_messaging, "send_sms", send)
    monkeypatch.setattr(vapi.twilio_messaging, "messaging_service_sid", "MG123")
    return db, send


class TestPhoneNumbers:
    """utils.phone.to_e164: whatever format the caller says, a full international number."""

    @pytest.mark.parametrize("raw, refs, expected", [
        ("55123456", ["+21698111222"], "+21655123456"),         # local, caller's country
        ("98 111 222", [None, "+21670000000"], "+21698111222"),  # web call: business's country
        ("(415) 555-0123", ["+14155550100"], "+14155550123"),    # US local
        ("14155550123", [None, "+21670000000"], "+14155550123"), # full number said without +
        ("0021655123456", [], "+21655123456"),
        ("+1 415 555 0123", [], "+14155550123"),
        ("12345", ["+21698111222"], None),                        # too short
        ("55123456", [], None),                                   # local with nothing to guess from
    ])
    def test_to_e164(self, raw, refs, expected):
        assert to_e164(raw, *refs) == expected


def test_confirmation_text_uses_business_time_and_fits_one_sms():
    text = vapi.confirmation_text("Salon Sam", _appointment(), TZ)
    assert text == "Hi Sam, your Haircut at Salon Sam is confirmed for Sat Oct 5 at 2:30 PM. Reply STOP to opt out."
    assert len(text) <= 160


@pytest.mark.asyncio
async def test_booking_during_the_call_is_confirmed_by_sms(env):
    db, send = env
    await vapi.send_sms_confirmation(TENANT_ID, "call-1", "+21698111222")
    send.assert_awaited_once()
    kwargs = send.await_args.kwargs
    assert kwargs["to"] == "+21655123456"
    assert kwargs["from_"] == "+21670000000"
    assert "Haircut at Salon Sam" in kwargs["body"]
    assert db.appointments.find.call_args.args[0]["vapi_call_id"] == "call-1"
    db.sms_confirmations.insert_one.assert_awaited_once()


@pytest.mark.asyncio
async def test_no_booking_no_sms(env):
    db, send = env
    db.appointments.find = MagicMock(return_value=_Cursor([]))
    await vapi.send_sms_confirmation(TENANT_ID, "call-1", "+21698111222")
    send.assert_not_awaited()


@pytest.mark.asyncio
async def test_repeated_call_report_does_not_text_twice(env):
    db, send = env
    db.appointments.update_one = AsyncMock(return_value=MagicMock(modified_count=0))  # already claimed
    await vapi.send_sms_confirmation(TENANT_ID, "call-1", "+21698111222")
    send.assert_not_awaited()


@pytest.mark.asyncio
async def test_business_can_turn_confirmations_off(env):
    db, send = env
    db.business_config.find_one = AsyncMock(return_value={"sms_config": {"send_confirmation_on_call_end": False}})
    await vapi.send_sms_confirmation(TENANT_ID, "call-1", "+21698111222")
    send.assert_not_awaited()


@pytest.mark.asyncio
async def test_falls_back_to_calleem_sender_when_business_number_cannot_text(env):
    db, send = env
    send.side_effect = [{"success": False, "error": "not SMS capable"}, {"success": True, "message_sid": "SM2"}]
    await vapi.send_sms_confirmation(TENANT_ID, "call-1", "+21698111222")
    assert send.await_count == 2
    assert send.await_args.kwargs["messaging_service_sid"] == "MG123"
    assert db.sms_confirmations.insert_one.await_args.args[0]["status"] == "sent"


@pytest.mark.asyncio
async def test_us_caller_booking_is_saved_with_full_number(monkeypatch):
    db = MagicMock()
    db.tenants.find_one = AsyncMock(return_value={"phone_config": {"phone_number": "+14155550100"}})
    db.business_config.find_one = AsyncMock(return_value={"timezone": "America/New_York"})
    db.appointments.update_one = AsyncMock()
    monkeypatch.setattr(vapi, "get_database", lambda: db)
    monkeypatch.setattr(vapi.socket_manager, "broadcast_to_tenant", AsyncMock())
    create = AsyncMock(return_value={"id": str(ObjectId())})
    monkeypatch.setattr(vapi.AppointmentsService, "create_appointment", create)

    result = await vapi.process_tool_call(
        "bookAppointment",
        {"name": "Dana Smith", "phone": "(415) 555-0123", "service": "Leak repair", "date": "2030-10-07", "time": "14:00"},
        TENANT_ID,
        {"id": "call-9", "customer": {"number": "+14155550199"}},
    )

    assert result.get("success"), result
    assert create.await_args.args[1].client_phone == "+14155550123"
    assert db.appointments.update_one.await_args.args[1]["$set"]["vapi_call_id"] == "call-9"


@pytest.mark.asyncio
async def test_existing_assistants_get_the_new_booking_tool(monkeypatch):
    old_tool = {"type": "function", "function": {"name": "bookAppointment", "parameters": {"properties": {
        "phone": {"type": "string", "description": "Customer phone number - exactly 8 digits without country code"},
    }}}}
    db = MagicMock()
    db.migrations.find_one = AsyncMock(return_value=None)
    db.migrations.insert_one = AsyncMock()
    db.tenants.find = MagicMock(return_value=_Cursor([
        {"_id": ObjectId(TENANT_ID), "vapi_assistant_id": "asst-1", "enabled_tools": [{"tool_id": "book_appointment", "config": copy.deepcopy(old_tool)}]},
    ]))
    db.tenants.update_one = AsyncMock()
    monkeypatch.setattr(provisioning, "get_database", lambda: db)
    fake_vapi = MagicMock()
    fake_vapi.is_configured = MagicMock(return_value=True)
    fake_vapi.get_assistant = AsyncMock(return_value={"model": {"provider": "openai", "tools": [copy.deepcopy(old_tool)]}})
    fake_vapi.patch_assistant = AsyncMock()
    monkeypatch.setattr(provisioning, "vapi_service", fake_vapi)

    await provisioning.update_booking_tools()

    patched = fake_vapi.patch_assistant.await_args.args[1]["model"]["tools"][0]["function"]["parameters"]["properties"]
    assert patched["phone"]["description"] == provisioning.BOOKING_PHONE_DESCRIPTION
    assert "service" in patched
    db.tenants.update_one.assert_awaited_once()
    db.migrations.insert_one.assert_awaited_once()
