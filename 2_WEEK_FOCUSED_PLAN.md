# 🎯 CALLFLOW AI - 2-WEEK FOCUSED FIX PLAN

**Date:** December 3, 2025  
**Deadline:** December 17, 2025 (14 days)  
**Target:** Fix agent isolation & responsiveness - NO EXTRAS

---

## 🔴 CRITICAL PROBLEMS (Must Fix)

### Problem 1: **Shared Agent (Not Isolated)**
- Current: `Parker_165/src/agent.py` is a single shared agent
- Issue: All tenants use the same system prompt, voice, and LLM
- Impact: Tenant A can't customize their agent differently than Tenant B

### Problem 2: **Agent Not Responding**
- Current: Agent connects to LiveKit room but doesn't speak
- Issue: Agent doesn't fetch tenant-specific API keys from `/tenant-config/{tenant_id}`
- Impact: Agent has no API keys to call LLM (Groq/OpenAI)

---

## ✅ WHAT'S ALREADY WORKING (Don't Touch)

| Feature | Status | Location |
|---------|--------|----------|
| **Dashboard UI** | ✅ Working | `frontend_next/app/dashboard/*` |
| **Appointments** | ✅ Working | Backend + N8N workflows |
| **API Keys (BYOK)** | ✅ Working | `/dashboard/settings/api-keys` |
| **Agent CRUD** | ✅ Working | `/dashboard/voice-agent/control-center` |
| **MongoDB Isolation** | ✅ Working | `tenant_id` field in all collections |
| **Authentication** | ✅ Working | JWT with `tenant_id` |
| **Services/Schedule** | ✅ Working | Backend routers + UI pages |

**Dashboard Pages Inventory:**
```
✅ /dashboard - Overview with stats
✅ /dashboard/appointments - List + manage appointments
✅ /dashboard/services - Service catalog
✅ /dashboard/conversations - Call transcripts
✅ /dashboard/voice-agent/control-center - Agent management hub
✅ /dashboard/voice-agent/chat - Text chat with agent
✅ /dashboard/voice-agent/test - WebRTC test page
✅ /dashboard/whatsapp - WhatsApp integration
✅ /dashboard/settings/team - Team members
✅ /dashboard/settings/billing - Subscription
✅ /dashboard/settings/api-keys - BYOK management ✅
✅ /dashboard/settings/business - Business info
✅ /dashboard/settings/ai - AI configuration
✅ /dashboard/help - Help center
```

**Sidebar Navigation:**
```
MENU:
- Dashboard
- Appointments
- Services
- Conversations
- Agents (redirects to control-center)
- Voice AI (expandable)
  - Control Center ✅
  - Voice Chat ✅
  - WebRTC Test ✅
- WhatsApp
- Team

GENERAL:
- Settings (expandable)
  - Settings Hub
  - Business
  - API Keys ✅
  - AI Config
- Help
- Logout
```

---

## 🎯 THE FIX (2 Weeks Only)

### Week 1: Multi-Tenant Agent Worker

**File:** `livekit-agent-worker/tenant_agent.py` (NEW)

```python
import asyncio
import httpx
from livekit.agents import Agent, AgentHandler, JobContext
from livekit.plugins import groq, openai, cartesia, elevenlabs

class TenantAgent(Agent):
    """Multi-tenant agent that fetches config per room"""
    
    @classmethod
    async def initialize(cls, ctx: JobContext):
        # Extract tenant_id from room metadata
        tenant_id = ctx.room.metadata.get("tenant_id")
        if not tenant_id:
            raise ValueError("No tenant_id in room metadata")
        
        # Fetch tenant config from backend
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://localhost:8000/voice-agent/tenant-config/{tenant_id}"
            )
            config = response.json()
        
        # Initialize LLM with tenant's API key
        api_keys = config["api_keys"]
        agent_config = config["agent_config"]
        
        if "groq" in api_keys:
            llm = groq.LLM(
                model=agent_config["llm_model"],
                api_key=api_keys["groq"]
            )
        elif "openai" in api_keys:
            llm = openai.LLM(
                model=agent_config["llm_model"],
                api_key=api_keys["openai"]
            )
        else:
            raise ValueError("No LLM API key found")
        
        # Initialize TTS with tenant's voice
        if agent_config["voice_provider"] == "elevenlabs":
            tts = elevenlabs.TTS(
                voice=agent_config["voice_id"],
                api_key=api_keys.get("elevenlabs")
            )
        else:
            tts = cartesia.TTS(voice=agent_config["voice_id"])
        
        # Create agent instance
        return cls(
            instructions=agent_config["system_prompt"],
            llm=llm,
            tts=tts,
        )

# Register handler
handler = AgentHandler(TenantAgent.initialize)
```

**File:** `livekit-agent-worker/main.py` (NEW)

```python
import logging
from livekit.agents import WorkerOptions, cli
from tenant_agent import handler

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=handler,
            agent_name="multi-tenant-agent"
        )
    )
```

**File:** `livekit-agent-worker/.env` (NEW)

```bash
LIVEKIT_URL=wss://aireceptionist-iqt10ym2.livekit.cloud
LIVEKIT_API_KEY=REDACTED
LIVEKIT_API_SECRET=REDACTED
BACKEND_URL=http://localhost:8000
```

**File:** `livekit-agent-worker/requirements.txt` (NEW)

```
livekit-agents>=0.9.0
livekit-plugins-groq
livekit-plugins-openai
livekit-plugins-cartesia
livekit-plugins-elevenlabs
httpx
python-dotenv
```

---

### Week 1: Update Backend to Pass tenant_id in Room Metadata

**File:** `backend/routers/voice_agent.py`

