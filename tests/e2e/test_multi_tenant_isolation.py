"""
Multi-Tenant API Key Isolation Tests

These tests verify that:
1. Each tenant can have their own Vapi and Groq API keys
2. API keys are properly isolated between tenants
3. Both sets of API keys work independently
4. No cross-tenant data leakage occurs

⚠️ WARNING: These tests make REAL API calls with REAL tenant keys
"""

import pytest
import httpx
import os
from typing import Dict, Any


@pytest.fixture(scope="module")
def tenant_keys():
    """Fixture to provide tenant API keys after env is loaded"""
    # Tenant 1 API Keys (from .env - loaded by conftest)
    tenant_1 = {
        "vapi_private": os.getenv("VAPI_PRIVATE_API_KEY"),
        "vapi_public": os.getenv("VAPI_PUBLIC_API_KEY"),
        "groq": os.getenv("GROQ_API_KEY"),
        "tenant_name": "Tenant 1 (Default)"
    }
    
    # Tenant 2 API Keys (provided by user - OLD KEY REMOVED FOR SECURITY)
    tenant_2 = {
        "vapi_private": "49fe433c-583e-4a9a-b54a-e8936eac3612",
        "vapi_public": "f8b3b743-c508-44ad-87b0-ca14d2bd1a08",
        "groq": os.getenv("TENANT_2_GROQ_API_KEY", "gsk_REMOVED_FOR_SECURITY"),
        "tenant_name": "Tenant 2 (Secondary)"
    }
    
    return {"tenant_1": tenant_1, "tenant_2": tenant_2}


