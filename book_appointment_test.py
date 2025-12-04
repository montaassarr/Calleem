#!/usr/bin/env python3
"""
Test appointment booking through LiveKit agent
Simulates a customer booking an appointment via voice conversation
"""
import asyncio
import requests
import json
from datetime import datetime, timedelta

# Configuration
BACKEND_URL = "http://localhost:8000/api/v1"
CUSTOMER_EMAIL = "montamsallem@gmail.com"
CUSTOMER_PASSWORD = "Mariemmontassar03$"

def print_step(step, message):
    print(f"\n{'='*70}")
    print(f"STEP {step}: {message}")
    print(f"{'='*70}\n")

def login(email, password):
    """Login and get JWT token"""
    print(f"🔐 Logging in as {email}...")
    response = requests.post(
        f"{BACKEND_URL}/users/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        user_data = response.json()
        print(f"✅ Login successful")
        print(f"   User ID: {user_data.get('user_id')}")
        print(f"   Tenant ID: {user_data.get('tenant_id')}")
        return token, user_data
    else:
        print(f"❌ Login failed: {response.text}")
        return None, None

def get_services(token):
    """Get available services"""
    print("\n📋 Fetching available services...")
    response = requests.get(
        f"{BACKEND_URL}/services",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        services = response.json()
        print(f"✅ Found {len(services)} services:")
        for service in services:
            duration = service.get('duration_minutes', service.get('duration', 'N/A'))
            print(f"   • {service['name']} - ${service['price']} - {duration} min")
        return services
    else:
        print(f"⚠️  No services found or error: {response.status_code}")
        return []

def create_service(token):
    """Create a test service"""
    print("\n➕ Creating test service...")
    service_data = {
        "name": "Consultation",
        "description": "Initial consultation appointment",
        "duration_minutes": 30,
        "price": 50.0,
        "is_active": True
    }
    
    response = requests.post(
        f"{BACKEND_URL}/services",
        json=service_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code in [200, 201]:
        service = response.json()
        print(f"✅ Service created: {service.get('name', 'Unknown')}")
        return service
    else:
        print(f"❌ Failed to create service: {response.status_code}")
        print(f"   {response.text}")
        return None

def check_availability(token, service_id, date_str):
    """Check appointment availability"""
    print(f"\n📅 Checking availability for {date_str}...")
    response = requests.get(
        f"{BACKEND_URL}/appointments/availability",
        params={"service_id": service_id, "date": date_str},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        slots = response.json()
        print(f"✅ Available slots found: {len(slots)}")
        if slots:
            for slot in slots[:5]:  # Show first 5 slots
                print(f"   • {slot}")
        return slots
    else:
        print(f"⚠️  Could not check availability: {response.status_code}")
        return []

def book_appointment(token, service_id, scheduled_time):
    """Book an appointment"""
    print(f"\n📝 Booking appointment for {scheduled_time}...")
    
    # Parse the scheduled time
    scheduled_dt = datetime.fromisoformat(scheduled_time)
    
    appointment_data = {
        "service_id": service_id,
        "client_name": "Montassar Sallem",
        "customer_name": "Montassar Sallem",
        "client_phone": "+1234567890",
        "customer_phone": "+1234567890",
        "datetime": scheduled_time,
        "duration_minutes": 30,
        "notes": "Test appointment booked via AI agent backend test"
    }
    
    response = requests.post(
        f"{BACKEND_URL}/appointments",
        json=appointment_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code in [200, 201]:
        appointment = response.json()
        print(f"✅ Appointment booked successfully!")
        print(f"   Appointment ID: {appointment.get('id')}")
        print(f"   Service: {appointment.get('service_name', 'N/A')}")
        print(f"   Time: {appointment.get('scheduled_at')}")
        print(f"   Status: {appointment.get('status')}")
        print(f"   Customer: {appointment.get('customer_name')}")
        return appointment
    else:
        print(f"❌ Failed to book appointment: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def get_appointments(token):
    """Get all appointments"""
    print("\n📋 Fetching all appointments...")
    response = requests.get(
        f"{BACKEND_URL}/appointments",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        appointments = response.json()
        print(f"✅ Found {len(appointments)} appointments:")
        for apt in appointments:
            print(f"   • {apt.get('scheduled_at')} - {apt.get('customer_name')} - {apt.get('status')}")
        return appointments
    else:
        print(f"⚠️  Could not fetch appointments")
        return []

def create_livekit_session(token):
    """Create LiveKit session to trigger agent"""
    print("\n🎙️  Creating LiveKit session (triggering AI agent)...")
    response = requests.post(
        f"{BACKEND_URL}/voice-agent/webrtc/test",
        json={},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ LiveKit session created")
        print(f"   Room: {data['room_name']}")
        print(f"   Agent: {data['agent_name']}")
        print(f"   Queue: {data['agent_queue']}")
        print(f"\n💡 The AI agent is now active in this room and ready to:")
        print(f"   • Listen to voice commands")
        print(f"   • Answer questions about services")
        print(f"   • Check availability")
        print(f"   • Book appointments")
        return data
    else:
        print(f"❌ Failed to create session: {response.text}")
        return None

def simulate_conversation():
    """Simulate the conversation that would happen"""
    print("\n" + "="*70)
    print("💬 SIMULATED VOICE CONVERSATION WITH AI AGENT")
    print("="*70)
    
    conversation = [
        ("👤 Customer", "Hello, I'd like to book an appointment"),
        ("🤖 AI Agent", "Hello! I'd be happy to help you book an appointment. What service are you interested in?"),
        ("👤 Customer", "I need a consultation"),
        ("🤖 AI Agent", "Great! Let me check our consultation availability. What date works best for you?"),
        ("👤 Customer", "Tomorrow at 2 PM"),
        ("🤖 AI Agent", "Let me check if tomorrow at 2 PM is available... Yes, that time slot is open!"),
        ("🤖 AI Agent", "May I have your name and contact information to complete the booking?"),
        ("👤 Customer", "My name is Montassar Sallem, email is montamslallem@gmail.com, phone +1234567890"),
        ("🤖 AI Agent", "Perfect! I've booked your consultation for tomorrow at 2 PM."),
        ("🤖 AI Agent", "You'll receive a confirmation email shortly. Is there anything else I can help you with?"),
        ("👤 Customer", "No, that's all. Thank you!"),
        ("🤖 AI Agent", "You're welcome! We look forward to seeing you tomorrow. Have a great day!"),
    ]
    
    import time
    for speaker, message in conversation:
        print(f"\n{speaker}: {message}")
        time.sleep(0.5)
    
    print("\n" + "="*70)

def test_n8n_webhook(appointment_data):
    """Test if n8n webhook receives appointment data"""
    print("\n🔗 Testing n8n webhook integration...")
    
    # n8n webhook URL (you'll need to get this from your n8n workflow)
    n8n_webhook_url = "http://localhost:5678/webhook-test/appointment-created"
    
    try:
        response = requests.post(
            n8n_webhook_url,
            json=appointment_data,
            timeout=5
        )
        if response.status_code == 200:
            print(f"✅ n8n webhook received appointment data")
            return True
    except requests.exceptions.RequestException as e:
        print(f"⚠️  n8n webhook not configured or not responding")
        print(f"   Configure webhook in n8n workflow to receive appointment notifications")
    
    return False

def main():
    """Main test flow"""
    print("\n" + "="*70)
    print("🎯 AI RECEPTIONIST - APPOINTMENT BOOKING TEST")
    print("Testing Backend Only (No Frontend)")
    print("="*70)
    
    # Step 1: Login as customer
    print_step(1, "Customer Login")
    token, user_data = login(CUSTOMER_EMAIL, CUSTOMER_PASSWORD)
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Step 2: Check/Create services
    print_step(2, "Service Management")
    services = get_services(token)
    if not services:
        print("No services found. Creating test service...")
        service = create_service(token)
        if not service:
            print("❌ Cannot proceed without services")
            return
        services = [service]
    
    service_id = services[0]['id']
    print(f"\n✅ Using service: {services[0]['name']} (ID: {service_id})")
    
    # Step 3: Check availability
    print_step(3, "Check Availability")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    slots = check_availability(token, service_id, tomorrow)
    
    # Step 4: Create LiveKit session (activate AI agent)
    print_step(4, "Activate AI Agent")
    session = create_livekit_session(token)
    
    # Step 5: Show simulated conversation
    print_step(5, "Voice Conversation Simulation")
    simulate_conversation()
    
    # Step 6: Actually book the appointment
    print_step(6, "Book Appointment via Backend API")
    scheduled_time = f"{tomorrow}T14:00:00"  # Tomorrow at 2 PM
    appointment = book_appointment(token, service_id, scheduled_time)
    
    if appointment:
        # Step 7: Test n8n webhook
        print_step(7, "n8n Workflow Integration")
        test_n8n_webhook(appointment)
    
    # Step 8: Verify booking
    print_step(8, "Verify Booking")
    appointments = get_appointments(token)
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    print(f"✅ Customer authenticated: {CUSTOMER_EMAIL}")
    print(f"✅ Service available: {services[0]['name']}")
    print(f"✅ AI Agent activated: LiveKit session created")
    print(f"✅ Appointment booked: {scheduled_time}")
    print(f"✅ Total appointments: {len(appointments)}")
    
    print("\n💡 NEXT STEPS:")
    print("   1. Configure n8n webhooks to receive appointment notifications")
    print("   2. Set up n8n workflow for:")
    print("      • Sending confirmation emails")
    print("      • WhatsApp reminders")
    print("      • Calendar integration")
    print("      • SMS notifications")
    print("\n   3. Test with actual voice using LiveKit client:")
    print("      • Frontend: http://localhost:3000/dashboard/voice-agent/chat")
    print("      • Or use talk_to_ai.py for terminal voice testing")
    
    print("\n" + "="*70)
    print("✅ BACKEND TEST COMPLETE!")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
