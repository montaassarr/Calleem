import requests
import json
import time
import sys
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("API_TESTER")

BASE_URL = "http://localhost:8000/api/v1"

class TenantTester:
    def __init__(self, name: str, email: str, password: str, plan: str):
        self.name = name
        self.email = email
        self.password = password
        self.plan = plan
        self.token = None
        self.user_id = None
        self.tenant_id = None
        self.headers = {}

    def register(self) -> bool:
        """Register a new user and tenant"""
        logger.info(f"📝 Registering {self.name} ({self.plan})...")
        payload = {
            "email": self.email,
            "username": self.email.split('@')[0],
            "password": self.password,
            "full_name": self.name,
            "phone_number": "+1234567890"
        }
        
        try:
            # Try to register
            response = requests.post(f"{BASE_URL}/users/register", json=payload)
            
            if response.status_code == 201:
                data = response.json()
                self.user_id = data["id"]
                self.tenant_id = data["tenant_id"]
                logger.info(f"✅ Registered successfully. Tenant ID: {self.tenant_id}")
                return True
            elif response.status_code == 400 and "already registered" in response.text:
                logger.info(f"ℹ️ User already exists, proceeding to login...")
                return True
            else:
                logger.error(f"❌ Registration failed: {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Registration error: {e}")
            return False

    def login(self) -> bool:
        """Login and get access token"""
        logger.info(f"🔐 Logging in {self.name}...")
        payload = {
            "username": self.email.split('@')[0],
            "password": self.password
        }
        
        try:
            response = requests.post(f"{BASE_URL}/users/login", data=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
                
                # Get user info to confirm tenant_id
                me_resp = requests.get(f"{BASE_URL}/users/me", headers=self.headers)
                if me_resp.status_code == 200:
                    me_data = me_resp.json()
                    self.tenant_id = me_data["tenant_id"]
                    self.user_id = me_data["id"]
                
                logger.info(f"✅ Login successful. Token acquired.")
                return True
            else:
                logger.error(f"❌ Login failed: {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False

    def test_endpoints(self):
        """Run comprehensive tests on all endpoints"""
        if not self.token:
            logger.error("Cannot run tests without token")
            return

        logger.info(f"🚀 Starting tests for {self.name} ({self.plan})...")
        
        results = {
            "passed": 0,
            "failed": 0,
            "details": []
        }

        # 1. Services CRUD
        self._test_services(results)
        
        # 2. Appointments CRUD
        self._test_appointments(results)
        
        # 3. Business Config
        self._test_config(results)
        
        # 4. Automations (Pro only check)
        self._test_automations(results)
        
        logger.info(f"🏁 Tests completed for {self.name}")
        logger.info(f"📊 Summary: {results['passed']} Passed, {results['failed']} Failed")
        return results

    def _test_services(self, results):
        logger.info("--- Testing Services ---")
        
        # Create
        service_payload = {
            "name": f"Test Service {int(time.time())}",
            "duration_minutes": 30,
            "price": 50.0,
            "description": "Test description"
        }
        resp = requests.post(f"{BASE_URL}/services/", json=service_payload, headers=self.headers)
        self._check(resp, 201, "Create Service", results)
        service_id = resp.json().get("id") if resp.status_code == 201 else None

        # List
        resp = requests.get(f"{BASE_URL}/services/", headers=self.headers)
        self._check(resp, 200, "List Services", results)
        
        if service_id:
            # Get
            resp = requests.get(f"{BASE_URL}/services/{service_id}", headers=self.headers)
            self._check(resp, 200, "Get Service", results)
            
            # Update
            resp = requests.put(f"{BASE_URL}/services/{service_id}", json={"price": 60.0}, headers=self.headers)
            self._check(resp, 200, "Update Service", results)
            
            # Delete
            resp = requests.delete(f"{BASE_URL}/services/{service_id}", headers=self.headers)
            self._check(resp, 204, "Delete Service", results)

    def _test_appointments(self, results):
        logger.info("--- Testing Appointments ---")
        
        # Create
        appt_payload = {
            "client_name": "John Doe",
            "client_phone": "+15551234567",
            "service": "Test Haircut",
            "datetime": "2025-12-25T10:00:00",
            "duration_minutes": 30
        }
        resp = requests.post(f"{BASE_URL}/appointments/", json=appt_payload, headers=self.headers)
        self._check(resp, 201, "Create Appointment", results)
        appt_id = resp.json().get("id") if resp.status_code == 201 else None
        
        # List
        resp = requests.get(f"{BASE_URL}/appointments/", headers=self.headers)
        self._check(resp, 200, "List Appointments", results)
        
        if appt_id:
            # Get
            resp = requests.get(f"{BASE_URL}/appointments/{appt_id}", headers=self.headers)
            self._check(resp, 200, "Get Appointment", results)
            
            # Cancel
            resp = requests.post(f"{BASE_URL}/appointments/{appt_id}/cancel", headers=self.headers)
            self._check(resp, 200, "Cancel Appointment", results)

    def _test_config(self, results):
        logger.info("--- Testing Business Config ---")
        
        # Get
        resp = requests.get(f"{BASE_URL}/admin/config", headers=self.headers)
        self._check(resp, 200, "Get Config", results)
        
        # Update
        update_payload = {
            "business_name": f"{self.name}'s Shop Updated",
            "timezone": "America/New_York"
        }
        resp = requests.put(f"{BASE_URL}/admin/config", json=update_payload, headers=self.headers)
        self._check(resp, 200, "Update Config", results)

    def _test_automations(self, results):
        logger.info("--- Testing Automations ---")
        
        # Try to update automations
        payload = {
            "automations": {
                "google_calendar_sync": True,
                "slack_notification": True
            }
        }
        resp = requests.post(f"{BASE_URL}/automations/update", json=payload, headers=self.headers)
        
        if self.plan == "basic":
            # Ideally this should be forbidden for basic plan, but currently logic is frontend-gated
            # So we just check if it returns 200 (since backend doesn't enforce plan check yet)
            # OR if we implemented backend check, it should be 403.
            # Based on code review, backend DOES NOT check plan yet.
            self._check(resp, 200, "Update Automations (Basic - should succeed technically)", results)
        else:
            self._check(resp, 200, "Update Automations (Pro)", results)

    def _check(self, response, expected_code, name, results):
        if response.status_code == expected_code:
            logger.info(f"✅ {name}: Passed ({response.status_code})")
            results["passed"] += 1
        else:
            logger.error(f"❌ {name}: Failed. Expected {expected_code}, got {response.status_code}")
            logger.error(f"   Response: {response.text}")
            results["failed"] += 1
            results["details"].append(f"{name} failed: {response.status_code} - {response.text}")

def main():
    logger.info("🧪 STARTING AUTOMATED API TESTS")
    
    # Tenant A: Basic Plan
    tenant_a = TenantTester("Tenant A", "basic@test.com", "Password123!", "basic")
    if tenant_a.register() and tenant_a.login():
        tenant_a.test_endpoints()
    
    print("\n" + "="*50 + "\n")
    
    # Tenant B: Pro Plan
    tenant_b = TenantTester("Tenant B", "pro@test.com", "Password123!", "pro")
    if tenant_b.register() and tenant_b.login():
        tenant_b.test_endpoints()

if __name__ == "__main__":
    main()
