# LiveKit Multi-Tenant Agent Setup Guide

## 🎯 Goal
Run self-hosted LiveKit agents that support multiple tenants, each with their own API keys and configuration.

## ✅ What You Already Have

Your backend already supports:
- ✅ Encrypted API key storage per tenant (`backend/routers/api_keys.py`)
- ✅ Tenant isolation in database
- ✅ Agent configuration per tenant
- ✅ LiveKit room creation with tenant metadata
- ✅ NEW: `/voice-agent/tenant-config/{tenant_id}` endpoint

## 🔧 What You Need to Build

### 1. Modify Your LiveKit Agent (Parker_165 or create new)

The agent needs to:
1. Read `tenant_id` from room metadata when a user connects
2. Call your backend API: `http://your-backend:8000/api/v1/voice-agent/tenant-config/{tenant_id}`
3. Use the returned API keys for that specific call
4. Use tenant-specific system prompts and voice settings

### 2. Example Agent Flow

```python
# In your LiveKit agent (Parker_165/src/agent.py)

import httpx
from livekit.agents import JobContext

BACKEND_URL = "http://localhost:8000/api/v1"

async def get_tenant_config(tenant_id: str):
    """Fetch tenant configuration from backend"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/voice-agent/tenant-config/{tenant_id}")
        return response.json()

@server.rtc_session(agent_name="multi_tenant_agent")
async def entrypoint(ctx: JobContext):
    # Get tenant_id from room metadata
    tenant_id = ctx.room.metadata.get("tenant_id")
    
    if not tenant_id:
        logger.error("No tenant_id in room metadata!")
        return
    
    # Fetch tenant config
    config = await get_tenant_config(tenant_id)
    api_keys = config["api_keys"]
    agent_config = config["agent_config"]
    
    # Create session with tenant's keys
    session = AgentSession(
        stt=inference.STT(model="assemblyai/universal-streaming", language="en"),
        llm=inference.LLM(
            model=agent_config["llm_model"],
            api_key=api_keys.get("groq") or api_keys.get("openai")
        ),
        tts=inference.TTS(
            model=f"{agent_config['voice_provider']}/sonic-3",
            voice=agent_config["voice_id"],
            api_key=api_keys.get("elevenlabs") if agent_config["voice_provider"] == "elevenlabs" else None
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )
    
    # Create agent with tenant's prompt
    agent = DefaultAgent(instructions=agent_config["system_prompt"])
    
    await session.start(agent=agent, room=ctx.room)
```

## 📋 Setup Steps

### Step 1: Test the New Endpoint

```bash
# Get your tenant_id from a logged-in session
TENANT_ID="your_tenant_id_here"

# Test the endpoint
curl http://localhost:8000/api/v1/voice-agent/tenant-config/$TENANT_ID
```

You should see:
```json
{
  "tenant_id": "...",
  "api_keys": {
    "groq": "gsk_...",
    "openai": "sk-...",
    "elevenlabs": "sk_..."
  },
  "agent_config": {
    "system_prompt": "You are...",
    "llm_model": "groq/llama-3.3-70b-versatile",
    "voice_id": "...",
    "voice_provider": "cartesia"
  }
}
```

### Step 2: Each Tenant Adds Their API Keys

Tenants must add their API keys via your dashboard:
1. Go to: `http://localhost:3000/dashboard/settings/api-keys`
2. Add Groq API key (for LLM)
3. Add ElevenLabs API key (optional, for custom voices)
4. Add OpenAI API key (optional, alternative to Groq)

### Step 3: Configure Their Agent

Each tenant configures their agent in the dashboard:
1. Go to: `http://localhost:3000/dashboard/voice-agent/control-center`
2. Create/edit their agent
3. Set system prompt (personality)
4. Choose LLM model
5. Choose voice settings

### Step 4: Deploy Your Modified LiveKit Agent

```bash
# Option A: Docker Compose (recommended for production)
cd Parker_165
docker build -t your-livekit-agent .
docker run -e BACKEND_URL=http://your-backend:8000 your-livekit-agent

# Option B: Local development
cd Parker_165
uv sync
export BACKEND_URL=http://localhost:8000
uv run python src/agent.py dev
```

## 🔒 Security Considerations

1. **Endpoint Security**: The `/tenant-config/{tenant_id}` endpoint should be:
   - Restricted to internal network only, OR
   - Protected with an API key that only your LiveKit agents know

2. **Add Authentication** (Recommended):
```python
# In backend/routers/voice_agent.py
AGENT_API_KEY = os.getenv("LIVEKIT_AGENT_API_KEY", "secret_key_here")

@router.get("/tenant-config/{tenant_id}")
async def get_tenant_agent_config(
    tenant_id: str,
    api_key: str = Header(None, alias="X-Agent-API-Key")
):
    if api_key != AGENT_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid agent API key")
    # ... rest of the code
```

## 🚀 Testing Multi-Tenancy

1. **Create 2 test tenants**:
   - Tenant A: Add Groq key A
   - Tenant B: Add Groq key B

2. **Start voice calls from each tenant's dashboard**
   - Verify Tenant A's call uses Groq key A
   - Verify Tenant B's call uses Groq key B

3. **Check logs** to ensure proper isolation

## 📊 Current vs Future State

### Current State (Not Working):
```
User → LiveKit Cloud → Shared Agent (no API keys) → ❌ No Response
```

### Future State (Multi-Tenant):
```
Tenant A → LiveKit Room (metadata: tenant_id=A) 
         → Your Agent → Backend API → Get Tenant A's keys 
         → Groq/OpenAI with Tenant A's key 
         → ✅ Response using Tenant A's config

Tenant B → LiveKit Room (metadata: tenant_id=B)
         → Your Agent → Backend API → Get Tenant B's keys
         → Groq/OpenAI with Tenant B's key
         → ✅ Response using Tenant B's config
```

## 🆘 Why Agent Not Responding Now

Your agent isn't responding because:
1. ❌ Parker_165 folder was deleted
2. ❌ No agent running to handle LiveKit rooms
3. ❌ LiveKit Cloud's hosted agents don't have access to your backend's tenant API keys

**Solution**: Run your own LiveKit agent worker that calls your backend for tenant configs!

## 📚 Resources

- LiveKit Agents SDK: https://docs.livekit.io/agents/
- Your API Keys Router: `backend/routers/api_keys.py`
- Your Voice Agent Router: `backend/routers/voice_agent.py`
- Frontend API Keys Page: `frontend_next/app/dashboard/settings/api-keys/page.tsx`
