"""
Tests for the Tunisian Arabic (Derja) voice stack: services/voice_languages.py, how VapiService and
AssistantService apply it, prices in the business currency, and the text agent's Derja rule.
Vapi and Mongo are replaced by fakes.
"""

import json
import os
import sys
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
import pytz

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import text_agent, voice_languages  # noqa: E402
from services.assistant_service import AssistantService  # noqa: E402
from services.vapi_service import VapiService  # noqa: E402
from utils.money import format_price  # noqa: E402

TN = voice_languages.TUNISIAN


@pytest.fixture(autouse=True)
def clean_tn_env(monkeypatch):
    for name in ("TN_TRANSCRIBER", "TN_LLM", "TN_ELEVENLABS_VOICES", "TN_ELEVENLABS_MODEL"):
        monkeypatch.delenv(name, raising=False)


class TestTunisianStack:
    def test_defaults(self):
        transcriber = voice_languages.transcriber(TN)
        assert transcriber["provider"] == "azure" and transcriber["language"] == "ar-TN"
        assert transcriber["fallbackPlan"]["transcribers"][0] == {"provider": "deepgram", "model": "nova-3", "language": "ar"}
        assert voice_languages.llm(TN) == {"provider": "openai", "model": "gpt-4o"}
        assert voice_languages.tunisian_voice() == {"provider": "azure", "voiceId": "ar-TN-ReemNeural"}

    def test_english_stack_is_the_original_one(self):
        assert voice_languages.transcriber("en") == {"provider": "deepgram", "model": "nova-2", "language": "en"}
        assert voice_languages.llm("en") == {"provider": "openai", "model": "gpt-4o-mini"}
        assert voice_languages.normalize("xx") == "en"

    def test_transcriber_and_llm_can_be_swapped(self, monkeypatch):
        monkeypatch.setenv("TN_TRANSCRIBER", "soniox")
        monkeypatch.setenv("TN_LLM", "google:gemini-3.5-flash")
        assert voice_languages.transcriber(TN)["languages"] == ["ar", "fr"]
        assert voice_languages.llm(TN) == {"provider": "google", "model": "gemini-3.5-flash"}

    def test_bad_overrides_fall_back_to_defaults(self, monkeypatch):
        monkeypatch.setenv("TN_TRANSCRIBER", "whisper-from-mars")
        monkeypatch.setenv("TN_LLM", "gpt-4o")  # missing the provider
        assert voice_languages.transcriber(TN)["provider"] == "azure"
        assert voice_languages.llm(TN) == {"provider": "openai", "model": "gpt-4o"}

    def test_presets_are_not_shared_between_calls(self, monkeypatch):
        monkeypatch.setenv("TN_TRANSCRIBER", "soniox")
        voice_languages.transcriber(TN)["languages"].append("en")
        assert voice_languages.transcriber(TN)["languages"] == ["ar", "fr"]


class TestTunisianVoices:
    def test_azure_voices_without_elevenlabs(self):
        voices = voice_languages.tunisian_voices()
        assert [v["id"] for v in voices] == ["ar-TN-ReemNeural", "ar-TN-HediNeural"]
        assert all(v["provider"] == "azure" and v["accent"] == "Tunisian" for v in voices)

    def test_cloned_elevenlabs_voice_becomes_the_default(self, monkeypatch):
        monkeypatch.setenv("TN_ELEVENLABS_VOICES", "abc123:Amira:female, def456:Skander:male")
        voices = voice_languages.tunisian_voices()
        assert [(v["id"], v["provider"], v["name"]) for v in voices[:2]] == [
            ("abc123", "11labs", "Amira"), ("def456", "11labs", "Skander")
        ]
        config = voice_languages.tunisian_voice()
        assert config["voiceId"] == "abc123" and config["provider"] == "11labs"
        assert config["model"] == "eleven_turbo_v2_5" and config["language"] == "ar"
        assert config["fallbackPlan"] == {"voices": [{"provider": "azure", "voiceId": "ar-TN-ReemNeural"}]}

    def test_male_clone_falls_back_to_the_male_azure_voice(self, monkeypatch):
        monkeypatch.setenv("TN_ELEVENLABS_VOICES", "def456:Skander:male")
        assert voice_languages.tunisian_voice("def456")["fallbackPlan"]["voices"][0]["voiceId"] == "ar-TN-HediNeural"

    def test_empty_model_override_keeps_the_default_model(self, monkeypatch):
        monkeypatch.setenv("TN_ELEVENLABS_VOICES", "abc123")
        monkeypatch.setenv("TN_ELEVENLABS_MODEL", "")
        assert voice_languages.tunisian_voice()["model"] == "eleven_turbo_v2_5"

    def test_picker_group_id_maps_to_the_real_provider(self):
        config = voice_languages.tunisian_voice("ar-TN-HediNeural", "tunisian", 1.1)
        assert config == {"provider": "azure", "voiceId": "ar-TN-HediNeural", "speed": 1.1}


