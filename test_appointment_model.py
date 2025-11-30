#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, '/home/montassar/Desktop/ai_receptionist/backend')

from datetime import datetime as dt, timedelta
from models.appointments.appointments import AppointmentResponse

# Test creating an AppointmentResponse
test_data = {
    "id": "test123",
    "_id": "test123",
    "client_name": "Test Client",
    "client_phone": "+1234567890",
    "service": "Haircut",
    "start_time": dt.utcnow(),
    "end_time": dt.utcnow() + timedelta(minutes=30),
    "datetime": dt.utcnow(),
    "duration_minutes": 30,
    "tenant_id": "test_tenant",
    "business_id": "test_business",
    "location_id": "test_location",
    "status": "confirmed",
    "source": "api",
    "created_at": dt.utcnow(),
    "updated_at": dt.utcnow()
}

try:
    response = AppointmentResponse(**test_data)
    print("✓ AppointmentResponse created successfully!")
    print(f"  ID: {response.id}")
    print(f"  Client: {response.client_name}")
    print(f"  Duration: {response.duration_minutes} minutes")
except Exception as e:
    print(f"✗ Error creating AppointmentResponse: {e}")
    import traceback
    traceback.print_exc()
