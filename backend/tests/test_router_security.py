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
    with open(path, encoding="utf-8") as f:
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

    def test_admin_router_is_super_admin_only(self):
        """The platform admin API is for the super admin only: business owners and their admins get 403."""
        src = read_source("routers/admin.py")
        assert "router = APIRouter(dependencies=[Depends(get_super_admin)])" in src, (
            "Every /api/v1/admin route must require get_super_admin"
        )
        assert "get_current_admin" not in src, (
            "get_current_admin lets owners in; admin.py must not use it"
        )

    def test_admin_router_mount_is_switchable(self):
        """Public deployments run with ADMIN_API_ENABLED=false, so main.py must only mount the admin router behind it."""
        src = read_source("main.py")
        assert re.search(r"if settings\.ADMIN_API_ENABLED:\s*\n\s+app\.include_router\(admin\.router", src), (
            "admin.router must be included only when settings.ADMIN_API_ENABLED is true"
        )

    def test_contact_management_is_admin_only(self):
        """Submitting the contact form is public; reading, editing and deleting leads is not."""
        src = read_source("routers/contacts.py")
        routes = re.findall(r"@router\.(get|post|put|delete)\((.*)\)", src)
        assert routes, "no routes found in contacts.py"
        for method, args in routes:
            if method == "post" and args.startswith('""'):
                assert "ADMIN_ONLY" not in args, "the public contact form must stay open"
            else:
                assert "dependencies=ADMIN_ONLY" in args, f"{method.upper()} {args.split(',')[0]} must be admin-only"

    def test_business_config_stays_available_to_clients(self):
        """The client dashboard reads/writes its own config at /admin/config: owners keep access
        and the route stays mounted when the platform admin API is switched off."""
        router_src = read_source("routers/business_config.py")
        assert "Depends(get_current_admin)" in router_src, "owners and their admins must keep access"
        main_src = read_source("main.py")
        mount = 'app.include_router(business_config.router, prefix=f"{settings.API_V1_PREFIX}/admin"'
        assert mount in main_src, "business_config router must be mounted under /api/v1/admin"
        line = next(l for l in main_src.splitlines() if mount in l)
        assert not line.startswith(" "), "business_config must not be gated behind ADMIN_API_ENABLED"
        assert '@router.get("/config")' not in read_source("routers/admin.py"), "config must not live in the super-admin router"


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
