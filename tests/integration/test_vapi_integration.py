"""
Phase 2: Vapi Integration Tests
Tests voice provider integration with real API keys
"""

import pytest
import httpx
from typing import Dict
import asyncio

BASE_URL = "http://localhost:8000/api/v1"

# These tests require real Vapi API keys
# Mark them to be skipped unless INTEGRATION_TEST=true
pytestmark = pytest.mark.skipif(
    pytest.config.getoption("--skip-integration", default=True),
    reason="Skipping integration tests - use --skip-integration=false to run"
)


@pytest.fixture
async def test_user_with_vapi():
    """Create a test user and add real Vapi key"""
    async with httpx.AsyncClient() as client:
        # Register user
        user_data = {
            "email": "vapi_test@example.com",
            "username": "vapi_test_user",
            "password": "SecurePass123!@#",
            "full_name": "Vapi Test User"
        }
        
        response = await client.post(f"{BASE_URL}/users/register", json=user_data)
        assert response.status_code == 201
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Add Vapi key (from environment or test config)
        import os
        vapi_key = os.getenv("TEST_VAPI_KEY", "957f3d01-6229-4834-bfff-667ccf49ff50")
        
        key_data = {
            "provider": "vapi",
            "api_key": vapi_key,
            "name": "Test Vapi Key"
        }
        
        response = await client.post(
            f"{BASE_URL}/keys",
            json=key_data,
            headers=headers
        )
        assert response.status_code == 201
        
        yield {"token": token, "headers": headers, "vapi_key": vapi_key}
        
        # Cleanup: Delete user (optional)
        # Could implement cleanup in teardown


class TestVapiIntegration:
    """Test Vapi voice provider integration"""
    
    @pytest.mark.asyncio
    async def test_vapi_key_validation(self, test_user_with_vapi):
        """Test that Vapi key is validated against real API"""
        headers = test_user_with_vapi["headers"]
        
        async with httpx.AsyncClient() as client:
            # Check onboarding status - should show vapi as provider
            response = await client.get(
                f"{BASE_URL}/onboarding/status",
                headers=headers
            )
            
            assert response.status_code == 200
            status = response.json()
            
            assert status["has_voice_provider"] is True
            assert status["voice_provider"] == "vapi"
            assert status["current_step"] == 3  # Ready to create agent
    
    @pytest.mark.asyncio
    async def test_vapi_assistant_list(self, test_user_with_vapi):
        """Test fetching assistants from Vapi"""
        headers = test_user_with_vapi["headers"]
        
        async with httpx.AsyncClient() as client:
            # Call voice agent status endpoint
            response = await client.get(
                f"{BASE_URL}/voice-agent/status",
                headers=headers
            )
            
            # Should succeed or return 404 if no assistants configured
            assert response.status_code in [200, 404]
            
            if response.status_code == 200:
                data = response.json()
                assert "status" in data
                assert data["status"] in ["active", "not_configured"]
    
    @pytest.mark.asyncio
    async def test_create_agent_with_vapi(self, test_user_with_vapi):
        """Test creating a voice agent that deploys to Vapi"""
        headers = test_user_with_vapi["headers"]
        
        # First, get tenant_id from token
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/users/me", headers=headers)
            assert response.status_code == 200
            tenant_id = response.json()["tenant_id"]
            
            # Create agent
            agent_data = {
                "tenant_id": tenant_id,
                "name": "Test Receptionist",
                "description": "Test voice agent for integration testing",
                "llm_model": "gpt-3.5-turbo",
                "llm_temperature": 0.7,
                "system_prompt": "You are a helpful receptionist.",
                "status": "draft",
                "voice_settings": {
                    "provider": "elevenlabs",
                    "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Default voice
                    "stability": 0.5,
                    "similarity_boost": 0.5
                },
                "webhook_urls": {
                    "book_appointment": "https://n8n.example.com/webhook/book",
                    "cancel_appointment": "https://n8n.example.com/webhook/cancel",
                    "get_available_slots": "https://n8n.example.com/webhook/slots"
                }
            }
            
            response = await client.post(
                f"{BASE_URL}/agents",
                json=agent_data,
                headers=headers
            )
            
            # Should create agent successfully
            assert response.status_code == 201
            agent = response.json()
            
            assert agent["name"] == "Test Receptionist"
            assert agent["status"] == "draft"
            assert "_id" in agent
    
    @pytest.mark.asyncio
    async def test_deploy_agent_to_vapi(self, test_user_with_vapi):
        """Test deploying agent to Vapi (creates assistant)"""
        headers = test_user_with_vapi["headers"]
        
        async with httpx.AsyncClient() as client:
            # Get tenant_id
            response = await client.get(f"{BASE_URL}/users/me", headers=headers)
            tenant_id = response.json()["tenant_id"]
            
            # Create agent first
            agent_data = {
                "tenant_id": tenant_id,
                "name": "Deploy Test Agent",
                "description": "Agent for deployment testing",
                "llm_model": "gpt-3.5-turbo",
                "llm_temperature": 0.7,
                "system_prompt": "You are a test receptionist.",
                "status": "draft",
                "voice_settings": {
                    "provider": "elevenlabs",
                    "voice_id": "21m00Tcm4TlvDq8ikWAM",
                    "stability": 0.5,
                    "similarity_boost": 0.5
                },
                "webhook_urls": {
                    "book_appointment": "https://n8n.example.com/webhook/book",
                    "cancel_appointment": "https://n8n.example.com/webhook/cancel",
                    "get_available_slots": "https://n8n.example.com/webhook/slots"
                }
            }
            
            response = await client.post(
                f"{BASE_URL}/agents",
                json=agent_data,
                headers=headers
            )
            assert response.status_code == 201
            agent_id = response.json()["_id"]
            
            # Deploy agent
            response = await client.post(
                f"{BASE_URL}/agents/{agent_id}/deploy",
                headers=headers
            )
            
            # Should deploy successfully to Vapi
            # This creates a Vapi assistant using tenant's API key
            assert response.status_code == 200
            deployed_agent = response.json()
            
            assert deployed_agent["status"] == "active"
            assert "vapi_assistant_id" in deployed_agent
            assert deployed_agent["vapi_assistant_id"] is not None
    
    @pytest.mark.asyncio
    async def test_multi_tenant_vapi_isolation(self):
        """Test that two tenants can use same Vapi account but data is isolated"""
        # This is a critical test for multi-tenancy
        
        # Create Tenant A
        async with httpx.AsyncClient() as client:
            user_a_data = {
                "email": "tenant_a_vapi@test.com",
                "username": "tenant_a_vapi",
                "password": "Password123!@#",
                "full_name": "Tenant A"
            }
            
            response = await client.post(f"{BASE_URL}/users/register", json=user_a_data)
            assert response.status_code == 201
            token_a = response.json()["access_token"]
            headers_a = {"Authorization": f"Bearer {token_a}"}
            
            # Add same Vapi key for Tenant A
            import os
            vapi_key = os.getenv("TEST_VAPI_KEY", "957f3d01-6229-4834-bfff-667ccf49ff50")
            
            response = await client.post(
                f"{BASE_URL}/keys",
                json={"provider": "vapi", "api_key": vapi_key, "name": "Tenant A Vapi"},
                headers=headers_a
            )
            assert response.status_code == 201
            
            # Create Tenant B
            user_b_data = {
                "email": "tenant_b_vapi@test.com",
                "username": "tenant_b_vapi",
                "password": "Password456!@#",
                "full_name": "Tenant B"
            }
            
            response = await client.post(f"{BASE_URL}/users/register", json=user_b_data)
            assert response.status_code == 201
            token_b = response.json()["access_token"]
            headers_b = {"Authorization": f"Bearer {token_b}"}
            
            # Add same Vapi key for Tenant B
            response = await client.post(
                f"{BASE_URL}/keys",
                json={"provider": "vapi", "api_key": vapi_key, "name": "Tenant B Vapi"},
                headers=headers_b
            )
            assert response.status_code == 201
            
            # Verify isolation
            # Tenant A lists their keys
            response = await client.get(f"{BASE_URL}/keys", headers=headers_a)
            assert response.status_code == 200
            keys_a = response.json()
            assert len(keys_a) == 1
            assert keys_a[0]["name"] == "Tenant A Vapi"
            
            # Tenant B lists their keys
            response = await client.get(f"{BASE_URL}/keys", headers=headers_b)
            assert response.status_code == 200
            keys_b = response.json()
            assert len(keys_b) == 1
            assert keys_b[0]["name"] == "Tenant B Vapi"
            
            # Keys have different IDs even though same API key value
            assert keys_a[0]["id"] != keys_b[0]["id"]
            
            print("✅ Multi-tenant Vapi isolation verified!")


