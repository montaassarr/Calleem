import asyncio
import logging
import httpx
from fastapi.testclient import TestClient
from main import app
from routers.users import get_current_user

from services.n8n_service import n8n_service

# Update find_one to return the new config when called after update
async def find_one_side_effect(query):
    if query.get("tenant_id") == "test_tenant_dashboard":
        return {
            "business_name": "Test Dashboard Business",
            "automations": {"google_calendar": True, "airtable": True},
            "airtable_api_key": "encrypted_key",
            "tenant_id": "test_tenant_dashboard"
        }
    return None

# Assuming mock_db is defined elsewhere or will be defined.
# For now, this line will cause an error if mock_db is not present.
# As per instructions, inserting faithfully.
# mock_db.business_config.find_one.side_effect = find_one_side_effect

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Override API URL for local testing
n8n_service.api_url = "http://localhost:5678/api/v1"

# Mock Database
from unittest.mock import AsyncMock, MagicMock, patch
from database.mongo_config import get_database

mock_db = MagicMock()
mock_db.business_config = AsyncMock()
mock_db.business_config.update_one.return_value = AsyncMock(matched_count=1)
mock_db.tenants = AsyncMock()
mock_db.tenants.find_one.return_value = {"is_configured": True}

# Update find_one to return the new config when called after update
async def find_one_side_effect(query):
    if query.get("tenant_id") == "test_tenant_dashboard":
        return {
            "business_name": "Test Dashboard Business",
            "automations": {"google_calendar": True, "airtable": True},
            "airtable_api_key": "encrypted_key",
            "tenant_id": "test_tenant_dashboard"
        }
    return None

mock_db.business_config.find_one.side_effect = find_one_side_effect

# Patch get_database in admin router
patch_db = patch("routers.admin.get_database", return_value=mock_db)
patch_db.start()

# Mock User (as dict, since admin router expects dict from get_current_admin)
mock_user = {
    "_id": "test_user_dashboard",
    "username": "test_dashboard",
    "email": "dashboard@test.com",
    "role": "admin",
    "tenant_id": "test_tenant_dashboard",
    "business_id": "test_tenant_dashboard"
}

async def mock_get_current_user():
    return mock_user

# Override dependency
app.dependency_overrides[get_current_user] = mock_get_current_user

def test_dashboard_activation():
    print("\n🧪 Testing Dashboard Activation...")
    
    client = TestClient(app)
    
    # 1. Enable Automations via API
    print(f"\n[1] Enabling Automations for {mock_user['tenant_id']}...")
    payload = {
        "business_name": "Test Dashboard Business",
        "automations": {
            "google_calendar": True,
            "airtable": True
        },
        "airtable_api_key": "patDashboardTestKey"
    }
    
    response = client.put("/api/v1/admin/config", json=payload)
    
    if response.status_code == 200:
        print("    ✅ API Request Successful")
        config = response.json()
        print(f"    Config: {config}")
    else:
        print(f"    ❌ API Request Failed: {response.status_code} {response.text}")
        return

    # 2. Verify n8n Workflow
    workflow_name = f"tenant_{mock_user['tenant_id']}_core_workflow"
    print(f"\n[2] Verifying n8n Workflow {workflow_name}...")
    
    # We need to use async httpx here because TestClient is synchronous but n8n verification is async
    async def verify_n8n():
        async with httpx.AsyncClient() as n8n_client:
            headers = {"X-N8N-API-KEY": n8n_service.api_key}
            
            # Get Workflow
            resp = await n8n_client.get(f"{n8n_service.api_url}/workflows", headers=headers)
            workflows = resp.json().get("data", [])
            target_wf = next((w for w in workflows if w["name"] == workflow_name), None)
            
            if target_wf:
                print(f"    ✅ Workflow found: {target_wf['id']}")
                
                # Check Status
                if target_wf['active']:
                    print("    ✅ Workflow is ACTIVE")
                else:
                    print("    ❌ Workflow is INACTIVE (Expected Active)")
                    
                # Check Nodes
                wf_details = await n8n_client.get(f"{n8n_service.api_url}/workflows/{target_wf['id']}", headers=headers)
                nodes = wf_details.json().get("nodes", [])
                
                gcal_nodes = [n for n in nodes if "googleCalendar" in n["type"]]
                airtable_nodes = [n for n in nodes if "airtable" in n["type"]]
                
                # Verify Google Calendar Enabled
                if gcal_nodes and not any(n.get("disabled", False) for n in gcal_nodes):
                    print("    ✅ Google Calendar nodes ENABLED")
                else:
                    print("    ❌ Google Calendar nodes issue")
                    
                # Verify Airtable Enabled & Credential Injected
                if airtable_nodes and not any(n.get("disabled", False) for n in airtable_nodes):
                    print("    ✅ Airtable nodes ENABLED")
                    # Check credential injection
                    node = airtable_nodes[0]
                    if "airtableApi" in node.get("credentials", {}):
                         print("    ✅ Airtable Credential Injected")
                    else:
                         print("    ❌ Airtable Credential MISSING")
                else:
                    print("    ❌ Airtable nodes issue")
                    
            else:
                print("    ❌ Workflow not found")

    asyncio.run(verify_n8n())

if __name__ == "__main__":
    test_dashboard_activation()
