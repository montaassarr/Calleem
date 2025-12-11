
import asyncio
import httpx
import os
import json
from datetime import datetime, timedelta

# Constants (assuming local backend)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
TENANT_ID = "69319a0e7436614acd86b5d5" # Hardcoded for test simplification or fetch dynamically
BUSINESS_ID = TENANT_ID # Usually same for single tenant

async def test_endpoint(client, method, url, headers=None, json_data=None, params=None, name=""):
    print(f"\n--- Testing: {name} ---")
    print(f"URL: {url}")
    try:
        if method == "GET":
            response = await client.get(url, headers=headers, params=params)
        elif method == "POST":
            response = await client.post(url, headers=headers, json=json_data)
        
        print(f"Status: {response.status_code}")
        if response.status_code in [200, 201]:
            print("Response:", response.json())
            return response.json()
        else:
            print(f"Error Response: {response.text}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

async def main():
    headers = {"X-Tenant-ID": TENANT_ID}
    async with httpx.AsyncClient(timeout=10.0) as client:
        
        # 1. Test Tenant Config (Agent startup)
        config = await test_endpoint(
            client, "GET", 
            f"{BACKEND_URL}/api/v1/voice-agent/tenant-config/{TENANT_ID}",
            name="Tenant Config"
        )
        if not config:
            print("FAILED: Could not fetch tenant config.")
            return

        # 2. Test List Services (Agent tool)
        services = await test_endpoint(
            client, "GET",
            f"{BACKEND_URL}/api/v1/services/agent/list",
            headers=headers,
            name="List Services"
        )
        if not services:
            print("WARNING: No services returned or failed.")
            service_name = "Haircut" # Fallback
        else:
            service_name = services[0].get("name", "Haircut")
            print(f"Using Service: {service_name}")

        # 3. Test Check Availability (Agent tool)
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        slots = await test_endpoint(
            client, "GET",
            f"{BACKEND_URL}/api/v1/appointments/agent/availability/slots",
            headers=headers,
            params={"start_date": tomorrow, "end_date": tomorrow, "timezone": "America/New_York"},
            name="Check Availability"
        )
        
        target_time = "10:00"
        if slots and slots.get("available_slots"):
            first_slot = slots["available_slots"][0]
            # Extract time from ISO string "2025-12-10T09:00:00-06:00"
            try:
                target_time = first_slot.split("T")[1][:5]
                print(f"Picked Time: {target_time}")
            except:
                pass
        
        # 4. Test Book Appointment (Agent tool)
        booking_payload = {
            "customer_name": "E2E Test User",
            "customer_phone": "+15550001234",
            "customer_email": "e2e@test.com",
            "service": service_name,
            "date": tomorrow,
            "time": target_time,
            "notes": "Automated E2E Test"
        }
        
        booking = await test_endpoint(
            client, "POST",
            f"{BACKEND_URL}/api/v1/appointments/agent/book",
            headers=headers, 
            json_data=booking_payload,
            name="Book Appointment"
        )

        if booking and booking.get("success"):
            print("\n✅ E2E Test Flow Passed!")
        else:
            print("\n❌ E2E Test Flow Failed at Booking.")

if __name__ == "__main__":
    asyncio.run(main())
