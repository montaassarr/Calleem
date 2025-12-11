
import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from dotenv import load_dotenv
load_dotenv("backend/.env", override=True)

from services.vapi_service import vapi_service
from services.provisioning import vapi_provisioning
from database.mongo_config import get_database, connect_to_mongo

async def refresh_tools():
    print("🚀 Refreshing Vapi Tools...")
    
    # Initialize DB
    await connect_to_mongo()
    db = get_database()
    
    # Find the real user tenant (assuming "Bella Salon" or similar, or just valid email)
    # We'll look for any tenant that is NOT an auto-test
    cursor = db.tenants.find({"vapi_assistant_id": {"$exists": True}})
    
    async for tenant in cursor:
        if "auto_test" in tenant.get("email", ""):
            continue
            
        tenant_id = str(tenant["_id"])
        assistant_id = tenant["vapi_assistant_id"]
        print(f"🔄 Updating Tenant: {tenant_id} ({tenant.get('business_name')})")
        
        try:
            await vapi_provisioning.provision_tenant_assistant(
                tenant_id, 
                tenant.get("business_name", "Refreshed Business")
            )
            print("   ✅ Updated")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            
    print("Done refreshing real users.")
    return

    # Old logic removed
    '''
    tenant = await db.tenants.find_one({"vapi_assistant_id": {"$exists": True}}, sort=[("_id", -1)])
    if not tenant:
    ...
    '''

if __name__ == "__main__":
    asyncio.run(refresh_tools())
