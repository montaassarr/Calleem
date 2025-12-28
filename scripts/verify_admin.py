
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))
MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DATABASE_NAME", "ai_receptionist")

async def check_admin():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    user = await db.users.find_one({"username": "superadmin"})
    if user:
        print(f"FOUND: User {user['username']} with role {user.get('role')}")
    else:
        print("NOT FOUND")

if __name__ == "__main__":
    asyncio.run(check_admin())
