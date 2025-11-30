import asyncio
import logging
import httpx
from services.n8n_service import n8n_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Override API URL for local testing
n8n_service.api_url = "http://localhost:5678/api/v1"

async def test_workflow_deployment():
    """
    Test the full workflow deployment logic.
    """
    print("\n🧪 Testing Workflow Deployment...")
    
    tenant_id = "test_tenant_deploy"
    
    # Mock Config: Enable Google Calendar, Disable Airtable
    config = {
        "automations": {
            "google_calendar": True,
            "airtable": False
        }
    }
    
    print(f"\n[1] Deploying Workflow for {tenant_id}...")
    print(f"    Config: {config}")
    
    success = await n8n_service.deploy_workflow_template(tenant_id, config)
    
    if success:
        print("    ✅ Deployment successful")
        
        # Verify nodes in n8n
        workflow_name = f"tenant_{tenant_id}_core_workflow"
        async with httpx.AsyncClient() as client:
            headers = {"X-N8N-API-KEY": n8n_service.api_key}
            response = await client.get(f"{n8n_service.api_url}/workflows", headers=headers)
            workflows = response.json().get("data", [])
            
            target_wf = next((w for w in workflows if w["name"] == workflow_name), None)
            
            if target_wf:
                # Fetch full workflow details to check nodes
                wf_details = await client.get(f"{n8n_service.api_url}/workflows/{target_wf['id']}", headers=headers)
                nodes = wf_details.json().get("nodes", [])
                
                gcal_nodes = [n for n in nodes if "googleCalendar" in n["type"]]
                airtable_nodes = [n for n in nodes if "airtable" in n["type"]]
                
                print(f"    🔍 Verification:")
                
                # Check Google Calendar (Should be enabled)
                gcal_disabled = any(n.get("disabled", False) for n in gcal_nodes)
                if not gcal_disabled and gcal_nodes:
                    print("    ✅ Google Calendar nodes are ENABLED")
                elif not gcal_nodes:
                     print("    ⚠️ No Google Calendar nodes found")
                else:
                    print("    ❌ Google Calendar nodes are DISABLED (Expected Enabled)")
                    
                # Check Airtable (Should be disabled)
                airtable_disabled = all(n.get("disabled", False) for n in airtable_nodes)
                if airtable_disabled and airtable_nodes:
                    print("    ✅ Airtable nodes are DISABLED")
                elif not airtable_nodes:
                     print("    ⚠️ No Airtable nodes found")
                else:
                    print("    ❌ Airtable nodes are ENABLED (Expected Disabled)")
                    
            else:
                print("    ❌ Workflow not found in n8n")
    else:
        print("    ❌ Deployment failed")

if __name__ == "__main__":
    asyncio.run(test_workflow_deployment())
