"""
Tests for live call transfer (services/call_transfer.py): the transferCall tool sent to Vapi, how the
transfer number is validated and applied, and the prompt rules that follow the tools.
Vapi and Mongo are replaced by fakes.
"""

import copy
import json
import os
import sys
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from fastapi import HTTPException

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import call_transfer, voice_languages  # noqa: E402
from services.assistant_service import AssistantService  # noqa: E402
from services.vapi_service import VapiService, vapi_service  # noqa: E402

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NUMBER = "+14155550123"
TN = voice_languages.TUNISIAN


def _enabled(*tool_ids):
    """tenant.enabled_tools entries for these built-in tools, as enable_tool stores them."""
    built_ins = {t["id"]: t for t in vapi_service.get_built_in_tools()}
    return [{"tool_id": tool_id, "config": built_ins[tool_id]["config"]} for tool_id in tool_ids]


def _transfers(tools):
    return [t for t in tools if t.get("type") == "transferCall"]


# ===== The Vapi tool =====

class TestTool:
    def test_number_becomes_the_destination(self):
        assert call_transfer.vapi_tool(NUMBER) == {
            "type": "transferCall",
            "destinations": [{
                "type": "number",
                "number": NUMBER,
                "message": "Please hold, I'm connecting you now.",
                "description": "Transfer to the business owner for emergencies or when the caller asks for a person",
            }],
        }

    def test_no_number_no_tool(self):
        assert call_transfer.vapi_tool(None) is None
        assert call_transfer.vapi_tool("") is None

    def test_hold_message_is_in_the_assistant_language(self):
        assert call_transfer.vapi_tool(NUMBER, TN)["destinations"][0]["message"] == call_transfer.HOLD_MESSAGES[TN]
        assert call_transfer.vapi_tool(NUMBER, "xx")["destinations"][0]["message"].startswith("Please hold")

    def test_only_a_transfer_with_a_destination_can_transfer(self):
        assert call_transfer.can_transfer([{"type": "endCall"}, call_transfer.vapi_tool(NUMBER)])
        assert not call_transfer.can_transfer([{"type": "transferCall", "destinations": []}])
        assert not call_transfer.can_transfer([{"type": "endCall"}])
        assert not call_transfer.can_transfer(None)


# ===== Prompt rules =====

class TestPromptRules:
    TOOLS = [call_transfer.vapi_tool(NUMBER)]

    def test_rules_only_while_the_tools_can_transfer(self):
        prompt = call_transfer.with_prompt_rules("You answer for Joe's Plumbing.", "en", self.TOOLS)
        assert prompt == "You answer for Joe's Plumbing.\n\n" + call_transfer.prompt_rules("en")
        assert call_transfer.with_prompt_rules("You answer for Joe's Plumbing.", "en", [{"type": "endCall"}]) == (
            "You answer for Joe's Plumbing."
        )

    def test_rules_are_replaced_not_stacked_and_come_out_cleanly(self):
        once = call_transfer.with_prompt_rules("Base prompt", "en", self.TOOLS)
        twice = call_transfer.with_prompt_rules(once, "en", self.TOOLS)
        assert twice == once and twice.count("<call_transfer>") == 1
        assert call_transfer.with_prompt_rules(twice, "en", []) == "Base prompt"

    def test_a_copy_pasted_old_block_is_removed_too(self):
        prompt = f"Intro\n\n{call_transfer.prompt_rules('en')}\n\nOutro"
        assert call_transfer.with_prompt_rules(prompt, "en", None) == "Intro\n\nOutro"

    def test_when_to_transfer(self):
        rules = call_transfer.prompt_rules("en")
        for case in ("burst pipe", "flooding", "sewage backing up", "no heat in freezing weather", "asks to speak to a person"):
            assert case in rules
        assert "calm enough" in rules and "name, phone number and the service address" in rules
        # The plumber template books emergency visits; with a transfer number the owner takes them live.
        assert "a transfer replaces booking a visit or promising a callback" in rules

    def test_the_gas_leak_rule_wins_over_a_transfer(self):
        rules = call_transfer.prompt_rules("en")
        assert "smells gas" in rules and "call 911 or the gas company from outside" in rules
        assert "Do not transfer that call" in rules
        assert rules.index("smells gas") < rules.index("Then call transferCall")
        tunisian = call_transfer.prompt_rules(TN)
        assert "civil protection" in tunisian and "911" not in tunisian


