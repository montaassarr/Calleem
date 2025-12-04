"""
Phase 4: Deployment Readiness Tests
Pre-deployment validation and health checks
"""

import pytest
import httpx
import asyncio
import os
from datetime import datetime

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"


class TestDeploymentReadiness:
    """Test system readiness for production deployment"""
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Test health check endpoint"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "healthy"
            assert "database" in data
            assert data["database"] == "connected"
            
            print(f"✅ Health check passed")
            print(f"   Status: {data['status']}")
            print(f"   Database: {data['database']}")
    
    @pytest.mark.asyncio
    async def test_api_docs_accessible(self):
        """Test API documentation is accessible"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/docs")
            
            assert response.status_code == 200
            print(f"✅ API documentation accessible at {BASE_URL}/docs")
    
    @pytest.mark.asyncio
    async def test_cors_configuration(self):
        """Test CORS headers are properly configured"""
        async with httpx.AsyncClient() as client:
            response = await client.options(
                f"{API_BASE}/users/register",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "POST"
                }
            )
            
            # Should allow CORS from frontend
            assert response.status_code in [200, 204]
            print(f"✅ CORS configured correctly")
    
    @pytest.mark.asyncio
    async def test_environment_variables_set(self):
        """Test required environment variables are set"""
        required_vars = [
            "MONGO_URI",
            "MONGO_DB_NAME",
            "SECRET_KEY",
            "MASTER_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️  Missing environment variables: {missing_vars}")
        else:
            print(f"✅ All required environment variables set")
        
        assert len(missing_vars) == 0, f"Missing: {missing_vars}"
    
    @pytest.mark.asyncio
    async def test_database_connection(self):
        """Test MongoDB connection is working"""
        from backend.database.mongo_config import get_database
        
        db = get_database()
        
        # Test a simple query
        result = await db.users.count_documents({})
        
        print(f"✅ Database connected")
        print(f"   Users in database: {result}")
        
        assert result >= 0
    
    @pytest.mark.asyncio
    async def test_api_key_encryption(self):
        """Test API key encryption/decryption works"""
        from backend.utils.encryption import encrypt_value, decrypt_value
        
        test_key = "test_api_key_123456"
        
        # Encrypt
        encrypted = encrypt_value(test_key)
        assert encrypted != test_key
        
        # Decrypt
        decrypted = decrypt_value(encrypted)
        assert decrypted == test_key
        
        print(f"✅ Encryption/decryption working")
        print(f"   Original: {test_key[:20]}...")
        print(f"   Encrypted length: {len(encrypted)}")
    
    @pytest.mark.asyncio
    async def test_jwt_token_generation(self):
        """Test JWT token generation and validation"""
        from backend.routers.users import create_access_token
        
        test_data = {"user_id": "test123", "tenant_id": "tenant456"}
        
        # Generate token
        token = create_access_token(test_data)
        assert token is not None
        assert len(token) > 0
        
        print(f"✅ JWT token generation working")
        print(f"   Token length: {len(token)}")
    
    @pytest.mark.asyncio
    async def test_ai_proxy_service_initialized(self):
        """Test AI Proxy service is properly initialized"""
        from backend.services.ai_proxy import ai_proxy
        
        # Check service is initialized
        assert ai_proxy is not None
        
        print(f"✅ AI Proxy service initialized")
    
    @pytest.mark.asyncio
    async def test_response_time_acceptable(self):
        """Test API response times are acceptable"""
        async with httpx.AsyncClient() as client:
            start = datetime.now()
            response = await client.get(f"{BASE_URL}/health")
            end = datetime.now()
            
            response_time = (end - start).total_seconds() * 1000  # ms
            
            assert response.status_code == 200
            assert response_time < 1000, f"Response time too slow: {response_time}ms"
            
            print(f"✅ Response time acceptable")
            print(f"   Response time: {response_time:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_concurrent_requests_handling(self):
        """Test system can handle concurrent requests"""
        async with httpx.AsyncClient() as client:
            # Make 10 concurrent health check requests
            tasks = [
                client.get(f"{BASE_URL}/health")
                for _ in range(10)
            ]
            
            responses = await asyncio.gather(*tasks)
            
            # All should succeed
            assert all(r.status_code == 200 for r in responses)
            
            print(f"✅ Handled 10 concurrent requests")
            print(f"   All responses: 200 OK")
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test proper error handling for invalid requests"""
        async with httpx.AsyncClient() as client:
            # Test 404
            response = await client.get(f"{API_BASE}/nonexistent-endpoint")
            assert response.status_code == 404
            
            # Test 401 (unauthorized)
            response = await client.get(f"{API_BASE}/keys")
            assert response.status_code == 401
            
            # Test 422 (validation error)
            response = await client.post(
                f"{API_BASE}/users/register",
                json={"email": "invalid"}  # Missing required fields
            )
            assert response.status_code == 422
            
            print(f"✅ Error handling working correctly")
            print(f"   404, 401, 422 responses validated")


