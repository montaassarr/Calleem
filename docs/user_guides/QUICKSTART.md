# 🚀 QUICKSTART: LiveKit-Managed Voice

**New Model**: Platform runs the LiveKit agent + telephony. Tenants optionally add BYOK keys for Groq/OpenAI/Anthropic/ElevenLabs.

---

## 🎯 What Changed

### OLD Model (Before)
- ❌ Tenants had to bring a Vapi/Retell key during onboarding
- ❌ Voice quality & cost depended on third-party accounts
- ❌ Support overhead for validating customer keys

### NEW Model (Now)
- ✅ LiveKit credentials live in platform env vars (single source of truth)
- ✅ Onboarding no longer blocks on tenant voice keys
- ✅ Dashboard issues LiveKit preview tokens instantly
- ✅ Tenants can still BYOK for LLM/TTS if desired

---

## 📁 Key Files

1. `backend/services/livekit_service.py` – token creation + status checks
2. `backend/routers/voice_agent.py` – status/history/toggle/preview APIs
3. `backend/routers/onboarding.py` – LiveKit-only wizard updates
4. `frontend_next/app/dashboard/voice-agent/*` – consumes new status payloads

---

## Smoke Test Flow

```bash
# 1. Check onboarding status (should auto-complete voice step)
curl http://localhost:8000/api/v1/onboarding/status \
  -H "Authorization: Bearer $TOKEN"

# 2. Enable voice agent toggle
curl -X POST http://localhost:8000/api/v1/voice-agent/enable \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'

# 3. Inspect LiveKit health
curl http://localhost:8000/api/v1/voice-agent/status \
  -H "Authorization: Bearer $TOKEN"

# 4. Request preview session (WebRTC)
curl -X POST http://localhost:8000/api/v1/voice-agent/webrtc/test \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Response includes `room_name`, `agent_identity`, and a short-lived token to feed into the LiveKit Prebuilt Agent UI.

---

## 💰 Pricing Model

- Bundle LiveKit minutes inside your SaaS tiers (e.g., 150 minutes on Starter, overages afterward)
- Keep BYOK discounts for advanced tenants who want to supply OpenAI/Groq/Anthropic keys
- Track usage via `platform_key_usage_logs` + LiveKit analytics

---

## 📚 Reference Docs

- `ARCHITECTURE_OVERVIEW.md` – LiveKit-first system design
- `API_TESTING_GUIDE.md` – How to validate LiveKit endpoints
- `USER_API_KEYS_GUIDE.md` – Updated BYOK instructions (LLM/TTS only)

---

**LiveKit is live. Remove the last Vapi references and ship!** 🎉
