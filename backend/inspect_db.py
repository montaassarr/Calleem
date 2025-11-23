import asyncio
import logging
from database.mongo_config import connect_to_mongo, get_database
from bson import json_util
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def inspect_appointments():
    print("🔌 Connecting to MongoDB...")
    await connect_to_mongo()
    db = get_database()
    
    print("\n🔍 Inspecting Appointments...")
    appointments = await db.appointments.find({}).to_list(length=100)
    
    print(f"Found {len(appointments)} appointments.")
    
    for apt in appointments:
        # Convert ObjectId and datetime to string for printing
        print(json.dumps(apt, default=json_util.default, indent=2))

if __name__ == "__main__":
    asyncio.run(inspect_appointments())
