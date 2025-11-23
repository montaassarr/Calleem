from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def check_configs():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.ai_barber_receptionist
    
    docs = await db.business_configs.find().to_list(length=10)
    print(f"Found {len(docs)} documents")
    
    for i, doc in enumerate(docs):
        print(f"\nDocument {i+1}:")
        print(f"  _id: {doc['_id']}")
        print(f"  business_id: {doc.get('business_id')}")
        print(f"  Has 'business_phone': {'business_phone' in doc}")
        print(f"  Has 'phone_number': {'phone_number' in doc}")
        print(f"  Has 'opening_hours': {'opening_hours' in doc}")
        print(f"  Has 'business_hours': {'business_hours' in doc}")
    
    client.close()

asyncio.run(check_configs())
