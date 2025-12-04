# 🔧 QUICK FIX - Agent Not Responding

**Your Issue:** Agent connects but doesn't respond  
**Cause:** No agent configuration found in database  
**Time to Fix:** 2 minutes

---

## ✅ THE FIX (Follow These Exact Steps)

### Step 1: Configure Your Agent (2 minutes)

1. **Open Control Center:**
   ```
   http://localhost:3000/dashboard/voice-agent/control-center
   ```

2. **Click "Create Agent" button** (or edit existing agent if you see one)

3. **Fill in the form:**

   **Name:** `My AI Receptionist`

   **System Prompt:** (Copy and paste this)
   ```
   You are a friendly AI receptionist for my business. You help customers with:
   - Scheduling appointments
   - Answering questions about our services
   - Providing business hours information
   
   Be warm, professional, and helpful. Keep responses concise and clear.
   This is a voice conversation, so speak naturally.
   ```

   **LLM Model:** Select `llama-3.3-70b-versatile` (or any Groq model)

   **Voice Provider:** Select `Cartesia` or `ElevenLabs`

   **Voice:** Select any voice from the dropdown

   **Status:** Make sure it's set to `Active` ✅

4. **Click "Save" button**

5. **Wait 3 seconds** for the configuration to save

---

### Step 2: Verify API Key (30 seconds)

1. **Go to API Keys page:**
   ```
   http://localhost:3000/dashboard/settings/api-keys
   ```

2. **Check you see your Groq key:**
   - Provider: Groq
   - Name: (whatever you named it)
   - Key: `gsk_****...` (masked)
   - Status: ✅ Active

3. **If NOT there, add it again:**
   - Click "Add API Key"
   - Provider: Groq
   - Name: `My Groq Key`
   - API Key: Paste your `gsk_...` key
   - Click "Save"

---

### Step 3: Restart Agent Worker (30 seconds)

The agent worker needs to be restarted to pick up new configuration:

1. **Go to the terminal where agent worker is running**
   - You should see logs like: `INFO:livekit.agents:Waiting for jobs...`

2. **Stop it:** Press `Ctrl+C`

3. **Restart it:**
   ```bash
   cd /home/montassar/Desktop/ai_receptionist/livekit-agent-worker
   ./start.sh
   ```

4. **Wait for this message:**
   ```
   INFO:livekit.agents:Worker started
   INFO:livekit.agents:Waiting for jobs...
   ```

---

### Step 4: Test the Call (1 minute)

1. **Open test page:**
   ```
   http://localhost:3000/dashboard/voice-agent/test
   ```

2. **Click "Start LiveKit Call"**

3. **Allow microphone** when browser asks

4. **Wait for "Connected" status** (green indicator)

5. **Speak clearly:** "Hello, can you hear me?"

6. **Expected:** Agent responds within 2-3 seconds! 🎉

---

## 🐛 If Still Not Working

### Check Agent Worker Terminal

Look for these messages in the agent worker terminal:

**✅ GOOD Messages:**
```
INFO:tenant-agent:Initializing agent for tenant: 692f43697c982c08898e127b
INFO:tenant-agent:Using Groq LLM: llama-3.3-70b-versatile
INFO:tenant-agent:Agent session started for tenant 692f43697c982c08898e127b
```

**❌ BAD Messages (and fixes):**

**Error:** `ValueError: Missing tenant_id in room metadata`
- **Fix:** Backend wasn't modified correctly. Run diagnostic:
  ```bash
  cd livekit-agent-worker
  ./diagnose.sh
  ```

**Error:** `Failed to fetch tenant config`
- **Fix:** Go back to Step 1, make sure you clicked "Save"

**Error:** `No LLM API key configured`
- **Fix:** Go back to Step 2, add your Groq API key

**Error:** `Cannot fetch config for tenant`
- **Fix:** Make sure backend is running:
  ```bash
  curl http://localhost:8000/docs
  ```

---

## 🎯 Quick Diagnostic

Run this command to check everything:
```bash
cd /home/montassar/Desktop/ai_receptionist/livekit-agent-worker
./diagnose.sh
```

**Should show:**
- ✅ Backend is running
- ✅ Tenant config found (with your system prompt)
- ✅ Agent worker is running
- ✅ LiveKit server reachable

---

## 📞 Expected Behavior After Fix

1. You click "Start LiveKit Call"
2. Status changes to "Connected" (green)
3. You say: "Hello"
4. Agent responds: "Hello! How can I help you today?"
5. You can have a full conversation!

---

## 🎉 Success Checklist

After following the steps above, you should have:

- [x] Agent configuration saved in Control Center
- [x] Groq API key added and visible in API Keys page
- [x] Agent worker restarted and showing "Waiting for jobs"
- [x] Test call connects and agent responds

**Time:** ~3-4 minutes total

---

## 💡 Pro Tips

1. **Keep agent worker terminal visible** - It shows what's happening
2. **Check browser console** - Press F12, look for errors
3. **Use "Start Call" not "Run Test"** - The LiveKit test page is what works
4. **Speak clearly** - Wait for green "Connected" before speaking
5. **Give it 2-3 seconds** - Agent needs time to process and respond

---

## 🆘 Still Having Issues?

1. **Check all 3 terminals are running:**
   - Terminal 1: Backend (uvicorn)
   - Terminal 2: Frontend (npm run dev)  
   - Terminal 3: Agent worker (./start.sh)

2. **Verify URLs are accessible:**
   ```bash
   curl http://localhost:8000/docs  # Should return HTML
   curl http://localhost:3000       # Should return HTML
   ```

3. **Check MongoDB is running:**
   ```bash
   mongosh --eval "db.version()"
   ```

4. **Run diagnostic again:**
   ```bash
   cd livekit-agent-worker
   ./diagnose.sh
   ```

---

**Let's get your agent working! Follow the 4 steps above.** 🚀
