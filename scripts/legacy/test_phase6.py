#!/usr/bin/env python3
"""
Test script for Phase 6 - Frontend Integration
Validates backend API endpoints work correctly before frontend testing
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_health():
    """Test health endpoint"""
    print_section("Test 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_business_config_get():
    """Test GET business config endpoint"""
    print_section("Test 2: Get Business Config (No Auth)")
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/business/config")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            config = response.json()
            print("✅ Config retrieved successfully")
            print(f"   Business: {config.get('business_name', 'N/A')}")
            print(f"   Phone: {config.get('phone_number', 'N/A')}")
            print(f"   Timezone: {config.get('timezone', 'N/A')}")
            print(f"   AI Model: {config.get('ai_config', {}).get('model', 'N/A')}")
            return True
        elif response.status_code == 404:
            print("⚠️  No config found - need to create default config")
            return False
        else:
            print(f"❌ Failed to get config: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_default_config():
    """Create a default business configuration"""
    print_section("Test 3: Create Default Business Config via MongoDB")
    
    print("⚠️  Note: PUT /config requires authentication")
    print("   Creating config directly in MongoDB instead...")
    
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        import asyncio
        
        async def insert_config():
            client = AsyncIOMotorClient("mongodb://localhost:27017")
            db = client.ai_barber_receptionist
            
            default_config = {
                "business_id": "default",
                "business_name": "Royal Fade Barbershop",
                "phone_number": "+216 20 123 456",
                "email": "contact@royalfade.tn",
                "address": "123 Avenue Habib Bourguiba, Tunis",
                "timezone": "Africa/Tunis",
                "business_hours": [
                    {"day": "Monday", "is_open": True, "open_time": "09:00", "close_time": "19:00"},
                    {"day": "Tuesday", "is_open": True, "open_time": "09:00", "close_time": "19:00"},
                    {"day": "Wednesday", "is_open": True, "open_time": "09:00", "close_time": "19:00"},
                    {"day": "Thursday", "is_open": True, "open_time": "09:00", "close_time": "19:00"},
                    {"day": "Friday", "is_open": True, "open_time": "09:00", "close_time": "20:00"},
                    {"day": "Saturday", "is_open": True, "open_time": "10:00", "close_time": "20:00"},
                    {"day": "Sunday", "is_open": False, "open_time": "00:00", "close_time": "00:00"}
                ],
                "services": [
                    {"name": "Classic Haircut", "duration_minutes": 30, "price": 25.0, "is_active": True},
                    {"name": "Beard Trim", "duration_minutes": 20, "price": 15.0, "is_active": True},
                    {"name": "Royal Fade", "duration_minutes": 45, "price": 40.0, "is_active": True}
                ],
                "ai_config": {
                    "model": "llama-3.1-70b-versatile",
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "system_prompt": "You are Ava, a friendly AI receptionist for Royal Fade Barbershop in Tunis, Tunisia."
                },
                "whatsapp_config": {
                    "phone_number_id": "897432366779845",
                    "is_enabled": True
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Upsert config
            result = await db.business_configs.update_one(
                {"business_id": "default"},
                {"$set": default_config},
                upsert=True
            )
            
            client.close()
            return result
        
        result = asyncio.run(insert_config())
        print("✅ Default config created in MongoDB")
        print(f"   Matched: {result.matched_count}, Modified: {result.modified_count}, Upserted: {result.upserted_id is not None}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_ai_prompt_endpoint():
    """Test AI prompt endpoints"""
    print_section("Test 4: AI Prompt Endpoints")
    try:
        # Get AI prompt
        response = requests.get(f"{BASE_URL}{API_PREFIX}/business/config/ai-prompt")
        if response.status_code == 200:
            prompt_data = response.json()
            print("✅ AI Prompt retrieved")
            print(f"   Prompt length: {len(prompt_data.get('prompt', ''))} characters")
            print(f"   Preview: {prompt_data.get('prompt', '')[:100]}...")
            return True
        else:
            print(f"⚠️  Prompt not available: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_services_endpoint():
    """Test services endpoint"""
    print_section("Test 5: Services Endpoint")
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/business/config/services")
        if response.status_code == 200:
            services = response.json()
            print(f"✅ Services retrieved: {len(services.get('services', []))} services")
            for service in services.get('services', [])[:3]:
                print(f"   - {service['name']}: {service['price']} TND ({service['duration_minutes']} min)")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_all_tests():
    """Run all Phase 6 tests"""
    print("\n" + "="*60)
    print("  PHASE 6 INTEGRATION TESTS")
    print("  Testing Backend API Endpoints for Frontend")
    print("="*60)
    
    results = {
        "health": test_health(),
        "get_config": test_business_config_get(),
    }
    
    # If no config exists, create one
    if not results["get_config"]:
        results["create_config"] = create_default_config()
        # Retry getting config
        results["get_config_retry"] = test_business_config_get()
    
    results["ai_prompt"] = test_ai_prompt_endpoint()
    results["services"] = test_services_endpoint()
    
    # Summary
    print_section("Test Summary")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    for test, result in results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {test}")
    
    print("\n" + "="*60)
    if passed == total:
        print("  🎉 ALL TESTS PASSED!")
        print("  Frontend can now connect to these endpoints")
    else:
        print("  ⚠️  Some tests failed - check configuration")
    print("="*60 + "\n")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()