class TestPrompts:
    def test_derja_prompt(self):
        instructions = "Dental clinic, closed on Sundays.\n\n**CURRENT DATE: Monday, January 05, 2026**\nToday is January 05, 2026 in the business timezone.\nUse this date to resolve relative dates like tomorrow, next week, or Friday."
        prompt = voice_languages.system_prompt(TN, "Clinique Yasmine", instructions)
        assert "Clinique Yasmine" in prompt and "closed on Sundays" in prompt
        assert "CURRENT DATE" not in prompt  # the stale saved date is replaced by Vapi's live date
        assert voice_languages.TUNIS_NOW in prompt
        assert "{company_name}" not in prompt and "{instructions}" not in prompt
        assert "bookAppointment()" in prompt and "زوز" in prompt and "جانفي" in prompt

    def test_derja_greeting_and_default_instructions(self):
        assert voice_languages.first_message(TN, "Clinique Yasmine").startswith("عسلامة")
        assert voice_languages.default_instructions(TN, "Clinique Yasmine") == ""
        assert "no extra instructions" in voice_languages.system_prompt(TN, "X", "")

    def test_untouched_instructions_are_detected(self):
        english_default = voice_languages.default_instructions("en", "Acme")
        assert voice_languages.is_default_instructions(english_default, "Acme")
        assert voice_languages.is_default_instructions("", "Acme")
        assert not voice_languages.is_default_instructions(english_default + "\nWe close on Sundays.", "Acme")

    def test_faq_section(self):
        faqs = [{"question": "Parking?", "answer": "Yes, free."}, {"question": " ", "answer": "ignored"}]
        assert voice_languages.faq_section("en", faqs).endswith("use the provided answer exactly.\n")
        assert "said in Tunisian Derja" in voice_languages.faq_section(TN, faqs)
        assert "ignored" not in voice_languages.faq_section(TN, faqs)
        assert voice_languages.faq_section(TN, []) == ""


# ===== VapiService against a fake Vapi API =====

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


def _sent(state, method):
    return [body for m, _, body in state["requests"] if m == method]


class TestVapiService:
    @pytest.mark.asyncio
    async def test_create_tunisian_assistant(self, fake_vapi):
        result = await VapiService().create_assistant(
            tenant_id="t1", company_name="Clinique Yasmine", instructions="", language=TN
        )
        body = _sent(fake_vapi, "POST")[0]
        assert body["transcriber"]["language"] == "ar-TN"
        assert body["voice"] == {"provider": "azure", "voiceId": "ar-TN-ReemNeural", "speed": 1.0}
        assert (body["model"]["provider"], body["model"]["model"]) == ("openai", "gpt-4o")
        assert body["firstMessage"].startswith("عسلامة")
        assert body["metadata"]["language"] == TN
        assert "Tunisian Derja" in body["model"]["messages"][0]["content"]
        assert result["voice"] == "ar-TN-ReemNeural" and result["voice_provider"] == "azure"

    @pytest.mark.asyncio

    async def test_updates_keep_the_tunisian_stack(self, fake_vapi):
        fake_vapi["assistant"] = {"model": {"provider": "openai", "model": "gpt-4o", "tools": [{"type": "endCall"}]},
                                  "metadata": {"language": TN}}
        service = VapiService()
        await service.update_assistant("asst_1", company_name="Clinique Yasmine", instructions="Be kind",
                                       faqs=[{"question": "Parking?", "answer": "Yes"}])
        await service.update_assistant("asst_1", voice="ar-TN-HediNeural", voice_provider="azure")
        prompt_update, voice_update = _sent(fake_vapi, "PATCH")
        assert prompt_update["model"]["model"] == "gpt-4o"  # not reset to gpt-4o-mini
        assert prompt_update["model"]["tools"] == [{"type": "endCall"}]
        content = prompt_update["model"]["messages"][0]["content"]
        assert "Tunisian Derja" in content and "said in Tunisian Derja" in content
        assert voice_update["voice"] == {"provider": "azure", "voiceId": "ar-TN-HediNeural"}

    @pytest.mark.asyncio

    async def test_english_updates_are_unchanged(self, fake_vapi):
        fake_vapi["assistant"] = {"model": {"provider": "openai", "model": "gpt-4o-mini"}, "metadata": {}}
        await VapiService().update_assistant("asst_1", company_name="Acme", instructions="Be kind")
        model = _sent(fake_vapi, "PATCH")[0]["model"]
        assert model["model"] == "gpt-4o-mini"
        assert model["messages"][0]["content"].startswith("You are an AI receptionist for Acme.")

    @pytest.mark.asyncio

    async def test_set_language_switches_everything_but_keeps_tools(self, fake_vapi):
        fake_vapi["assistant"] = {"model": {"provider": "openai", "model": "gpt-4o-mini", "temperature": 0.4,
                                            "tools": [{"type": "endCall"}]},
                                  "metadata": {"tenant_id": "t1"}}
        await VapiService().set_language("asst_1", TN, "Clinique Yasmine", "", faqs=[])
        patch = _sent(fake_vapi, "PATCH")[0]
        assert patch["transcriber"]["provider"] == "azure"
        assert patch["model"]["model"] == "gpt-4o" and patch["model"]["temperature"] == 0.4
        assert patch["model"]["tools"] == [{"type": "endCall"}]
        assert patch["voice"]["voiceId"] == "ar-TN-ReemNeural"
        assert patch["metadata"] == {"tenant_id": "t1", "language": TN}
        assert patch["firstMessage"].startswith("عسلامة")


