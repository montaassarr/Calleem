"""
Comprehensive Backend and Database Test Scenarios
Testing with phone number: +216 92 034 689
"""

import requests
import json
from datetime import datetime, timedelta
import time

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"
PHONE_NUMBER = "+21692034689"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.YELLOW}ℹ {text}{Colors.RESET}")

def test_health_check():
    """Test 1: Health Check"""
    print_header("TEST 1: Backend Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Backend is running: {data}")
            return True
        else:
            print_error(f"Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Backend is not responding: {e}")
        return False

def test_database_connection():
    """Test 2: Database Connection"""
    print_header("TEST 2: Database Connection")
    
    try:
        # Test getting appointments (will fail if DB is down)
        response = requests.get(f"{API_URL}/appointments/", timeout=5)
        print_success(f"Database connection OK - Status: {response.status_code}")
        
        if response.status_code == 200:
            appointments = response.json()
            print_info(f"Current appointments in database: {len(appointments)}")
            return True
        return response.status_code == 200
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        return False

def test_create_appointment():
    """Test 3: Create Appointment"""
    print_header("TEST 3: Create Appointment")
    
    # Calculate appointment time (tomorrow at 2 PM)
    tomorrow = datetime.now() + timedelta(days=1)
    appointment_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    
    appointment_data = {
        "client_name": "Montassar Test",
        "client_phone": PHONE_NUMBER,
        "service": "Haircut",
        "appointment_time": appointment_time.isoformat(),
        "status": "confirmed",
        "notes": "Test appointment created by automated test"
    }
    
    try:
        response = requests.post(
            f"{API_URL}/appointments/",
            json=appointment_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print_success(f"Appointment created successfully!")
            print_info(f"Appointment ID: {data.get('id', 'N/A')}")
            print_info(f"Client: {data.get('client_name')}")
            print_info(f"Phone: {data.get('client_phone')}")
            print_info(f"Service: {data.get('service')}")
            print_info(f"Time: {data.get('appointment_time')}")
            return data.get('id')
        else:
            print_error(f"Failed to create appointment: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error creating appointment: {e}")
        return None

def test_get_appointments():
    """Test 4: Get All Appointments"""
    print_header("TEST 4: Get All Appointments")
    
    try:
        response = requests.get(f"{API_URL}/appointments/", timeout=5)
        
        if response.status_code == 200:
            appointments = response.json()
            print_success(f"Retrieved {len(appointments)} appointments")
            
            for i, apt in enumerate(appointments[-3:], 1):  # Show last 3
                print(f"\n  Appointment {i}:")
                print(f"    ID: {apt.get('id')}")
                print(f"    Name: {apt.get('client_name')}")
                print(f"    Phone: {apt.get('client_phone')}")
                print(f"    Service: {apt.get('service')}")
                print(f"    Time: {apt.get('appointment_time')}")
                print(f"    Status: {apt.get('status')}")
            
            return appointments
        else:
            print_error(f"Failed to get appointments: {response.status_code}")
            return []
    except Exception as e:
        print_error(f"Error getting appointments: {e}")
        return []

def test_get_appointment_by_id(appointment_id):
    """Test 5: Get Specific Appointment"""
    print_header("TEST 5: Get Specific Appointment")
    
    if not appointment_id:
        print_error("No appointment ID provided")
        return None
    
    try:
        response = requests.get(f"{API_URL}/appointments/{appointment_id}", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Appointment retrieved successfully")
            print_info(f"Name: {data.get('client_name')}")
            print_info(f"Phone: {data.get('client_phone')}")
            print_info(f"Service: {data.get('service')}")
            return data
        else:
            print_error(f"Failed to get appointment: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Error getting appointment: {e}")
        return None

def test_update_appointment(appointment_id):
    """Test 6: Update Appointment"""
    print_header("TEST 6: Update Appointment")
    
    if not appointment_id:
        print_error("No appointment ID provided")
        return False
    
    update_data = {
        "status": "completed",
        "notes": "Test appointment - Updated by automated test"
    }
    
    try:
        response = requests.patch(
            f"{API_URL}/appointments/{appointment_id}",
            json=update_data,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Appointment updated successfully")
            print_info(f"New status: {data.get('status')}")
            print_info(f"Notes: {data.get('notes')}")
            return True
        else:
            print_error(f"Failed to update appointment: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error updating appointment: {e}")
        return False

def test_phone_number_search():
    """Test 7: Search by Phone Number"""
    print_header("TEST 7: Search Appointments by Phone Number")
    
    try:
        # Get all appointments and filter by phone
        response = requests.get(f"{API_URL}/appointments/", timeout=5)
        
        if response.status_code == 200:
            all_appointments = response.json()
            my_appointments = [apt for apt in all_appointments if apt.get('client_phone') == PHONE_NUMBER]
            
            print_success(f"Found {len(my_appointments)} appointments for {PHONE_NUMBER}")
            
            for i, apt in enumerate(my_appointments, 1):
                print(f"\n  Appointment {i}:")
                print(f"    Service: {apt.get('service')}")
                print(f"    Time: {apt.get('appointment_time')}")
                print(f"    Status: {apt.get('status')}")
            
            return my_appointments
        else:
            print_error(f"Search failed: {response.status_code}")
            return []
    except Exception as e:
        print_error(f"Error searching appointments: {e}")
        return []

def test_delete_appointment(appointment_id):
    """Test 8: Delete Appointment"""
    print_header("TEST 8: Delete Appointment")
    
    if not appointment_id:
        print_error("No appointment ID provided")
        return False
    
    try:
        response = requests.delete(f"{API_URL}/appointments/{appointment_id}", timeout=5)
        
        if response.status_code in [200, 204]:
            print_success("Appointment deleted successfully")
            return True
        else:
            print_error(f"Failed to delete appointment: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error deleting appointment: {e}")
        return False

def test_webhook_verification():
    """Test 9: WhatsApp Webhook Verification"""
    print_header("TEST 9: WhatsApp Webhook Verification")
    
    try:
        params = {
            "hub.mode": "subscribe",
            "hub.verify_token": "verifytokenmeta",
            "hub.challenge": "test_challenge_123"
        }
        
        response = requests.get(f"{API_URL}/webhook/sms", params=params, timeout=5)
        
        if response.status_code == 200 and response.text == "test_challenge_123":
            print_success("Webhook verification endpoint working correctly")
            return True
        else:
            print_error(f"Webhook verification failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error testing webhook: {e}")
        return False

def test_services_endpoint():
    """Test 10: Get Available Services"""
    print_header("TEST 10: Available Services")
    
    try:
        response = requests.get(f"{API_URL}/services/", timeout=5)
        
        if response.status_code == 200:
            services = response.json()
            print_success(f"Retrieved {len(services)} services")
            
            for service in services:
                print(f"  • {service.get('name')} - ${service.get('price', 0)} ({service.get('duration', 30)} min)")
            
            return services
        else:
            print_error(f"Failed to get services: {response.status_code}")
            return []
    except Exception as e:
        print_error(f"Error getting services: {e}")
        return []

def run_all_tests():
    """Run all test scenarios"""
    print(f"\n{Colors.BLUE}{'='*80}")
    print(f"  COMPREHENSIVE BACKEND & DATABASE TEST SUITE")
    print(f"  Testing with phone: {PHONE_NUMBER}")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}{Colors.RESET}\n")
    
    results = {}
    appointment_id = None
    
    # Wait for backend to be ready
    print_info("Waiting for backend to be ready...")
    time.sleep(2)
    
    # Run tests
    results['health'] = test_health_check()
    results['database'] = test_database_connection()
    results['services'] = test_services_endpoint()
    
    if results['health'] and results['database']:
        appointment_id = test_create_appointment()
        results['create'] = appointment_id is not None
        
        results['get_all'] = test_get_appointments()
        
        if appointment_id:
            results['get_one'] = test_get_appointment_by_id(appointment_id)
            results['update'] = test_update_appointment(appointment_id)
        
        results['search'] = test_phone_number_search()
        results['webhook'] = test_webhook_verification()
        
        # Clean up - delete test appointment
        if appointment_id:
            results['delete'] = test_delete_appointment(appointment_id)
    
    # Print summary
    print_header("TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {Colors.GREEN}{passed_tests}{Colors.RESET}")
    print(f"Failed: {Colors.RED}{total_tests - passed_tests}{Colors.RESET}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%\n")
    
    if passed_tests == total_tests:
        print(f"{Colors.GREEN}🎉 ALL TESTS PASSED!{Colors.RESET}\n")
    else:
        print(f"{Colors.YELLOW}⚠ Some tests failed - check details above{Colors.RESET}\n")
    
    return results

if __name__ == "__main__":
    run_all_tests()
