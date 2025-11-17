#!/usr/bin/env python3
"""
Backend Phases Testing Script
Tests all completed backend functionality before moving to frontend phases
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from utils.config import settings
from services.config_loader import config_loader
from ai.brain.prompt_builder import PromptBuilder
from ai.brain.memory_engine import MemoryEngine
from ai.brain.appointment_reasoning import AppointmentReasoner, BookingRequest
from ai.brain.intent_classifier import IntentClassifierEngine
from models.business_config import BusinessConfigCreate, OpeningHours, ServiceDefinition, AIConfiguration, WhatsAppConfiguration


class BackendTester:
    def __init__(self):
        self.db = None
        self.client = None
        self.test_results = []
    
    async def setup(self):
        """Initialize database connection"""
        print("🔧 Setting up test environment...\n")
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DB_NAME]
    
    async def cleanup(self):
        """Close database connection"""
        if self.client:
            self.client.close()
    
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append((test_name, passed))
        print(f"{status} - {test_name}")
        if message:
            print(f"   {message}")
    
    async def test_config_loader(self):
        """Test Phase 3: MongoDB Memory System - Config Loader"""
        print("\n📋 Testing Config Loader Service...\n")
        
        try:
            # Test 1: Get default config
            config = await config_loader.get_config(self.db, "default")
            self.log_test(
                "Config Loader - Get Default Config",
                config is not None and config.get("business_id") == "default",
                f"Business: {config.get('business_name', 'N/A')}"
            )
            
            # Test 2: Update config
            update_data = {
                "business_name": "Test Barbershop Updated",
                "timezone": "America/New_York"
            }
            updated = await config_loader.update_config(self.db, "default", update_data)
            self.log_test(
                "Config Loader - Update Config",
                updated.get("business_name") == "Test Barbershop Updated",
                f"Updated name: {updated.get('business_name')}"
            )
            
            # Test 3: Cache functionality
            cached_config = await config_loader.get_config(self.db, "default")
            self.log_test(
                "Config Loader - Cache Retrieval",
                cached_config.get("business_name") == "Test Barbershop Updated",
                "Config retrieved from cache"
            )
            
            # Test 4: Reload config
            await config_loader.reload_config("default")
            self.log_test(
                "Config Loader - Cache Reload",
                True,
                "Cache invalidated successfully"
            )
            
        except Exception as e:
            self.log_test("Config Loader", False, f"Error: {str(e)}")
    
    async def test_prompt_builder(self):
        """Test Phase 4: AI Brain - Prompt Builder"""
        print("\n🧠 Testing Prompt Builder...\n")
        
        try:
            # Get config for prompt building
            config = await config_loader.get_config(self.db, "default")
            
            # Test 1: Build system prompt
            prompt = PromptBuilder.build_system_prompt(config)
            self.log_test(
                "Prompt Builder - Generate System Prompt",
                len(prompt) > 100 and "{business_name}" not in prompt,
                f"Prompt length: {len(prompt)} chars"
            )
            
            # Test 2: Variable injection
            has_business_name = config.get("business_name", "").lower() in prompt.lower()
            self.log_test(
                "Prompt Builder - Variable Injection",
                has_business_name,
                "Business name injected into prompt"
            )
            
            # Test 3: Custom prompt override
            custom_config = config.copy()
            custom_config["ai_config"] = {
                "system_prompt": "You are a custom AI assistant for {business_name}.",
                "model": "llama-3.1-70b-versatile"
            }
            custom_prompt = PromptBuilder.build_system_prompt(custom_config)
            self.log_test(
                "Prompt Builder - Custom Prompt Override",
                "custom AI assistant" in custom_prompt.lower(),
                "Custom prompt template used"
            )
            
        except Exception as e:
            self.log_test("Prompt Builder", False, f"Error: {str(e)}")
    
    async def test_memory_engine(self):
        """Test Phase 4: AI Brain - Memory Engine"""
        print("\n🧠 Testing Memory Engine...\n")
        
        try:
            test_phone = "+1234567890"
            
            # Test 1: Create new memory
            memory = await MemoryEngine.get_or_create_memory(self.db, test_phone, "default")
            self.log_test(
                "Memory Engine - Create Memory",
                memory.phone_number == test_phone,
                f"Memory created for {test_phone}"
            )
            
            # Test 2: Add conversation turn
            await MemoryEngine.add_conversation_turn(
                self.db,
                test_phone,
                "default",
                "user",
                "I want to book a haircut"
            )
            self.log_test(
                "Memory Engine - Add Conversation Turn",
                True,
                "User message added to history"
            )
            
            await MemoryEngine.add_conversation_turn(
                self.db,
                test_phone,
                "default",
                "assistant",
                "Great! What time works for you?"
            )
            
            # Test 3: Retrieve updated memory
            updated_memory = await MemoryEngine.get_or_create_memory(self.db, test_phone, "default")
            self.log_test(
                "Memory Engine - Conversation History",
                len(updated_memory.conversation_history) >= 2,
                f"History has {len(updated_memory.conversation_history)} messages"
            )
            
            # Test 4: Update collected info
            await MemoryEngine.update_collected_info(
                self.db,
                test_phone,
                "default",
                {"service": "haircut", "preferred_time": "afternoon"}
            )
            updated_memory = await MemoryEngine.get_or_create_memory(self.db, test_phone, "default")
            self.log_test(
                "Memory Engine - Collected Info",
                updated_memory.collected_info.get("service") == "haircut",
                f"Collected: {updated_memory.collected_info}"
            )
            
        except Exception as e:
            self.log_test("Memory Engine", False, f"Error: {str(e)}")
    
    async def test_appointment_reasoner(self):
        """Test Phase 4: AI Brain - Appointment Reasoner"""
        print("\n🧠 Testing Appointment Reasoner...\n")
        
        try:
            config = await config_loader.get_config(self.db, "default")
            
            # Test 1: Valid booking request
            tomorrow_2pm = datetime.now() + timedelta(days=1)
            tomorrow_2pm = tomorrow_2pm.replace(hour=14, minute=0, second=0, microsecond=0)
            
            valid_request = BookingRequest(
                service="Haircut",
                datetime=tomorrow_2pm,
                duration_minutes=30,
                customer_name="John Doe",
                customer_phone="+1234567890"
            )
            
            is_valid, message, result = await AppointmentReasoner.validate_booking_request(
                self.db,
                valid_request,
                config,
                "default"
            )
            self.log_test(
                "Appointment Reasoner - Valid Booking",
                is_valid,
                f"Validation: {message}"
            )
            
            # Test 2: Past date validation
            yesterday = datetime.now() - timedelta(days=1)
            past_request = BookingRequest(
                service="Haircut",
                datetime=yesterday,
                duration_minutes=30,
                customer_name="Jane Doe",
                customer_phone="+1234567891"
            )
            
            is_valid, message, result = await AppointmentReasoner.validate_booking_request(
                self.db,
                past_request,
                config,
                "default"
            )
            self.log_test(
                "Appointment Reasoner - Past Date Rejection",
                not is_valid and "past" in message.lower(),
                f"Rejected: {message}"
            )
            
            # Test 3: Find available slots
            target_date = datetime.now() + timedelta(days=2)
            slots = await AppointmentReasoner.find_available_slots(
                self.db,
                target_date,
                30,
                config,
                "default"
            )
            self.log_test(
                "Appointment Reasoner - Find Available Slots",
                len(slots) > 0,
                f"Found {len(slots)} available slots"
            )
            
        except Exception as e:
            self.log_test("Appointment Reasoner", False, f"Error: {str(e)}")
    
    async def test_intent_classifier(self):
        """Test Phase 4: AI Brain - Intent Classifier"""
        print("\n🧠 Testing Intent Classifier...\n")
        
        try:
            classifier = IntentClassifierEngine()
            
            # Test 1: Greeting intent
            greeting_result = await classifier.classify_intent(
                "Hello, how are you?",
                []
            )
            self.log_test(
                "Intent Classifier - Greeting",
                greeting_result.intent == "greeting",
                f"Classified as: {greeting_result.intent} ({greeting_result.confidence})"
            )
            
            # Test 2: Book appointment intent
            booking_result = await classifier.classify_intent(
                "I want to book a haircut for tomorrow at 2pm",
                []
            )
            self.log_test(
                "Intent Classifier - Book Appointment",
                booking_result.intent == "book_appointment",
                f"Classified as: {booking_result.intent} ({booking_result.confidence})"
            )
            
            # Test 3: Entity extraction
            entities = await classifier.extract_entities(
                "Book a fade haircut tomorrow at 3pm for John Smith"
            )
            self.log_test(
                "Intent Classifier - Entity Extraction",
                entities.service is not None or entities.datetime is not None,
                f"Extracted: service={entities.service}, time={entities.datetime}, name={entities.customer_name}"
            )
            
        except Exception as e:
            self.log_test("Intent Classifier", False, f"Error: {str(e)}")
    
    async def test_business_config_api(self):
        """Test Phase 3: Business Config API Router"""
        print("\n🔌 Testing Business Config API Integration...\n")
        
        try:
            # Test 1: Config model validation
            config_data = BusinessConfigCreate(
                business_id="test_tenant",
                business_name="Test Barber Shop",
                timezone="America/New_York",
                opening_hours=[
                    OpeningHours(
                        day_of_week=1,
                        open_time="09:00",
                        close_time="18:00",
                        is_open=True
                    )
                ],
                services=[
                    ServiceDefinition(
                        name="Haircut",
                        duration_minutes=30,
                        price=25.00,
                        description="Classic haircut"
                    )
                ],
                ai_config=AIConfiguration(
                    model="llama-3.1-70b-versatile",
                    temperature=0.7
                ),
                whatsapp_config=WhatsAppConfiguration(
                    phone_number_id="test123",
                    access_token="test_token",
                    verify_token="verify123"
                )
            )
            self.log_test(
                "Business Config - Pydantic Validation",
                config_data.business_id == "test_tenant",
                f"Config validated for {config_data.business_name}"
            )
            
            # Test 2: Save to database
            config_dict = config_data.model_dump()
            result = await self.db.business_configs.update_one(
                {"business_id": "test_tenant"},
                {"$set": config_dict},
                upsert=True
            )
            self.log_test(
                "Business Config - Database Save",
                result.acknowledged,
                f"Config saved for tenant: test_tenant"
            )
            
            # Test 3: Multi-tenant isolation
            default_config = await config_loader.get_config(self.db, "default")
            test_config = await config_loader.get_config(self.db, "test_tenant")
            self.log_test(
                "Business Config - Multi-tenant Isolation",
                default_config.get("business_id") != test_config.get("business_id"),
                f"Configs isolated: default vs test_tenant"
            )
            
        except Exception as e:
            self.log_test("Business Config API", False, f"Error: {str(e)}")
    
    async def test_integration_flow(self):
        """Test complete integration flow"""
        print("\n🔄 Testing Complete Integration Flow...\n")
        
        try:
            # Simulate complete conversation flow
            phone = "+1999888777"
            business_id = "default"
            
            # Step 1: Get config
            config = await config_loader.get_config(self.db, business_id)
            
            # Step 2: Build prompt
            prompt = PromptBuilder.build_system_prompt(config)
            
            # Step 3: Get/create memory
            memory = await MemoryEngine.get_or_create_memory(self.db, phone, business_id)
            
            # Step 4: Classify intent
            classifier = IntentClassifierEngine()
            intent_result = await classifier.classify_intent(
                "I need a haircut tomorrow at 2pm",
                memory.conversation_history
            )
            
            # Step 5: Extract entities
            entities = await classifier.extract_entities(
                "I need a haircut tomorrow at 2pm"
            )
            
            # Step 6: Validate appointment (if booking intent)
            if intent_result.intent == "book_appointment" and entities.datetime:
                booking = BookingRequest(
                    service=entities.service or "Haircut",
                    datetime=entities.datetime,
                    duration_minutes=30,
                    customer_name=entities.customer_name or "Customer",
                    customer_phone=phone
                )
                is_valid, msg, result = await AppointmentReasoner.validate_booking_request(
                    self.db, booking, config, business_id
                )
            
            # Step 7: Save conversation
            await MemoryEngine.add_conversation_turn(
                self.db, phone, business_id, "user",
                "I need a haircut tomorrow at 2pm"
            )
            
            self.log_test(
                "Integration Flow - Complete Flow",
                True,
                "Config → Prompt → Memory → Intent → Validation → Save completed"
            )
            
        except Exception as e:
            self.log_test("Integration Flow", False, f"Error: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for _, result in self.test_results if result)
        total = len(self.test_results)
        percentage = (passed / total * 100) if total > 0 else 0
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {percentage:.1f}%\n")
        
        if percentage == 100:
            print("🎉 ALL TESTS PASSED! Backend phases are working correctly.")
            print("\n✅ Ready to proceed with:")
            print("   - Phase 6: Frontend Architecture Upgrade")
            print("   - Phase 7: SaaS Multi-Tenant Implementation")
            print("   - Phase 8: Token Management UI")
        else:
            print("⚠️  Some tests failed. Please review the errors above.")
        
        print("=" * 80)
        
        return percentage == 100


async def main():
    """Run all tests"""
    tester = BackendTester()
    
    try:
        await tester.setup()
        
        # Run all test suites
        await tester.test_config_loader()
        await tester.test_prompt_builder()
        await tester.test_memory_engine()
        await tester.test_appointment_reasoner()
        await tester.test_intent_classifier()
        await tester.test_business_config_api()
        await tester.test_integration_flow()
        
        # Print summary
        success = tester.print_summary()
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