class TestVapiCallHistory:
    """Test Vapi call history integration"""
    
    @pytest.mark.asyncio
    async def test_fetch_call_history(self, test_user_with_vapi):
        """Test fetching call history from Vapi"""
        headers = test_user_with_vapi["headers"]
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/voice-agent/history",
                headers=headers
            )
            
            # Should return call history or empty list
            assert response.status_code == 200
            data = response.json()
            
            assert "items" in data
            assert isinstance(data["items"], list)
    
    @pytest.mark.asyncio
    async def test_call_history_pagination(self, test_user_with_vapi):
        """Test call history with pagination"""
        headers = test_user_with_vapi["headers"]
        
        async with httpx.AsyncClient() as client:
            # Request with limit
            response = await client.get(
                f"{BASE_URL}/voice-agent/history?limit=5",
                headers=headers
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Should return max 5 items
            assert len(data["items"]) <= 5


class TestVapiKeyValidation:
    """Test Vapi key validation"""
    
    @pytest.mark.asyncio
    async def test_invalid_vapi_key_rejected(self):
        """Test that invalid Vapi key is rejected"""
        async with httpx.AsyncClient() as client:
            # Register user
            user_data = {
                "email": "invalid_key_test@example.com",
                "username": "invalid_key_test",
                "password": "Password123!@#",
                "full_name": "Invalid Key Test"
            }
            
            response = await client.post(f"{BASE_URL}/users/register", json=user_data)
            assert response.status_code == 201
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Try to add invalid Vapi key
            invalid_key_data = {
                "provider": "vapi",
                "api_key": "invalid_key_12345",
                "name": "Invalid Vapi Key"
            }
            
            response = await client.post(
                f"{BASE_URL}/keys",
                json=invalid_key_data,
                headers=headers
            )
            
            # Should reject invalid key
            # Note: This requires backend validation against Vapi API
            # If validation not implemented, this test will fail
            assert response.status_code == 400
            error = response.json()
            assert "detail" in error
            assert "invalid" in error["detail"].lower()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--skip-integration=false"])
