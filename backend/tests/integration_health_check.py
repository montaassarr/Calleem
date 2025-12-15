import asyncio
import httpx
import logging
import sys
import os
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("IntegrationTest")

BASE_URL = "http://localhost:8000/api/v1"
TEST_EMAIL = f"test_integr_{int(datetime.now().timestamp())}@example.com"
TEST_PASS = "securePass123!"

async def run_tests():
    logger.info("🚀 Starting Comprehensive Application Health Check")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. Health Check
        try:
            resp = await client.get("http://localhost:8000/health")
            if resp.status_code == 200:
                logger.info("✅ Health check passed")
            else:
                logger.error(f"❌ Health check failed: {resp.status_code}")
                # Don't exit, try to proceed
        except Exception as e:
            logger.error(f"❌ Health check connection error: {e}")
            sys.exit(1)

        # 2. Register User (User Service)
        logger.info(f"👤 Registering new user: {TEST_EMAIL}")
        payload = {
            "email": TEST_EMAIL,
            "username": TEST_EMAIL.split("@")[0],
            "password": TEST_PASS,
            "full_name": "Integration Test User",
            "business_name": "Integration Corp"
        }
        resp = await client.post(f"{BASE_URL}/users/register", json=payload)
        
        if resp.status_code != 201:
            logger.error(f"❌ Registration failed: {resp.text}")
            sys.exit(1)
            
        token_data = resp.json()
        token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        logger.info("✅ User registered and token obtained")

        # 3. Get User Profile (Auth Check)
        resp = await client.get(f"{BASE_URL}/users/me", headers=headers)
        if resp.status_code == 200:
            user_data = resp.json()
            tenant_id = user_data.get("tenant_id")
            logger.info(f"✅ User profile retrieved. Tenant ID: {tenant_id}")
        else:
            logger.error(f"❌ Failed to get profile: {resp.text}")

        # 4. Create Appointment (Appointments Service)
        logger.info("📅 Creating test appointment...")
        start_time = (datetime.utcnow() + timedelta(days=1)).replace(microsecond=0)
        appt_payload = {
            "customer_name": "Test Client",
            "customer_phone": "+1234567890",
            "datetime": start_time.isoformat(),
            "duration_minutes": 30,
            "service": "Integration Test Service",
            "notes": "Created by automation script"
        }
        resp = await client.post(f"{BASE_URL}/appointments/", json=appt_payload, headers=headers)
        
        if resp.status_code == 201:
            appt = resp.json()
            appt_id = appt["id"]
            logger.info(f"✅ Appointment created: {appt_id}")
        else:
            logger.error(f"❌ Failed to create appointment: {resp.text}")
            appt_id = None

        # 5. Check Availability (Appointments Service)
        logger.info("Checking availability...")
        date_str = start_time.strftime("%Y-%m-%d")
        time_str = start_time.strftime("%H:%M")
        resp = await client.get(
            f"{BASE_URL}/appointments/availability/check", 
            params={"date": date_str, "time": time_str, "duration_minutes": 30},
            headers=headers
        )
        if resp.status_code == 200:
            avail = resp.json()
            # It SHOULD be unavailable because we just booked it
            if not avail["available"]:
                 logger.info("✅ Availability check correctly returned unavailable for booked slot")
            else:
                 logger.warning("⚠️ Availability check returned available for a just-booked slot (Concurrency/Logic issue?)")
        else:
             logger.error(f"❌ Failed to check availability: {resp.text}")

        # 6. List Conversations (Conversation Service)
        logger.info("💬 Listing conversations...")
        resp = await client.get(f"{BASE_URL}/conversations/", headers=headers)
        if resp.status_code == 200:
            convs = resp.json()
            logger.info(f"✅ Retrieved {len(convs)} conversations")
        else:
            logger.error(f"❌ Failed to list conversations: {resp.text}")

        # 7. Cancel Appointment
        if appt_id:
            logger.info(f"🚫 Cancelling appointment {appt_id}...")
            resp = await client.post(f"{BASE_URL}/appointments/{appt_id}/cancel", headers=headers)
            if resp.status_code == 200:
                logger.info("✅ Appointment cancelled")
            else:
                logger.error(f"❌ Failed to cancel appointment: {resp.text}")

    logger.info("✨ Integration Tests Completed ✨")

if __name__ == "__main__":
    asyncio.run(run_tests())
