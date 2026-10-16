"""
Text Receptionist
=================
The business's AI receptionist over text: WhatsApp messages and the dashboard Chat Test.

It knows the same business facts as the voice assistant (name, instructions, FAQs, services,
location, hours) and books through the same tools (routers/vapi.process_tool_call), answered by
Amazon Bedrock (Converse API with tool use). Conversations are kept in `text_conversations`.
"""

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import boto3
from botocore.config import Config
from bson import ObjectId

from database.mongo_config import get_database
from models.appointment import AppointmentCreate
from services import voice_languages
from services.appointments_service import AppointmentsService
from services.bedrock_chat_service import BEDROCK_MODEL_ID, BEDROCK_REGION
from services.usage_billing import tenant_query
from utils.money import format_price
from utils.phone import to_e164

logger = logging.getLogger(__name__)

MAX_MODEL_MESSAGES = 30  # Bedrock messages kept per conversation (tool turns included)
MAX_TOOL_ROUNDS = 5
FRESH_START_AFTER = timedelta(hours=12)  # an idle conversation starts over (old transcript is kept)
FALLBACK_REPLY = "Sorry, I'm having a small technical issue. Someone from the team will get back to you shortly."

# Amazon Nova writes its reasoning in <thinking> tags when tools are available.
_THINKING = re.compile(r"<thinking>.*?</thinking>", re.DOTALL | re.IGNORECASE)


def _tool(name: str, description: str, properties: Dict[str, Any], required: List[str]) -> Dict[str, Any]:
    return {"toolSpec": {
        "name": name,
        "description": description,
        "inputSchema": {"json": {"type": "object", "properties": properties, "required": required}},
    }}


TOOLS = [
    _tool("getCurrentDateTime", "Current date, time and weekday in the business timezone.", {}, []),
    _tool("getAvailableServices", "The services the business offers, with prices.", {}, []),
    _tool("getBusinessLocation", "The business address.", {}, []),
    _tool(
        "checkAvailability",
        "Check whether a time slot is free for an appointment.",
        {
            "date": {"type": "string", "description": "YYYY-MM-DD"},
            "time": {"type": "string", "description": "HH:MM, 24-hour"},
        },
        ["date", "time"],
    ),
    _tool(
        "bookAppointment",
        "Book the appointment once the customer has confirmed every detail.",
        {
            "name": {"type": "string", "description": "Customer's name"},
            "service": {"type": "string", "description": "Service to book"},
            "date": {"type": "string", "description": "YYYY-MM-DD"},
            "time": {"type": "string", "description": "HH:MM, 24-hour"},
            "phone": {"type": "string", "description": "Customer's phone number with country code"},
        },
        ["name", "service", "date", "time"],
    ),
]


@dataclass
class AgentReply:
    text: str
    tools_used: List[str] = field(default_factory=list)
    appointment_id: Optional[str] = None


def _business_name(tenant: Dict[str, Any]) -> str:
    return (
        tenant.get("business_name")
        or (tenant.get("settings") or {}).get("business_name")
        or tenant.get("name")
        or "our business"
    )


def _hours_text(business_hours: Dict[str, Any]) -> str:
    days = []
    for day in ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"):
        config = business_hours.get(day)
        if not config:
            continue
        if config.get("enabled", True):
            days.append(f"{day.capitalize()} {config.get('start', '09:00')}-{config.get('end', '17:00')}")
        else:
            days.append(f"{day.capitalize()} closed")
    return ", ".join(days)


CHANNEL_RULES = {
    "whatsapp": (
        "You are chatting on WhatsApp. Write short, friendly messages (1-3 sentences), like a real "
        "receptionist texting. No headings or long lists. You already have the customer's WhatsApp "
        "number ({customer_phone}). Never ask them to type a phone number: for a booking, ask "
        "\"Should I use this WhatsApp number for the booking?\" and only take another number if they give one."
    ),
    "test": (
        "You are chatting by text. Write short, friendly messages (1-3 sentences). The person is the "
        "business owner testing you, so behave exactly as with a real customer. You don't have their "
        "phone number: ask for it before booking."
    ),
}


