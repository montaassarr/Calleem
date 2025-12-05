# Frontend-Backend Connection Fix

## Problem
Frontend API route `/api/connection-details` was failing with "Failed to connect to backend: fetch failed"

## Root Cause
1. **URL Construction Issue**: The `NEXT_PUBLIC_API_URL` in Docker includes `/api/v1`, but the code was appending it again
2. **Error Handling**: Generic error messages made debugging difficult
3. **Timeout**: No timeout on fetch calls, causing indefinite hangs

## Fix Applied

### 1. Fixed URL Construction
The API route now handles both cases:
- If `NEXT_PUBLIC_API_URL` already includes `/api/v1` → use as-is
- If not → append `/api/v1`

### 2. Added Better Error Handling
- Specific error messages for different failure types:
  - Timeout errors
  - Connection refused
  - DNS resolution failures
- Added 10-second timeout to prevent indefinite hangs

### 3. Added Logging
- Logs the exact endpoint being called
- Logs the base URL from environment
- Better error details for debugging

## How to Apply the Fix

### Option 1: Restart Frontend Container (Quick)
```bash
docker compose restart frontend
```

### Option 2: Rebuild Frontend (If restart doesn't work)
```bash
docker compose up -d --build frontend
```

### Option 3: Full Restart
```bash
docker compose down
docker compose up -d
```

## Verification

After restarting, test the connection:

1. **Check frontend logs**:
   ```bash
   docker compose logs -f frontend
   ```

2. **Test in browser**:
   - Go to: http://localhost:3000/dashboard/voice-agent/test
   - Click "Start Test Call"
   - Check browser console and frontend logs for any errors

3. **Expected logs**:
   ```
   Calling backend: http://core-service:8000/api/v1/voice-agent/webrtc/test
   Base URL from env: http://core-service:8000/api/v1
   Backend response: { ... }
   ```

## Network Configuration

The Docker setup uses:
- **Frontend**: `NEXT_PUBLIC_API_URL=http://core-service:8000/api/v1`
- **Backend**: Accessible at `http://core-service:8000` within Docker network
- **Network**: Both containers on `ai-receptionist-network`

## Troubleshooting

### If still getting "fetch failed":

1. **Check network connectivity**:
   ```bash
   docker exec ai-receptionist-frontend ping -c 1 core-service
   ```
   Should return: `64 bytes from 172.x.x.x`

2. **Check backend is running**:
   ```bash
   docker compose ps core-service
   ```
   Should show: `Up (healthy)`

3. **Check frontend logs**:
   ```bash
   docker compose logs frontend | grep -E "error|Error|fetch|backend"
   ```

4. **Verify environment variable**:
   ```bash
   docker exec ai-receptionist-frontend printenv | grep NEXT_PUBLIC_API_URL
   ```
   Should show: `NEXT_PUBLIC_API_URL=http://core-service:8000/api/v1`

### If getting timeout:

- Backend might be slow to respond
- Check backend logs: `docker compose logs core-service`
- Increase timeout in code (currently 10 seconds)

### If getting "Connection refused":

- Backend might not be running
- Check: `docker compose ps`
- Start backend: `docker compose up -d core-service`

## Code Changes

**File**: `frontend_next/app/api/connection-details/route.ts`

**Changes**:
1. Smart URL construction that handles `/api/v1` in env var
2. Added 10-second timeout with AbortController
3. Better error messages with specific failure types
4. Added logging for debugging

## Next Steps

1. Restart the frontend container
2. Test the voice agent in the browser
3. Check logs if issues persist
4. Your tenant_id is: `693160c13a149b6ff88b18b0` (save this!)

