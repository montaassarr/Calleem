# 🎯 Non-Technical User Guide: API Keys Made Easy

LiveKit voice is now fully managed by the platform. This guide only covers optional BYOK keys for LLM/TTS providers like OpenAI, Groq, Anthropic, ElevenLabs, and Deepgram.

---

## 🤔 What Are These Keys?

Think of them as passwords that let your receptionist talk to AI engines:
- **OpenAI / Groq / Anthropic** – Brain of the assistant
- **ElevenLabs / Deepgram** – Optional TTS/STT providers

Voice transport (LiveKit) is included. No action required there.

---

## 🚀 Quick Start

### Option 1: Do Nothing (Default)
- We supply shared keys so you can use the product immediately.
- Perfect for new users and trials.
- Costs are bundled into your subscription.

### Option 2: Bring Your Own Keys
- Add your own OpenAI/Groq/Anthropic/etc. key.
- Great for teams that already have API credits or need enterprise compliance.
- You’re billed directly by the provider; our platform becomes zero-cost for those calls.

---

## 📝 Add Your Own Key

### Step 1. Generate a Key
- **OpenAI** → https://platform.openai.com → API Keys → “Create new secret key” (`sk-...`)
- **Groq** → https://console.groq.com → API Keys → “Generate new key” (`gsk-...`)
- **Anthropic** → https://console.anthropic.com → “Create API key” (`sk-ant-...`)
- **ElevenLabs** → https://elevenlabs.io → Profile → API Keys (`eleven_...`)
- **Deepgram** → https://console.deepgram.com → API Keys (`dg_...`)

### Step 2. Save It
```bash
curl -X POST http://localhost:8000/api/v1/keys \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "name": "My Primary Key",
    "api_key": "sk-..."
  }'
```
(Or use Dashboard → Settings → API Keys once the UI form ships.)

### Step 3. We Validate Automatically
1. ✅ Ping the provider to confirm the key works
2. ✅ Encrypt it with AES-256-GCM
3. ✅ Mask it in the UI (e.g., `sk-***...xyz`)
4. ✅ Start routing your tenant’s traffic through that key

If validation fails, you’ll see a friendly error explaining what to fix.

---

## 🔄 How Routing Works

```
When tenant calls OpenAI:
  if tenant_key(provider): use tenant key
  else: use platform key
```

Platform keys still exist for convenience, so nothing breaks if you remove your key later.

---

## 📊 Viewing Keys

```bash
curl http://localhost:8000/api/v1/keys \
  -H "Authorization: Bearer $TOKEN"
```

Example:
```json
[
  {
    "id": "key_openai_123",
    "provider": "openai",
    "name": "My Primary Key",
    "masked_key": "sk-***...123",
    "is_valid": true,
    "last_used": "2025-12-02T10:30:00Z"
  }
]
```

---

## 🗑️ Removing a Key

```bash
curl -X DELETE http://localhost:8000/api/v1/keys/key_openai_123 \
  -H "Authorization: Bearer $TOKEN"
```

We immediately fall back to platform keys so calls keep working.

---

## ❓ FAQ

**Q: Do I need a LiveKit key?**  
A: Nope. LiveKit is managed by the platform. All you do is click “Enable voice agent”.

**Q: What happens if my key hits a quota?**  
A: AI Proxy marks it unhealthy and automatically reverts to the platform key, then notifies you to refresh the key.

**Q: Can I mix and match?**  
A: Yes—use your own Groq key but stick with platform OpenAI, etc.

---

That’s it! Add optional keys when you want finer billing control; otherwise enjoy the fully managed LiveKit experience.
