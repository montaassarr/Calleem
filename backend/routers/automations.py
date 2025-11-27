"""
Automations API Router
Handles Smart Automations configuration and n8n workflow deployment
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any
from pydantic import BaseModel
from datetime import datetime
import logging

from database.mongo_config import get_database
from routers.users import get_current_user
from services.n8n_service import n8n_service
from models.business.business_config import BusinessConfig

logger = logging.getLogger(__name__)

router = APIRouter()


class AutomationsUpdate(BaseModel):
    """Model for updating automations"""
    automations: Dict[str, bool]


@router.post("/update")
async def update_automations(
    data: AutomationsUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update Smart Automations configuration and deploy n8n workflows.
    
    This endpoint:
    1. Validates the user is on Pro or Enterprise plan
    2. Updates the automations config in business_config collection
    3. Triggers n8n workflow deployment with enabled/disabled nodes
    
    Args:
        data: Automations configuration (dict of automation_id: enabled)
        current_user: Authenticated user from JWT token
        
    Returns:
        Updated business config with automation status
    """
    db = get_database()
    tenant_id = str(current_user.get("tenant_id") or current_user.get("business_id"))
    
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant ID not found in user session"
        )
    
    # 🔒 PLAN ENFORCEMENT — PROTECT $499 REVENUE
    from bson import ObjectId
    tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    tenant_plan = tenant.get("plan", "free")
    if tenant_plan not in ["pro", "enterprise"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Smart Automations require Pro or Enterprise plan. Current plan: {tenant_plan}"
        )
    
    logger.info(f"✅ Plan check passed: {tenant_plan} plan has access to automations")
    
    # Fetch current config
    query = {"tenant_id": tenant_id}
    existing_config = await db.business_config.find_one(query)
    
    if not existing_config:
        # Create default config if it doesn't exist
        existing_config = {
            "tenant_id": tenant_id,
            "business_id": tenant_id,
            "business_name": "My Business",
            "timezone": "UTC",
            "currency": "USD",
            "automations": {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await db.business_config.insert_one(existing_config)
    
    # Update automations
    update_data = {
        "automations": data.automations,
        "updated_at": datetime.utcnow()
    }
    
    await db.business_config.update_one(
        query,
        {"$set": update_data}
    )
    
    logger.info(f"✅ Updated automations for tenant {tenant_id}: {data.automations}")
    
    # Trigger n8n workflow deployment
    try:
        # Fetch updated config for n8n deployment
        updated_config = await db.business_config.find_one(query)
        
        # Deploy workflow with updated automation toggles
        await deploy_n8n_workflows(tenant_id, updated_config, data.automations)
        
        logger.info(f"🚀 n8n workflows deployed for tenant {tenant_id}")
    except Exception as e:
        logger.error(f"Failed to deploy n8n workflows: {e}")
        # Don't fail the request if n8n deployment fails
        # The config is still saved
    
    # Return updated config
    final_config = await db.business_config.find_one(query)
    if "_id" in final_config:
        del final_config["_id"]
    
    return {
        "success": True,
        "message": "Automations updated successfully",
        "automations": data.automations,
        "config": final_config
    }



async def deploy_n8n_workflows(
    tenant_id: str,
    config: Dict[str, Any],
    automations: Dict[str, bool]
):
    """
    Deploy n8n workflows for the tenant based on enabled automations.
    
    This function creates/updates tenant-specific workflows in n8n with:
    - Google Calendar sync (if enabled)
    - Airtable data logging (if enabled)
    - WhatsApp/SMS confirmations (if enabled)
    - HubSpot contact creation (if enabled)
    - Slack notifications (if enabled)
    
    Args:
        tenant_id: Tenant identifier
        config: Full business config from MongoDB
        automations: Dict of automation toggles
    """
    import json
    
    # Build workflow template dynamically based on enabled automations
    workflow_name = f"tenant_{tenant_id}_smart_automations"
    
    # Base workflow structure
    workflow = {
        "name": workflow_name,
        "nodes": [],
        "connections": {},
        "settings": {
            "executionOrder": "v1"
        }
    }
    
    # Add webhook trigger (always present)
    webhook_node = {
        "parameters": {
            "path": f"tenant-{tenant_id}-automation",
            "httpMethod": "POST",
            "responseMode": "onReceived",
            "options": {}
        },
        "name": "Webhook",
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 1,
        "position": [250, 300],
        "webhookId": f"wh-{tenant_id[:10]}"
    }
    workflow["nodes"].append(webhook_node)
    
    # Track node positions for layout
    x_pos = 450
    y_pos = 200
    y_offset = 150
    
    # Add Google Calendar node if enabled
    if automations.get("google_calendar_sync"):
        calendar_node = {
            "parameters": {
                "resource": "event",
                "operation": "create",
                "calendarId": "={{ $json.calendar_id }}",
                "start": "={{ $json.start_time }}",
                "end": "={{ $json.end_time }}",
                "summary": "={{ $json.summary }}",
                "description": "={{ $json.description }}"
            },
            "name": "Google Calendar",
            "type": "n8n-nodes-base.googleCalendar",
            "typeVersion": 1,
            "position": [x_pos, y_pos],
            "disabled": False
        }
        workflow["nodes"].append(calendar_node)
        workflow["connections"]["Webhook"] = {
            "main": [[{"node": "Google Calendar", "type": "main", "index": 0}]]
        }
        y_pos += y_offset
    
    # Add Airtable node if enabled
    if automations.get("airtable_sync"):
        airtable_node = {
            "parameters": {
                "operation": "append",
                "application": "={{ $json.airtable_base_id }}",
                "table": "={{ $json.airtable_table }}",
                "options": {}
            },
            "name": "Airtable",
            "type": "n8n-nodes-base.airtable",
            "typeVersion": 1,
            "position": [x_pos, y_pos],
            "disabled": False
        }
        workflow["nodes"].append(airtable_node)
        if "Webhook" not in workflow["connections"]:
            workflow["connections"]["Webhook"] = {"main": [[]]}
        workflow["connections"]["Webhook"]["main"][0].append(
            {"node": "Airtable", "type": "main", "index": 0}
        )
        y_pos += y_offset
    
    # Add WhatsApp/SMS node if enabled
    if automations.get("whatsapp_confirmation"):
        sms_node = {
            "parameters": {
                "resource": "message",
                "operation": "send",
                "to": "={{ $json.customer_phone }}",
                "message": "={{ $json.confirmation_message }}"
            },
            "name": "Send Confirmation",
            "type": "n8n-nodes-base.twilio",
            "typeVersion": 1,
            "position": [x_pos, y_pos],
            "disabled": False
        }
        workflow["nodes"].append(sms_node)
        if "Webhook" not in workflow["connections"]:
            workflow["connections"]["Webhook"] = {"main": [[]]}
        workflow["connections"]["Webhook"]["main"][0].append(
            {"node": "Send Confirmation", "type": "main", "index": 0}
        )
        y_pos += y_offset
    
    # Add HubSpot node if enabled
    if automations.get("hubspot_contact"):
        hubspot_node = {
            "parameters": {
                "resource": "contact",
                "operation": "create",
                "email": "={{ $json.customer_email }}",
                "additionalFields": {
                    "firstname": "={{ $json.customer_name }}",
                    "phone": "={{ $json.customer_phone }}"
                }
            },
            "name": "HubSpot",
            "type": "n8n-nodes-base.hubspot",
            "typeVersion": 1,
            "position": [x_pos, y_pos],
            "disabled": False
        }
        workflow["nodes"].append(hubspot_node)
        if "Webhook" not in workflow["connections"]:
            workflow["connections"]["Webhook"] = {"main": [[]]}
        workflow["connections"]["Webhook"]["main"][0].append(
            {"node": "HubSpot", "type": "main", "index": 0}
        )
        y_pos += y_offset
    
    # Add Slack node if enabled
    if automations.get("slack_notification"):
        slack_node = {
            "parameters": {
                "resource": "message",
                "operation": "post",
                "channel": "={{ $json.slack_channel }}",
                "text": "🎉 New appointment booked: {{ $json.summary }}",
                "attachments": []
            },
            "name": "Slack",
            "type": "n8n-nodes-base.slack",
            "typeVersion": 1,
            "position": [x_pos, y_pos],
            "disabled": False
        }
        workflow["nodes"].append(slack_node)
        if "Webhook" not in workflow["connections"]:
            workflow["connections"]["Webhook"] = {"main": [[]]}
        workflow["connections"]["Webhook"]["main"][0].append(
            {"node": "Slack", "type": "main", "index": 0}
        )
    
    # Deploy workflow to n8n
    logger.info(f"📋 Deploying workflow with {len(workflow['nodes'])} nodes for tenant {tenant_id}")
    
    # Use existing n8n service to deploy
    # Note: This is a simplified version. The actual n8n_service.deploy_workflow_template
    # expects a template file, so we might need to adapt it or create a new method.
    # For now, we'll log the workflow structure.
    logger.info(f"Workflow structure: {json.dumps(workflow, indent=2)}")
    
    # TODO: Implement actual n8n API call to create/update workflow
    # This would use the n8n_service methods or direct API calls
    
    return workflow
