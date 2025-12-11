#!/usr/bin/env python3
"""
Test script to get tenant_id and test LiveKit tenant-config endpoint
This script will:
1. Login with your credentials
2. Extract tenant_id from the JWT token
3. Test the tenant-config endpoint
4. Show what's in the database
"""

import requests
import json
import sys
from typing import Optional

# Configuration
BACKEND_URL = "http://localhost:8000/api/v1"
USERNAME = "montamsallem@gmail.com"
PASSWORD = "Mariemmontassar03$"

def login() -> Optional[str]:
    """Login and return JWT token"""
    print("🔐 Logging in...")
    try:
        response = requests.post(
            f"{BACKEND_URL}/users/login",
            data={"username": USERNAME, "password": PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✅ Login successful\n")
            return token
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def decode_jwt_token(token: str) -> dict:
    """Decode JWT token to get tenant_id"""
    import base64
    try:
        # JWT format: header.payload.signature
        parts = token.split('.')
        if len(parts) < 2:
            return {}
        
        # Decode payload (add padding if needed)
        payload = parts[1]
        padding = len(payload) % 4
        if padding:
            payload += '=' * (4 - padding)
        
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        print(f"⚠️  Error decoding token: {e}")
        return {}

def get_tenant_id_from_token(token: str) -> Optional[str]:
    """Extract tenant_id from JWT token"""
    payload = decode_jwt_token(token)
    tenant_id = payload.get("tenant_id")
    
    if tenant_id:
        print(f"✅ Found tenant_id in token: {tenant_id}")
        return tenant_id
    else:
        print("⚠️  No tenant_id in token payload")
        print(f"   Token payload: {json.dumps(payload, indent=2)}")
        return None

def get_user_info(token: str) -> Optional[dict]:
    """Get current user info from backend"""
    print("\n👤 Fetching user info...")
    try:
        response = requests.get(
            f"{BACKEND_URL}/users/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            user = response.json()
            print("✅ User info retrieved")
            return user
        else:
            print(f"⚠️  Failed to get user info: {response.status_code}")
            return None
    except Exception as e:
        print(f"⚠️  Error getting user info: {e}")
        return None

def test_tenant_config(tenant_id: str) -> bool:
    """Test the tenant-config endpoint"""
    print(f"\n🧪 Testing tenant-config endpoint...")
    print(f"   URL: {BACKEND_URL}/voice-agent/tenant-config/{tenant_id}")
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/voice-agent/tenant-config/{tenant_id}",
            timeout=10
        )
        
        if response.status_code == 200:
            config = response.json()
            print("✅ Tenant config retrieved successfully!")
            print(f"\n📋 Configuration:")
            print(f"   Tenant ID: {config.get('tenant_id')}")
            print(f"   Business Name: {config.get('business_name')}")
            print(f"   API Keys: {len(config.get('api_keys', {}))} providers")
            for provider, key in config.get('api_keys', {}).items():
                masked = key[:10] + "..." if len(key) > 10 else key
                print(f"      - {provider}: {masked}")
            print(f"   LLM Model: {config.get('llm_model', 'N/A')}")
            print(f"   Voice Provider: {config.get('voice_provider', 'N/A')}")
            print(f"   Voice ID: {config.get('voice_id', 'N/A')}")
            return True
        elif response.status_code == 404:
            print(f"❌ Tenant config not found (404)")
            print(f"   This means business_config doesn't exist for tenant_id: {tenant_id}")
            print(f"   The backend should auto-create it, but let's check...")
            return False
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_webrtc_endpoint(token: str) -> bool:
    """Test the webrtc/test endpoint"""
    print(f"\n🧪 Testing webrtc/test endpoint...")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/voice-agent/webrtc/test",
            json={},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ WebRTC test endpoint works!")
            print(f"\n📋 Session Data:")
            print(f"   Room Name: {data.get('room_name')}")
            print(f"   URL: {data.get('url')}")
            print(f"   Token: {data.get('token', '')[:50]}...")
            print(f"   Agent Queue: {data.get('agent_queue')}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("🧪 Tenant Configuration Test")
    print("=" * 60)
    print()
    
    # Step 1: Login
    token = login()
    if not token:
        print("\n❌ Cannot proceed without authentication token")
        return
    
    # Step 2: Get tenant_id from token
    tenant_id = get_tenant_id_from_token(token)
    
    # Step 3: Also try getting from user info
    user_info = get_user_info(token)
    if user_info:
        user_tenant_id = user_info.get("tenant_id") or user_info.get("business_id")
        if user_tenant_id:
            print(f"✅ Found tenant_id from user info: {user_tenant_id}")
            if not tenant_id:
                tenant_id = user_tenant_id
            elif tenant_id != user_tenant_id:
                print(f"⚠️  Warning: Token tenant_id ({tenant_id}) != User tenant_id ({user_tenant_id})")
                print(f"   Using token tenant_id: {tenant_id}")
    
    if not tenant_id:
        print("\n❌ Cannot find tenant_id!")
        print("   This is a critical issue. Your account may not have a tenant_id assigned.")
        return
    
    print(f"\n✅ Using tenant_id: {tenant_id}")
    print()
    
    # Step 4: Test tenant-config endpoint
    config_success = test_tenant_config(tenant_id)
    
    # Step 5: Test webrtc endpoint
    webrtc_success = test_webrtc_endpoint(token)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"Tenant ID: {tenant_id}")
    print(f"Tenant Config Endpoint: {'✅ Working' if config_success else '❌ Failed'}")
    print(f"WebRTC Test Endpoint: {'✅ Working' if webrtc_success else '❌ Failed'}")
    print()
    
    if config_success and webrtc_success:
        print("🎉 All tests passed! Your setup is ready.")
        print()
        print("🔗 Test URLs:")
        print(f"   Tenant Config: {BACKEND_URL}/voice-agent/tenant-config/{tenant_id}")
        print(f"   WebRTC Test: {BACKEND_URL}/voice-agent/webrtc/test")
        print()
        print("💡 Your tenant_id is:", tenant_id)
        print("   Save this for debugging!")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        if not config_success:
            print()
            print("💡 To fix missing business_config:")
            print("   1. The backend should auto-create it now")
            print("   2. Or run: python3 debug_tenant_config.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()


