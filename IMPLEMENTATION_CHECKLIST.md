# ✅ 2-WEEK IMPLEMENTATION CHECKLIST

**Start Date:** December 3, 2025  
**End Date:** December 17, 2025  
**Goal:** Fix agent isolation & responsiveness

---

## 📅 WEEK 1: BUILD MULTI-TENANT AGENT WORKER

### Day 1-2: Setup Agent Worker Project

- [ ] Create directory: `livekit-agent-worker/`
- [ ] Create `requirements.txt`:
  ```
  livekit-agents>=0.9.0
  livekit-plugins-groq
  livekit-plugins-openai
  livekit-plugins-cartesia
  livekit-plugins-elevenlabs
  httpx
  python-dotenv
  ```
- [ ] Create `.env`:
  ```bash
  LIVEKIT_URL=wss://aireceptionist-iqt10ym2.livekit.cloud
  LIVEKIT_API_KEY=REDACTED
  LIVEKIT_API_SECRET=REDACTED
  BACKEND_URL=http://localhost:8000
  ```
- [ ] Install dependencies:
  ```bash
  cd livekit-agent-worker
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  pip install -r requirements.txt
  ```

---

### Day 3-4: Write Agent Code

- [ ] Create `tenant_agent.py`:
  ```python
  import asyncio
  import httpx
  from livekit.agents import Agent, AgentHandler, JobContext
  from livekit.plugins import groq, openai, cartesia, elevenlabs
  
  class TenantAgent(Agent):
      @classmethod
      async def initialize(cls, ctx: JobContext):
          # Get tenant_id from room metadata
          tenant_id = ctx.room.metadata.get("tenant_id")
          if not tenant_id:
              raise ValueError("No tenant_id in room metadata")
          
          # Fetch config from backend
          async with httpx.AsyncClient() as client:
              response = await client.get(
                  f"http://localhost:8000/voice-agent/tenant-config/{tenant_id}"
              )
              config = response.json()
          
          api_keys = config["api_keys"]
          agent_config = config["agent_config"]
          
          # Initialize LLM
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
              raise ValueError("No LLM API key")
          
          # Initialize TTS
          if agent_config["voice_provider"] == "elevenlabs":
              tts = elevenlabs.TTS(
                  voice=agent_config["voice_id"],
                  api_key=api_keys.get("elevenlabs")
              )
          else:
              tts = cartesia.TTS(voice=agent_config["voice_id"])
          
          return cls(
              instructions=agent_config["system_prompt"],
              llm=llm,
              tts=tts,
          )
  
  handler = AgentHandler(TenantAgent.initialize)
  ```

- [ ] Create `main.py`:
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

---

### Day 5: Modify Backend

- [ ] Open `backend/routers/voice_agent.py`
- [ ] Find the `@router.post("/webrtc/test")` endpoint
- [ ] Modify to add `tenant_id` to room metadata:
  ```python
  @router.post("/webrtc/test")
  async def create_webrtc_test_session(
      request: PreviewSessionRequest = None,
      current_user: dict = Depends(get_current_user)
  ):
      tenant_id = str(current_user["tenant_id"])
      room_name = f"test-{tenant_id}-{int(time.time())}"
      
      # Create room with tenant_id in metadata
      room = await livekit_service.create_room(
          room_name=room_name,
          metadata={"tenant_id": tenant_id}  # 🔥 ADD THIS
      )
      
      # Create token
      token = livekit_service.create_token(
          room_name=room_name,
          identity=f"tenant-{tenant_id}",
          metadata={"tenant_id": tenant_id}  # 🔥 ADD THIS
      )
      
      return {
          "room_name": room_name,
          "token": token,
          "livekit_url": livekit_service.livekit_url
      }
  ```

- [ ] Restart backend:
  ```bash
  docker-compose restart backend
  ```

---

### Day 6-7: Local Testing

- [ ] Start backend:
  ```bash
  docker-compose up -d
  ```

- [ ] Start agent worker:
  ```bash
  cd livekit-agent-worker
  source venv/bin/activate
  python main.py dev
  ```

- [ ] Open browser: `http://localhost:3000`

- [ ] **Test Tenant A:**
  - [ ] Login as existing user
  - [ ] Go to `/dashboard/settings/api-keys`
  - [ ] Add Groq API key: `gsk_...`
  - [ ] Go to `/dashboard/voice-agent/control-center`
  - [ ] Update system prompt: "You are a dentist receptionist at Dr. Smith's office."
  - [ ] Go to `/dashboard/voice-agent/test`
  - [ ] Click "Start Call"
  - [ ] Speak: "Do you have appointments tomorrow?"
  - [ ] **Expected:** Agent responds with dentist context

- [ ] **Test Tenant B:**
  - [ ] Logout
  - [ ] Register new account (different email)
  - [ ] Go to `/dashboard/settings/api-keys`
  - [ ] Add different Groq API key
  - [ ] Update system prompt: "You are a receptionist at Johnson & Associates law firm."
  - [ ] Go to `/dashboard/voice-agent/test`
  - [ ] Click "Start Call"
  - [ ] Speak: "Do you handle divorce cases?"
  - [ ] **Expected:** Agent responds with law firm context

- [ ] **Verify Isolation:**
  - [ ] Check that Tenant A can't see Tenant B's API keys
  - [ ] Check that Tenant A's agent uses different prompt than Tenant B
  - [ ] Check conversation history is isolated

---

## 📅 WEEK 2: PRODUCTION DEPLOYMENT

### Day 8-9: Fix Any Bugs from Testing

- [ ] Check agent worker logs:
  ```bash
  # Look for errors
  tail -f livekit-agent-worker/logs/agent.log
  ```

