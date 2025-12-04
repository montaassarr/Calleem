"""
Fixtures for integration tests
Provides authentication overrides and common test setup
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
from bson import ObjectId
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.main import app


@pytest.fixture
def mock_user_owner():
    """Mock owner user for authentication"""
    return {
        "_id": ObjectId(),
        "email": "owner@test.com",
        "tenant_id": "test_tenant_001",
        "role": "owner",
        "full_name": "Test Owner",
        "is_active": True
    }


@pytest.fixture
def mock_user_staff():
    """Mock staff user for authentication"""
    return {
        "_id": str(ObjectId()),
        "email": "staff@test.com",
        "tenant_id": "test_tenant_001",
        "role": "staff",
        "full_name": "Test Staff"
    }


@pytest.fixture
def auth_headers(mock_user_owner):
    """
    Generate valid JWT token for authentication
    Returns headers dict with Authorization bearer token
    """
    from backend.routers.users import create_access_token
    from datetime import timedelta
    
    # Create a real JWT token with the mock user's ID
    token_data = {"sub": str(mock_user_owner["_id"])}
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(hours=1)
    )
    
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def authenticated_client(mock_user_owner, mock_db_connection, auth_headers):
    """
    TestClient with pre-configured auth headers and mocked database
    Use this fixture for tests that need authenticated requests
    
    Usage:
        response = authenticated_client.get("/api/v1/agents/")
        # Headers are automatically included
    """
    from backend.database.mongo_config import get_database
    import backend.database.mongo_config as mongo_config
    
    # Mock the database to return our mock user when JWT validation looks up the user
    mock_db_connection.users.find_one = AsyncMock(return_value={
        **mock_user_owner,
        "_id": mock_user_owner["_id"],  # Keep as ObjectId
        "id": str(mock_user_owner["_id"])
    })
    
    # CRITICAL: Patch the module-level database variable
    with patch.object(mongo_config, 'database', mock_db_connection):
        
        # Create client
        client = TestClient(app)
        
        # Monkey-patch client methods to automatically include auth headers
        original_get = client.get
        original_post = client.post
        original_put = client.put
        original_delete = client.delete
        original_patch = client.patch
        
        def get_with_auth(url, **kwargs):
            kwargs.setdefault('headers', {}).update(auth_headers)
            return original_get(url, **kwargs)
        
        def post_with_auth(url, **kwargs):
            kwargs.setdefault('headers', {}).update(auth_headers)
            return original_post(url, **kwargs)
        
        def put_with_auth(url, **kwargs):
            kwargs.setdefault('headers', {}).update(auth_headers)
            return original_put(url, **kwargs)
        
        def delete_with_auth(url, **kwargs):
            kwargs.setdefault('headers', {}).update(auth_headers)
            return original_delete(url, **kwargs)
        
        def patch_with_auth(url, **kwargs):
            kwargs.setdefault('headers', {}).update(auth_headers)
            return original_patch(url, **kwargs)
        
        client.get = get_with_auth
        client.post = post_with_auth
        client.put = put_with_auth
        client.delete = delete_with_auth
        client.patch = patch_with_auth
        
        yield client


@pytest.fixture
def unauthenticated_client():
    """
    TestClient without authentication
    Use this fixture for tests that should fail with 401
    """
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Mock MongoDB database"""
    db = Mock()
    return db


@pytest.fixture
def mock_db_connection():
    """Mock MongoDB database connection with common collections"""
    db = Mock()
    
    # Mock collections with async methods
    db.agents = AsyncMock()
    db.appointments = AsyncMock()
    db.conversations = AsyncMock()
    db.tenants = AsyncMock()
    db.users = AsyncMock()
    db.services = AsyncMock()
    
    # Default return values for common queries
    db.agents.find.return_value.to_list = AsyncMock(return_value=[])
    db.agents.find_one = AsyncMock(return_value=None)
    db.agents.insert_one = AsyncMock(return_value=Mock(inserted_id=ObjectId()))
    db.agents.update_one = AsyncMock(return_value=Mock(modified_count=1))
    db.agents.delete_one = AsyncMock(return_value=Mock(deleted_count=1))
    
    db.appointments.find.return_value.to_list = AsyncMock(return_value=[])
    db.appointments.find_one = AsyncMock(return_value=None)
    db.appointments.insert_one = AsyncMock(return_value=Mock(inserted_id=ObjectId()))
    db.appointments.update_one = AsyncMock(return_value=Mock(modified_count=1))
    
    db.tenants.find_one = AsyncMock(return_value=None)
    db.tenants.insert_one = AsyncMock(return_value=Mock(inserted_id=ObjectId()))
    
    db.users.find_one = AsyncMock(return_value=None)
    db.users.insert_one = AsyncMock(return_value=Mock(inserted_id=ObjectId()))
    
    return db


@pytest.fixture
def sample_agent_data():
    """Sample agent data for tests"""
    return {
        "tenant_id": "test_tenant_001",
        "name": "Test Agent",
        "phone_number": "+15555551234",
        "voice": "jennifer",
        "language": "en-US",
        "greeting_message": "Hello!",
        "system_prompt": "You are helpful.",
        "personality_traits": ["friendly"],
        "status": "draft"
    }


@pytest.fixture
def sample_appointment_data():
    """Sample appointment data for tests"""
    from datetime import datetime, timedelta
    tomorrow = datetime.utcnow() + timedelta(days=1)
    
    return {
        "tenant_id": "test_tenant_001",
        "customer_name": "John Doe",
        "customer_phone": "+15555551234",
        "customer_email": "john@example.com",
        "appointment_date": tomorrow.strftime("%Y-%m-%d"),
        "appointment_time": "14:00",
        "service": "Haircut",
        "duration_minutes": 30,
        "status": "confirmed"
    }


@pytest.fixture(autouse=True, scope="function")
def clean_test_database():
    """
    Automatically clean the test database before each test function.
    This ensures test isolation for integration tests.
    """
    import subprocess
    
    # Clean before test
    subprocess.run(
        [
            "mongosh", "ai_receptionist_test", "--quiet", "--eval",
            "db.users.deleteMany({}); db.tenants.deleteMany({}); db.api_keys.deleteMany({}); db.conversations.deleteMany({}); db.appointments.deleteMany({});"
        ],
        capture_output=True,
        text=True
    )
    
    yield  # Run the test
    
    # No cleanup after - let next test handle it for inspection if needed
