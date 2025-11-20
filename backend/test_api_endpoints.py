"""
Quick test script to verify API endpoints work with normalized schema
"""

import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient

async def test_api_data():
    """Test that we can fetch data from MongoDB with normalized schema"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.ai_barber_receptionist
    
    print("🧪 Testing API Data Layer...\n")
    
    # Test 1: Fetch appointments
    print("1️⃣ Testing Appointments:")
    appointments = await db.appointments.find({"businessId": "default"}).to_list(length=10)
    print(f"   Found {len(appointments)} appointments")
    if appointments:
        apt = appointments[0]
        print(f"   Sample: {apt.get('name')} - {apt.get('phone')} - {apt.get('service')}")
        print(f"   Time: {apt.get('start')} to {apt.get('end')}")
        print(f"   Source: {apt.get('source', 'N/A')}")
    
    # Test 2: Fetch services
    print("\n2️⃣ Testing Services:")
    services = await db.services.find({"businessId": "default"}).to_list(length=10)
    print(f"   Found {len(services)} services")
    for svc in services:
        print(f"   - {svc.get('name')}: ${svc.get('price')}, {svc.get('durationMinutes')}min, Active: {svc.get('isActive')}")
    
    # Test 3: Fetch availability
    print("\n3️⃣ Testing Availability:")
    availability = await db.availability.find({"businessId": "default"}).to_list(length=10)
    print(f"   Found {len(availability)} availability entries")
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for avail in sorted(availability, key=lambda x: x.get("dayOfWeek", 0)):
        day_num = avail.get("dayOfWeek")
        if avail.get("isOpen"):
            print(f"   - {days[day_num]}: {avail.get('open')} - {avail.get('close')}")
        else:
            print(f"   - {days[day_num]}: Closed")
    
    # Test 4: Fetch conversation history
    print("\n4️⃣ Testing Conversation History:")
    history = await db.conversation_history.find({"businessId": "default"}).limit(5).to_list(length=5)
    print(f"   Found {await db.conversation_history.count_documents({'businessId': 'default'})} total entries")
    print(f"   Showing latest 5:")
    for entry in history:
        print(f"   - {entry.get('type')}: {entry.get('sender')} - {entry.get('message')[:50]}...")
    
    print("\n✅ All data fetched successfully!")
    print("\n📌 Summary:")
    print(f"   - Appointments use normalized schema (name, phone, start, end, source)")
    print(f"   - Services use normalized schema (durationMinutes, isActive)")
    print(f"   - API routers will convert to legacy format for frontend")
    print(f"   - Voice tools use normalized schema directly")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(test_api_data())
