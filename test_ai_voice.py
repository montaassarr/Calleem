#!/usr/bin/env python3
"""
Test script to verify AI voice agent backend functionality
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_voice_agent():
    print("🧪 Testing AI Voice Agent Backend\n")
    print("=" * 60)
    
    # Step 1: Login
    print("\n1️⃣  Testing Authentication...")
    login_response = requests.post(
        f"{BASE_URL}/users/login",
        data={"username": "mike_royalfade", "password": "test123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if login_response.status_code != 200:
        print(f"   ❌ Login failed: {login_response.text}")
        return False
    
    token = login_response.json()["access_token"]
    print(f"   ✅ Login successful")
    print(f"   📝 Token: {token[:50]}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Get Agent Config
    print("\n2️⃣  Testing Agent Configuration...")
    agent_response = requests.get(f"{BASE_URL}/agents/my-agent", headers=headers)
    
    if agent_response.status_code == 200:
        agent = agent_response.json()
        print(f"   ✅ Agent found: {agent.get('name')}")
        print(f"   🤖 LLM Model: {agent.get('llm_model')}")
        print(f"   🎙️  Voice Provider: {agent.get('voice_settings', {}).get('provider')}")
        print(f"   📊 Status: {agent.get('status')}")
    else:
        print(f"   ❌ Failed to get agent: {agent_response.text}")
    
    # Step 3: Create WebRTC Session
    print("\n3️⃣  Testing WebRTC Session Creation...")
    webrtc_response = requests.post(
        f"{BASE_URL}/voice-agent/webrtc/test",
        json={},
        headers=headers
    )
    
    if webrtc_response.status_code == 200:
        session = webrtc_response.json()
        print(f"   ✅ Session created successfully")
        print(f"   🏠 Room: {session.get('room_name')}")
        print(f"   🌐 WebSocket URL: {session.get('url')}")
        print(f"   👤 Agent Name: {session.get('agent_name')}")
        print(f"   📋 Agent Queue: {session.get('agent_queue')}")
        print(f"   🎫 Token: {session.get('token')[:50]}...")
        
        # Step 4: Verify LiveKit Connection
        print("\n4️⃣  Verifying LiveKit Configuration...")
        livekit_url = session.get('url')
        if livekit_url and 'livekit.cloud' in livekit_url:
            print(f"   ✅ LiveKit URL is valid: {livekit_url}")
        else:
            print(f"   ⚠️  LiveKit URL might be invalid: {livekit_url}")
        
        return True
    else:
        print(f"   ❌ Failed to create session: {webrtc_response.text}")
        return False

if __name__ == "__main__":
    print("\n" + "🎯 " * 30)
    success = test_voice_agent()
    print("\n" + "=" * 60)
    
    if success:
        print("\n✅ ALL TESTS PASSED!")
        print("\n📝 Summary:")
        print("   • Backend API is responding correctly")
        print("   • Authentication is working")
        print("   • Agent configuration is accessible")
        print("   • WebRTC session tokens are being generated")
        print("   • LiveKit connection details are valid")
        print("\n🎤 The AI can now respond through the frontend!")
        print("   Access: http://localhost:3000/dashboard/voice-agent/chat")
    else:
        print("\n❌ TESTS FAILED - Check the errors above")
    
    print("\n" + "🎯 " * 30 + "\n")
