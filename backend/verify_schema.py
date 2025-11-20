"""
Verification Script: Check MongoDB Schema Normalization
Validates that all collections use the correct normalized field names
"""

import asyncio
import sys
from datetime import datetime
from typing import Dict, Any, List
import logging

from database.mongo_config import get_database

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def print_header(text: str):
    """Print formatted header"""
    logger.info("\n" + "=" * 70)
    logger.info(f"  {text}")
    logger.info("=" * 70)


def print_success(text: str):
    """Print success message"""
    logger.info(f"✅ {text}")


def print_error(text: str):
    """Print error message"""
    logger.error(f"❌ {text}")


def print_warning(text: str):
    """Print warning message"""
    logger.warning(f"⚠️  {text}")


def print_info(text: str):
    """Print info message"""
    logger.info(f"ℹ️  {text}")


async def check_appointments(db) -> bool:
    """Verify appointments collection schema"""
    print_header("CHECKING APPOINTMENTS COLLECTION")
    
    count = await db.appointments.count_documents({})
    logger.info(f"Total appointments: {count}")
    
    if count == 0:
        print_warning("No appointments found")
        return True
    
    # Get sample appointments
    appointments = await db.appointments.find({}).limit(5).to_list(length=5)
    
    required_fields = ["businessId", "name", "phone", "service", "start", "end", "source"]
    optional_fields = ["notes", "status", "createdAt", "updatedAt"]
    legacy_fields = ["client_name", "client_phone", "datetime", "scheduled_time", "business_id"]
    
    all_valid = True
    
    for i, apt in enumerate(appointments, 1):
        logger.info(f"\n📋 Appointment {i}/{len(appointments)}:")
        
        # Check required fields
        missing = [f for f in required_fields if f not in apt]
        if missing:
            print_error(f"Missing required fields: {missing}")
            all_valid = False
        else:
            print_success("All required fields present")
        
        # Check for legacy fields
        legacy_found = [f for f in legacy_fields if f in apt]
        if legacy_found:
            print_warning(f"Legacy fields found (should be removed): {legacy_found}")
            all_valid = False
        
        # Display appointment details
        if all(f in apt for f in required_fields):
            logger.info(f"   Name: {apt.get('name')}")
            logger.info(f"   Phone: {apt.get('phone')}")
            logger.info(f"   Service: {apt.get('service')}")
            logger.info(f"   Start: {apt.get('start')}")
            logger.info(f"   End: {apt.get('end')}")
            logger.info(f"   Source: {apt.get('source')}")
            logger.info(f"   Status: {apt.get('status', 'N/A')}")
    
    if all_valid:
        print_success(f"All {count} appointments use normalized schema")
    
    return all_valid


async def check_availability(db) -> bool:
    """Verify availability collection schema"""
    print_header("CHECKING AVAILABILITY COLLECTION")
    
    count = await db.availability.count_documents({})
    logger.info(f"Total availability entries: {count}")
    
    if count == 0:
        print_error("No availability entries found!")
        print_info("Run migration script to create default availability")
        return False
    
    # Get all availability entries
    entries = await db.availability.find({}).to_list(length=100)
    
    required_fields = ["businessId", "dayOfWeek", "open", "close", "isOpen"]
    optional_fields = ["breaks"]
    
    all_valid = True
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Group by business
    businesses = {}
    for entry in entries:
        bid = entry.get("businessId", "unknown")
        if bid not in businesses:
            businesses[bid] = []
        businesses[bid].append(entry)
    
    for business_id, business_entries in businesses.items():
        logger.info(f"\n🏢 Business: {business_id}")
        
        # Check for all 7 days
        days_covered = set(e.get("dayOfWeek") for e in business_entries)
        missing_days = set(range(7)) - days_covered
        
        if missing_days:
            print_warning(f"Missing days: {[day_names[d] for d in missing_days]}")
        
        for entry in sorted(business_entries, key=lambda x: x.get("dayOfWeek", 0)):
            day = entry.get("dayOfWeek", -1)
            day_name = day_names[day] if 0 <= day <= 6 else "Invalid"
            
            # Check required fields
            missing = [f for f in required_fields if f not in entry]
            if missing:
                print_error(f"{day_name}: Missing fields {missing}")
                all_valid = False
            else:
                status = "Open" if entry.get("isOpen") else "Closed"
                hours = f"{entry.get('open', 'N/A')}-{entry.get('close', 'N/A')}"
                breaks = entry.get("breaks", [])
                break_info = f", {len(breaks)} breaks" if breaks else ""
                logger.info(f"   {day_name}: {status} {hours}{break_info}")
    
    if all_valid:
        print_success(f"All {count} availability entries use normalized schema")
    
    return all_valid


