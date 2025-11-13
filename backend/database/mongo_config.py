"""
MongoDB Configuration and Connection Management
"""

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import logging
from utils.config import settings

logger = logging.getLogger(__name__)

# Global MongoDB client
mongodb_client: AsyncIOMotorClient = None
database = None


async def connect_to_mongo():
    """
    Establish connection to MongoDB
    """
    global mongodb_client, database
    
    try:
        logger.info(f"Connecting to MongoDB at {settings.MONGO_URI}")
        mongodb_client = AsyncIOMotorClient(settings.MONGO_URI)
        
        # Test connection
        await mongodb_client.admin.command('ping')
        
        database = mongodb_client[settings.MONGO_DB_NAME]
        logger.info(f"✅ Successfully connected to MongoDB database: {settings.MONGO_DB_NAME}")
        
        # Create indexes
        await create_indexes()
        
    except ConnectionFailure as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error during MongoDB connection: {e}")
        raise


async def close_mongo_connection():
    """
    Close MongoDB connection
    """
    global mongodb_client
    
    if mongodb_client:
        logger.info("Closing MongoDB connection...")
        mongodb_client.close()
        logger.info("✅ MongoDB connection closed")


async def create_indexes():
    """
    Create database indexes for better query performance
    """
    try:
        # Appointments indexes
        await database.appointments.create_index("client_phone")
        await database.appointments.create_index("datetime")
        await database.appointments.create_index("status")
        await database.appointments.create_index([("datetime", 1), ("status", 1)])
        
        # Conversations indexes
        await database.conversations.create_index("phone_number")
        await database.conversations.create_index("created_at")
        await database.conversations.create_index("conversation_id")
        
        # Services indexes
        await database.services.create_index("name", unique=True)
        await database.services.create_index("active")
        
        # Users indexes
        await database.users.create_index("email", unique=True)
        await database.users.create_index("username", unique=True)
        
        logger.info("✅ Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")


def get_database():
    """
    Get database instance (dependency injection)
    """
    return database
