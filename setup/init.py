"""
AI Receptionist - Database Setup and Initialization
====================================================
This script initializes the MongoDB database with:
- Database and collections
- Indexes for performance
- Default business configuration
- Admin user account
- Schema validation

This runs as a one-time setup container.
"""

import os
import sys
import time
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, OperationFailure
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def wait_for_mongodb(mongo_uri: str, max_retries: int = 30, retry_interval: int = 2):
    """Wait for MongoDB to be ready"""
    logger.info("Waiting for MongoDB to be ready...")
    
    for attempt in range(max_retries):
        try:
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            logger.info("✓ MongoDB is ready!")
            return client
        except ConnectionFailure:
            logger.warning(f"MongoDB not ready yet (attempt {attempt + 1}/{max_retries})")
            time.sleep(retry_interval)
    
    logger.error("✗ Failed to connect to MongoDB after maximum retries")
    sys.exit(1)


def create_collections(db):
    """Create required collections"""
    logger.info("Creating collections...")
    
    collections = [
        'users',
        'appointments',
        'services',
        'conversations',
        'business_config',
        'availability'
    ]
    
    existing_collections = db.list_collection_names()
    
    for collection_name in collections:
        if collection_name not in existing_collections:
            db.create_collection(collection_name)
            logger.info(f"✓ Created collection: {collection_name}")
        else:
            logger.info(f"⊘ Collection already exists: {collection_name}")


def create_indexes(db):
    """Create indexes for performance"""
    logger.info("Creating indexes...")
    
    # Users collection indexes
    db.users.create_index([("email", ASCENDING)], unique=True)
    db.users.create_index([("phone", ASCENDING)])
    logger.info("✓ Created indexes for 'users' collection")
    
    # Appointments collection indexes
    db.appointments.create_index([("appointment_date", ASCENDING)])
    db.appointments.create_index([("customer_phone", ASCENDING)])
    db.appointments.create_index([("status", ASCENDING)])
    db.appointments.create_index([("created_at", DESCENDING)])
    logger.info("✓ Created indexes for 'appointments' collection")
    
    # Conversations collection indexes
    db.conversations.create_index([("phone_number", ASCENDING)])
    db.conversations.create_index([("created_at", DESCENDING)])
    db.conversations.create_index([("updated_at", DESCENDING)])
    logger.info("✓ Created indexes for 'conversations' collection")
    
    # Services collection indexes
    db.services.create_index([("name", ASCENDING)], unique=True)
    db.services.create_index([("active", ASCENDING)])
    logger.info("✓ Created indexes for 'services' collection")


