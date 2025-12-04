"""
Phase 1.5: Onboarding Wizard Tests
===================================

Tests the mandatory onboarding flow for voice provider setup.
"""

import pytest
import httpx
from typing import Dict

BASE_URL = "http://localhost:8000/api/v1"


class TestOnboardingWizard:
    """Test onboarding wizard flow"""
    
    @pytest.fixture
    async def new_user(self):
        """Create a new user (no API keys)"""
        user = {
            "email": "onboarding_test@test.com",
            "password": "Test123!@#",
            "username": "onboarding_test",
            "full_name": "Onboarding Test User",
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
    async def test_new_user_onboarding_incomplete(self, new_user):
        """Test that new user has incomplete onboarding status"""
        auth = await new_user
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{BASE_URL}/onboarding/status",
                headers=auth["headers"]
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["completed"] == False
            assert data["has_voice_provider"] == False
            assert data["voice_provider"] is None
            assert data["agent_deployed"] == False
            
            print(f"✅ New user onboarding incomplete")
    
    @pytest.mark.asyncio
    async def test_get_voice_provider_options(self, new_user):
        """Test retrieving voice provider options"""
        auth = await new_user
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{BASE_URL}/onboarding/voice-providers",
                headers=auth["headers"]
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "providers" in data
            providers = data["providers"]
            
            # Should have at least Vapi, Retell, Bland
            provider_names = [p["id"] for p in providers]
            assert "vapi" in provider_names
            assert "retell" in provider_names
            assert "bland" in provider_names
            
            # Each provider should have required info
            for provider in providers:
                assert "id" in provider
                assert "name" in provider
                assert "description" in provider
                assert "setup_url" in provider
                assert "pricing" in provider
            
            print(f"✅ Voice provider options retrieved: {provider_names}")
    
    @pytest.mark.asyncio
    async def test_setup_vapi_key_success(self, new_user):
        """Test setting up Vapi key during onboarding"""
        auth = await new_user
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            vapi_setup = {
                "provider": "vapi",
                "api_key": "vapi_onboarding_test_key_12345",
                "name": "My Vapi Key"
            }
            
            response = await client.post(
                f"{BASE_URL}/onboarding/setup-voice-key",
                json=vapi_setup,
                headers=auth["headers"]
            )
            
            assert response.status_code == 201, f"Vapi key setup failed: {response.text}"
            data = response.json()
            
            assert "key_id" in data
            assert data["provider"] == "vapi"
            assert data["status"] == "active"
            
            print(f"✅ Vapi key setup successful: {data['key_id']}")
            
            # Verify onboarding status updated
            status_response = await client.get(
                f"{BASE_URL}/onboarding/status",
                headers=auth["headers"]
            )
            
            status_data = status_response.json()
            assert status_data["has_voice_provider"] == True
            assert status_data["voice_provider"] == "vapi"
            
            print(f"✅ Onboarding status updated after key setup")
    
    @pytest.mark.asyncio
    async def test_setup_invalid_vapi_key(self, new_user):
        """Test that invalid Vapi key is rejected"""
        auth = await new_user
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            invalid_vapi = {
                "provider": "vapi",
                "api_key": "invalid_key",  # Too short
                "name": "Invalid Key"
            }
            
            response = await client.post(
                f"{BASE_URL}/onboarding/setup-voice-key",
                json=invalid_vapi,
                headers=auth["headers"]
            )
            
            # Should return 400 or 422 for invalid key
            assert response.status_code in [400, 422], \
                f"Invalid key should be rejected, got {response.status_code}"
            
            print(f"✅ Invalid Vapi key rejected")
    
    @pytest.mark.asyncio
    async def test_setup_retell_key_success(self, new_user):
        """Test setting up Retell key during onboarding"""
        auth = await new_user
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            retell_setup = {
                "provider": "retell",
                "api_key": "retell_onboarding_test_key_67890",
                "name": "My Retell Key"
            }
            
            response = await client.post(
                f"{BASE_URL}/onboarding/setup-voice-key",
                json=retell_setup,
                headers=auth["headers"]
            )
            
            assert response.status_code == 201, f"Retell key setup failed: {response.text}"
            data = response.json()
            
            assert data["provider"] == "retell"
            
            # Verify onboarding status
            status_response = await client.get(
                f"{BASE_URL}/onboarding/status",
                headers=auth["headers"]
            )
            
            status_data = status_response.json()
            assert status_data["has_voice_provider"] == True
            assert status_data["voice_provider"] == "retell"
            
            print(f"✅ Retell key setup successful")
    
    @pytest.mark.asyncio
    async def test_cannot_skip_onboarding_without_voice_key(self, new_user):
        """Test that user cannot skip onboarding without adding voice key"""
        auth = await new_user
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # Try to create agent without completing onboarding
            agent = {
                "name": "Premature Agent",
                "provider": "vapi",
                "voice": "en-US-Neural2-A"
            }
            
            response = await client.post(
                f"{BASE_URL}/agents",
                json=agent,
                headers=auth["headers"]
            )
            
            # Should return 428 Precondition Required
            assert response.status_code == 428, \
                f"Should block agent creation without voice key, got {response.status_code}"
            
            error_data = response.json()
            assert "voice provider" in error_data.get("detail", "").lower() or \
                   "onboarding" in error_data.get("detail", "").lower()
            
            print(f"✅ Cannot skip onboarding without voice key")
    
    @pytest.mark.asyncio
    async def test_configure_agent_after_key_setup(self, new_user):
        """Test configuring agent after voice key is set up"""
        auth = await new_user
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # Setup Vapi key first
            vapi_setup = {
                "provider": "vapi",
                "api_key": "vapi_agent_config_test_key",
                "name": "Agent Config Key"
            }
            
            await client.post(
                f"{BASE_URL}/onboarding/setup-voice-key",
                json=vapi_setup,
                headers=auth["headers"]
            )
            
            # Configure agent
            agent_config = {
                "name": "My First Agent",
                "voice": "en-US-Neural2-A",
                "system_prompt": "You are a helpful AI receptionist.",
                "enable_appointment_booking": True,
                "enable_faq": True
            }
            
            response = await client.post(
                f"{BASE_URL}/onboarding/configure-agent",
                json=agent_config,
                headers=auth["headers"]
            )
            
            # May return 400 if Vapi validation fails with test key
            # but should NOT return 428 (missing key)
            assert response.status_code != 428, \
                "Agent configuration should not fail with 428 after key setup"
            
            if response.status_code == 201:
                data = response.json()
                assert "agent_id" in data
                print(f"✅ Agent configured successfully: {data['agent_id']}")
                
                # Verify onboarding completed
                status_response = await client.get(
                    f"{BASE_URL}/onboarding/status",
                    headers=auth["headers"]
                )
                
                status_data = status_response.json()
                assert status_data["completed"] == True
                assert status_data["agent_deployed"] == True
                assert status_data["agent_id"] is not None
                
                print(f"✅ Onboarding completed after agent configuration")
            else:
                print(f"⚠️ Agent creation returned {response.status_code} (expected with test key)")
    
    @pytest.mark.asyncio
    async def test_onboarding_complete_user(self):
        """Test onboarding status for user who has completed onboarding"""
        # Create user and complete onboarding
        user = {
            "email": "completed_onboarding@test.com",
            "password": "Test123!@#",
            "username": "onboarding_test",
            "full_name": "Completed User",
        }
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # Register
            register_response = await client.post(
                f"{BASE_URL}/users/register",
                json=user
            )
            token = register_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Add Vapi key
            vapi_setup = {
                "provider": "vapi",
                "api_key": "vapi_completed_user_key",
                "name": "Completed User Key"
            }
            
            await client.post(
                f"{BASE_URL}/onboarding/setup-voice-key",
                json=vapi_setup,
                headers=headers
            )
            
            # Check status
            response = await client.get(
                f"{BASE_URL}/onboarding/status",
                headers=headers
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Onboarding should be marked complete (at least voice key step)
            assert data["has_voice_provider"] == True
            assert data["voice_provider"] == "vapi"
            
            print(f"✅ Completed user has correct onboarding status")
    
    @pytest.mark.asyncio
    async def test_update_voice_key_after_onboarding(self, new_user):
        """Test that user can update/change voice key after onboarding"""
        auth = await new_user
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # Initial setup with Vapi
            vapi_setup = {
                "provider": "vapi",
                "api_key": "vapi_initial_key",
                "name": "Initial Vapi Key"
            }
            
            initial_response = await client.post(
                f"{BASE_URL}/onboarding/setup-voice-key",
                json=vapi_setup,
                headers=auth["headers"]
            )
            
            assert initial_response.status_code == 201
            initial_key_id = initial_response.json()["key_id"]
            
            # Update to new Vapi key
            new_vapi_setup = {
                "provider": "vapi",
                "api_key": "vapi_updated_key",
                "name": "Updated Vapi Key"
            }
            
            update_response = await client.post(
                f"{BASE_URL}/onboarding/setup-voice-key",
                json=new_vapi_setup,
                headers=auth["headers"]
            )
            
            assert update_response.status_code == 201
            new_key_id = update_response.json()["key_id"]
            
            # Should have both keys
            keys_response = await client.get(
                f"{BASE_URL}/keys",
                headers=auth["headers"]
            )
            
            keys = keys_response.json()
            vapi_keys = [k for k in keys if k["provider"] == "vapi"]
            assert len(vapi_keys) >= 2, "Should have both old and new Vapi keys"
            
            print(f"✅ User can update voice key after onboarding")


class TestOnboardingEdgeCases:
    """Test edge cases and error scenarios"""
    
    @pytest.fixture
    async def new_user(self):
        """Create a new user (no API keys)"""
        user = {
            "email": "onboarding_test@test.com",
            "password": "Test123!@#",
            "username": "onboarding_test",
            "full_name": "Onboarding Test User",
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
    async def test_onboarding_without_authentication(self):
        """Test that onboarding endpoints require authentication"""
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(f"{BASE_URL}/onboarding/status")
            
            assert response.status_code == 401
            print(f"✅ Onboarding requires authentication")
    
    @pytest.mark.asyncio
    async def test_setup_voice_key_missing_fields(self, new_user):
        """Test that voice key setup validates required fields"""
        auth = await new_user
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # Missing api_key
            incomplete_setup = {
                "provider": "vapi",
                "name": "Incomplete Key"
            }
            
            response = await client.post(
                f"{BASE_URL}/onboarding/setup-voice-key",
                json=incomplete_setup,
                headers=auth["headers"]
            )
            
            assert response.status_code == 422  # Validation error
            print(f"✅ Voice key setup validates required fields")
    
    @pytest.mark.asyncio
    async def test_setup_unsupported_voice_provider(self, new_user):
        """Test that unsupported voice providers are rejected"""
        auth = await new_user
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            unsupported_setup = {
                "provider": "unsupported_provider",
                "api_key": "some_key",
                "name": "Unsupported Provider"
            }
            
            response = await client.post(
                f"{BASE_URL}/onboarding/setup-voice-key",
                json=unsupported_setup,
                headers=auth["headers"]
            )
            
            # Should return 400 or 422
            assert response.status_code in [400, 422]
            print(f"✅ Unsupported voice provider rejected")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
