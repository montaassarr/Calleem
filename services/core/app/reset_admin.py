import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from utils.config import settings
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')

async def reset_admin():
    print(f"Connecting to: {settings.MONGO_URI}")
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    
    # Delete existing admin
    await db.users.delete_one({"username": "admin"})
    print("🗑️  Deleted existing admin user")
    
    # Create new admin
    hashed_password = pwd_context.hash('admin123')
    admin_user = {
        'username': 'admin',
        'email': 'admin@saas.com',
        'full_name': 'System Admin',
        'role': 'admin',
        'tenant_id': None,
        'hashed_password': hashed_password,
        'active': True,
        'created_at': '2023-01-01T00:00:00',
        'updated_at': '2023-01-01T00:00:00',
        'last_login': None
    }
    
    result = await db.users.insert_one(admin_user)
    print(f"✅ Created new admin user with ID: {result.inserted_id}")
    print(f"Hashed Password: {hashed_password}")
    
    # Verify immediately
    user = await db.users.find_one({"username": "admin"})
    if user:
        print("🔍 Verification: User found in DB")
        is_valid = pwd_context.verify('admin123', user['hashed_password'])
        print(f"🔐 Password Verification: {is_valid}")
    else:
        print("❌ Verification: User NOT found in DB")

if __name__ == '__main__':
    asyncio.run(reset_admin())