def seed_default_business_config(db):
    """Seed default business configuration"""
    logger.info("Seeding default business configuration...")
    
    business_name = os.getenv("BUSINESS_NAME", "Royal Fade Barbershop")
    business_email = os.getenv("BUSINESS_EMAIL", "info@royalfade.com")
    business_phone = os.getenv("BUSINESS_PHONE", "+1234567890")
    
    existing_config = db.business_config.find_one({"config_type": "main"})
    
    if not existing_config:
        config = {
            "config_type": "main",
            "business_name": business_name,
            "business_email": business_email,
            "business_phone": business_phone,
            "business_address": os.getenv("BUSINESS_ADDRESS", "123 Main Street"),
            "business_hours": os.getenv("BUSINESS_HOURS", "Monday-Saturday 9:00 AM - 8:00 PM"),
            "timezone": os.getenv("TIMEZONE", "America/New_York"),
            "appointment_duration_minutes": 30,
            "booking_advance_days": 30,
            "cancellation_hours": 24,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        db.business_config.insert_one(config)
        logger.info(f"✓ Created business configuration for: {business_name}")
    else:
        logger.info("⊘ Business configuration already exists")


def seed_default_services(db):
    """Seed default services"""
    logger.info("Seeding default services...")
    
    default_services = [
        {"name": "Haircut", "duration_minutes": 30, "price": 25.00, "description": "Classic haircut", "active": True},
        {"name": "Beard Trim", "duration_minutes": 15, "price": 15.00, "description": "Beard trimming and shaping", "active": True},
        {"name": "Fade", "duration_minutes": 45, "price": 35.00, "description": "Professional fade haircut", "active": True},
        {"name": "Hot Shave", "duration_minutes": 30, "price": 30.00, "description": "Traditional hot towel shave", "active": True},
        {"name": "Hair & Beard Combo", "duration_minutes": 60, "price": 45.00, "description": "Haircut and beard trim combo", "active": True},
    ]
    
    for service in default_services:
        existing = db.services.find_one({"name": service["name"]})
        if not existing:
            service["created_at"] = datetime.utcnow()
            service["updated_at"] = datetime.utcnow()
            db.services.insert_one(service)
            logger.info(f"✓ Created service: {service['name']}")
        else:
            logger.info(f"⊘ Service already exists: {service['name']}")


def create_admin_user(db):
    """Create admin user account"""
    logger.info("Creating admin user...")
    
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "changeme")
    
    existing_admin = db.users.find_one({"email": admin_email})
    
    if not existing_admin:
        # Note: In production, use proper password hashing (bcrypt, argon2)
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        admin_user = {
            "email": admin_email,
            "password_hash": pwd_context.hash(admin_password),
            "full_name": "System Administrator",
            "role": "admin",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        db.users.insert_one(admin_user)
        logger.info(f"✓ Created admin user: {admin_email}")
        logger.warning(f"⚠ Default password is set. Please change it immediately!")
    else:
        logger.info("⊘ Admin user already exists")


def validate_setup(db):
    """Validate that setup completed successfully"""
    logger.info("Validating setup...")
    
    required_collections = ['users', 'appointments', 'services', 'conversations', 'business_config']
    existing_collections = db.list_collection_names()
    
    for collection in required_collections:
        if collection not in existing_collections:
            logger.error(f"✗ Missing collection: {collection}")
            return False
        logger.info(f"✓ Collection exists: {collection}")
    
    # Check if we have at least one service
    service_count = db.services.count_documents({})
    if service_count == 0:
        logger.error("✗ No services found in database")
        return False
    logger.info(f"✓ Found {service_count} services")
    
    # Check if business config exists
    config = db.business_config.find_one({"config_type": "main"})
    if not config:
        logger.error("✗ Business configuration not found")
        return False
    logger.info("✓ Business configuration exists")
    
    logger.info("✅ Setup validation passed!")
    return True


def main():
    """Main setup function"""
    logger.info("=" * 60)
    logger.info("AI Receptionist - Database Setup")
    logger.info("=" * 60)
    
    # Get MongoDB connection details from environment
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB_NAME", "ai_receptionist")
    
    if not mongo_uri:
        logger.error("✗ MONGO_URI environment variable not set")
        sys.exit(1)
    
    logger.info(f"Database: {db_name}")
    logger.info(f"MongoDB URI: {mongo_uri.split('@')[1] if '@' in mongo_uri else 'localhost'}")
    
    # Connect to MongoDB
    client = wait_for_mongodb(mongo_uri)
    db = client[db_name]
    
    try:
        # Run setup steps
        create_collections(db)
        create_indexes(db)
        seed_default_business_config(db)
        seed_default_services(db)
        
        # Create admin user (requires passlib)
        try:
            create_admin_user(db)
        except ImportError:
            logger.warning("⚠ passlib not installed, skipping admin user creation")
        
        # Validate setup
        if validate_setup(db):
            logger.info("=" * 60)
            logger.info("✅ Setup completed successfully!")
            logger.info("=" * 60)
            sys.exit(0)
        else:
            logger.error("=" * 60)
            logger.error("✗ Setup validation failed")
            logger.error("=" * 60)
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"✗ Setup failed with error: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()
