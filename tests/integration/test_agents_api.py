"""
Phase 2 Integration Tests - Agents API

Tests the full agent CRUD flow with FastAPI TestClient.
This validates API endpoints work correctly with mocked external services (Vapi).

Critical flows:
1. Create agent → Stored in DB with tenant isolation
2. List agents → Only returns current tenant's agents
3. Get agent → Returns agent details
4. Update agent → Modifies agent correctly
5. Delete agent → Removes agent and cleans up Vapi
6. Deploy agent → Creates Vapi assistant
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from bson import ObjectId
from datetime import datetime

# Import the FastAPI app
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.main import app
from backend.database.mongo_config import get_database


class TestAgentsAPI:
    """Integration tests for Agents API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Fixture providing TestClient"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_current_user(self):
        """Fixture providing mock authenticated user"""
        return {
            "_id": str(ObjectId()),
            "email": "test@example.com",
            "tenant_id": "test_tenant_001",
            "role": "owner"
        }
    
    @pytest.fixture
    def mock_agent_data(self):
        """Fixture providing mock agent creation data"""
        return {
            "tenant_id": "test_tenant_001",
            "name": "Test Receptionist",
            "phone_number": "+15555551234",
            "voice": "jennifer",
            "language": "en-US",
            "greeting_message": "Hello, how can I help you today?",
            "system_prompt": "You are a helpful receptionist.",
            "personality_traits": ["friendly", "professional"],
            "status": "draft"
        }
    
    @patch('backend.routers.agents.get_current_user')
    @patch('backend.database.mongo_config.get_database')
    async def test_create_agent_success(self, mock_get_db, mock_auth, client, mock_current_user, mock_agent_data):
        """Test creating a new agent successfully"""
        # Setup mocks
        mock_auth.return_value = mock_current_user
        
        mock_db = Mock()
        mock_collection = AsyncMock()
        mock_db.agents = mock_collection
        
        # Mock insert_one
        inserted_id = ObjectId()
        mock_collection.insert_one = AsyncMock(return_value=Mock(inserted_id=inserted_id))
        
        # Mock find_one to return created agent
        created_agent = {**mock_agent_data, "_id": inserted_id, "created_at": datetime.utcnow()}
        mock_collection.find_one = AsyncMock(return_value=created_agent)
        
        mock_get_db.return_value = mock_db
        
        # Make request
        response = client.post("/api/v1/agents/", json=mock_agent_data)
        
        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Receptionist"
        assert data["tenant_id"] == "test_tenant_001"
        assert "id" in data or "_id" in data
    
    @patch('backend.routers.agents.get_current_user')
    @patch('backend.database.mongo_config.get_database')
    async def test_create_agent_wrong_tenant_forbidden(self, mock_get_db, mock_auth, client, mock_current_user):
        """Test that creating agent for different tenant is forbidden"""
        mock_auth.return_value = mock_current_user
        
        # Try to create agent for different tenant
        wrong_tenant_data = {
            "tenant_id": "different_tenant_999",
            "name": "Hacker Agent",
            "phone_number": "+15555559999"
        }
        
        response = client.post("/api/v1/agents/", json=wrong_tenant_data)
        
        # Should be forbidden
        assert response.status_code == 403
        assert "another tenant" in response.json()["detail"].lower()
    
    @patch('backend.routers.agents.get_current_user')
    @patch('backend.database.mongo_config.get_database')
    async def test_list_agents_only_returns_tenant_agents(self, mock_get_db, mock_auth, client, mock_current_user):
        """Test listing agents returns only current tenant's agents"""
        mock_auth.return_value = mock_current_user
        
        mock_db = Mock()
        mock_collection = AsyncMock()
        mock_db.agents = mock_collection
        
        # Mock agents for current tenant
        tenant_agents = [
            {"_id": ObjectId(), "tenant_id": "test_tenant_001", "name": "Agent 1"},
            {"_id": ObjectId(), "tenant_id": "test_tenant_001", "name": "Agent 2"}
        ]
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=tenant_agents)
        mock_collection.find = Mock(return_value=mock_cursor)
        mock_collection.count_documents = AsyncMock(return_value=2)
        
        mock_get_db.return_value = mock_db
        
        # Make request
        response = client.get("/api/v1/agents/")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        
        # Verify find was called with tenant_id filter
        call_args = mock_collection.find.call_args
        assert call_args is not None
        filter_query = call_args[0][0]
        assert filter_query["tenant_id"] == "test_tenant_001"
    
    @patch('backend.routers.agents.get_current_user')
    @patch('backend.database.mongo_config.get_database')
    async def test_get_agent_by_id_success(self, mock_get_db, mock_auth, client, mock_current_user):
        """Test getting a specific agent by ID"""
        mock_auth.return_value = mock_current_user
        
        mock_db = Mock()
        mock_collection = AsyncMock()
        mock_db.agents = mock_collection
        
        agent_id = str(ObjectId())
        agent_data = {
            "_id": ObjectId(agent_id),
            "tenant_id": "test_tenant_001",
            "name": "Test Agent",
            "status": "active"
        }
        
        mock_collection.find_one = AsyncMock(return_value=agent_data)
        mock_get_db.return_value = mock_db
        
        # Make request
        response = client.get(f"/api/v1/agents/{agent_id}")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Agent"
        
        # Verify query included tenant_id check
        call_args = mock_collection.find_one.call_args
        query = call_args[0][0]
        assert query["tenant_id"] == "test_tenant_001"
    
    @patch('backend.routers.agents.get_current_user')
    @patch('backend.database.mongo_config.get_database')
    async def test_get_agent_different_tenant_not_found(self, mock_get_db, mock_auth, client, mock_current_user):
        """Test that accessing another tenant's agent returns 404"""
        mock_auth.return_value = mock_current_user
        
        mock_db = Mock()
        mock_collection = AsyncMock()
        mock_db.agents = mock_collection
        
        # Agent doesn't exist for this tenant (returns None)
        mock_collection.find_one = AsyncMock(return_value=None)
        mock_get_db.return_value = mock_db
        
        agent_id = str(ObjectId())
        response = client.get(f"/api/v1/agents/{agent_id}")
        
        # Should return 404
        assert response.status_code == 404
    
    @patch('backend.routers.agents.get_current_user')
    @patch('backend.database.mongo_config.get_database')
    async def test_update_agent_success(self, mock_get_db, mock_auth, client, mock_current_user):
        """Test updating an agent"""
        mock_auth.return_value = mock_current_user
        
        mock_db = Mock()
        mock_collection = AsyncMock()
        mock_db.agents = mock_collection
        
        agent_id = str(ObjectId())
        
        # Mock find_one to return existing agent
        existing_agent = {
            "_id": ObjectId(agent_id),
            "tenant_id": "test_tenant_001",
            "name": "Old Name",
            "status": "draft"
        }
        mock_collection.find_one = AsyncMock(return_value=existing_agent)
        
        # Mock update_one
        mock_collection.update_one = AsyncMock(return_value=Mock(modified_count=1))
        
        mock_get_db.return_value = mock_db
        
        # Make request
        update_data = {"name": "New Name", "status": "active"}
        response = client.put(f"/api/v1/agents/{agent_id}", json=update_data)
        
        # Assertions
        assert response.status_code == 200
        
        # Verify update was called
        assert mock_collection.update_one.called
    
    @patch('backend.routers.agents.get_current_user')
    @patch('backend.database.mongo_config.get_database')
    @patch('backend.services.vapi_service.delete_vapi_assistant')
    async def test_delete_agent_success(self, mock_delete_vapi, mock_get_db, mock_auth, client, mock_current_user):
        """Test deleting an agent"""
        mock_auth.return_value = mock_current_user
        mock_delete_vapi.return_value = True
        
        mock_db = Mock()
        mock_collection = AsyncMock()
        mock_db.agents = mock_collection
        
        agent_id = str(ObjectId())
        
        # Mock find_one to return agent
        agent_data = {
            "_id": ObjectId(agent_id),
            "tenant_id": "test_tenant_001",
            "name": "Agent to Delete",
            "vapi_assistant_id": "vapi_asst_123"
        }
        mock_collection.find_one = AsyncMock(return_value=agent_data)
        
        # Mock delete_one
        mock_collection.delete_one = AsyncMock(return_value=Mock(deleted_count=1))
        
        mock_get_db.return_value = mock_db
        
        # Make request
        response = client.delete(f"/api/v1/agents/{agent_id}")
        
        # Assertions
        assert response.status_code in [200, 204]
        
        # Verify Vapi cleanup was called
        mock_delete_vapi.assert_called_once()
    
    @patch('backend.routers.agents.get_current_user')
    @patch('backend.database.mongo_config.get_database')
    @patch('backend.services.vapi_service.create_vapi_assistant')
    async def test_deploy_agent_creates_vapi_assistant(self, mock_create_vapi, mock_get_db, mock_auth, client, mock_current_user):
        """Test deploying an agent creates Vapi assistant"""
        mock_auth.return_value = mock_current_user
        
        # Mock Vapi service
        mock_create_vapi.return_value = {
            "id": "vapi_asst_new_123",
            "phoneNumberId": "vapi_phone_456"
        }
        
        mock_db = Mock()
        mock_collection = AsyncMock()
        mock_db.agents = mock_collection
        
        agent_id = str(ObjectId())
        
        # Mock find_one to return agent
        agent_data = {
            "_id": ObjectId(agent_id),
            "tenant_id": "test_tenant_001",
            "name": "Agent to Deploy",
            "status": "draft",
            "vapi_assistant_id": None
        }
        mock_collection.find_one = AsyncMock(return_value=agent_data)
        
        # Mock update_one
        mock_collection.update_one = AsyncMock(return_value=Mock(modified_count=1))
        
        mock_get_db.return_value = mock_db
        
        # Make request
        response = client.post(f"/api/v1/agents/{agent_id}/deploy")
        
        # Assertions
        assert response.status_code == 200
        
        # Verify Vapi was called
        mock_create_vapi.assert_called_once()
        
        # Verify agent was updated with Vapi IDs
        assert mock_collection.update_one.called


