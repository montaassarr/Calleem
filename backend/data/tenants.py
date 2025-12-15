
from bson import ObjectId
from typing import Optional, Dict, Any
from database.mongo_config import get_database

class TenantRepository:
    def __init__(self, db=None):
        self.db = db if db is not None else get_database()
        self.collection = self.db.tenants

    async def get_by_id(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """
        Get tenant by ID (trying both ObjectId and string tenant_id)
        """
        try:
            return await self.collection.find_one({"_id": ObjectId(tenant_id)})
        except:
            return await self.collection.find_one({"tenant_id": tenant_id})

    async def update(self, tenant_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update tenant data
        """
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(tenant_id)},
                {"$set": update_data}
            )
            if result.matched_count == 0:
                 # Fallback to string ID
                 result = await self.collection.update_one(
                    {"tenant_id": tenant_id},
                    {"$set": update_data}
                )
            return result.modified_count > 0
        except Exception as e:
            # Fallback for string ID if ObjectId conversion failed above (logic could be cleaner but mirrors prototype)
            result = await self.collection.update_one(
                {"tenant_id": tenant_id},
                {"$set": update_data}
            )
            return result.modified_count > 0

    async def unset_field(self, tenant_id: str, fields: Dict[str, Any]) -> bool:
        """
        Unset specific fields
        """
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(tenant_id)},
                {"$unset": fields}
            )
            return result.modified_count > 0
        except:
             return (await self.collection.update_one(
                {"tenant_id": tenant_id},
                {"$unset": fields}
            )).modified_count > 0
