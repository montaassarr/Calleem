# 🚨 Critical Fix Needed: API Keys Missing

## Problem

The agent worker is **failing to initialize** because **no LLM API key is configured**.

**Error in logs**:
```
ValueError: No LLM API key configured for this tenant
```

## Impact

- ❌ Voice agent cannot start
- ❌ Cannot make voice calls
- ❌ Cannot book appointments via voice

## Solution

### Quick Fix (5 minutes)

1. **Get a Groq API key** (free tier available):
   - Go to: https://console.groq.com/
   - Sign up / Login
   - Create API key
   - Copy the key

2. **Add the key**:
   ```bash
   python3 add_api_key.py --provider groq --key YOUR_GROQ_API_KEY
   ```

3. **Verify**:
   ```bash
   python3 add_api_key.py --list
   ```

4. **Test**:
   - Go to: http://localhost:3000/dashboard/voice-agent/test
   - Click "Start Test Call"
   - Should work now!

## Required Keys

Based on your configuration:
- ✅ **Groq** (for LLM: `llama-3.3-70b-versatile`)
- ✅ **Cartesia** (for voice: `cartesia`)

## Current Status

✅ Backend: Working  
✅ Frontend: Working  
✅ Agent Worker: Running but failing (needs API keys)  
❌ Voice Agent: Cannot initialize (missing API keys)  

## After Adding Keys

The agent worker will automatically:
1. Detect the new API keys
2. Initialize successfully
3. Start handling voice calls

**No restart needed** - the agent worker will pick up new keys on the next call attempt.

## Help

See `API_KEY_SETUP_GUIDE.md` for detailed instructions.

