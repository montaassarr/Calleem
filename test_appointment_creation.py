"""
Test appointment creation flow to verify the fix
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from ai.conversation_manager import conversation_manager
from database.mongo_config import connect_to_mongo, close_mongo_connection, get_database


async def test_booking_flow():
    """Test the complete booking flow"""
    
    print("=" * 60)
    print("Testing Appointment Creation Flow")
    print("=" * 60)
    
    # Connect to database
    await connect_to_mongo()
    db = get_database()
    
    # Test phone number
    test_phone = "+21692034689"
    
    # Clear any existing conversation for this test
    await db.conversations.delete_many({"phone_number": test_phone})
    
    print(f"\n📱 Testing with phone: {test_phone}")
    print("-" * 60)
    
    # Initialize conversation manager
    await conversation_manager.initialize()
    
    # Simulate the conversation
    messages = [
        ("hi", "Greeting"),
        ("hi", "Greeting again"),
        ("yes i want a haircut today, what the available time", "Request haircut"),
        ("Early evening, i'm montassar", "Provide name and time preference"),
        ("5", "Confirm 5 PM"),
        ("yes thank you", "Final confirmation")
    ]
    
    conversation_id = None
    
    for i, (message, description) in enumerate(messages, 1):
        print(f"\n{i}. Client: {message}")
        print(f"   Context: {description}")
        
        result = await conversation_manager.process_message(
            phone_number=test_phone,
            message_text=message
        )
        
        conversation_id = result.get("conversation_id")
        
        print(f"   Intent: {result.get('intent')}")
        print(f"   AI: {result.get('response')[:100]}...")
        
        # Check state
        state = result.get("state", {})
        collected_info = state.get("collected_info", {})
        
        if collected_info:
            print(f"   Collected: {collected_info}")
        
        if state.get("completed"):
            print("   ✅ Booking COMPLETED!")
    
    print("\n" + "=" * 60)
    print("Checking Database...")
    print("=" * 60)
    
    # Check if conversation has appointment_id
    conversation = await db.conversations.find_one({"conversation_id": conversation_id})
    
    print(f"\n📋 Conversation ID: {conversation_id}")
    print(f"   Appointment ID: {conversation.get('appointment_id')}")
    print(f"   Completed: {conversation['state'].get('completed')}")
    
    if conversation.get('appointment_id'):
        # Check if appointment exists in database
        from bson import ObjectId
        appointment = await db.appointments.find_one({"_id": ObjectId(conversation['appointment_id'])})
        
        if appointment:
            print(f"\n✅ SUCCESS! Appointment created in database:")
            print(f"   - Client: {appointment.get('client_name')}")
            print(f"   - Service: {appointment.get('service')}")
            print(f"   - DateTime: {appointment.get('datetime')}")
            print(f"   - Phone: {appointment.get('client_phone')}")
            print(f"   - Status: {appointment.get('status')}")
        else:
            print(f"\n❌ ERROR: Appointment ID exists in conversation but not found in database!")
    else:
        print(f"\n❌ ERROR: No appointment_id in conversation!")
        print(f"   This is the BUG we're fixing - appointment should have been created.")
    
    # Close connection
    await close_mongo_connection()
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(test_booking_flow())
