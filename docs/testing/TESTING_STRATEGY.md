# 🧪 Testing Strategy - LiveKit Managed Voice

**Updated**: December 2, 2025  
**Architecture**: Platform-managed LiveKit voice, tenant BYOK for LLM/TTS  
**Pre-Deployment**: AWS Learner Lab

---

## 📋 Table of Contents

1. [Testing Overview](#testing-overview)
2. [Phase 1: Backend API & Tenant Isolation](#phase-1-backend-api--tenant-isolation)
3. [Phase 2: LiveKit Service + Voice Agent](#phase-2-livekit-service--voice-agent)
4. [Phase 3: End-to-End Workflows](#phase-3-end-to-end-workflows)
5. [Phase 4: AWS Deployment Readiness](#phase-4-aws-deployment-readiness)
6. [Test Data Setup](#test-data-setup)
7. [Success Criteria](#success-criteria)

---

## 🎯 Testing Overview

### Objectives
- ✅ Validate backend API functionality
- ✅ Ensure **tenant isolation** for all Mongo collections
- ✅ Verify LiveKit status + preview token generation
- ✅ Confirm onboarding wizard enables LiveKit without requiring tenant voice keys
- ✅ Exercise AI proxy BYOK flow for Groq/OpenAI/Anthropic/ElevenLabs
- ✅ Prove n8n automation hooks still execute after LiveKit refactor

### Architecture Under Test
```
Managed Voice Stack:
├── LiveKit Service → issues access tokens + monitors queue health
├── AI Proxy → BYOK-first routing for LLM/TTS providers
└── n8n Workflows → Business automations (appointments, CRM, WhatsApp)
```

### Test Environment
- **Backend**: FastAPI (`localhost:8000`)
- **Database**: MongoDB (`localhost:27017`)
- **Auth**: JWT tokens (tenant scoped)
- **LiveKit**: Cloud project configured via env vars
- **Tenants**: 2 sample tenants for isolation tests

---

## 📊 Phase 1: Backend API & Tenant Isolation

**Priority**: 🔴 CRITICAL  
**Duration**: 2-3 hours

### 1.1 Authentication & Authorization
- `tests/integration/test_auth.py`
- Register/login two tenants, confirm JWT payload includes tenant_id
- Validate 401s for missing/invalid tokens

### 1.2 Tenant Isolation
- `tests/integration/test_tenant_isolation.py`
- Create API keys, agents, appointments for Tenant A/B and ensure cross-tenant reads fail

### 1.3 API Key Management (BYOK)
- `tests/integration/test_api_keys.py`
- Add/remove OpenAI/Groq/ElevenLabs keys
- Ensure masking + encryption fields persist

### 1.4 AI Proxy
- `tests/integration/test_ai_proxy.py`
- REQUIRED providers now include only non-voice critical keys (e.g., `openai` when tenant marks conversation AI as BYOK-only)
- OPTIONAL providers fallback to platform keys when tenant key absent
- PLATFORM providers (Twilio, n8n credentials) always use platform secrets

### 1.5 Onboarding Wizard
- `tests/integration/test_onboarding.py`
- New flow auto-completes voice step (LiveKit managed)
- Ensure LiveKit toggle can still be disabled and reenrolled
- Confirm onboarding prevents access to `/voice-agent` routes when required metadata missing

---

## 📞 Phase 2: LiveKit Service + Voice Agent

**Priority**: 🟡 HIGH  
**Duration**: 2 hours

### 2.1 LiveKit Status Endpoint
- `tests/integration/test_livekit_status.py` (new)
- Validate `/voice-agent/status` returns:
  - `configured: true/false`
  - `livekit_url`
  - `agent_name`, `queue`
  - `voice_agent_enabled` flag per tenant

### 2.2 Preview Session
- `tests/integration/test_livekit_preview.py` (new)
- POST `/voice-agent/webrtc/test`
- Expect `token`, `room_name`, `agent_identity`
- TTL defaults to 900 seconds; verify manual overrides rejected unless admin

### 2.3 Feature Toggle
- `tests/integration/test_voice_agent_toggle.py`
- Call `/voice-agent/enable` with `{ "enabled": true }`
- Confirm Mongo `features_enabled.voice_agent` updates and audit log appended

### 2.4 History + Stats
- `tests/integration/test_voice_history.py`
- Seed `voice_calls` collection
- Ensure `/voice-agent/history` and `/voice-agent/stats` return per-tenant summaries without exposing recordings from other tenants

### 2.5 Failure Modes
- Remove `LIVEKIT_API_KEY` → `/voice-agent/status` should report `configured: false`
- Call preview endpoint while disabled → expect `403`

---

## 🔁 Phase 3: End-to-End Workflows

**Priority**: 🟢 MEDIUM  
**Duration**: 2 hours

1. **Appointment lifecycle**
    - Trigger `tests/e2e/test_complete_onboarding_flow.py`
    - Validate n8n webhook events fire using LiveKit transcripts (call import job)
2. **Multi-tenant isolation**
    - `tests/e2e/test_multi_tenant_isolation.py` ensures n8n workflow IDs remain tenant-specific
3. **Admin analytics**
    - `/admin/analytics/livekit` endpoint should aggregate voice readiness + queue stats
4. **Dashboard smoke**
    - Run `frontend_next` Playwright specs focusing on `voice-agent/*` routes to ensure UI now expects `livekit_status` objects instead of Vapi metadata

---

## ☁️ Phase 4: AWS Deployment Readiness

1. **Environment validation**
    - Confirm ECS task definitions include `LIVEKIT_*` variables
    - Run smoke tests against staging URL
2. **Secrets rotation**
    - Store LiveKit keys in AWS Secrets Manager or SSM Parameter Store
    - Update CI pipelines to inject them during deploy
3. **Observability**
    - CloudWatch metrics for preview-token issuance failures
    - Alert when `configured=false` for more than 5 minutes

---

## 🧪 Test Data Setup

```bash
# Seed demo tenant
python scripts/testing/setup_test_env.sh --tenant demo

# Load sample appointments & conversations
python backend/tests/fixtures/load_sample_data.py
```

Ensure LiveKit env vars are present locally:
```bash
export LIVEKIT_URL=...
export LIVEKIT_API_KEY=...
export LIVEKIT_API_SECRET=...
```

---

## ✅ Success Criteria

- All Phase 1 + Phase 2 integration tests pass locally and in CI
- LiveKit preview sessions can be created for multiple tenants simultaneously
- Tenant onboarding never requires manual voice-provider API keys
- n8n automations continue to execute after LiveKit call imports
- Documentation/tests/scripts contain zero references to Vapi or Retell
