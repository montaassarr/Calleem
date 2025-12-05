# Quick Fix Summary - Tenant Config Issue

## ✅ Fixes Applied

### 1. Docker Agent Worker Backend URL
**Problem**: Agent worker in Docker was trying to connect to `localhost:8000` which doesn't work inside containers.

**Fix**: Added `BACKEND_URL: http://core-service:8000` to `docker-compose.yml` for the agent worker.

### 2. Auto-Create business_config
**Problem**: `business_config` collection might not exist for your tenant, causing 404 errors.

**Fix**: Updated `/api/v1/voice-agent/tenant-config/{tenant_id}` endpoint to auto-create `business_config` if missing.

### 3. Better Error Handling
- Added ObjectId import for tenant lookup
- Added fallback tenant lookup methods
- Better logging for debugging

## 🚨 Critical Issue: Duplicate Agent Workers

**You're running the agent worker TWICE:**
1. In Docker (via `start.sh`)
2. Separately (via `cd livekit-agent-worker && ./start.sh`)

**This causes conflicts!** Choose ONE:

### Option A: Docker Only (Recommended)
```bash
# Stop separate agent worker
pkill -f "tenant_agent.py dev"

# Restart Docker
./start.sh

# Check logs
docker compose logs -f parker_agent
```

### Option B: Separate Only
```bash
# Stop Docker agent worker
docker compose stop parker_agent

# Run separately
cd livekit-agent-worker
./start.sh
```

## 🔧 Quick Fix Steps

1. **Stop duplicate agent worker:**
   ```bash
   # Find and kill separate process
   pkill -f "tenant_agent.py dev"
   ```

2. **Restart Docker services:**
   ```bash
   ./start.sh
   ```

3. **Check if business_config exists:**
   ```bash
   python3 debug_tenant_config.py
   ```

4. **Test the endpoint:**
   ```bash
   # Get your tenant_id from the debug script output
   curl http://localhost:8000/api/v1/voice-agent/tenant-config/YOUR_TENANT_ID
   ```

5. **Test voice agent:**
   - Go to: http://localhost:3000/dashboard/voice-agent/test
   - Click "Start Test Call"
   - Check browser console and agent logs

## 📊 Expected Behavior

### Before Fix:
```
ERROR: Failed to fetch tenant config: 404
ValueError: Cannot fetch config for tenant <tenant_id>
```

### After Fix:
```
INFO: Initializing agent for tenant: <tenant_id>
INFO: Fetched config for tenant <tenant_id>: ['tenant_id', 'api_keys', ...]
INFO: Using Groq LLM: llama-3.3-70b-versatile
INFO: Agent session started for tenant <tenant_id>
```

## 🔍 Debugging

### Check Backend Logs:
```bash
docker compose logs -f core-service | grep tenant-config
```

### Check Agent Worker Logs:
```bash
# Docker:
docker compose logs -f parker_agent

# Separate:
tail -f livekit-agent-worker/agent.log
```

### Check Frontend:
- Open browser console (F12)
- Look for errors in Network tab
- Check `/api/connection-details` response

## 📝 Files Changed

1. `docker-compose.yml` - Added BACKEND_URL for agent worker
2. `backend/routers/voice_agent.py` - Auto-create business_config
3. `debug_tenant_config.py` - Diagnostic script (new)
4. `fix_tenant_config.sh` - Fix script (new)

## ✅ Next Steps

1. **Stop duplicate agent worker**
2. **Restart Docker services**
3. **Test voice agent in browser**
4. **Check logs for success messages**

The fixes are in place. The main issue is running the agent worker twice - choose one method and stick with it!


