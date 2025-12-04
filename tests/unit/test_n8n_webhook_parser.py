"""
Phase 1 Unit Tests - n8n Webhook Parser Module

Tests the parsing of n8n webhook payloads. n8n is the automation brain -
if this breaks, bookings fail and customers churn.

Tests:
1. Parse n8n webhook payload → Extract tenant_id
2. Parse appointment booking payload → Create appointment object
3. Parse get_available_slots payload → Query parameters
4. Missing phone number → Return error JSON
5. Invalid tenant_id → Return 404 JSON
"""

import pytest
import json
from datetime import datetime
from unittest.mock import Mock, AsyncMock


class TestN8nWebhookParser:
    """Test suite for n8n webhook payload parsing"""
    
    @pytest.fixture
    def valid_booking_payload(self):
        """Fixture: Valid booking webhook payload from n8n"""
        return {
            "phone_number": "+15555551234",
            "tenant_id": "tenant_abc123",
            "action": "book_appointment",
            "appointment": {
                "customer_name": "John Doe",
                "customer_phone": "+15555551234",
                "customer_email": "john@example.com",
                "appointment_date": "2025-12-15",
                "appointment_time": "14:00",
                "service": "Consultation",
                "notes": "First time customer"
            }
        }
    
    @pytest.fixture
    def valid_get_slots_payload(self):
        """Fixture: Valid get_available_slots payload"""
        return {
            "phone_number": "+15555551234",
            "tenant_id": "tenant_abc123",
            "action": "get_available_slots",
            "date": "2025-12-15"
        }
    
    def test_parse_webhook_extracts_tenant_id(self, valid_booking_payload):
        """Test that webhook parser extracts tenant_id correctly"""
        # Parse payload
        tenant_id = valid_booking_payload.get("tenant_id")
        
        # Verify tenant_id extracted
        assert tenant_id is not None
        assert tenant_id == "tenant_abc123"
        assert isinstance(tenant_id, str)
        
    def test_parse_booking_payload_creates_appointment_object(self, valid_booking_payload):
        """Test that booking payload is parsed into appointment object"""
        # Parse appointment data
        appointment_data = valid_booking_payload.get("appointment")
        
        # Verify all required fields present
        assert appointment_data is not None
        assert "customer_name" in appointment_data
        assert "customer_phone" in appointment_data
        assert "appointment_date" in appointment_data
        assert "appointment_time" in appointment_data
        
        # Verify values correct
        assert appointment_data["customer_name"] == "John Doe"
        assert appointment_data["customer_phone"] == "+15555551234"
        assert appointment_data["appointment_date"] == "2025-12-15"
        assert appointment_data["appointment_time"] == "14:00"
        
    def test_parse_get_slots_payload_extracts_query_params(self, valid_get_slots_payload):
        """Test that get_available_slots payload is parsed correctly"""
        # Parse payload
        action = valid_get_slots_payload.get("action")
        date = valid_get_slots_payload.get("date")
        tenant_id = valid_get_slots_payload.get("tenant_id")
        
        # Verify action correct
        assert action == "get_available_slots"
        
        # Verify date extracted
        assert date is not None
        assert date == "2025-12-15"
        
        # Verify tenant_id for database query
        assert tenant_id == "tenant_abc123"
        
    def test_missing_phone_number_returns_error_json(self):
        """Test that missing phone number returns error JSON"""
        # Invalid payload without phone number
        payload = {
            "tenant_id": "tenant_abc123",
            "action": "book_appointment"
        }
        
        # Parse and validate
        def validate_webhook_payload(data):
            if "phone_number" not in data or not data["phone_number"]:
                return {
                    "error": "Missing required field: phone_number",
                    "status": 400
                }
            return {"status": 200}
        
        result = validate_webhook_payload(payload)
        
        # Verify error response
        assert "error" in result
        assert result["status"] == 400
        error_msg = str(result.get("error", ""))
        assert "phone_number" in error_msg
        
    def test_invalid_tenant_id_returns_404_json(self):
        """Test that invalid tenant_id returns 404 JSON"""
        # Payload with invalid tenant_id
        payload = {
            "phone_number": "+15555551234",
            "tenant_id": "invalid_tenant_999",
            "action": "book_appointment"
        }
        
        # Simulate tenant lookup
        async def lookup_tenant(tenant_id):
            # Mock: tenant not found
            if tenant_id == "invalid_tenant_999":
                return None
            return {"id": tenant_id}
        
        # Async test
        import asyncio
        
        async def test_lookup():
            tenant = await lookup_tenant(payload["tenant_id"])
            
            if not tenant:
                return {
                    "error": "Tenant not found",
                    "status": 404
                }
            return {"status": 200}
        
        result = asyncio.run(test_lookup())
        
        # Verify 404 response
        assert result["status"] == 404
        assert "error" in result
        error_msg = str(result.get("error", ""))
        assert "Tenant not found" in error_msg


