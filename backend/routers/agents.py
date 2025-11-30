"""
Agents API Router
CRUD operations for voice agents with VAPI integration
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import logging

from models.agent import (
    Agent,
    AgentCreate,
    AgentUpdate,
    AgentResponse,
    AgentStatus
)
from database.mongo_config import get_database
from routers.users import get_current_user
from services.vapi_service import create_vapi_assistant, update_vapi_assistant, delete_vapi_assistant

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new voice agent"""
    db = get_database()
    
    # Get tenant_id from current user
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="User has no tenant_id")
    
    # Ensure agent belongs to current tenant
    if agent_data.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Cannot create agent for another tenant")
    
    # Create agent document
    agent_dict = agent_data.model_dump()
    agent_dict["created_at"] = datetime.utcnow()
    agent_dict["updated_at"] = datetime.utcnow()
    agent_dict["total_calls"] = 0
    agent_dict["total_minutes"] = 0.0
    agent_dict["successful_calls"] = 0
    agent_dict["vapi_assistant_id"] = None
    agent_dict["vapi_phone_number_id"] = None
    agent_dict["last_deployed_at"] = None
    
    # Insert into database
    result = await db.agents.insert_one(agent_dict)
    
    # Get created agent
    created_agent = await db.agents.find_one({"_id": result.inserted_id})
    created_agent["_id"] = str(created_agent["_id"])
    
    logger.info(f"Created agent {created_agent['_id']} for tenant {tenant_id}")
    
    return AgentResponse(**created_agent)


@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    status_filter: Optional[AgentStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: dict = Depends(get_current_user)
):
    """List all agents for current tenant"""
    db = get_database()
    
    # Get tenant_id from current user
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="User has no tenant_id")
    
    # Build query
    query = {"tenant_id": tenant_id}
    if status_filter:
        query["status"] = status_filter.value
    
    # Fetch agents
    cursor = db.agents.find(query).skip(skip).limit(limit).sort("created_at", -1)
    agents = await cursor.to_list(length=limit)
    
    # Convert ObjectId to string
    for agent in agents:
        agent["_id"] = str(agent["_id"])
    
    return [AgentResponse(**agent) for agent in agents]


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get agent by ID"""
    if not ObjectId.is_valid(agent_id):
        raise HTTPException(status_code=400, detail="Invalid agent ID")
    
    db = get_database()
    tenant_id = current_user.get("tenant_id")
    
    # Fetch agent
    agent = await db.agents.find_one({"_id": ObjectId(agent_id), "tenant_id": tenant_id})
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent["_id"] = str(agent["_id"])
    return AgentResponse(**agent)


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_update: AgentUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an agent"""
    if not ObjectId.is_valid(agent_id):
        raise HTTPException(status_code=400, detail="Invalid agent ID")
    
    db = get_database()
    tenant_id = current_user.get("tenant_id")
    
    # Check agent exists and belongs to tenant
    existing_agent = await db.agents.find_one({"_id": ObjectId(agent_id), "tenant_id": tenant_id})
    if not existing_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Prepare update
    update_dict = agent_update.model_dump(exclude_unset=True)
    update_dict["updated_at"] = datetime.utcnow()
    
    # Update in database
    await db.agents.update_one(
        {"_id": ObjectId(agent_id)},
        {"$set": update_dict}
    )
    
    # Get updated agent
    updated_agent = await db.agents.find_one({"_id": ObjectId(agent_id)})
    updated_agent["_id"] = str(updated_agent["_id"])
    
    logger.info(f"Updated agent {agent_id}")
    
    return AgentResponse(**updated_agent)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete an agent"""
    if not ObjectId.is_valid(agent_id):
        raise HTTPException(status_code=400, detail="Invalid agent ID")
    
    db = get_database()
    tenant_id = current_user.get("tenant_id")
    
    # Check agent exists and belongs to tenant
    agent = await db.agents.find_one({"_id": ObjectId(agent_id), "tenant_id": tenant_id})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Delete VAPI assistant if exists
    if agent.get("vapi_assistant_id"):
        try:
            await delete_vapi_assistant(agent["vapi_assistant_id"], tenant_id)
        except Exception as e:
            logger.warning(f"Failed to delete VAPI assistant: {e}")
    
    # Delete from database
    await db.agents.delete_one({"_id": ObjectId(agent_id)})
    
    logger.info(f"Deleted agent {agent_id}")
    
    return None


@router.post("/{agent_id}/deploy", response_model=AgentResponse)
async def deploy_agent(
    agent_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Deploy agent to VAPI (create or update assistant)"""
    if not ObjectId.is_valid(agent_id):
        raise HTTPException(status_code=400, detail="Invalid agent ID")
    
    db = get_database()
    tenant_id = current_user.get("tenant_id")
    
    # Get agent
    agent_doc = await db.agents.find_one({"_id": ObjectId(agent_id), "tenant_id": tenant_id})
    if not agent_doc:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Convert to Agent model
    agent_doc["_id"] = str(agent_doc["_id"])
    agent = Agent(**agent_doc)
    
    try:
        # Create or update VAPI assistant
        if agent.vapi_assistant_id:
            # Update existing assistant
            await update_vapi_assistant(agent.vapi_assistant_id, agent, tenant_id)
            logger.info(f"Updated VAPI assistant for agent {agent_id}")
        else:
            # Create new assistant
            assistant_id = await create_vapi_assistant(agent, tenant_id)
            
            # Update agent with assistant ID
            await db.agents.update_one(
                {"_id": ObjectId(agent_id)},
                {
                    "$set": {
                        "vapi_assistant_id": assistant_id,
                        "last_deployed_at": datetime.utcnow(),
                        "status": AgentStatus.ACTIVE.value
                    }
                }
            )
            
            logger.info(f"Created VAPI assistant {assistant_id} for agent {agent_id}")
        
        # Get updated agent
        updated_agent = await db.agents.find_one({"_id": ObjectId(agent_id)})
        updated_agent["_id"] = str(updated_agent["_id"])
        
        return AgentResponse(**updated_agent)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to deploy agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to deploy agent: {str(e)}")


@router.post("/{agent_id}/pause", response_model=AgentResponse)
async def pause_agent(
    agent_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Pause an active agent"""
    if not ObjectId.is_valid(agent_id):
        raise HTTPException(status_code=400, detail="Invalid agent ID")
    
    db = get_database()
    tenant_id = current_user.get("tenant_id")
    
    # Update status
    result = await db.agents.update_one(
        {"_id": ObjectId(agent_id), "tenant_id": tenant_id},
        {"$set": {"status": AgentStatus.PAUSED.value, "updated_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Get updated agent
    agent = await db.agents.find_one({"_id": ObjectId(agent_id)})
    agent["_id"] = str(agent["_id"])
    
    return AgentResponse(**agent)


@router.post("/{agent_id}/activate", response_model=AgentResponse)
async def activate_agent(
    agent_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Activate a paused agent"""
    if not ObjectId.is_valid(agent_id):
        raise HTTPException(status_code=400, detail="Invalid agent ID")
    
    db = get_database()
    tenant_id = current_user.get("tenant_id")
    
    # Update status
    result = await db.agents.update_one(
        {"_id": ObjectId(agent_id), "tenant_id": tenant_id},
        {"$set": {"status": AgentStatus.ACTIVE.value, "updated_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Get updated agent
    agent = await db.agents.find_one({"_id": ObjectId(agent_id)})
    agent["_id"] = str(agent["_id"])
    
    return AgentResponse(**agent)
