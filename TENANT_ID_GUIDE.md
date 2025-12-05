# How to Get Your Tenant ID

## Quick Method

Run this script (it will login and extract your tenant_id):

```bash
./get_tenant_id.sh
```

Or directly:

```bash
python3 test_tenant_config.py
```

## Manual Method

### 1. Login via Browser

1. Open: http://localhost:3000/login
2. Login with: `montamsallem@gmail.com` / `Mariemmontassar03$`
3. Open browser console (F12)
4. Go to Application/Storage → Local Storage
5. Look for `access_token`
6. Copy the token

### 2. Decode JWT Token

The JWT token contains your `tenant_id`. You can decode it at:
- https://jwt.io
- Or use the Python script: `python3 test_tenant_config.py`

### 3. Test Endpoint Directly

Once you have your tenant_id:

```bash
# Replace YOUR_TENANT_ID with actual tenant_id
curl http://localhost:8000/api/v1/voice-agent/tenant-config/YOUR_TENANT_ID
```

## Auto-Creation

**Good news!** The system now auto-creates `business_config` in three places:

1. **During Registration** - New users get business_config automatically
2. **During Login** - If missing, it's created when you login
3. **When Agent Worker Requests** - The tenant-config endpoint auto-creates it

So you don't need to manually create it anymore!

## Testing

### Test 1: Get Tenant ID
```bash
python3 test_tenant_config.py
```

This will:
- Login with your credentials
- Extract tenant_id from JWT token
- Test the tenant-config endpoint
- Test the webrtc/test endpoint

### Test 2: Check Database
```bash
python3 debug_tenant_config.py
```

This will:
- Check if business_config exists
- Create it if missing
- Show all tenant information

## Expected Output

When you run `test_tenant_config.py`, you should see:

```
✅ Login successful
✅ Found tenant_id in token: <your-tenant-id>
✅ Tenant config retrieved successfully!
✅ WebRTC test endpoint works!
🎉 All tests passed!
```

## Troubleshooting

### "Connection refused"
- Backend is not running
- Start it: `./start.sh`

### "Tenant configuration not found"
- The auto-create should fix this
- Try logging in again (triggers auto-create)
- Or run: `python3 debug_tenant_config.py`

### "No tenant_id in token"
- Your account might not have a tenant_id
- This is a critical issue - contact support

## Your Tenant ID

After running the test script, it will show your tenant_id. Save it for debugging!

Example output:
```
💡 Your tenant_id is: 692f43697c982c08898e127b
   Save this for debugging!
```


