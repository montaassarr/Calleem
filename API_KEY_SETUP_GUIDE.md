# API Key Setup Guide

## ⚠️ Critical Issue Found

The agent worker is failing with:
```
ValueError: No LLM API key configured for this tenant
```

**This means you need to add API keys before the voice agent can work!**

## Quick Fix

### Option 1: Using the Script (Recommended)

```bash
# Add Groq API key (for LLM)
python3 add_api_key.py --provider groq --key YOUR_GROQ_API_KEY

# Add Cartesia API key (for voice)
python3 add_api_key.py --provider cartesia --key YOUR_CARTESIA_API_KEY

# List all keys
python3 add_api_key.py --list
```

### Option 2: Using the Dashboard

1. Go to: http://localhost:3000/dashboard/settings/ai
2. Scroll to "API Keys" section
3. Click "Add API Key"
4. Select provider (e.g., "groq")
5. Enter your API key
6. Click "Add"

### Option 3: Using API Directly

```bash
# Login first
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/users/login \
  -d "username=montamsallem@gmail.com&password=Mariemmontassar03$" \
  | jq -r '.access_token')

# Add Groq key
curl -X POST http://localhost:8000/api/v1/keys \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "groq",
    "api_key": "YOUR_GROQ_API_KEY",
    "name": "Groq API Key"
  }'
```

## Required API Keys

### For Voice Agent to Work:

1. **LLM Provider** (choose one):
   - **Groq** (recommended - fast and cheap)
   - OpenAI
   - Anthropic

2. **Voice Provider** (choose one):
   - **Cartesia** (recommended - high quality)
   - ElevenLabs
   - Deepgram

### Current Configuration

From your test results:
- **LLM Model**: `llama-3.3-70b-versatile` (requires Groq)
- **Voice Provider**: `cartesia` (requires Cartesia API key)
- **Voice ID**: `79a125e8-cd45-4c13-8a67-188112f4dd22`

## Get API Keys

### Groq API Key
1. Go to: https://console.groq.com/
2. Sign up / Login
3. Go to API Keys section
4. Create a new API key
5. Copy the key (starts with `gsk_...`)

### Cartesia API Key
1. Go to: https://cartesia.ai/
2. Sign up / Login
3. Go to API Keys section
4. Create a new API key
5. Copy the key

## Verify Setup

After adding keys, verify:

```bash
# List keys
python3 add_api_key.py --list

# Test voice agent
# Go to: http://localhost:3000/dashboard/voice-agent/test
# Click "Start Test Call"
```

## Check Agent Logs

After adding keys, check if agent worker can now initialize:

```bash
docker compose logs -f parker_agent | grep -E "LLM|API key|initialized"
```

You should see:
```
✅ Using Groq LLM: llama-3.3-70b-versatile
✅ Using Cartesia voice
✅ Agent initialized successfully
```

## Troubleshooting

### "Invalid API key"
- Check that the key is correct
- Make sure there are no extra spaces
- Verify the key is active in the provider's dashboard

### "No LLM API key found" (still)
- Make sure you added the key for the correct provider
- Check that the key is in `api_keys` array in business_config
- Verify tenant_id matches: `693160c13a149b6ff88b18b0`

### Agent still failing
1. Restart agent worker: `docker compose restart parker_agent`
2. Check logs: `docker compose logs -f parker_agent`
3. Verify config: `python3 test_tenant_config.py`

## Next Steps

Once API keys are added:

1. ✅ Restart agent worker (if needed)
2. ✅ Test voice agent in browser
3. ✅ Make a test call
4. ✅ Try booking an appointment via voice

## Your Tenant ID

**Save this for reference**: `693160c13a149b6ff88b18b0`

