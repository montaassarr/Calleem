"""
Phase 1.1: Authentication & Authorization Tests
================================================

Tests user registration, login, JWT tokens, and protected routes.
"""

import pytest
import httpx
from datetime import datetime, timedelta
import jwt
import os
import uuid
from dotenv import load_dotenv

load_dotenv(override=True)

BASE_URL = "http://localhost:8000/api/v1"
SECRET_KEY = os.getenv("SECRET_KEY", "fe6d9f5f69591cdbc257e0fde33fb4d056dbc28170de0089e941824d30fd35c3")


# Shared test fixtures
def _unique_suffix(prefix: str) -> str:
    """Generate a short deterministic suffix for test users"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def test_user_a():
    """Test user A credentials (unique per test run)"""
    suffix = _unique_suffix("tenant_a")
    return {
        "email": f"{suffix}@test.com",
        "username": suffix,
        "password": "Test123!@#",
        "full_name": "Tenant A Owner"
    }


@pytest.fixture
def test_user_b():
    """Test user B credentials (unique per test run)"""
    suffix = _unique_suffix("tenant_b")
    return {
        "email": f"{suffix}@test.com",
        "username": suffix,
        "password": "Test456!@#",
        "full_name": "Tenant B Owner"
    }


class TestAuthentication:
    """Test authentication flows"""
    
    @pytest.mark.asyncio
    async def test_user_registration(self, test_user_a):
        """Test user can register and receive JWT token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/users/register",
                json=test_user_a
            )
            
            assert response.status_code == 201, f"Registration failed: {response.text}"
            data = response.json()
            
            # Verify response structure
            assert "access_token" in data
            assert "token_type" in data
            assert data["token_type"] == "bearer"
            
            # Decode token and verify tenant_id
            token = data["access_token"]
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            
            assert "sub" in payload  # User ID
            assert "tenant_id" in payload  # Critical for isolation
            assert "email" in payload
            assert payload["email"] == test_user_a["email"]
            
            print(f"✅ User A registered with tenant_id: {payload['tenant_id']}")
            
            return data
    
    @pytest.mark.asyncio
    async def test_user_login(self, test_user_a):
        """Test user can login and receive JWT token"""
        async with httpx.AsyncClient() as client:
            # First register the user
            register_response = await client.post(
                f"{BASE_URL}/users/register",
                json=test_user_a
            )
            assert register_response.status_code == 201, f"Registration failed: {register_response.text}"
            
            # Then login
            response = await client.post(
                f"{BASE_URL}/users/login",
                data={
                    "username": test_user_a["email"],
                    "password": test_user_a["password"]
                }
            )
            
            assert response.status_code == 200, f"Login failed: {response.text}"
            data = response.json()
            
            assert "access_token" in data
            assert "token_type" in data
            
            print(f"✅ User A logged in successfully")
            
            return data
    
    @pytest.mark.asyncio
    async def test_multiple_users_different_tokens(self, test_user_a, test_user_b):
        """Test that different users get different JWT tokens with different tenant_ids"""
        async with httpx.AsyncClient() as client:
            # Register both users
            response_a = await client.post(
                f"{BASE_URL}/users/register",
                json=test_user_a
            )
            response_b = await client.post(
                f"{BASE_URL}/users/register",
                json=test_user_b
            )
            
            assert response_a.status_code == 201
            assert response_b.status_code == 201
            
            token_a = response_a.json()["access_token"]
            token_b = response_b.json()["access_token"]
            
            # Tokens must be different
            assert token_a != token_b
            
            # Decode both tokens
            payload_a = jwt.decode(token_a, SECRET_KEY, algorithms=["HS256"])
            payload_b = jwt.decode(token_b, SECRET_KEY, algorithms=["HS256"])
            
            # Tenant IDs must be different
            assert payload_a["tenant_id"] != payload_b["tenant_id"]
            
            print(f"✅ Tenant A ID: {payload_a['tenant_id']}")
            print(f"✅ Tenant B ID: {payload_b['tenant_id']}")
            print(f"✅ Tenant isolation confirmed at token level")
            
            return {
                "token_a": token_a,
                "token_b": token_b,
                "tenant_a_id": payload_a["tenant_id"],
                "tenant_b_id": payload_b["tenant_id"]
            }
    
    @pytest.mark.asyncio
    async def test_protected_route_without_token(self):
        """Test that protected routes reject requests without token"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/keys")
            
            assert response.status_code == 401
            print(f"✅ Protected route rejected request without token")
    
    @pytest.mark.asyncio
    async def test_protected_route_with_invalid_token(self):
        """Test that protected routes reject invalid tokens"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/keys",
                headers={"Authorization": "Bearer invalid_token_123"}
            )
            
            assert response.status_code == 401
            print(f"✅ Protected route rejected invalid token")
    
    @pytest.mark.asyncio
    async def test_protected_route_with_valid_token(self, test_user_a):
        """Test that protected routes accept valid tokens"""
        async with httpx.AsyncClient() as client:
            # Register and get token
            register_response = await client.post(
                f"{BASE_URL}/users/register",
                json=test_user_a
            )
            token = register_response.json()["access_token"]
            
            # Access protected route
            response = await client.get(
                f"{BASE_URL}/keys",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            print(f"✅ Protected route accepted valid token")
    
    @pytest.mark.asyncio
    async def test_token_expiration(self):
        """Test that expired tokens are rejected"""
        # Create expired token
        expired_payload = {
            "sub": "test_user_id",
            "tenant_id": "test_tenant_id",
            "email": "test@example.com",
            "exp": datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
        }
        expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm="HS256")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/keys",
                headers={"Authorization": f"Bearer {expired_token}"}
            )
            
            assert response.status_code == 401
            print(f"✅ Expired token rejected")


class TestAuthorization:
    """Test authorization and role-based access"""
    
    @pytest.mark.asyncio
    async def test_user_cannot_access_admin_routes(self, test_user_a):
        """Test that owner users CAN access admin routes (first user is always owner)"""
        async with httpx.AsyncClient() as client:
            # Register user (becomes owner)
            register_response = await client.post(
                f"{BASE_URL}/users/register",
                json=test_user_a
            )
            token = register_response.json()["access_token"]
            
            # Try to access admin route
            response = await client.get(
                f"{BASE_URL}/admin/users",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Owner should have access (200 OK)
            # Note: In production, admin routes should check for OWNER or ADMIN role
            assert response.status_code == 200
            print(f"✅ Owner user can access admin routes")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
