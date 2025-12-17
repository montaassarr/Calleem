#!/usr/bin/env python3
"""
Script to fix the hardcoded date in assistant system prompts
Adds the current date dynamically to all existing assistants
"""
import sys
import os
import asyncio
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database.mongo_config import get_database
from services.vapi_service import vapi_service
from utils.datetime_utils import DateTimeUtils
import re


async def fix_assistant_date(tenant_id: str):
    """Update assistant with current date"""
    from database.mongo_config import connect_to_mongo
    
    # Initialize MongoDB connection
    await connect_to_mongo()
    
    db = get_database()
    
    # Get tenant
    from bson import ObjectId
    tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
    if not tenant:
        print(f"❌ Tenant {tenant_id} not found")
        return False
    
    assistant_id = tenant.get("vapi_assistant_id")
    if not assistant_id:
        print(f"❌ No assistant configured for tenant {tenant_id}")
        return False
    
    print(f"📋 Fetching assistant {assistant_id}...")
    
    # Get current assistant config
    assistant = await vapi_service.get_assistant(assistant_id)
    if not assistant:
        print(f"❌ Could not fetch assistant {assistant_id}")
        return False
    
    # Extract system prompt
    model_config = assistant.get("model", {})
    messages = model_config.get("messages", [])
    system_prompt = ""
    for msg in messages:
        if msg.get("role") == "system":
            system_prompt = msg.get("content", "")
            break
    
    if not system_prompt:
        print("❌ No system prompt found")
        return False
    
    print(f"📝 Current system prompt (first 200 chars):\n{system_prompt[:200]}...\n")
    
    # Generate new date header
    now = DateTimeUtils.now()
    current_date_str = now.strftime("%B %d, %Y")
    tomorrow = now + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%B %d, %Y")
    
    date_header = f"""**CURRENT DATE: {current_date_str} - Use this for all date calculations**
When customers say 'tomorrow', they mean {tomorrow_str}.

"""
    
    # Remove old date header if present
    updated_prompt = re.sub(
        r'\*\*CURRENT DATE:.*?\*\*\n.*?tomorrow.*?\n\n?',
        '',
        system_prompt,
        flags=re.DOTALL
    )
    
    # Inject new date header
    lines = updated_prompt.split('\n')
    if lines and lines[0].strip().startswith('You are'):
        # Insert after the "You are..." line
        updated_prompt = lines[0] + '\n\n' + date_header + '\n'.join(lines[1:])
    else:
        # Insert at the very beginning
        updated_prompt = date_header + updated_prompt
    
    # Also ensure year is correct in instructions
    updated_prompt = re.sub(r'\b2025\b', '2024', updated_prompt)
    
    print(f"✅ New system prompt (first 400 chars):\n{updated_prompt[:400]}...\n")
    
    # Update assistant
    print(f"🔄 Updating assistant {assistant_id}...")
    
    result = await vapi_service.update_assistant(
        assistant_id=assistant_id,
        instructions=updated_prompt
    )
    
    if result.get("success"):
        print(f"✅ Successfully updated assistant {assistant_id}")
        print(f"📅 Current date set to: {current_date_str}")
        print(f"📅 Tomorrow set to: {tomorrow_str}")
        return True
    else:
        print(f"❌ Failed to update assistant: {result}")
        return False


async def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_assistant_date.py <tenant_id>")
        print("\nExample: python fix_assistant_date.py 694031d581072ad069cc9412")
        sys.exit(1)
    
    tenant_id = sys.argv[1]
    print(f"🔧 Fixing assistant date for tenant: {tenant_id}\n")
    
    success = await fix_assistant_date(tenant_id)
    
    if success:
        print("\n✅ Date fix complete!")
    else:
        print("\n❌ Date fix failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
