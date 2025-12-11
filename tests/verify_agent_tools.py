import asyncio
import httpx
import sys

# Config
BACKEND_URL = "http://localhost:8000/api/v1"
TENANT_ID = "69319a0e7436614acd86b5d5" # Example tenant
EMAIL = "test@example.com"

async def test_tools():
    print("🧪 Testing Agent Tools (Direct to Backend)...")
    
    async with httpx.AsyncClient() as client:
        # 1. BOOK (Setup)
        print("\n1. Booking Appointment...")
        book_res = await client.post(
            f"{BACKEND_URL}/appointments/agent/book",
            json={
                "customer_name": "Test User",
                "customer_email": EMAIL,
                "date": "2025-12-25",
                "time": "10:00",
                "service": "Test Service"
            },
            headers={"X-Tenant-ID": TENANT_ID}
        )
        if book_res.status_code not in [200, 201]:
            print(f"❌ Booking failed: {book_res.text}")
            return
        print("✅ Booking successful")

        # 2. LIST
        print("\n2. Listing Appointments...")
        list_res = await client.post(
            f"{BACKEND_URL}/appointments/agent/list",
            json={"email": EMAIL},
            headers={"X-Tenant-ID": TENANT_ID}
        )
        if list_res.status_code == 200:
            apps = list_res.json().get("appointments", [])
            print(f"✅ Found {len(apps)} appointments")
        else:
            print(f"❌ List failed: {list_res.text}")

        # 3. UPDATE
        print("\n3. Updating Appointment...")
        update_res = await client.post(
            f"{BACKEND_URL}/appointments/agent/update",
            json={
                "email": EMAIL,
                "original_time": "2025-12-25 10:00",
                "new_start_time": "2025-12-25T14:00:00"
            },
            headers={"X-Tenant-ID": TENANT_ID}
        )
        if update_res.status_code == 200 and update_res.json().get("success"):
            print("✅ Update successful")
        else:
            print(f"❌ Update failed: {update_res.text}")

        # 4. CANCEL
        print("\n4. Cancelling Appointment...")
        cancel_res = await client.post(
            f"{BACKEND_URL}/appointments/agent/cancel",
            json={
                "email": EMAIL,
                "date": "2025-12-25"
            },
            headers={"X-Tenant-ID": TENANT_ID}
        )
        if cancel_res.status_code == 200 and cancel_res.json().get("success"):
            print("✅ Cancel successful")
        else:
            print(f"❌ Cancel failed: {cancel_res.text}")

if __name__ == "__main__":
    asyncio.run(test_tools())
