"""
Tests for LiveKit Token Server Endpoint
========================================

Tests the POST /api/v1/livekit/token endpoint for generating LiveKit access tokens.
"""

import asyncio
import httpx
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

API_URL = "http://localhost:8000/api/v1"

# Test User Credentials
TEST_USER = {
    "username": "test_user",
    "password": "SecurePassword123!"
}


async def test_livekit_token_endpoints():
    """Test all LiveKit token endpoints."""
    print("\n" + "=" * 60)
    print("🧪 Testing LiveKit Token Server Endpoints")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Check LiveKit status (no auth required)
        print("\n[1] Checking LiveKit Status (no auth)...")
        resp = await client.get(f"{API_URL}/livekit/status")
        if resp.status_code == 200:
            data = resp.json()
            print(f"    ✅ Status endpoint works")
            print(f"    ℹ️  Configured: {data.get('configured')}")
            print(f"    ℹ️  Server URL: {data.get('server_url')}")
            print(f"    ℹ️  Agent Queue: {data.get('agent_queue')}")
        else:
            print(f"    ❌ Status check failed: {resp.status_code} - {resp.text}")
            return
        
        # 2. Try token without auth (should fail)
        print("\n[2] Testing token endpoint without auth (expect 401)...")
        resp = await client.post(
            f"{API_URL}/livekit/token",
            json={"room_name": "test", "participant_identity": "test"}
        )
        if resp.status_code == 401:
            print("    ✅ Correctly rejected unauthenticated request")
        else:
            print(f"    ❌ Expected 401, got: {resp.status_code}")
        
        # 3. Login to get token
        print("\n[3] Logging in...")
        login_data = {
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
        resp = await client.post(f"{API_URL}/users/login", data=login_data)
        if resp.status_code != 200:
            print(f"    ❌ Login failed: {resp.text}")
            print("    ℹ️  Trying to register user first...")
            
            # Try to register
            register_data = {
                "username": TEST_USER["username"],
                "password": TEST_USER["password"],
                "email": "test@callflow.ai",
                "full_name": "Test User",
                "business_name": "Test Business"
            }
            resp = await client.post(f"{API_URL}/users/register", json=register_data)
            if resp.status_code in [200, 201]:
                print("    ✅ Registered new user")
                token = resp.json()["access_token"]
            else:
                print(f"    ❌ Registration failed: {resp.text}")
                return
        else:
            token = resp.json()["access_token"]
            print("    ✅ Logged in successfully")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 4. Generate token (basic request)
        print("\n[4] Generating LiveKit token (basic)...")
        resp = await client.post(
            f"{API_URL}/livekit/token",
            headers=headers,
            json={
                "room_name": "test-room",
                "participant_identity": "user-123"
            }
        )
        if resp.status_code == 200:
            data = resp.json()
            print("    ✅ Token generated successfully")
            print(f"    ℹ️  Server URL: {data.get('server_url')}")
            print(f"    ℹ️  Token: {data.get('participant_token')[:50]}...")
        elif resp.status_code == 503:
            print(f"    ⚠️  LiveKit not configured: {resp.json().get('detail')}")
            print("    ℹ️  Set LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET in .env")
        else:
            print(f"    ❌ Token generation failed: {resp.status_code} - {resp.text}")
        
        # 5. Generate token with full options
        print("\n[5] Generating LiveKit token (full options)...")
        resp = await client.post(
            f"{API_URL}/livekit/token",
            headers=headers,
            json={
                "room_name": "meeting-room",
                "participant_identity": "host-1",
                "participant_name": "John Doe",
                "participant_metadata": {"role": "host", "custom": "data"},
                "ttl": 1800,  # 30 minutes
                "grants": {
                    "canPublish": True,
                    "canSubscribe": True,
                    "roomJoin": True
                }
            }
        )
        if resp.status_code == 200:
            data = resp.json()
            print("    ✅ Token generated with custom options")
            print(f"    ℹ️  Server URL: {data.get('server_url')}")
        elif resp.status_code == 503:
            print("    ⚠️  LiveKit not configured (expected in test environment)")
        else:
            print(f"    ❌ Token generation failed: {resp.status_code}")
        
        # 6. Test extended endpoint
        print("\n[6] Testing extended token endpoint...")
        resp = await client.post(
            f"{API_URL}/livekit/token/extended",
            headers=headers,
            json={
                "room_name": "extended-test",
                "participant_identity": "test-user"
            }
        )
        if resp.status_code == 200:
            data = resp.json()
            print("    ✅ Extended token generated")
            print(f"    ℹ️  Full room name: {data.get('room_name')}")
            print(f"    ℹ️  Agent queue: {data.get('agent_queue')}")
        elif resp.status_code == 503:
            print("    ⚠️  LiveKit not configured")
        else:
            print(f"    ❌ Extended token failed: {resp.status_code}")
        
        # 7. Test validation (missing required field)
        print("\n[7] Testing validation (missing room_name)...")
        resp = await client.post(
            f"{API_URL}/livekit/token",
            headers=headers,
            json={"participant_identity": "user-1"}  # Missing room_name
        )
        if resp.status_code == 422:
            print("    ✅ Correctly rejected invalid request (422)")
        else:
            print(f"    ❌ Expected 422, got: {resp.status_code}")
    
    print("\n" + "=" * 60)
    print("✅ LiveKit Token Server Tests Complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(test_livekit_token_endpoints())
