#!/usr/bin/env python3
"""
One-Time Migration Script: Encrypt Existing API Keys in MongoDB
================================================================

This script encrypts all existing plaintext API keys in the business_config
collection using the utils.security encryption module.

IMPORTANT: Run this ONCE after deploying the encryption changes to production.

Usage:
    python migrate_encrypt_keys.py

The script will:
1. Connect to MongoDB
2. Find all business_config documents
3. Encrypt the following fields if they exist and are not already encrypted:
   - vapi_api_key
   - openai_api_key
   - groq_api_key
   - elevenlabs_api_key
   - twilio_auth_token
   - twilio_account_sid
   - airtable_api_key (may already be encrypted)
4. Update the documents with encrypted values
5. Print a summary of changes

Author: AI Development Team
Date: November 27, 2025
"""

import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient

# Add parent directory to path to import utils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.security import security

# Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://REDACTED:REDACTED@localhost:27017/ai_barber_receptionist?authSource=admin")
DB_NAME = os.getenv("MONGO_DB_NAME", "ai_barber_receptionist")

# Fields to encrypt
FIELDS_TO_ENCRYPT = [
    "vapi_api_key",
    "openai_api_key",
    "groq_api_key",
    "elevenlabs_api_key",
    "twilio_auth_token",
    "twilio_account_sid",
    "airtable_api_key"
]


def is_already_encrypted(value: str) -> bool:
    """
    Check if a value is already encrypted by attempting to decrypt it.
    Encrypted values will successfully decrypt, plaintext will fail.
    """
    if not value:
        return False
    
    try:
        decrypted = security.decrypt(value)
        # If decryption succeeds and returns a value, it was encrypted
        return decrypted is not None
    except Exception:
        # If decryption fails, it's likely plaintext
        return False


async def migrate_encrypt_keys():
    """Main migration function"""
    print(f"🔐 Starting API Key Encryption Migration")
    print(f"📊 Connecting to MongoDB at {MONGO_URI}...")
    
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    # Get all business_config documents
    cursor = db.business_config.find({})
    configs = await cursor.to_list(length=None)
    
    total_configs = len(configs)
    print(f"✅ Found {total_configs} business_config documents")
    
    if total_configs == 0:
        print("⚠️  No documents to migrate. Exiting.")
        return
    
    # Statistics
    updated_count = 0
    skipped_count = 0
    field_stats = {field: {"encrypted": 0, "skipped": 0} for field in FIELDS_TO_ENCRYPT}
    
    # Process each config
    for config in configs:
        tenant_id = config.get("tenant_id", "unknown")
        business_name = config.get("business_name", "unknown")
        config_id = config.get("_id")
        
        print(f"\n📋 Processing: {business_name} (tenant_id: {tenant_id})")
        
        updates = {}
        has_updates = False
        
        # Check each field
        for field in FIELDS_TO_ENCRYPT:
            if field in config and config[field]:
                value = config[field]
                
                # Check if already encrypted
                if is_already_encrypted(value):
                    print(f"  ⏭️  {field}: Already encrypted, skipping")
                    field_stats[field]["skipped"] += 1
                else:
                    # Encrypt the value
                    encrypted_value = security.encrypt(value)
                    updates[field] = encrypted_value
                    has_updates = True
                    print(f"  🔒 {field}: Encrypted")
                    field_stats[field]["encrypted"] += 1
        
        # Update the document if there are changes
        if has_updates:
            await db.business_config.update_one(
                {"_id": config_id},
                {"$set": updates}
            )
            updated_count += 1
            print(f"  ✅ Updated document")
        else:
            skipped_count += 1
            print(f"  ⏭️  No changes needed")
    
    # Print summary
    print("\n" + "="*60)
    print("📊 MIGRATION SUMMARY")
    print("="*60)
    print(f"Total documents processed: {total_configs}")
    print(f"Documents updated: {updated_count}")
    print(f"Documents skipped (no changes): {skipped_count}")
    print("\nField-level statistics:")
    
    for field, stats in field_stats.items():
        total = stats["encrypted"] + stats["skipped"]
        if total > 0:
            print(f"  {field}:")
            print(f"    - Encrypted: {stats['encrypted']}")
            print(f"    - Already encrypted/skipped: {stats['skipped']}")
    
    print("\n✅ Migration complete!")
    print("\n⚠️  IMPORTANT: This script should only be run ONCE.")
    print("    Running it again will attempt to re-encrypt already encrypted values,")
    print("    which will corrupt the data. The script has built-in detection to")
    print("    prevent this, but be cautious.")
    
    client.close()


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║  API Key Encryption Migration Script                        ║
║  WARNING: This will encrypt all plaintext API keys in DB    ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Confirmation prompt
    response = input("Do you want to proceed? (yes/no): ").strip().lower()
    
    if response != "yes":
        print("❌ Migration cancelled.")
        sys.exit(0)
    
    # Run migration
    asyncio.run(migrate_encrypt_keys())
