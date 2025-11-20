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

from models.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    Token,
    TokenData,
    LoginRequest
)
from database.mongo_config import get_database
from utils.config import settings

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
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
        
        token_data = TokenData(user_id=user_id)
        
    except JWTError:
        raise credentials_exception
    
    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    
    if user is None:
        raise credentials_exception
    
    user["id"] = str(user["_id"])
    
    return user


@router.post("/register", response_model=UserResponse, status_code=201)
async def register_user(user: UserCreate):
    """Register a new user"""
    try:
        db = get_database()

        if not settings.ALLOW_SELF_REGISTRATION:
            raise HTTPException(
                status_code=403,
                detail="Self-service registration is disabled. Please contact the shop owner to request access."
            )

        max_users = settings.MAX_DASHBOARD_USERS
        if max_users and max_users > 0:
            active_users = await db.users.count_documents({"active": True})
            if active_users >= max_users:
                raise HTTPException(
                    status_code=403,
                    detail=f"User limit reached (max {max_users} active users). Deactivate an account before adding another."
                )
        
        # Check if user exists
        existing_email = await db.users.find_one({"email": user.email})
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        existing_username = await db.users.find_one({"username": user.username})
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already taken")
        
        # Hash password
        user_dict = user.model_dump(exclude={"password"})
        user_dict["hashed_password"] = hash_password(user.password)
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = datetime.utcnow()
        user_dict["last_login"] = None
        
        # Insert user
        result = await db.users.insert_one(user_dict)
        
        # Retrieve created user
        created_user = await db.users.find_one({"_id": result.inserted_id})
        created_user["id"] = str(created_user["_id"])
        
        logger.info(f"User registered: {created_user['username']}")
        
        return UserResponse(**created_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to register user")


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """User login - returns JWT token"""
    try:
        db = get_database()
        
        # Find user
        user = await db.users.find_one({"username": form_data.username})
        
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
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user["_id"]), "username": user["username"], "role": user["role"]}
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
        update_data = {
            k: v
            for k, v in update.model_dump(exclude_unset=True).items()
            if v is not None
        }
        
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
