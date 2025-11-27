import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os

# MongoDB Configuration
MONGO_URL = os.getenv("MONGO_URI", os.getenv("MONGO_URL", "mongodb://REDACTED:REDACTED@localhost:27017/?authSource=admin"))
DB_NAME = os.getenv("MONGO_DB_NAME", "ai_barber_receptionist")

async def promote_user():
    print(f"Connecting to MongoDB at {MONGO_URL}...")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    username = "superadmin_test"
    
    print(f"Finding user '{username}'...")
    user = await db.users.find_one({"username": username})
    
    if user:
        print(f"User found: {user['_id']} (Current Role: {user.get('role')})")
        
        result = await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"role": "super_admin"}}
        )
        
        if result.modified_count > 0:
            print("✅ User promoted to super_admin successfully")
        else:
            print("⚠️ User was already super_admin or update failed")
            
        # Verify
        updated_user = await db.users.find_one({"_id": user["_id"]})
        print(f"New Role: {updated_user.get('role')}")
    else:
        print(f"❌ User '{username}' not found. Please run verify_backend.py first to register the user.")

if __name__ == "__main__":
    asyncio.run(promote_user())
