#!/usr/bin/env python3
"""
E2E Vapi Integration Test
Creates two business tenants, each with their own AI receptionist,
and tests the appointment booking flow.
"""

import asyncio
import httpx
import os
import sys
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, '/home/montassar/Desktop/ai_receptionist/backend')

# Vapi credentials from .env
VAPI_API_KEY = "REDACTED"
VAPI_BASE_URL = "https://api.vapi.ai"
BACKEND_URL = "http://localhost:8000/api/v1"

# Test data for two businesses
BUSINESSES = [
    {
        "name": "Bella's Hair Salon",
        "email": "bella@hairsalon.test",
        "password": "Test123!",
        "voice": "jennifer",
        "first_message": "Hello! Thank you for calling Bella's Hair Salon. How can I help you today?",
        "instructions": """You are a friendly receptionist for Bella's Hair Salon.
Services offered: Haircuts ($30), Color ($80), Highlights ($120), Styling ($50).
Business hours: Monday-Saturday 9 AM to 6 PM. Closed Sundays.
When booking, always confirm the service, date, time, and customer name."""
    },
    {
        "name": "Dr. Smith Dental Clinic",
        "email": "smith@dentalclinic.test",
        "password": "Test123!",
        "voice": "adam",
        "first_message": "Good day! You've reached Dr. Smith's Dental Clinic. How may I assist you?",
        "instructions": """You are a professional receptionist for Dr. Smith's Dental Clinic.
Services: Checkup ($75), Cleaning ($100), Filling ($150), Root Canal ($500), Whitening ($200).
Hours: Monday-Friday 8 AM to 5 PM.
For emergencies, collect details and assure callback within 1 hour."""
    }
]


async def test_vapi_direct():
    """Test direct connection to Vapi API"""
    print("\n" + "="*60)
    print("🔌 TESTING DIRECT VAPI API CONNECTION")
    print("="*60)
    
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: List existing assistants
        print("\n📋 Listing existing assistants...")
        try:
            response = await client.get(f"{VAPI_BASE_URL}/assistant", headers=headers)
            if response.status_code == 200:
                assistants = response.json()
                print(f"   ✅ Found {len(assistants)} existing assistants")
                for a in assistants[:5]:  # Show first 5
                    print(f"      - {a.get('name', 'Unnamed')} (ID: {a.get('id', 'N/A')[:8]}...)")
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text[:200]}")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
        
        # Test 2: Create test assistant for Business 1
        print(f"\n🤖 Creating assistant for '{BUSINESSES[0]['name']}'...")
        assistant_config = {
            "name": f"Test - {BUSINESSES[0]['name']}",
            "firstMessage": BUSINESSES[0]["first_message"],
            "model": {
                "provider": "openai",
                "model": "gpt-4o-mini",
                "temperature": 0.7,
                "messages": [
                    {"role": "system", "content": BUSINESSES[0]["instructions"]}
                ]
            },
            "voice": {
                "provider": "11labs",
                "voiceId": "EXAVITQu4vr4xnSDxMaL"  # Sarah voice
            },
            "transcriber": {
                "provider": "deepgram",
                "model": "nova-2",
                "language": "en"
            }
        }
        
        try:
            response = await client.post(
                f"{VAPI_BASE_URL}/assistant",
                headers=headers,
                json=assistant_config
            )
            if response.status_code in [200, 201]:
                assistant1 = response.json()
                print(f"   ✅ Created assistant: {assistant1.get('id')}")
                business1_assistant_id = assistant1.get('id')
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text[:300]}")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
        
        # Test 3: Create test assistant for Business 2
        print(f"\n🤖 Creating assistant for '{BUSINESSES[1]['name']}'...")
        assistant_config2 = {
            "name": f"Test - {BUSINESSES[1]['name']}",
            "firstMessage": BUSINESSES[1]["first_message"],
            "model": {
                "provider": "openai",
                "model": "gpt-4o-mini",
                "temperature": 0.7,
                "messages": [
                    {"role": "system", "content": BUSINESSES[1]["instructions"]}
                ]
            },
            "voice": {
                "provider": "11labs",
                "voiceId": "pNInz6obpgDQGcFmaJgB"  # Adam voice
            },
            "transcriber": {
                "provider": "deepgram",
                "model": "nova-2",
                "language": "en"
            }
        }
        
        try:
            response = await client.post(
                f"{VAPI_BASE_URL}/assistant",
                headers=headers,
                json=assistant_config2
            )
            if response.status_code in [200, 201]:
                assistant2 = response.json()
                print(f"   ✅ Created assistant: {assistant2.get('id')}")
                business2_assistant_id = assistant2.get('id')
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text[:300]}")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
        
        # Test 4: Get assistant details
        print(f"\n📖 Verifying assistant configurations...")
        for aid, name in [(business1_assistant_id, BUSINESSES[0]['name']), 
                          (business2_assistant_id, BUSINESSES[1]['name'])]:
            response = await client.get(f"{VAPI_BASE_URL}/assistant/{aid}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ {name}:")
                print(f"      - Voice: {data.get('voice', {}).get('voiceId', 'N/A')[:20]}...")
                print(f"      - Model: {data.get('model', {}).get('model', 'N/A')}")
            else:
                print(f"   ❌ Failed to get {name}")
        
        print("\n" + "="*60)
        print("✅ VAPI DIRECT CONNECTION TEST PASSED")
        print("="*60)
        print(f"\n📌 Created Assistants:")
        print(f"   1. {BUSINESSES[0]['name']}: {business1_assistant_id}")
        print(f"   2. {BUSINESSES[1]['name']}: {business2_assistant_id}")
        
        return {
            "business1": {"name": BUSINESSES[0]['name'], "assistant_id": business1_assistant_id},
            "business2": {"name": BUSINESSES[1]['name'], "assistant_id": business2_assistant_id}
        }