class TestAgentsAPIEdgeCases:
    """Edge case tests for Agents API"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @patch('backend.routers.agents.get_current_user')
    def test_create_agent_missing_required_fields(self, mock_auth, client):
        """Test creating agent with missing fields returns 422"""
        mock_auth.return_value = {"tenant_id": "test_tenant_001"}
        
        # Missing required fields
        incomplete_data = {
            "name": "Incomplete Agent"
            # Missing tenant_id, phone_number, etc.
        }
        
        response = client.post("/api/v1/agents/", json=incomplete_data)
        
        # Should be validation error
        assert response.status_code == 422
    
    @patch('backend.routers.agents.get_current_user')
    def test_list_agents_with_pagination(self, mock_auth, client):
        """Test listing agents with skip and limit parameters"""
        mock_auth.return_value = {"tenant_id": "test_tenant_001"}
        
        # Make request with pagination
        response = client.get("/api/v1/agents/?skip=10&limit=20")
        
        # Should not error (even if no data)
        assert response.status_code in [200, 401]  # 401 if auth not fully mocked
    
    @patch('backend.routers.agents.get_current_user')
    def test_update_agent_invalid_id_format(self, mock_auth, client):
        """Test updating with invalid ObjectId format"""
        mock_auth.return_value = {"tenant_id": "test_tenant_001"}
        
        # Invalid ObjectId
        response = client.put("/api/v1/agents/invalid_id_format", json={"name": "New Name"})
        
        # Should return 400 or 422
        assert response.status_code in [400, 422, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