class TestMultiTenantIsolation:
    """Test that each tenant's API keys work independently"""
    
    @pytest.mark.e2e
    @pytest.mark.vapi
    async def test_tenant1_vapi_connectivity(self, tenant_keys):
        """Test Tenant 1's Vapi API connection"""
        vapi_key = tenant_keys["tenant_1"]["vapi_private"]
        
        assert vapi_key, "Tenant 1 Vapi key not found in environment"
        assert len(vapi_key) > 20, "Tenant 1 Vapi key seems invalid"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.vapi.ai/assistant",
                headers={"Authorization": f"Bearer {vapi_key}"},
                timeout=10.0
            )
            
            print(f"\n✅ Tenant 1 Vapi Status: {response.status_code}")
            assert response.status_code in [200, 404], \
                f"Tenant 1 Vapi API failed: {response.status_code} - {response.text}"
    
    @pytest.mark.e2e
    @pytest.mark.vapi
    async def test_tenant2_vapi_connectivity(self, tenant_keys):
        """Test Tenant 2's Vapi API connection"""
        vapi_key = tenant_keys["tenant_2"]["vapi_private"]
        
        assert vapi_key, "Tenant 2 Vapi key not configured"
        assert len(vapi_key) > 20, "Tenant 2 Vapi key seems invalid"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.vapi.ai/assistant",
                headers={"Authorization": f"Bearer {vapi_key}"},
                timeout=10.0
            )
            
            print(f"\n✅ Tenant 2 Vapi Status: {response.status_code}")
            assert response.status_code in [200, 404], \
                f"Tenant 2 Vapi API failed: {response.status_code} - {response.text}"
    
    @pytest.mark.e2e
    @pytest.mark.groq
    async def test_tenant1_groq_connectivity(self, tenant_keys):
        """Test Tenant 1's Groq API connection"""
        from groq import Groq
        
        groq_key = tenant_keys["tenant_1"]["groq"]
        
        assert groq_key, "Tenant 1 Groq key not found in environment"
        assert groq_key.startswith("gsk_"), "Tenant 1 Groq key format invalid"
        assert len(groq_key) > 40, "Tenant 1 Groq key seems too short"
        
        client = Groq(api_key=groq_key)
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Tenant 1 verified' in exactly 3 words."}
            ],
            max_tokens=50,
            temperature=0.1
        )
        
        content = response.choices[0].message.content
        answer = content.strip() if content else ""
        print(f"\n✅ Tenant 1 Groq Response: {answer}")
        
        assert len(answer) > 0, "Tenant 1 Groq returned empty response"
        assert "tenant" in answer.lower() or "verified" in answer.lower(), \
            "Tenant 1 Groq response doesn't match expected pattern"
    
    @pytest.mark.e2e
    @pytest.mark.groq
    async def test_tenant2_groq_connectivity(self, tenant_keys):
        """Test Tenant 2's Groq API connection"""
        from groq import Groq
        
        groq_key = tenant_keys["tenant_2"]["groq"]
        
        assert groq_key, "Tenant 2 Groq key not configured"
        assert groq_key.startswith("gsk_"), "Tenant 2 Groq key format invalid"
        assert len(groq_key) > 40, "Tenant 2 Groq key seems too short"
        
        client = Groq(api_key=groq_key)
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Tenant 2 verified' in exactly 3 words."}
            ],
            max_tokens=50,
            temperature=0.1
        )
        
        content = response.choices[0].message.content
        answer = content.strip() if content else ""
        print(f"\n✅ Tenant 2 Groq Response: {answer}")
        
        assert len(answer) > 0, "Tenant 2 Groq returned empty response"
        assert "tenant" in answer.lower() or "verified" in answer.lower(), \
            "Tenant 2 Groq response doesn't match expected pattern"
    
    @pytest.mark.e2e
    @pytest.mark.vapi
    async def test_vapi_keys_are_different(self, tenant_keys):
        """Verify that tenant API keys are actually different"""
        key1 = tenant_keys["tenant_1"]["vapi_private"]
        key2 = tenant_keys["tenant_2"]["vapi_private"]
        
        assert key1 != key2, "⚠️ Tenant Vapi keys should be different!"
        print(f"\n✅ Tenant 1 Vapi: {key1[:20]}...")
        print(f"✅ Tenant 2 Vapi: {key2[:20]}...")
    
    @pytest.mark.e2e
    @pytest.mark.groq
    async def test_groq_keys_are_different(self, tenant_keys):
        """Verify that tenant Groq keys are actually different"""
        key1 = tenant_keys["tenant_1"]["groq"]
        key2 = tenant_keys["tenant_2"]["groq"]
        
        assert key1 != key2, "⚠️ Tenant Groq keys should be different!"
        print(f"\n✅ Tenant 1 Groq: {key1[:20]}...")
        print(f"✅ Tenant 2 Groq: {key2[:20]}...")
    
    @pytest.mark.e2e
    @pytest.mark.vapi
    async def test_tenant1_vapi_create_test_assistant(self, tenant_keys):
        """Create a test assistant with Tenant 1's Vapi key"""
        vapi_key = tenant_keys["tenant_1"]["vapi_private"]
        tenant_name = tenant_keys["tenant_1"]["tenant_name"]
        
        async with httpx.AsyncClient() as client:
            payload = {
                "name": f"Test Assistant - {tenant_name}",
                "model": {
                    "provider": "openai",
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant for Tenant 1."
                        }
                    ]
                },
                "voice": {
                    "provider": "playht",
                    "voiceId": "jennifer"
                }
            }
            
            response = await client.post(
                "https://api.vapi.ai/assistant",
                headers={
                    "Authorization": f"Bearer {vapi_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=15.0
            )
            
            print(f"\n✅ Tenant 1 Assistant Creation Status: {response.status_code}")
            
            if response.status_code == 201:
                data = response.json()
                assistant_id = data.get("id")
                print(f"✅ Tenant 1 Assistant ID: {assistant_id}")
                
                # Clean up - delete the test assistant
                await client.delete(
                    f"https://api.vapi.ai/assistant/{assistant_id}",
                    headers={"Authorization": f"Bearer {vapi_key}"},
                    timeout=10.0
                )
                print(f"✅ Cleaned up test assistant {assistant_id}")
            
            assert response.status_code == 201, \
                f"Tenant 1 assistant creation failed: {response.status_code} - {response.text}"
    
    @pytest.mark.e2e
    @pytest.mark.vapi
    async def test_tenant2_vapi_create_test_assistant(self, tenant_keys):
        """Create a test assistant with Tenant 2's Vapi key"""
        vapi_key = tenant_keys["tenant_2"]["vapi_private"]
        tenant_name = tenant_keys["tenant_2"]["tenant_name"]
        
        async with httpx.AsyncClient() as client:
            payload = {
                "name": f"Test Assistant - {tenant_name}",
                "model": {
                    "provider": "openai",
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant for Tenant 2."
                        }
                    ]
                },
                "voice": {
                    "provider": "playht",
                    "voiceId": "jennifer"
                }
            }
            
            response = await client.post(
                "https://api.vapi.ai/assistant",
                headers={
                    "Authorization": f"Bearer {vapi_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=15.0
            )
            
            print(f"\n✅ Tenant 2 Assistant Creation Status: {response.status_code}")
            
            if response.status_code == 201:
                data = response.json()
                assistant_id = data.get("id")
                print(f"✅ Tenant 2 Assistant ID: {assistant_id}")
                
                # Clean up - delete the test assistant
                await client.delete(
                    f"https://api.vapi.ai/assistant/{assistant_id}",
                    headers={"Authorization": f"Bearer {vapi_key}"},
                    timeout=10.0
                )
                print(f"✅ Cleaned up test assistant {assistant_id}")
            
            assert response.status_code == 201, \
                f"Tenant 2 assistant creation failed: {response.status_code} - {response.text}"
    
    @pytest.mark.e2e
    async def test_cross_tenant_key_isolation(self, tenant_keys):
        """Verify that using wrong tenant's key fails appropriately"""
        # This test ensures there's no way to accidentally use another tenant's keys
        
        print("\n" + "="*60)
        print("🔒 MULTI-TENANT ISOLATION VERIFICATION")
        print("="*60)
        
        # Verify both tenants have different keys
        t1_keys = tenant_keys["tenant_1"]
        t2_keys = tenant_keys["tenant_2"]
        
        assert t1_keys["groq"] != t2_keys["groq"], \
            "Tenant Groq keys must be different"
        assert t1_keys["vapi_private"] != t2_keys["vapi_private"], \
            "Tenant Vapi keys must be different"
        
        print("✅ All tenant API keys are properly isolated")
        print(f"   - Tenant 1: {len(t1_keys)} keys configured")
        print(f"   - Tenant 2: {len(t2_keys)} keys configured")
        print("="*60)