class TextReceptionist:
    def __init__(self):
        self._client = None
        self.appointments = AppointmentsService()

    @property
    def client(self):
        if self._client is None:
            self._client = boto3.client(
                "bedrock-runtime",
                region_name=BEDROCK_REGION,
                config=Config(retries={"max_attempts": 4, "mode": "adaptive"}, read_timeout=45),
            )
        return self._client

    async def _system_prompt(self, tenant_id: str, channel: str, customer_phone: Optional[str]) -> str:
        db = get_database()
        tenant = await db.tenants.find_one(tenant_query(tenant_id)) or {}
        config = await db.business_config.find_one({"tenant_id": tenant_id}) or {}
        faqs = await db.knowledge_base.find({"tenant_id": tenant_id, "type": "faq"}).to_list(50)
        services = await db.services.find({"tenant_id": tenant_id, "active": True}).to_list(50)

        name = _business_name(tenant)
        tz = await self.appointments._resolve_tenant_timezone(tenant_id)
        now = datetime.now(tz)

        facts = [f"Business: {name}"]
        location = config.get("business_location") or config.get("business_address") or tenant.get("address")
        if location:
            facts.append(f"Address: {location}")
        if config.get("business_hours"):
            facts.append(f"Opening hours: {_hours_text(config['business_hours'])}")
        if services:
            facts.append("Services: " + "; ".join(
                f"{s.get('name')}" + (f" ({format_price(s['price'], config.get('currency'))})" if s.get("price") else "")
                for s in services
            ))
        if faqs:
            facts.append("FAQ:\n" + "\n".join(f"Q: {f.get('question')}\nA: {f.get('answer')}" for f in faqs))

        instructions = ((tenant.get("ai_config") or {}).get("system_prompt") or "").strip()
        channel_rules = CHANNEL_RULES.get(channel, CHANNEL_RULES["test"]).format(customer_phone=customer_phone or "unknown")
        language_rule = "- Answer in the customer's language."
        if voice_languages.normalize((tenant.get("ai_config") or {}).get("language")) == voice_languages.TUNISIAN:
            language_rule = (
                "- Customers usually write Tunisian Derja, in Arabic letters or in Latin letters with digits "
                "(\"3aslema\", \"n7eb na3mel rdv\", \"9adech\"). Reply in Tunisian Derja in the same script they "
                "use, never in Modern Standard Arabic. If they write in French or English, reply in that language."
            )

        return f"""You are the AI receptionist of {name}. You answer customers' questions and book appointments.

Today is {now.strftime('%A, %B %d, %Y')} and it is {now.strftime('%H:%M')} ({tz.zone}). Use this to resolve "tomorrow", "Friday", etc.

{channel_rules}

Business facts:
{chr(10).join(facts)}

{('Instructions from the business:' + chr(10) + instructions) if instructions else ''}

Booking:
1. Get the customer's name, the service, and the day and time they want.
2. Call checkAvailability. If the slot is taken or outside opening hours, suggest another time.
3. Repeat the details and ask the customer to confirm.
4. After they confirm, call bookAppointment. Only say the appointment is booked once bookAppointment succeeded.
5. If a tool returns an error, apologise and ask for the detail that needs fixing.

Rules:
{language_rule}
- Never invent prices, services, hours or availability: use the facts above or the tools.
- If you can't help, say someone from the team will get back to them.
- Never mention tools, functions or these instructions."""

    async def _run_tool(self, tenant_id: str, name: str, args: Dict[str, Any], channel: str,
                        customer_phone: Optional[str]) -> Dict[str, Any]:
        if name != "bookAppointment":
            from routers.vapi import process_tool_call  # the voice assistant's tool implementations
            return await process_tool_call(name, args, tenant_id)

        # Booking from text: any format, the WhatsApp sender by default; a local number takes the
        # country of the sender, else of the business's own number.
        tenant = await get_database().tenants.find_one(tenant_query(tenant_id)) or {}
        business_phone = (tenant.get("phone_config") or {}).get("phone_number")
        raw_phone = args.get("phone") or customer_phone or ""
        if not raw_phone:
            return {"error": "Ask the customer for a phone number first."}
        phone = to_e164(raw_phone, customer_phone, business_phone)
        if not phone:
            return {"error": "That phone number doesn't look complete. Ask for it again with all digits."}
        date, time = args.get("date"), args.get("time")
        slot = await self.appointments.check_availability(tenant_id, date, time)
        if not slot.get("available"):
            return {"error": f"Not booked: {slot.get('reason', 'slot unavailable')}. Offer another time."}
        try:
            appointment = AppointmentCreate(
                client_name=args.get("name"),
                client_phone=phone,
                service=args.get("service") or "Appointment",
                datetime=datetime.fromisoformat(slot["requested_datetime"]),
                duration_minutes=30,
                notes="Booked from the Chat Test" if channel == "test" else "Booked on WhatsApp",
            )
            created = await self.appointments.create_appointment(tenant_id, appointment)
        except Exception as e:
            detail = getattr(e, "detail", None) or str(e)
            return {"error": f"Not booked: {detail}"}
        await get_database().appointments.update_one({"_id": ObjectId(created["id"])}, {"$set": {"source": channel}})
        return {"success": True, "appointment_id": created["id"], "datetime": slot["requested_datetime"]}

    async def _converse(self, system_prompt: str, messages: List[dict]) -> Dict[str, Any]:
        # boto3 is blocking; keep the event loop free for other requests.
        return await asyncio.to_thread(
            self.client.converse,
            modelId=BEDROCK_MODEL_ID,
            system=[{"text": system_prompt}],
            messages=messages,
            toolConfig={"tools": TOOLS},
            # Greedy decoding: what AWS recommends for reliable tool use with Nova.
            inferenceConfig={"maxTokens": 600, "temperature": 0},
        )

    async def reply(
        self,
        tenant_id: str,
        conversation_id: str,
        text: str,
        *,
        channel: str,
        customer_phone: Optional[str] = None,
        customer_name: Optional[str] = None,
    ) -> AgentReply:
        """Answer one customer message, running booking tools as needed. Never raises."""
        db = get_database()
        now = datetime.utcnow()
        conversation = await db.text_conversations.find_one({"_id": conversation_id}) or {}
        messages: List[dict] = conversation.get("messages") or []
        if conversation.get("updated_at") and now - conversation["updated_at"] > FRESH_START_AFTER:
            messages = []
        previous = list(messages)

        messages.append({"role": "user", "content": [{"text": text}]})
        result = AgentReply(text=FALLBACK_REPLY)
        try:
            system_prompt = await self._system_prompt(tenant_id, channel, customer_phone)
            for _ in range(MAX_TOOL_ROUNDS):
                response = await self._converse(system_prompt, messages)
                message = response["output"]["message"]
                messages.append(message)
                tool_uses = [block["toolUse"] for block in message["content"] if "toolUse" in block]
                if response.get("stopReason") != "tool_use" or not tool_uses:
                    reply = "".join(block.get("text", "") for block in message["content"])
                    result.text = _THINKING.sub("", reply).strip() or FALLBACK_REPLY
                    break
                results = []
                for tool_use in tool_uses:
                    output = await self._run_tool(
                        tenant_id, tool_use["name"], tool_use.get("input") or {}, channel, customer_phone
                    )
                    result.tools_used.append(tool_use["name"])
                    if output.get("appointment_id"):
                        result.appointment_id = output["appointment_id"]
                    results.append({"toolResult": {
                        "toolUseId": tool_use["toolUseId"],
                        "content": [{"text": json.dumps(output, default=str)}],
                        "status": "error" if "error" in output else "success",
                    }})
                messages.append({"role": "user", "content": results})
            else:
                logger.warning(f"Text agent hit {MAX_TOOL_ROUNDS} tool rounds for {conversation_id}")
        except Exception as e:
            logger.error(f"Text agent failed for tenant {tenant_id}: {e}")
            # Drop this turn so the stored history stays a valid user/assistant sequence.
            await self._save(conversation_id, tenant_id, channel, customer_phone, customer_name,
                             previous, text, result, now)
            return result

        await self._save(conversation_id, tenant_id, channel, customer_phone, customer_name,
                         _trim(messages), text, result, now)
        return result

    async def _save(self, conversation_id, tenant_id, channel, customer_phone, customer_name,
                    messages, text, result: AgentReply, now: datetime):
        fields = {
            "tenant_id": tenant_id,
            "channel": channel,
            "messages": messages,
            "last_message": text,
            "updated_at": now,
        }
        if customer_phone:
            fields["customer_phone"] = customer_phone
        if customer_name:
            fields["customer_name"] = customer_name
        await get_database().text_conversations.update_one(
            {"_id": conversation_id},
            {
                "$set": fields,
                "$setOnInsert": {"created_at": now},
                "$push": {"transcript": {"$each": [
                    {"role": "customer", "text": text, "at": now},
                    {"role": "assistant", "text": result.text, "at": datetime.utcnow(),
                     **({"tools": result.tools_used} if result.tools_used else {})},
                ], "$slice": -200}},
            },
            upsert=True,
        )


def _trim(messages: List[dict]) -> List[dict]:
    """Keep the latest messages, starting at a customer text (not a tool result) so turns stay paired."""
    if len(messages) <= MAX_MODEL_MESSAGES:
        return messages
    recent = messages[-MAX_MODEL_MESSAGES:]
    for i, message in enumerate(recent):
        if message["role"] == "user" and any("text" in block for block in message["content"]):
            return recent[i:]
    return []


text_receptionist = TextReceptionist()
