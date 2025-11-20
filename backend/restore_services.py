"""
Restore Services Script
Quickly add the 2 essential services back to the database
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def restore_services():
    """Restore the 2 default services"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.ai_barber_receptionist
    
    print("🔧 Restoring services...")
    
    # Default services with normalized schema
    services = [
        {
            "businessId": "default",
            "name": "Classic Haircut",
            "description": "Traditional men's haircut with styling",
            "durationMinutes": 30,
            "price": 25.0,
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "businessId": "default",
            "name": "Royal Fade",
            "description": "Premium fade haircut with razor line",
            "durationMinutes": 45,
            "price": 40.0,
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
    ]
    
    # Insert services
    for service in services:
        # Check if already exists
        existing = await db.services.find_one({
            "businessId": service["businessId"],
            "name": service["name"]
        })
        
        if existing:
            print(f"   ⚠️  Service '{service['name']}' already exists, skipping")
        else:
            result = await db.services.insert_one(service)
            print(f"   ✅ Added service: {service['name']} (${service['price']}, {service['durationMinutes']}min)")
    
    # Verify
    count = await db.services.count_documents({"businessId": "default"})
    print(f"\n✅ Total services in database: {count}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(restore_services())
