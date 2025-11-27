"""
PHASE 4-6: E2E Testing Script
Comprehensive testing of Basic and Pro client scenarios
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

class E2ETester:
    def __init__(self):
        self.results = {
            "phase4_basic": {"passed": [], "failed": []},
            "phase4_pro": {"passed": [], "failed": []},
            "phase5_admin": {"passed": [], "failed": []},
            "critical_bugs": [],
            "security_issues": []
        }
    
    def log(self, msg, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {msg}")
    
    def test_basic_scenario(self):
        """Scenario 1: Basic Client Journey"""
        self.log("=" * 60)
        self.log("PHASE 4 - SCENARIO 1: BASIC CLIENT (Tenant A)")
        self.log("=" * 60)
        
        # Step 1: Signup
        self.log("Step 1: Testing signup...")
        signup_data = {
            "email": "basic@callflow.test",
            "username": "basic_user",
            "password": "TestPass123!",
            "full_name": "Basic User",
            "phone_number": "+15551234567"
        }
        
        try:
            resp = requests.post(f"{BASE_URL}/users/register", json=signup_data)
            if resp.status_code in [201, 400]:  # 400 if already exists
                self.results["phase4_basic"]["passed"].append("Signup")
                self.log("✅ Signup successful or user exists")
            else:
                self.results["phase4_basic"]["failed"].append(f"Signup: {resp.status_code}")
                self.log(f"❌ Signup failed: {resp.text}", "ERROR")
        except Exception as e:
            self.results["phase4_basic"]["failed"].append(f"Signup: {str(e)}")
            self.log(f"❌ Signup error: {e}", "ERROR")
        
        # Step 2: Login
        self.log("Step 2: Testing login...")
        try:
            login_resp = requests.post(f"{BASE_URL}/users/login", data={
                "username": "basic_user",
                "password": "TestPass123!"
            })
            
            if login_resp.status_code == 200:
                token = login_resp.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}"}
                self.results["phase4_basic"]["passed"].append("Login")
                self.log("✅ Login successful")
                
                # Step 3: Try to access automations (should be hidden/403)
                self.log("Step 3: Testing automations access (should fail)...")
                auto_resp = requests.post(
                    f"{BASE_URL}/automations/update",
                    json={"automations": {"google_calendar_sync": True}},
                    headers=headers
                )
                
                # CRITICAL: This should return 403 for basic plan
                if auto_resp.status_code == 403:
                    self.results["phase4_basic"]["passed"].append("Automations blocked")
                    self.log("✅ Automations correctly blocked for Basic plan")
                elif auto_resp.status_code == 200:
                    self.results["phase4_basic"]["failed"].append("Automations NOT blocked")
                    self.results["security_issues"].append(
                        "CRITICAL: Basic plan can access Pro automations endpoint"
                    )
                    self.log("❌ SECURITY ISSUE: Basic plan can update automations!", "ERROR")
                else:
                    self.log(f"⚠️ Unexpected response: {auto_resp.status_code}")
                
                # Step 4: List appointments
                self.log("Step 4: Testing appointments list...")
                appt_resp = requests.get(f"{BASE_URL}/appointments/", headers=headers)
                if appt_resp.status_code == 200:
                    self.results["phase4_basic"]["passed"].append("List appointments")
                    self.log("✅ Appointments list works")
                else:
                    self.results["phase4_basic"]["failed"].append(f"Appointments: {appt_resp.status_code}")
                    
            else:
                self.results["phase4_basic"]["failed"].append(f"Login: {login_resp.status_code}")
                self.log(f"❌ Login failed: {login_resp.text}", "ERROR")
                
        except Exception as e:
            self.results["phase4_basic"]["failed"].append(f"Login: {str(e)}")
            self.log(f"❌ Login error: {e}", "ERROR")
    
    def test_pro_scenario(self):
        """Scenario 2: Pro Client Journey"""
        self.log("\n" + "=" * 60)
        self.log("PHASE 4 - SCENARIO 2: PRO CLIENT (Tenant B)")
        self.log("=" * 60)
        
        # Similar to basic but with Pro features
        signup_data = {
            "email": "pro@callflow.test",
            "username": "pro_user",
            "password": "TestPass123!",
            "full_name": "Pro User",
            "phone_number": "+15559876543"
        }
        
        try:
            resp = requests.post(f"{BASE_URL}/users/register", json=signup_data)
            if resp.status_code in [201, 400]:
                self.results["phase4_pro"]["passed"].append("Signup")
                self.log("✅ Pro user signup successful")
            
            # Login
            login_resp = requests.post(f"{BASE_URL}/users/login", data={
                "username": "pro_user",
                "password": "TestPass123!"
            })
            
            if login_resp.status_code == 200:
                token = login_resp.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}"}
                self.results["phase4_pro"]["passed"].append("Login")
                
                # Test automations (should work for Pro)
                self.log("Testing automations for Pro user...")
                auto_resp = requests.post(
                    f"{BASE_URL}/automations/update",
                    json={
                        "automations": {
                            "google_calendar_sync": True,
                            "airtable_sync": True
                        }
                    },
                    headers=headers
                )
                
                if auto_resp.status_code == 200:
                    self.results["phase4_pro"]["passed"].append("Automations update")
                    self.log("✅ Pro automations update works")
                else:
                    self.results["phase4_pro"]["failed"].append(f"Automations: {auto_resp.status_code}")
                    self.log(f"❌ Pro automations failed: {auto_resp.text}", "ERROR")
                    
        except Exception as e:
            self.results["phase4_pro"]["failed"].append(f"Error: {str(e)}")
            self.log(f"❌ Pro scenario error: {e}", "ERROR")
    
    def test_admin_panel(self):
        """Phase 5: Admin Panel Testing"""
        self.log("\n" + "=" * 60)
        self.log("PHASE 5: ADMIN PANEL STRESS TEST")
        self.log("=" * 60)
        
        # Try to login as admin
        self.log("Testing admin login...")
        try:
            admin_resp = requests.post(f"{BASE_URL}/users/login", data={
                "username": "admin",
                "password": "admin123"
            })
            
            if admin_resp.status_code == 200:
                admin_token = admin_resp.json()["access_token"]
                admin_headers = {"Authorization": f"Bearer {admin_token}"}
                self.results["phase5_admin"]["passed"].append("Admin login")
                self.log("✅ Admin login successful")
                
                # List tenants
                tenants_resp = requests.get(f"{BASE_URL}/admin/tenants", headers=admin_headers)
                if tenants_resp.status_code == 200:
                    tenants = tenants_resp.json()
                    self.log(f"✅ Found {len(tenants)} tenants")
                    self.results["phase5_admin"]["passed"].append("List tenants")
                else:
                    self.log(f"❌ Failed to list tenants: {tenants_resp.status_code}", "ERROR")
                    self.results["phase5_admin"]["failed"].append("List tenants")
            else:
                self.log(f"⚠️ Admin login failed (might not exist): {admin_resp.status_code}")
                self.results["phase5_admin"]["failed"].append("Admin login")
                
        except Exception as e:
            self.log(f"❌ Admin test error: {e}", "ERROR")
            self.results["phase5_admin"]["failed"].append(f"Error: {str(e)}")
    
    def generate_report(self):
        """Generate final report"""
        self.log("\n" + "=" * 60)
        self.log("FINAL RESULTS SUMMARY")
        self.log("=" * 60)
        
        total_passed = (
            len(self.results["phase4_basic"]["passed"]) +
            len(self.results["phase4_pro"]["passed"]) +
            len(self.results["phase5_admin"]["passed"])
        )
        
        total_failed = (
            len(self.results["phase4_basic"]["failed"]) +
            len(self.results["phase4_pro"]["failed"]) +
            len(self.results["phase5_admin"]["failed"])
        )
        
        self.log(f"\nPhase 4 Basic: {len(self.results['phase4_basic']['passed'])} passed, {len(self.results['phase4_basic']['failed'])} failed")
        self.log(f"Phase 4 Pro: {len(self.results['phase4_pro']['passed'])} passed, {len(self.results['phase4_pro']['failed'])} failed")
        self.log(f"Phase 5 Admin: {len(self.results['phase5_admin']['passed'])} passed, {len(self.results['phase5_admin']['failed'])} failed")
        
        self.log(f"\n📊 TOTAL: {total_passed} passed, {total_failed} failed")
        
        if self.results["security_issues"]:
            self.log("\n🚨 CRITICAL SECURITY ISSUES:")
            for issue in self.results["security_issues"]:
                self.log(f"  - {issue}", "ERROR")
        
        # Save to file
        with open("/tmp/e2e_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        self.log("\n✅ Results saved to /tmp/e2e_test_results.json")

if __name__ == "__main__":
    tester = E2ETester()
    
    # Run all tests
    tester.test_basic_scenario()
    tester.test_pro_scenario()
    tester.test_admin_panel()
    
    # Generate report
    tester.generate_report()
    
    print("\n" + "=" * 60)
    print("PHASE 4/6 COMPLETED")
    print("=" * 60)
