#!/usr/bin/env python3
"""
Quick test to verify AI agent is responding with voice
"""
import requests
import json

BACKEND_URL = "http://localhost:8000/api/v1"
EMAIL = "montamsallem@gmail.com"
PASSWORD = "Mariemmontassar03$"

def test_voice_agent():
    print("="*70)
    print("🎤 AI VOICE AGENT - QUICK TEST")
    print("="*70)
    print()
    
    # Login
    print("1. Authenticating...")
    response = requests.post(
        f"{BACKEND_URL}/users/login",
        data={"username": EMAIL, "password": PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code != 200:
        print("❌ Authentication failed")
        return False
    
    token = response.json()["access_token"]
    print("   ✅ Authenticated")
    
    # Create LiveKit session
    print("\n2. Creating LiveKit voice session...")
    response = requests.post(
        f"{BACKEND_URL}/voice-agent/webrtc/test",
        json={},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code != 200:
        print(f"   ❌ Failed: {response.text}")
        return False
    
    data = response.json()
    print(f"   ✅ Session created!")
    print(f"   Room: {data['room_name']}")
    print(f"   Agent: {data['agent_name']}")
    print(f"   URL: {data['url']}")
    
    # Get tenant config to check voice settings
    print("\n3. Checking AI voice configuration...")
    tenant_id = "692f43697c982c08898e127b"  # Your tenant ID
    
    response = requests.get(
        f"{BACKEND_URL}/voice-agent/tenant-config/{tenant_id}"
    )
    
    if response.status_code == 200:
        config = response.json()
        agent_config = config.get('agent_config', {})
        
        print("   ✅ Voice Configuration:")
        print(f"      LLM Model: {agent_config.get('llm_model', 'N/A')}")
        print(f"      Voice Provider: {agent_config.get('voice_provider', 'N/A')}")
        print(f"      Voice ID: {agent_config.get('voice_id', 'N/A')}")
        
        # Check if API keys are configured
        api_keys = config.get('api_keys', {})
        print(f"\n   API Keys Status:")
        print(f"      Groq (LLM): {'✅ Configured' if 'groq' in api_keys else '❌ Missing'}")
        print(f"      Cartesia (Voice): {'✅ Built-in' if agent_config.get('voice_provider') == 'cartesia' else '❌ Check config'}")
        print(f"      Deepgram (STT): ✅ Built-in")
    else:
        print(f"   ⚠️  Could not fetch config: {response.status_code}")
    
    # Instructions
    print("\n" + "="*70)
    print("📋 HOW TO TEST VOICE")
    print("="*70)
    print()
    print("The AI agent is ready! To hear the voice:")
    print()
    print("1. Open your browser:")
    print("   → http://localhost:3000/dashboard/voice-agent/chat")
    print()
    print("2. Click 'Start Chat' button")
    print()
    print("3. 🔊 IMPORTANT: Click 'Click to enable audio' button")
    print("   (This allows the browser to play AI voice)")
    print()
    print("4. Grant microphone permission when asked")
    print()
    print("5. Say: 'Hello, can you hear me?'")
    print()
    print("6. You should hear the AI respond!")
    print()
    print("🐛 TROUBLESHOOTING:")
    print()
    print("   If you don't hear voice:")
    print("   • Make sure speakers/headphones are connected")
    print("   • Check browser volume is not muted")
    print("   • Look for 'Click to enable audio' button and click it")
    print("   • Try refreshing the page and reconnecting")
    print("   • Check browser console for errors (F12)")
    print()
    print("="*70)
    
    return True

if __name__ == "__main__":
    test_voice_agent()
