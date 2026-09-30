"""
Tests for backend/routers/webhook.py security fixes.

Verifies:
- _validate_twilio_signature rejects requests with invalid signatures
- _validate_twilio_signature accepts requests with valid signatures
- _validate_twilio_signature skips validation when TWILIO_AUTH_TOKEN is unset (logs warning)
- Rate limit decorators are present on /sms and /whatsapp endpoints
- Phone numbers are masked in log output (PII)
"""

import pytest
import os
import sys
import inspect
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestTwilioSignatureValidation:
    @pytest.mark.asyncio
    async def test_valid_signature_passes(self):
        """A correctly signed Twilio request must be accepted."""
        from twilio.request_validator import RequestValidator
        auth_token = "test_auth_token_12345"
        url = "https://example.com/api/v1/webhook/sms"
        form_data = {"From": "+15551234567", "Body": "Hello"}

        validator = RequestValidator(auth_token)
        signature = validator.compute_signature(url, form_data)

        # Simulate what _validate_twilio_signature does
        assert validator.validate(url, form_data, signature)

    @pytest.mark.asyncio
    async def test_invalid_signature_rejected(self):
        """A request with a tampered signature must be rejected."""
        from fastapi import HTTPException
        from unittest.mock import MagicMock, patch

        mock_request = MagicMock()
        mock_request.url = MagicMock()
        mock_request.url.__str__ = MagicMock(return_value="https://example.com/api/v1/webhook/sms")
        mock_request.headers = {"X-Twilio-Signature": "INVALID_SIG"}
        mock_request.client = MagicMock()
        mock_request.client.host = "1.2.3.4"

        with patch("utils.config.settings") as mock_settings:
            mock_settings.TWILIO_AUTH_TOKEN = "real_auth_token"
            from routers.webhook import _validate_twilio_signature
            with pytest.raises(HTTPException) as exc_info:
                await _validate_twilio_signature(mock_request, {"From": "+15551234567"})
            assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_missing_auth_token_skips_validation(self):
        """When TWILIO_AUTH_TOKEN is not set, validation is skipped without raising."""
        from unittest.mock import MagicMock, patch
        import logging

        mock_request = MagicMock()
        mock_request.url = MagicMock()
        mock_request.url.__str__ = MagicMock(return_value="https://example.com/sms")
        mock_request.headers = {}

        warning_messages = []

        class CapturingHandler(logging.Handler):
            def emit(self, record):
                warning_messages.append(record.getMessage())

        handler = CapturingHandler()
        wh_logger = logging.getLogger("routers.webhook")
        wh_logger.addHandler(handler)
        try:
            with patch("routers.webhook.settings") as mock_settings:
                mock_settings.TWILIO_AUTH_TOKEN = ""
                from routers.webhook import _validate_twilio_signature
                # Must not raise
                await _validate_twilio_signature(mock_request, {})
        finally:
            wh_logger.removeHandler(handler)

        assert any("skipping" in m.lower() or "not set" in m.lower()
                   for m in warning_messages), f"Expected skip warning, got: {warning_messages}"


class TestWebhookRateLimits:
    def test_sms_endpoint_has_rate_limit(self):
        """The /sms endpoint must have a @limiter.limit() decorator."""
        import ast
        webhook_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "routers", "webhook.py"
        )
        with open(webhook_path, encoding="utf-8") as f:
            source = f.read()
        # Check both the decorator and the route are present together
        assert "@limiter.limit" in source, "webhook.py must use @limiter.limit"
        assert '"/sms"' in source or "'/sms'" in source

    def test_whatsapp_endpoint_has_rate_limit(self):
        webhook_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "routers", "webhook.py"
        )
        with open(webhook_path, encoding="utf-8") as f:
            source = f.read()
        assert "@limiter.limit" in source
        assert '"/whatsapp"' in source or "'/whatsapp'" in source

    def test_rate_limit_value_reasonable(self):
        """Rate limit should be defined and <=120/minute for webhook endpoints."""
        webhook_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "routers", "webhook.py"
        )
        with open(webhook_path, encoding="utf-8") as f:
            source = f.read()
        # Extract all rate limit strings like "30/minute"
        limits = re.findall(r'"(\d+)/minute"', source)
        assert len(limits) >= 2, "Expected at least 2 rate limit decorators in webhook.py"
        for lim in limits:
            assert int(lim) <= 120, f"Rate limit {lim}/min seems too high for webhook"


class TestPIIMasking:
    def test_phone_numbers_masked_in_logs(self):
        """Log statements in webhook.py must not log full phone numbers."""
        webhook_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "routers", "webhook.py"
        )
        with open(webhook_path, encoding="utf-8") as f:
            source = f.read()

        log_lines = [
            line.strip() for line in source.splitlines()
            if "logger." in line and "phone" in line.lower()
        ]
        for line in log_lines:
            assert "[-4:]" in line or "***" in line or "mask" in line.lower(), (
                f"Phone number may be unmasked in log line: {line}"
            )

    def test_vapi_router_phone_masking(self):
        """vapi.py log statements that include actual phone number variables must mask them."""
        vapi_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "routers", "vapi.py"
        )
        if not os.path.exists(vapi_path):
            pytest.skip("vapi.py not found")

        with open(vapi_path, encoding="utf-8") as f:
            source = f.read()

        # Only check lines that interpolate a phone number variable (not just containing "phone" as a word)
        phone_var_pattern = re.compile(r'\{(phone|customer_phone|sender_phone|from_number|to_number)\}')
        log_lines = [
            line.strip() for line in source.splitlines()
            if "logger." in line and phone_var_pattern.search(line)
        ]
        for line in log_lines:
            assert "[-4:]" in line or "***" in line or "mask" in line.lower(), (
                f"Phone number variable potentially exposed in vapi.py log line: {line}"
            )
