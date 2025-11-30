"""
Tenant Authentication API Router
Handles tenant signup, login, and authentication
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from bson import ObjectId
import logging

from models.tenant import (
    Tenant,
    TenantCreate,
    TenantLogin,
    TenantResponse,
    TenantConfig
)
from database.mongo_config import get_database
from utils.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


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


async def get_current_tenant(token: str = Depends(oauth2_scheme)):
    """Get current authenticated tenant from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        tenant_id: str = payload.get("sub")
        
        if tenant_id is None:
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    db = get_database()
    tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
    
    if tenant is None:
        raise credentials_exception
    
    tenant["id"] = str(tenant["_id"])
    
    return tenant


@router.post("/signup", response_model=dict)
async def signup(tenant_data: TenantCreate):
    """
    Register a new tenant (business owner)
    """
    try:
        db = get_database()
        
        # Check if email already exists
        existing_tenant = await db.tenants.find_one({"email": tenant_data.email})
        if existing_tenant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if phone already exists
        existing_phone = await db.tenants.find_one({"phone": tenant_data.phone})
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )
        
        # Create tenant document
        tenant_doc = {
            "fullname": tenant_data.fullname,
            "email": tenant_data.email,
            "password": hash_password(tenant_data.password),
            "phone": tenant_data.phone,
            "config": {
                "business_name": tenant_data.business_name,
                "timezone": "UTC",
                "currency": "USD",
                "language": "en"
            },
            "api_keys": {},
            "plan": "free",
            "status": "active",
            "total_calls": 0,
            "total_minutes": 0.0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_configured": False
        }
        
        result = await db.tenants.insert_one(tenant_doc)
        tenant_id = str(result.inserted_id)
        
        # Create access token
        access_token = create_access_token(data={"sub": tenant_id})
        
        logger.info(f"✅ New tenant registered: {tenant_data.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "tenant_id": tenant_id,
            "email": tenant_data.email,
            "fullname": tenant_data.fullname
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during signup: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/login", response_model=dict)
async def login(credentials: TenantLogin):
    """
    Tenant login
    """
    try:
        db = get_database()
        
        # Find tenant by email
        tenant = await db.tenants.find_one({"email": credentials.email})
        
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(credentials.password, tenant["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if account is active
        if tenant.get("status") != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is suspended or inactive"
            )
        
        # Create access token
        tenant_id = str(tenant["_id"])
        access_token = create_access_token(data={"sub": tenant_id})
        
        logger.info(f"✅ Tenant logged in: {credentials.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "tenant_id": tenant_id,
            "email": tenant["email"],
            "fullname": tenant["fullname"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Login failed")


@router.get("/me", response_model=TenantResponse)
async def get_current_tenant_info(current_tenant: dict = Depends(get_current_tenant)):
    """
    Get current tenant information
    """
    # Remove password from response
    current_tenant.pop("password", None)
    current_tenant.pop("_id", None)
    
    return TenantResponse(**current_tenant)
