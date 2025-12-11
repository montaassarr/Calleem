"""
Cleanup Script
Removes all tenants except 'bella@example.com' and 'admin' to ensure a clean slate.
"""
import asyncio
import os
from database.mongo_config import get_database, connect_to_mongo, close_mongo_connection

async def clean_tenants():
    await connect_to_mongo()
    db = get_database()
    
    # Keep Bella and Admin
    keep_emails = ["bella@example.com", "admin", "admin@example.com"]
    
    # Find tenants to remove
    to_remove = []
    cursor = db.users.find({"email": {"$nin": keep_emails}})
    async for user in cursor:
        to_remove.append(user)
    
    print(f"Found {len(to_remove)} users/tenants to remove.")
    
    for user in to_remove:
        email = user.get("email")
        tenant_id = user.get("tenant_id")
        
        # Delete User
        await db.users.delete_one({"_id": user["_id"]})
        print(f"Deleted user: {email}")
        
        # Delete Tenant Data
        if tenant_id:
            try:
                # Delete Tenant
                await db.tenants.delete_one({"_id": tenant_id})
                
                # Delete Appointments
                await db.appointments.delete_many({"tenant_id": str(tenant_id)})
                
                # Delete Call Logs
                await db.call_logs.delete_many({"tenant_id": str(tenant_id)})
                
                print(f"Deleted tenant data for: {email}")
            except Exception as e:
                print(f"Error cleaning tenant {tenant_id}: {e}")

    print("\nCleanup Complete! Remaining users:")
    async for user in db.users.find({}):
        print(f"- {user.get('email')} ({user.get('role')})")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(clean_tenants())
