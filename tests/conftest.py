"""
Pytest configuration and fixtures for AI Receptionist testing.

This file sets up the test environment with:
- Environment variables
- Python path configuration
- Common fixtures
- Mock objects
"""

import sys
import os
from pathlib import Path
import pytest

# Add project root and backend to Python path
project_root = Path(__file__).parent.parent
backend_path = project_root / "backend"

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_path))

# Set up test environment variables
os.environ.setdefault("TEST_MODE", "true")
os.environ.setdefault("MASTER_KEY", "7ccfa038143ba07e46a10a22b0bf065a580cdc36d8c003d606b567a44ff59090")  # Valid 64-char hex
os.environ.setdefault("ENCRYPTION_KEY", "test_encryption_key_1234567890abcdef")
os.environ.setdefault("JWT_SECRET", "test_jwt_secret_key_for_testing")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017/ai_receptionist_test")
os.environ.setdefault("STRIPE_MOCK_MODE", "true")
os.environ.setdefault("GROQ_API_KEY", "gsk_test_mock_key")
os.environ.setdefault("VAPI_API_KEY", "vapi_test_mock_key")
os.environ.setdefault("OPENAI_API_KEY", "sk-test_mock_key")


@pytest.fixture(scope="session")
def test_env():
    """Fixture providing test environment variables"""
    return {
        "MASTER_KEY": os.getenv("MASTER_KEY"),
        "ENCRYPTION_KEY": os.getenv("ENCRYPTION_KEY"),
        "JWT_SECRET": os.getenv("JWT_SECRET"),
        "MONGO_URI": os.getenv("MONGO_URI"),
    }


@pytest.fixture
def mock_tenant():
    """Fixture providing a mock tenant for testing"""
    from bson import ObjectId
    return {
        "_id": ObjectId(),
        "tenant_id": "test_tenant_001",
        "name": "Test Tenant",
        "email": "test@example.com",
        "plan": "pro",
        "status": "active"
    }


@pytest.fixture
def mock_api_keys():
    """Fixture providing mock encrypted API keys"""
    # These will be proper encrypted keys in actual tests
    return {
        "groq": "gsk_test_tenant_groq_key_" + "a" * 20,
        "vapi": "vapi_test_tenant_key_" + "b" * 20,
        "openai": "sk-test_tenant_openai_key_" + "c" * 20,
        "elevenlabs": "sk_test_tenant_11labs_key_" + "d" * 20
    }


@pytest.fixture
def mock_agent():
    """Fixture providing a mock agent"""
    from bson import ObjectId
    return {
        "_id": ObjectId(),
        "tenant_id": "test_tenant_001",
        "name": "Test Agent",
        "prompt": "You are a helpful assistant",
        "voice": "jennifer",
        "vapi_assistant_id": "vapi_asst_test_123"
    }


@pytest.fixture
def mock_conversation():
    """Fixture providing a mock conversation"""
    from bson import ObjectId
    from datetime import datetime
    return {
        "_id": ObjectId(),
        "tenant_id": "test_tenant_001",
        "agent_id": "agent_test_123",
        "phone_number": "+15555551234",
        "transcript": "User: Hello\nAssistant: Hi, how can I help?",
        "duration": 120,
        "created_at": datetime.utcnow()
    }


@pytest.fixture
def mock_appointment():
    """Fixture providing a mock appointment"""
    from bson import ObjectId
    from datetime import datetime
    return {
        "_id": ObjectId(),
        "tenant_id": "test_tenant_001",
        "customer_name": "John Doe",
        "customer_phone": "+15555551234",
        "customer_email": "john@example.com",
        "appointment_date": "2025-12-15",
        "appointment_time": "14:00",
        "service": "Consultation",
        "status": "confirmed",
        "created_at": datetime.utcnow()
    }


# Async fixtures for motor/MongoDB
@pytest.fixture
async def async_mock_db():
    """Fixture providing a mock async MongoDB database"""
    from unittest.mock import AsyncMock, MagicMock
    
    db = MagicMock()
    db.tenants = AsyncMock()
    db.agents = AsyncMock()
    db.conversations = AsyncMock()
    db.appointments = AsyncMock()
    db.api_keys = AsyncMock()
    
    return db
