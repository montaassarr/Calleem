# 🚀 QUICKSTART: LiveKit Voice Platform

**New Model**: Voice runs on LiveKit managed by the platform. Tenants optionally BYOK their LLM/TTS keys.

---

## 🎯 What Changed

### Before
- ❌ Tenants had to paste Vapi keys before doing anything
- ❌ Support had to debug 3rd-party accounts
- ❌ Billing was unpredictable

### Now
- ✅ LiveKit env vars ship with the backend (no tenant key required)
- ✅ Onboarding auto-enables voice agent toggle
- ✅ Dashboard fetches preview tokens directly from `/voice-agent/webrtc/test`
- ✅ BYOK applies only to OpenAI/Groq/Anthropic/ElevenLabs

---

## 📁 Important Files

1. `backend/services/livekit_service.py`
2. `backend/routers/voice_agent.py`
3. `backend/routers/onboarding.py`
4. `frontend_next/app/dashboard/voice-agent/*`

---

## 🧪 Smoke Test

```bash
# 1. Check onboarding status
curl http://localhost:8000/api/v1/onboarding/status \
  -H "Authorization: Bearer $TOKEN"

# 2. Enable voice agent
curl -X POST http://localhost:8000/api/v1/voice-agent/enable \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'

# 3. Issue LiveKit preview
curl -X POST http://localhost:8000/api/v1/voice-agent/webrtc/test \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Use the returned token + room in the LiveKit prebuilt agent UI.

---

## 💰 Pricing Snapshot

| Plan | Included Minutes | Notes |
| --- | --- | --- |
| Starter $49 | 150 | LiveKit minutes bundled |
| Pro $149 | 800 | Priority queue |
| Enterprise | Custom | Dedicated queue + BYOK discounts |

---

## 📚 Reference Docs

- `docs/architecture/ARCHITECTURE_OVERVIEW.md`
- `docs/api_docs/API_TESTING_GUIDE.md`
- `docs/user_guides/USER_API_KEYS_GUIDE.md`

---

**Ship it!** 🎉
