"""
Tests for backend/utils/config.py security settings.

Verifies:
- DEBUG defaults to False in code (not relying on .env)
- JWT access token expiry is 30 minutes in code defaults
- AGENT_INTERNAL_TOKEN weakness check raises RuntimeError in production
- CORS origins list is correctly parsed from string
- ENVIRONMENT defaults to "production" in code
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDefaultSettings:
    """
    Test code-level defaults, bypassing any .env file that may be present.
    We use _env_file=None to test what the class itself provides.
    """

    def _fresh_settings(self, monkeypatch, **overrides):
        """Create Settings instance ignoring .env, with optional env var overrides."""
        from utils.config import Settings
        # Clear env vars that might be set by .env
        for key in ["DEBUG", "ENVIRONMENT", "ACCESS_TOKEN_EXPIRE_MINUTES"]:
            monkeypatch.delenv(key, raising=False)
        for key, val in overrides.items():
            monkeypatch.setenv(key, str(val))
        return Settings(_env_file=None)

    def test_debug_is_false_by_default(self, monkeypatch):
        """DEBUG must default to False in code — .env may override for dev, but code is safe."""
        s = self._fresh_settings(monkeypatch)
        assert s.DEBUG is False, "DEBUG must default to False"

    def test_environment_is_production_by_default(self, monkeypatch):
        """ENVIRONMENT must default to 'production', not 'development'."""
        s = self._fresh_settings(monkeypatch)
        assert s.ENVIRONMENT == "production"

    def test_jwt_expiry_is_30_minutes(self, monkeypatch):
        """ACCESS_TOKEN_EXPIRE_MINUTES must be 30 (was previously 1440 — a 24-hour token)."""
        s = self._fresh_settings(monkeypatch)
        assert s.ACCESS_TOKEN_EXPIRE_MINUTES == 30, (
            f"JWT expiry is {s.ACCESS_TOKEN_EXPIRE_MINUTES} min — should be 30"
        )

    def test_jwt_expiry_not_excessive(self, monkeypatch):
        """JWT expiry must not exceed 60 minutes in code default."""
        s = self._fresh_settings(monkeypatch)
        assert s.ACCESS_TOKEN_EXPIRE_MINUTES <= 60

    def test_cors_origins_list_parses_correctly(self):
        from utils.config import Settings
        s = Settings()
        origins = s.cors_origins_list
        assert isinstance(origins, list)
        assert len(origins) > 0
        for origin in origins:
            assert origin.strip() != "", "CORS origin must not be empty string"
            assert origin.startswith("http"), f"CORS origin '{origin}' must start with http"

    def test_cors_origins_no_wildcard(self):
        from utils.config import Settings
        s = Settings()
        origins = s.cors_origins_list
        assert "*" not in origins, "CORS must not use wildcard '*'"

    def test_backend_url_has_no_hardcoded_value(self, monkeypatch):
        """BACKEND_URL code default must be empty — never a hardcoded production URL."""
        s = self._fresh_settings(monkeypatch)
        assert s.BACKEND_URL == ""


class TestWeakTokenCheck:
    def test_weak_agent_token_raises_in_production(self, monkeypatch):
        """AGENT_INTERNAL_TOKEN startup check must raise RuntimeError for known-weak values."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("AGENT_INTERNAL_TOKEN", "sdhcqkuefyqkjsdclzyedsdkfskdjsl")

        import importlib
        import utils.config as config_mod
        with pytest.raises((RuntimeError, SystemExit)):
            importlib.reload(config_mod)

    def test_empty_agent_token_raises_in_production(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("AGENT_INTERNAL_TOKEN", "")

        import importlib
        import utils.config as config_mod
        with pytest.raises((RuntimeError, SystemExit)):
            importlib.reload(config_mod)

    def test_strong_agent_token_accepted(self, monkeypatch):
        import secrets
        strong_token = secrets.token_urlsafe(32)
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("AGENT_INTERNAL_TOKEN", strong_token)

        import importlib
        import utils.config as config_mod
        importlib.reload(config_mod)
