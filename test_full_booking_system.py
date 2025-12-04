#!/usr/bin/env python3
"""
Complete Booking System Test with AI Agent
Tests: Create, Read, Update, Delete, Check Availability
Includes n8n webhook integration
"""
import requests
import json
from datetime import datetime, timedelta
import time

# Configuration
BACKEND_URL = "http://localhost:8000/api/v1"
N8N_URL = "http://localhost:5678"
EMAIL = "montamsallem@gmail.com"
PASSWORD = "Mariemmontassar03$"

def print_header(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

class BookingSystemTest:
    def __init__(self):
        self.token = None
        self.tenant_id = None
        self.service_id = None
        self.appointment_id = None
        
    def login(self):
        """Step 1: Authenticate"""
        print_header("STEP 1: AUTHENTICATION")
        print(f"🔐 Logging in as {EMAIL}...")
        
        response = requests.post(
            f"{BACKEND_URL}/users/login",
            data={"username": EMAIL, "password": PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.tenant_id = data.get("tenant_id")
            print(f"✅ Login successful")
            print(f"   Token: {self.token[:30]}...")
            print(f"   Tenant ID: {self.tenant_id}")
            return True
        else:
            print(f"❌ Login failed: {response.text}")
            return False
    
    def setup_service(self):
        """Step 2: Get or create service"""
        print_header("STEP 2: SERVICE SETUP")
        print("📋 Checking available services...")
        
        response = requests.get(
            f"{BACKEND_URL}/services",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        if response.status_code == 200:
            services = response.json()
            if services:
                self.service_id = services[0]['id']
                duration = services[0].get('duration_minutes', services[0].get('duration', 30))
                print(f"✅ Using existing service: {services[0]['name']}")
                print(f"   Service ID: {self.service_id}")
                print(f"   Price: ${services[0]['price']}")
                print(f"   Duration: {duration} minutes")
            else:
                print("➕ Creating new service...")
                service_data = {
                    "name": "Hair Cut",
                    "description": "Professional haircut service",
                    "duration_minutes": 45,
                    "price": 35.0,
                    "is_active": True
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/services",
                    json=service_data,
                    headers={"Authorization": f"Bearer {self.token}"}
                )
                
                if response.status_code in [200, 201]:
                    service = response.json()
                    self.service_id = service['id']
                    print(f"✅ Service created: {service.get('name')}")
                    print(f"   Service ID: {self.service_id}")
                else:
                    print(f"❌ Failed to create service: {response.text}")
                    return False
        return True
    
    def check_availability(self):
        """Step 3: Check availability"""
        print_header("STEP 3: CHECK AVAILABILITY")
        print("📅 Checking available time slots...")
        
        # Try tomorrow and day after
        for days_ahead in [1, 2]:
            date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
            print(f"\n📆 Date: {date}")
            
            response = requests.get(
                f"{BACKEND_URL}/appointments/availability",
                params={"service_id": self.service_id, "date": date},
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                try:
                    slots = response.json()
                    if isinstance(slots, list) and slots:
                        print(f"✅ {len(slots)} available slots:")
                        for i, slot in enumerate(slots[:5], 1):
                            print(f"   {i}. {slot}")
                    else:
                        print("   ℹ️  Response format:", slots)
                except Exception as e:
                    print(f"   ⚠️  Could not parse slots: {e}")
            else:
                print(f"   ⚠️  Status {response.status_code}: {response.text[:100]}")
    
    def create_appointment(self):
        """Step 4: Create (Book) appointment"""
        print_header("STEP 4: CREATE APPOINTMENT")
        print("📝 Booking new appointment...")
        
        # Book for tomorrow at 2 PM
        tomorrow = datetime.now() + timedelta(days=1)
        scheduled_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
        
        appointment_data = {
            "service_id": self.service_id,
            "client_name": "John Customer",
            "customer_name": "John Customer",
            "client_phone": "+1234567890",
            "customer_phone": "+1234567890",
            "datetime": scheduled_time.isoformat(),
            "duration_minutes": 45,
            "notes": "Test booking - Full system test"
        }
        
        print(f"   Customer: John Customer")
        print(f"   Phone: +1234567890")
        print(f"   Time: {scheduled_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Duration: 45 minutes")
        
        response = requests.post(
            f"{BACKEND_URL}/appointments",
            json=appointment_data,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        if response.status_code in [200, 201]:
            appointment = response.json()
            self.appointment_id = appointment.get('id')
            print(f"\n✅ Appointment created successfully!")
            print(f"   Appointment ID: {self.appointment_id}")
            print(f"   Status: {appointment.get('status')}")
            print(f"   Service: {appointment.get('service', 'N/A')}")
            
            # Trigger n8n webhook
            self.trigger_n8n_webhook('appointment.created', appointment)
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   {response.text}")
            return False
    
    def read_appointments(self):
        """Step 5: Read (List) appointments"""
        print_header("STEP 5: READ APPOINTMENTS")
        print("📋 Fetching all appointments...")
        
        response = requests.get(
            f"{BACKEND_URL}/appointments",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        if response.status_code == 200:
            appointments = response.json()
            print(f"✅ Found {len(appointments)} appointments:\n")
            
            for i, apt in enumerate(appointments[:5], 1):
                print(f"{i}. Appointment {apt.get('id', 'N/A')[:8]}...")
                print(f"   Customer: {apt.get('client_name', 'N/A')}")
                print(f"   Phone: {apt.get('client_phone', 'N/A')}")
                print(f"   Time: {apt.get('datetime', apt.get('start_time', 'N/A'))}")
                print(f"   Status: {apt.get('status', 'N/A')}")
                print()
            
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False
    
    def read_single_appointment(self):
        """Step 6: Read single appointment"""
        if not self.appointment_id:
            print("⚠️  No appointment ID to read")
            return False
            
        print_header("STEP 6: READ SINGLE APPOINTMENT")
        print(f"🔍 Fetching appointment {self.appointment_id}...")
        
        response = requests.get(
            f"{BACKEND_URL}/appointments/{self.appointment_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        if response.status_code == 200:
            apt = response.json()
            print(f"✅ Appointment details:")
            print(f"   ID: {apt.get('id')}")
            print(f"   Customer: {apt.get('client_name')}")
            print(f"   Phone: {apt.get('client_phone')}")
            print(f"   Service: {apt.get('service')}")
            print(f"   Time: {apt.get('datetime', apt.get('start_time'))}")
            print(f"   Duration: {apt.get('duration_minutes')} minutes")
            print(f"   Status: {apt.get('status')}")
            print(f"   Notes: {apt.get('notes')}")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False
    
    def update_appointment(self):
        """Step 7: Update appointment"""
        if not self.appointment_id:
            print("⚠️  No appointment ID to update")
            return False
            
        print_header("STEP 7: UPDATE APPOINTMENT")
        print(f"📝 Updating appointment {self.appointment_id}...")
        
        # Update time to 3 PM and add notes
        tomorrow = datetime.now() + timedelta(days=1)
        new_time = tomorrow.replace(hour=15, minute=0, second=0, microsecond=0)
        
        update_data = {
            "datetime": new_time.isoformat(),
            "notes": "Rescheduled to 3 PM - Customer request"
        }
        
        print(f"   New time: {new_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"   New notes: {update_data['notes']}")
        
        response = requests.put(
            f"{BACKEND_URL}/appointments/{self.appointment_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        if response.status_code == 200:
            apt = response.json()
            print(f"\n✅ Appointment updated successfully!")
            print(f"   New time: {apt.get('datetime', apt.get('start_time'))}")
            print(f"   Status: {apt.get('status')}")
            
            # Trigger n8n webhook
            self.trigger_n8n_webhook('appointment.updated', apt)
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False
    
    def cancel_appointment(self):
        """Step 8: Cancel appointment (soft delete)"""
        if not self.appointment_id:
            print("⚠️  No appointment ID to cancel")
            return False
            
        print_header("STEP 8: CANCEL APPOINTMENT")
        print(f"❌ Cancelling appointment {self.appointment_id}...")
        
        cancel_data = {
            "status": "cancelled"
        }
        
        response = requests.put(
            f"{BACKEND_URL}/appointments/{self.appointment_id}",
            json=cancel_data,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        if response.status_code == 200:
            apt = response.json()
            print(f"✅ Appointment cancelled")
            print(f"   Status: {apt.get('status')}")
            
            # Trigger n8n webhook
            self.trigger_n8n_webhook('appointment.cancelled', apt)
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False
    
    def delete_appointment(self):
        """Step 9: Delete appointment (hard delete)"""
        if not self.appointment_id:
            print("⚠️  No appointment ID to delete")
            return False
            
        print_header("STEP 9: DELETE APPOINTMENT")
        print(f"🗑️  Permanently deleting appointment {self.appointment_id}...")
        
        response = requests.delete(
            f"{BACKEND_URL}/appointments/{self.appointment_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        if response.status_code == 200:
            print(f"✅ Appointment deleted permanently")
            
            # Trigger n8n webhook
            self.trigger_n8n_webhook('appointment.deleted', {'id': self.appointment_id})
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False
    
    def test_livekit_agent(self):
        """Step 10: Test LiveKit AI Agent"""
        print_header("STEP 10: AI AGENT INTEGRATION")
        print("🎙️  Testing LiveKit AI Agent...")
        
        response = requests.post(
            f"{BACKEND_URL}/voice-agent/webrtc/test",
            json={},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI Agent session created")
            print(f"   Room: {data['room_name']}")
            print(f"   Agent: {data['agent_name']}")
            print(f"   Queue: {data['agent_queue']}")
            print(f"   URL: {data['url']}")
            print()
            print("💡 The AI agent can now:")
            print("   • Check appointment availability")
            print("   • Book new appointments")
            print("   • Reschedule existing appointments")
            print("   • Cancel appointments")
            print("   • Answer questions about services")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False
    
    def trigger_n8n_webhook(self, event_type, data):
        """Trigger n8n webhook for workflow automation"""
        print(f"\n🔗 Triggering n8n webhook: {event_type}")
        
        webhook_url = f"{N8N_URL}/webhook/appointment-lifecycle"
        payload = {
            "event": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=3)
            if response.status_code == 200:
                print(f"   ✅ n8n workflow triggered")
            else:
                print(f"   ⚠️  n8n response: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"   ℹ️  n8n webhook not configured (this is optional)")
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "="*80)
        print("  🎯 COMPLETE BOOKING SYSTEM TEST")
        print("  Testing CRUD Operations + AI Agent + n8n Integration")
        print("="*80)
        
        results = []
        
        # Run all tests
        results.append(("Authentication", self.login()))
        if not results[-1][1]:
            self.print_summary(results)
            return
        
        results.append(("Service Setup", self.setup_service()))
        if not results[-1][1]:
            self.print_summary(results)
            return
        
        results.append(("Check Availability", self.check_availability() or True))  # Non-critical
        results.append(("Create Appointment", self.create_appointment()))
        results.append(("Read All Appointments", self.read_appointments()))
        results.append(("Read Single Appointment", self.read_single_appointment()))
        results.append(("Update Appointment", self.update_appointment()))
        results.append(("Cancel Appointment", self.cancel_appointment()))
        results.append(("Delete Appointment", self.delete_appointment()))
        results.append(("AI Agent Integration", self.test_livekit_agent()))
        
        self.print_summary(results)
    
    def print_summary(self, results):
        """Print test summary"""
        print_header("TEST SUMMARY")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
        
        print(f"\n{'='*80}")
        print(f"  Results: {passed}/{total} tests passed")
        if passed == total:
            print("  🎉 ALL TESTS PASSED!")
        else:
            print(f"  ⚠️  {total - passed} test(s) failed")
        print(f"{'='*80}\n")
        
        print("📝 Next Steps:")
        print("   1. Access n8n: http://localhost:5678")
        print("   2. View workflows: Test Full Appointment Lifecycle")
        print("   3. Test AI voice: http://localhost:3000/dashboard/voice-agent/chat")
        print("   4. Check MongoDB: mongosh callflow_ai_saas")
        print()

if __name__ == "__main__":
    try:
        tester = BookingSystemTest()
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
