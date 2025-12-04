#!/usr/bin/env python3
"""
Simulate AI Agent Appointment Booking Flow
This script mimics what happens when a user talks to the AI agent
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"

def simulate_ai_conversation():
    print("\n" + "🎤 " * 30)
    print("AI AGENT APPOINTMENT BOOKING SIMULATION")
    print("🎤 " * 30 + "\n")
    
    # Step 1: User logs in (happens automatically in frontend)
    print("👤 User: montamsallem@gmail.com")
    print("🔐 Authenticating...\n")
    
    login_response = requests.post(
        f"{BASE_URL}/users/login",
        data={"username": "montamsallem@gmail.com", "password": "Mariemmontassar03$"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if login_response.status_code != 200:
        print("❌ Authentication failed!")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    print("✅ User authenticated\n")
    
    # Extract tenant_id
    import base64
    token_parts = token.split('.')
    payload = json.loads(base64.b64decode(token_parts[1] + '=='))
    tenant_id = payload.get('tenant_id')
    
    print("=" * 70)
    print("\n🎙️  USER: 'Hi, I want to book an appointment'")
    print("\n🤖 AI AGENT: 'Hello! I'd be happy to help you book an appointment.")
    print("           Let me check what services we have available...'\n")
    
    # AI checks available services
    services_response = requests.get(f"{BASE_URL}/services", headers=headers)
    if services_response.status_code == 200:
        services = services_response.json()
        print("   [AI Agent calling: list_services()]")
        print(f"   [AI Agent found: {len(services)} services]\n")
        
        if services:
            print("🤖 AI AGENT: 'We offer the following services:")
            for svc in services:
                print(f"           • {svc.get('name')} - {svc.get('duration')} minutes - ${svc.get('price')}")
            print("           Which service would you like?'\n")
    
    print("🎙️  USER: 'I want a haircut'\n")
    
    # AI gets business hours
    print("🤖 AI AGENT: 'Great choice! Let me check our availability...'")
    print("   [AI Agent calling: get_business_hours()]\n")
    
    # Simulate checking availability
    target_date = datetime.now() + timedelta(days=1)
    print(f"   [AI Agent calling: check_appointment_availability('{target_date.strftime('%Y-%m-%d')}', '14:00')]\n")
    
    list_response = requests.get(f"{BASE_URL}/appointments", headers=headers)
    if list_response.status_code == 200:
        existing_appointments = list_response.json()
        print(f"   [AI Agent found: {len(existing_appointments)} existing appointments]")
        print("   [AI Agent: Time slot 2:00 PM is available]\n")
    
    print("🤖 AI AGENT: 'I have availability tomorrow at 2:00 PM. Would that work for you?'\n")
    print("🎙️  USER: 'Yes, that's perfect!'\n")
    
    print("🤖 AI AGENT: 'Excellent! Let me book that for you...'")
    print("   [AI Agent calling: book_appointment()]")
    
    # Create the appointment
    appointment_date = target_date.replace(hour=14, minute=0, second=0, microsecond=0)
    appointment_data = {
        "customer_name": "Montassar Sallem",
        "customer_email": "montamsallem@gmail.com",
        "customer_phone": "+33612345678",
        "datetime": appointment_date.isoformat(),
        "duration_minutes": 60,
        "notes": "Haircut appointment - Booked via AI voice agent"
    }
    
    if services and len(services) > 0:
        # Find haircut service
        haircut_service = next((s for s in services if 'hair' in s.get('name', '').lower()), services[0])
        appointment_data["service_id"] = haircut_service.get('id')
    
    appointment_response = requests.post(
        f"{BASE_URL}/appointments",
        json=appointment_data,
        headers=headers
    )
    
    if appointment_response.status_code in [200, 201]:
        appointment = appointment_response.json()
        apt_id = appointment.get('id')
        apt_datetime = appointment.get('datetime')
        print(f"   [AI Agent: Appointment created - ID: {apt_id}]\n")
        
        print("🤖 AI AGENT: 'Perfect! Your appointment has been booked!")
        print(f"           📅 Date: {apt_datetime}")
        print(f"           👤 Name: Montassar Sallem")
        print(f"           📧 Email: montamsallem@gmail.com")
        print(f"           ⏱️  Duration: 60 minutes")
        print("           ")
        print("           You'll receive a confirmation email shortly.")
        print("           Is there anything else I can help you with?'\n")
    else:
        print(f"   ❌ Booking failed: {appointment_response.text}\n")
        return
    
    print("🎙️  USER: 'No, that's all. Thank you!'\n")
    
    print("🤖 AI AGENT: 'You're welcome! We look forward to seeing you tomorrow")
    print("           at 2:00 PM. Have a great day!'\n")
    
    print("=" * 70)
    print("\n📊 APPOINTMENT BOOKING SUMMARY:")
    print("   ✅ Service: Haircut")
    print(f"   ✅ Date: {apt_datetime}")
    print("   ✅ Duration: 60 minutes")
    print("   ✅ Customer: Montassar Sallem")
    print("   ✅ Email: montamsallem@gmail.com")
    print(f"   ✅ Status: Confirmed (ID: {apt_id})")
    
    print("\n📋 VERIFY IN DASHBOARD:")
    print("   🌐 http://localhost:3000/dashboard/appointments")
    print(f"   🔑 Login: montamsallem@gmail.com")
    print(f"   🔐 Password: Mariemmontassar03$")
    
    print("\n🎤 TRY IT WITH REAL VOICE:")
    print("   1. Go to: http://localhost:3000/dashboard/voice-agent/chat")
    print("   2. Click 'Start Chat'")
    print("   3. Speak: 'I want to book an appointment'")
    print("   4. Follow the AI's prompts")
    
    print("\n" + "🎤 " * 30 + "\n")

if __name__ == "__main__":
    simulate_ai_conversation()
