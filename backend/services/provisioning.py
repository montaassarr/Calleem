"""
Vapi Provisioning Service
Automates the creation and configuration of Vapi assistants for new tenants.
Ensures every new user gets a "Bella-like" fully functional AI out of the box.
"""
import logging
import os
from typing import Dict, Any, Optional

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
                        "content": f"""You are the AI Receptionist for {business_name}.
Your role is to answer calls professionally, check availability, and book appointments.

Services:
- General Consultation
- Service Inquiry

Hours: Mon-Fri 9AM-5PM

Always be polite, concise, and helpful. Ask for name and phone number before booking."""
                    }
                ]
            },
            "firstMessage": f"Hello! Thanks for calling {business_name}. How can I help you today?",
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
                                "date": {"type": "string", "description": "Date YYYY-MM-DD"},
                                "time": {"type": "string", "description": "Time HH:MM"},
                                "name": {"type": "string", "description": "Customer Full Name"},
                                "phone": {"type": "string", "description": "Customer Phone Number"}
                            },
                            "required": ["date", "time", "name", "phone"]
                        }
                    },
                    "server": {"url": webhook_url}
                }
            ]
            
            logger.info(f"   Enabling {len(core_tools)} core tools...")
            
            logger.info(f"   Enabling {len(core_tools)} core tools...")
            
            # Use update_assistant to set tools
            await vapi_service.update_assistant(
                assistant_id=assistant_id,
                tools=core_tools
            )
            
            logger.info("   ✅ Core tools enabled")

            # 3. Update Tenant Record
            db = get_database()
            await db.tenants.update_one(
                {"_id": ObjectId(tenant_id)},
                {"$set": {
                    "vapi_assistant_id": assistant_id,
                    "ai_config.voice": default_config["voice"],
                    "ai_config.voice_provider": "11labs",
                    "ai_config.system_prompt": default_config["model"]["messages"][0]["content"],
                    "ai_config.first_message": default_config["firstMessage"],
                    "enabled_tools": core_tools, # Persist enabled tools configuration
                    "is_configured": True
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
