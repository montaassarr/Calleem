"""
Fixtures for integration tests
Provides authentication overrides and common test setup
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock
from bson import ObjectId
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.main import app


@pytest.fixture
def mock_user_owner():
    """Mock owner user for authentication"""
    return {
        "_id": str(ObjectId()),
        "email": "owner@test.com",
        "tenant_id": "test_tenant_001",
        "role": "owner",
        "full_name": "Test Owner"
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
def authenticated_client(mock_user_owner):
    """
    TestClient with authentication bypassed
    Use this fixture for tests that need authenticated requests
    """
    from backend.routers.users import get_current_user
    
    # Override the authentication dependency
    def override_get_current_user():
        return mock_user_owner
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    client = TestClient(app)
    
    yield client
    
    # Clean up
    app.dependency_overrides.clear()


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
