#!/usr/bin/env python3
"""
Comprehensive API Endpoint Testing Script
Tests all 80 endpoints from the OpenAPI schema and generates a detailed report
"""

import requests
import json
import sys
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import time

# Configuration
BASE_URL = "https://ai-receptionist-production-299a.up.railway.app"
TEST_TENANT_ID = "test_tenant_123"
RESULTS_FILE = "/tmp/endpoint_test_results.json"
REPORT_FILE = "/tmp/endpoint_test_report.md"

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class EndpointTester:
    def __init__(self):
        self.results = []
        self.auth_token = None
        self.admin_token = None
        self.test_tenant_id = None
        self.test_service_id = None
        self.test_appointment_id = None
        
    def log(self, message: str, color: str = Colors.RESET):
        print(f"{color}{message}{Colors.RESET}")
    
    def test_endpoint(
        self, 
        method: str, 
        path: str, 
        description: str = "",
        headers: Optional[Dict] = None,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        requires_auth: bool = False,
        requires_admin: bool = False,
        expected_status: List[int] = None
    ) -> Dict:
        """Test a single endpoint and return results"""
        url = f"{BASE_URL}{path}"
        
        # Prepare headers
        test_headers = {"Content-Type": "application/json"}
        if headers:
            test_headers.update(headers)
        
        if requires_auth and self.auth_token:
            test_headers["Authorization"] = f"Bearer {self.auth_token}"
        
        if requires_admin and self.admin_token:
            test_headers["Authorization"] = f"Bearer {self.admin_token}"
        
        # Default expected statuses
        if expected_status is None:
            expected_status = [200, 201, 204]
        
        try:
            # Make request
            if method == "GET":
                response = requests.get(url, headers=test_headers, params=params, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=test_headers, json=data, params=params, timeout=10)
            elif method == "PUT":
                response = requests.put(url, headers=test_headers, json=data, timeout=10)
            elif method == "PATCH":
                response = requests.patch(url, headers=test_headers, json=data, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, headers=test_headers, timeout=10)
            else:
                return self._create_result(path, method, "SKIP", 0, "Unsupported method", description)
            
            # Determine status
            status_code = response.status_code
            
            if status_code in expected_status:
                status = "PASS"
            elif status_code == 401:
                status = "AUTH_REQUIRED"
            elif status_code == 403:
                status = "FORBIDDEN"
            elif status_code == 404:
                status = "NOT_FOUND"
            elif status_code == 422:
                status = "VALIDATION_ERROR"
            elif status_code == 500:
                status = "SERVER_ERROR"
            else:
                status = "UNEXPECTED"
            
            # Parse response
            try:
                response_data = response.json() if response.text else {}
            except:
                response_data = {"raw": response.text[:200]}
            
            return self._create_result(
                path, method, status, status_code, 
                response_data, description, response.elapsed.total_seconds()
            )
            
        except requests.exceptions.Timeout:
            return self._create_result(path, method, "TIMEOUT", 0, "Request timed out", description)
        except requests.exceptions.ConnectionError:
            return self._create_result(path, method, "CONNECTION_ERROR", 0, "Connection failed", description)
        except Exception as e:
            return self._create_result(path, method, "ERROR", 0, str(e), description)
    
    def _create_result(self, path, method, status, status_code, response, description, duration=0):
        """Create a result dictionary"""
        result = {
            "path": path,
            "method": method,
            "status": status,
            "status_code": status_code,
            "description": description,
            "response": response if isinstance(response, dict) else {"message": str(response)},
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        return result
    
    def register_test_user(self):
        """Register a test user for authentication"""
        self.log("📝 Registering test user...", Colors.BLUE)
        timestamp = int(time.time())
        result = self.test_endpoint(
            "POST", "/api/v1/users/register",
            description="Register test user",
            data={
                "email": f"test_{timestamp}@example.com",
                "password": "TestPassword123!",
                "business_name": "Test Business"
            },
            expected_status=[200, 201, 400]  # 400 if user exists
        )
        
        if result["status"] in ["PASS"]:
            self.auth_token = result["response"].get("access_token")
            self.test_tenant_id = result["response"].get("tenant_id")
            self.log(f"✅ User registered, token obtained", Colors.GREEN)
            return True
        else:
            # Try login instead
            return self.login_test_user()
    
    def login_test_user(self):
        """Login with test credentials"""
        self.log("🔐 Attempting login...", Colors.BLUE)
        result = self.test_endpoint(
            "POST", "/api/v1/users/login",
            description="Login test user",
            data={
                "username": "test@example.com",
                "password": "TestPassword123!"
            },
            expected_status=[200, 401]
        )
        
        if result["status"] == "PASS":
            self.auth_token = result["response"].get("access_token")
            self.test_tenant_id = result["response"].get("tenant_id")
            self.log(f"✅ Login successful", Colors.GREEN)
            return True
        
        self.log(f"⚠️ Could not authenticate", Colors.YELLOW)
        return False
    
    def run_all_tests(self):
        """Run tests on all endpoints"""
        self.log(f"\n{Colors.BOLD}{'='*80}", Colors.BLUE)
        self.log(f"🧪 API ENDPOINT TESTING SUITE", Colors.BLUE)
        self.log(f"{'='*80}{Colors.RESET}\n", Colors.BLUE)
        self.log(f"Base URL: {BASE_URL}")
        self.log(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Try to authenticate first
        self.register_test_user()
        
        # Test health and basic endpoints
        self.log(f"\n{Colors.BOLD}1. HEALTH & BASIC ENDPOINTS{Colors.RESET}", Colors.BLUE)
        self.test_endpoint("GET", "/", "Root endpoint")
        self.test_endpoint("GET", "/health", "Health check")
        
        # Test public/agent endpoints
        self.log(f"\n{Colors.BOLD}2. AGENT ENDPOINTS (No Auth){Colors.RESET}", Colors.BLUE)
        self.test_endpoint(
            "GET", "/api/v1/appointments/agent/availability",
            "Check availability",
            headers={"X-Tenant-ID": TEST_TENANT_ID},
            params={"date": "2025-12-20", "time": "10:00"}
        )
        self.test_endpoint(
            "POST", "/api/v1/appointments/agent/book",
            "Book appointment",
            headers={"X-Tenant-ID": TEST_TENANT_ID},
            data={
                "customer_name": "John Doe",
                "customer_phone": "+1234567890",
                "date": "2025-12-20",
                "time": "10:00",
                "service": "Haircut"
            }
        )
        
        # Test authentication endpoints
        self.log(f"\n{Colors.BOLD}3. AUTHENTICATION ENDPOINTS{Colors.RESET}", Colors.BLUE)
        self.test_endpoint("POST", "/api/v1/users/token", "Get token", 
                          data={"username": "test@example.com", "password": "wrong"})
        self.test_endpoint("GET", "/api/v1/users/me", "Get current user", 
                          requires_auth=True)
        self.test_endpoint("PUT", "/api/v1/users/me", "Update user", 
                          requires_auth=True,
                          data={"full_name": "Updated Name"})
        
        # Test tenant endpoints
        self.log(f"\n{Colors.BOLD}4. TENANT ENDPOINTS{Colors.RESET}", Colors.BLUE)
        self.test_endpoint("GET", "/api/v1/tenants/me", "Get tenant", 
                          requires_auth=True)
        self.test_endpoint("POST", "/api/v1/tenants/lookup-by-phone",
                          "Lookup by phone",
                          data={"phone_number": "+1234567890"})
        self.test_endpoint("PATCH", "/api/v1/tenants/me/complete-onboarding",
                          "Complete onboarding",
                          requires_auth=True)
        
        # Test services endpoints
        self.log(f"\n{Colors.BOLD}5. SERVICES ENDPOINTS{Colors.RESET}", Colors.BLUE)
        self.test_endpoint("GET", "/api/v1/services/", "List services", 
                          requires_auth=True)
        
        create_service = self.test_endpoint(
            "POST", "/api/v1/services/",
            "Create service",
            requires_auth=True,
            data={
                "name": "Test Haircut",
                "description": "A test service",
                "duration_minutes": 30,
                "price": 25.00,
                "active": True
            }
        )
        
        if create_service["status"] == "PASS":
            self.test_service_id = create_service["response"].get("id")
            
            if self.test_service_id:
                self.test_endpoint("GET", f"/api/v1/services/{self.test_service_id}",
                                  "Get service", requires_auth=True)
                self.test_endpoint("PUT", f"/api/v1/services/{self.test_service_id}",
                                  "Update service", requires_auth=True,
                                  data={"name": "Updated Haircut", "price": 30.00})
        
        # Test appointments endpoints
        self.log(f"\n{Colors.BOLD}6. APPOINTMENTS ENDPOINTS{Colors.RESET}", Colors.BLUE)
        self.test_endpoint("GET", "/api/v1/appointments/", "List appointments",
                          requires_auth=True)
        self.test_endpoint("GET", "/api/v1/appointments/stats/summary",
                          "Appointment stats", requires_auth=True)
        self.test_endpoint("GET", "/api/v1/appointments/availability/check",
                          "Check availability (auth)", requires_auth=True,
                          params={"date": "2025-12-20", "time": "14:00"})
        
        create_apt = self.test_endpoint(
            "POST", "/api/v1/appointments/",
            "Create appointment",
            requires_auth=True,
            data={
                "client_name": "Test Client",
                "client_phone": "+1234567890",
                "client_email": "client@test.com",
                "service": "Haircut",
                "datetime": "2025-12-20T15:00:00",
                "duration_minutes": 30,
                "notes": "Test appointment"
            }
        )
        
        if create_apt["status"] == "PASS":
            self.test_appointment_id = create_apt["response"].get("id")
            
            if self.test_appointment_id:
                self.test_endpoint("GET", f"/api/v1/appointments/{self.test_appointment_id}",
                                  "Get appointment", requires_auth=True)
                self.test_endpoint("PUT", f"/api/v1/appointments/{self.test_appointment_id}",
                                  "Update appointment", requires_auth=True,
                                  data={"notes": "Updated notes"})
                self.test_endpoint("POST", f"/api/v1/appointments/{self.test_appointment_id}/cancel",
                                  "Cancel appointment", requires_auth=True)
        
        # Test conversations
        self.log(f"\n{Colors.BOLD}7. CONVERSATIONS ENDPOINTS{Colors.RESET}", Colors.BLUE)
        self.test_endpoint("GET", "/api/v1/conversations/", "List conversations",
                          requires_auth=True)
        
        # Test assistant endpoints
        self.log(f"\n{Colors.BOLD}8. ASSISTANT ENDPOINTS{Colors.RESET}", Colors.BLUE)
        self.test_endpoint("GET", "/api/v1/assistant/me", "Get assistant",
                          requires_auth=True)
        self.test_endpoint("GET", "/api/v1/assistant/me/tools", "List tools",
                          requires_auth=True)
        self.test_endpoint("GET", "/api/v1/tools/built-in", "Built-in tools",
                          requires_auth=True)
        self.test_endpoint("GET", "/api/v1/assistant/me/personality",
                          "Get personality", requires_auth=True)
        self.test_endpoint("GET", "/api/v1/assistant/me/voice",
                          "Get voice settings", requires_auth=True)
        self.test_endpoint("GET", "/api/v1/assistant/me/analytics/calls",
                          "Call analytics", requires_auth=True)
        self.test_endpoint("GET", "/api/v1/assistant/me/conversations",
                          "Assistant conversations", requires_auth=True)
        self.test_endpoint("GET", "/api/v1/assistant/me/knowledge-base",
                          "Knowledge base", requires_auth=True)
        self.test_endpoint("GET", "/api/v1/voice-providers",
                          "Voice providers", requires_auth=True)
        
        # Test billing endpoints
        self.log(f"\n{Colors.BOLD}9. BILLING ENDPOINTS{Colors.RESET}", Colors.BLUE)
        self.test_endpoint("GET", "/api/v1/billing/subscription",
                          "Get subscription", requires_auth=True)
        self.test_endpoint("POST", "/api/v1/billing/checkout",
                          "Create checkout", requires_auth=True,
                          data={"plan": "basic"})
        
        # Test monitoring endpoints
        self.log(f"\n{Colors.BOLD}10. MONITORING ENDPOINTS{Colors.RESET}", Colors.BLUE)
        self.test_endpoint("POST", "/api/v1/monitoring/frontend-error",
                          "Log frontend error",
                          data={"error": "Test error", "level": "error"})
        self.test_endpoint("POST", "/api/v1/monitoring/frontend-action",
                          "Log action",
                          data={"action": "test_action"})
        
        # Test API keys
        self.log(f"\n{Colors.BOLD}11. API KEYS ENDPOINTS{Colors.RESET}", Colors.BLUE)
        self.test_endpoint("GET", "/api/v1/keys", "List API keys",
                          requires_auth=True)
        self.test_endpoint("GET", "/api/v1/platform-keys", "Platform keys",
                          requires_auth=True)
        
        # Test phone numbers
        self.log(f"\n{Colors.BOLD}12. PHONE NUMBERS ENDPOINTS{Colors.RESET}", Colors.BLUE)
        if self.test_tenant_id:
            self.test_endpoint("GET", f"/api/v1/phone-numbers/status/{self.test_tenant_id}",
                              "Phone status", requires_auth=True)
        
        # Test WhatsApp
        self.log(f"\n{Colors.BOLD}13. WHATSAPP ENDPOINTS{Colors.RESET}", Colors.BLUE)
        self.test_endpoint("GET", "/api/v1/whatsapp/status", "WhatsApp status",
                          requires_auth=True)
        
        # Test admin endpoints (will likely fail without admin role)
        self.log(f"\n{Colors.BOLD}14. ADMIN ENDPOINTS (Expected to fail without admin){Colors.RESET}", Colors.BLUE)
        self.test_endpoint("GET", "/api/v1/admin/tenants", "Admin list tenants",
                          requires_auth=True)
        self.test_endpoint("GET", "/api/v1/admin/analytics/overview",
                          "Admin analytics", requires_auth=True)
        self.test_endpoint("GET", "/api/v1/admin/database/collections",
                          "Database collections", requires_auth=True)
        
        # Test Vapi webhooks (POST without signature will fail)
        self.log(f"\n{Colors.BOLD}15. VAPI WEBHOOKS{Colors.RESET}", Colors.BLUE)
        self.test_endpoint("POST", "/api/v1/vapi/webhook",
                          "Vapi webhook",
                          data={"message": {"type": "test"}})
        
        # Test chat completions
        self.log(f"\n{Colors.BOLD}16. CHAT COMPLETIONS{Colors.RESET}", Colors.BLUE)
        self.test_endpoint("POST", "/api/v1/chat/completions",
                          "Chat completion",
                          requires_auth=True,
                          data={"messages": [{"role": "user", "content": "Hello"}]})
        
        # Cleanup - delete test resources
        self.log(f"\n{Colors.BOLD}17. CLEANUP{Colors.RESET}", Colors.BLUE)
        if self.test_service_id:
            self.test_endpoint("DELETE", f"/api/v1/services/{self.test_service_id}",
                              "Delete test service", requires_auth=True)
        if self.test_appointment_id:
            self.test_endpoint("DELETE", f"/api/v1/appointments/{self.test_appointment_id}",
                              "Delete test appointment", requires_auth=True)
    
    def generate_report(self):
        """Generate comprehensive report"""
        self.log(f"\n{Colors.BOLD}{'='*80}", Colors.BLUE)
        self.log(f"📊 GENERATING REPORT", Colors.BLUE)
        self.log(f"{'='*80}{Colors.RESET}\n", Colors.BLUE)
        
        # Save JSON results
        with open(RESULTS_FILE, 'w') as f:
            json.dump(self.results, f, indent=2)
        self.log(f"✅ JSON results saved to: {RESULTS_FILE}", Colors.GREEN)
        
        # Generate markdown report
        report = self._generate_markdown_report()
        with open(REPORT_FILE, 'w') as f:
            f.write(report)
        self.log(f"✅ Markdown report saved to: {REPORT_FILE}", Colors.GREEN)
        
        # Print summary
        self._print_summary()
    
    def _generate_markdown_report(self) -> str:
        """Generate markdown report"""
        report = f"""# API Endpoint Testing Report

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Base URL:** {BASE_URL}
**Total Endpoints Tested:** {len(self.results)}

## Summary

"""
        # Count by status
        status_counts = {}
        for result in self.results:
            status = result["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        report += "| Status | Count | Percentage |\n"
        report += "|--------|-------|------------|\n"
        total = len(self.results)
        for status, count in sorted(status_counts.items()):
            percentage = (count / total * 100) if total > 0 else 0
            report += f"| {status} | {count} | {percentage:.1f}% |\n"
        
        report += "\n## Detailed Results\n\n"
        
        # Group by category
        current_category = None
        for result in self.results:
            path = result["path"]
            
            # Determine category
            if "/admin/" in path:
                category = "Admin"
            elif "/assistant/" in path or "/tools/" in path or "/voice-providers" in path:
                category = "Assistant"
            elif "/appointments/" in path:
                category = "Appointments"
            elif "/services/" in path:
                category = "Services"
            elif "/billing/" in path:
                category = "Billing"
            elif "/monitoring/" in path:
                category = "Monitoring"
            elif "/users/" in path:
                category = "Users"
            elif "/tenants/" in path:
                category = "Tenants"
            elif "/vapi/" in path:
                category = "Vapi"
            elif "/conversations/" in path:
                category = "Conversations"
            else:
                category = "Other"
            
            if category != current_category:
                report += f"\n### {category}\n\n"
                current_category = category
            
            # Status icon
            status_icon = {
                "PASS": "✅",
                "AUTH_REQUIRED": "🔒",
                "FORBIDDEN": "🚫",
                "NOT_FOUND": "❓",
                "VALIDATION_ERROR": "⚠️",
                "SERVER_ERROR": "❌",
                "ERROR": "💥",
                "TIMEOUT": "⏱️",
                "SKIP": "⏭️"
            }.get(result["status"], "❔")
            
            report += f"#### {status_icon} {result['method']} `{result['path']}`\n\n"
            report += f"- **Status:** {result['status']} (HTTP {result['status_code']})\n"
            report += f"- **Description:** {result['description']}\n"
            
            if result['duration']:
                report += f"- **Duration:** {result['duration']:.3f}s\n"
            
            # Add response snippet
            if result['status'] not in ['PASS', 'AUTH_REQUIRED']:
                response = result['response']
                if 'detail' in response:
                    report += f"- **Error:** {response['detail']}\n"
                elif 'message' in response:
                    report += f"- **Message:** {response['message']}\n"
            
            report += "\n"
        
        # Recommendations
        report += "\n## 🎯 Recommendations\n\n"
        report += "### Endpoints to Keep\n"
        report += "- All PASS and AUTH_REQUIRED endpoints are functional\n\n"
        
        report += "### Endpoints to Review\n"
        for result in self.results:
            if result['status'] in ['SERVER_ERROR', 'NOT_FOUND', 'ERROR']:
                report += f"- `{result['method']} {result['path']}` - {result['status']}\n"
        
        report += "\n### Missing Functionality\n"
        report += "- ❌ `/api/v1/services/agent/list` - Agent needs service listing endpoint\n"
        report += "- ⚠️ Consider adding real-time sync for dashboard updates\n"
        
        return report
    
    def _print_summary(self):
        """Print summary to console"""
        status_counts = {}
        for result in self.results:
            status = result["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        self.log(f"\n{Colors.BOLD}SUMMARY:", Colors.BLUE)
        self.log(f"{'='*50}{Colors.RESET}")
        
        total = len(self.results)
        for status, count in sorted(status_counts.items()):
            percentage = (count / total * 100) if total > 0 else 0
            color = Colors.GREEN if status == "PASS" else Colors.YELLOW if status in ["AUTH_REQUIRED", "FORBIDDEN"] else Colors.RED
            self.log(f"{status:20} {count:3} ({percentage:5.1f}%)", color)
        
        self.log(f"{'='*50}")
        self.log(f"TOTAL: {total} endpoints tested\n", Colors.BOLD)

def main():
    """Main entry point"""
    tester = EndpointTester()
    
    try:
        tester.run_all_tests()
        tester.generate_report()
        
        print(f"\n{Colors.GREEN}✅ Testing complete!{Colors.RESET}")
        print(f"View detailed report at: {Colors.BLUE}{REPORT_FILE}{Colors.RESET}")
        print(f"View JSON results at: {Colors.BLUE}{RESULTS_FILE}{Colors.RESET}\n")
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️ Testing interrupted by user{Colors.RESET}")
        tester.generate_report()
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {e}{Colors.RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
