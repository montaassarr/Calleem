"""
Complete Client Flow Test
=========================
Tests the full user journey:
1. Sign up (creates user + tenant + auto-provisions Vapi assistant)
2. Login
3. Check Vapi assistant was created
4. Create services
5. Check availability
6. Book appointment
7. Verify appointment created
8. Test call simulation (Vapi webhook)

Run: python -m pytest tests/test_client_flow.py -v -s
Or:  python tests/test_client_flow.py (standalone)
"""

import asyncio
import httpx
import os
import sys
from datetime import datetime, timedelta
from typing import Optional
import random
import string

# Configuration
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_PREFIX = "/api/v1"

# Test data
TEST_EMAIL = f"test_{random.randint(1000, 9999)}@example.com"
TEST_USERNAME = f"testuser_{random.randint(1000, 9999)}"
TEST_PASSWORD = "SecurePassword123!"
TEST_BUSINESS = f"Test Business {random.randint(1000, 9999)}"


class Colors:
    """ANSI colors for terminal output"""
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def log_step(step: int, message: str):
    print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}Step {step}: {message}{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")


def log_success(message: str):
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")


def log_error(message: str):
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")


def log_warning(message: str):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")


def log_info(message: str):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.RESET}")


class ClientFlowTest:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.api_url = f"{base_url}{API_PREFIX}"
        self.token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.tenant_id: Optional[str] = None
        self.vapi_assistant_id: Optional[str] = None
        self.service_id: Optional[str] = None
        self.appointment_id: Optional[str] = None
        self.results = []

    async def run_all_tests(self):
        """Run the complete client flow test"""
        print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}🧪 AI RECEPTIONIST - COMPLETE CLIENT FLOW TEST{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"API URL: {self.api_url}")
        print(f"Test User: {TEST_EMAIL}")
        print(f"Test Business: {TEST_BUSINESS}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Step 0: Health Check
            await self.test_health_check(client)
            
            # Step 1: Register
            await self.test_register(client)
            
            # Step 2: Login
            await self.test_login(client)
            
            # Step 3: Verify Vapi Assistant Created
            await self.test_vapi_assistant_created(client)
            
            # Step 4: Get/Create Services
            await self.test_services(client)
            
            # Step 5: Check Availability
            await self.test_check_availability(client)
            
            # Step 6: Book Appointment
            await self.test_book_appointment(client)
            
            # Step 7: Verify Appointment
            await self.test_verify_appointment(client)
            
            # Step 8: Simulate Vapi Call (webhook test)
            await self.test_vapi_webhook(client)
            
            # Step 9: Check Conversations
            await self.test_conversations(client)
            
            # Cleanup (optional)
            # await self.cleanup(client)
        
        # Print Summary
        self.print_summary()

    async def test_health_check(self, client: httpx.AsyncClient):
        """Step 0: Check API is running"""
        log_step(0, "Health Check")
        
        try:
            response = await client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                log_success(f"API is healthy: {data.get('status', 'ok')}")
                self.results.append(("Health Check", True, None))
            else:
                log_error(f"Health check failed: {response.status_code}")
                self.results.append(("Health Check", False, f"Status {response.status_code}"))
        except Exception as e:
            log_error(f"Cannot connect to API: {e}")
            self.results.append(("Health Check", False, str(e)))
            raise SystemExit("API not reachable. Start the server first.")

    async def test_register(self, client: httpx.AsyncClient):
        """Step 1: Register new user (creates tenant + Vapi assistant)"""
        log_step(1, "User Registration")
        
        payload = {
            "email": TEST_EMAIL,
            "username": TEST_USERNAME,
            "full_name": "Test User",
            "password": TEST_PASSWORD,
            "business_name": TEST_BUSINESS
        }
        
        log_info(f"Registering: {TEST_EMAIL}")
        
        try:
            response = await client.post(
                f"{self.api_url}/users/register",
                json=payload
            )
            
            if response.status_code == 201:
                data = response.json()
                self.token = data.get("access_token")
                log_success("User registered successfully")
                log_info(f"Token received: {self.token[:50]}...")
                self.results.append(("Registration", True, None))
            else:
                error = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                log_error(f"Registration failed: {response.status_code} - {error}")
                self.results.append(("Registration", False, str(error)))
        except Exception as e:
            log_error(f"Registration error: {e}")
            self.results.append(("Registration", False, str(e)))

    async def test_login(self, client: httpx.AsyncClient):
        """Step 2: Login and get new token"""
        log_step(2, "User Login")
        
        try:
            response = await client.post(
                f"{self.api_url}/users/login",
                data={
                    "username": TEST_USERNAME,
                    "password": TEST_PASSWORD
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                log_success("Login successful")
                
                # Decode token to get tenant_id
                import base64
                import json
                payload = self.token.split(".")[1]
                # Add padding
                payload += "=" * (4 - len(payload) % 4)
                decoded = json.loads(base64.urlsafe_b64decode(payload))
                self.tenant_id = decoded.get("tenant_id")
                self.user_id = decoded.get("sub")
                log_info(f"Tenant ID: {self.tenant_id}")
                log_info(f"User ID: {self.user_id}")
                self.results.append(("Login", True, None))
            else:
                log_error(f"Login failed: {response.status_code}")
                self.results.append(("Login", False, f"Status {response.status_code}"))
        except Exception as e:
            log_error(f"Login error: {e}")
            self.results.append(("Login", False, str(e)))

    async def test_vapi_assistant_created(self, client: httpx.AsyncClient):
        """Step 3: Verify Vapi assistant was auto-created"""
        log_step(3, "Verify Vapi Assistant")
        
        if not self.token:
            log_warning("Skipping - no token")
            self.results.append(("Vapi Assistant", False, "No token"))
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            # Check tenant for vapi_assistant_id
            response = await client.get(
                f"{self.api_url}/tenants/me",
                headers=headers
            )
            
            if response.status_code == 200:
                tenant = response.json()
                self.vapi_assistant_id = tenant.get("vapi_assistant_id")
                is_configured = tenant.get("is_configured", False)
                
                if self.vapi_assistant_id:
                    log_success(f"Vapi Assistant created: {self.vapi_assistant_id}")
                    log_info(f"Is Configured: {is_configured}")
                    self.results.append(("Vapi Assistant", True, None))
                else:
                    log_warning("Vapi Assistant not created (VAPI_API_KEY may not be set)")
                    self.results.append(("Vapi Assistant", False, "No vapi_assistant_id"))
            else:
                log_error(f"Failed to get tenant: {response.status_code}")
                self.results.append(("Vapi Assistant", False, f"Status {response.status_code}"))
        except Exception as e:
            log_error(f"Error checking Vapi assistant: {e}")
            self.results.append(("Vapi Assistant", False, str(e)))

    async def test_services(self, client: httpx.AsyncClient):
        """Step 4: Create or list services"""
        log_step(4, "Services Setup")
        
        if not self.token:
            log_warning("Skipping - no token")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            # First try to list existing services
            response = await client.get(
                f"{self.api_url}/services/",
                headers=headers
            )
            
            if response.status_code == 200:
                services = response.json()
                if services:
                    log_info(f"Found {len(services)} existing services")
                    self.service_id = services[0].get("id") or str(services[0].get("_id"))
                    log_success(f"Using service: {services[0].get('name')}")
                    self.results.append(("Services", True, None))
                    return
            
            # Create a service if none exist
            log_info("Creating default service...")
            service_payload = {
                "name": "General Consultation",
                "description": "Standard consultation service",
                "duration_minutes": 30,
                "price": 50.0,
                "active": True
            }
            
            response = await client.post(
                f"{self.api_url}/services/",
                json=service_payload,
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                service = response.json()
                self.service_id = service.get("id") or str(service.get("_id"))
                log_success(f"Service created: {service.get('name')}")
                self.results.append(("Services", True, None))
            else:
                log_error(f"Failed to create service: {response.status_code}")
                self.results.append(("Services", False, f"Status {response.status_code}"))
        except Exception as e:
            log_error(f"Services error: {e}")
            self.results.append(("Services", False, str(e)))

    async def test_check_availability(self, client: httpx.AsyncClient):
        """Step 5: Check appointment availability"""
        log_step(5, "Check Availability")
        
        if not self.token:
            log_warning("Skipping - no token")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Check tomorrow at 10:00
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        try:
            response = await client.get(
                f"{self.api_url}/appointments/availability/check",
                params={"date": tomorrow, "time": "10:00"},
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                available = data.get("available", data.get("slot_available", False))
                log_success(f"Availability check: {tomorrow} 10:00 - {'Available' if available else 'Not Available'}")
                log_info(f"Response: {data}")
                self.results.append(("Check Availability", True, None))
            else:
                log_error(f"Availability check failed: {response.status_code}")
                self.results.append(("Check Availability", False, f"Status {response.status_code}"))
        except Exception as e:
            log_error(f"Availability error: {e}")
            self.results.append(("Check Availability", False, str(e)))

    async def test_book_appointment(self, client: httpx.AsyncClient):
        """Step 6: Book an appointment"""
        log_step(6, "Book Appointment")
        
        if not self.token:
            log_warning("Skipping - no token")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Book tomorrow at 10:00
        tomorrow = datetime.now() + timedelta(days=1)
        appointment_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
        
        payload = {
            "client_name": "John Doe",
            "client_phone": "+1234567890",
            "service": "General Consultation",
            "datetime": appointment_time.isoformat(),
            "duration_minutes": 30,
            "notes": "Test appointment from client flow test"
        }
        
        if self.service_id:
            payload["service_id"] = self.service_id
        
        try:
            response = await client.post(
                f"{self.api_url}/appointments/",
                json=payload,
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                appointment = response.json()
                self.appointment_id = appointment.get("id") or str(appointment.get("_id"))
                log_success(f"Appointment booked!")
                log_info(f"ID: {self.appointment_id}")
                log_info(f"Client: {appointment.get('client_name')}")
                log_info(f"Time: {appointment.get('datetime') or appointment.get('start_time')}")
                log_info(f"Status: {appointment.get('status')}")
                self.results.append(("Book Appointment", True, None))
            else:
                error = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                log_error(f"Booking failed: {response.status_code} - {error}")
                self.results.append(("Book Appointment", False, str(error)))
        except Exception as e:
            log_error(f"Booking error: {e}")
            self.results.append(("Book Appointment", False, str(e)))

    async def test_verify_appointment(self, client: httpx.AsyncClient):
        """Step 7: Verify appointment was created"""
        log_step(7, "Verify Appointment")
        
        if not self.token:
            log_warning("Skipping - no token")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = await client.get(
                f"{self.api_url}/appointments/",
                headers=headers
            )
            
            if response.status_code == 200:
                appointments = response.json()
                log_success(f"Found {len(appointments)} appointments")
                
                # Find our test appointment
                test_appt = None
                for appt in appointments:
                    appt_id = appt.get("id") or str(appt.get("_id"))
                    if appt_id == self.appointment_id:
                        test_appt = appt
                        break
                
                if test_appt:
                    log_success("Test appointment verified!")
                    log_info(f"  Client: {test_appt.get('client_name')}")
                    log_info(f"  Status: {test_appt.get('status')}")
                    self.results.append(("Verify Appointment", True, None))
                else:
                    log_warning("Test appointment not found in list")
                    self.results.append(("Verify Appointment", False, "Not in list"))
            else:
                log_error(f"Failed to list appointments: {response.status_code}")
                self.results.append(("Verify Appointment", False, f"Status {response.status_code}"))
        except Exception as e:
            log_error(f"Verification error: {e}")
            self.results.append(("Verify Appointment", False, str(e)))

    async def test_vapi_webhook(self, client: httpx.AsyncClient):
        """Step 8: Simulate Vapi call webhook"""
        log_step(8, "Vapi Webhook Test (Call Simulation)")
        
        if not self.tenant_id:
            log_warning("Skipping - no tenant_id")
            return
        
        # Simulate a function call from Vapi
        webhook_payload = {
            "message": {
                "type": "function-call",
                "functionCall": {
                    "name": "checkAvailability",
                    "parameters": {
                        "date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
                    }
                },
                "call": {
                    "id": f"test-call-{random.randint(1000, 9999)}",
                    "assistantId": self.vapi_assistant_id or "test-assistant",
                    "customer": {
                        "number": "+1234567890"
                    }
                }
            }
        }
        
        try:
            # The webhook endpoint
            response = await client.post(
                f"{self.api_url}/vapi/webhook/{self.tenant_id}",
                json=webhook_payload
            )
            
            if response.status_code == 200:
                data = response.json()
                log_success("Webhook processed successfully!")
                log_info(f"Response: {data}")
                self.results.append(("Vapi Webhook", True, None))
            else:
                error = response.text
                log_warning(f"Webhook response: {response.status_code} - {error}")
                self.results.append(("Vapi Webhook", False, f"Status {response.status_code}"))
        except Exception as e:
            log_error(f"Webhook error: {e}")
            self.results.append(("Vapi Webhook", False, str(e)))

    async def test_conversations(self, client: httpx.AsyncClient):
        """Step 9: Check conversations"""
        log_step(9, "Check Conversations")
        
        if not self.token:
            log_warning("Skipping - no token")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = await client.get(
                f"{self.api_url}/conversations/",
                headers=headers
            )
            
            if response.status_code == 200:
                conversations = response.json()
                log_success(f"Found {len(conversations)} conversations")
                self.results.append(("Conversations", True, None))
            else:
                log_warning(f"Conversations: {response.status_code}")
                self.results.append(("Conversations", False, f"Status {response.status_code}"))
        except Exception as e:
            log_error(f"Conversations error: {e}")
            self.results.append(("Conversations", False, str(e)))

    async def cleanup(self, client: httpx.AsyncClient):
        """Optional cleanup - delete test data"""
        log_step(10, "Cleanup (Optional)")
        
        if not self.token:
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Delete appointment
        if self.appointment_id:
            try:
                await client.delete(
                    f"{self.api_url}/appointments/{self.appointment_id}",
                    headers=headers
                )
                log_info(f"Deleted appointment: {self.appointment_id}")
            except:
                pass

    def print_summary(self):
        """Print test results summary"""
        print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}📊 TEST RESULTS SUMMARY{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")
        
        passed = 0
        failed = 0
        
        for test_name, success, error in self.results:
            if success:
                print(f"  {Colors.GREEN}✅ {test_name}{Colors.RESET}")
                passed += 1
            else:
                print(f"  {Colors.RED}❌ {test_name}: {error}{Colors.RESET}")
                failed += 1
        
        print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
        total = passed + failed
        if failed == 0:
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! ({passed}/{total}){Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}Results: {passed}/{total} passed, {failed} failed{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")
        
        # Return test data for further use
        print(f"\n{Colors.CYAN}Test Data Created:{Colors.RESET}")
        print(f"  User ID: {self.user_id}")
        print(f"  Tenant ID: {self.tenant_id}")
        print(f"  Vapi Assistant: {self.vapi_assistant_id}")
        print(f"  Appointment ID: {self.appointment_id}")
        print(f"\n  Login: {TEST_EMAIL} / {TEST_PASSWORD}")


async def main():
    """Run the test"""
    # Check for custom base URL
    base_url = sys.argv[1] if len(sys.argv) > 1 else BASE_URL
    
    test = ClientFlowTest(base_url)
    await test.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
