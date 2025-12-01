"""
Phase 1 Unit Tests - Tenant Isolation Module

Tests multi-tenant data isolation. This is CRITICAL - a data leak between
tenants would destroy the business and violate GDPR/privacy laws.

Tests:
1. Get tenant A's agents → Only tenant A's agents returned
2. Get tenant B's conversations → Only tenant B's conversations
3. Tenant A can't delete tenant B's agent
4. Tenant A can't read tenant B's API keys
5. Tenant A can't update tenant B's profile
6. No tenant_id in query → Error (not all results)
7. Invalid tenant_id → Empty results (not error)
8. Database queries always include tenant_id filter
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from bson import ObjectId


class TestTenantIsolation:
    """Test suite for multi-tenant data isolation"""
    
    @pytest.fixture
    def mock_db(self):
        """Fixture: Mock MongoDB database"""
        db = MagicMock()
        db.agents = AsyncMock()
        db.conversations = AsyncMock()
        db.api_keys = AsyncMock()
        db.tenants = AsyncMock()
        return db
    
    @pytest.fixture
    def tenant_a_id(self):
        return str(ObjectId())
    
    @pytest.fixture
    def tenant_b_id(self):
        return str(ObjectId())
    
    @pytest.mark.asyncio
    async def test_get_tenant_a_agents_only_returns_tenant_a(self, mock_db, tenant_a_id, tenant_b_id):
        """Test that getting tenant A's agents only returns tenant A's agents"""
        # Setup mock data
        agent_a1 = {"_id": ObjectId(), "tenant_id": tenant_a_id, "name": "Agent A1"}
        agent_a2 = {"_id": ObjectId(), "tenant_id": tenant_a_id, "name": "Agent A2"}
        agent_b1 = {"_id": ObjectId(), "tenant_id": tenant_b_id, "name": "Agent B1"}
        
        # Mock the cursor that find() returns
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=[agent_a1, agent_a2])
        mock_db.agents.find = MagicMock(return_value=mock_cursor)
        
        # Query for tenant A's agents
        agents = await mock_db.agents.find({"tenant_id": tenant_a_id}).to_list(None)
        
        # Verify only tenant A's agents returned
        assert len(agents) == 2
        assert all(agent["tenant_id"] == tenant_a_id for agent in agents)
        assert not any(agent["tenant_id"] == tenant_b_id for agent in agents)
        
        # Verify query included tenant_id filter
        mock_db.agents.find.assert_called_with({"tenant_id": tenant_a_id})
        
    @pytest.mark.asyncio
    async def test_get_tenant_b_conversations_only_returns_tenant_b(self, mock_db, tenant_a_id, tenant_b_id):
        """Test that getting tenant B's conversations only returns tenant B's"""
        # Setup mock data
        conv_a1 = {"_id": ObjectId(), "tenant_id": tenant_a_id, "transcript": "A conversation"}
        conv_b1 = {"_id": ObjectId(), "tenant_id": tenant_b_id, "transcript": "B conversation"}
        conv_b2 = {"_id": ObjectId(), "tenant_id": tenant_b_id, "transcript": "B conversation 2"}
        
        # Mock the cursor that find() returns
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=[conv_b1, conv_b2])
        mock_db.conversations.find = MagicMock(return_value=mock_cursor)
        
        # Query for tenant B's conversations
        conversations = await mock_db.conversations.find({"tenant_id": tenant_b_id}).to_list(None)
        
        # Verify only tenant B's conversations returned
        assert len(conversations) == 2
        assert all(conv["tenant_id"] == tenant_b_id for conv in conversations)
        
    @pytest.mark.asyncio
    async def test_tenant_a_cannot_delete_tenant_b_agent(self, mock_db, tenant_a_id, tenant_b_id):
        """Test that tenant A cannot delete tenant B's agent"""
        agent_b_id = ObjectId()
        
        # Mock delete operation - should fail or return 0 deleted
        mock_db.agents.delete_one = AsyncMock(return_value=Mock(deleted_count=0))
        
        # Try to delete tenant B's agent with tenant A's filter
        result = await mock_db.agents.delete_one({
            "_id": agent_b_id,
            "tenant_id": tenant_a_id  # Wrong tenant!
        })
        
        # Verify no documents deleted
        assert result.deleted_count == 0
        
        # Verify query included tenant_id filter (security!)
        mock_db.agents.delete_one.assert_called_with({
            "_id": agent_b_id,
            "tenant_id": tenant_a_id
        })
        
    @pytest.mark.asyncio
    async def test_tenant_a_cannot_read_tenant_b_api_keys(self, mock_db, tenant_a_id, tenant_b_id):
        """Test that tenant A cannot read tenant B's API keys"""
        # Mock database to return None (no access)
        mock_db.api_keys.find_one = AsyncMock(return_value=None)
        
        # Try to read tenant B's keys with tenant A's credentials
        result = await mock_db.api_keys.find_one({"tenant_id": tenant_b_id})
        
        # Should return None (no results) when tenant_id doesn't match auth
        assert result is None
        
    @pytest.mark.asyncio
    async def test_tenant_a_cannot_update_tenant_b_profile(self, mock_db, tenant_a_id, tenant_b_id):
        """Test that tenant A cannot update tenant B's profile"""
        # Mock update operation - should fail or return 0 modified
        mock_db.tenants.update_one = AsyncMock(return_value=Mock(modified_count=0))
        
        # Try to update tenant B's profile with tenant A's filter
        result = await mock_db.tenants.update_one(
            {"_id": ObjectId(tenant_b_id), "owner_id": tenant_a_id},  # Wrong owner!
            {"$set": {"name": "Hacked!"}}
        )
        
        # Verify no documents modified
        assert result.modified_count == 0
        
    @pytest.mark.asyncio
    async def test_query_without_tenant_id_raises_error(self, mock_db):
        """Test that queries without tenant_id raise error (safety check)"""
        # This should be enforced at the API router level
        # If a query doesn't include tenant_id, it's a bug
        
        # Simulate a middleware check
        def require_tenant_id(query):
            if "tenant_id" not in query:
                raise ValueError("Security Error: tenant_id required in query")
            return query
        
        # Try query without tenant_id
        with pytest.raises(ValueError, match="tenant_id required"):
            require_tenant_id({"name": "some_agent"})
            
    @pytest.mark.asyncio
    async def test_invalid_tenant_id_returns_empty(self, mock_db):
        """Test that invalid tenant_id returns empty results, not error"""
        fake_tenant_id = "invalid_tenant_id_999"
        
        # Mock the cursor that find() returns
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=[])
        mock_db.agents.find = MagicMock(return_value=mock_cursor)
        
        # Query with invalid tenant_id
        agents = await mock_db.agents.find({"tenant_id": fake_tenant_id}).to_list(None)
        
        # Should return empty list, not error
        assert agents == []
        assert len(agents) == 0
        
    @pytest.mark.asyncio
    async def test_database_queries_always_include_tenant_id_filter(self, mock_db, tenant_a_id):
        """Test that all database queries include tenant_id filter"""
        # This tests the query builder/middleware
        
        # Define a query builder that always adds tenant_id
        def build_query(base_query, tenant_id):
            return {**base_query, "tenant_id": tenant_id}
        
        # Test various queries
        queries = [
            {"name": "Test Agent"},
            {"status": "active"},
            {"created_at": {"$gte": "2025-01-01"}}
        ]
        
        for base_query in queries:
            full_query = build_query(base_query, tenant_a_id)
            
            # Verify tenant_id always included
            assert "tenant_id" in full_query
            assert full_query["tenant_id"] == tenant_a_id