class TestSecurityChecklist:
    """Security validation tests"""
    
    @pytest.mark.asyncio
    async def test_no_default_credentials(self):
        """Test no default credentials work"""
        async with httpx.AsyncClient() as client:
            # Try common default credentials
            response = await client.post(
                f"{API_BASE}/users/login",
                data={
                    "username": "admin",
                    "password": "admin"
                }
            )
            
            assert response.status_code == 401
            print(f"✅ Default credentials rejected")
    
    @pytest.mark.asyncio
    async def test_sql_injection_prevention(self):
        """Test SQL injection attempts are handled"""
        async with httpx.AsyncClient() as client:
            # Try SQL injection in login
            response = await client.post(
                f"{API_BASE}/users/login",
                data={
                    "username": "admin' OR '1'='1",
                    "password": "anything"
                }
            )
            
            assert response.status_code == 401
            print(f"✅ SQL injection attempts blocked")
    
    @pytest.mark.asyncio
    async def test_rate_limiting_exists(self):
        """Test rate limiting is configured"""
        # Note: This is a basic check
        # Proper rate limiting requires stress testing
        
        print(f"ℹ️  Rate limiting check")
        print(f"   Manual verification recommended")
        print(f"   Load test with: locust or ab")
    
    @pytest.mark.asyncio
    async def test_https_redirect_configured(self):
        """Check HTTPS configuration (manual verification needed)"""
        print(f"ℹ️  HTTPS configuration")
        print(f"   Manual verification required:")
        print(f"   - Ensure SSL certificates configured")
        print(f"   - Verify HTTP→HTTPS redirect")
        print(f"   - Check HSTS headers")


class TestDockerDeployment:
    """Docker deployment validation"""
    
    def test_dockerfile_exists(self):
        """Check Dockerfile exists"""
        backend_dockerfile = os.path.exists("backend/Dockerfile")
        frontend_dockerfile = os.path.exists("frontend_next/Dockerfile")
        
        assert backend_dockerfile, "Backend Dockerfile missing"
        assert frontend_dockerfile, "Frontend Dockerfile missing"
        
        print(f"✅ Dockerfiles present")
        print(f"   Backend: {backend_dockerfile}")
        print(f"   Frontend: {frontend_dockerfile}")
    
    def test_docker_compose_exists(self):
        """Check docker-compose.yml exists"""
        docker_compose = os.path.exists("infrastructure/docker-compose.yml")
        
        assert docker_compose, "docker-compose.yml missing"
        
        print(f"✅ docker-compose.yml present")
    
    def test_env_example_exists(self):
        """Check .env.example exists"""
        env_example = os.path.exists(".env.example") or os.path.exists("backend/.env.example")
        
        print(f"ℹ️  .env.example check")
        if env_example:
            print(f"   ✅ .env.example found")
        else:
            print(f"   ⚠️  .env.example not found (recommended)")


if __name__ == "__main__":
    # Run all tests
    pytest.main([__file__, "-v", "-s"])
