import asyncio
import httpx
import json
from datetime import datetime
import random

BASE_URL = "http://localhost:8000/api/v1"
WEBHOOK_URL = "http://localhost:8000/api/vapi/webhook"

# Test Data
EMAIL = f"rentcars_{random.randint(1000,9999)}@test.com"
PASSWORD = "password123"
BUSINESS_NAME = "Best Rent Cars"

async def main():
    async with httpx.AsyncClient(timeout=30.0) as client:
        print(f"🚀 Starting Rent Cars Flow Test for {EMAIL}...")

        # 1. Register / Login
        print("\n1️⃣  Registering User...")
        try:
            # Try login first in case checking re-run
            resp = await client.post("http://localhost:8000/api/v1/auth/token", data={"username": EMAIL, "password": PASSWORD})
            if resp.status_code == 200:
                 token = resp.json()["access_token"]
                 print("   ✅ User already exists, logged in.")
            else:
                 # Register
                 reg_data = {
                     "email": EMAIL,
                     "username": EMAIL,  # Use email as username
                     "password": PASSWORD,
                     "full_name": "Car Rental Owner",
                     # "business_name": BUSINESS_NAME # Ignored by model, removing to be safe
                 }
                 resp = await client.post("http://localhost:8000/api/v1/users/register", json=reg_data)
                 resp.raise_for_status()
                 # Register returns token directly
                 token_data = resp.json()
                 if "access_token" in token_data:
                     token = token_data["access_token"]
                 else:
                     # Fallback to login if needed (shouldn't be reached if register succeeds)
                     resp = await client.post("http://localhost:8000/api/v1/users/login", data={"username": EMAIL, "password": PASSWORD})
                     token = resp.json()["access_token"]
                 
                 print("   ✅ User registered and logged in.")
        except Exception as e:
            print(f"   ❌ Registration failed: {e}")
            return

        headers = {"Authorization": f"Bearer {token}"}

        # Get Tenant ID
        resp = await client.get(f"{BASE_URL}/users/me", headers=headers)
        user_data = resp.json()
        tenant_id = user_data["tenant_id"]
        print(f"   ℹ️  Tenant ID: {tenant_id}")

        # 2. Configure Assistant
        print("\n2️⃣  Configuring Vapi Assistant...")
        config_payload = {
            "company_name": BUSINESS_NAME,
            "instructions": "You are a helpful assistant for Best Rent Cars. Help customers rent cars.",
            "voice": "ryan",
            "first_message": "Welcome to Best Rent Cars!"
        }
        
        # We need to use the endpoint that matches the router (vapi.py)
        # vapi.py uses prefix="/api/vapi", not "/api/v1/vapi"
        try:
            resp = await client.post("http://localhost:8000/api/vapi/assistant/me", json=config_payload, headers=headers)
            if resp.status_code == 200:
                print("   ✅ Assistant configured.")
                assistant_data = resp.json()
                assistant_id = assistant_data["assistant_id"]
            else:
                print(f"   ❌ Failed to config assistant: {resp.text}")
                return
        except Exception as e:
            print(f"   ❌ Assistant config error: {e}")
            return

        # 3. Simulate Vapi Call (Webhooks)
        print("\n3️⃣  Simulating Vapi Call Flow...")
        
        # Fake Vapi Call ID
        call_id = f"call_{random.randint(10000,99999)}"
        
        # A. Call Start
        start_payload = {
            "message": {
                "type": "call-start",
                "call": {
                    "id": call_id,
                    "assistantId": assistant_id,
                    "metadata": {"tenant_id": tenant_id},
                    "customer": {"number": "+15550001234"}
                }
            }
        }
        resp = await client.post(WEBHOOK_URL, json=start_payload)
        print(f"   📡 Call Start Webhook: {resp.status_code}")

        # B. Check Availability (Function Call)
        print("   🔍 Checking Availability...")
        avail_payload = {
            "message": {
                "type": "function-call",
                "call": {
                    "id": call_id,
                    "metadata": {"tenant_id": tenant_id}
                },
                "functionCall": {
                    "name": "checkAvailability",
                    "parameters": {"date": datetime.now().strftime("%Y-%m-%d")}
                }
            }
        }
        resp = await client.post(WEBHOOK_URL, json=avail_payload)
        print(f"   📡 Availability Response: {resp.json()}")

        # C. Book Appointment (Function Call)
        print("   📅 Booking Car Rental...")
        book_payload = {
            "message": {
                "type": "function-call",
                "call": {
                    "id": call_id,
                    "metadata": {"tenant_id": tenant_id}
                },
                "functionCall": {
                    "name": "bookAppointment",
                    "parameters": {
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "time": "14:00",
                        "name": "Alice Renter",
                        "phone": "+15550001234",
                        "service": "Tesla Model 3 Rental"
                    }
                }
            }
        }
        resp = await client.post(WEBHOOK_URL, json=book_payload)
        print(f"   📡 Booking Response: {resp.json()}")

        # 4. Verify Booking in System
        print("\n4️⃣  Verifying Booking...")
        resp = await client.get(f"{BASE_URL}/appointments/", headers=headers)
        appointments = resp.json()
        
        found = False
        for appt in appointments:
            if appt.get("client_name") == "Alice Renter":
                print(f"   ✅ SUCCESS: Found booking for {appt.get('client_name')} at {appt.get('datetime', appt.get('start_time'))}")
                found = True
                break
        
        if not found:
            print("   ❌ FAILURE: Booking not found in database.")

if __name__ == "__main__":
    asyncio.run(main())
