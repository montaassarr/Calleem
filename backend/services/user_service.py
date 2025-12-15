import logging
import datetime
from typing import Optional, Dict, Any, Union
from datetime import datetime, timedelta
from bson import ObjectId
from fastapi import HTTPException, status
from jose import jwt, JWTError
from passlib.context import CryptContext

from database.mongo_config import get_database
from models.user import UserCreate, UserUpdate, Token, TokenData, UserRole
from models.tenant import TenantStatus
from utils.config import settings
from utils.error_logger import error_logger, ErrorCategory, ErrorLevel
from services.provisioning import vapi_provisioning

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class UserService:
    def __init__(self):
        pass

    @property
    def db(self):
        return get_database()

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    async def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        user = await self.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return None
        user["id"] = str(user["_id"])
        return user
    
    async def get_user_by_email(self, email: str) -> Dict[str, Any]:
         return await self.db.users.find_one({"email": email})

    async def get_user_by_username(self, username: str) -> Dict[str, Any]:
         return await self.db.users.find_one({"username": username})

    async def register_user(self, user_create: UserCreate) -> Token:
        """Register a new user, create tenant, and provision resources"""
        # Logging action
        await error_logger.log_action(
            action='registration_attempt',
            data={
                'email': user_create.email,
                'username': user_create.username,
                'business_name': getattr(user_create, 'business_name', None)
            }
        )

        try:
             # Check constraints (self-reg, max users)
            if not settings.ALLOW_SELF_REGISTRATION and not settings.TESTING:
                raise HTTPException(status_code=403, detail="Self-service registration disabled")
            
            if (not settings.TESTING) and settings.MAX_DASHBOARD_USERS > 0:
                 active = await self.db.users.count_documents({"active": True})
                 if active >= settings.MAX_DASHBOARD_USERS:
                     raise HTTPException(status_code=403, detail="User limit reached")

            # Check duplication
            if await self.get_user_by_email(user_create.email):
                 raise HTTPException(status_code=400, detail="Email already registered")
            if await self.get_user_by_username(user_create.username):
                 raise HTTPException(status_code=400, detail="Username already taken")

            # Prepare User
            user_dict = user_create.dict(exclude={"password"})
            user_dict["hashed_password"] = self.hash_password(user_create.password)
            user_dict["active"] = True
            user_dict["created_at"] = datetime.utcnow()
            user_dict["updated_at"] = datetime.utcnow()
            user_dict["last_login"] = datetime.utcnow()
            user_dict["role"] = UserRole.OWNER # First user is owner

            res = await self.db.users.insert_one(user_dict)
            user_id = str(res.inserted_id)

            await error_logger.log_action(action='user_record_created', user_id=user_id, data={'email': user_create.email})

            # Create Tenant
            business_name = user_create.business_name or f"{user_create.full_name}'s Business"
            tenant_dict = {
                "owner_id": user_id,
                "name": business_name,
                "status": TenantStatus.ACTIVE,
                "plan": "free",
                "is_configured": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "total_calls": 0,
                "total_minutes": 0.0
            }
            res_tenant = await self.db.tenants.insert_one(tenant_dict)
            tenant_id = str(res_tenant.inserted_id)

             # Update User with Tenant
            await self.db.users.update_one(
                {"_id": res.inserted_id},
                {"$set": {"tenant_id": tenant_id, "business_id": tenant_id}}
            )

            # Create default config
            business_config = {
                "tenant_id": tenant_id,
                "business_name": business_name,
                "timezone": "UTC",
                "api_keys": [],
                "features_enabled": {"voice_agent": False},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await self.db.business_config.insert_one(business_config)

            # Auto-Provision Vapi
            try:
                logger.info(f"🤖 Triggering auto-provisioning for {tenant_id}")
                await vapi_provisioning.provision_tenant_assistant(tenant_id, business_name)
            except Exception as e:
                logger.error(f"⚠️ Auto-provisioning failed: {e}")

            # Return Token
            access_token = self.create_access_token(
                data={
                    "sub": user_id,
                    "username": user_create.username,
                    "email": user_create.email,
                    "role": UserRole.OWNER,
                    "tenant_id": tenant_id
                }
            )
            return Token(access_token=access_token, token_type="bearer")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Registration error: {e}")
            await error_logger.log_error(error=e, category=ErrorCategory.USER, level=ErrorLevel.ERROR)
            raise HTTPException(status_code=500, detail="Failed to register user")

    async def authenticate_user(self, username_or_email: str, password: str) -> Dict[str, Any]:
        """Authenticate user and return full user object + token logic"""
        user = await self.db.users.find_one({
            "$or": [{"username": username_or_email}, {"email": username_or_email}]
        })

        if not user or not self.verify_password(password, user["hashed_password"]):
            return None
        
        if not user.get("active", True):
             raise HTTPException(status_code=403, detail="User account is inactive")
        
        # Update login
        await self.db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )

        return user

    async def ensure_tenant_config(self, tenant_id: str):
        """Ensure business config exists for tenant"""
        if not tenant_id: return
        
        existing = await self.db.business_config.find_one({"tenant_id": tenant_id})
        if not existing:
            # Create default
             # Try to get name
             tenant = await self.db.tenants.find_one({"_id": ObjectId(tenant_id)}) if ObjectId.is_valid(tenant_id) else None
             name = tenant.get("name", "My Business") if tenant else "My Business"
             
             cfg = {
                "tenant_id": tenant_id,
                "business_name": name,
                "timezone": "UTC",
                "api_keys": [],
                "features_enabled": {"voice_agent": False},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
             await self.db.business_config.insert_one(cfg)


    async def update_user(self, user_id: str, update: UserUpdate) -> Dict[str, Any]:
        update_data = {k: v for k, v in update.dict(exclude_unset=True).items() if v is not None}
        
        if "password" in update_data:
            update_data["hashed_password"] = self.hash_password(update_data.pop("password"))
            
        if not update_data:
             raise HTTPException(status_code=400, detail="No fields to update")
            
        update_data["updated_at"] = datetime.utcnow()
        
        await self.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
        
        return await self.get_user_by_id(user_id)

    async def delete_user_and_tenant(self, user_id: str):
        """Super Admin deletion"""
        user = await self.get_user_by_id(user_id)
        if not user: raise HTTPException(404, "User not found")
        if user.get("role") == UserRole.SUPER_ADMIN: raise HTTPException(400, "Cannot delete super admin")
        
        tenant_id = user.get("tenant_id")
        if tenant_id:
            try:
                tid_str = str(tenant_id)
                await self.db.tenants.delete_one({"_id": ObjectId(tenant_id)})
                await self.db.appointments.delete_many({"tenant_id": tid_str})
                await self.db.call_logs.delete_many({"tenant_id": tid_str})
                await self.db.conversations.delete_many({"tenant_id": tid_str})
                await self.db.business_config.delete_many({"tenant_id": tid_str})
            except Exception as e:
                logger.error(f"Error cleaning tenant tokens: {e}")
        
        await self.db.users.delete_one({"_id": ObjectId(user_id)})