# ===== AssistantService =====

@pytest.fixture
def assistant_service(monkeypatch):
    tenant = {
        "_id": "t1", "name": "Acme", "vapi_assistant_id": "asst_1",
        "ai_config": {"system_prompt": voice_languages.default_instructions("en", "Acme")},
    }
    service = AssistantService(db=MagicMock())
    service.tenant_repo = MagicMock(get_by_id=AsyncMock(return_value=tenant), update=AsyncMock())
    service.get_knowledge_base = AsyncMock(return_value={"documents": [], "faqs": []})
    vapi = MagicMock()
    vapi.set_language = AsyncMock(return_value={
        "voice": {"provider": "azure", "voiceId": "ar-TN-ReemNeural"}, "firstMessage": "عسلامة",
    })
    monkeypatch.setattr("services.assistant_service.vapi_service", vapi)
    return service, tenant, vapi


class TestAssistantServiceLanguage:
    @pytest.mark.asyncio
    async def test_switch_replaces_untouched_instructions(self, assistant_service):
        service, _, vapi = assistant_service
        result = await service.set_language("t1", TN)
        args = vapi.set_language.await_args.args
        assert args[1] == TN and voice_languages.strip_static_date(args[3]) == ""
        saved = service.tenant_repo.update.await_args.args[1]
        assert saved["ai_config.language"] == TN and saved["ai_config.system_prompt"] == ""
        assert saved["ai_config.voice"] == "ar-TN-ReemNeural" and saved["ai_config.voice_provider"] == "azure"
        assert result["success"] and result["first_message"] == "عسلامة"

    @pytest.mark.asyncio

    async def test_switch_keeps_edited_instructions(self, assistant_service):
        service, tenant, _ = assistant_service
        tenant["ai_config"]["system_prompt"] = "We are a dental clinic in Sousse."
        await service.set_language("t1", TN)
        assert service.tenant_repo.update.await_args.args[1]["ai_config.system_prompt"] == "We are a dental clinic in Sousse."

    @pytest.mark.asyncio

    async def test_unknown_language_is_refused(self, assistant_service):
        from fastapi import HTTPException
        service, _, _ = assistant_service
        with pytest.raises(HTTPException) as error:
            await service.set_language("t1", "klingon")
        assert error.value.status_code == 400

    @pytest.mark.asyncio

    async def test_personality_returns_the_instructions_not_the_wrapped_prompt(self, assistant_service, monkeypatch):
        service, tenant, vapi = assistant_service
        tenant["ai_config"]["system_prompt"] = "Closed on Sundays."
        vapi.get_assistant = AsyncMock(return_value={
            "model": {"messages": [{"role": "system", "content": "You are an AI receptionist for Acme... Closed on Sundays. ..."}]},
            "firstMessage": "Hello!",
        })
        settings = await service.get_personality_settings("t1")
        assert settings["system_prompt"] == "Closed on Sundays."


# ===== Prices and the text agent =====

def test_format_price():
    assert format_price(45, "USD") == "$45.00"
    assert format_price(45, None) == "$45.00"
    assert format_price(45, "tnd") == "45 TND"
    assert format_price(45.5, "TND") == "45.5 TND"
    assert format_price(12.25, "EUR") == "12.25 EUR"


class _Cursor:
    def __init__(self, docs):
        self.docs = docs

    async def to_list(self, length=None):
        return self.docs


@pytest.mark.asyncio


async def test_text_agent_speaks_derja_for_tunisian_businesses(monkeypatch):
    db = MagicMock()
    db.tenants.find_one = AsyncMock(return_value={"name": "Clinique Yasmine", "ai_config": {"language": TN}})
    db.business_config.find_one = AsyncMock(return_value={"currency": "TND"})
    db.knowledge_base.find = MagicMock(return_value=_Cursor([]))
    db.services.find = MagicMock(return_value=_Cursor([{"name": "Consultation", "price": 40}]))
    monkeypatch.setattr(text_agent, "get_database", lambda: db)
    agent = text_agent.TextReceptionist()
    agent.appointments._resolve_tenant_timezone = AsyncMock(return_value=pytz.timezone("Africa/Tunis"))

    prompt = await agent._system_prompt("64b000000000000000000001", "whatsapp", "21650000000")
    assert "Consultation (40 TND)" in prompt
    assert "Tunisian Derja" in prompt and "n7eb na3mel rdv" in prompt
