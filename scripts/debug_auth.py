
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys
from passlib.context import CryptContext
from dotenv import load_dotenv

# Replicate backend logic EXACTLY
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))
MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DATABASE_NAME", "ai_receptionist")

async def verify_login():
    print(f"Connecting to {MONGO_URL}...")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    username = "superadmin"
    password = "CalleemMaster2025!"
    
    user = await db.users.find_one({"username": username})
    if not user:
        print("User not found!")
        return
        
    print(f"User found: {user['username']}")
    print(f"Stored hash: {user['hashed_password']}")
    
    is_valid = pwd_context.verify(password, user['hashed_password'])
    print(f"Password 'CalleemMaster2025!' matches hash: {is_valid}")
    
    if is_valid:
        print("SUCCESS: Password is correct in DB.")
    else:
        print("FAILURE: Password hash mismatch.")

if __name__ == "__main__":
    asyncio.run(verify_login())
