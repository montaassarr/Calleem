#!/usr/bin/env python3
"""
Test script to verify AI brain tenant isolation
Tests that different tenants use different API keys
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from motor.motor_asyncio import AsyncIOMotorClient
from ai.conversation_manager import ConversationManager
from database.mongo_config import get_database
from utils.security import security
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_tenant_isolation():
    """Test that different tenants use different API keys"""
    
    logger.info("🧪 Testing AI Brain Tenant Isolation")
    logger.info("=" * 60)
    
    # Connect to database
    db = await get_database()
    
    # Get all tenants
    tenants = await db.tenants.find({}).to_list(length=10)
    logger.info(f"Found {len(tenants)} tenants")
    
    if len(tenants) < 2:
        logger.warning("⚠️  Need at least 2 tenants to test isolation")
        return
    
    # Check business_config for each tenant
    for tenant in tenants[:2]:  # Test first 2
        tenant_id = tenant.get("tenant_id")
        logger.info(f"\n📋 Checking Tenant: {tenant_id}")
        logger.info(f"   Business Name: {tenant.get('business_name')}")
        
        # Get business config
        config = await db.business_config.find_one({"tenant_id": tenant_id})
        
        if not config:
            logger.warning(f"   ❌ No business_config found")
            continue
        
        # Check for Groq API key
        groq_key = config.get("groq_api_key")
        if groq_key:
            # Decrypt key (first 20 chars only for security)
            try:
                decrypted = security.decrypt(groq_key)
                masked = decrypted[:10] + "..." + decrypted[-10:] if len(decrypted) > 20 else "***"
                logger.info(f"   ✅ Groq API Key: {masked}")
            except Exception as e:
                logger.error(f"   ❌ Failed to decrypt key: {e}")
        else:
            logger.warning(f"   ⚠️  No Groq API key configured (will use fallback)")
        
        # Check AI config
        ai_config = config.get("ai_config", {})
        model = ai_config.get("model", "default")
        temperature = ai_config.get("temperature", 0.7)
        has_custom_prompt = bool(ai_config.get("system_prompt"))
        
        logger.info(f"   Model: {model}")
        logger.info(f"   Temperature: {temperature}")
        logger.info(f"   Custom Prompt: {'Yes' if has_custom_prompt else 'No'}")
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ Test complete - Check logs above for configuration")
    logger.info("\nTo fully test isolation:")
    logger.info("1. Configure different Groq API keys for each tenant")
    logger.info("2. Send WhatsApp message to each tenant")
    logger.info("3. Check logs for 'Generating response for tenant...' messages")
    logger.info("4. Verify different API keys are being used")


async def test_conversation_flow():
    """Test a mock conversation flow"""
    
    logger.info("\n🧪 Testing Conversation Flow")
    logger.info("=" * 60)
    
    db = await get_database()
    conv_manager = ConversationManager(db)
    
    # Get first tenant
    tenant = await db.tenants.find_one({})
    if not tenant:
        logger.warning("No tenants found in database")
        return
    
    tenant_id = tenant.get("tenant_id")
    phone = "+1234567890"
    
    logger.info(f"Testing with tenant: {tenant_id}")
    
    # Simulate message
    try:
        response = await conv_manager.process_message(
            tenant_id=tenant_id,
            phone_number=phone,
            message_text="Hello, I'd like to book an appointment"
        )
        
        logger.info(f"✅ Response generated: {response[:100]}...")
        logger.info("✅ Conversation flow working correctly")
        
    except Exception as e:
        logger.error(f"❌ Error in conversation flow: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all tests"""
    
    try:
        await test_tenant_isolation()
        await test_conversation_flow()
        
    except KeyboardInterrupt:
        logger.info("\n⏸️  Tests interrupted by user")
    except Exception as e:
        logger.error(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
