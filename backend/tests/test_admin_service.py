"""
Tests for backend/services/admin_service.py security fixes.

Verifies:
- list_tenants uses re.escape() to prevent ReDoS via $regex injection
- impersonate_user enforces tenant isolation for non-super-admins
- impersonate_user writes an audit log entry on success
- impersonate_user allows super_admin to cross tenants
"""

import pytest
import re
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch, call
from bson import ObjectId
from datetime import datetime
from fastapi import HTTPException

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


TENANT_A = str(ObjectId())
TENANT_B = str(ObjectId())
USER_ID = str(ObjectId())


def make_service(mock_db):
    from services.admin_service import AdminService
    svc = AdminService.__new__(AdminService)
    svc.db = mock_db
    return svc


class TestListTenantsRegexEscape:
    def test_re_escape_used_in_source(self):
        """list_tenants must call re.escape() to prevent ReDoS via user-supplied regex."""
        import inspect
        from services import admin_service
        src = inspect.getsource(admin_service)
        assert "re.escape(search)" in src, (
            "admin_service.py must use re.escape(search) in list_tenants"
        )

    def test_special_chars_are_escaped(self):
        """Verify that re.escape actually escapes regex metacharacters."""
        dangerous = "(.*)|DROP"
        escaped = re.escape(dangerous)
        assert escaped != dangerous
        # The escaped version must not match an unintended wider pattern
        assert re.search(escaped, "(.*)|DROP")  # exact literal match
        assert not re.search(escaped, "anything_else")


class TestImpersonationTenantIsolation:
    @pytest.mark.asyncio
    async def test_admin_cannot_impersonate_different_tenant(self, mock_db):
        """Non-super-admin must not impersonate a user from a different tenant."""
        target_user = {
            "_id": ObjectId(USER_ID),
            "username": "victim",
            "role": "user",
            "tenant_id": TENANT_B,
        }
        mock_db.users.find_one = AsyncMock(return_value=target_user)

        admin = {"role": "admin", "tenant_id": TENANT_A, "username": "attacker"}
        svc = make_service(mock_db)

        with pytest.raises(HTTPException) as exc_info:
            await svc.impersonate_user(USER_ID, admin)

        assert exc_info.value.status_code == 403
        assert "different tenant" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_admin_can_impersonate_same_tenant(self, mock_db):
        """Non-super-admin must be allowed to impersonate a user in the same tenant."""
        target_user = {
            "_id": ObjectId(USER_ID),
            "username": "colleague",
            "role": "user",
            "tenant_id": TENANT_A,
        }
        mock_db.users.find_one = AsyncMock(return_value=target_user)
        mock_db.audit_log.insert_one = AsyncMock(return_value=MagicMock())

        admin = {"role": "admin", "tenant_id": TENANT_A, "username": "boss", "id": str(ObjectId())}
        svc = make_service(mock_db)

        with patch("services.admin_service.UserService") as MockUserService:
            mock_user_svc = MockUserService.return_value
            mock_user_svc.create_access_token = MagicMock(return_value="mock-token")
            result = await svc.impersonate_user(USER_ID, admin)

        assert result["access_token"] == "mock-token"

    @pytest.mark.asyncio
    async def test_super_admin_can_impersonate_any_tenant(self, mock_db):
        """super_admin must bypass tenant isolation check."""
        target_user = {
            "_id": ObjectId(USER_ID),
            "username": "other-tenant-user",
            "role": "user",
            "tenant_id": TENANT_B,
        }
        mock_db.users.find_one = AsyncMock(return_value=target_user)
        mock_db.audit_log.insert_one = AsyncMock(return_value=MagicMock())

        admin = {"role": "super_admin", "tenant_id": TENANT_A, "username": "superuser", "id": str(ObjectId())}
        svc = make_service(mock_db)

        with patch("services.admin_service.UserService") as MockUserService:
            mock_user_svc = MockUserService.return_value
            mock_user_svc.create_access_token = MagicMock(return_value="super-token")
            result = await svc.impersonate_user(USER_ID, admin)

        assert result["access_token"] == "super-token"

    @pytest.mark.asyncio
    async def test_impersonation_writes_audit_log(self, mock_db):
        """Every impersonation must write a record to audit_log collection."""
        target_user = {
            "_id": ObjectId(USER_ID),
            "username": "target",
            "role": "user",
            "tenant_id": TENANT_A,
        }
        mock_db.users.find_one = AsyncMock(return_value=target_user)
        mock_db.audit_log.insert_one = AsyncMock(return_value=MagicMock())

        admin = {"role": "admin", "tenant_id": TENANT_A, "username": "admin_user", "id": str(ObjectId())}
        svc = make_service(mock_db)

        with patch("services.admin_service.UserService") as MockUserService:
            MockUserService.return_value.create_access_token = MagicMock(return_value="tok")
            await svc.impersonate_user(USER_ID, admin)

        mock_db.audit_log.insert_one.assert_called_once()
        audit_entry = mock_db.audit_log.insert_one.call_args[0][0]
        assert audit_entry["action"] == "impersonate"
        assert audit_entry["target_user_id"] == USER_ID
        assert "timestamp" in audit_entry

    @pytest.mark.asyncio
    async def test_invalid_user_id_raises_400(self, mock_db):
        svc = make_service(mock_db)
        with pytest.raises(HTTPException) as exc_info:
            await svc.impersonate_user("not-a-valid-id", {"role": "super_admin"})
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_nonexistent_user_raises_404(self, mock_db):
        mock_db.users.find_one = AsyncMock(return_value=None)
        svc = make_service(mock_db)
        with pytest.raises(HTTPException) as exc_info:
            await svc.impersonate_user(USER_ID, {"role": "super_admin"})
        assert exc_info.value.status_code == 404
