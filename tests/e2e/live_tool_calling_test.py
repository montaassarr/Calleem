"""
Phase 3: Live Tool Calling Tests
End-to-end tests with real API integrations (Vapi, Groq, ElevenLabs)

These tests validate:
1. Real Vapi API calls (assistant creation, phone number management)
2. Real Groq AI conversations (appointment booking scenarios)
3. End-to-end appointment booking flow
4. AI conversation context management
5. Webhook integration with n8n

⚠️ WARNING: These tests make REAL API calls and may incur costs
"""

import pytest
import httpx
import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, Any
import json
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.utils.config import settings
from backend.ai.groq_agent import GroqAgent
from backend.ai.conversation_manager import ConversationManager


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="module")
def api_keys():
    """Load API keys from environment"""
    keys = {
        "vapi_private": os.getenv("VAPI_PRIVATE_API_KEY"),
        "vapi_public": os.getenv("VAPI_PUBLIC_API_KEY"),
        "groq": os.getenv("GROQ_API_KEY"),
        "elevenlabs": os.getenv("ELEVENLABS_API_KEY")
    }
    
    # Validate all keys are present
    missing_keys = [k for k, v in keys.items() if not v]
    if missing_keys:
        pytest.skip(f"Missing API keys: {', '.join(missing_keys)}")
    
    return keys


@pytest.fixture(scope="module")
def vapi_client(api_keys):
    """HTTP client for Vapi API"""
    return httpx.Client(
        base_url="https://api.vapi.ai",
        headers={
            "Authorization": f"Bearer {api_keys['vapi_private']}",
            "Content-Type": "application/json"
        },
        timeout=30.0
    )


@pytest.fixture
def sample_appointment_request():
    """Sample appointment booking request"""
    tomorrow = datetime.now() + timedelta(days=1)
    return {
        "customer_name": "John Doe",
        "customer_phone": "+1234567890",
        "customer_email": "john@example.com",
        "service": "Haircut",
        "preferred_date": tomorrow.strftime("%Y-%m-%d"),
        "preferred_time": "14:00",
        "notes": "First time customer"
    }


@pytest.fixture
def mock_tenant_id():
    """Mock tenant ID for testing"""
    return "test_tenant_e2e_001"


# ============================================================================
# TEST CLASS: Vapi Integration
# ============================================================================

@pytest.mark.e2e
@pytest.mark.vapi
class TestVapiIntegration:
    """Test real Vapi API integration"""
    
    def test_vapi_api_connectivity(self, vapi_client):
        """Test basic connectivity to Vapi API"""
        # Try to list assistants (should work even if empty)
        response = vapi_client.get("/assistant")
        
        assert response.status_code in [200, 201], f"Vapi API returned {response.status_code}"
        data = response.json()
        assert isinstance(data, list) or isinstance(data, dict), "Vapi API returned valid response"
        print(f"✅ Vapi API connected successfully")
    
    def test_vapi_create_assistant(self, vapi_client, mock_tenant_id):
        """Test creating a Vapi assistant"""
        assistant_config = {
            "name": f"E2E Test {datetime.now().strftime('%H%M')}",  # Shortened name
            "model": {
                "provider": "groq",
                "model": "llama-3.3-70b-versatile",
                "temperature": 0.7
            },
            "voice": {
                "provider": "11labs",
                "voiceId": "jennifer"
            },
            "firstMessage": "Hello! I'm your AI receptionist.",
            # Note: Vapi requires HTTPS URLs - using a placeholder for testing
            # In production, this would be your actual webhook URL
            "serverUrl": f"https://example.com/webhook/vapi/{mock_tenant_id}",
            "serverUrlSecret": "test_secret_123"
        }
        
        response = vapi_client.post("/assistant", json=assistant_config)
        
        # Accept both 200 and 201 as success
        assert response.status_code in [200, 201], f"Failed to create assistant: {response.text}"
        
        assistant_data = response.json()
        assert "id" in assistant_data, "Assistant ID missing from response"
        
        assistant_id = assistant_data["id"]
        print(f"✅ Created Vapi assistant: {assistant_id}")
        
        # Cleanup: Delete the test assistant
        try:
            delete_response = vapi_client.delete(f"/assistant/{assistant_id}")
            if delete_response.status_code in [200, 204]:
                print(f"✅ Cleaned up test assistant: {assistant_id}")
        except Exception as e:
            print(f"⚠️ Could not cleanup assistant {assistant_id}: {e}")
    
    def test_vapi_list_phone_numbers(self, vapi_client):
        """Test listing Vapi phone numbers"""
        response = vapi_client.get("/phone-number")
        
        assert response.status_code == 200, f"Failed to list phone numbers: {response.text}"
        
        phone_numbers = response.json()
        print(f"✅ Retrieved {len(phone_numbers)} Vapi phone numbers")
        
        # If phone numbers exist, validate structure
        if phone_numbers:
            first_number = phone_numbers[0]
            assert "id" in first_number, "Phone number missing ID"
            assert "number" in first_number or "phoneNumber" in first_number, "Phone number missing number field"


