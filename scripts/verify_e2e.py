import asyncio
import httpx
import os
import sys
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "montamsallem@gmail.com"
PASSWORD = "Mariemmontassar03$"

async def verify_flow():
    print(f"🚀 Starting E2E Verification against {BASE_URL}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Login
        print("\n🔐 Authenticating...")
        try:
            login_res = await client.post(
                f"{BASE_URL}/users/token",
                data={"username": EMAIL, "password": PASSWORD},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            login_res.raise_for_status()
            token = login_res.json()["access_token"]
            print("✅ Login successful")
        except Exception as e:
            print(f"⚠️ Login failed: {e}")
            if login_res.status_code == 401 or login_res.status_code == 404:
                print("🆕 Attempting to REGISTER user...")
                try:
                    reg_res = await client.post(
                        f"{BASE_URL}/users/register",
                        json={
                            "email": EMAIL,
                            "password": PASSWORD,
                            "username": EMAIL.split("@")[0],
                            "full_name": "Test Administrator",
                            "business_name": "Test Barber Shop"
                        }
                    )
                    reg_res.raise_for_status()
                    print("✅ Registration successful. Retrying login...")
                    # Retry Login
                    login_res = await client.post(
                        f"{BASE_URL}/users/token",
                        data={"username": EMAIL, "password": PASSWORD},
                        headers={"Content-Type": "application/x-www-form-urlencoded"}
                    )
                    login_res.raise_for_status()
                    token = login_res.json()["access_token"]
                    print("✅ Login successful")
                except Exception as reg_e:
                    print(f"❌ Registration failed: {reg_e}")
                    if 'reg_res' in locals():
                        print(f"Reg Response: {reg_res.text}")
                    return
            else:
                return

        headers = {"Authorization": f"Bearer {token}"}

        # 2. Get User/Tenant Info
        print("\n👤 Grabbing User Info...")
        me_res = await client.get(f"{BASE_URL}/users/me", headers=headers)
        me_res.raise_for_status()
        user_data = me_res.json()
        tenant_id = user_data["tenant_id"]
        print(f"✅ User found: {user_data['email']}")
        print(f"✅ Tenant ID: {tenant_id}")

        # 3. Simulate Chat Flow
        session_id = f"test-e2e-{int(datetime.now().timestamp())}"
        print(f"\n💬 Starting Chat Simulation (Session: {session_id})")

        # Step 3a: Initial Greeting / Booking Request
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        chat_1_payload = {
            "message": f"I want to book an appointment for {tomorrow} at 12:00 PM",
            "session_id": session_id,
            "tenant_id": tenant_id
        }
        print(f"--> User: {chat_1_payload['message']}")
        chat_1 = await client.post(f"{BASE_URL}/ai/chat", json=chat_1_payload)
        print(f"<-- AI: {chat_1.json()['response']}")
        await asyncio.sleep(5)

        # Step 3b: Provide Details
        chat_2_payload = {
            "message": "My name is Auto Tester, phone 555-0199, and email auto@test.com",
            "session_id": session_id,
            "tenant_id": tenant_id
        }
        print(f"--> User: {chat_2_payload['message']}")
        chat_2 = await client.post(f"{BASE_URL}/ai/chat", json=chat_2_payload)
        print(f"<-- AI: {chat_2.json()['response']}")
        await asyncio.sleep(5)

        # Step 3c: Confirm
        chat_3_payload = {
            "message": "Yes, please confirm the booking",
            "session_id": session_id,
            "tenant_id": tenant_id
        }
        print(f"--> User: {chat_3_payload['message']}")
        chat_3 = await client.post(f"{BASE_URL}/ai/chat", json=chat_3_payload)
        print(f"<-- AI: {chat_3.json()['response']}")
        await asyncio.sleep(5)

        # 4. Verify Booking in DB
        print("\n📅 Verifying Appointment in Database...")
        # Brief pause to allow async booking to complete if needed
        await asyncio.sleep(2)
        
        appointments_res = await client.get(f"{BASE_URL}/appointments/", headers=headers)
        appointments = appointments_res.json()
        
        # Look for our booking
        found = False
        for appt in appointments:
            # Check client name and date in start_time
            if appt.get("client_name") == "Auto Tester" and tomorrow in appt.get("start_time", ""):
                found = True
                print(f"✅ FOUND Appointment: {appt['start_time']} for {appt['client_name']}")
                break
        
        if not found:
            print("❌ Appointment NOT found in the list.")
            print(f"Latest appointments: {[a.get('client_name') + ' ' + a.get('start_time', '') for a in appointments[:3]]}")
        else:
            print("\n🎉 E2E TEST PASSED: Full flow verified successfully.")

if __name__ == "__main__":
    asyncio.run(verify_flow())
