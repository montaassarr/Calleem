#!/usr/bin/env python3
"""
Debug script to check tenant configuration
Run this to see what's in the database for your tenant
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://REDACTED:REDACTED@localhost:27017/ai_barber_receptionist?authSource=admin")
DB_NAME = os.getenv("MONGO_DB_NAME", "ai_barber_receptionist")

async def check_tenant_config():
    """Check tenant configuration in database"""
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    print("=" * 60)
    print("🔍 Tenant Configuration Debug")
    print("=" * 60)
    print()
    
    # Find user
    username = "montamsallem@gmail.com"
    user = await db.users.find_one({
        "$or": [
            {"username": username},
            {"email": username}
        ]
    })
    
    if not user:
        print(f"❌ User not found: {username}")
        return
    
    user_id = str(user["_id"])
    tenant_id = user.get("tenant_id") or user.get("business_id")
    
    print(f"✅ User found: {user.get('username')}")
    print(f"   User ID: {user_id}")
    print(f"   Tenant ID: {tenant_id}")
    print()
    
    if not tenant_id:
        print("❌ User has no tenant_id!")
        return
    
    # Check business_config
    print(f"🔍 Checking business_config for tenant_id: {tenant_id}")
    config = await db.business_config.find_one({"tenant_id": tenant_id})
    
    if not config:
        print(f"❌ business_config not found for tenant_id: {tenant_id}")
        print()
        print("💡 Creating business_config...")
        
        # Get tenant info for business name
        from bson import ObjectId
        try:
            tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
        except:
            tenant = await db.tenants.find_one({"tenant_id": tenant_id})
        
        business_name = tenant.get("name", "My Business") if tenant else user.get("business_name", "My Business")
        
        # Create business_config
        from datetime import datetime
        business_config = {
            "tenant_id": tenant_id,
            "business_name": business_name,
            "features_enabled": {
                "voice_agent": False
            },
            "api_keys": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.business_config.insert_one(business_config)
        print(f"✅ Created business_config with _id: {result.inserted_id}")
        config = business_config
    else:
        print(f"✅ business_config found")
        print(f"   Business name: {config.get('business_name')}")
        print(f"   API keys count: {len(config.get('api_keys', []))}")
        print(f"   Features enabled: {config.get('features_enabled', {})}")
    
    print()
    
    # Check agent
    print(f"🔍 Checking agent for tenant_id: {tenant_id}")
    agent = await db.agents.find_one({"tenant_id": tenant_id})
    
    if agent:
        print(f"✅ Agent found")
        print(f"   Agent name: {agent.get('name')}")
        print(f"   Status: {agent.get('status')}")
    else:
        print(f"⚠️  No agent found (this is okay, will be auto-created)")
    
    print()
    print("=" * 60)
    print("📋 Summary")
    print("=" * 60)
    print(f"Tenant ID: {tenant_id}")
    print(f"Business Config: {'✅ Exists' if config else '❌ Missing'}")
    print(f"Agent: {'✅ Exists' if agent else '⚠️  Not found'}")
    print()
    print("🔗 Test URL:")
    print(f"   http://localhost:8000/api/v1/voice-agent/tenant-config/{tenant_id}")
    print()
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_tenant_config())

