
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException

from database.mongo_config import get_database
from models.tenant import TenantStatus
from models.appointment import AppointmentStatus
from utils.encryption import encrypt_value, decrypt_value
from services.user_service import UserService

logger = logging.getLogger(__name__)

class AdminService:
    def __init__(self, db=None):
        self.db = db or get_database()

    def _normalize_appointment_record(self, appt: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure appointments have API-friendly fields"""
        if not appt:
            return appt

        normalized = dict(appt)
        normalized["id"] = str(normalized.get("_id", normalized.get("id", "")))
        normalized.pop("_id", None)

        normalized["client_name"] = (
            normalized.get("client_name")
            or normalized.get("customer_name")
            or "Unknown"
        )
        normalized["client_phone"] = (
            normalized.get("client_phone")
            or normalized.get("customer_phone")
            or ""
        )
        normalized["service"] = (
            normalized.get("service")
            or normalized.get("service_name")
            or "General Consultation"
        )

        normalized["datetime"] = (
            normalized.get("datetime")
            or normalized.get("start_time")
            or datetime.utcnow()
        )
        normalized["duration_minutes"] = (
            normalized.get("duration_minutes")
            or normalized.get("duration")
            or 30
        )

        status_value = normalized.get("status") or AppointmentStatus.CONFIRMED
        if isinstance(status_value, str):
            try:
                normalized["status"] = AppointmentStatus(status_value)
            except ValueError:
                normalized["status"] = AppointmentStatus.CONFIRMED
        else:
            normalized["status"] = status_value

        normalized["created_at"] = normalized.get("created_at") or datetime.utcnow()
        normalized["updated_at"] = normalized.get("updated_at") or normalized["created_at"]

        return normalized

    # --- Tenant Management ---
    async def list_tenants(self, skip: int, limit: int, search: Optional[str]) -> List[Dict[str, Any]]:
        try:
            query = {}
            if search:
                query["name"] = {"$regex": search, "$options": "i"}
                
            cursor = self.db.tenants.find(query).skip(skip).limit(limit)
            tenants = await cursor.to_list(length=limit)
            
            results = []
            for t in tenants:
                # Convert ObjectId to string
                t["id"] = str(t["_id"])
                del t["_id"]
                
                # Ensure required fields exist
                if "total_calls" not in t: 
                    t["total_calls"] = 0
                if "total_minutes" not in t: 
                    t["total_minutes"] = 0.0
                if "name" not in t:
                    t["name"] = "Unknown Tenant"
                if "email" not in t:
                    t["email"] = "no-email@example.com"
                if "plan" not in t:
                    t["plan"] = "free"
                if "status" not in t:
                    t["status"] = "active"
                if "created_at" not in t:
                    t["created_at"] = datetime.utcnow()
                if "settings" not in t:
                    t["settings"] = {
                        "business_name": t.get("name", "Unknown"),
                        "timezone": "UTC",
                        "currency": "USD"
                    }
                results.append(t)
            
            logger.info(f"Listed {len(results)} tenants")
            return results
        except Exception as e:
            logger.error(f"Error listing tenants: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to list tenants: {str(e)}")

    async def create_tenant(self, tenant_data: Any) -> Dict[str, Any]:
        if await self.db.tenants.find_one({"name": tenant_data.name}):
            raise HTTPException(status_code=400, detail="Tenant name already exists")
            
        tenant_dict = tenant_data.model_dump()
        tenant_dict["created_at"] = datetime.utcnow()
        tenant_dict["updated_at"] = datetime.utcnow()
        tenant_dict["total_calls"] = 0
        tenant_dict["total_minutes"] = 0.0
        
        result = await self.db.tenants.insert_one(tenant_dict)
        created = await self.db.tenants.find_one({"_id": result.inserted_id})
        created["_id"] = str(created["_id"])
        return created

    async def get_tenant(self, tenant_id: str) -> Dict[str, Any]:
        if not ObjectId.is_valid(tenant_id):
            raise HTTPException(status_code=400, detail="Invalid tenant ID")
            
        tenant = await self.db.tenants.find_one({"_id": ObjectId(tenant_id)})
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
            
        tenant["_id"] = str(tenant["_id"])
        return tenant

    async def update_tenant(self, tenant_id: str, update_data: Any) -> Dict[str, Any]:
        if not ObjectId.is_valid(tenant_id):
            raise HTTPException(status_code=400, detail="Invalid tenant ID")
            
        data = {k: v for k, v in update_data.model_dump(exclude_unset=True).items() if v is not None}
        if not data:
            raise HTTPException(status_code=400, detail="No fields to update")
            
        data["updated_at"] = datetime.utcnow()
        
        await self.db.tenants.update_one({"_id": ObjectId(tenant_id)}, {"$set": data})
        
        updated = await self.db.tenants.find_one({"_id": ObjectId(tenant_id)})
        updated["_id"] = str(updated["_id"])
        return updated

    async def delete_tenant(self, tenant_id: str) -> None:
        """Delete a tenant and all associated data"""
        if not ObjectId.is_valid(tenant_id):
            raise HTTPException(status_code=400, detail="Invalid tenant ID")
            
        # Check if tenant exists
        tenant = await self.db.tenants.find_one({"_id": ObjectId(tenant_id)})
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        try:
            # Delete all associated data
            await self.db.users.delete_many({"tenant_id": tenant_id})
            await self.db.appointments.delete_many({"tenant_id": tenant_id})
            await self.db.services.delete_many({"tenant_id": tenant_id})
            await self.db.conversations.delete_many({"tenant_id": tenant_id})
            await self.db.business_config.delete_many({"tenant_id": tenant_id})
            
            # Delete the tenant itself
            await self.db.tenants.delete_one({"_id": ObjectId(tenant_id)})
            
            logger.info(f"Deleted tenant {tenant_id} and all associated data")
        except Exception as e:
            logger.error(f"Error deleting tenant {tenant_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to delete tenant: {str(e)}")

    # --- User Management (Global) ---
    async def list_all_users(self, skip: int, limit: int, tenant_id: Optional[str]) -> List[Dict[str, Any]]:
        query = {}
        if tenant_id:
            query["tenant_id"] = tenant_id
            
        cursor = self.db.users.find(query).skip(skip).limit(limit)
        users = await cursor.to_list(length=limit)
        
        results = []
        for u in users:
            u["id"] = str(u["_id"])
            if "tenant_id" in u and u["tenant_id"]:
                u["tenant_id"] = str(u["tenant_id"])
            results.append(u)
        return results

    async def impersonate_user(self, user_id: str, admin_username: str) -> Dict[str, str]:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID")
            
        user = await self.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        user_service = UserService()
        access_token = user_service.create_access_token(data={
            "sub": str(user["_id"]),
            "username": user["username"],
            "role": user["role"],
            "tenant_id": str(user.get("tenant_id")) if user.get("tenant_id") else None,
            "impersonator": admin_username
        })
        
        logger.warning(f"Admin {admin_username} impersonating user {user['username']}")
        return {"access_token": access_token, "token_type": "bearer"}

    # --- System Management ---
    async def get_global_analytics(self) -> Dict[str, Any]:
        total_tenants = await self.db.tenants.count_documents({})
        active_tenants = await self.db.tenants.count_documents({"status": TenantStatus.ACTIVE})
        total_users = await self.db.users.count_documents({})
        total_appointments = await self.db.appointments.count_documents({})
        total_conversations = await self.db.conversations.count_documents({})
        
        return {
            "tenants": {"total": total_tenants, "active": active_tenants},
            "users": total_users,
            "appointments": total_appointments,
            "conversations": total_conversations,
            "timestamp": datetime.utcnow()
        }

    # --- Business Config ---
    async def get_business_config(self, tenant_id: str) -> Dict[str, Any]:
        query = {}
        if tenant_id:
            query["tenant_id"] = tenant_id
            
        config = await self.db.business_config.find_one(query)
        
        if not config:
            return {
                "business_name": "My Business",
                "business_id": tenant_id or "default",
                "tenant_id": tenant_id
            }
            
        if "_id" in config:
            config["_id"] = str(config["_id"])
            
        # Decrypt
        encrypted_fields = ["openai_api_key", "groq_api_key", "elevenlabs_api_key", 
                           "twilio_auth_token", "twilio_account_sid", "airtable_api_key"]
        
        for field in encrypted_fields:
            if config.get(field):
                try:
                    decrypted = decrypt_value(config[field])
                    if decrypted:
                        config[field] = decrypted
                except:
                    pass  # Leave encrypted if decrypt fails
        
        # Defaults
        if not config.get("business_name"): config["business_name"] = "My Business"
        if not config.get("timezone"): config["timezone"] = "UTC"
        if "tenant_id" not in config and tenant_id: config["tenant_id"] = tenant_id
        
        return config

    async def update_business_config(self, tenant_id: str, config_update: Any) -> Dict[str, Any]:
        config_dict = config_update.dict(exclude_unset=True)
        config_dict["updated_at"] = datetime.utcnow()
        
        query = {}
        if tenant_id:
            query["tenant_id"] = tenant_id
            config_dict["tenant_id"] = tenant_id

        # Encrypt
        encrypted_fields = ["openai_api_key", "groq_api_key", "elevenlabs_api_key", 
                           "twilio_auth_token", "twilio_account_sid", "airtable_api_key"]
        
        from utils.encryption import encrypt_value
        config_dump = config_update.model_dump(by_alias=True, exclude={"id"})
        
        for field in encrypted_fields:
            if config_dump.get(field):
                try:
                    config_dump[field] = encrypt_value(config_dump[field])
                except:
                    raise HTTPException(500, f"Encryption failed for {field}")

        if "_id" in config_dump: del config_dump["_id"]
        
        await self.db.business_config.update_one(query, {"$set": config_dump}, upsert=True)
        
        updated = await self.db.business_config.find_one(query)
        if "_id" in updated: del updated["_id"]
        
        # Defaults
        if not updated.get("business_name"): updated["business_name"] = "My Business"
        if not updated.get("timezone"): updated["timezone"] = "UTC"
        if "tenant_id" not in updated and tenant_id: updated["tenant_id"] = tenant_id
        
        return updated

    # --- Other CRUD (Appointments, Services, Conversations, Users) ---
    # These follow similar patterns. Implementing generic/specfic methods.
    
    async def create_user(self, user_data: Any, tenant_id: str) -> Dict[str, Any]:
        if await self.db.users.find_one({"email": user_data.email}):
             raise HTTPException(400, "Email already registered")
        if await self.db.users.find_one({"username": user_data.username}):
             raise HTTPException(400, "Username already taken")
             
        user_service = UserService()
        user_dict = user_data.dict(exclude={"password"})
        user_dict["hashed_password"] = user_service.hash_password(user_data.password)
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = datetime.utcnow()
        user_dict["last_login"] = None
        user_dict["tenant_id"] = tenant_id
        user_dict["business_id"] = tenant_id
        
        result = await self.db.users.insert_one(user_dict)
        created = await self.db.users.find_one({"_id": result.inserted_id})
        created["id"] = str(created["_id"])
        return created
    
    async def update_user(self, user_id: str, update_data: Any) -> Dict[str, Any]:
        if not ObjectId.is_valid(user_id): raise HTTPException(400, "Invalid ID")
        data = {k: v for k, v in update_data.dict(exclude_unset=True).items() if v is not None}
        
        if "password" in data:
            user_service = UserService()
            data["hashed_password"] = user_service.hash_password(data.pop("password"))
        
        if not data: raise HTTPException(400, "No fields")
        data["updated_at"] = datetime.utcnow()
        
        result = await self.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": data})
        if result.matched_count == 0: raise HTTPException(404, "User not found")
        
        updated = await self.db.users.find_one({"_id": ObjectId(user_id)})
        updated["id"] = str(updated["_id"])
        return updated

    async def delete_user(self, user_id: str) -> bool:
        if not ObjectId.is_valid(user_id): raise HTTPException(400, "Invalid ID")
        result = await self.db.users.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0: raise HTTPException(404, "User not found")
        return True

    # Appointments
    async def list_appointments(self, skip: int, limit: int, status: Optional[str]) -> List[Dict[str, Any]]:
        query = {}
        if status: query["status"] = status
        cursor = self.db.appointments.find(query).sort("datetime", -1).skip(skip).limit(limit)
        appts = await cursor.to_list(length=limit)
        return [self._normalize_appointment_record(a) for a in appts]

    async def create_appointment(self, appt_data: Any, tenant_id: str) -> Dict[str, Any]:
        appt_dict = appt_data.dict()
        appt_dict["status"] = "confirmed" # Enum?
        appt_dict["created_at"] = datetime.utcnow()
        appt_dict["updated_at"] = datetime.utcnow()
        appt_dict["tenant_id"] = tenant_id
        appt_dict["business_id"] = tenant_id
        
        result = await self.db.appointments.insert_one(appt_dict)
        created = await self.db.appointments.find_one({"_id": result.inserted_id})
        return self._normalize_appointment_record(created)

    async def update_appointment(self, appt_id: str, update_data: Any) -> Dict[str, Any]:
        if not ObjectId.is_valid(appt_id): raise HTTPException(400, "Invalid ID")
        data = {k: v for k, v in update_data.dict(exclude_unset=True).items() if v is not None}
        if not data: raise HTTPException(400, "No fields")
        data["updated_at"] = datetime.utcnow()
        
        result = await self.db.appointments.update_one({"_id": ObjectId(appt_id)}, {"$set": data})
        if result.matched_count == 0: raise HTTPException(404, "Not found")
        
        updated = await self.db.appointments.find_one({"_id": ObjectId(appt_id)})
        return self._normalize_appointment_record(updated)

    async def delete_appointment(self, appt_id: str) -> bool:
        if not ObjectId.is_valid(appt_id): raise HTTPException(400, "Invalid ID")
        result = await self.db.appointments.delete_one({"_id": ObjectId(appt_id)})
        if result.deleted_count == 0: raise HTTPException(404, "Not found")
        return True

    # Services
    async def list_services(self, skip: int, limit: int) -> List[Dict[str, Any]]:
        cursor = self.db.services.find({}).skip(skip).limit(limit)
        services = await cursor.to_list(length=limit)
        for s in services: s["_id"] = str(s["_id"])
        return services

    async def create_service(self, service_data: Any, tenant_id: str) -> Dict[str, Any]:
        s_dict = service_data.dict()
        s_dict["created_at"] = datetime.utcnow()
        s_dict["updated_at"] = datetime.utcnow()
        s_dict["tenant_id"] = tenant_id
        s_dict["business_id"] = tenant_id
        
        result = await self.db.services.insert_one(s_dict)
        created = await self.db.services.find_one({"_id": result.inserted_id})
        created["_id"] = str(created["_id"])
        return created

    async def update_service(self, service_id: str, update_data: Any) -> Dict[str, Any]:
        if not ObjectId.is_valid(service_id): raise HTTPException(400, "Invalid ID")
        data = {k: v for k, v in update_data.dict(exclude_unset=True).items() if v is not None}
        if not data: raise HTTPException(400, "No fields")
        data["updated_at"] = datetime.utcnow()
        
        result = await self.db.services.update_one({"_id": ObjectId(service_id)}, {"$set": data})
        if result.matched_count == 0: raise HTTPException(404, "Not found")
        
        updated = await self.db.services.find_one({"_id": ObjectId(service_id)})
        updated["_id"] = str(updated["_id"])
        return updated
        
    async def delete_service(self, service_id: str) -> bool:
        if not ObjectId.is_valid(service_id): raise HTTPException(400, "Invalid ID")
        result = await self.db.services.delete_one({"_id": ObjectId(service_id)})
        if result.deleted_count == 0: raise HTTPException(404, "Not found")
        return True

    # Conversations
    async def list_conversations(self, skip: int, limit: int, phone: Optional[str]) -> List[Dict[str, Any]]:
        query = {}
        if phone: query["phone_number"] = {"$regex": phone}
        cursor = self.db.conversations.find(query).sort("updated_at", -1).skip(skip).limit(limit)
        convs = await cursor.to_list(length=limit)
        for c in convs: c["_id"] = str(c["_id"])
        return convs

    async def delete_conversation(self, conv_id: str) -> bool:
        if not ObjectId.is_valid(conv_id): raise HTTPException(400, "Invalid ID")
        result = await self.db.conversations.delete_one({"_id": ObjectId(conv_id)})
        if result.deleted_count == 0: raise HTTPException(404, "Not found")
        return True

def get_admin_service():
    return AdminService()
