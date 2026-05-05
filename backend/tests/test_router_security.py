"""
Tests for security properties of modified routers.

Verifies:
- users.py: /register and /login have rate limit decorators
- chat.py: /init and /message have rate limit decorators
- billing.py: /sync-vapi has rate limit decorator
- admin.py: admin_add_credits requires super_admin auth
- main.py: /docs and /redoc are disabled in production, no str(exc) leakage
- database/mongo_config.py: MongoDB URI credentials are redacted in logs
"""

import os
import sys
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_source(relative_path: str) -> str:
    path = os.path.join(BACKEND_DIR, relative_path)
    with open(path) as f:
        return f.read()


def has_rate_limit_near_route(source: str, route_pattern: str) -> bool:
    """
    Check that @limiter.limit() appears within 3 lines of the @router.* decorator
    for the given route. FastAPI decorators stack in order: route first, then rate limit,
    then the function — so we look for the rate limit in the lines immediately following.
    """
    lines = source.splitlines()
    for i, line in enumerate(lines):
        if route_pattern in line and ("@router.post" in line or "@router.get" in line or "@router.put" in line):
            # Look at next 5 lines for the rate limit decorator
            window = "\n".join(lines[i:i+5])
            if "@limiter.limit" in window:
                return True
    return False


class TestRateLimitDecorators:
    def test_users_register_rate_limited(self):
        src = read_source("routers/users.py")
        assert has_rate_limit_near_route(src, '"/register"'), (
            "/register must have @limiter.limit decorator within 5 lines of @router.post"
        )

    def test_users_login_rate_limited(self):
        src = read_source("routers/users.py")
        assert has_rate_limit_near_route(src, '"/login"'), (
            "/login must have @limiter.limit decorator"
        )

    def test_chat_init_rate_limited(self):
        src = read_source("routers/chat.py")
        assert has_rate_limit_near_route(src, '"/init"'), (
            "/init must have @limiter.limit decorator"
        )

    def test_chat_message_rate_limited(self):
        src = read_source("routers/chat.py")
        assert has_rate_limit_near_route(src, '"/message"'), (
            "/message must have @limiter.limit decorator"
        )

    def test_billing_sync_vapi_rate_limited(self):
        src = read_source("routers/billing.py")
        assert has_rate_limit_near_route(src, '"/sync-vapi"'), (
            "/sync-vapi must have @limiter.limit decorator"
        )

    def test_sms_webhook_rate_limited(self):
        src = read_source("routers/webhook.py")
        assert has_rate_limit_near_route(src, '"/sms"'), (
            "/sms webhook must have @limiter.limit decorator"
        )

    def test_whatsapp_webhook_rate_limited(self):
        src = read_source("routers/webhook.py")
        assert has_rate_limit_near_route(src, '"/whatsapp"'), (
            "/whatsapp webhook must have @limiter.limit decorator"
        )


class TestAdminEndpointAuth:
    def test_add_credits_requires_super_admin(self):
        """admin_add_credits must have get_super_admin dependency after fix."""
        src = read_source("routers/admin.py")
        lines = src.splitlines()
        for i, line in enumerate(lines):
            if "async def admin_add_credits" in line:
                # Look at the function signature (next ~10 lines)
                window = "\n".join(lines[i:i+10])
                assert "get_super_admin" in window, (
                    "admin_add_credits must have Depends(get_super_admin)"
                )
                return
        pytest.fail("admin_add_credits function not found in admin.py")

    def test_impersonate_passes_admin_dict(self):
        """impersonate_user must pass the full admin dict for tenant isolation."""
        src = read_source("routers/admin.py")
        assert "impersonate_user(user_id, current_admin)" in src, (
            "Router must pass current_admin dict to impersonate_user"
        )


class TestMainAppSecurity:
    def test_docs_disabled_in_production(self):
        """FastAPI docs must be disabled unless DEBUG is True."""
        src = read_source("main.py")
        assert "docs_url" in src, "docs_url must be configured in main.py"
        assert "DEBUG" in src, "docs_url must be conditional on DEBUG flag"

    def test_exception_handler_no_exc_leakage(self):
        """Generic exception handler must not return str(exc) unconditionally."""
        src = read_source("main.py")
        if "exception_handler" in src:
            # Check for unconditional str(exc) in content/detail fields (not conditional)
            # Pattern: return ... str(exc) without a DEBUG guard
            handler_lines = [
                line.strip() for line in src.splitlines()
                if "str(exc)" in line
                and "if settings.DEBUG" not in line
                and "if" not in line
                and ("content" in line or "detail" in line or "return" in line)
            ]
            assert len(handler_lines) == 0, (
                f"Exception handler must not unconditionally expose str(exc): {handler_lines}"
            )

    def test_exception_handler_returns_generic_message(self):
        """Exception handler response must contain a safe generic error message."""
        src = read_source("main.py")
        if "exception_handler" in src or "global_exception_handler" in src:
            assert '"Internal server error"' in src or "'Internal server error'" in src, (
                "Exception handler must return a safe generic error message"
            )


class TestMongoURIRedaction:
    def test_mongo_uri_credentials_redacted(self):
        """MongoDB URI in logs must redact user:password@ portion."""
        src = read_source("database/mongo_config.py")
        assert "re.sub" in src or "***" in src, (
            "mongo_config.py must redact credentials from logged URI"
        )
        assert "@" in src, "URI redaction must handle the user:password@ portion"