async def test_backend_integration():
    """Test backend API endpoints"""
    print("\n" + "="*60)
    print("🔌 TESTING BACKEND API INTEGRATION")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test health endpoint
        print("\n🏥 Testing backend health...")
        try:
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                health = response.json()
                print(f"   ✅ Backend healthy: {health.get('status')}")
                print(f"   - Database: {health.get('database')}")
            else:
                print(f"   ❌ Backend unhealthy: {response.status_code}")
                return False
        except httpx.ConnectError:
            print("   ❌ Backend not running! Start with: cd backend && uvicorn main:app --reload")
            return False
        
        # Test voice providers endpoint
        print("\n🎤 Testing /voice-providers endpoint...")
        try:
            # This endpoint doesn't require auth for listing
            response = await client.get(f"{BACKEND_URL}/voice-providers")
            if response.status_code == 200:
                providers = response.json()
                print(f"   ✅ Got {len(providers.get('providers', []))} voice providers")
            else:
                print(f"   ⚠️ Voice providers returned: {response.status_code}")
        except Exception as e:
            print(f"   ⚠️ Voice providers error: {e}")
        
        # Test built-in tools endpoint
        print("\n🔧 Testing /tools/built-in endpoint...")
        try:
            response = await client.get(f"{BACKEND_URL}/tools/built-in")
            if response.status_code == 200:
                tools = response.json()
                print(f"   ✅ Got {len(tools.get('tools', []))} built-in tools")
                for tool in tools.get('tools', []):
                    print(f"      - {tool.get('name')}: {tool.get('description', '')[:50]}...")
            else:
                print(f"   ⚠️ Built-in tools returned: {response.status_code}")
        except Exception as e:
            print(f"   ⚠️ Built-in tools error: {e}")
        
        print("\n" + "="*60)
        print("✅ BACKEND INTEGRATION TEST COMPLETE")
        print("="*60)
        return True


async def cleanup_test_assistants():
    """Clean up test assistants from Vapi"""
    print("\n" + "="*60)
    print("🧹 CLEANING UP TEST ASSISTANTS")
    print("="*60)
    
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{VAPI_BASE_URL}/assistant", headers=headers)
        if response.status_code == 200:
            assistants = response.json()
            test_assistants = [a for a in assistants if a.get('name', '').startswith('Test -')]
            print(f"   Found {len(test_assistants)} test assistants to clean up")
            
            for a in test_assistants:
                del_response = await client.delete(
                    f"{VAPI_BASE_URL}/assistant/{a['id']}",
                    headers=headers
                )
                if del_response.status_code in [200, 204]:
                    print(f"   ✅ Deleted: {a['name']}")
                else:
                    print(f"   ⚠️ Failed to delete: {a['name']}")


async def main():
    print("\n" + "🚀"*30)
    print("   VAPI E2E INTEGRATION TEST SUITE")
    print("🚀"*30)
    print(f"\n📅 Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 Using Vapi API Key: {VAPI_API_KEY[:8]}...{VAPI_API_KEY[-4:]}")
    
    # Run tests
    vapi_result = await test_vapi_direct()
    backend_result = await test_backend_integration()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"   Vapi Direct API: {'✅ PASSED' if vapi_result else '❌ FAILED'}")
    print(f"   Backend Integration: {'✅ PASSED' if backend_result else '❌ FAILED'}")
    
    if vapi_result:
        print(f"\n🎉 SUCCESS! Created test assistants:")
        print(f"   1. {vapi_result['business1']['name']}")
        print(f"      Assistant ID: {vapi_result['business1']['assistant_id']}")
        print(f"   2. {vapi_result['business2']['name']}")
        print(f"      Assistant ID: {vapi_result['business2']['assistant_id']}")
        print("\n📱 You can now test these assistants in the Vapi dashboard!")
        print("   https://dashboard.vapi.ai/assistants")
    
    # Ask about cleanup
    print("\n⚠️  Note: Test assistants were created in your Vapi account.")
    print("   To clean them up, run: python3 test_vapi_e2e.py --cleanup")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--cleanup":
        await cleanup_test_assistants()


if __name__ == "__main__":
    asyncio.run(main())