# ===== AssistantService: tools synced to Vapi, the transfer number =====

class FakeTenants:
    """TenantRepository stand-in holding one tenant; updates are applied like Mongo $set (dotted keys too)."""

    def __init__(self, tenant):
        self.tenant = tenant

    async def get_by_id(self, tenant_id):
        return copy.deepcopy(self.tenant)

    async def update(self, tenant_id, fields):
        for key, value in fields.items():
            target = self.tenant
            *parents, last = key.split(".")
            for parent in parents:
                target = target.setdefault(parent, {})
            target[last] = copy.deepcopy(value)
        return True


@pytest.fixture
def tenant():
    return {
        "_id": "t1",
        "name": "Joe's Plumbing",
        "vapi_assistant_id": "asst_1",
        "ai_config": {"language": "en", "system_prompt": "Plumber rules"},
        "enabled_tools": _enabled("check_availability", "book_appointment"),
    }


@pytest.fixture
def service(tenant, monkeypatch):
    """(AssistantService on the fake tenant, the tenant, the mocked vapi_service.update_assistant)."""
    svc = AssistantService(db=MagicMock())
    svc.tenant_repo = FakeTenants(tenant)
    update_assistant = AsyncMock(return_value={"updated": True})
    monkeypatch.setattr(vapi_service, "update_assistant", update_assistant)
    return svc, tenant, update_assistant


def _sent_tools(update_assistant):
    return update_assistant.await_args.kwargs["tools"]


class TestToolSync:
    @pytest.mark.asyncio
    async def test_number_set_sends_the_transfer_with_its_destination(self, service):
        svc, tenant, update_assistant = service
        tenant.update(transfer_phone_number=NUMBER, enabled_tools=_enabled("book_appointment", "transfer_call"))
        await svc._sync_tools_to_vapi("t1", tenant["enabled_tools"])
        tools = _sent_tools(update_assistant)
        assert _transfers(tools) == [call_transfer.vapi_tool(NUMBER)]
        assert [t["function"]["name"] for t in tools if t["type"] == "function"] == ["bookAppointment"]

    @pytest.mark.asyncio
    async def test_no_number_sends_no_transfer_tool(self, service):
        svc, tenant, update_assistant = service
        tenant["enabled_tools"] = _enabled("book_appointment", "transfer_call")  # switched on before numbers existed
        await svc._sync_tools_to_vapi("t1", tenant["enabled_tools"])
        tools = _sent_tools(update_assistant)
        assert _transfers(tools) == [] and len(tools) == 1

    @pytest.mark.asyncio
    async def test_a_lone_transfer_tool_without_a_number_still_clears_vapi(self, service):
        svc, tenant, update_assistant = service
        tenant["enabled_tools"] = _enabled("transfer_call")
        await svc._sync_tools_to_vapi("t1", tenant["enabled_tools"])
        assert _sent_tools(update_assistant) == []

    @pytest.mark.asyncio
    async def test_tunisian_assistant_says_the_hold_message_in_derja(self, service):
        svc, tenant, update_assistant = service
        tenant.update(transfer_phone_number=NUMBER, enabled_tools=_enabled("transfer_call"))
        tenant["ai_config"]["language"] = TN
        await svc._sync_tools_to_vapi("t1", tenant["enabled_tools"])
        assert _sent_tools(update_assistant) == [call_transfer.vapi_tool(NUMBER, TN)]


