import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.admin_service import AdminService
from models.core.tenants import TenantCreate
from bson import ObjectId

@pytest.fixture
def mock_db():
    db = AsyncMock()
    # collections are AsyncMock by default, but find is synchronous returning a cursor
    db.tenants = AsyncMock()
    db.tenants.find = MagicMock()
    db.users = AsyncMock()
    return db

@pytest.fixture
def admin_service(mock_db):
    with patch('services.admin_service.get_database', return_value=mock_db):
        yield AdminService()

@pytest.mark.asyncio
async def test_list_tenants(admin_service, mock_db):
    # Setup
    mock_tenants = [
        {"_id": ObjectId(), "name": "Tenant A"},
        {"_id": ObjectId(), "name": "Tenant B"}
    ]
    # Mock cursor behavior
    # Use MagicMock for the cursor so chaining works synchronously
    mock_cursor = MagicMock()
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    # to_list is async, so it should be an AsyncMock
    mock_cursor.to_list = AsyncMock(return_value=mock_tenants)
    
    mock_db.tenants.find.return_value = mock_cursor

    # Execute
    result = await admin_service.list_tenants(skip=0, limit=10, search=None)

    # Verify
    assert len(result) == 2
    assert result[0]["name"] == "Tenant A"
    # Defaults should be injected
    assert result[0]["total_calls"] == 0

@pytest.mark.asyncio
async def test_create_tenant(admin_service, mock_db):
    # Setup
    # Provide owner_id as required by Pydantic model
    tenant_data = TenantCreate(name="New Tenant", email="test@example.com", owner_id="owner123")
    
    # Mock check for existing
    mock_db.tenants.find_one.side_effect = [None, None] # Name ok, Email ok (simplified)
    
    mock_insert_result = AsyncMock()
    mock_insert_result.inserted_id = ObjectId()
    mock_db.tenants.insert_one.return_value = mock_insert_result
    
    # Mock retrieval of created tenant
    mock_created_tenant = {
        "_id": mock_insert_result.inserted_id,
        "name": "New Tenant",
        "created_at": "2024-01-01",
        "total_calls": 0
    }
    # Reset side effect for the 3rd call (the retrieval)
    mock_db.tenants.find_one.side_effect = None 
    # Use a sequence of return values: check_name(None), retrieval(mock_created)
    # The service logic: checks name first.
    
    # Let's adjust mock for clarity
    mock_db.tenants.find_one = AsyncMock(side_effect=[
        None, # check name existence
        mock_created_tenant # retrieve created
    ])

    # Execute
    result = await admin_service.create_tenant(tenant_data)

    # Verify
    assert result["name"] == "New Tenant"
    mock_db.tenants.insert_one.assert_called_once()
