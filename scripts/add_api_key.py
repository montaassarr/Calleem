#!/usr/bin/env python3
"""
Script to add API keys for voice agent
Usage: python3 add_api_key.py --provider groq --key YOUR_API_KEY
"""

import requests
import argparse
import sys

# Configuration
BACKEND_URL = "http://localhost:8000/api/v1"
USERNAME = "montamsallem@gmail.com"
PASSWORD = "Mariemmontassar03$"

def login():
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

def add_api_key(token: str, provider: str, api_key: str, name: str = None):
    """Add an API key"""
    print(f"🔑 Adding {provider} API key...")
    
    if not name:
        name = f"{provider.title()} API Key"
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/keys",
            json={
                "provider": provider,
                "api_key": api_key,
                "name": name
            },
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=30  # Validation may take time
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ {provider} API key added successfully!")
            print(f"   Key ID: {result.get('id')}")
            print(f"   Name: {result.get('name')}")
            print(f"   Masked: {result.get('masked_key')}")
            return True
        else:
            error_text = response.text
            print(f"❌ Failed to add API key: {response.status_code}")
            print(f"   Error: {error_text}")
            return False
    except Exception as e:
        print(f"❌ Error adding API key: {e}")
        return False

def list_api_keys(token: str):
    """List all API keys"""
    print("📋 Listing API keys...")
    try:
        response = requests.get(
            f"{BACKEND_URL}/keys",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            keys = response.json()
            if keys:
                print(f"\n✅ Found {len(keys)} API key(s):\n")
                for key in keys:
                    print(f"   Provider: {key.get('provider')}")
                    print(f"   Name: {key.get('name')}")
                    print(f"   Masked: {key.get('masked_key')}")
                    print(f"   Valid: {key.get('is_valid')}")
                    print()
            else:
                print("⚠️  No API keys configured")
            return keys
        else:
            print(f"❌ Failed to list keys: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error listing keys: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description="Add API keys for voice agent")
    parser.add_argument("--provider", choices=["groq", "openai", "anthropic", "elevenlabs", "deepgram", "cartesia"], 
                       help="API provider")
    parser.add_argument("--key", help="API key value")
    parser.add_argument("--name", help="Optional name for the key")
    parser.add_argument("--list", action="store_true", help="List all API keys")
    
    args = parser.parse_args()
    
    # Login
    token = login()
    if not token:
        print("\n❌ Cannot proceed without authentication")
        return 1
    
    # List keys if requested
    if args.list:
        list_api_keys(token)
        return 0
    
    # Add key if provided
    if args.provider and args.key:
        success = add_api_key(token, args.provider, args.key, args.name)
        if success:
            print("\n✅ API key added! The voice agent should now work.")
            print("\n💡 Next steps:")
            print("   1. Test the voice agent: http://localhost:3000/dashboard/voice-agent/test")
            print("   2. Check agent logs: docker compose logs -f parker_agent")
            return 0
        else:
            return 1
    else:
        print("❌ Please provide --provider and --key, or use --list to see existing keys")
        print("\nExample:")
        print("  python3 add_api_key.py --provider groq --key gsk_...")
        print("  python3 add_api_key.py --list")
        return 1

if __name__ == "__main__":
    sys.exit(main())

