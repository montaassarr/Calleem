# 🔑 API KEY ARCHITECTURE — LIVEKIT + BYOK

The platform now follows a **two-tier key strategy**: tenants can still bring their own LLM/TTS keys, while LiveKit voice credentials are centrally managed for predictable operations.

```
┌─────────────────────────────────────────────────────────────┐
│                      AI PROXY SERVICE                        │
│                  (Routing & Accounting)                      │
│                                                             │
│  ┌────────────────────┐        ┌──────────────────────────┐ │
│  │ 1. Tenant BYOK     │ -----> │ 2. Platform Vault        │ │
│  │    (Groq/OpenAI/   │        │    (Fallback + LiveKit)  │ │
│  │     Anthropic/     │        │                          │ │
│  │     ElevenLabs)    │        │                          │ │
│  └────────────────────┘        └──────────────────────────┘ │
│                                                             │
│  Usage tracking • Health checks • Cost attribution          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏗️ IMPLEMENTED COMPONENTS

### 1. Platform API Keys (`backend/models/core/platform_api_keys.py`)
- Supports providers: `openai`, `anthropic`, `groq`, `elevenlabs`, `deepgram`, etc.
- AES-256-GCM encrypted secrets with masking helpers.
- Health + quota metadata so operations can disable bad keys without touching tenant data.

### 2. AI Proxy (`backend/services/ai_proxy.py`)
- Single entry point for provider calls.
- Chooses tenant BYOK first, else falls back to platform key pool.
- Logs usage so billing dashboards can estimate spend vs. revenue.
- No longer exposes any legacy voice helpers; voice now flows through LiveKit service instead.

### 3. LiveKit Service (`backend/services/livekit_service.py`)
- Reads `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`, plus `LIVEKIT_AGENT_NAME`/queue.
- Generates scoped access tokens, preview rooms, and readiness payloads for `/voice-agent/*` routes.
- Centralized so tenants never handle LiveKit secrets directly.

### 4. Platform Keys Router (`backend/routers/platform_keys.py`)
- Admin-only CRUD for non-voice providers.
- Usage summary endpoints still work; LiveKit costs are tracked via infrastructure metrics instead of BYOK entries.

### 5. Business Configs (`backend/models/business/business_config.py`)
- The old voice key field has been removed.
- Feature flags (e.g., `features_enabled.voice_agent`) now gate LiveKit access per tenant.

---

## 🚀 HOW OPERATORS USE IT

1. **Add shared keys (Super Admin)**
    ```bash
    curl -X POST http://localhost:8000/api/v1/platform-keys \
      -H "Authorization: Bearer $ADMIN_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "provider": "openai",
        "name": "Prod Groq 70B",
        "api_key": "gsk_...",
        "tier": "standard",
        "max_requests_per_minute": 60,
        "max_tokens_per_day": 1000000
      }'
    ```
    Repeat for Groq/Anthropic/ElevenLabs, etc. LiveKit credentials stay in env vars rather than the BYOK tables.

2. **Tenant onboarding**
    - When the tenant creates an agent, the AI proxy automatically injects platform keys for LLM + TTS.
    - Voice-specific metadata (`livekit_agent_name`, `livekit_queue`) lives on the `Agent` document instead of the old provider IDs.

3. **Tenant BYOK (Optional)**
    ```bash
    curl -X POST http://localhost:8000/api/v1/keys \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "provider": "openai",
        "name": "My Prod Key",
        "api_key": "sk-..."
      }'
    ```
    The proxy prefers BYOK for cost savings but seamlessly falls back to platform keys when missing.

4. **Voice agent preview**
    - Dashboard hits `/voice-agent/webrtc/test` → backend calls `livekit_service.build_preview_session()`.
    - Response includes `token`, `room_name`, `agent_identity` for the prebuilt agent package.

5. **Monitoring**
    - `/voice-agent/status` reports LiveKit heartbeat + env config state.
    - `/admin/analytics/livekit` (new) summarizes readiness per environment.
    - Platform key usage APIs keep covering LLM/TTS spend; LiveKit usage is handled via LiveKit’s own analytics.

---

## 🔐 SECURITY & OPERATIONS

- **Encryption**: BYOK + platform keys continue to use AES-256-GCM with rotation via `MASTER_KEY`.
- **RBAC**: Tenants only see their keys; only super admins can touch platform key endpoints.
- **Validation**: Provider validators exist for OpenAI/ElevenLabs/Groq/etc. LiveKit validation happens at startup; failures mark the service as `configured: false` in `/voice-agent/status`.
- **Health checks**: Platform keys store `last_health_check`, `failure_count`, etc. LiveKit health is tracked by pinging the server and verifying token issuance.

---

## 🧭 MIGRATION NOTES

1. Remove any lingering legacy voice key fields from `business_config` documents (migration script already executed in code, but double-check old tenants).
2. Delete the obsolete voice webhook/service/settings modules if they still exist in a stale checkout.
3. Update docs and onboarding flows so tenants are pointed to LiveKit preview sessions instead of the Vapi dashboard.
4. Ensure environment variables include:
    ```env
    LIVEKIT_URL=
    LIVEKIT_API_KEY=
    REDACTED
    LIVEKIT_AGENT_NAME=Parker165
    LIVEKIT_AGENT_QUEUE=default
    ```
5. Platform BYOK docs should highlight that only VLM/LLM/TTS providers are user-configurable; LiveKit remains managed by the platform for quality control.

---

## 📈 REPORTING & BILLING

- `platform_key_usage_logs` continues to power tenant invoices for text/audio model usage.
- LiveKit minutes are aggregated via LiveKit’s REST API + internal `voice_calls` collection (status, duration, transcript links, recording URLs).
- Admin dashboards reference the same collections; nothing relies on old Vapi IDs anymore.

---

## ✅ CHECKLIST

- [x] No source file imports the deprecated voice service module.
- [x] Voice agent endpoints only expose LiveKit data.
- [x] BYOK UI/screens document OpenAI/Groq/Anthropic/ElevenLabs only.
- [x] Docs/tests/scripts updated to remove the legacy provider terminology.

LiveKit is now the single voice transport, while AI Proxy keeps BYOK flexible for everything else.
