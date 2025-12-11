#!/usr/bin/env python3
"""
Test the complete voice agent flow:
1. Login
2. Create WebRTC session 
3. Verify token and room details
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def test_voice_flow():
    print("=" * 60)
    print("TESTING COMPLETE VOICE AGENT FLOW")
    print("=" * 60)
    
    # Step 1: Login
    print("\n1. Authenticating...")
    login_data = {
        "email": "montamsallem@gmail.com",
        "password": "Mariemmontassar03$"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return False
    
    auth_data = response.json()
    token = auth_data["access_token"]
    tenant_id = auth_data["user"]["tenant_id"]
    print(f"✅ Logged in successfully")
    print(f"   Tenant ID: {tenant_id}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Get tenant config (what the agent worker fetches)
    print("\n2. Fetching tenant configuration...")
    response = requests.get(f"{BASE_URL}/voice-agent/tenant-config/{tenant_id}")
    if response.status_code != 200:
        print(f"❌ Failed to get config: {response.status_code}")
        print(response.text)
        return False
    
    config = response.json()
    print(f"✅ Tenant configuration retrieved")
    print(f"   LLM Model: {config.get('llm_model', 'NOT FOUND')}")
    print(f"   Voice Provider: {config.get('voice_provider', 'NOT FOUND')}")
    print(f"   Voice ID: {config.get('voice_id', 'NOT FOUND')[:30]}...")
    print(f"   System Prompt: {config.get('system_prompt', 'NOT FOUND')[:50]}...")
    
    # Step 3: Create WebRTC session (what frontend does)
    print("\n3. Creating WebRTC session...")
    response = requests.post(f"{BASE_URL}/voice-agent/webrtc/test", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to create session: {response.status_code}")
        print(response.text)
        return False
    
    session = response.json()
    print(f"✅ WebRTC session created")
    print(f"   Room Name: {session['room_name']}")
    print(f"   Token: {session['token'][:50]}...")
    print(f"   LiveKit URL: {session['url']}")
    
    # Step 4: Check agent worker status
    print("\n4. Checking agent worker status...")
    import subprocess
    result = subprocess.run(
        ["ps", "aux"],
        capture_output=True,
        text=True
    )
    
    agent_running = "tenant_agent.py" in result.stdout
    if agent_running:
        print("✅ Agent worker is running")
        # Get process info
        for line in result.stdout.split("\n"):
            if "tenant_agent.py" in line and "grep" not in line:
                parts = line.split()
                if len(parts) > 1:
                    print(f"   PID: {parts[1]}")
                break
    else:
        print("❌ Agent worker is NOT running")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL SYSTEMS READY FOR VOICE INTERACTION")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Open http://localhost:3000/dashboard/voice-agent/chat")
    print("2. Click 'Start Chat' button")
    print("3. Allow microphone permissions")
    print("4. Say: 'Hello, I need to book an appointment'")
    print("\nThe AI should:")
    print("- Greet you with voice")
    print("- Ask what service you need")
    print("- Check availability")
    print("- Book the appointment")
    
    return True

if __name__ == "__main__":
    try:
        success = test_voice_flow()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
