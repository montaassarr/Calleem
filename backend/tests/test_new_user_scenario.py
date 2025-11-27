import asyncio
import logging
import httpx
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = "http://localhost:8000/api/v1"
FRONTEND_URL = "http://localhost:3000"

TEST_USER = {
    "email": "montassartentouch4@gmail.com",
    "password": "SecurePassword123!",
    "username": "test_user",
    "full_name": "Test User"
}

VAPI_CONFIG = {
    "vapi_api_key": "957f3d01-6229-4834-bfff-667ccf49ff50",
    # Public key might be stored in frontend config or backend if needed, 
    # but BusinessConfig model has vapi_api_key. 
    # Let's check if there's a field for public key or if it's just used in frontend.
    # BusinessConfig has vapi_api_key. It doesn't seem to have public key field explicitly 
    # in the Pydantic model I saw earlier, but it allows extra fields.
    "vapi_public_key": "5c43aa1c-9745-47a3-9d71-0e751df8097a",
    "business_name": "Test User Business",
    "business_email": "montassartentouch4@gmail.com"
}

async def test_new_user_scenario():
    print("\n🧪 Testing New User Scenario...")
    
    async with httpx.AsyncClient() as client:
        # 1. Check Frontend Health
        print("\n[1] Checking Frontend Health...")
        try:
            resp = await client.get(FRONTEND_URL)
            if resp.status_code == 200:
                print("    ✅ Frontend is reachable at localhost:3000")
            else:
                print(f"    ⚠️ Frontend returned status {resp.status_code}")
        except Exception as e:
             print(f"    ❌ Frontend unreachable: {e}")

        # 2. Register User
        print("\n[2] Registering User...")
        # First check if user exists to avoid 400 error on re-run
        # We can't check easily without login, so we'll try login first.
        
        token = None
        
        print("    Attempting login first...")
        login_data = {
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
        resp = await client.post(f"{API_URL}/users/login", data=login_data)
        
        if resp.status_code == 200:
            print("    ✅ User already exists, logged in.")
            token = resp.json()["access_token"]
        else:
            print("    User not found, registering...")
            resp = await client.post(f"{API_URL}/users/register", json=TEST_USER)
            if resp.status_code == 201:
                print("    ✅ Registration successful")
                # Login to get token
                resp = await client.post(f"{API_URL}/users/login", data=login_data)
                token = resp.json()["access_token"]
            else:
                print(f"    ❌ Registration failed: {resp.status_code} {resp.text}")
                return

        if not token:
            print("    ❌ Failed to obtain token")
            return

        headers = {"Authorization": f"Bearer {token}"}

        # 3. Configure Business (VAPI Keys)
        print("\n[3] Configuring Business (VAPI Keys)...")
        
        # Get current config first
        resp = await client.get(f"{API_URL}/admin/config", headers=headers) # Using admin endpoint as owner
        current_config = resp.json()
        
        # Merge with new config
        update_payload = {
            **current_config,
            **VAPI_CONFIG,
            "business_name": "Test User Business", # Ensure required field
            "timezone": "UTC",
            "currency": "USD"
        }
        
        # Remove read-only fields if any
        if "id" in update_payload: del update_payload["id"]
        if "_id" in update_payload: del update_payload["_id"]
        if "created_at" in update_payload: del update_payload["created_at"]
        if "updated_at" in update_payload: del update_payload["updated_at"]
        
        resp = await client.put(f"{API_URL}/admin/config", json=update_payload, headers=headers)
        
        if resp.status_code == 200:
            print("    ✅ Configuration updated successfully")
            config = resp.json()
            # Verify VAPI Key (it might be masked or encrypted in response, but let's check)
            # The model decrypts it on GET, so we should see it.
            if config.get("vapi_api_key") == VAPI_CONFIG["vapi_api_key"]:
                print("    ✅ VAPI API Key verified")
            else:
                print(f"    ⚠️ VAPI API Key mismatch or masked: {config.get('vapi_api_key')}")
        else:
            print(f"    ❌ Configuration update failed: {resp.status_code} {resp.text}")
            
        # 4. Verify User Email
        print("\n[4] Verifying User Email...")
        resp = await client.get(f"{API_URL}/users/me", headers=headers)
        user_info = resp.json()
        if user_info["email"] == TEST_USER["email"]:
             print(f"    ✅ User email verified: {user_info['email']}")
        else:
             print(f"    ❌ User email mismatch: {user_info['email']}")

if __name__ == "__main__":
    asyncio.run(test_new_user_scenario())
