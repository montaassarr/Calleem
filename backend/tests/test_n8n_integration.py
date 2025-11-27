import asyncio
import logging
import httpx
from services.n8n_service import n8n_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Override API URL for local testing (since we are running outside docker)
n8n_service.api_url = "http://localhost:5678/api/v1"

async def test_n8n_integration():
    """
    Test the n8n integration logic against a real running n8n instance.
    """
    print("\n🧪 Testing Real n8n Integration...")
    print(f"    Target: {n8n_service.api_url}")
    
    tenant_id = "test_tenant_real"
    automation_id = "google_calendar"
    workflow_name = f"tenant_{tenant_id}_{automation_id}"
    
    # 0. Cleanup (Delete if exists from previous run)
    print("\n[0] Pre-test Cleanup:")
    try:
        wf_id = None
        async with httpx.AsyncClient() as client:
            headers = {"X-N8N-API-KEY": n8n_service.api_key}
            response = await client.get(f"{n8n_service.api_url}/workflows", headers=headers)
            for w in response.json().get("data", []):
                if w["name"] == workflow_name:
                    wf_id = w["id"]
                    break
        
        if wf_id:
            async with httpx.AsyncClient() as client:
                await client.delete(f"{n8n_service.api_url}/workflows/{wf_id}", headers=headers)
            print(f"    ✅ Deleted stale workflow {wf_id}")
    except Exception as e:
        print(f"    ⚠️ Cleanup warning: {e}")
    
    # 1. Test Activation (Should create workflow)
    print("\n[1] Testing Automation Activation (Create & Activate):")
    try:
        success = await n8n_service.sync_automation_state(tenant_id, automation_id, True)
        if success:
            print("    ✅ Workflow creation/activation successful")
        else:
            print("    ❌ Workflow creation/activation failed")
            return
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return

    # Verify it exists via API
    async with httpx.AsyncClient() as client:
        headers = {"X-N8N-API-KEY": n8n_service.api_key}
        response = await client.get(f"{n8n_service.api_url}/workflows", headers=headers)
        workflows = response.json().get("data", [])
        found = any(w["name"] == workflow_name for w in workflows)
        if found:
            print(f"    ✅ Verified: Workflow '{workflow_name}' exists in n8n")
        else:
            print(f"    ❌ Failed: Workflow '{workflow_name}' not found in n8n")

    # 2. Test Deactivation
    print("\n[2] Testing Automation Deactivation:")
    try:
        success = await n8n_service.sync_automation_state(tenant_id, automation_id, False)
        if success:
            print("    ✅ Workflow deactivation successful")
        else:
            print("    ❌ Workflow deactivation failed")
    except Exception as e:
        print(f"    ❌ Error: {e}")

    # 3. Cleanup (Delete the test workflow)
    print("\n[3] Cleanup:")
    try:
        # Find ID
        wf_id = None
        async with httpx.AsyncClient() as client:
            headers = {"X-N8N-API-KEY": n8n_service.api_key}
            response = await client.get(f"{n8n_service.api_url}/workflows", headers=headers)
            for w in response.json().get("data", []):
                if w["name"] == workflow_name:
                    wf_id = w["id"]
                    break
        
        if wf_id:
            async with httpx.AsyncClient() as client:
                await client.delete(f"{n8n_service.api_url}/workflows/{wf_id}", headers=headers)
            print(f"    ✅ Deleted test workflow {wf_id}")
        else:
            print("    ⚠️ Could not find workflow to delete")
            
    except Exception as e:
        print(f"    ❌ Cleanup failed: {e}")

    print("\n🎉 Real n8n integration tests completed!")

if __name__ == "__main__":
    asyncio.run(test_n8n_integration())
