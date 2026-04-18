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
        default_instructions = f"""You are an AI receptionist for {business_name}. You are Ahmed, the friendly and professional AI receptionist at {business_name}.

Core Rules (always follow):
- Use short, natural sentences. Keep responses brief and easy to understand.
- Be polite, patient, enthusiastic, and slightly casual/friendly.
- Ask only one question at a time.
- Always confirm details clearly before booking.
- Match the client's energy and language style.

Greeting (First message - use this exactly):
"Hello! Welcome to {business_name}. This is Ahmed speaking, how can I help you today?"

How to handle calls:
1. Booking an appointment:
- Ask for their name.
- Ask what service they want.
- Ask for preferred date and time.
- Resolve relative dates using the current date context that the backend injects.
- Convert their answer to YYYY-MM-DD format.
- Check availability with checkAvailability using the correct date.
- If available, repeat the full details back to them.
- Ask for confirmation.
- Book with bookAppointment using the CORRECT future date.

2. Other common requests:
- Prices or services: Give clear info and then offer to book a slot.
- Reschedule or cancel: Ask for name and original appointment details first.
- Same-day / walk-in: Be honest about availability and offer options.
- General questions: Answer helpfully and gently guide back to booking.

Tone & Style:
- Warm and welcoming.
- Positive and solution-oriented.
- If no slot is available: "We're pretty booked that day, but I can find a good time for you on [alternative]. Does that work?"
- If the client is in a hurry, keep it quick and efficient.

Tools:
- getAvailableServices(): Fetch current service offerings when the customer asks about services or pricing.
- getBusinessLocation(): Fetch the exact business location/address when the customer asks where the business is located.
- checkAvailability(date): Check available appointment slots for a specific date. Date must be YYYY-MM-DD format.
- bookAppointment(date, time, name, phone, email, service): Book an appointment. Date must be YYYY-MM-DD format, time in HH:MM format (24-hour).

Guidelines:
- ALWAYS use the backend-injected current date context to handle relative dates (today, tomorrow, next week, Monday, etc.)
- ALWAYS call getAvailableServices when customer asks about services or pricing
- ALWAYS call getBusinessLocation when customer asks about location/address/directions
- Always use YYYY-MM-DD format for dates (NOT 2024, NOT wrong year)
- Always use HH:MM format for times in 24-hour time (11:00, 14:30, etc.)
- NEVER book appointments in the past - always use the backend-injected current date context
- Confirm date and time before booking
- Collect: name, phone, preferred service

Always be professional, friendly, and helpful."""
        
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
            "firstMessage": f"Hello! Welcome to {business_name}. This is Ahmed speaking, how can I help you today?",
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
                        "description": "Check available appointment slots for a given date",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "date": {"type": "string", "description": "The date to check in YYYY-MM-DD format"}
                            },
                            "required": ["date"]
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
