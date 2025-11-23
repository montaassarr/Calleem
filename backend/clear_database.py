import asyncio
import logging
from database.mongo_config import connect_to_mongo, get_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def clear_database():
    print("🔌 Connecting to MongoDB...")
    await connect_to_mongo()
    db = get_database()
    
    print("\n🗑️  Clearing Database Collections...")
    
    # Clear conversations
    result = await db.conversations.delete_many({})
    print(f"✅ Deleted {result.deleted_count} conversations")
    
    # Clear conversation_history
    result = await db.conversation_history.delete_many({})
    print(f"✅ Deleted {result.deleted_count} conversation history entries")
    
    # Clear appointments
    result = await db.appointments.delete_many({})
    print(f"✅ Deleted {result.deleted_count} appointments")
    
    # Clear voice_calls (if any)
    result = await db.voice_calls.delete_many({})
    print(f"✅ Deleted {result.deleted_count} voice calls")
    
    print("\n✨ Database cleared successfully!")

if __name__ == "__main__":
    confirm = input("⚠️  This will DELETE ALL conversations and appointments. Are you sure? (yes/no): ")
    if confirm.lower() == "yes":
        asyncio.run(clear_database())
    else:
        print("❌ Operation cancelled.")