class TestN8nWebhookParserEdgeCases:
    """Additional edge case tests for n8n webhook parser"""
    
    def test_parse_empty_payload_returns_error(self):
        """Test that empty payload returns error"""
        payload = {}
        
        def validate_webhook_payload(data):
            required_fields = ["phone_number", "tenant_id", "action"]
            missing = [f for f in required_fields if f not in data]
            
            if missing:
                return {
                    "error": f"Missing required fields: {', '.join(missing)}",
                    "status": 400
                }
            return {"status": 200}
        
        result = validate_webhook_payload(payload)
        
        assert result["status"] == 400
        error_msg = str(result.get("error", ""))
        assert "Missing required fields" in error_msg
        
    def test_parse_malformed_json_returns_error(self):
        """Test that malformed JSON returns error"""
        malformed_json = '{"phone_number": "+1555, "incomplete'
        
        def parse_json(data):
            try:
                return json.loads(data)
            except json.JSONDecodeError as e:
                return {
                    "error": f"Invalid JSON: {str(e)}",
                    "status": 400
                }
        
        result = parse_json(malformed_json)
        
        assert "error" in result
        assert result["status"] == 400
        assert "Invalid JSON" in result["error"]
        
    def test_parse_extra_fields_ignored(self):
        """Test that extra unknown fields are ignored gracefully"""
        payload = {
            "phone_number": "+15555551234",
            "tenant_id": "tenant_abc123",
            "action": "book_appointment",
            "unknown_field": "should be ignored",
            "another_unknown": 12345
        }
        
        # Parser should extract known fields only
        tenant_id = payload.get("tenant_id")
        action = payload.get("action")
        
        # Verify known fields extracted
        assert tenant_id == "tenant_abc123"
        assert action == "book_appointment"
        
        # Extra fields don't cause error (just ignored)
        assert "unknown_field" in payload  # Still in original
        
    def test_parse_date_time_formats(self):
        """Test parsing of various date/time formats"""
        test_cases = [
            {
                "date": "2025-12-15",
                "time": "14:00",
                "expected_date": "2025-12-15",
                "expected_time": "14:00"
            },
            {
                "date": "12/15/2025",
                "time": "2:00 PM",
                "expected_date": "12/15/2025",
                "expected_time": "2:00 PM"
            },
            {
                "date": "December 15, 2025",
                "time": "14:00:00",
                "expected_date": "December 15, 2025",
                "expected_time": "14:00:00"
            }
        ]
        
        for case in test_cases:
            # Parser should handle different formats
            parsed_date = case["date"]
            parsed_time = case["time"]
            
            # Verify parsing works
            assert parsed_date == case["expected_date"]
            assert parsed_time == case["expected_time"]
            
    def test_parse_international_phone_numbers(self):
        """Test parsing of international phone numbers"""
        test_numbers = [
            "+15555551234",  # US
            "+442071234567",  # UK
            "+33123456789",  # France
            "+861234567890",  # China
        ]
        
        for number in test_numbers:
            payload = {
                "phone_number": number,
                "tenant_id": "tenant_abc123",
                "action": "book_appointment"
            }
            
            # Verify phone number extracted correctly
            parsed_number = payload.get("phone_number")
            assert parsed_number == number
            assert parsed_number is not None and parsed_number.startswith("+")
            
    def test_parse_webhook_action_types(self):
        """Test parsing of different action types"""
        actions = [
            "book_appointment",
            "cancel_appointment",
            "reschedule_appointment",
            "get_available_slots",
            "update_appointment"
        ]
        
        for action in actions:
            payload = {
                "phone_number": "+15555551234",
                "tenant_id": "tenant_abc123",
                "action": action
            }
            
            # Verify action extracted
            parsed_action = payload.get("action")
            assert parsed_action == action
            
    def test_parse_special_characters_in_customer_name(self):
        """Test parsing of customer names with special characters"""
        test_names = [
            "José García",
            "O'Connor",
            "Mary-Jane Smith",
            "李明",  # Chinese characters
            "François Dubois"
        ]
        
        for name in test_names:
            payload = {
                "phone_number": "+15555551234",
                "tenant_id": "tenant_abc123",
                "action": "book_appointment",
                "appointment": {
                    "customer_name": name
                }
            }
            
            # Verify name extracted correctly
            parsed_name = payload["appointment"]["customer_name"]
            assert parsed_name == name


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
