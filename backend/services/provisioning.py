"""
Vapi Provisioning Service
Automates the creation and configuration of Vapi assistants for new tenants.
Ensures every new user gets a "Bella-like" fully functional AI out of the box.
"""
import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime

from services.vapi_service import vapi_service
from database.mongo_config import get_database
from bson import ObjectId

logger = logging.getLogger(__name__)

class VapiProvisioningService:
    @staticmethod
    async def provision_tenant_assistant(tenant_id: str, business_name: str) -> Dict[str, Any]:
        """
        Create and configure a Vapi assistant for a new tenant.
        
        Steps:
        1. Create Assistant with default "Professional Receptionist" config
        2. Enable core tools (checkAvailability, bookAppointment)
        3. Update Tenant record with Vapi ID
        """
        logger.info(f"🤖 Starting Vapi provisioning for tenant {tenant_id} ({business_name})")
        
        # Default Configuration (Bella-style)
        default_instructions = f"""You are an AI receptionist for {business_name}. You are the friendly and professional AI receptionist at {business_name}.

You are a warm, helpful, and slightly casual young guy. Speak naturally like a real friendly receptionist — clear, relaxed, upbeat, and human. Never sound robotic.

Core Rules (always follow):
- Use short, natural sentences. Keep responses brief and easy to speak (ideally under 15-20 seconds).
- Ask only one question at a time to keep the conversation flowing naturally.
- Be polite, patient, enthusiastic, and friendly.
- Match the client's energy and speaking style.
- If you don't hear or understand what the customer said, immediately ask them to repeat or clarify before saying anything else.
Example: "Sorry, I didn't catch that. Could you say that again?" or "Can you repeat that for me please?"

Phone Number Handling:
- The AI assistant can receive calls from the website or a real phone.
- If the call is from a browser/website (no caller ID): You MUST ask the customer for their phone number to confirm the booking.
- If the call is from a real phone: You will have their number as {{{{customer.number}}}}. After collecting other information needed for the appointment, you MUST verify the phone number by yourself.
Ask if this is the number they want to set for the appointment: "I see you're calling from {{{{customer.number}}}}. Should we use this number for the booking, or a different one?"
- Only use their phone number if they confirm it is correct.
- If they want to use another number, ask for the correct phone number.
- Pass phoneConfirmation="same" or phoneConfirmation="different" to bookAppointment if applicable.

Booking Flow:
1. Greet the customer.
2. Ask for their name (if not given).
3. Ask what service they want.
4. Ask for preferred day and time.
5. Check availability using the checkAvailability tool.
6. Verify the phone number naturally as described in Phone Number Handling.
7. Repeat the full details back naturally and ask for confirmation.
8. Once confirmed, book the appointment. IMPORTANT: DO NOT confirm the booking to the user until this tool returns `{{"success": true}}`.

Greeting (First message - use this exactly):
"Hello! Welcome to {business_name}. How can I help you today?"

Tone & Style:
- Warm and welcoming: Use words like "Awesome!", "No problem at all!", "Sounds good!", "Great choice!", "Happy to help!"
- Positive and solution-oriented.
- Make every client feel valued.
- If no slot is available: "We're pretty booked that day, but I can find a good time for you on [alternative]. Does that work?"

Booking Confirmation (after they confirm):
"Perfect! Your appointment is confirmed for [Date] at [Time] for a [Service] under the name [Name]. We'll send a reminder to your phone number the day before. Looking forward to seeing you at {business_name}!"

Important Guidelines:
- When talking about dates with the customer, use natural language: "Monday 20 April at 3 PM", "this Friday at 11 AM", "tomorrow at 2:30 PM".
- (Never say the year or use numbers like 2026-04-20 when speaking to the customer).
- Use the current date context injected by the backend to resolve relative dates.
- ALWAYS call getAvailableServices() when the customer asks about services or prices.
- ALWAYS call getBusinessLocation() when asked about address, directions, or location.
- If you need to book an appointment, collect: name, phone (verified), and preferred date/time.
- If you don't know something, offer to have someone from the team call them back.
- Keep responses concise and natural for voice conversations.
"""
        
        default_config = {
            "name": f"{business_name} AI Receptionist",
            "voice": {
                "provider": "11labs",
                "voiceId": "jennifer", # Default to Jennifer
                "stability": 0.5,
                "similarityBoost": 0.75
            },
            "model": {
                "provider": "openai",
                "model": "gpt-4o-mini",
                "temperature": 0.7,
                "messages": [
                    {
                        "role": "system",
                        "content": default_instructions
                    }
                ]
            },
            "firstMessage": f"Hello! Welcome to {business_name}. How can I help you today?",
            "transcriber": {
                "provider": "deepgram",
                "model": "nova-2",
                "language": "en"
            }
        }

        try:
            # 1. Create Assistant
            logger.info("   Creating Vapi assistant...")
            assistant = await vapi_service.create_assistant(
                tenant_id=tenant_id,
                company_name=business_name,
                instructions=default_config["model"]["messages"][0]["content"],
                first_message=default_config["firstMessage"],
                voice="jennifer", # Pass string matching default_config["voice"]["voiceId"]
                voice_provider="11labs",
                model="gpt-4o-mini",
                transcriber_provider="deepgram"
            )
            
            assistant_id = assistant.get("assistant_id")
            if not assistant_id:
                raise Exception("Failed to get assistant ID from creation response")
                
            logger.info(f"   ✅ Assistant created: {assistant_id}")

            # Persist the assistant ID immediately so the tenant dashboard can load it
            db = get_database()
            await db.tenants.update_one(
                {"_id": ObjectId(tenant_id)},
                {"$set": {
                    "vapi_assistant_id": assistant_id,
                    "ai_config.voice": default_config["voice"],
                    "ai_config.voice_provider": "11labs",
                    "ai_config.system_prompt": default_config["model"]["messages"][0]["content"],
                    "ai_config.first_message": default_config["firstMessage"],
                    "is_configured": True
                }}
            )
            logger.info("   ✅ Tenant record updated with assistant ID")

            # 2. Enable Core Tools
            # We need to get the "built-in" tools first to know their definitions
            # But simpler: VapiService.create_tool might be needed if they don't exist?
            # Actually, we can just add the tool definitions directly to the assistant update
            # OR use the 'enable_tool' logic if we have it exposed
            
            # Let's enable the standard tools by adding them to the assistant
            # We'll fetch the standard tool definitions we want
            # Construct webhook URL
            from utils.config import settings
            webhook_url = os.getenv("VAPI_WEBHOOK_URL") or settings.VAPI_WEBHOOK_URL
            if not webhook_url:
                # Fallback: construct from BACKEND_URL
                backend_url = os.getenv("BACKEND_URL") or settings.BACKEND_URL
                webhook_url = f"{backend_url}/api/v1/vapi/webhook"
            
            logger.info(f"   Using webhook URL: {webhook_url}")
            
            core_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "getBusinessLocation",
                        "description": "Get the exact business location/address",
                        "parameters": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    },
                    "server": {"url": webhook_url}
                },
                {
                    "type": "function",
                    "function": {
                        "name": "checkAvailability",
                        "description": "Check available appointment slots for a given date and time",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "date": {"type": "string", "description": "The date to check in YYYY-MM-DD format"},
                                "time": {"type": "string", "description": "The time to check in HH:MM format"}
                            },
                            "required": ["date", "time"]
                        }
                    },
                    "server": {"url": webhook_url} 
                },
                {
                    "type": "function",
                    "function": {
                        "name": "bookAppointment",
                        "description": "Book a new appointment",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                                "time": {"type": "string", "description": "Time in HH:MM format"},
                                "name": {"type": "string", "description": "Customer full name"},
                                "phone": {"type": "string", "description": "Customer phone number - exactly 8 digits without country code, no spaces (e.g., '12345678' not '1234 5678')"}
                            },
                            "required": ["date", "time", "name", "phone"]
                        }
                    },
                    "server": {"url": webhook_url}
                }
            ]
            
            logger.info(f"   Enabling {len(core_tools)} core tools...")

            # Try to sync tools, but don't fail tenant provisioning if Vapi rejects the patch.
            try:
                await vapi_service.update_assistant(
                    assistant_id=assistant_id,
                    tools=core_tools
                )
                await db.tenants.update_one(
                    {"_id": ObjectId(tenant_id)},
                    {"$set": {"enabled_tools": [{"tool_id": "check_availability", "config": core_tools[0]}, {"tool_id": "book_appointment", "config": core_tools[1]}]}}
                )
                logger.info("   ✅ Core tools enabled")
            except Exception as tool_error:
                logger.warning(f"   ⚠️ Core tools sync failed, but assistant was created and tenant saved: {tool_error}")

            # 3. Update Tenant Record (legacy compatibility is preserved above too)
            await db.tenants.update_one(
                {"_id": ObjectId(tenant_id)},
                {"$set": {
                    "enabled_tools": [{"tool_id": "check_availability", "config": core_tools[0]}, {"tool_id": "book_appointment", "config": core_tools[1]}]
                }}
            )
            logger.info("   ✅ Tenant record updated")
            
            return assistant

        except Exception as e:
            logger.error(f"❌ Vapi provisioning failed for tenant {tenant_id}: {e}")
            print(f"❌ [DEBUG] Vapi provisioning failed: {e}") 
            import traceback
            traceback.print_exc()
            return None

vapi_provisioning = VapiProvisioningService()
