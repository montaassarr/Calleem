"""
Agents API Router
CRUD operations for voice agents (Vapi specific)
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import logging

from models.agent import (
    AgentCreate,
    AgentUpdate,
    AgentResponse,
    AgentStatus
)
from database.mongo_config import get_database
from routers.users import get_current_user
from utils.error_logger import error_logger, ErrorCategory, ErrorLevel

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/my-agent", response_model=AgentResponse)
async def get_or_create_my_agent(
    current_user: dict = Depends(get_current_user)
):
    """
    Get the single agent for the current tenant.
    Creates a default agent if none exists.
    Each tenant can only have ONE agent.
    """
    db = get_database()
    tenant_id = current_user.get("tenant_id")
    
    if not tenant_id:
        raise HTTPException(status_code=400, detail="User has no tenant_id")
    
    # Try to find existing agent
    agent = await db.agents.find_one({"tenant_id": tenant_id})
    
    if agent:
        # Return existing agent
        agent["id"] = str(agent.pop("_id"))
        return AgentResponse(**agent)
    
    # Create default agent if none exists
    try:
        default_agent = {
            "name": "My AI Receptionist",
            "tenant_id": tenant_id,
            "system_prompt": """You are a friendly and professional AI receptionist. Help customers book appointments, answer questions about services, and provide information about the business.

APPOINTMENT BOOKING:
- Check availability before booking
- Collect: customer name, phone, email, service, date, and time
- Confirm all details before finalizing

TEST & DEMO CAPABILITIES:
- Weather lookup (get_weather) - Check weather for any location
- Discount calculator (calculate_discount) - Calculate prices with discounts
- Reminder setter (set_reminder) - Set future reminders
- Business status checker (check_business_status) - Check if business is open/closed

When testing, feel free to demonstrate these capabilities to show the agent's function calling abilities.""",
            "voice_settings": {
                "provider": "vapi",
                "voice_id": "jennifer",
                "stability": 0.5,
                "similarity_boost": 0.75
            },
            "llm_model": "llama-3.3-70b-versatile",
            "llm_temperature": 0.7,
            "greeting_enabled": True,
            "greeting_message": "Hello! I'm your AI receptionist. How can I help you today?",
            "webhook_urls": {
                "get_slots": "http://localhost:5678/webhook/getslots",
                "book": "http://localhost:5678/webhook/bookslots",
                "update": "http://localhost:5678/webhook/updateslots",
                "cancel": "http://localhost:5678/webhook/cancelslots"
            },
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "total_calls": 0,
            "total_minutes": 0.0,
            "successful_calls": 0,
            "last_deployed_at": None
        }
        
        result = await db.agents.insert_one(default_agent)
        default_agent["_id"] = result.inserted_id
        default_agent["id"] = str(default_agent.pop("_id"))
        
        logger.info(f"Created default agent for tenant {tenant_id}")
        return AgentResponse(**default_agent)
        
    except Exception as e:
        logger.error(f"Failed to create default agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create agent: {str(e)}")


# Removed: list_agents - Each tenant has only ONE agent


# Removed: get_agent by ID - Use /my-agent instead


@router.put("/my-agent", response_model=AgentResponse)
async def update_my_agent(
    agent_update: AgentUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update the tenant's agent configuration"""
    db = get_database()
    tenant_id = current_user.get("tenant_id")
    
    if not tenant_id:
        raise HTTPException(status_code=400, detail="User has no tenant_id")
    
    # Check agent exists
    existing_agent = await db.agents.find_one({"tenant_id": tenant_id})
    if not existing_agent:
        raise HTTPException(status_code=404, detail="Agent not found. Please create one first.")
    
    # Prepare update
    update_dict = agent_update.model_dump(exclude_unset=True)
    update_dict["updated_at"] = datetime.utcnow()
    
    # Update in database
    await db.agents.update_one(
        {"tenant_id": tenant_id},
        {"$set": update_dict}
    )
    
    # Get updated agent
    updated_agent = await db.agents.find_one({"tenant_id": tenant_id})
    updated_agent["id"] = str(updated_agent.pop("_id"))
    
    logger.info(f"Updated agent for tenant {tenant_id}")
    
    return AgentResponse(**updated_agent)


# Removed: delete_agent, deploy_agent, pause_agent, activate_agent
# Each tenant has ONE agent that is always active
# Configuration changes take effect immediately
