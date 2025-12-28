
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
    print("\n=== CREATE SUPER ADMIN ===")
    print("This script helps you create or update a Super Admin user.")
    print("To run against PRODUCTION, provide your production MongoDB URI.")
    print("To run LOCALLY, just press Enter.")
    
    env_mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    custom_mongo_url = input(f"\nEnter MongoDB URI [Default: {env_mongo_url}]: ").strip()
    
    mongo_url = custom_mongo_url if custom_mongo_url else env_mongo_url
    
    # Simple check to warn user
    if "localhost" not in mongo_url and "127.0.0.1" not in mongo_url:
        print(f"\n⚠️  WARNING: You are about to connect to a REMOTE database: {mongo_url}")
        confirm = input("Type 'yes' to proceed: ").strip().lower()
        if confirm != "yes":
            print("Operation cancelled.")
            return

    print(f"\nConnecting to database...")
    try:
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000)
        # Verify connection
        await client.server_info()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    # Try to parse DB name from URI
    default_db = "ai_receptionist"
    if "/" in mongo_url and not mongo_url.endswith("/"):
        try:
            # tailored for mongodb+srv://.../dbname?params
            potential_name = mongo_url.rsplit("/", 1)[1].split("?")[0]
            if potential_name:
                default_db = potential_name
        except:
            pass

    print(f"\nTarget Database Name (Check your Railway MONGO_DB_NAME if unsure)")
    db_name = input(f"Enter Database Name [Default: {default_db}]: ").strip() or default_db
    print(f"Using Database: {db_name}")
    db = client[db_name]
    
    print("\n--- User Details ---")
    email = input("Enter email [admin@calleem.com]: ").strip() or "admin@calleem.com"
    username = input("Enter username [superadmin]: ").strip() or "superadmin"
    password = input("Enter password: ").strip()
    
    if not password:
        print("Error: Password is required.")
        return

    print(f"\nCreating/Updating user: {username} ({email})")
    
    # Check existing
    existing = await db.users.find_one({"$or": [{"email": email}, {"username": username}]})
    if existing:
        print(f"Found existing user ID: {existing['_id']}")
        await db.users.update_one(
            {"_id": existing["_id"]},
            {"$set": {
                "role": "super_admin",
                "hashed_password": pwd_context.hash(password)
            }}
        )
        print("✅ User updated to SUPER_ADMIN successfully.")
    else:
        # Create new
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
            "tenant_id": "system", 
            "business_id": "system"
        }
        
        result = await db.users.insert_one(user_doc)
        print(f"✅ Super Admin created successfully (ID: {result.inserted_id})")

if __name__ == "__main__":
    try:
        asyncio.run(create_super_admin())
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
