"""
Script to create an admin user
"""

import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from utils.config import settings

pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')


async def create_admin():
    """Create admin user"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    
    try:
        # Check if admin exists
        existing = await db.users.find_one({'username': 'admin'})
        if existing:
            print('✅ Admin user already exists')
            print(f'Username: {existing["username"]}')
            return
        
        # Create admin user
        hashed_password = pwd_context.hash('admin123')
        admin_user = {
            'username': 'admin',
            'email': 'admin@example.com',
            'full_name': 'Shop Owner',
            'role': 'admin',
            'hashed_password': hashed_password,
            'active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'last_login': None
        }
        
        result = await db.users.insert_one(admin_user)
        print('✅ Admin user created successfully!')
        print(f'Username: admin')
        print(f'Password: admin123')
        print(f'ID: {result.inserted_id}')
        
    finally:
        client.close()


if __name__ == '__main__':
    asyncio.run(create_admin())
