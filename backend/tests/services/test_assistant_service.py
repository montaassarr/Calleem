import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.assistant_service import AssistantService
from models.core.tenants import Tenant

@pytest.fixture
def mock_db():
    db = AsyncMock()
    # Mock collection access
    db.tenants = AsyncMock()
    return db

@pytest.fixture
def mock_vapi():
    return AsyncMock()

@pytest.fixture
def assistant_service(mock_db, mock_vapi):
    # Patch get_database to return our mock_db
    with patch('services.assistant_service.get_database', return_value=mock_db):
        service = AssistantService()
        # Inject mock vapi service if the service uses a global instance, 
        # but better to patch the module level import
        with patch('services.assistant_service.vapi_service', mock_vapi):
            yield service

@pytest.mark.asyncio
async def test_get_assistant_found(assistant_service, mock_db, mock_vapi):
    # Setup
    tenant_id = "tenant123"
    mock_tenant = {
        "tenant_id": tenant_id,
        "vapi_assistant_id": "vapi123"
    }
    mock_db.tenants.find_one.return_value = mock_tenant
    
    mock_vapi_details = {
        "id": "vapi123",
        "name": "Test Assistant",
        "firstMessage": "Hello",
        "voice": "voice-id",
        "model": "gpt-4"
    }
    mock_vapi.get_assistant.return_value = mock_vapi_details

    # Execute
    result = await assistant_service.get_assistant(tenant_id)

    # Verify
    assert result["configured"] is True
    assert result["assistant_id"] == "vapi123"
    assert result["name"] == "Test Assistant"
    mock_db.tenants.find_one.assert_called_once()
    mock_vapi.get_assistant.assert_called_with("vapi123")

@pytest.mark.asyncio
async def test_get_assistant_not_configured(assistant_service, mock_db):
    # Setup
    tenant_id = "tenant123"
    # Tenant exists but has no assistant
    mock_tenant = {"tenant_id": tenant_id, "vapi_assistant_id": None}
    mock_db.tenants.find_one.return_value = mock_tenant

    # Execute
    result = await assistant_service.get_assistant(tenant_id)

    # Verify
    assert result["configured"] is False

@pytest.mark.asyncio
async def test_update_assistant(assistant_service, mock_db, mock_vapi):
    # Setup
    tenant_id = "tenant123"
    config = MagicMock()
    config.company_name = "Tech Corp"
    config.instructions = "Be helpful"
    config.first_message = "Hi"
    config.voice = "voice-id"
    config.voice_provider = "11labs"
    config.voice_speed = 1.0
    config.model = "gpt-4"
    config.temperature = 0.7
    config.max_tokens = 100
    config.tools = []

    mock_tenant = {
        "_id": "obj123",
        "tenant_id": tenant_id,
        "vapi_assistant_id": "vapi123",
        "business_name": "Old Corp"
    }
    mock_db.tenants.find_one.return_value = mock_tenant
    
    mock_vapi_response = {
        "id": "vapi123",
        "name": "Tech Corp Assistant",
        # ... other fields
    }
    mock_vapi.update_assistant.return_value = mock_vapi_response
    
    # Mock update_one result
    update_result = MagicMock()
    update_result.modified_count = 1
    mock_db.tenants.update_one.return_value = update_result

    # Execute
    # Patch ObjectId to allow string 'tenant123' or use valid ObjectId
    with patch('bson.ObjectId', MagicMock(return_value="obj123")):
        result = await assistant_service.update_assistant(tenant_id, config)

    # Verify
    mock_vapi.update_assistant.assert_called_with(
        assistant_id="vapi123",
        company_name="Tech Corp",
        instructions="Be helpful",
        first_message="Hi",
        voice="voice-id",
        voice_provider="11labs",
        voice_speed=1.0,
        model="gpt-4",
        temperature=0.7,
        max_tokens=100,
        tools=[]
    )
    # mock_db.tenants.update_one.assert_called_once() # Called by repo
    assert result == mock_vapi_response
