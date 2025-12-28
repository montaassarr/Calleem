
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys
from passlib.context import CryptContext
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path to import models if needed, 
# but we'll keep it simple and self-contained
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load env vars
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DATABASE_NAME", "ai_barber_receptionist")

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

async def create_super_admin():
    print(f"Connecting to {MONGO_URL}...")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("\n--- Create Super Admin User ---")
    # Non-interactive mode for agent execution
    email = "admin@calleem.com"
    username = "superadmin"
    password = "CalleemMaster2025!"
    
    print(f"Using email: {email}")
    print(f"Using username: {username}")
    
    if not email or not username or not password:
        print("Error: All fields are required.")
        return

    # Check existing
    existing = await db.users.find_one({"$or": [{"email": email}, {"username": username}]})
    if existing:
        print(f"\nUser already exists (ID: {existing['_id']}). Updating to SUPER_ADMIN...")
        await db.users.update_one(
            {"_id": existing["_id"]},
            {"$set": {
                "role": "super_admin",
                "hashed_password": pwd_context.hash(password) # Update password just in case
            }}
        )
        print("User updated successfully.")
    else:
        # Create new
        print("\nCreating new user...")
        user_doc = {
            "email": email,
            "username": username,
            "full_name": "Super Admin",
            "hashed_password": pwd_context.hash(password),
            "role": "super_admin",
            "active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": None,
            # Super admin might not need a tenant, but good to have one for consistency
            "tenant_id": "system", 
            "business_id": "system"
        }
        
        result = await db.users.insert_one(user_doc)
        print(f"Super Admin created successfully (ID: {result.inserted_id})")

if __name__ == "__main__":
    asyncio.run(create_super_admin())
