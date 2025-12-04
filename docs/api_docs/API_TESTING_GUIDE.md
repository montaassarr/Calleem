# 🧪 API Testing Guide: LiveKit Voice + BYOK Stack

**Purpose**: Verify the multi-tenant platform now that LiveKit fully replaced Vapi.

---

## 🚀 Quick Start

### 1. Start the Server
```bash
cd /home/montassar/Desktop/ai_receptionist/backend

# Generate encryption key
export MASTER_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')

# Start server
uvicorn main:app --reload --port 8000
```

### 2. Smoke Test
```bash
curl http://localhost:8000/
```

**Expected Response**
```json
{
  "message": "🤖 AI Receptionist API is running!",
  "version": "1.0.0"
}
```

---

## 📝 Test Scenarios

### Scenario 1: Tenant With Platform-Managed LiveKit

1. **Create a tenant user**
    ```bash
    curl -X POST http://localhost:8000/api/v1/users/register \
      -H "Content-Type: application/json" \
      -d '{
        "email": "test@example.com",
        "password": "Test123!",
        "business_name": "Test Barber Shop"
      }'
    ```
2. **Login and capture the JWT**
    ```bash
    export TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/users/login \
      -H "Content-Type: application/json" \
      -d '{"username":"test@example.com","password":"Test123!"}' | jq -r '.access_token')
    ```
3. **Check BYOK keys (expect empty array)**
    ```bash
    curl http://localhost:8000/api/v1/setup/my-keys \
      -H "Authorization: Bearer $TOKEN"
    ```
    The response should mention that the platform will supply Groq/OpenAI/LiveKit keys automatically.
4. **Check LiveKit readiness**
    ```bash
    curl http://localhost:8000/api/v1/voice-agent/status \
      -H "Authorization: Bearer $TOKEN"
    ```
    Expect `livekit_status` to be `ready`, `voice_agent_enabled` defaults to `false` until toggled.
5. **Create a preview WebRTC session**
    ```bash
    curl -X POST http://localhost:8000/api/v1/voice-agent/webrtc/test \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{}'
    ```
    Response includes `room_name`, `agent_identity`, and a short-lived LiveKit token that the dashboard can feed into the Prebuilt Agent UI.

### Scenario 2: Tenant Toggles Voice Agent

1. **Enable voice agent**
    ```bash
    curl -X POST http://localhost:8000/api/v1/voice-agent/enable \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"enabled": true}'
    ```
    Expect `{ "voice_agent": true }` in the payload.
2. **Verify status again** – the `/status` endpoint now reports `voice_agent_enabled: true` while LiveKit health remains unchanged.
3. **List historical calls** (empty on fresh tenants)
    ```bash
    curl http://localhost:8000/api/v1/voice-agent/history \
      -H "Authorization: Bearer $TOKEN"
    ```
4. **Attempt PSTN call** – `/voice-agent/call` returns `501` because outbound telephony is paused until LiveKit SIP trunks land. The error keeps clients from invoking the old Vapi dialer.

### Scenario 3: AI Providers (LLM + TTS)

LiveKit handles transport, while LLM/TTS keys can still be BYOK. Reuse the `/keys` router to test encryption/masking, e.g. add an OpenAI key and ensure masked output is returned. No LiveKit key management is exposed to tenants.

---

## 🔐 Platform Admin Checks

Use a super-admin JWT for these calls.

1. **Global analytics**
    ```bash
    curl http://localhost:8000/api/v1/admin/analytics/global \
      -H "Authorization: Bearer $ADMIN_TOKEN"
    ```
    Confirms tenant/user counts still render without the Vapi aggregation tables.
2. **Infrastructure health**
    ```bash
    curl http://localhost:8000/api/v1/admin/analytics/livekit \
      -H "Authorization: Bearer $ADMIN_TOKEN"
    ```
    (Endpoint returns LiveKit heartbeat, queue depth, and configured agent name.)
3. **Business config inspection** – the legacy voice key field is gone. Sensitive fields list now contains Groq/OpenAI/ElevenLabs/Twilio only.

---

## 🐛 Error Testing

- **LiveKit disabled**: turn off the feature flag and call `/voice-agent/webrtc/test`. Expect `403` instructing the user to enable the agent again.
- **Missing platform config**: unset `LIVEKIT_URL` or `LIVEKIT_API_KEY` before launching the server and hit `/voice-agent/status`. The endpoint should surface `configured: false` so ops can detect env drift.
- **Expired preview token**: request a preview, wait 15 minutes, and try to join with the stale token – LiveKit will reject it, and the dashboard should request a fresh session.

---

## ✅ Expected Outcomes

- No endpoint references Vapi.
- LiveKit preview sessions can be issued per-tenant without manual key entry.
- Platform BYOK router continues to manage non-voice providers only.
