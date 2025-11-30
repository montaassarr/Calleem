import asyncio
import httpx
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from routers.users import create_access_token

API_URL = "http://localhost:8000/api/v1"

# Test User Credentials (from previous test)
TEST_USER = {
    "username": "test_user",
    "password": "SecurePassword123!"
}

async def test_voice_agent_endpoints():
    print("\n🧪 Testing Voice Agent Endpoints...")
    
    async with httpx.AsyncClient() as client:
        # 1. Login to get token
        print("\n[1] Logging in...")
        login_data = {
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
        resp = await client.post(f"{API_URL}/users/login", data=login_data)
        if resp.status_code != 200:
            print(f"❌ Login failed: {resp.text}")
            return
            
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("    ✅ Logged in")
        
        # 2. Check Status
        print("\n[2] Checking Voice Agent Status...")
        resp = await client.get(f"{API_URL}/voice-agent/status", headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            print(f"    ✅ Status: {data.get('status')}")
            print(f"    ℹ️ Assistant ID: {data.get('assistant_id')}")
            print(f"    ℹ️ Model: {data.get('groq_model')}")
        else:
            print(f"    ❌ Status check failed: {resp.status_code} - {resp.text}")
            
        # 3. Check History
        print("\n[3] Checking Call History...")
        resp = await client.get(f"{API_URL}/voice-agent/history", headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("items", [])
            print(f"    ✅ History fetched: {len(items)} calls")
        else:
            print(f"    ❌ History check failed: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    asyncio.run(test_voice_agent_endpoints())