class TestTransferNumber:
    @pytest.mark.asyncio
    async def test_saving_a_number_turns_transfer_on_right_away(self, service):
        svc, tenant, update_assistant = service
        result = await svc.set_transfer_number("t1", " +1 (415) 555-0123 ")
        assert result == {"transfer_phone_number": NUMBER, "active": True}
        assert tenant["transfer_phone_number"] == NUMBER
        assert [t["tool_id"] for t in tenant["enabled_tools"]] == ["check_availability", "book_appointment", "transfer_call"]
        assert _transfers(_sent_tools(update_assistant)) == [call_transfer.vapi_tool(NUMBER)]
        assert await svc.get_transfer_number("t1") == result

    @pytest.mark.asyncio
    async def test_changing_the_number_keeps_a_single_transfer_tool(self, service):
        svc, tenant, update_assistant = service
        await svc.set_transfer_number("t1", NUMBER)
        await svc.set_transfer_number("t1", "+12125550199")
        assert [t["tool_id"] for t in tenant["enabled_tools"]].count("transfer_call") == 1
        assert _transfers(_sent_tools(update_assistant))[0]["destinations"][0]["number"] == "+12125550199"

    @pytest.mark.asyncio
    async def test_clearing_the_number_turns_transfer_off(self, service):
        svc, tenant, update_assistant = service
        await svc.set_transfer_number("t1", NUMBER)
        result = await svc.set_transfer_number("t1", "")
        assert result == {"transfer_phone_number": None, "active": False}
        assert tenant["transfer_phone_number"] is None
        assert "transfer_call" not in [t["tool_id"] for t in tenant["enabled_tools"]]
        assert update_assistant.await_count == 2 and _transfers(_sent_tools(update_assistant)) == []

    @pytest.mark.asyncio
    @pytest.mark.parametrize("raw", ["4155550123", "(415) 555-0123", "+1 415", "+0123456789", "call me", "+1415555012345678"])
    async def test_numbers_not_in_international_format_are_refused(self, service, raw):
        svc, tenant, update_assistant = service
        with pytest.raises(HTTPException) as error:
            await svc.set_transfer_number("t1", raw)
        assert error.value.status_code == 400 and "international format" in error.value.detail
        assert "transfer_phone_number" not in tenant
        update_assistant.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_the_business_own_calleem_number_is_refused(self, service):
        svc, tenant, update_assistant = service
        tenant["phone_config"] = {"phone_number": "+1 415-555-0123", "is_active": True}
        with pytest.raises(HTTPException) as error:
            await svc.set_transfer_number("t1", NUMBER)
        assert error.value.status_code == 400 and "Calleem number" in error.value.detail
        update_assistant.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_transfer_tool_cannot_be_switched_on_without_a_number(self, service):
        svc, _, update_assistant = service
        with pytest.raises(HTTPException) as error:
            await svc.enable_tool("t1", "transfer_call")
        assert error.value.status_code == 400
        update_assistant.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_a_kept_number_with_the_tool_switched_off_is_not_active(self, service):
        svc, _, update_assistant = service
        await svc.set_transfer_number("t1", NUMBER)
        await svc.disable_tool("t1", "transfer_call")
        assert _transfers(_sent_tools(update_assistant)) == []
        assert await svc.get_transfer_number("t1") == {"transfer_phone_number": NUMBER, "active": False}

    @pytest.mark.asyncio
    async def test_saving_a_number_without_an_assistant_creates_one_first(self, service, monkeypatch):
        svc, tenant, update_assistant = service
        del tenant["vapi_assistant_id"]

        async def provision(tenant_id, business_name, language=None):
            tenant["vapi_assistant_id"] = "asst_new"
            return {"assistant_id": "asst_new"}

        from services.provisioning import vapi_provisioning
        monkeypatch.setattr(vapi_provisioning, "provision_tenant_assistant", AsyncMock(side_effect=provision))
        assert (await svc.set_transfer_number("t1", NUMBER))["active"] is True
        assert update_assistant.await_args.args[0] == "asst_new"

    @pytest.mark.asyncio
    async def test_language_switch_says_the_hold_message_in_the_new_language(self, service, monkeypatch):
        svc, _, update_assistant = service
        await svc.set_transfer_number("t1", NUMBER)
        monkeypatch.setattr(vapi_service, "set_language", AsyncMock(return_value={"voice": {}, "firstMessage": "عسلامة"}))
        svc.get_knowledge_base = AsyncMock(return_value={"documents": [], "faqs": []})
        await svc.set_language("t1", TN)
        assert _transfers(_sent_tools(update_assistant)) == [call_transfer.vapi_tool(NUMBER, TN)]


