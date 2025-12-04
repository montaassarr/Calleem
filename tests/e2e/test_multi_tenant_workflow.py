"""
Phase 3: Multi-Tenant E2E Workflow Test
Tests complete isolation between multiple tenants
"""

import pytest
import httpx
import asyncio
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"


class TestMultiTenantWorkflow:
    """Test multi-tenant isolation in complete workflows"""
    
    @pytest.mark.asyncio
    async def test_two_tenants_complete_isolation(self):
        """
        Test that two tenants can:
        1. Register independently
        2. Add same API keys
        3. Create agents
        4. Access only their own data
        """
        
        timestamp = int(datetime.now().timestamp())
        
        print(f"\n{'='*70}")
        print(f"🏢 Multi-Tenant Isolation E2E Test")
        print(f"{'='*70}")
        
        # Tenant A: Coffee Shop
        tenant_a = {
            "email": f"coffee_shop_{timestamp}@test.com",
            "username": f"coffee_shop_{timestamp}",
            "password": "CoffeePass123!@#",
            "full_name": "Coffee Shop Owner",
            "business_name": "Downtown Coffee Shop"
        }
        
        # Tenant B: Dental Clinic
        tenant_b = {
            "email": f"dental_clinic_{timestamp}@test.com",
            "username": f"dental_clinic_{timestamp}",
            "password": "DentalPass456!@#",
            "full_name": "Dental Clinic Owner",
            "business_name": "Smile Dental Clinic"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            
            # ============================================================
            # PHASE 1: Register Both Tenants
            # ============================================================
            print(f"\n📝 Phase 1: Register Both Tenants")
            
            # Register Tenant A
            response = await client.post(f"{BASE_URL}/users/register", json=tenant_a)
            assert response.status_code == 201
            tenant_a_data = response.json()
            tenant_a["token"] = tenant_a_data["access_token"]
            tenant_a["tenant_id"] = tenant_a_data["user"]["tenant_id"]
            tenant_a["headers"] = {"Authorization": f"Bearer {tenant_a['token']}"}
            
            print(f"   ✅ Tenant A registered: {tenant_a['business_name']}")
            print(f"      Tenant ID: {tenant_a['tenant_id']}")
            
            # Register Tenant B
            response = await client.post(f"{BASE_URL}/users/register", json=tenant_b)
            assert response.status_code == 201
            tenant_b_data = response.json()
            tenant_b["token"] = tenant_b_data["access_token"]
            tenant_b["tenant_id"] = tenant_b_data["user"]["tenant_id"]
            tenant_b["headers"] = {"Authorization": f"Bearer {tenant_b['token']}"}
            
            print(f"   ✅ Tenant B registered: {tenant_b['business_name']}")
            print(f"      Tenant ID: {tenant_b['tenant_id']}")
            
            # Verify different tenant IDs
            assert tenant_a["tenant_id"] != tenant_b["tenant_id"]
            print(f"\n   ✅ Tenants have different IDs (isolation confirmed)")
            
            # ============================================================
            # PHASE 2: Both Add Same API Keys
            # ============================================================
            print(f"\n🔑 Phase 2: Both Tenants Add Same API Keys")
            
            import os
            shared_keys = {
                "vapi": os.getenv("TEST_VAPI_KEY", "957f3d01-6229-4834-bfff-667ccf49ff50"),
                "elevenlabs": os.getenv("TEST_ELEVENLABS_KEY", "sk_a6ba2e5af83bbfd611069dba90d7b07af81ae5c1397b2a10"),
                "groq": os.getenv("TEST_GROQ_KEY", "REDACTED_GROQ_KEY")
            }
            
            # Tenant A adds keys
            print(f"\n   Adding keys for Tenant A...")
            for provider, api_key in shared_keys.items():
                response = await client.post(
                    f"{BASE_URL}/keys",
                    json={
                        "provider": provider,
                        "api_key": api_key,
                        "name": f"Tenant A - {provider}"
                    },
                    headers=tenant_a["headers"]
                )
                assert response.status_code == 201
                print(f"      ✅ Added {provider} key")
            
            # Tenant B adds same keys
            print(f"\n   Adding keys for Tenant B...")
            for provider, api_key in shared_keys.items():
                response = await client.post(
                    f"{BASE_URL}/keys",
                    json={
                        "provider": provider,
                        "api_key": api_key,
                        "name": f"Tenant B - {provider}"
                    },
                    headers=tenant_b["headers"]
                )
                assert response.status_code == 201
                print(f"      ✅ Added {provider} key")
            
            # ============================================================
            # PHASE 3: Verify Key Isolation
            # ============================================================
            print(f"\n🔐 Phase 3: Verify Key Isolation")
            
            # Tenant A lists their keys
            response = await client.get(f"{BASE_URL}/keys", headers=tenant_a["headers"])
            assert response.status_code == 200
            tenant_a_keys = response.json()
            
            # Tenant B lists their keys
            response = await client.get(f"{BASE_URL}/keys", headers=tenant_b["headers"])
            assert response.status_code == 200
            tenant_b_keys = response.json()
            
            # Both should have 3 keys
            assert len(tenant_a_keys) == 3
            assert len(tenant_b_keys) == 3
            
            # Keys should have different IDs
            tenant_a_key_ids = {key["id"] for key in tenant_a_keys}
            tenant_b_key_ids = {key["id"] for key in tenant_b_keys}
            
            # No overlap in key IDs
            assert len(tenant_a_key_ids.intersection(tenant_b_key_ids)) == 0
            
            print(f"   ✅ Tenant A has {len(tenant_a_keys)} keys (IDs: unique)")
            print(f"   ✅ Tenant B has {len(tenant_b_keys)} keys (IDs: unique)")
            print(f"   ✅ Zero overlap in key IDs - isolation confirmed")
            
            # ============================================================
            # PHASE 4: Create Agents for Both Tenants
            # ============================================================
            print(f"\n🤖 Phase 4: Create Agents")
            
            # Tenant A creates agent
            agent_a_data = {
                "tenant_id": tenant_a["tenant_id"],
                "name": "Coffee Shop Assistant",
                "description": "Helps customers order coffee",
                "llm_model": "gpt-3.5-turbo",
                "llm_temperature": 0.7,
                "system_prompt": "You are a friendly coffee shop assistant.",
                "status": "draft",
                "voice_settings": {
                    "provider": "elevenlabs",
                    "voice_id": "21m00Tcm4TlvDq8ikWAM",
                    "stability": 0.5,
                    "similarity_boost": 0.5
                },
                "webhook_urls": {
                    "book_appointment": "https://n8n.coffee/webhook/book",
                    "cancel_appointment": "https://n8n.coffee/webhook/cancel",
                    "get_available_slots": "https://n8n.coffee/webhook/slots"
                }
            }
            
            response = await client.post(
                f"{BASE_URL}/agents",
                json=agent_a_data,
                headers=tenant_a["headers"]
            )
            assert response.status_code == 201
            agent_a = response.json()
            tenant_a["agent_id"] = agent_a["_id"]
            
            print(f"   ✅ Tenant A created agent: {agent_a['name']}")
            print(f"      Agent ID: {agent_a['_id']}")
            
            # Tenant B creates agent
            agent_b_data = {
                "tenant_id": tenant_b["tenant_id"],
                "name": "Dental Receptionist",
                "description": "Books dental appointments",
                "llm_model": "gpt-3.5-turbo",
                "llm_temperature": 0.7,
                "system_prompt": "You are a professional dental receptionist.",
                "status": "draft",
                "voice_settings": {
                    "provider": "elevenlabs",
                    "voice_id": "21m00Tcm4TlvDq8ikWAM",
                    "stability": 0.5,
                    "similarity_boost": 0.5
                },
                "webhook_urls": {
                    "book_appointment": "https://n8n.dental/webhook/book",
                    "cancel_appointment": "https://n8n.dental/webhook/cancel",
                    "get_available_slots": "https://n8n.dental/webhook/slots"
                }
            }
            
            response = await client.post(
                f"{BASE_URL}/agents",
                json=agent_b_data,
                headers=tenant_b["headers"]
            )
            assert response.status_code == 201
            agent_b = response.json()
            tenant_b["agent_id"] = agent_b["_id"]
            
            print(f"   ✅ Tenant B created agent: {agent_b['name']}")
            print(f"      Agent ID: {agent_b['_id']}")
            
            # ============================================================
            # PHASE 5: Verify Agent Isolation
            # ============================================================
            print(f"\n🔒 Phase 5: Verify Agent Isolation")
            
            # Tenant A lists agents
            response = await client.get(f"{BASE_URL}/agents", headers=tenant_a["headers"])
            assert response.status_code == 200
            tenant_a_agents = response.json()
            
            # Tenant B lists agents
            response = await client.get(f"{BASE_URL}/agents", headers=tenant_b["headers"])
            assert response.status_code == 200
            tenant_b_agents = response.json()
            
            # Each should only see their own agent
            assert len(tenant_a_agents) >= 1
            assert len(tenant_b_agents) >= 1
            
            # Verify Tenant A only sees their agent
            tenant_a_agent_ids = {agent["_id"] for agent in tenant_a_agents}
            assert tenant_a["agent_id"] in tenant_a_agent_ids
            assert tenant_b["agent_id"] not in tenant_a_agent_ids
            
            # Verify Tenant B only sees their agent
            tenant_b_agent_ids = {agent["_id"] for agent in tenant_b_agents}
            assert tenant_b["agent_id"] in tenant_b_agent_ids
            assert tenant_a["agent_id"] not in tenant_b_agent_ids
            
            print(f"   ✅ Tenant A sees only their agents")
            print(f"   ✅ Tenant B sees only their agents")
            print(f"   ✅ No cross-tenant agent visibility")
            
            # ============================================================
            # PHASE 6: Test Cross-Tenant Access Prevention
            # ============================================================
            print(f"\n🚫 Phase 6: Test Cross-Tenant Access Prevention")
            
            # Tenant A tries to access Tenant B's agent
            response = await client.get(
                f"{BASE_URL}/agents/{tenant_b['agent_id']}",
                headers=tenant_a["headers"]
            )
            assert response.status_code in [403, 404]
            print(f"   ✅ Tenant A blocked from accessing Tenant B's agent")
            
            # Tenant B tries to access Tenant A's agent
            response = await client.get(
                f"{BASE_URL}/agents/{tenant_a['agent_id']}",
                headers=tenant_b["headers"]
            )
            assert response.status_code in [403, 404]
            print(f"   ✅ Tenant B blocked from accessing Tenant A's agent")
            
            # Tenant A tries to access Tenant B's keys
            if tenant_b_keys:
                tenant_b_key_id = tenant_b_keys[0]["id"]
                response = await client.delete(
                    f"{BASE_URL}/keys/{tenant_b_key_id}",
                    headers=tenant_a["headers"]
                )
                assert response.status_code in [403, 404]
                print(f"   ✅ Tenant A blocked from deleting Tenant B's key")
            
            # ============================================================
            # FINAL SUMMARY
            # ============================================================
            print(f"\n{'='*70}")
            print(f"✅ MULTI-TENANT ISOLATION VERIFIED")
            print(f"{'='*70}")
            print(f"\nTest Results:")
            print(f"  ✅ Both tenants registered independently")
            print(f"  ✅ Both tenants added same API keys (different records)")
            print(f"  ✅ API keys isolated per tenant")
            print(f"  ✅ Both tenants created agents")
            print(f"  ✅ Agents isolated per tenant")
            print(f"  ✅ Cross-tenant access blocked")
            print(f"  ✅ No data leakage between tenants")
            print(f"\n🎊 Multi-tenant architecture working perfectly!")
            print(f"{'='*70}\n")


if __name__ == "__main__":
    # Run the test
    asyncio.run(TestMultiTenantWorkflow().test_two_tenants_complete_isolation())
