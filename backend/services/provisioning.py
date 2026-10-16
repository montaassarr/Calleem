"""
Vapi Provisioning Service
Automates the creation and configuration of Vapi assistants for new tenants.
Ensures every new user gets a "Bella-like" fully functional AI out of the box.
"""
import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime

from services import voice_languages
from services.vapi_service import vapi_service
from database.mongo_config import get_database
from bson import ObjectId

logger = logging.getLogger(__name__)

BOOKING_PHONE_DESCRIPTION = (
    "Customer phone number, digits only, including the country code if the customer gives one "
    "(e.g. '55123456', '4155550123' or '+14155550123')"
)
BOOKING_SERVICE_DESCRIPTION = "The service the customer wants to book"
BOOKING_TOOLS_MIGRATION = "booking_phone_any_country_v1"


async def update_booking_tools() -> None:
    """
    One-time update of existing assistants' bookAppointment tool: accept phone numbers from any
    country (it used to demand exactly 8 digits) and take the service. Runs at startup until every
    assistant was updated, then records itself in the `migrations` collection.
    """
    db = get_database()
    if not vapi_service.is_configured() or await db.migrations.find_one({"_id": BOOKING_TOOLS_MIGRATION}):
        return

    def fix(tools) -> bool:
        changed = False
        for tool in tools or []:
            tool = (tool or {}).get("config", tool) or {}
            function = tool.get("function") or {}
            if function.get("name") != "bookAppointment":
                continue
            properties = (function.get("parameters") or {}).setdefault("properties", {})
            if (properties.get("phone") or {}).get("description") != BOOKING_PHONE_DESCRIPTION:
                properties["phone"] = {"type": "string", "description": BOOKING_PHONE_DESCRIPTION}
                changed = True
            if "service" not in properties:
                properties["service"] = {"type": "string", "description": BOOKING_SERVICE_DESCRIPTION}
                changed = True
        return changed

    failures = 0
    tenants = await db.tenants.find(
        {"vapi_assistant_id": {"$nin": [None, ""]}}, {"vapi_assistant_id": 1, "enabled_tools": 1}
    ).to_list(5000)
    for tenant in tenants:
        assistant_id = tenant["vapi_assistant_id"]
        try:
            assistant = await vapi_service.get_assistant(assistant_id)
            model = (assistant or {}).get("model") or {}
            if fix(model.get("tools")):
                await vapi_service.patch_assistant(assistant_id, {"model": model})
                logger.info(f"Updated bookAppointment tool of assistant {assistant_id}")
            enabled_tools = tenant.get("enabled_tools") or []
            if fix(enabled_tools):
                await db.tenants.update_one({"_id": tenant["_id"]}, {"$set": {"enabled_tools": enabled_tools}})
        except Exception as e:
            failures += 1
            logger.error(f"Could not update the booking tool of assistant {assistant_id}: {e}")
    if not failures:
        await db.migrations.insert_one({"_id": BOOKING_TOOLS_MIGRATION, "done_at": datetime.utcnow(), "assistants": len(tenants)})


class VapiProvisioningService:
    @staticmethod
    async def provision_tenant_assistant(tenant_id: str, business_name: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Create and configure a Vapi assistant for a new tenant.
        
        Steps:
        1. Create Assistant with default "Professional Receptionist" config
        2. Enable core tools (checkAvailability, bookAppointment)
        3. Update Tenant record with Vapi ID

        language: "en" or "ar-TN" (services/voice_languages.py); defaults to the tenant's
        ai_config.language, else English.
        """
        logger.info(f"🤖 Starting Vapi provisioning for tenant {tenant_id} ({business_name})")

        if language is None:
            tenant = await get_database().tenants.find_one({"_id": ObjectId(tenant_id)}, {"ai_config.language": 1}) or {}
            language = (tenant.get("ai_config") or {}).get("language")
        language = voice_languages.normalize(language)
        
        # Default Configuration (Bella-style)
        default_instructions = voice_languages.default_instructions(language, business_name)
        
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
            "firstMessage": voice_languages.first_message(language, business_name),
            "transcriber": {
                "provider": "deepgram",
                "model": "nova-2",
                "language": "en"
            }
        }
        if language == voice_languages.TUNISIAN:
            default_config["voice"] = voice_languages.tunisian_voice()

        try:
            # 1. Create Assistant
            logger.info("   Creating Vapi assistant...")
            assistant = await vapi_service.create_assistant(
                tenant_id=tenant_id,
                company_name=business_name,
                instructions=default_config["model"]["messages"][0]["content"],
                first_message=default_config["firstMessage"],
                voice=default_config["voice"]["voiceId"], # "jennifer" for English
                voice_provider=default_config["voice"]["provider"],
                model="gpt-4o-mini",
                transcriber_provider="deepgram",
                language=language
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
                    "ai_config.voice_provider": default_config["voice"]["provider"],
                    "ai_config.language": language,
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
                                "phone": {"type": "string", "description": BOOKING_PHONE_DESCRIPTION},
                                "service": {"type": "string", "description": BOOKING_SERVICE_DESCRIPTION}
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
