#!/usr/bin/env python3
"""
Comprehensive System Test Script for AI Receptionist
Tests all endpoints and core functionality
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any
import sys

# Configuration
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")

def print_test(test_name: str):
    """Print test name"""
    print(f"{Colors.BLUE}[TEST]{Colors.END} {test_name}...", end=" ")

def print_success(message: str = "PASSED"):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}✗ FAILED: {message}{Colors.END}")

def print_info(message: str):
    """Print info message"""
    print(f"{Colors.YELLOW}ℹ {message}{Colors.END}")

def print_data(label: str, data: Any):
    """Print formatted data"""
    print(f"  {Colors.BOLD}{label}:{Colors.END} {json.dumps(data, indent=2)}")

# Store tokens and IDs for reuse
test_data = {
    'admin_token': None,
    'user_id': None,
    'service_ids': [],
    'appointment_ids': [],
}

def test_health_check():
    """Test 1: Health Check Endpoint"""
    print_test("Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success()
            print_data("Status", data.get('status'))
            print_data("Database", data.get('database'))
            return True
        else:
            print_error(f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(str(e))
        return False

def test_root_endpoint():
    """Test 2: Root Endpoint"""
    print_test("Root Endpoint")
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success()
            print_data("Message", data.get('message'))
            return True
        else:
            print_error(f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(str(e))
        return False

def test_create_admin_user():
    """Test 3: Create Admin User"""
    print_test("Create Admin User")
    try:
        payload = {
            "email": f"admin_{int(time.time())}@barbershop.com",
            "username": f"admin_{int(time.time())}",
            "full_name": "Test Admin User",
            "password": "SecurePassword123!",
            "role": "admin"
        }
        response = requests.post(f"{API_V1}/users/register", json=payload, timeout=5)
        
        if response.status_code in [200, 201]:  # Accept both 200 and 201 Created
            data = response.json()
            test_data['user_id'] = data.get('id')
            print_success()
            print_data("User ID", data.get('id'))
            print_data("Username", data.get('username'))
            return True
        elif response.status_code == 400 and "already registered" in response.text:
            print_info("User already exists, continuing...")
            return True
        else:
            print_error(f"Status code: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_error(str(e))
        return False

def test_user_login():
    """Test 4: User Login"""
    print_test("User Login")
    try:
        # Use the newly created user or fallback to default
        username = "admin"
        password = "SecurePassword123!"
        
        payload = {
            "username": username,
            "password": password
        }
        
        response = requests.post(
            f"{API_V1}/users/login",
            data=payload,  # OAuth2 expects form data
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            test_data['admin_token'] = data.get('access_token')
            print_success()
            print_data("Token Type", data.get('token_type'))
            print_info(f"Access Token: {data.get('access_token')[:50]}...")
            return True
        else:
            print_error(f"Status code: {response.status_code}, Response: {response.text}")
            # Try creating default admin
            print_info("Creating default admin user...")
            create_payload = {
                "email": "admin@barbershop.com",
                "username": "admin",
                "full_name": "Admin User",
                "password": "SecurePassword123!",
                "role": "admin"
            }
            requests.post(f"{API_V1}/users/register", json=create_payload)
            # Retry login
            response = requests.post(f"{API_V1}/users/login", data=payload, timeout=5)
            if response.status_code == 200:
                data = response.json()
                test_data['admin_token'] = data.get('access_token')
                print_success("Login after user creation")
                return True
            return False
    except Exception as e:
        print_error(str(e))
        return False

def test_create_service():
    """Test 5: Create Service"""
    print_test("Create Service")
    try:
        services = [
            {
                "name": "Haircut",
                "description": "Classic men's haircut with styling",
                "duration_minutes": 30,
                "price": 25.00,
                "active": True
            },
            {
                "name": "Beard Trim",
                "description": "Professional beard trim and shape",
                "duration_minutes": 20,
                "price": 15.00,
                "active": True
            },
            {
                "name": "Hot Shave",
                "description": "Traditional hot towel shave",
                "duration_minutes": 25,
                "price": 20.00,
                "active": True
            }
        ]
        
        for service in services:
            response = requests.post(
                f"{API_V1}/services/",
                json=service,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                test_data['service_ids'].append(data.get('id'))
        
        print_success(f"Created {len(test_data['service_ids'])} services")
        return True
    except Exception as e:
        print_error(str(e))
        return False

def test_list_services():
    """Test 6: List All Services"""
    print_test("List All Services")
    try:
        response = requests.get(f"{API_V1}/services/", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Found {len(data)} services")
            for service in data[:3]:  # Show first 3
                print(f"  - {service.get('name')}: ${service.get('price')} ({service.get('duration_minutes')} min)")
            return True
        else:
            print_error(f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(str(e))
        return False

def test_create_appointment():
    """Test 7: Create Appointment"""
    print_test("Create Appointment")
    try:
        tomorrow = datetime.now() + timedelta(days=1)
        appointment_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
        
        payload = {
            "client_name": "John Doe",
            "client_phone": "+1234567890",
            "service": "Haircut",
            "datetime": appointment_time.isoformat(),
            "notes": "First time customer, prefers short on sides"
        }
        
        response = requests.post(
            f"{API_V1}/appointments/",
            json=payload,
            timeout=5
        )
        
        if response.status_code in [200, 201]:  # Accept both 200 and 201 Created
            data = response.json()
            test_data['appointment_ids'].append(data.get('id'))
            print_success()
            print_data("Appointment ID", data.get('id'))
            print_data("Customer", data.get('client_name'))
            print_data("Service", data.get('service'))
            print_data("Time", data.get('datetime'))
            return True
        else:
            print_error(f"Status code: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_error(str(e))
        return False

def test_list_appointments():
    """Test 8: List All Appointments"""
    print_test("List All Appointments")
    try:
        response = requests.get(f"{API_V1}/appointments/", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Found {len(data)} appointments")
            for apt in data[:3]:  # Show first 3
                print(f"  - {apt.get('client_name')} | {apt.get('service')} | {apt.get('status')}")
            return True
        else:
            print_error(f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(str(e))
        return False

def test_get_appointment_by_id():
    """Test 9: Get Specific Appointment"""
    print_test("Get Appointment by ID")
    try:
        if not test_data['appointment_ids']:
            print_info("No appointments to test, skipping...")
            return True
            
        apt_id = test_data['appointment_ids'][0]
        response = requests.get(f"{API_V1}/appointments/{apt_id}", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success()
            print_data("Customer", data.get('client_name'))
            print_data("Phone", data.get('client_phone'))
            return True
        else:
            print_error(f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(str(e))
        return False

def test_update_appointment():
    """Test 10: Update Appointment Status"""
    print_test("Update Appointment Status")
    try:
        if not test_data['appointment_ids']:
            print_info("No appointments to test, skipping...")
            return True
            
        apt_id = test_data['appointment_ids'][0]
        payload = {
            "status": "confirmed"
        }
        
        response = requests.put(
            f"{API_V1}/appointments/{apt_id}",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success()
            print_data("New Status", data.get('status'))
            return True
        else:
            print_error(f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(str(e))
        return False

def test_appointment_stats():
    """Test 11: Get Appointment Statistics"""
    print_test("Get Appointment Statistics")
    try:
        response = requests.get(f"{API_V1}/appointments/stats/summary", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success()
            print_data("Total Appointments", data.get('total_appointments'))
            print_data("By Status", data.get('by_status'))
            return True
        else:
            print_error(f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(str(e))
        return False

def test_webhook_sms():
    """Test 12: SMS Webhook (Simulated)"""
    print_test("SMS Webhook (Simulated)")
    try:
        payload = {
            "From": "+1234567890",
            "Body": "Hello, I want to book a haircut",
            "MessageSid": f"SM{int(time.time())}",
            "AccountSid": "ACxxxxxx"
        }
        
        response = requests.post(
            f"{API_V1}/webhook/sms",
            data=payload,  # Twilio sends form data
            timeout=10
        )
        
        if response.status_code == 200:
            print_success()
            print_info("Response (TwiML):")
            print(f"  {response.text[:200]}...")
            return True
        else:
            print_error(f"Status code: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_error(str(e))
        return False

def test_ngrok_status():
    """Test 13: Check ngrok Status"""
    print_test("Check ngrok Status")
    try:
        response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get('tunnels', [])
            if tunnels:
                public_url = tunnels[0].get('public_url')
                print_success()
                print_data("Public URL", public_url)
                print_info(f"Use this URL for Twilio webhooks: {public_url}/api/v1/webhook/sms")
                return True
            else:
                print_error("No active tunnels found")
                return False
        else:
            print_error("ngrok API not accessible. Is ngrok running?")
            return False
    except Exception as e:
        print_error(f"ngrok not running or not accessible: {str(e)}")
        return False

def run_all_tests():
    """Run all tests in sequence"""
    print_header("AI RECEPTIONIST - COMPREHENSIVE SYSTEM TEST")
    
    tests = [
        ("Server Health", test_health_check),
        ("Root Endpoint", test_root_endpoint),
        ("Create Admin User", test_create_admin_user),
        ("User Login", test_user_login),
        ("Create Services", test_create_service),
        ("List Services", test_list_services),
        ("Create Appointment", test_create_appointment),
        ("List Appointments", test_list_appointments),
        ("Get Appointment by ID", test_get_appointment_by_id),
        ("Update Appointment", test_update_appointment),
        ("Appointment Statistics", test_appointment_stats),
        ("SMS Webhook", test_webhook_sms),
        ("ngrok Status", test_ngrok_status),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            time.sleep(0.5)  # Small delay between tests
        except Exception as e:
            print_error(f"Unexpected error in {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n{Colors.BOLD}Results:{Colors.END}")
    for test_name, result in results:
        status = f"{Colors.GREEN}✓ PASSED{Colors.END}" if result else f"{Colors.RED}✗ FAILED{Colors.END}"
        print(f"  {test_name.ljust(30)} {status}")
    
    print(f"\n{Colors.BOLD}Overall:{Colors.END} {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! System is working perfectly!{Colors.END}")
        return 0
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ Some tests failed. Check the output above for details.{Colors.END}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{Colors.RED}Fatal error: {str(e)}{Colors.END}")
        sys.exit(1)
