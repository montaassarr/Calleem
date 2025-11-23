import asyncio
import logging
from database.mongo_config import connect_to_mongo, get_database
from bson import json_util
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_conversations():
    print("🔌 Connecting to MongoDB...")
    await connect_to_mongo()
    db = get_database()
    
    print("\n💬 Checking Conversation History...")
    conversations = await db.conversation_history.find({}).sort("timestamp", -1).limit(20).to_list(length=20)
    
    print(f"Found {len(conversations)} recent conversation entries.\n")
    
    for conv in conversations:
        timestamp = conv.get("timestamp", "N/A")
        sender = conv.get("sender", "N/A")
        message = conv.get("message", "")
        phone = conv.get("metadata", {}).get("phone", "N/A")
        
        print(f"[{timestamp}] {sender} ({phone}): {message[:100]}")
    
    print("\n📋 Checking Conversations Collection...")
    convs = await db.conversations.find({}).sort("updated_at", -1).limit(10).to_list(length=10)
    
    print(f"Found {len(convs)} conversations.\n")
    
    for c in convs:
        print(json.dumps(c, default=json_util.default, indent=2))

if __name__ == "__main__":
    asyncio.run(check_conversations())
