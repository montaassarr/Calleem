import httpx
import asyncio
import os

TENANT_ID = "69319a0e7436614acd86b5d5"
BACKEND_URL = "http://localhost:8000"

async def test_booking():
    print(f"Testing booking for tenant {TENANT_ID}...")
    
    payload = {
        "customer_name": "Test User",
        "customer_phone": "+1234567890",
        "customer_email": "test@example.com",
        "service": "Haircut",
        "date": "2025-12-10",
        "time": "14:00",
        "notes": "Test simulated booking from python script"
    }
    
    headers = {"X-Tenant-ID": TENANT_ID}
    
    async with httpx.AsyncClient() as client:
        # 1. Check Availability First
        print("Checking availability...")
        resp = await client.get(
            f"{BACKEND_URL}/api/v1/appointments/agent/availability/slots",
            params={"start_date": "2025-12-10", "end_date": "2025-12-10"},
            headers=headers
        )
        print(f"Availability Status: {resp.status_code}")
        print(f"Availability Response: {resp.text}")

        # 2. Book Appointment
        print("\nBooking appointment...")
        resp = await client.post(
            f"{BACKEND_URL}/api/v1/appointments/agent/book",
            json=payload,
            headers=headers
        )
        print(f"Booking Status: {resp.status_code}")
        print(f"Booking Response: {resp.text}")

if __name__ == "__main__":
    asyncio.run(test_booking())
