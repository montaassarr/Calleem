# 🧪 TESTING GUIDE - Multi-Tenant Agent Worker

**Date:** December 3, 2025  
**Goal:** Verify agent isolation and responsiveness with 2 tenants

---

## ✅ Pre-Test Checklist

Before testing, ensure:

- [ ] Backend is running: `docker-compose up -d`
- [ ] Frontend is running: `cd frontend_next && npm run dev`
- [ ] MongoDB is accessible: `docker ps | grep mongo`
- [ ] You have 2 different email accounts for testing
- [ ] You have a Groq API key (get free at https://console.groq.com)

---

## 🚀 Step 1: Start the Agent Worker

```bash
cd livekit-agent-worker
./start.sh
```

**Expected Output:**
```
🚀 CallFlow AI - Multi-Tenant Agent Worker Setup
================================================

✅ Python version: 3.11.x
✅ Virtual environment created
✅ Dependencies installed
✅ Environment file found
✅ Backend is running at http://localhost:8000

🎙️  Starting CallFlow AI Agent Worker...
   Press Ctrl+C to stop

INFO:callflow-worker:Starting CallFlow AI Multi-Tenant Agent Worker
INFO:livekit.agents:Worker started
INFO:livekit.agents:Waiting for jobs...
```

**Leave this terminal running!** Open a new terminal for the next steps.

---

## 🧪 Step 2: Test Tenant A (Dentist)

### 2.1 Register Account

1. Open browser: `http://localhost:3000`
2. Click "Register"
3. Fill in:
   - Email: `dentist@test.com`
   - Password: `test123456`
   - Business Name: `Dr. Smith's Dental Office`
4. Click "Register"
5. Login with the same credentials

### 2.2 Add API Keys

1. Go to: `http://localhost:3000/dashboard/settings/api-keys`
2. Click "Add API Key"
3. Select Provider: **Groq**
4. Name: `My Groq Key`
5. API Key: Paste your Groq API key (starts with `gsk_...`)
6. Click "Save"
7. Verify you see green checkmark: ✅

**Screenshot:** You should see the key listed with masked value like `gsk_****...`

### 2.3 Configure Agent

1. Go to: `http://localhost:3000/dashboard/voice-agent/control-center`
2. Click on your agent (or create one if none exists)
3. Update System Prompt:
   ```
   You are Sarah, the friendly receptionist at Dr. Smith's Dental Office. 
   We specialize in general dentistry, cleanings, and cosmetic procedures.
   Be warm, professional, and help patients schedule appointments.
   Our office hours are Monday-Friday 9 AM to 5 PM.
   ```
4. Select LLM Model: `llama-3.3-70b-versatile` (or any Groq model)
5. Select Voice: Choose any voice you like
6. Click "Save"

### 2.4 Test Web Call

1. Go to: `http://localhost:3000/dashboard/voice-agent/test`
2. Click "Start Call" or "Connect"
3. Allow microphone access when prompted
4. Wait for agent to connect (you'll see "Connected" status)
5. **Speak:** "Hi, do you have any appointments available tomorrow?"

**Expected Response:**
- Agent should respond in character as "Sarah" from the dental office
- Should mention Dr. Smith's Dental Office
- Should ask follow-up questions about appointment times
- Voice should be clear and responsive

**Check Agent Worker Terminal:**
```
INFO:tenant-agent:Initializing agent for tenant: <tenant_id>
INFO:tenant-agent:Using Groq LLM: llama-3.3-70b-versatile
INFO:tenant-agent:Using Cartesia TTS: <voice_id>
INFO:tenant-agent:Agent session started for tenant <tenant_id>
```

### 2.5 Verify Function Calling

Still in the call, test the appointment booking tool:

**You:** "I'd like to schedule an appointment for next Tuesday at 2 PM"

**Expected:**
- Agent should ask for your name, phone, and email
- Agent should confirm the appointment details
- Agent should say something like: "Perfect! I've scheduled your appointment..."

**Check Backend Logs:**
```bash
# In a new terminal
docker logs -f ai_receptionist-backend-1 | grep appointment
```

You should see POST requests to `/appointments/` endpoint.

### 2.6 End Call

Click "End Call" or "Disconnect"

---

## 🧪 Step 3: Test Tenant B (Lawyer)

### 3.1 Logout and Register New Account

1. Click your profile → "Logout"
2. Click "Register"
3. Fill in:
   - Email: `lawyer@test.com`
   - Password: `test123456`
   - Business Name: `Johnson & Associates Law Firm`
4. Click "Register"
5. Login

### 3.2 Add Different API Keys

1. Go to: `http://localhost:3000/dashboard/settings/api-keys`
2. Click "Add API Key"
3. Select Provider: **Groq**
4. Name: `Law Firm Groq Key`
5. API Key: Paste a **DIFFERENT** Groq API key (or same one for testing)
6. Click "Save"

**Important:** Even if you use the same key, the system will store it separately per tenant.

### 3.3 Configure Different Agent

1. Go to: `http://localhost:3000/dashboard/voice-agent/control-center`
2. Click on your agent
3. Update System Prompt:
   ```
   You are Michael, the professional receptionist at Johnson & Associates Law Firm.
   We specialize in family law, divorce cases, and estate planning.
   Be professional, empathetic, and help clients schedule consultations.
   Our office hours are Monday-Friday 9 AM to 6 PM.
   ```
4. Select LLM Model: `llama-3.3-70b-versatile`
5. Select Voice: Choose a **DIFFERENT** voice than Tenant A
6. Click "Save"

### 3.4 Test Web Call

1. Go to: `http://localhost:3000/dashboard/voice-agent/test`
2. Click "Start Call"
3. Allow microphone access
4. Wait for connection
5. **Speak:** "Hi, do you handle divorce cases?"

**Expected Response:**
- Agent should respond as "Michael" from the law firm
- Should mention Johnson & Associates
- Should talk about family law and divorce cases
- Should NOT mention dentistry or Dr. Smith
- Voice should be different from Tenant A

**Check Agent Worker Terminal:**
```
INFO:tenant-agent:Initializing agent for tenant: <different_tenant_id>
INFO:tenant-agent:Using Groq LLM: llama-3.3-70b-versatile
INFO:tenant-agent:Agent initialized for tenant <tenant_id> (Johnson & Associates Law Firm)
```

### 3.5 Test Function Calling

**You:** "I'd like to schedule a consultation for next Wednesday at 3 PM"

**Expected:**
- Agent should collect your information
- Should confirm the appointment
- Should NOT mention dental appointments

### 3.6 End Call

Click "End Call"

---

## ✅ Step 4: Verify Isolation

### 4.1 Check API Keys Are Isolated

1. Login as Tenant A (dentist@test.com)
2. Go to: `/dashboard/settings/api-keys`
3. You should see ONLY your Groq key
4. Logout

5. Login as Tenant B (lawyer@test.com)
6. Go to: `/dashboard/settings/api-keys`
7. You should see ONLY your Groq key (different from Tenant A)

**✅ PASS:** API keys are isolated per tenant

### 4.2 Check Conversations Are Isolated

1. Login as Tenant A
2. Go to: `/dashboard/conversations`
3. You should see ONLY conversations from dental office calls
4. Logout

5. Login as Tenant B
6. Go to: `/dashboard/conversations`
7. You should see ONLY conversations from law firm calls

**✅ PASS:** Conversations are isolated per tenant

### 4.3 Check Agent Configs Are Different

1. Login as Tenant A
2. Go to: `/dashboard/voice-agent/control-center`
3. Note the system prompt (should be about dentistry)
4. Logout

5. Login as Tenant B
6. Go to: `/dashboard/voice-agent/control-center`
7. Note the system prompt (should be about law firm)

**✅ PASS:** Agent configurations are isolated

---

## 🎉 Success Criteria

You've successfully implemented multi-tenant agent isolation if:

- [x] **Tenant A agent responds with dental context**
- [x] **Tenant B agent responds with law firm context**
- [x] **API keys are not shared between tenants**
- [x] **Conversations are isolated per tenant**
- [x] **Agents use different voices**
- [x] **Function tools work for both tenants**
- [x] **Agent worker logs show different tenant_ids**

---

## 🐛 Troubleshooting

### Agent Not Responding

**Symptom:** Agent connects but doesn't speak

**Check:**
```bash
# Agent worker logs
cd livekit-agent-worker
tail -f logs/agent.log  # If logs directory exists

# Or check terminal output
```

**Common Issues:**
- ❌ No API key: "No LLM API key configured"
  - **Fix:** Add Groq key at `/dashboard/settings/api-keys`
- ❌ Can't fetch config: "Failed to fetch tenant config"
  - **Fix:** Check `BACKEND_URL` in agent worker `.env`
- ❌ No tenant_id: "No tenant_id in room metadata"
  - **Fix:** Verify backend modification was applied

### Backend Errors

**Check Backend Logs:**
```bash
docker logs -f ai_receptionist-backend-1
```

**Common Issues:**
- ❌ `404 Not Found` on `/tenant-config/{tenant_id}`
  - **Fix:** Restart backend: `docker-compose restart backend`
- ❌ Decryption error
  - **Fix:** Check `MASTER_KEY` in `backend/.env`

### LiveKit Connection Issues

**Check:**
```bash
curl -X POST https://aireceptionist-iqt10ym2.livekit.cloud
```

**Expected:** Should return JSON (not error)

**Fix:** Verify `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` in both:
- `backend/.env`
- `livekit-agent-worker/.env`

### Agent Worker Won't Start

**Error:** `ModuleNotFoundError: No module named 'livekit'`

**Fix:**
```bash
cd livekit-agent-worker
source venv/bin/activate
pip install -r requirements.txt
```

**Error:** `ValueError: Missing tenant_id in room metadata`

**Fix:** Backend didn't create room with metadata. Check the backend modification was applied.

---

## 📊 Expected Test Results

| Test | Tenant A (Dentist) | Tenant B (Lawyer) | Isolated? |
|------|-------------------|-------------------|-----------|
| System Prompt | "Dr. Smith's Dental Office" | "Johnson & Associates" | ✅ Yes |
| Voice | Voice A | Voice B (different) | ✅ Yes |
| API Key | Key A | Key B | ✅ Yes |
| Conversations | Dental calls only | Law calls only | ✅ Yes |
| Function Tools | Works | Works | ✅ Yes |

---

## 📝 Test Report Template

After testing, fill out:

```
Date: ___________
Tester: ___________

Tenant A (Dentist):
- Agent responded: [ ] Yes [ ] No
- Correct context: [ ] Yes [ ] No
- Function tools worked: [ ] Yes [ ] No

Tenant B (Lawyer):
- Agent responded: [ ] Yes [ ] No
- Correct context: [ ] Yes [ ] No
- Function tools worked: [ ] Yes [ ] No

Isolation:
- API keys isolated: [ ] Yes [ ] No
- Conversations isolated: [ ] Yes [ ] No
- Configs isolated: [ ] Yes [ ] No

Overall Status: [ ] PASS [ ] FAIL

Issues Found:
___________________________________________
___________________________________________
```

---

## 🎯 Next Steps After Successful Testing

Once all tests pass:

1. ✅ Mark Phase 1 complete in `IMPLEMENTATION_CHECKLIST.md`
2. 📝 Document any issues in a separate file
3. 🚀 Move to Phase 2: Production deployment
4. 📧 Test with real phone numbers (optional)
5. 🎉 Celebrate! You fixed the critical bugs!

**Time to complete:** ~2-3 hours for thorough testing
