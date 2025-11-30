import asyncio
import os
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

# Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://REDACTED:REDACTED@localhost:27017/ai_barber_receptionist?authSource=admin")
DB_NAME = os.getenv("MONGO_DB_NAME", "ai_barber_receptionist")

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

async def seed_data():
    print(f"🌱 Connecting to MongoDB at {MONGO_URI}...")
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    # Clear existing data (optional, but good for clean slate)
    print("🧹 Clearing existing data...")
    await db.users.delete_many({})
    await db.appointments.delete_many({})
    await db.conversations.delete_many({})
    await db.services.delete_many({})
    await db.business_configs.delete_many({})
    
    # Drop indexes to prevent legacy constraints
    print("🧹 Dropping indexes...")
    await db.services.drop_indexes()
    
    # Create compound unique index for services
    await db.services.create_index([("user_id", 1), ("name", 1)], unique=True)
    
    tenants = [
        {"username": "admin", "email": "admin@saas.com", "business": "SaaS Admin", "role": "admin"},
        {"username": "tenant1", "email": "tenant1@example.com", "business": "Royal Fade", "role": "user"},
        {"username": "tenant2", "email": "tenant2@example.com", "business": "Urban Cuts", "role": "user"},
        {"username": "tenant3", "email": "tenant3@example.com", "business": "Style Studio", "role": "user"},
        {"username": "tenant4", "email": "tenant4@example.com", "business": "Elite Grooming", "role": "user"},
        {"username": "tenant5", "email": "tenant5@example.com", "business": "Classic Barbers", "role": "user"},
    ]
    
    services_template = [
        {"name": "Haircut", "duration": 30, "price": 30.0},
        {"name": "Beard Trim", "duration": 15, "price": 15.0},
        {"name": "Full Service", "duration": 60, "price": 50.0},
    ]
    
    print("🚀 Seeding tenants...")
    
    for t in tenants:
        # Create User
        user_doc = {
            "username": t["username"],
            "email": t["email"],
            "hashed_password": get_password_hash("password123"),
            "full_name": f"Owner of {t['business']}",
            "role": t.get("role", "user"),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await db.users.insert_one(user_doc)
        user_id = str(result.inserted_id)
        print(f"  ✅ Created user: {t['username']} (ID: {user_id})")
        
        # Create Business Config
        config_doc = {
            "business_id": user_id,
            "business_name": t["business"],
            "voice_config": {
                "model_provider": "groq",
                "model_name": "llama-3.3-70b-versatile",
                "voice_provider": "openai",
                "voice_id": "alloy",
                "first_message": f"Welcome to {t['business']}. How can I help you?"
            },
            "features_enabled": {"voice_agent": True},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await db.business_configs.insert_one(config_doc)
        
        # Create Services
        for s in services_template:
            service_doc = {
                "user_id": user_id,
                "name": s["name"],
                "description": f"Standard {s['name']} at {t['business']}",
                "duration_minutes": s["duration"],
                "price": s["price"],
                "active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await db.services.insert_one(service_doc)
            
        # Create Appointments
        now = datetime.utcnow()
        for i in range(3):
            appt_time = now + timedelta(days=1, hours=9 + i)
            appt_doc = {
                "user_id": user_id,
                "customer_name": f"Customer {i+1}",
                "customer_phone": f"+1555000000{i}",
                "service_id": "dummy_service_id", # In real scenario, link to actual service ID
                "start_time": appt_time,
                "end_time": appt_time + timedelta(minutes=30),
                "status": "confirmed",
                "created_at": now,
                "updated_at": now
            }
            await db.appointments.insert_one(appt_doc)
            
        # Create Conversations
        conv_doc = {
            "user_id": user_id,
            "customer_phone": "+15551234567",
            "status": "active",
            "channel": "whatsapp",
            "messages": [
                {"role": "user", "content": "Hi, are you open?", "created_at": now},
                {"role": "assistant", "content": f"Yes, {t['business']} is open until 8 PM.", "created_at": now}
            ],
            "created_at": now,
            "updated_at": now
        }
        await db.conversations.insert_one(conv_doc)

    print("✨ Seeding complete! 5 tenants created with data.")

if __name__ == "__main__":
    asyncio.run(seed_data())
