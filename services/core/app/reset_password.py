"""
Script to reset admin password
"""

import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from utils.config import settings

pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')


async def reset_password():
    """Reset admin password"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    
    try:
        # Find admin user
        admin = await db.users.find_one({'username': 'admin'})
        
        if not admin:
            print('❌ Admin user not found! Run create_admin.py first.')
            return
        
        # New password
        new_password = 'admin123'
        hashed_password = pwd_context.hash(new_password)
        
        # Update password
        result = await db.users.update_one(
            {'username': 'admin'},
            {
                '$set': {
                    'hashed_password': hashed_password,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        if result.modified_count > 0:
            print('✅ Password reset successfully!')
            print(f'Username: admin')
            print(f'New Password: {new_password}')
            print('\n⚠️  Please change this password after logging in!')
        else:
            print('ℹ️  Password was already set to default.')
            print(f'Username: admin')
            print(f'Password: {new_password}')
        
    finally:
        client.close()


if __name__ == '__main__':
    asyncio.run(reset_password())