```python
# MODIFY the /webrtc/test endpoint

@router.post("/webrtc/test")
async def create_webrtc_test_session(
    request: PreviewSessionRequest = None,
    current_user: dict = Depends(get_current_user)
):
    """Create a LiveKit room for web testing"""
    
    tenant_id = str(current_user["tenant_id"])
    room_name = f"test-{tenant_id}-{int(time.time())}"
    
    # Create room with tenant_id in metadata
    room = await livekit_service.create_room(
        room_name=room_name,
        metadata={"tenant_id": tenant_id}  # 🔥 THIS IS THE KEY FIX
    )
    
    # Create token
    token = livekit_service.create_token(
        room_name=room_name,
        identity=f"tenant-{tenant_id}",
        metadata={"tenant_id": tenant_id}
    )
    
    return {
        "room_name": room_name,
        "token": token,
        "livekit_url": livekit_service.livekit_url
    }
```

---

### Week 2: Test & Deploy

**Day 8-10: Testing**

1. **Start the agent worker:**
```bash
cd livekit-agent-worker
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py dev
```

2. **Test with Tenant A:**
- Login as Tenant A
- Go to `/dashboard/settings/api-keys`
- Add Groq API key
- Go to `/dashboard/voice-agent/control-center`
- Update system prompt: "You are a dentist receptionist"
- Go to `/dashboard/voice-agent/test`
- Click "Start Call"
- **Expected:** Agent responds with dentist context

3. **Test with Tenant B:**
- Logout and register new account (Tenant B)
- Add different Groq API key
- Update system prompt: "You are a law firm receptionist"
- Test web call
- **Expected:** Agent responds with law firm context

4. **Verify Isolation:**
- Check that Tenant A and Tenant B have different conversations
- Verify API keys are not shared

**Day 11-14: Production Deployment**

1. **Deploy agent worker to server:**
```bash
# On production server
cd /opt/callflow-agent
git pull
source venv/bin/activate
pip install -r requirements.txt

# Run as systemd service
sudo systemctl start callflow-agent
sudo systemctl enable callflow-agent
```

2. **Update environment variables:**
```bash
# backend/.env
LIVEKIT_URL=wss://aireceptionist-iqt10ym2.livekit.cloud
LIVEKIT_API_KEY=REDACTED
LIVEKIT_API_SECRET=REDACTED
```

3. **Monitor logs:**
```bash
# Agent worker logs
tail -f /var/log/callflow-agent.log

# Backend logs
docker logs -f ai_receptionist-backend-1
```

---

## 📦 WHAT WE'RE NOT BUILDING (Save for Later)

❌ Real-time transcript UI (use existing `/dashboard/conversations`)  
❌ Call analytics dashboard (use existing stats endpoints)  
❌ Phone number integration (use existing Twilio/LiveKit)  
❌ Advanced voice studio (use existing `/dashboard/voice-agent/control-center`)  
❌ Onboarding wizard (use existing `/dashboard/onboarding`)  
❌ Team collaboration features (already have `/dashboard/settings/team`)  

**Why Skip These?**
- They're nice-to-have, not critical
- Your current UI already handles these
- Focus = Fix agent isolation in 2 weeks

---

## 🎯 SUCCESS METRICS

After 2 weeks, you should be able to:

1. ✅ **Tenant A** creates agent with "Dentist receptionist" prompt
2. ✅ **Tenant B** creates agent with "Law firm receptionist" prompt
3. ✅ Both agents respond correctly with their context
4. ✅ API keys are isolated (Tenant A can't see Tenant B's keys)
5. ✅ Web testing works (`/dashboard/voice-agent/test`)
6. ✅ Conversations are isolated per tenant

---

## 📂 FILES TO CREATE/MODIFY

### NEW FILES (Week 1):
```
livekit-agent-worker/
├── main.py                 # Agent entry point
├── tenant_agent.py         # Multi-tenant agent class
├── requirements.txt        # Python dependencies
├── .env                    # Agent worker config
└── README.md              # Setup instructions
```

### MODIFY (Week 1):
```
backend/routers/voice_agent.py
  → Add tenant_id to room metadata in /webrtc/test endpoint
```

### NO CHANGES NEEDED:
```
✅ frontend_next/app/dashboard/**  (Already good)
✅ backend/routers/agents.py       (Already good)
✅ backend/routers/api_keys.py     (Already good)
✅ backend/models/**               (Already good)
✅ frontend_next/components/**     (Already good)
```

---

## 🚀 FINAL CHECKLIST

**Week 1:**
- [ ] Create `livekit-agent-worker/` directory
- [ ] Write `tenant_agent.py` with config fetching
- [ ] Write `main.py` with worker setup
- [ ] Add `requirements.txt`
- [ ] Modify `backend/routers/voice_agent.py` to pass `tenant_id` in room metadata
- [ ] Test locally with 1 tenant

**Week 2:**
- [ ] Test with 2 different tenants
- [ ] Verify API key isolation
- [ ] Verify prompt isolation
- [ ] Deploy agent worker to production
- [ ] Monitor logs for errors
- [ ] Document setup in README

---

## 🎉 DONE!

After 2 weeks:
- ✅ Each tenant has isolated agent
- ✅ Agents respond correctly
- ✅ Everything else keeps working

**No fancy UI needed. No complex refactoring. Just fix the core issue.**

---

## 📞 EMERGENCY CONTACT

If something breaks:
1. Check agent worker logs: `tail -f /var/log/callflow-agent.log`
2. Check backend logs: `docker logs -f ai_receptionist-backend-1`
3. Verify LiveKit connection: `curl -X POST https://aireceptionist-iqt10ym2.livekit.cloud`
4. Check MongoDB: `docker exec -it ai_receptionist-mongo-1 mongosh`

**The most common issue will be:** Agent worker can't reach backend → Check `BACKEND_URL` in agent worker `.env`
