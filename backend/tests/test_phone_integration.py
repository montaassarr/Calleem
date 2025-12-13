import asyncio
import httpx
import logging
from pymongo import MongoClient
from bson import ObjectId
import os
import sys

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import settings
from utils.encryption import decrypt_value
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_TENANT_EMAIL = "montamsallem@gmail.com"

# Mock Twilio Credentials for testing logic (fake values)
MOCK_TWILIO_SID = "AC" + "a" * 32
MOCK_TWILIO_TOKEN = "b" * 32
MOCK_PHONE_NUMBER = "+15551234567"

async def test_phone_integration():
    """Test the complete phone number integration flow"""
    
    logger.info("🧪 STARTING PHONE INTEGRATION TEST")
    
    # 1. Get Tenant ID
    # ----------------
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    tenant = db.tenants.find_one({"email": TEST_TENANT_EMAIL})
    
    if not tenant:
        logger.warning(f"⚠️ Tenant {TEST_TENANT_EMAIL} not found! Creating test tenant...")
        # Create a basic test tenant
        new_tenant = {
            "name": "Test Tenant",
            "email": TEST_TENANT_EMAIL,
            "status": "active",
            "plan": "pro",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "settings": {
                "business_name": "Test Barber Shop",
                "timezone": "UTC"
            }
        }
        result = db.tenants.insert_one(new_tenant)
        tenant = db.tenants.find_one({"_id": result.inserted_id})
        logger.info(f"✅ Created test tenant: {tenant['_id']}")
    
    tenant_id = str(tenant["_id"])
    
    # Ensure tenant has a Vapi assistant for the test
    if not tenant.get("vapi_assistant_id"):
        logger.warning("⚠️ Tenant has no Vapi Assistant ID. Setting a dummy one for testing...")
        db.tenants.update_one(
            {"_id": tenant["_id"]},
            {"$set": {"vapi_assistant_id": "dummy-assistant-id"}}
        )
        logger.info("✅ Set dummy assistant ID")

    # 2. Test Provisioning (with Mock Vapi Service if needed, or real errors)
    # ---------------------------------------------------------------------
    logger.info("\n📞 Testing Provisioning Endpoint...")
    
    # Note: This will fail if Vapi credentials in .env are invalid or if we use fake Twilio creds against real Vapi API
    # But we want to test that the *endpoint* handles the request correctly up to the external call
    
    provision_payload = {
        "twilio_account_sid": MOCK_TWILIO_SID,
        "twilio_auth_token": MOCK_TWILIO_TOKEN,
        "phone_number": MOCK_PHONE_NUMBER
    }
    
    async with httpx.AsyncClient() as http_client:
        try:
            response = await http_client.post(
                f"{BASE_URL}/phone-numbers/provision/{tenant_id}",
                json=provision_payload
            )
            
            # We expect a 400 or 500 because of fake credentials, but let's check the response structure
            if response.status_code == 200:
                logger.info("✅ Provisioning successful (Unexpected with fake creds!)")
                data = response.json()
                logger.info(f"Response: {data}")
            else:
                logger.info(f"ℹ️ Provisioning failed as expected with fake creds: {response.status_code}")
                logger.info(f"Error detail: {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Request failed: {e}")

    # 3. Verify Database Storage (Manual Injection for Status Test)
    # ----------------------------------------------------------
    logger.info("\n💾 Simulating successful provisioning in DB...")
    
    # Manually inject encrypted config to test status endpoint and encryption
    from services.twilio_service import twilio_service
    
    encrypted = twilio_service.encrypt_credentials(MOCK_TWILIO_SID, MOCK_TWILIO_TOKEN)
    
    phone_config = {
        "vapi_phone_number_id": "mock-vapi-phone-id",
        "phone_number": MOCK_PHONE_NUMBER,
        "phone_provider": "twilio",
        "twilio_credentials": {
            "account_sid_encrypted": encrypted["account_sid_encrypted"],
            "auth_token_encrypted": encrypted["auth_token_encrypted"],
            "phone_number": MOCK_PHONE_NUMBER,
            "credential_id": "mock-credential-id"
        },
        "is_active": True,
        "created_at": datetime.utcnow()
    }
    
    db.tenants.update_one(
        {"_id": tenant["_id"]},
        {"$set": {"phone_config": phone_config}}
    )
    logger.info("✅ Injected mock phone config into DB")
    
    # 4. Test Status Endpoint
    # ---------------------
    logger.info("\n🔍 Testing Status Endpoint...")
    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(f"{BASE_URL}/phone-numbers/status/{tenant_id}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Status response: {data}")
            
            if data["has_phone"] and data["phone_number"] == MOCK_PHONE_NUMBER:
                logger.info("✅ Phone number matches")
            else:
                logger.error("❌ Phone number mismatch")
        else:
            logger.error(f"❌ Status check failed: {response.status_code}")

    # 5. Verify Encryption
    # ------------------
    logger.info("\n🔐 Verifying Encryption...")
    updated_tenant = db.tenants.find_one({"_id": tenant["_id"]})
    creds = updated_tenant["phone_config"]["twilio_credentials"]
    
    decrypted_sid = decrypt_value(creds["account_sid_encrypted"])
    if decrypted_sid == MOCK_TWILIO_SID:
        logger.info("✅ Decryption successful: SID matches")
    else:
        logger.error(f"❌ Decryption failed: {decrypted_sid} != {MOCK_TWILIO_SID}")

    # 6. Test Removal
    # -------------
    logger.info("\n🗑️ Testing Removal Endpoint...")
    async with httpx.AsyncClient() as http_client:
        # We set delete_from_vapi=False to avoid API calls with mock IDs
        response = await http_client.delete(f"{BASE_URL}/phone-numbers/{tenant_id}?delete_from_vapi=False")
        
        if response.status_code == 200:
            logger.info("✅ Removal successful")
        else:
            logger.error(f"❌ Removal failed: {response.status_code}")
            
    # Verify DB update
    final_tenant = db.tenants.find_one({"_id": tenant["_id"]})
    if not final_tenant["phone_config"]["is_active"]:
        logger.info("✅ Database updated: is_active=False")
    else:
        logger.error("❌ Database not updated correctly")

    logger.info("\n✨ TEST COMPLETE")

if __name__ == "__main__":
    asyncio.run(test_phone_integration())
