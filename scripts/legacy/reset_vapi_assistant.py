import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "testuser_vapi"
PASSWORD = "TestPassword123!"

def get_token():
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    response = requests.post(f"{BASE_URL}/users/login", data=login_data)
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Login failed: {response.text}")
        sys.exit(1)

def reset_vapi_assistant(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🔄 Resetting VAPI Assistant...")
    # First, update voice config to trigger reset
    config_payload = {
        "model_provider": "groq",
        "model_name": "llama-3.3-70b-versatile",
        "voice_provider": "openai",
        "voice_id": "alloy",
        "enabled_tools": ["check_availability", "book_appointment", "get_services"]
    }
    
    response = requests.put(f"{BASE_URL}/voice/config", json=config_payload, headers=headers)
    if response.status_code == 200:
        print(f"✅ Voice config updated: {response.json()}")
    else:
        print(f"❌ Failed to update config: {response.text}")
        return
    
    # Test the agent
    print("\n🧪 Testing VAPI Agent...")
    response = requests.get(f"{BASE_URL}/voice/test-agent", headers=headers)
    if response.status_code == 200:
        print(f"✅ Agent test successful: {response.json()}")
    else:
        print(f"❌ Agent test failed: {response.text}")

if __name__ == "__main__":
    token = get_token()
    reset_vapi_assistant(token)
