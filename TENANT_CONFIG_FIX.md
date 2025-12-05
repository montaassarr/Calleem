# Tenant Configuration Fix

## Problem
The agent worker is getting "Tenant configuration not found" when trying to fetch tenant config.

## Root Causes

1. **Docker Backend URL Issue**: Agent worker in Docker was using `http://localhost:8000` which doesn't work inside Docker containers. Fixed to use `http://core-service:8000`.

2. **Missing business_config**: The `business_config` collection might not exist for your tenant. The backend now auto-creates it if missing.

3. **Duplicate Agent Workers**: You're running the agent worker both in Docker AND separately, which can cause conflicts.

## Fixes Applied

### 1. Docker Agent Worker Backend URL
- **File**: `docker-compose.yml`
- **Change**: Added `BACKEND_URL: http://core-service:8000` to agent worker environment
- **Why**: Docker containers need to use service names, not localhost

### 2. Auto-Create business_config
- **File**: `backend/routers/voice_agent.py`
- **Change**: Endpoint now auto-creates `business_config` if it doesn't exist
- **Why**: Ensures tenant config is always available

### 3. Better Error Handling
- Added ObjectId import
- Added fallback tenant lookup
- Better logging

## How to Fix Your Setup

### Option 1: Use Docker Only (Recommended)

1. **Stop the separately running agent worker:**
   ```bash
   # Find and kill the process
   pkill -f "tenant_agent.py dev"
   ```

2. **Restart Docker services:**
   ```bash
   ./start.sh
   ```

3. **Check agent worker logs:**
   ```bash
   docker compose logs -f parker_agent
   ```

### Option 2: Use Separate Agent Worker Only

1. **Stop Docker agent worker:**
   ```bash
   docker compose stop parker_agent
   ```

2. **Ensure backend URL is correct in `.env`:**
   ```bash
   cd livekit-agent-worker
   # Check .env has: BACKEND_URL=http://localhost:8000
   ```

3. **Run agent worker separately:**
   ```bash
   cd livekit-agent-worker
   ./start.sh
   ```

### Option 3: Fix Missing business_config

Run the diagnostic script:
```bash
python3 debug_tenant_config.py
```

Or use the fix script:
```bash
./fix_tenant_config.sh
```

## Testing

1. **Check backend is accessible:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Get your tenant_id:**
   - Login to frontend
   - Open browser console
   - Check localStorage or network requests for tenant_id

3. **Test tenant config endpoint:**
   ```bash
   # Replace YOUR_TENANT_ID with actual tenant_id
   curl http://localhost:8000/api/v1/voice-agent/tenant-config/YOUR_TENANT_ID
   ```

4. **Check agent worker logs:**
   ```bash
   # If using Docker:
   docker compose logs -f parker_agent
   
   # If running separately:
   tail -f livekit-agent-worker/agent.log
   ```

## Expected Logs

### Successful Connection:
```
INFO:tenant-agent:Initializing agent for tenant: <tenant_id>
INFO:tenant-agent:Fetched config for tenant <tenant_id>: ['tenant_id', 'api_keys', 'business_name', ...]
INFO:tenant-agent:Using Groq LLM: llama-3.3-70b-versatile
INFO:tenant-agent:Using Cartesia TTS: <voice_id>
INFO:tenant-agent:Agent session started for tenant <tenant_id> in room <room_name>
```

### Error (Before Fix):
```
ERROR:tenant-agent:Failed to fetch tenant config: 404
ERROR:tenant-agent:Error fetching tenant config: 404 Client Error: Not Found
ValueError: Cannot fetch config for tenant <tenant_id>
```

## Next Steps

1. **Choose one agent worker setup** (Docker OR separate, not both)
2. **Restart services** with the fix
3. **Test voice agent** in the web interface
4. **Check logs** to verify tenant config is being fetched

## Important Notes

- **Don't run agent worker in both Docker and separately** - this causes conflicts
- **Docker agent worker** must use `http://core-service:8000` (service name)
- **Separate agent worker** must use `http://localhost:8000` (host machine)
- **business_config** is now auto-created if missing


