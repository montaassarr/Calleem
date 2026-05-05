"""
Shared pytest fixtures for all backend security tests.
"""

import os
import pytest
import secrets
from unittest.mock import AsyncMock, MagicMock, patch


# Provide a valid 32-byte MASTER_KEY so encryption tests can run without a real .env
MASTER_KEY_HEX = secrets.token_hex(32)


@pytest.fixture(autouse=True)
def set_master_key(monkeypatch):
    monkeypatch.setenv("MASTER_KEY", MASTER_KEY_HEX)


@pytest.fixture
def mock_db():
    """Return a mock Motor database with AsyncMock collections."""
    db = MagicMock()
    db.users = AsyncMock()
    db.tenants = AsyncMock()
    db.audit_log = AsyncMock()
    return db