async def check_services(db) -> bool:
    """Verify services collection schema"""
    print_header("CHECKING SERVICES COLLECTION")
    
    count = await db.services.count_documents({})
    logger.info(f"Total services: {count}")
    
    if count == 0:
        print_error("No services found!")
        print_info("Run migration script to extract services from business_config")
        return False
    
    # Get all services
    services = await db.services.find({}).to_list(length=100)
    
    required_fields = ["businessId", "name", "durationMinutes", "price"]
    optional_fields = ["isActive"]
    legacy_fields = ["duration_minutes", "is_active"]
    
    all_valid = True
    
    # Group by business
    businesses = {}
    for service in services:
        bid = service.get("businessId", "unknown")
        if bid not in businesses:
            businesses[bid] = []
        businesses[bid].append(service)
    
    for business_id, business_services in businesses.items():
        logger.info(f"\n🏢 Business: {business_id}")
        
        for svc in business_services:
            # Check required fields
            missing = [f for f in required_fields if f not in svc]
            if missing:
                print_error(f"Service '{svc.get('name', 'unknown')}': Missing fields {missing}")
                all_valid = False
            else:
                active = "✓" if svc.get("isActive", True) else "✗"
                logger.info(f"   {active} {svc['name']}: ${svc['price']}, {svc['durationMinutes']}min")
            
            # Check for legacy fields
            legacy_found = [f for f in legacy_fields if f in svc]
            if legacy_found:
                print_warning(f"Service '{svc.get('name')}': Legacy fields {legacy_found}")
                all_valid = False
    
    if all_valid:
        print_success(f"All {count} services use normalized schema")
    
    return all_valid


async def check_business_config(db) -> bool:
    """Verify business_config collection schema"""
    print_header("CHECKING BUSINESS_CONFIG COLLECTION")
    
    count = await db.business_configs.count_documents({})
    logger.info(f"Total business configs: {count}")
    
    if count == 0:
        print_error("No business config found!")
        return False
    
    # Get all configs
    configs = await db.business_configs.find({}).to_list(length=10)
    
    required_fields = ["businessId", "name", "phone", "timezone"]
    recommended_fields = ["openingHours", "services", "features"]
    
    all_valid = True
    
    for config in configs:
        business_id = config.get("businessId", config.get("business_id", "unknown"))
        logger.info(f"\n🏢 Business: {business_id}")
        
        # Check required fields
        missing = [f for f in required_fields if f not in config]
        if missing:
            print_warning(f"Missing recommended fields: {missing}")
        else:
            logger.info(f"   Name: {config.get('name')}")
            logger.info(f"   Phone: {config.get('phone')}")
            logger.info(f"   Timezone: {config.get('timezone')}")
        
        # Check features
        features = config.get("features", config.get("features_enabled", {}))
        voice_enabled = features.get("voiceAgent", features.get("voice_agent", False))
        logger.info(f"   Voice Agent: {'Enabled' if voice_enabled else 'Disabled'}")
        
        # Check voice config
        voice_config = config.get("voiceConfig", config.get("voice_config"))
        if voice_config:
            print_success("Voice configuration present")
        else:
            print_warning("No voice configuration found")
    
    if all_valid:
        print_success(f"All {count} business configs verified")
    
    return all_valid


