"""
Users/Authentication API Router
User management and JWT authentication
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime
import logging

from models.user import (
    UserCreate, 
    UserUpdate, 
    UserResponse, 
    Token, 
    TokenData,
    UserRole
)
from utils.config import settings
from utils.error_logger import error_logger
from services.user_service import UserService

logger = logging.getLogger(__name__)

router = APIRouter()
user_service = UserService()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/users/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current authenticated user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        from jose import jwt, JWTError
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    user = await user_service.get_user_by_id(user_id)
    
    if user is None:
        raise credentials_exception
    
    # STRICT TENANT ISOLATION CHECK
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
    return await user_service.register_user(user)


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """User login - returns JWT token (supports both username and email)"""
    user = await user_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Ensure tenant config exists
    tenant_id = user.get("tenant_id") or user.get("business_id")
    await user_service.ensure_tenant_config(tenant_id)
    
    # Create access token
    access_token = user_service.create_access_token(
        data={
            "sub": str(user["_id"]),
            "username": user["username"],
            "role": user["role"],
            "tenant_id": tenant_id
        }
    )
    
    logger.info(f"🔐 User logged in: {user['username']}")
    
    return {"access_token": access_token, "token_type": "bearer"}


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
        updated_user = await user_service.update_user(current_user["id"], update)
        logger.info(f"✏️ User updated: {updated_user['username']}")
        return UserResponse(**updated_user)
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user")


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: dict = Depends(get_super_admin)
):
    """Delete a user and their tenant data (Super Admin only)"""
    await user_service.delete_user_and_tenant(user_id)
    return {"message": "User and associated data deleted successfully"}
