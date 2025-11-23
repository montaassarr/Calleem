import asyncio
import logging
from datetime import datetime
from database.mongo_config import connect_to_mongo, get_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_database():
    print("🔌 Connecting to MongoDB...")
    await connect_to_mongo()
    db = get_database()
    
    business_id = "default"
    
    print("\n🌱 Seeding Services...")
    services = [
        {"businessId": business_id, "name": "Haircut", "durationMinutes": 30, "price": 30, "isActive": True},
        {"businessId": business_id, "name": "Beard Trim", "durationMinutes": 15, "price": 15, "isActive": True},
        {"businessId": business_id, "name": "Fade", "durationMinutes": 45, "price": 40, "isActive": True},
        {"businessId": business_id, "name": "Hot Shave", "durationMinutes": 30, "price": 25, "isActive": True},
        {"businessId": business_id, "name": "Hair & Beard Combo", "durationMinutes": 60, "price": 50, "isActive": True}
    ]
    
    # Clear existing services
    await db.services.delete_many({})
    await db.services.insert_many(services)
    print(f"✅ Added {len(services)} services")
    
    print("\n🌱 Seeding Availability...")
    # 0=Monday, 6=Sunday
    availability = []
    for day in range(7):
        is_open = day != 6  # Closed on Sunday
        availability.append({
            "businessId": business_id,
            "dayOfWeek": day,
            "isOpen": is_open,
            "open": "09:00",
            "close": "20:00",
            "breaks": [{"start": "13:00", "end": "14:00"}] if is_open else []
        })
        
    await db.availability.delete_many({})
    await db.availability.insert_many(availability)
    print(f"✅ Added availability for 7 days")

if __name__ == "__main__":
    asyncio.run(seed_database())
