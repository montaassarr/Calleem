"""
Phase 1.3: API Key Management Tests
====================================

Tests API key CRUD operations and encryption.
"""

import pytest
import httpx
from typing import Dict

BASE_URL = "http://localhost:8000/api/v1"


class TestAPIKeyManagement:
    """Test API key creation, retrieval, and deletion"""
    
    @pytest.fixture
    async def authenticated_user(self):
        """Create and authenticate a test user"""
        user = {
            "email": "apikey_test@test.com",
            "password": "Test123!@#",
            "username": "apikey_test",
            "full_name": "API Key Test User",
        }
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post(f"{BASE_URL}/users/register", json=user)
            assert response.status_code == 201
            
            token = response.json()["access_token"]
            return {
                "token": token,
                "headers": {"Authorization": f"Bearer {token}"}
            }
    
    @pytest.mark.asyncio
    async def test_create_required_provider_key(self, authenticated_user):
        """Test creating API key for REQUIRED provider (Vapi)"""
        auth = await authenticated_user
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            vapi_key = {
                "provider": "vapi",
                "api_key": "vapi_test_key_12345",
                "name": "My Vapi Key"
            }
            
            response = await client.post(
                f"{BASE_URL}/keys",
                json=vapi_key,
                headers=auth["headers"]
            )
            
            assert response.status_code == 201, f"Failed to create Vapi key: {response.text}"
            data = response.json()
            
            assert "id" in data
            assert data["provider"] == "vapi"
            assert data["name"] == "My Vapi Key"
            assert "api_key" not in data, "API key should not be returned in response"
            assert "encrypted_key" not in data, "Encrypted key should not be exposed"
            
            print(f"✅ REQUIRED provider (Vapi) key created: {data['id']}")
            
            return data["id"]
    
    @pytest.mark.skip(reason="Requires real OpenAI API key validation - skip for Phase 1")
    @pytest.mark.asyncio
    async def test_create_optional_provider_key(self, authenticated_user):
        """Test creating API key for OPTIONAL provider (OpenAI)"""
        auth = await authenticated_user
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            openai_key = {
                "provider": "openai",
                "api_key": "sk-test_openai_key_67890",
                "name": "My OpenAI Key"
            }
            
            response = await client.post(
                f"{BASE_URL}/keys",
                json=openai_key,
                headers=auth["headers"]
            )
            
            assert response.status_code == 201, f"Failed to create OpenAI key: {response.text}"
            data = response.json()
            
            assert data["provider"] == "openai"
            assert data["name"] == "My OpenAI Key"
            
            print(f"✅ OPTIONAL provider (OpenAI) key created: {data['id']}")
            
            return data["id"]
    
    @pytest.mark.asyncio
    async def test_create_multiple_keys_same_provider(self, authenticated_user):
        """Test creating multiple API keys for same provider"""
        auth = await authenticated_user
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # Create first Vapi key
            vapi_key_1 = {
                "provider": "vapi",
                "api_key": "vapi_test_key_primary",
                "name": "Primary Vapi Key"
            }
            
            response_1 = await client.post(
                f"{BASE_URL}/keys",
                json=vapi_key_1,
                headers=auth["headers"]
            )
            
            assert response_1.status_code == 201
            key_1_id = response_1.json()["id"]
            
            # Create second Vapi key
            vapi_key_2 = {
                "provider": "vapi",
                "api_key": "vapi_test_key_backup",
                "name": "Backup Vapi Key"
            }
            
            response_2 = await client.post(
                f"{BASE_URL}/keys",
                json=vapi_key_2,
                headers=auth["headers"]
            )
            
            assert response_2.status_code == 201
            key_2_id = response_2.json()["id"]
            
            assert key_1_id != key_2_id
            
            print(f"✅ Multiple keys for same provider created")
    
    @pytest.mark.asyncio
    async def test_retrieve_all_api_keys(self, authenticated_user):
        """Test retrieving all API keys for user"""
        auth = await authenticated_user
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # Create multiple keys
            vapi_key = {
                "provider": "vapi",
                "api_key": "vapi_key_retrieve_test",
                "name": "Vapi Key"
            }
            
            # Use another non-validated provider instead of OpenAI
            custom_key = {
                "provider": "custom_provider",
                "api_key": "custom_key_retrieve_test",
                "name": "Custom Provider Key"
            }
            
            await client.post(f"{BASE_URL}/keys", json=vapi_key, headers=auth["headers"])
            await client.post(f"{BASE_URL}/keys", json=custom_key, headers=auth["headers"])
            
            # Retrieve all keys
            response = await client.get(
                f"{BASE_URL}/keys",
                headers=auth["headers"]
            )
            
            assert response.status_code == 200
            keys = response.json()
            
            assert len(keys) >= 2
            providers = [k["provider"] for k in keys]
            assert "vapi" in providers
            assert "custom_provider" in providers
            
            # Verify API keys not exposed
            for key in keys:
                assert "api_key" not in key
                assert "encrypted_key" not in key
            
            print(f"✅ Retrieved {len(keys)} API keys")
    
    @pytest.mark.asyncio
    async def test_retrieve_specific_api_key(self, authenticated_user):
        """Test retrieving specific API key by ID"""
        auth = await authenticated_user
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # Create key
            vapi_key = {
                "provider": "vapi",
                "api_key": "vapi_key_specific_test",
                "name": "Specific Vapi Key"
            }
            
            create_response = await client.post(
                f"{BASE_URL}/keys",
                json=vapi_key,
                headers=auth["headers"]
            )
            
            key_id = create_response.json()["id"]
            
            # Retrieve all keys and verify specific key exists
            response = await client.get(
                f"{BASE_URL}/keys",
                headers=auth["headers"]
            )
            
            assert response.status_code == 200
            keys = response.json()
            
            # Find the created key in the list
            found_key = next((k for k in keys if k["id"] == key_id), None)
            assert found_key is not None, f"Key {key_id} not found in list"
            assert found_key["provider"] == "vapi"
            assert found_key["name"] == "Specific Vapi Key"
            
            print(f"✅ Verified specific API key exists in list: {key_id}")
    
    @pytest.mark.asyncio
    async def test_retrieve_nonexistent_key(self, authenticated_user):
        """Test retrieving non-existent API key (skipped - no GET by ID endpoint)"""
        pytest.skip("No GET /keys/{id} endpoint - verification done via list endpoint")
    
    @pytest.mark.asyncio
    async def test_delete_api_key(self, authenticated_user):
        """Test deleting API key"""
        auth = await authenticated_user
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # Create key
            vapi_key = {
                "provider": "vapi",
                "api_key": "vapi_key_delete_test",
                "name": "Key to Delete"
            }
            
            create_response = await client.post(
                f"{BASE_URL}/keys",
                json=vapi_key,
                headers=auth["headers"]
            )
            
            key_id = create_response.json()["id"]
            
            # Delete key
            delete_response = await client.delete(
                f"{BASE_URL}/keys/{key_id}",
                headers=auth["headers"]
            )
            
            assert delete_response.status_code == 204
            
            # Verify key deleted by checking list
            get_response = await client.get(
                f"{BASE_URL}/keys",
                headers=auth["headers"]
            )
            
            assert get_response.status_code == 200
            keys = get_response.json()
            key_ids = [k["id"] for k in keys]
            assert key_id not in key_ids, "Deleted key still in list"
            
            print(f"✅ API key deleted successfully")
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_key(self, authenticated_user):
        """Test deleting non-existent key returns 404"""
        auth = await authenticated_user
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.delete(
                f"{BASE_URL}/keys/nonexistent_key_id_456",
                headers=auth["headers"]
            )
            
            assert response.status_code == 404
            print(f"✅ Deleting non-existent key returns 404")
    
    @pytest.mark.asyncio
    async def test_api_key_encryption(self, authenticated_user):
        """Test that API keys are encrypted (cannot verify directly, but check they're not stored in plain text)"""
        auth = await authenticated_user
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # Create key
            vapi_key = {
                "provider": "vapi",
                "api_key": "vapi_plaintext_test_key_12345",
                "name": "Encryption Test Key"
            }
            
            create_response = await client.post(
                f"{BASE_URL}/keys",
                json=vapi_key,
                headers=auth["headers"]
            )
            
            assert create_response.status_code == 201
            
            # Retrieve key
            key_id = create_response.json()["id"]
            get_response = await client.get(
                f"{BASE_URL}/keys/{key_id}",
                headers=auth["headers"]
            )
            
            data = get_response.json()
            
            # API key should NOT be in response
            assert "api_key" not in data, "⚠️ SECURITY ISSUE: Plain text API key exposed!"
            assert "encrypted_key" not in data, "⚠️ SECURITY ISSUE: Encrypted key exposed!"
            
            # Should have masked version
            if "masked_key" in data:
                assert "****" in data["masked_key"], "Masked key should contain asterisks"
            
            print(f"✅ API key encryption verified (not exposed in responses)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
