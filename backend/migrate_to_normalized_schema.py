"""
Migration Script: Normalize MongoDB Schema
Converts all existing documents to use the new normalized field names
"""

import asyncio
import sys
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

from database.mongo_config import get_database
from models.normalized_schemas import (
    convert_legacy_appointment_to_normalized,
    convert_legacy_service_to_normalized,
    convert_legacy_availability_to_normalized
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def migrate_appointments(db):
    """Migrate appointments collection to normalized schema"""
    logger.info("=" * 60)
    logger.info("MIGRATING APPOINTMENTS")
    logger.info("=" * 60)
    
    # Get all appointments
    appointments = await db.appointments.find({}).to_list(length=10000)
    logger.info(f"Found {len(appointments)} appointments to migrate")
    
    migrated = 0
    errors = 0
    
    for apt in appointments:
        try:
            # Check if already normalized (has 'start' field)
            if "start" in apt and "end" in apt and "phone" in apt and "name" in apt:
                logger.debug(f"Appointment {apt['_id']} already normalized, skipping")
                continue
            
            # Convert to normalized format
            normalized = convert_legacy_appointment_to_normalized(apt)
            
            # Keep the original _id
            normalized_with_id = {**normalized, "_id": apt["_id"]}
            
            # Replace document
            await db.appointments.replace_one(
                {"_id": apt["_id"]},
                normalized_with_id
            )
            
            migrated += 1
            logger.info(f"✓ Migrated appointment {apt['_id']}: {normalized.get('name')} - {normalized.get('service')}")
            
        except Exception as e:
            errors += 1
            logger.error(f"✗ Failed to migrate appointment {apt['_id']}: {e}")
    
    logger.info(f"\nAppointments Migration Complete:")
    logger.info(f"  - Migrated: {migrated}")
    logger.info(f"  - Errors: {errors}")
    logger.info(f"  - Total: {len(appointments)}")
    return migrated, errors


async def migrate_services(db):
    """Migrate services from business_config to dedicated services collection"""
    logger.info("=" * 60)
    logger.info("MIGRATING SERVICES")
    logger.info("=" * 60)
    
    # Get all business configs
    configs = await db.business_configs.find({}).to_list(length=100)
    logger.info(f"Found {len(configs)} business configs")
    
    migrated = 0
    errors = 0
    
    for config in configs:
        business_id = config.get("businessId") or config.get("business_id") or "default"
        services_list = config.get("services", [])
        
        if not services_list:
            logger.info(f"No services found for business {business_id}")
            continue
        
        for service in services_list:
            try:
                # Convert to normalized format
                normalized = convert_legacy_service_to_normalized(service)
                normalized["businessId"] = business_id
                
                # Upsert into services collection
                await db.services.update_one(
                    {
                        "businessId": business_id,
                        "name": normalized["name"]
                    },
                    {"$set": normalized},
                    upsert=True
                )
                
                migrated += 1
                logger.info(f"✓ Migrated service: {normalized['name']} (${normalized['price']}, {normalized['durationMinutes']}min)")
                
            except Exception as e:
                errors += 1
                logger.error(f"✗ Failed to migrate service {service.get('name')}: {e}")
    
    logger.info(f"\nServices Migration Complete:")
    logger.info(f"  - Migrated: {migrated}")
    logger.info(f"  - Errors: {errors}")
    return migrated, errors


async def migrate_availability(db):
    """Migrate availability from business_config.opening_hours to dedicated availability collection"""
    logger.info("=" * 60)
    logger.info("MIGRATING AVAILABILITY")
    logger.info("=" * 60)
    
    # Get all business configs
    configs = await db.business_configs.find({}).to_list(length=100)
    logger.info(f"Found {len(configs)} business configs")
    
    migrated = 0
    errors = 0
    
    for config in configs:
        business_id = config.get("businessId") or config.get("business_id") or "default"
        opening_hours = config.get("openingHours") or config.get("opening_hours", [])
        
        if not opening_hours:
            logger.info(f"No opening hours found for business {business_id}")
            # Create default availability (Monday-Friday 9-17)
            for day in range(5):
                default_availability = {
                    "businessId": business_id,
                    "dayOfWeek": day,
                    "open": "09:00",
                    "close": "17:00",
                    "breaks": [],
                    "isOpen": True
                }
                await db.availability.update_one(
                    {"businessId": business_id, "dayOfWeek": day},
                    {"$set": default_availability},
                    upsert=True
                )
                migrated += 1
            logger.info(f"Created default availability for business {business_id}")
            continue
        
        for hours in opening_hours:
            try:
                # Convert to normalized format
                normalized = convert_legacy_availability_to_normalized(hours)
                normalized["businessId"] = business_id
                
                # Upsert into availability collection
                await db.availability.update_one(
                    {
                        "businessId": business_id,
                        "dayOfWeek": normalized["dayOfWeek"]
                    },
                    {"$set": normalized},
                    upsert=True
                )
                
                migrated += 1
                day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                day_name = day_names[normalized["dayOfWeek"]]
                status = "Open" if normalized["isOpen"] else "Closed"
                logger.info(f"✓ Migrated availability: {day_name} {status} {normalized.get('open')}-{normalized.get('close')}")
                
            except Exception as e:
                errors += 1
                logger.error(f"✗ Failed to migrate availability: {e}")
    
    logger.info(f"\nAvailability Migration Complete:")
    logger.info(f"  - Migrated: {migrated}")
    logger.info(f"  - Errors: {errors}")
    return migrated, errors


async def migrate_business_config(db):
    """Update business_config collection to use normalized field names"""
    logger.info("=" * 60)
    logger.info("MIGRATING BUSINESS CONFIG")
    logger.info("=" * 60)
    
    configs = await db.business_configs.find({}).to_list(length=100)
    logger.info(f"Found {len(configs)} business configs to migrate")
    
    migrated = 0
    errors = 0
    
    for config in configs:
        try:
            updates = {}
            
            # Normalize field names
            if "business_id" in config and "businessId" not in config:
                updates["businessId"] = config["business_id"]
            
            if "business_name" in config and "name" not in config:
                updates["name"] = config["business_name"]
            
            if "business_phone" in config and "phone" not in config:
                updates["phone"] = config["business_phone"]
            
            if "features_enabled" in config and "features" not in config:
                updates["features"] = config["features_enabled"]
            
            if "voice_config" in config and "voiceConfig" not in config:
                updates["voiceConfig"] = config["voice_config"]
            
            if "ai_config" in config and "aiConfig" not in config:
                updates["aiConfig"] = config["ai_config"]
            
            if "created_at" in config and "createdAt" not in config:
                updates["createdAt"] = config["created_at"]
            
            if "updated_at" in config and "updatedAt" not in config:
                updates["updatedAt"] = config["updated_at"]
            else:
                updates["updatedAt"] = datetime.utcnow()
            
            if updates:
                await db.business_configs.update_one(
                    {"_id": config["_id"]},
                    {"$set": updates}
                )
                migrated += 1
                logger.info(f"✓ Migrated business config: {updates.get('name', config.get('businessId', 'unknown'))}")
            
        except Exception as e:
            errors += 1
            logger.error(f"✗ Failed to migrate business config: {e}")
    
    logger.info(f"\nBusiness Config Migration Complete:")
    logger.info(f"  - Migrated: {migrated}")
    logger.info(f"  - Errors: {errors}")
    return migrated, errors


async def create_conversation_history(db):
    """Create conversation_history collection from existing conversations"""
    logger.info("=" * 60)
    logger.info("CREATING CONVERSATION HISTORY")
    logger.info("=" * 60)
    
    # Check if collection exists and has data
    existing_count = await db.conversation_history.count_documents({})
    if existing_count > 0:
        logger.info(f"conversation_history already has {existing_count} entries, skipping migration")
        return 0, 0
    
    # Get all conversations
    conversations = await db.conversations.find({}).to_list(length=10000)
    logger.info(f"Found {len(conversations)} conversations to migrate")
    
    migrated = 0
    errors = 0
    
    for conv in conversations:
        try:
            phone = conv.get("phone_number", "unknown")
            messages = conv.get("messages", [])
            
            # Determine if voice or text
            metadata = messages[-1].get("metadata", {}) if messages else {}
            is_voice = metadata.get("source") == "voice_agent"
            conv_type = "voice" if is_voice else "text"
            business_id = "default"
            
            for msg in messages:
                role = msg.get("role", "client")
                sender = "client" if role in ["client", "user"] else "agent"
                
                history_entry = {
                    "businessId": business_id,
                    "type": conv_type,
                    "sender": sender,
                    "message": msg.get("text", ""),
                    "timestamp": msg.get("timestamp", datetime.utcnow()),
                    "metadata": {
                        "phone": phone,
                        "conversationId": conv.get("conversation_id")
                    }
                }
                
                await db.conversation_history.insert_one(history_entry)
                migrated += 1
            
            logger.info(f"✓ Migrated {len(messages)} messages from conversation {conv.get('conversation_id')}")
            
        except Exception as e:
            errors += 1
            logger.error(f"✗ Failed to migrate conversation: {e}")
    
    logger.info(f"\nConversation History Migration Complete:")
    logger.info(f"  - Migrated: {migrated}")
    logger.info(f"  - Errors: {errors}")
    return migrated, errors


async def cleanup_old_collections(db, dry_run=True):
    """Remove unnecessary collections and old field names"""
    logger.info("=" * 60)
    logger.info("CLEANUP (DRY RUN)" if dry_run else "CLEANUP")
    logger.info("=" * 60)
    
    # Collections to keep
    essential_collections = {
        "appointments",
        "availability",
        "services",
        "business_configs",
        "conversation_history"
    }
    
    # Get all collections
    all_collections = await db.list_collection_names()
    logger.info(f"Found {len(all_collections)} collections")
    
    # Find collections to remove
    to_remove = [c for c in all_collections if c not in essential_collections and not c.startswith("system.")]
    
    if to_remove:
        logger.info(f"\nCollections to remove: {to_remove}")
        if not dry_run:
            for collection in to_remove:
                await db[collection].drop()
                logger.info(f"✓ Dropped collection: {collection}")
        else:
            logger.info("(Dry run - no collections removed)")
    else:
        logger.info("No collections to remove")
    
    return len(to_remove), 0


async def main():
    """Run all migrations"""
    logger.info("\n" + "=" * 60)
    logger.info("MONGODB SCHEMA NORMALIZATION")
    logger.info("=" * 60 + "\n")
    
    # Import and connect to MongoDB directly
    from motor.motor_asyncio import AsyncIOMotorClient
    from utils.config import settings
    
    logger.info(f"Connecting to MongoDB at {settings.MONGO_URI}/{settings.MONGO_DB_NAME}")
    
    try:
        client = AsyncIOMotorClient(settings.MONGO_URI)
        # Test connection
        await client.admin.command('ping')
        db = client[settings.MONGO_DB_NAME]
        logger.info("Connected to MongoDB successfully\n")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        sys.exit(1)
    
    # Run migrations in order
    total_migrated = 0
    total_errors = 0
    
    # 1. Migrate appointments
    m, e = await migrate_appointments(db)
    total_migrated += m
    total_errors += e
    
    # 2. Migrate services
    m, e = await migrate_services(db)
    total_migrated += m
    total_errors += e
    
    # 3. Migrate availability
    m, e = await migrate_availability(db)
    total_migrated += m
    total_errors += e
    
    # 4. Migrate business config
    m, e = await migrate_business_config(db)
    total_migrated += m
    total_errors += e
    
    # 5. Create conversation history
    m, e = await create_conversation_history(db)
    total_migrated += m
    total_errors += e
    
    # 6. Cleanup (dry run first)
    logger.info("\n" + "=" * 60)
    logger.info("PREVIEW: Collections that would be removed")
    logger.info("=" * 60)
    await cleanup_old_collections(db, dry_run=True)
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("MIGRATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total documents migrated: {total_migrated}")
    logger.info(f"Total errors: {total_errors}")
    logger.info("=" * 60 + "\n")
    
    if total_errors == 0:
        logger.info("✅ Migration completed successfully!")
    else:
        logger.warning(f"⚠️ Migration completed with {total_errors} errors")
    
    # Ask user if they want to cleanup
    cleanup_input = input("\nDo you want to remove non-essential collections? (yes/no): ")
    if cleanup_input.lower() in ["yes", "y"]:
        await cleanup_old_collections(db, dry_run=False)
        logger.info("✅ Cleanup completed!")
    else:
        logger.info("Cleanup skipped")


if __name__ == "__main__":
    asyncio.run(main())
