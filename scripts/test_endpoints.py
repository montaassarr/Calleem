#!/usr/bin/env python3
"""
Comprehensive Backend Endpoint Test Script
Tests all API endpoints to ensure they work correctly before deployment
"""

import requests
import json
import sys
from typing import Dict, List, Tuple
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Test results
results: List[Dict] = []
test_token: str = None
test_user_id: str = None
test_tenant_id: str = None


def log_test(name: str, method: str, endpoint: str, status: str, details: str = ""):
    """Log test result"""
    result = {
        "name": name,
        "method": method,
        "endpoint": endpoint,
        "status": status,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    results.append(result)
    
    status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"{status_icon} {method:6} {endpoint:50} - {name}")
    if details:
        print(f"   {details}")


def test_endpoint(name: str, method: str, endpoint: str, **kwargs) -> Tuple[bool, Dict]:
    """Test an endpoint and return (success, response_data)"""
    url = f"{API_BASE}{endpoint}"
    headers = kwargs.pop("headers", {})
    
    if test_token:
        headers["Authorization"] = f"Bearer {test_token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, **kwargs)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=kwargs.pop("json", {}), **kwargs)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=kwargs.pop("json", {}), **kwargs)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, **kwargs)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=kwargs.pop("json", {}), **kwargs)
        else:
            log_test(name, method, endpoint, "SKIP", f"Unsupported method: {method}")
            return False, {}
        
        success = 200 <= response.status_code < 300
        status = "PASS" if success else "FAIL"
        
        try:
            data = response.json()
        except:
            data = {"text": response.text[:200]}
        
        details = f"Status: {response.status_code}"
        if not success:
            details += f" - {data.get('detail', data.get('message', 'Unknown error'))}"
        
        log_test(name, method, endpoint, status, details)
        return success, data
        
    except requests.exceptions.ConnectionError:
        log_test(name, method, endpoint, "FAIL", "Connection refused - Is the server running?")
        return False, {}
    except Exception as e:
        log_test(name, method, endpoint, "FAIL", f"Exception: {str(e)}")
        return False, {}


def main():
    """Run all endpoint tests"""
    print("=" * 80)
    print("Backend Endpoint Test Suite")
    print("=" * 80)
    print(f"Testing API at: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}\n")
    
    # 1. Health Check Endpoints
    print("\n📋 Health & Status Endpoints")
    print("-" * 80)
    test_endpoint("Root endpoint", "GET", "/")
    test_endpoint("Health check", "GET", "/health")
    
    # 2. Authentication Endpoints
    print("\n🔐 Authentication Endpoints")
    print("-" * 80)
    test_endpoint("User registration", "POST", "/users/register", json={
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User"
    })
    
    # Try to login (may fail if user already exists, that's OK)
    success, data = test_endpoint("User login", "POST", "/users/login", json={
        "email": "test@example.com",
        "password": "TestPassword123!"
    })
    
    if success and "access_token" in data:
        global test_token
        test_token = data["access_token"]
        if "user" in data:
            global test_user_id, test_tenant_id
            test_user_id = data["user"].get("id")
            test_tenant_id = data["user"].get("tenant_id")
        print(f"   ✅ Obtained access token for authenticated tests")
    
    # 3. User Management Endpoints
    print("\n👤 User Management Endpoints")
    print("-" * 80)
    test_endpoint("Get current user", "GET", "/users/me")
    test_endpoint("List users (admin)", "GET", "/admin/users")
    
    # 4. Tenant Endpoints
    print("\n🏢 Tenant Endpoints")
    print("-" * 80)
    test_endpoint("List tenants (admin)", "GET", "/admin/tenants")
    test_endpoint("Lookup tenant by phone", "POST", "/tenants/lookup", json={"phone": "+1234567890"})
    
    # 5. Services Endpoints
    print("\n🛎️  Services Endpoints")
    print("-" * 80)
    test_endpoint("List services", "GET", "/services/")
    test_endpoint("Create service", "POST", "/services/", json={
        "name": "Test Service",
        "description": "Test service description",
        "duration_minutes": 30,
        "price": 50.00,
        "active": True
    })
    
    # 6. Appointments Endpoints
    print("\n📅 Appointments Endpoints")
    print("-" * 80)
    test_endpoint("List appointments", "GET", "/appointments/")
    test_endpoint("Check availability", "GET", "/appointments/availability/check", params={
        "date": "2025-12-25",
        "time": "10:00",
        "duration_minutes": 30
    })
    test_endpoint("Appointment stats", "GET", "/appointments/stats/summary")
    
    # 7. Conversations Endpoints
    print("\n💬 Conversations Endpoints")
    print("-" * 80)
    test_endpoint("List conversations", "GET", "/conversations")
    
    # 8. Agents Endpoints
    print("\n🤖 Agents Endpoints")
    print("-" * 80)
    test_endpoint("Get my agent", "GET", "/agents/my-agent")
    
    # 9. Assistant Endpoints
    print("\n🎙️  Assistant Endpoints")
    print("-" * 80)
    test_endpoint("Get my assistant", "GET", "/assistant/me")
    test_endpoint("Get voice providers", "GET", "/voice-providers")
    
    # 10. API Keys Endpoints
    print("\n🔑 API Keys Endpoints")
    print("-" * 80)
    test_endpoint("List API keys", "GET", "/keys")
    test_endpoint("List platform keys (admin)", "GET", "/platform-keys")
    
    # 11. Monitoring Endpoints
    print("\n📊 Monitoring Endpoints")
    print("-" * 80)
    test_endpoint("Frontend error logging", "POST", "/monitoring/frontend-error", json={
        "message": "Test error",
        "level": "error"
    })
    test_endpoint("Frontend action logging", "POST", "/monitoring/frontend-action", json={
        "action": "test_action",
        "data": {}
    })
    
    # 12. Onboarding Endpoints
    print("\n🚀 Onboarding Endpoints")
    print("-" * 80)
    test_endpoint("Get onboarding status", "GET", "/onboarding/status")
    
    # 13. Simple Setup Endpoints
    print("\n⚙️  Simple Setup Endpoints")
    print("-" * 80)
    test_endpoint("List setup providers", "GET", "/simple-setup/providers")
    
    # 14. Webhook Endpoints
    print("\n🔔 Webhook Endpoints")
    print("-" * 80)
    test_endpoint("WhatsApp webhook status", "GET", "/webhook/whatsapp/status")
    
    # 15. Chat Endpoints
    print("\n💭 Chat Endpoints")
    print("-" * 80)
    test_endpoint("Chat completions", "POST", "/chat/completions", json={
        "messages": [{"role": "user", "content": "Hello"}],
        "model": "gpt-3.5-turbo"
    })
    
    # 16. AI Chat Endpoints
    print("\n🧠 AI Chat Endpoints")
    print("-" * 80)
    if test_tenant_id:
        test_endpoint("AI chat", "POST", "/ai/chat", json={
            "message": "Hello",
            "tenant_id": test_tenant_id
        })
    
    # Summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    skipped = sum(1 for r in results if r["status"] == "SKIP")
    
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Skipped: {skipped}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    # Save results to file
    with open("endpoint_test_results.json", "w") as f:
        json.dump({
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "success_rate": passed/total*100 if total > 0 else 0
            },
            "results": results,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: endpoint_test_results.json")
    
    # Exit with error code if any tests failed
    if failed > 0:
        print("\n❌ Some tests failed. Please review the results above.")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()

