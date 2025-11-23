import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "testuser_vapi"
PASSWORD = "TestPassword123!"
EMAIL = "test_vapi@example.com"

def get_token():
    # 1. Try to login
    print(f"🔑 Attempting login for {USERNAME}...")
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    response = requests.post(f"{BASE_URL}/users/login", data=login_data)
    
    if response.status_code == 200:
        print("✅ Login successful!")
        return response.json()["access_token"]
    
    # 2. If login fails, try to register
    print("⚠️  Login failed. Attempting registration...")
    register_data = {
        "username": USERNAME,
        "password": PASSWORD,
        "email": EMAIL,
        "full_name": "Test User",
        "role": "admin"
    }
    response = requests.post(f"{BASE_URL}/users/register", json=register_data)
    
    if response.status_code == 201:
        print("✅ Registration successful!")
        # Login again to get token
        return get_token()
    elif response.status_code == 400 and "already registered" in response.text:
        print("⚠️  User exists but login failed. Resetting DB might be needed if password changed.")
        sys.exit(1)
    else:
        print(f"❌ Registration failed: {response.text}")
        sys.exit(1)

def test_endpoints(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🎤 Testing VAPI Endpoints...")
    
    # Step 0: Enable Voice Agent
    print("\n0. PUT /voice/config (Enable Agent)")
    config_payload = {
        "model_provider": "groq",
        "model_name": "llama-3.3-70b-versatile",
        "voice_provider": "openai",
        "voice_id": "alloy",
        "enabled_tools": ["check_availability", "book_appointment"]
    }
    try:
        response = requests.put(f"{BASE_URL}/voice/config", json=config_payload, headers=headers)
        if response.status_code == 200:
            print(f"✅ Success: {response.json()}")
        else:
            print(f"❌ Failed ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 1: Simple Voice Test
    print("\n1. GET /voice/test")
    try:
        response = requests.get(f"{BASE_URL}/voice/test", headers=headers)
        if response.status_code == 200:
            print(f"✅ Success: {response.json()}")
        else:
            print(f"❌ Failed ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 2: VAPI Config (Public Key)
    print("\n2. GET /voice/vapi-config")
    try:
        response = requests.get(f"{BASE_URL}/voice/vapi-config", headers=headers)
        if response.status_code == 200:
            print(f"✅ Success: {response.json()}")
        else:
            print(f"❌ Failed ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 3: Test Agent (Internal Config)
    print("\n3. GET /voice/test-agent")
    try:
        response = requests.get(f"{BASE_URL}/voice/test-agent", headers=headers)
        if response.status_code == 200:
            print(f"✅ Success: {response.json()}")
        else:
            print(f"❌ Failed ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    try:
        token = get_token()
        test_endpoints(token)
    except Exception as e:
        print(f"\n❌ Critical Error: {e}")
