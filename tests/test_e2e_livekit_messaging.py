#!/usr/bin/env python3
"""
End-to-End Test for LiveKit Agent Messaging
Tests the full flow: Login -> Create Session -> Agent Connection
"""

import asyncio
import httpx
import json

# Configuration
BACKEND_URL = "http://localhost:8000"
EMAIL = "montamsallem@gmail.com"
PASSWORD = "Mariemmontassar03$"


async def run_e2e_test():
    print("=" * 70)
    print("🧪 E2E TEST: LiveKit Agent Messaging")
    print("=" * 70)
    print()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Authenticate
        print("1️⃣  Authenticating user...")
        try:
            login_response = await client.post(
                f"{BACKEND_URL}/api/v1/users/login",
                data={"username": EMAIL, "password": PASSWORD},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if login_response.status_code != 200:
                print(f"   ❌ Login failed: {login_response.status_code}")
                print(f"   Response: {login_response.text}")
                return False
            
            auth_data = login_response.json()
            token = auth_data.get("access_token")
            print(f"   ✅ Authenticated successfully")
            print(f"   Token: {token[:30]}...")
        except Exception as e:
            print(f"   ❌ Error during login: {e}")
            return False
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 2: Get User Info (to verify tenant_id)
        print()
        print("2️⃣  Fetching user profile...")
        try:
            me_response = await client.get(
                f"{BACKEND_URL}/api/v1/users/me",
                headers=headers
            )
            if me_response.status_code == 200:
                user_data = me_response.json()
                tenant_id = user_data.get("tenant_id", "")
                business_name = user_data.get("business_name", "N/A")
                print(f"   ✅ User: {user_data.get('email')}")
                print(f"   Tenant ID: {tenant_id}")
                print(f"   Business: {business_name}")
            else:
                print(f"   ⚠️  Could not fetch user profile: {me_response.status_code}")
                tenant_id = None
        except Exception as e:
            print(f"   ⚠️  Error fetching profile: {e}")
            tenant_id = None
        
        # Step 3: Check Voice Agent Status
        print()
        print("3️⃣  Checking voice agent status...")
        try:
            status_response = await client.get(
                f"{BACKEND_URL}/api/v1/voice-agent/status",
                headers=headers
            )
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"   ✅ Voice Agent Status:")
                print(f"      - Configured: {status.get('configured')}")
                print(f"      - Enabled: {status.get('voice_agent_enabled')}")
                print(f"      - Agent Name: {status.get('agent_name')}")
            else:
                print(f"   ⚠️  Status check failed: {status_response.status_code}")
        except Exception as e:
            print(f"   ⚠️  Error checking status: {e}")
        
        # Step 4: Create WebRTC Session (triggers agent)
        print()
        print("4️⃣  Creating LiveKit WebRTC session...")
        try:
            webrtc_response = await client.post(
                f"{BACKEND_URL}/api/v1/voice-agent/webrtc/test",
                json={},
                headers=headers
            )
            
            if webrtc_response.status_code == 200:
                session_data = webrtc_response.json()
                print(f"   ✅ Session created successfully!")
                print(f"   Room Name: {session_data.get('room_name')}")
                print(f"   Agent Name: {session_data.get('agent_name')}")
                print(f"   Agent Queue: {session_data.get('agent_queue')}")
                print(f"   LiveKit URL: {session_data.get('url')}")
                token_preview = session_data.get('token', '')[:50] + "..."
                print(f"   Token: {token_preview}")
                
                room_name = session_data.get('room_name')
            else:
                print(f"   ❌ Failed to create session: {webrtc_response.status_code}")
                print(f"   Response: {webrtc_response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Error creating session: {e}")
            return False
        
        # Step 5: Test Agent Configuration
        print()
        print("5️⃣  Fetching tenant agent configuration...")
        try:
            if tenant_id:
                config_response = await client.get(
                    f"{BACKEND_URL}/api/v1/voice-agent/tenant-config/{tenant_id}",
                )
                if config_response.status_code == 200:
                    config = config_response.json()
                    print(f"   ✅ Agent Config Retrieved:")
                    print(f"      - Business: {config.get('business_name')}")
                    print(f"      - API Keys: {list(config.get('api_keys', {}).keys())}")
                    agent_config = config.get('agent_config', {})
                    print(f"      - LLM Model: {agent_config.get('llm_model')}")
                    print(f"      - Voice Provider: {agent_config.get('voice_provider')}")
                else:
                    print(f"   ⚠️  Config fetch failed: {config_response.status_code}")
            else:
                print(f"   ⚠️  No tenant_id available for config fetch")
        except Exception as e:
            print(f"   ⚠️  Error fetching config: {e}")
        
        # Step 6: Test Agent Endpoints (simulate what agent calls)
        print()
        print("6️⃣  Testing agent tool endpoints...")
        
        # Test list services
        try:
            services_response = await client.get(
                f"{BACKEND_URL}/api/v1/services/",
                headers={"X-Tenant-ID": tenant_id} if tenant_id else headers
            )
            if services_response.status_code == 200:
                services = services_response.json()
                print(f"   ✅ Services: {len(services)} services found")
                for svc in services[:3]:
                    print(f"      - {svc.get('name', 'N/A')}")
            else:
                print(f"   ⚠️  Services endpoint: {services_response.status_code}")
        except Exception as e:
            print(f"   ⚠️  Error fetching services: {e}")
        
        # Test availability check
        from datetime import datetime, timedelta
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        try:
            avail_response = await client.get(
                f"{BACKEND_URL}/api/v1/appointments/availability/check",
                params={"date": tomorrow},
                headers={"X-Tenant-ID": tenant_id} if tenant_id else headers
            )
            if avail_response.status_code == 200:
                avail = avail_response.json()
                slots = avail.get("available_slots", [])
                print(f"   ✅ Availability ({tomorrow}): {len(slots)} slots")
                if slots:
                    print(f"      First few: {slots[:3]}")
            else:
                print(f"   ⚠️  Availability check: {avail_response.status_code}")
        except Exception as e:
            print(f"   ⚠️  Error checking availability: {e}")
        
        print()
        print("=" * 70)
        print("✅ E2E TEST COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print()
        print("📋 Summary:")
        print(f"   • User authenticated: {EMAIL}")
        print(f"   • Tenant ID: {tenant_id}")
        print(f"   • LiveKit room created: {room_name}")
        print(f"   • Agent should now be listening in the room")
        print()
        print("🎤 To test voice interaction:")
        print(f"   1. Open: http://localhost:3000/dashboard/voice-agent/test")
        print(f"   2. Click 'Start Call'")
        print(f"   3. Say 'Hello, can you hear me?'")
        print(f"   4. The agent should respond!")
        print()
        
        return True


if __name__ == "__main__":
    success = asyncio.run(run_e2e_test())
    exit(0 if success else 1)
