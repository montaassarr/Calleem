import logging
import httpx
from typing import Dict, Any, Optional, List
from utils.config import settings

logger = logging.getLogger(__name__)

class N8nService:
    """
    Service to handle interactions with the n8n API.
    Manages workflow activation/deactivation for tenants.
    """
    
    def __init__(self):
        self.api_url = settings.N8N_API_URL
        self.api_key = settings.N8N_API_KEY
        self.headers = {
            "X-N8N-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
    async def _get_workflow_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Fetch a workflow by its name."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_url}/workflows", headers=self.headers)
                response.raise_for_status()
                workflows = response.json().get("data", [])
                
                for wf in workflows:
                    if wf.get("name") == name:
                        return wf
            return None
        except Exception as e:
            logger.error(f"Failed to fetch workflows: {str(e)}")
            return None

    async def _create_workflow(self, name: str) -> Optional[Dict[str, Any]]:
        """Create a new empty workflow."""
        try:
            payload = {
                "name": name,
                "nodes": [
                    {
                        "parameters": {
                            "path": f"{name}-webhook",
                            "authentication": "none",
                            "httpMethod": "POST"
                        },
                        "name": "Webhook",
                        "type": "n8n-nodes-base.webhook",
                        "typeVersion": 1,
                        "position": [250, 300],
                        "webhookId": "wh-" + name[-10:]
                    }
                ],
                "connections": {},
                "settings": {},
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.api_url}/workflows", json=payload, headers=self.headers)
                if response.status_code >= 400:
                    logger.error(f"n8n API Error: {response.text}")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to create workflow {name}: {str(e)}")
            return None

    async def _update_workflow_status(self, workflow_id: str, active: bool) -> bool:
        """Activate or deactivate a workflow."""
        try:
            async with httpx.AsyncClient() as client:
                # Update active status
                payload = {"active": active}
                # Try activation endpoint first
                url = f"{self.api_url}/workflows/{workflow_id}/activate" if active else f"{self.api_url}/workflows/{workflow_id}/deactivate"
                response = await client.post(url, headers=self.headers)
                
                # If 404, try PUT /workflows/{id} (older versions)
                if response.status_code == 404:
                     response = await client.put(f"{self.api_url}/workflows/{workflow_id}", json=payload, headers=self.headers)
                
                if response.status_code >= 400:
                    logger.error(f"n8n API Error (Update Status): {response.text}")
                    
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Failed to update workflow status {workflow_id}: {str(e)}")
            return False

    async def deploy_workflow_template(self, tenant_id: str, config: Dict[str, Any], credential_ids: Dict[str, str] = None) -> bool:
        """
        Deploys the workflow template for a tenant, enabling/disabling nodes based on config.
        Injects credential IDs if provided.
        """
        import json
        import os
        
        template_path = os.path.join(os.path.dirname(__file__), "../templates/ai_receptionist_v2.json")
        try:
            with open(template_path, 'r') as f:
                workflow = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load template: {e}")
            return False

        workflow_name = f"tenant_{tenant_id}_core_workflow"
        
        # Construct strict payload
        payload = {
            "name": workflow_name,
            "nodes": workflow.get("nodes", []),
            "connections": workflow.get("connections", {}),
            "settings": workflow.get("settings", {})
        }
        
        # Inject Tenant ID Variable (if n8n supports workflow variables, or we replace in JSON)
        # n8n v1 API doesn't support setting variables easily in payload unless using "variables" key (newer n8n)
        # Or we can replace the placeholder in the JSON string before parsing.
        # But our migrate script used `={{ $vars.tenant_id }}`.
        # We need to ensure `tenant_id` is available in the workflow execution context.
        # Alternatively, we can hardcode the tenant_id in the HTTP node headers during deployment.
        
        for node in payload['nodes']:
            if node['type'] == 'n8n-nodes-base.httpRequest':
                # Check for header parameters
                header_params = node.get('parameters', {}).get('headerParameters', {}).get('parameters', [])
                for param in header_params:
                    if param['name'] == 'X-Tenant-ID':
                        param['value'] = tenant_id # Hardcode it for this tenant's workflow
                        
        # Toggle Nodes & Inject Credentials
        automations = config.get('automations', {})
        google_calendar_enabled = automations.get('google_calendar', False)
        airtable_enabled = automations.get('airtable', False)
        
        credential_ids = credential_ids or {}
        
        for node in payload['nodes']:
            node_type = node.get('type', '')
            
            # Google Calendar
            if 'googleCalendar' in node_type:
                # Toggle
                if not google_calendar_enabled:
                    node['disabled'] = True
                else:
                    node['disabled'] = False
                
                # Inject Credential
                if 'google_calendar' in credential_ids:
                    node['credentials'] = {
                        "googleCalendarOAuth2Api": {
                            "id": credential_ids['google_calendar']
                        }
                    }
                    
            # Airtable
            if 'airtable' in node_type:
                # Toggle
                if not airtable_enabled:
                    node['disabled'] = True
                else:
                    node['disabled'] = False
                    
                # Inject Credential
                if 'airtable' in credential_ids:
                    node['credentials'] = {
                        "airtableApi": {
                            "id": credential_ids['airtable']
                        }
                    }

        # Check if workflow exists to update or create
        existing_workflow = await self._get_workflow_by_name(workflow_name)
        
        try:
            async with httpx.AsyncClient() as client:
                if existing_workflow:
                    # Update existing
                    # For update, we might need to keep the ID in the URL but not in body? 
                    # Actually PUT usually takes the whole object.
                    # But let's try just updating the fields we care about.
                    # n8n API for PUT /workflows/:id expects the full workflow object.
                    
                    # We need to preserve the ID for the PUT request URL, but maybe not in the body?
                    # Let's try sending the payload as is (without ID) to the URL with ID.
                    response = await client.put(f"{self.api_url}/workflows/{existing_workflow['id']}", json=payload, headers=self.headers)
                else:
                    # Create new
                    response = await client.post(f"{self.api_url}/workflows", json=payload, headers=self.headers)
                
                if response.status_code >= 400:
                    logger.error(f"n8n API Error (Deploy): {response.text}")
                    return False
                
                response.raise_for_status()
                wf_data = response.json()
                
                # Activate
                # Note: If we just created it, it's inactive. If we updated it, we might want to keep it active?
                # The user wants "Auto-deploy...". We should probably activate it.
                return await self._update_workflow_status(wf_data['id'], True)
                
        except Exception as e:
            logger.error(f"Failed to deploy workflow {workflow_name}: {str(e)}")
            return False

    async def handle_config_update(self, tenant_id: str, old_config: Dict[str, Any], new_config: Dict[str, Any]):
        """
        Detects changes in automation config and triggers workflow deployment.
        Creates credentials if keys are present.
        """
        # Always try to sync if something relevant changed
        # Relevant fields: automations, airtable_api_key, google_calendar_connected
        
        should_deploy = False
        credential_ids = {}
        
        # Check Automations
        if old_config.get('automations') != new_config.get('automations'):
            should_deploy = True
            
        # Check Airtable Key
        airtable_key = new_config.get('airtable_api_key')
        if airtable_key:
            # Create/Update Credential
            # We do this even if key didn't change, to ensure it exists in n8n (idempotent-ish)
            # Or optimize: only if changed. But we need the ID for deployment.
            # So we should probably fetch/create it.
            cred_id = await self.create_airtable_credential(tenant_id, airtable_key)
            if cred_id:
                credential_ids['airtable'] = cred_id
                # If key changed, we definitely need to deploy to inject new ID (though ID might be same if we updated in place)
                # If we updated in place, ID is same, so workflow doesn't strictly need update, but good to be safe.
                if old_config.get('airtable_api_key') != airtable_key:
                    should_deploy = True
        
        # Check Google Calendar
        # For now we don't have tokens, so we skip credential creation
        # But if we did, we would do it here.
        
        if should_deploy or credential_ids:
            logger.info(f"🔄 Config/Creds changed for {tenant_id}, redeploying workflow...")
            await self.deploy_workflow_template(tenant_id, new_config, credential_ids)
            return
    async def create_airtable_credential(self, tenant_id: str, api_key: str) -> Optional[str]:
        """
        Creates or updates an Airtable credential for the tenant.
        Returns the credential ID.
        """
        name = f"tenant_{tenant_id}_airtable"
        data = {
            "name": name,
            "type": "airtableApi",
            "data": {
                "apiKey": api_key
            }
        }
        return await self._create_or_update_credential(name, data)

    async def create_google_credential(self, tenant_id: str, tokens: Dict[str, Any]) -> Optional[str]:
        """
        Creates or updates a Google Calendar OAuth2 credential.
        Returns the credential ID.
        """
        name = f"tenant_{tenant_id}_google_calendar"
        # Note: This schema is a best-guess. n8n OAuth2 credentials usually need:
        # clientId, clientSecret, accessToken, refreshToken, etc.
        # If we are using n8n's internal OAuth, we can't easily inject tokens.
        # But if we use "Generic OAuth2" or specific type with token injection:
        data = {
            "name": name,
            "type": "googleCalendarOAuth2Api",
            "data": {
                "clientId": tokens.get("client_id", ""),
                "clientSecret": tokens.get("client_secret", ""),
                "accessToken": tokens.get("access_token", ""),
                "refreshToken": tokens.get("refresh_token", ""),
                "scope": "https://www.googleapis.com/auth/calendar",
                "authUrl": "https://accounts.google.com/o/oauth2/v2/auth",
                "accessTokenUrl": "https://oauth2.googleapis.com/token",
            }
        }
        return await self._create_or_update_credential(name, data)

    async def _create_or_update_credential(self, name: str, payload: Dict[str, Any]) -> Optional[str]:
        """
        Helper to create or update a credential in n8n.
        """
        try:
            async with httpx.AsyncClient() as client:
                # Check if exists (we can't list easily with 405, so we might have to try create and fail?)
                # Actually, let's try to just CREATE. If it fails with "already exists", we might need to find its ID.
                # But since we can't list, we might have to store the ID in our DB.
                # For now, let's assume we just create a NEW one with a unique name every time? 
                # No, that spams n8n.
                
                # Let's try to GET by ID if we stored it? We don't have it yet.
                # Let's try to create.
                response = await client.post(f"{self.api_url}/credentials", json=payload, headers=self.headers)
                
                if response.status_code == 200:
                    return response.json()['id']
                
                logger.error(f"Failed to create credential {name}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error managing credential {name}: {e}")
            return None

n8n_service = N8nService()