async def check_conversation_history(db) -> bool:
    """Verify conversation_history collection schema"""
    print_header("CHECKING CONVERSATION_HISTORY COLLECTION")
    
    count = await db.conversation_history.count_documents({})
    logger.info(f"Total conversation entries: {count}")
    
    if count == 0:
        print_warning("No conversation history found (this is OK if no conversations yet)")
        return True
    
    # Get sample entries
    entries = await db.conversation_history.find({}).limit(10).to_list(length=10)
    
    required_fields = ["businessId", "type", "sender", "message", "timestamp"]
    optional_fields = ["metadata"]
    
    all_valid = True
    
    # Count by type
    voice_count = await db.conversation_history.count_documents({"type": "voice"})
    text_count = await db.conversation_history.count_documents({"type": "text"})
    
    logger.info(f"\n📊 Message breakdown:")
    logger.info(f"   Voice messages: {voice_count}")
    logger.info(f"   Text messages: {text_count}")
    
    logger.info(f"\n📝 Sample messages:")
    for i, entry in enumerate(entries[:5], 1):
        # Check required fields
        missing = [f for f in required_fields if f not in entry]
        if missing:
            print_error(f"Entry {i}: Missing fields {missing}")
            all_valid = False
        else:
            msg_type = entry.get("type", "unknown")
            sender = entry.get("sender", "unknown")
            message = entry.get("message", "")[:50]
            logger.info(f"   [{msg_type}] {sender}: {message}...")
    
    if all_valid:
        print_success(f"All {count} conversation entries use normalized schema")
    
    return all_valid


async def check_collections_list(db) -> bool:
    """List all collections and identify non-essential ones"""
    print_header("CHECKING DATABASE COLLECTIONS")
    
    all_collections = await db.list_collection_names()
    
    essential = ["appointments", "availability", "services", "business_configs", "conversation_history"]
    system = [c for c in all_collections if c.startswith("system.")]
    extra = [c for c in all_collections if c not in essential and not c.startswith("system.")]
    
    logger.info(f"\n✅ Essential collections ({len([c for c in all_collections if c in essential])}/5):")
    for col in essential:
        if col in all_collections:
            count = await db[col].count_documents({})
            print_success(f"{col}: {count} documents")
        else:
            print_error(f"{col}: MISSING!")
    
    if extra:
        logger.info(f"\n⚠️  Extra collections (consider removing):")
        for col in extra:
            count = await db[col].count_documents({})
            logger.info(f"   - {col}: {count} documents")
    
    if system:
        logger.info(f"\nℹ️  System collections: {len(system)}")
    
    return len([c for c in all_collections if c in essential]) == 5


async def main():
    """Run all verification checks"""
    print_header("MONGODB SCHEMA VERIFICATION")
    
    # Import and connect to MongoDB directly
    from motor.motor_asyncio import AsyncIOMotorClient
    from utils.config import settings
    
    try:
        client = AsyncIOMotorClient(settings.MONGO_URI)
        # Test connection
        await client.admin.command('ping')
        db = client[settings.MONGO_DB_NAME]
        print_success("Connected to MongoDB")
    except Exception as e:
        print_error("Failed to connect to database!")
        logger.error(f"Connection error: {e}")
        sys.exit(1)
    
    # Run all checks
    results = {}
    
    results["collections"] = await check_collections_list(db)
    results["appointments"] = await check_appointments(db)
    results["availability"] = await check_availability(db)
    results["services"] = await check_services(db)
    results["business_config"] = await check_business_config(db)
    results["conversation_history"] = await check_conversation_history(db)
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    logger.info(f"\nResults: {passed}/{total} checks passed\n")
    
    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}  {check.replace('_', ' ').title()}")
    
    if passed == total:
        print_header("✅ ALL CHECKS PASSED - SCHEMA IS NORMALIZED!")
    else:
        print_header("⚠️  SOME CHECKS FAILED - RUN MIGRATION SCRIPT")
        print_info("Run: python migrate_to_normalized_schema.py")
    
    logger.info("")


if __name__ == "__main__":
    asyncio.run(main())