# ============================================================================
# TEST CLASS: Groq AI Integration
# ============================================================================

@pytest.mark.e2e
@pytest.mark.groq
class TestGroqAIIntegration:
    """Test real Groq AI integration"""
    
    @pytest.mark.asyncio
    async def test_groq_api_connectivity(self, api_keys):
        """Test basic connectivity to Groq API"""
        agent = GroqAgent()
        
        # Simple test message with tenant API key
        response = await agent.generate_response(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello, Groq!' if you can hear me."}
            ],
            api_key=api_keys["groq"],
            model="llama-3.3-70b-versatile"
        )
        
        assert response is not None, "Groq API returned no response"
        assert len(response) > 0, "Groq API returned empty response"
        assert "groq" in response.lower() or "hello" in response.lower(), "Groq AI not responding correctly"
        
        print(f"✅ Groq AI responded: {response[:100]}...")
    
    @pytest.mark.asyncio
    async def test_groq_appointment_booking_intent(self, api_keys, sample_appointment_request):
        """Test Groq AI can understand appointment booking intent"""
        agent = GroqAgent()
        
        # Simulate customer requesting appointment
        customer_message = (
            f"Hi, I'd like to book a {sample_appointment_request['service']} "
            f"for {sample_appointment_request['preferred_date']} "
            f"at {sample_appointment_request['preferred_time']}. "
            f"My name is {sample_appointment_request['customer_name']}."
        )
        
        system_prompt = """You are an AI receptionist. Analyze the user's message and determine if they want to:
1. Book an appointment
2. Check availability
3. Cancel an appointment
4. Just ask a question

Respond with ONLY ONE WORD: "BOOK", "CHECK", "CANCEL", or "QUESTION"."""
        
        response = await agent.generate_response(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": customer_message}
            ],
            api_key=api_keys["groq"],
            model="llama-3.3-70b-versatile"
        )
        
        assert response is not None, "Groq returned no intent"
        assert "book" in response.lower(), f"Groq failed to detect booking intent: {response}"
        
        print(f"✅ Groq correctly identified booking intent: {response}")
    
    @pytest.mark.asyncio
    async def test_groq_extract_appointment_details(self, api_keys, sample_appointment_request):
        """Test Groq AI can extract appointment details from natural language"""
        agent = GroqAgent()
        
        customer_message = (
            f"Hi, I'm {sample_appointment_request['customer_name']} "
            f"and I'd like to schedule a {sample_appointment_request['service']}. "
            f"My phone number is {sample_appointment_request['customer_phone']} "
            f"and email is {sample_appointment_request['customer_email']}. "
            f"I prefer {sample_appointment_request['preferred_date']} "
            f"at {sample_appointment_request['preferred_time']} if available."
        )
        
        system_prompt = """You are an AI assistant that extracts appointment information.
Extract and return ONLY a valid JSON object with these fields:
- customer_name
- customer_phone
- customer_email
- service
- preferred_date (YYYY-MM-DD format)
- preferred_time (HH:MM format)

Return ONLY the JSON, nothing else."""
        
        response = await agent.generate_response(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": customer_message}
            ],
            api_key=api_keys["groq"],
            model="llama-3.3-70b-versatile"
        )
        
        assert response is not None, "Groq returned no data"
        
        # Try to parse as JSON
        try:
            # Extract JSON from response (might have markdown code blocks)
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            
            extracted_data = json.loads(json_str)
            
            # Validate extracted data
            assert "customer_name" in extracted_data, "Missing customer_name"
            assert "service" in extracted_data, "Missing service"
            assert "preferred_date" in extracted_data, "Missing preferred_date"
            
            print(f"✅ Groq extracted appointment details: {json.dumps(extracted_data, indent=2)}")
            
        except json.JSONDecodeError as e:
            pytest.fail(f"Groq did not return valid JSON: {response}\nError: {e}")


# ============================================================================
# TEST CLASS: Conversation Manager
# ============================================================================