def test_only_owners_and_admins_can_change_the_number():
    with open(os.path.join(BACKEND_DIR, "routers", "assistants.py"), encoding="utf-8") as f:
        lines = f.read().splitlines()

    def handler(decorator):
        start = lines.index(decorator)
        return "\n".join(lines[start:start + 6])

    assert "Depends(get_current_admin)" in handler('@router.put("/assistant/me/transfer-number")')
    assert "Depends(get_current_user)" in handler('@router.get("/assistant/me/transfer-number")')


# ===== VapiService: the prompt follows the tools =====

@pytest.fixture
def fake_vapi(monkeypatch):
    """Records requests; GET /assistant/{id} returns `state["assistant"]`."""
    monkeypatch.setenv("VAPI_PRIVATE_KEY", "test-key")
    state = {"requests": [], "assistant": {}}

    def handler(request):
        body = json.loads(request.content) if request.content else None
        state["requests"].append((request.method, request.url.path, body))
        if request.method == "GET":
            return httpx.Response(200, json=state["assistant"])
        return httpx.Response(200, json={"id": "asst_1", "name": "x", **(body or {})})

    real_client = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda *a, **k: real_client(transport=httpx.MockTransport(handler)))
    return state


def _patched_model(state):
    return next(body for method, _, body in state["requests"] if method == "PATCH")["model"]


def _assistant(tools, prompt=None):
    model = {"provider": "openai", "model": "gpt-4o-mini", "tools": tools}
    if prompt is not None:
        model["messages"] = [{"role": "system", "content": prompt}]
    return {"model": model, "metadata": {"tenant_id": "t1"}}


class TestPromptFollowsTools:
    @pytest.mark.asyncio
    async def test_switching_transfer_on_adds_the_rules(self, fake_vapi):
        fake_vapi["assistant"] = _assistant([{"type": "endCall"}], "Joe's prompt")
        await VapiService().update_assistant("asst_1", tools=[{"type": "endCall"}, call_transfer.vapi_tool(NUMBER)])
        model = _patched_model(fake_vapi)
        assert model["tools"] == [{"type": "endCall"}, call_transfer.vapi_tool(NUMBER)]
        assert model["messages"][0]["content"] == "Joe's prompt\n\n" + call_transfer.prompt_rules("en")

    @pytest.mark.asyncio
    async def test_switching_transfer_off_removes_them(self, fake_vapi):
        transfer = [call_transfer.vapi_tool(NUMBER)]
        fake_vapi["assistant"] = _assistant(transfer, call_transfer.with_prompt_rules("Joe's prompt", "en", transfer))
        await VapiService().update_assistant("asst_1", tools=[{"type": "endCall"}])
        assert _patched_model(fake_vapi)["messages"][0]["content"] == "Joe's prompt"

    @pytest.mark.asyncio
    async def test_assistants_that_never_transfer_keep_their_prompt_as_is(self, fake_vapi):
        fake_vapi["assistant"] = _assistant([{"type": "endCall"}], "Joe's prompt\n")
        await VapiService().update_assistant("asst_1", tools=[{"type": "endCall"}])
        assert _patched_model(fake_vapi)["messages"][0]["content"] == "Joe's prompt\n"

    @pytest.mark.asyncio
    async def test_prompt_rebuilds_keep_the_rules_while_the_assistant_can_transfer(self, fake_vapi):
        fake_vapi["assistant"] = _assistant([call_transfer.vapi_tool(NUMBER)])
        await VapiService().update_assistant("asst_1", company_name="Joe's Plumbing", instructions="Plumber rules",
                                             faqs=[{"question": "Weekends?", "answer": "Yes"}])
        prompt = _patched_model(fake_vapi)["messages"][0]["content"]
        assert "Plumber rules" in prompt and "Weekends?" in prompt
        assert prompt.endswith("\n\n" + call_transfer.prompt_rules("en")) and prompt.count("<call_transfer>") == 1

    @pytest.mark.asyncio
    async def test_language_switch_rewrites_the_rules_in_the_new_language(self, fake_vapi):
        fake_vapi["assistant"] = _assistant([call_transfer.vapi_tool(NUMBER)])
        await VapiService().set_language("asst_1", TN, "Joe's Plumbing", "", faqs=[])
        prompt = _patched_model(fake_vapi)["messages"][0]["content"]
        assert "Tunisian Derja" in prompt and prompt.endswith(call_transfer.prompt_rules(TN))
