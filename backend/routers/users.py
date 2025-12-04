"""
Users/Authentication API Router
User management and JWT authentication
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from bson import ObjectId
import logging

from models.core.users import (
    User, 
    UserCreate, 
    UserUpdate, 
    UserResponse, 
    Token, 
    TokenData, 
    LoginRequest,
    UserRole
)
from models.core.tenants import Tenant, TenantCreate, TenantStatus
from database.mongo_config import get_database
from utils.config import settings
from utils.error_logger import error_logger, ErrorCategory, ErrorLevel

logger = logging.getLogger(__name__)

router = APIRouter()

# Password hashing (using argon2 instead of bcrypt due to compatibility issues)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/users/login")


def hash_password(password: str) -> str:
    """Hash a password using argon2"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current authenticated user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        
        if user_id is None or not isinstance(user_id, str):
            raise credentials_exception
        
        token_data = TokenData(user_id=user_id)
        
    except JWTError:
        raise credentials_exception
    
    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    
    if user is None:
        raise credentials_exception
    
    user["id"] = str(user["_id"])
    
    # STRICT TENANT ISOLATION CHECK
    # If user is not a super admin, they MUST have a tenant_id
    # Otherwise, they might see all data (global access)
    if user.get("role") != UserRole.SUPER_ADMIN.value:
        tenant_id = user.get("tenant_id") or user.get("business_id")
        if not tenant_id:
            logger.critical(f"🚨 SECURITY ALERT: User {user_id} ({user.get('username')}) has no tenant_id! Blocking access.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account configuration error: Missing tenant association. Please contact support."
            )
    
    return user


async def get_current_admin(current_user: dict = Depends(get_current_user)):
    """Get current user and verify they are an admin"""
    if current_user.get("role") not in [UserRole.ADMIN.value, UserRole.OWNER.value, UserRole.SUPER_ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_super_admin(current_user: dict = Depends(get_current_user)):
    """Get current user and verify they are a super admin"""
    if current_user.get("role") != UserRole.SUPER_ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin access required"
        )
    return current_user


@router.post("/register", response_model=Token, status_code=201)
async def register_user(user: UserCreate):
    """Register a new user and return JWT token"""
    await error_logger.log_action(
        action='registration_attempt',
        data={
            'email': user.email,
            'username': user.username,
            'business_name': getattr(user, 'business_name', None)
        }
    )
    
    try:
        db = get_database()

        if not settings.ALLOW_SELF_REGISTRATION and not settings.TESTING:
            raise HTTPException(
                status_code=403,
                detail="Self-service registration is disabled. Please contact the shop owner to request access."
            )

        max_users = settings.MAX_DASHBOARD_USERS
        if (not settings.TESTING) and max_users and max_users > 0:
            active_users = await db.users.count_documents({"active": True})
            if active_users >= max_users:
                raise HTTPException(
                    status_code=403,
                    detail=f"User limit reached (max {max_users} active users). Deactivate an account before adding another."
                )
        
        # Check if user exists
        existing_email = await db.users.find_one({"email": user.email})
        if existing_email:
            logger.warning(f"Registration attempt with existing email: {user.email}")
            raise HTTPException(status_code=400, detail="Email already registered")
        
        existing_username = await db.users.find_one({"username": user.username})
        if existing_username:
            logger.warning(f"Registration attempt with existing username: {user.username}")
            raise HTTPException(status_code=400, detail="Username already taken")
        
        # Hash password
        user_dict = user.dict(exclude={"password"})
        user_dict["hashed_password"] = hash_password(user.password)
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = datetime.utcnow()
        user_dict["last_login"] = datetime.utcnow()  # Set initial login time
        
        # Insert user first to get ID
        result = await db.users.insert_one(user_dict)
        user_id = str(result.inserted_id)
        
        await error_logger.log_action(
            action='user_record_created',
            user_id=user_id,
            data={'email': user.email}
        )
        
        # Create a new tenant for this user
        # Use business_name if provided during signup, otherwise default
        business_name = user.business_name if hasattr(user, 'business_name') and user.business_name else f"{user.full_name}'s Business"
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
        
        tenant_result = await db.tenants.insert_one(tenant_dict)
        tenant_id = str(tenant_result.inserted_id)
        
        await error_logger.log_action(
            action='tenant_record_created',
            user_id=user_id,
            tenant_id=tenant_id,
            data={'business_name': business_name}
        )
        
        # Update user with tenant_id
        await db.users.update_one(
            {"_id": result.inserted_id},
            {
                "$set": {
                    "tenant_id": tenant_id,
                    "business_id": tenant_id, # Legacy support
                    "role": UserRole.OWNER # First user is always owner
                }
            }
        )
        
        # Retrieve created user with updated fields
        created_user = await db.users.find_one({"_id": result.inserted_id})
        
        logger.info(f"✅ User registered and tenant created: {created_user['username']} (Tenant: {tenant_id})")
        
        # Create and return access token
        access_token = create_access_token(
            data={
                "sub": user_id,
                "username": created_user["username"],
                "email": created_user["email"],
                "role": created_user["role"],
                "tenant_id": tenant_id
            }
        )
        
        return Token(access_token=access_token, token_type="bearer")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {e}", exc_info=True)
        await error_logger.log_error(
            error=e,
            category=ErrorCategory.USER,
            level=ErrorLevel.ERROR,
            context={
                'email': user.email,
                'username': user.username,
                'business_name': getattr(user, 'business_name', None)
            }
        )
        raise HTTPException(status_code=500, detail="Failed to register user")


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """User login - returns JWT token (supports both username and email)"""
    try:
        db = get_database()
        
        # Find user by username or email
        user = await db.users.find_one({
            "$or": [
                {"username": form_data.username},
                {"email": form_data.username}
            ]
        })
        
        if not user or not verify_password(form_data.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.get("active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Update last login
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        # Get tenant_id
        tenant_id = user.get("tenant_id") or user.get("business_id")
        
        # Create access token with tenant_id
        access_token = create_access_token(
            data={
                "sub": str(user["_id"]),
                "username": user["username"],
                "role": user["role"],
                "tenant_id": tenant_id
            }
        )
        
        logger.info(f"🔐 User logged in: {user['username']}")
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Login failed")


# Alias for /token endpoint (standard OAuth2)
@router.post("/token", response_model=Token)
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 compatible token endpoint - alias for /login"""
    return await login(form_data)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(**current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update current user information"""
    try:
        db = get_database()
        
        # Prepare update data
        update_data = {k: v for k, v in update.dict(exclude_unset=True).items() if v is not None}
        
        # Hash password if being updated
        if "password" in update_data:
            update_data["hashed_password"] = hash_password(update_data.pop("password"))
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_data["updated_at"] = datetime.utcnow()
        
        # Update user
        await db.users.update_one(
            {"_id": ObjectId(current_user["id"])},
            {"$set": update_data}
        )
        
        # Retrieve updated user
        updated_user = await db.users.find_one({"_id": ObjectId(current_user["id"])})
        updated_user["id"] = str(updated_user["_id"])
        
        logger.info(f"✏️ User updated: {updated_user['username']}")
        
        return UserResponse(**updated_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update user")