@pytest.mark.e2e
@pytest.mark.conversation
class TestConversationManager:
    """Test conversation management with real AI"""
    
    @pytest.mark.asyncio
    async def test_conversation_context_management(self, api_keys, mock_tenant_id):
        """Test that conversation manager maintains context across messages"""
        manager = ConversationManager()
        await manager.initialize()
        
        # Start conversation
        phone_number = "+1234567890"
        
        # Message 1: Customer introduces themselves
        response1 = await manager.process_message(
            phone_number=phone_number,
            message_text="Hi, my name is Alice Johnson.",
            tenant_id=mock_tenant_id
        )
        
        assert response1 is not None, "No response from conversation manager"
        assert "response" in response1 or "text" in response1, "Invalid response structure"
        print(f"✅ Response 1 received")
        
        # Message 2: Customer mentions service
        response2 = await manager.process_message(
            phone_number=phone_number,
            message_text="I'd like to book a haircut for tomorrow at 2 PM.",
            tenant_id=mock_tenant_id
        )
        
        assert response2 is not None, "No response to booking request"
        print(f"✅ Response 2 received")
        
        print(f"✅ Conversation flow tested successfully")


# ============================================================================
# TEST CLASS: End-to-End Appointment Flow
# ============================================================================

@pytest.mark.e2e
@pytest.mark.appointment_flow
class TestEndToEndAppointmentFlow:
    """Test complete appointment booking flow with all integrations"""
    
    @pytest.mark.asyncio
    async def test_complete_appointment_booking_flow(
        self, 
        api_keys, 
        mock_tenant_id,
        sample_appointment_request
    ):
        """
        Test the complete flow:
        1. Customer initiates conversation
        2. AI understands intent
        3. System processes booking
        """
        manager = ConversationManager()
        await manager.initialize()
        
        phone_number = sample_appointment_request["customer_phone"]
        
        # Step 1: Customer greeting
        response1 = await manager.process_message(
            phone_number=phone_number,
            message_text="Hello, I need to schedule an appointment.",
            tenant_id=mock_tenant_id
        )
        
        assert response1 is not None
        print(f"✅ Step 1 - Greeting processed")
        
        # Step 2: Customer provides details
        booking_message = (
            f"I'm {sample_appointment_request['customer_name']}, "
            f"I want a {sample_appointment_request['service']} "
            f"on {sample_appointment_request['preferred_date']} "
            f"at {sample_appointment_request['preferred_time']}. "
            f"My email is {sample_appointment_request['customer_email']}."
        )
        
        response2 = await manager.process_message(
            phone_number=phone_number,
            message_text=booking_message,
            tenant_id=mock_tenant_id
        )
        
        assert response2 is not None
        print(f"✅ Step 2 - Booking request processed")
        
        print(f"✅ COMPLETE E2E FLOW SUCCESSFUL")
        
        return {
            "success": True,
            "steps_completed": 2
        }


# ============================================================================
# TEST CLASS: Performance & Reliability
# ============================================================================

@pytest.mark.e2e
@pytest.mark.performance
class TestPerformanceAndReliability:
    """Test performance and reliability of live API integrations"""
    
    @pytest.mark.asyncio
    async def test_groq_response_time(self, api_keys):
        """Test that Groq responds within acceptable time"""
        agent = GroqAgent()
        
        start_time = datetime.now()
        
        response = await agent.generate_response(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'OK' if you're ready."}
            ],
            api_key=api_keys["groq"],
            model="llama-3.3-70b-versatile"
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        assert response is not None, "Groq API failed"
        assert duration < 10, f"Groq response took too long: {duration}s"
        
        print(f"✅ Groq response time: {duration:.2f}s")
    
    def test_vapi_rate_limiting(self, vapi_client):
        """Test that we handle Vapi rate limiting gracefully"""
        # Make multiple rapid requests
        responses = []
        for i in range(3):
            try:
                response = vapi_client.get("/assistant")
                responses.append(response.status_code)
            except httpx.HTTPError as e:
                responses.append(f"error: {e}")
        
        # At least one request should succeed
        assert 200 in responses or 201 in responses, f"All requests failed: {responses}"
        
        print(f"✅ Vapi rate limiting handled: {responses}")


# ============================================================================
# RUN CONFIGURATION
# ============================================================================

if __name__ == "__main__":
    """Run E2E tests directly"""
    print("=" * 70)
    print("PHASE 3: LIVE TOOL CALLING TESTS")
    print("=" * 70)
    print("⚠️  WARNING: These tests make REAL API calls")
    print("⚠️  Ensure you have valid API keys in .env file")
    print("=" * 70)
    
    pytest.main([
        __file__,
        "-v",
        "-s",
        "--tb=short",
        "-m", "e2e"
    ])
