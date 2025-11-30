"""
Create Super Admin User
Run this script to create the default super admin account
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mongo_config import get_database, connect_to_mongo, close_mongo_connection
from routers.users import hash_password
from datetime import datetime


async def create_super_admin():
    """Create super admin user if it doesn't exist"""
    # Connect to DB first
    await connect_to_mongo()
    db = get_database()
    
    # Check if super admin already exists
    existing_admin = await db.users.find_one({"role": "super_admin"})
    
    if existing_admin:
        print("✅ Super admin already exists:")
        print(f"   Email: {existing_admin.get('email')}")
        print(f"   Username: {existing_admin.get('username')}")
        return
    
    # Create super admin
    admin_data = {
        "email": "admin@callflow.ai",
        "username": "admin",
        "hashed_password": hash_password("CallFlow2025!Admin"),
        "full_name": "Super Administrator",
        "phone_number": "+10000000000",
        "role": "super_admin",
        "active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "last_login": None,
        "tenant_id": None,  # Super admin has no tenant
        "business_id": None
    }
    
    result = await db.users.insert_one(admin_data)
    
    print("🎉 Super admin created successfully!")
    print(f"   Email: admin@callflow.ai")
    print(f"   Username: admin")
    print(f"   Password: CallFlow2025!Admin")
    print(f"   ID: {result.inserted_id}")
    print("")
    print("⚠️  IMPORTANT: Change this password immediately after first login!")


if __name__ == "__main__":
    asyncio.run(create_super_admin())