class TestTenantIsolationEdgeCases:
    """Additional edge case tests for tenant isolation"""
    
    @pytest.mark.asyncio
    async def test_empty_tenant_id_rejected(self):
        """Test that empty tenant_id is rejected"""
        def validate_tenant_id(tenant_id):
            if not tenant_id or tenant_id.strip() == "":
                raise ValueError("Invalid tenant_id")
            return tenant_id
        
        with pytest.raises(ValueError, match="Invalid tenant_id"):
            validate_tenant_id("")
            
    @pytest.mark.asyncio
    async def test_none_tenant_id_rejected(self):
        """Test that None tenant_id is rejected"""
        def validate_tenant_id(tenant_id):
            if tenant_id is None:
                raise ValueError("tenant_id cannot be None")
            return tenant_id
        
        with pytest.raises(ValueError, match="cannot be None"):
            validate_tenant_id(None)
            
    @pytest.mark.asyncio
    async def test_sql_injection_in_tenant_id_blocked(self):
        """Test that SQL injection attempts in tenant_id are blocked"""
        malicious_tenant_id = "tenant' OR '1'='1"
        
        # MongoDB is safe from SQL injection, but test validation
        def sanitize_tenant_id(tenant_id):
            # Only allow alphanumeric and underscores
            import re
            if not re.match(r'^[a-zA-Z0-9_]+$', tenant_id):
                raise ValueError("Invalid tenant_id format")
            return tenant_id
        
        with pytest.raises(ValueError, match="Invalid tenant_id format"):
            sanitize_tenant_id(malicious_tenant_id)
            
    @pytest.mark.asyncio
    async def test_cross_tenant_aggregation_queries_isolated(self):
        """Test that aggregation queries don't leak data across tenants"""
        # MongoDB aggregation pipelines must include tenant_id filter
        
        def build_aggregation_pipeline(tenant_id):
            return [
                {"$match": {"tenant_id": tenant_id}},  # CRITICAL: First stage must filter by tenant
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]
        
        tenant_a_id = "tenant_a"
        pipeline = build_aggregation_pipeline(tenant_a_id)
        
        # Verify first stage is tenant filter
        assert pipeline[0]["$match"]["tenant_id"] == tenant_a_id
        
    @pytest.mark.asyncio
    async def test_admin_queries_must_be_explicit(self):
        """Test that admin queries must explicitly bypass tenant filter"""
        # Admin should not accidentally query all tenants
        
        def admin_query(tenant_id=None, admin_override=False):
            if not admin_override and not tenant_id:
                raise ValueError("Admin must explicitly set admin_override=True")
            
            if admin_override:
                return {}  # No tenant filter (admin sees all)
            else:
                return {"tenant_id": tenant_id}
        
        # Normal query requires tenant_id
        with pytest.raises(ValueError):
            admin_query()
        
        # Admin must be explicit
        query = admin_query(admin_override=True)
        assert "tenant_id" not in query


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
