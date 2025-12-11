
import asyncio
import os
import sys
import httpx

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from dotenv import load_dotenv
load_dotenv("backend/.env", override=True)

from database.mongo_config import get_database, connect_to_mongo
from services.vapi_service import vapi_service

async def reset_system():
    print("🚨 STARTING SYSTEM RESET 🚨")
    print("This will delete ALL users, tenants, and Vapi assistants.")
    
    confirm = input("Are you sure? Type 'DELETE' to confirm: ")
    if confirm != "DELETE":
        print("Aborted.")
        return

    # 1. MongoDB Cleanup
    print("\nConnecting to MongoDB...")
    await connect_to_mongo()
    db = get_database()
    
    collections = ["users", "tenants", "appointments", "call_logs", "knowledge_base", "platform_keys_usage_logs"]
    for col_name in collections:
        print(f"Proping collection: {col_name}...")
        try:
            await db[col_name].drop()
            print(f"✅ Dropped {col_name}")
        except Exception as e:
            print(f"⚠️ Failed to drop {col_name}: {e}")

    # 2. Vapi Cleanup
    print("\nCleaning up Vapi Assistants...")
    if not vapi_service.is_configured():
        print("⚠️ Vapi not configured, skipping assistant cleanup.")
    else:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # List all assistants
                print("Fetching assistants...")
                response = await client.get(
                    f"{vapi_service.base_url}/assistant",
                    headers=vapi_service.headers
                )
                
                if response.status_code == 200:
                    assistants = response.json()
                    print(f"Found {len(assistants)} assistants.")
                    
                    for assistant in assistants:
                        aid = assistant.get("id")
                        name = assistant.get("name", "Unknown")
                        print(f"Deleting assistant: {name} ({aid})...")
                        await vapi_service.delete_assistant(aid)
                    print("✅ All Vapi assistants deleted.")
                else:
                    print(f"❌ Failed to list assistants: {response.text}")

        except Exception as e:
            print(f"❌ Vapi cleanup error: {e}")

    print("\n✨ SYSTEM RESET COMPLETE ✨")

if __name__ == "__main__":
    asyncio.run(reset_system())