- [ ] Check backend logs:
  ```bash
  docker logs -f ai_receptionist-backend-1
  ```

- [ ] Common issues to fix:
  - [ ] Agent can't reach backend → Check `BACKEND_URL` in `.env`
  - [ ] API keys not decrypting → Check `MASTER_KEY` in backend `.env`
  - [ ] Agent not responding → Check LiveKit credentials
  - [ ] Wrong tenant config → Verify `tenant_id` in room metadata

---

### Day 10-11: Production Setup

- [ ] **Server Setup:**
  ```bash
  # SSH to production server
  ssh user@your-server.com
  
  # Create directory
  cd /opt
  sudo mkdir callflow-agent
  sudo chown $USER:$USER callflow-agent
  cd callflow-agent
  
  # Clone code (or copy files)
  # Copy livekit-agent-worker/ folder
  
  # Install dependencies
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

- [ ] **Create systemd service:**
  ```bash
  sudo nano /etc/systemd/system/callflow-agent.service
  ```
  
  Paste:
  ```ini
  [Unit]
  Description=CallFlow AI Multi-Tenant Agent Worker
  After=network.target
  
  [Service]
  Type=simple
  User=your-username
  WorkingDirectory=/opt/callflow-agent
  Environment="PATH=/opt/callflow-agent/venv/bin"
  ExecStart=/opt/callflow-agent/venv/bin/python main.py start
  Restart=always
  RestartSec=10
  
  [Install]
  WantedBy=multi-user.target
  ```

- [ ] **Start service:**
  ```bash
  sudo systemctl daemon-reload
  sudo systemctl start callflow-agent
  sudo systemctl enable callflow-agent
  sudo systemctl status callflow-agent
  ```

---

### Day 12-13: Production Testing

- [ ] **Test from production frontend:**
  - [ ] Login to production site
  - [ ] Add API keys
  - [ ] Update system prompt
  - [ ] Test web call
  - [ ] Verify agent responds correctly

- [ ] **Monitor logs:**
  ```bash
  # Agent worker logs
  sudo journalctl -u callflow-agent -f
  
  # Backend logs
  docker logs -f ai_receptionist-backend-1
  ```

- [ ] **Test with 3 different tenants:**
  - [ ] Dentist
  - [ ] Lawyer
  - [ ] Gym
  - [ ] Verify each has isolated config

---

### Day 14: Documentation & Handoff

- [ ] **Create README in `livekit-agent-worker/`:**
  ```markdown
  # CallFlow AI - Multi-Tenant Agent Worker
  
  ## Setup
  1. Install dependencies: `pip install -r requirements.txt`
  2. Copy `.env.example` to `.env`
  3. Update LiveKit credentials
  4. Run: `python main.py dev` (development) or `python main.py start` (production)
  
  ## Environment Variables
  - `LIVEKIT_URL`: LiveKit server URL
  - `LIVEKIT_API_KEY`: LiveKit API key
  - `LIVEKIT_API_SECRET`: LiveKit API secret
  - `BACKEND_URL`: Backend API URL
  
  ## How It Works
  1. User creates LiveKit room with `tenant_id` in metadata
  2. Agent worker receives job request
  3. Agent extracts `tenant_id` from room metadata
  4. Agent calls `/tenant-config/{tenant_id}` to get config
  5. Agent initializes LLM/TTS with tenant's API keys
  6. Agent responds with tenant's system prompt
  ```

- [ ] **Update main README:**
  - [ ] Add section on agent worker setup
  - [ ] Document environment variables
  - [ ] Add troubleshooting guide

- [ ] **Final checks:**
  - [ ] All tests passing ✅
  - [ ] Agent responds correctly ✅
  - [ ] Tenant isolation working ✅
  - [ ] Logs are clean ✅
  - [ ] Documentation complete ✅

---

## 🎉 DONE!

After 14 days:
- ✅ Multi-tenant agent worker deployed
- ✅ Each tenant has isolated agent
- ✅ Agents respond correctly with their prompts
- ✅ API keys are isolated
- ✅ Everything tested and documented

---

## 🚨 EMERGENCY CONTACTS

**If something breaks:**

1. **Agent not responding:**
   ```bash
   # Check agent worker status
   sudo systemctl status callflow-agent
   
   # Check logs
   sudo journalctl -u callflow-agent -n 100
   ```

2. **Backend errors:**
   ```bash
   # Check backend logs
   docker logs -f ai_receptionist-backend-1
   ```

3. **LiveKit connection issues:**
   ```bash
   # Test LiveKit connection
   curl -X POST https://aireceptionist-iqt10ym2.livekit.cloud
   ```

4. **Database issues:**
   ```bash
   # Check MongoDB
   docker exec -it ai_receptionist-mongo-1 mongosh
   > use callflow_ai_saas
   > db.business_config.find().limit(1)
   ```

**Common Fixes:**
- Agent can't reach backend → Check `BACKEND_URL` in agent worker `.env`
- API keys not decrypting → Check `MASTER_KEY` in backend `.env`
- Room metadata missing → Check `voice_agent.py` modification
- Worker not starting → Check Python version (needs 3.10+)

---

## 📊 PROGRESS TRACKER

**Week 1:**
- [ ] Day 1-2: Project setup
- [ ] Day 3-4: Write agent code
- [ ] Day 5: Modify backend
- [ ] Day 6-7: Local testing

**Week 2:**
- [ ] Day 8-9: Bug fixes
- [ ] Day 10-11: Production setup
- [ ] Day 12-13: Production testing
- [ ] Day 14: Documentation

**Status:** 0/14 days complete
