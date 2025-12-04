# LIVEKIT-FIRST ARCHITECTURE

**Updated**: December 2, 2025  
**Model**: The platform operates the LiveKit agent + telephony, tenants optionally supply LLM/TTS keys.

---

## 💡 Core Business Model

### Your Platform Provides
- 🎙️ **Managed LiveKit Agent** – Parker_165 prebuilt agent + SIP queue
- 🔧 **n8n Automation Pack** – appointment lifecycle, reminders, owner alerts
- 📝 **Prompt + Intent Library** – optimized conversations stored in Mongo
- 📊 **Analytics Dashboard** – call stats, transcripts, customer journeys
- 🔌 **Integrations** – Calendar, WhatsApp, CRM webhooks
- 🤖 **Shared AI Keys** – Groq/OpenAI/Anthropic/ElevenLabs fallback

### Tenants Bring (Optional)
- ⚙️ Their own LLM/TTS keys if they want direct billing
- 📅 Business data (services, hours, staff)

### Revenue Model
- SaaS subscription ($49–$199/mo) covering LiveKit minutes + tooling
- Optional overages for high call volumes

---

## 🏗️ Updated Architecture

1. **Onboarding Wizard** enables LiveKit by default and skips any Vapi steps.
2. **LiveKit Service** issues WebRTC tokens, manages queues, monitors health.
3. **AI Proxy** still routes Groq/OpenAI/etc. keys via BYOK → platform fallback.
4. **n8n Workflows** remain the decisioning brain for appointments, CRM, WhatsApp.

```
Tenant Browser → Next.js Dashboard → FastAPI →
  ├─ LiveKit Service (preview tokens, status)
  ├─ AI Proxy (LLM/TTS BYOK)
  └─ n8n Workflows (business logic)
```

---

## 🔑 API Key Strategy (New)

### Tier 1: Platform-Managed Voice
```python
VOICE_PROVIDER = "livekit"
STRATEGY = "Centralized credentials in env vars"
REASON = "Quality control & simpler onboarding"
```

### Tier 2: Optional BYOK Providers
```python
PROVIDERS = ["openai", "groq", "anthropic", "elevenlabs", "deepgram"]
STRATEGY = "Use tenant key if present → fallback to platform key"
```

### Tier 3: Platform Only Infra
```python
PROVIDERS = ["twilio", "n8n", "mongodb"]
```

---

## 📊 Economics Example (Managed Voice)

| Item | Amount |
|---|---|
| LiveKit minutes (150 min @ $0.011) | $1.65 |
| Groq tokens | $0.30 |
| WhatsApp + infra | $5.00 |
| **Total Cost** | **$6.95** |
| SaaS Plan | $79.00 |
| **Profit** | **$72.05** |

Tenants no longer need to open a Vapi account — voice costs are bundled into your pricing.

---

## 🚀 Files of Interest

1. `services/livekit_service.py` – token issuance & readiness checks
2. `routers/voice_agent.py` – status/history/preview endpoints
3. `routers/onboarding.py` – LiveKit-only onboarding flow
4. `services/ai_proxy.py` – BYOK routing for non-voice providers

---

**Conclusion**: LiveKit gives you full control over call quality while AI Proxy keeps providers flexible. No Vapi dependency remains in code or onboarding.
