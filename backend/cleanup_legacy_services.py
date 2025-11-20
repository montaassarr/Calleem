"""Quick cleanup of legacy services"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from utils.config import settings

async def cleanup():
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    
    # Delete services without businessId (legacy)
    result = await db.services.delete_many({'businessId': {'$exists': False}})
    print(f"Deleted {result.deleted_count} legacy services")
    
    # Drop and recreate old empty collections
    for collection in ['users', 'conversations']:
        try:
            await db[collection].drop()
            print(f"Dropped {collection}")
        except:
            pass
    
    print("Cleanup complete!")

asyncio.run(cleanup())
