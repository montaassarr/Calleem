import asyncio
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

import httpx
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    RunContext,
    ToolError,
    cli,
    function_tool,
)
from livekit.plugins import cartesia, deepgram, elevenlabs, groq, openai, silero

load_dotenv()

logger = logging.getLogger("tenant-agent")
logger.setLevel(logging.INFO)


@dataclass
class TenantContext:
    """Shared data for the agent session"""
    tenant_id: str
    business_name: str
    backend_url: str
    webhook_url: Optional[str] = None


class CallFlowAgent(Agent):
    """Multi-tenant AI receptionist agent that fetches config per tenant"""
    
    def __init__(
        self,
        *,
        tenant_id: str,
        system_prompt: str,
        business_name: str,
        timezone: str = "UTC",
    ):
        self.tenant_id = tenant_id
        self.business_name = business_name
        self.tz = ZoneInfo(timezone)
        
        today = datetime.now(self.tz).strftime("%A, %B %d, %Y")
        
        # Inject today's date and business name into system prompt
        enhanced_prompt = (
            f"{system_prompt}\n\n"
            f"Today is {today}. "
            f"You are representing {business_name}. "
            f"This is a voice conversation — speak naturally, clearly, and concisely. "
            f"When the user says hello or greets you, respond warmly and ask how you can help. "
            f"Be proactive and helpful in guiding the conversation."
        )
        
        super().__init__(instructions=enhanced_prompt)
        
        logger.info(f"Agent initialized for tenant {tenant_id} ({business_name})")

    @function_tool
    async def check_appointment_availability(
        self,
        ctx: RunContext[TenantContext],
        date: str,
        service_name: Optional[str] = None,
    ) -> str:
        """
        Check available appointment slots for a specific date.
        
        Args:
            date: The date to check availability (format: YYYY-MM-DD)
            service_name: Optional service name to filter availability
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                params = {"date": date}
                if service_name:
                    params["service_name"] = service_name
                
                response = await client.get(
                    f"{ctx.userdata.backend_url}/appointments/availability/check",
                    params=params,
                    headers={"X-Tenant-ID": ctx.userdata.tenant_id}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    slots = data.get("available_slots", [])
                    
                    if not slots:
                        return f"No available slots on {date}."
                    
                    # Format slots in a natural way
                    slot_texts = []
                    for slot in slots[:5]:  # Limit to 5 slots
                        time_str = slot.get("time", "")
                        slot_texts.append(f"{time_str}")
                    
                    return f"Available times on {date}: {', '.join(slot_texts)}"
                else:
                    logger.error(f"Availability check failed: {response.status_code}")
                    return "I'm having trouble checking availability right now. Please try again."
                    
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            raise ToolError("Unable to check availability at the moment")

    @function_tool
    async def book_appointment(
        self,
        ctx: RunContext[TenantContext],
        customer_name: str,
        customer_phone: str,
        customer_email: str,
        service_name: str,
        appointment_date: str,
        appointment_time: str,
        notes: Optional[str] = None,
    ) -> str:
        """
        Book an appointment for a customer.
        
        Args:
            customer_name: Customer's full name
            customer_phone: Customer's phone number
            customer_email: Customer's email address
            service_name: Name of the service being booked
            appointment_date: Date in YYYY-MM-DD format
            appointment_time: Time in HH:MM format (24-hour)
            notes: Optional notes or special requests
        """
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                payload = {
                    "customer_name": customer_name,
                    "customer_phone": customer_phone,
                    "customer_email": customer_email,
                    "service_name": service_name,
                    "appointment_date": appointment_date,
                    "appointment_time": appointment_time,
                    "notes": notes or "",
                }
                
                # If webhook URL is configured, trigger N8N workflow
                if ctx.userdata.webhook_url:
                    webhook_response = await client.post(
                        ctx.userdata.webhook_url,
                        json=payload,
                        headers={"X-Tenant-ID": ctx.userdata.tenant_id}
                    )
                    logger.info(f"N8N webhook triggered: {webhook_response.status_code}")
                
                # Create appointment in backend
                response = await client.post(
                    f"{ctx.userdata.backend_url}/appointments/",
                    json=payload,
                    headers={"X-Tenant-ID": ctx.userdata.tenant_id}
                )
                
                if response.status_code in [200, 201]:
                    return (
                        f"Perfect! I've scheduled your appointment for {appointment_date} "
                        f"at {appointment_time}. You'll receive a confirmation email at {customer_email}."
                    )
                else:
                    logger.error(f"Booking failed: {response.status_code} - {response.text}")
                    return "I'm sorry, I couldn't complete the booking. Please try again or call us directly."
                    
        except Exception as e:
            logger.error(f"Error booking appointment: {e}")
            raise ToolError("Unable to book appointment at the moment")

    @function_tool
    async def get_business_hours(
        self,
        ctx: RunContext[TenantContext],
    ) -> str:
        """
        Get the business operating hours.
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{ctx.userdata.backend_url}/admin/config",
                    headers={"X-Tenant-ID": ctx.userdata.tenant_id}
                )
                
                if response.status_code == 200:
                    config = response.json()
                    hours = config.get("business_hours", {})
                    
                    if not hours:
                        return "We're open Monday through Friday, 9 AM to 5 PM."
                    
                    # Format hours naturally
                    return f"Our hours are: {hours}"
                else:
                    return "We're typically open during regular business hours."
                    
        except Exception as e:
            logger.error(f"Error fetching business hours: {e}")
            return "We're open during regular business hours."

    @function_tool
    async def list_services(
        self,
        ctx: RunContext[TenantContext],
    ) -> str:
        """
        List all available services offered by the business.
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{ctx.userdata.backend_url}/services/",
                    headers={"X-Tenant-ID": ctx.userdata.tenant_id}
                )
                
                if response.status_code == 200:
                    services = response.json()
                    
                    if not services:
                        return "Please ask about our available services."
                    
                    # Format services naturally
                    service_list = []
                    for service in services[:10]:  # Limit to 10 services
                        name = service.get("name", "")
                        duration = service.get("duration_minutes", 0)
                        price = service.get("price", 0)
                        service_list.append(f"{name} ({duration} minutes, ${price})")
                    
                    return f"We offer the following services: {', '.join(service_list)}"
                else:
                    return "Let me know what service you're interested in."
                    
        except Exception as e:
            logger.error(f"Error fetching services: {e}")
            return "Please ask about specific services you're interested in."

    # Demo/Test Function Tools - For testing agent capabilities
    @function_tool
    async def get_weather(
        self,
        ctx: RunContext[TenantContext],
        location: str,
    ) -> str:
        """
        Get current weather information for a location (Demo function for testing).
        
        Args:
            location: City name or location to check weather for
        """
        logger.info(f"[Tenant {ctx.userdata.tenant_id}] Weather check for: {location}")
        
        # This is a demo function - returns mock data
        weather_conditions = [
            "sunny and clear", "partly cloudy", "overcast", 
            "light rain", "scattered showers"
        ]
        import random
        condition = random.choice(weather_conditions)
        temperature = random.randint(60, 85)
        
        return (
            f"The weather in {location} is {condition} with a temperature "
            f"of {temperature}°F. This is demonstration data for testing the agent's "
            f"function calling capabilities."
        )

    @function_tool
    async def calculate_discount(
        self,
        ctx: RunContext[TenantContext],
        original_price: float,
        discount_percent: int,
    ) -> str:
        """
        Calculate the final price after applying a discount (Demo function for testing).
        
        Args:
            original_price: Original price before discount
            discount_percent: Discount percentage (e.g., 20 for 20% off)
        """
        logger.info(
            f"[Tenant {ctx.userdata.tenant_id}] Calculating {discount_percent}% "
            f"discount on ${original_price}"
        )
        
        if discount_percent < 0 or discount_percent > 100:
            return "Discount percentage must be between 0 and 100."
        
        discount_amount = original_price * (discount_percent / 100)
        final_price = original_price - discount_amount
        
        return (
            f"Original price: ${original_price:.2f}. "
            f"Discount: {discount_percent}% (${discount_amount:.2f}). "
            f"Final price: ${final_price:.2f}"
        )

    @function_tool
    async def set_reminder(
        self,
        ctx: RunContext[TenantContext],
        reminder_text: str,
        minutes_from_now: int,
    ) -> str:
        """
        Set a reminder for the future (Demo function for testing).
        
        Args:
            reminder_text: What to be reminded about
            minutes_from_now: How many minutes from now to set the reminder
        """
        logger.info(
            f"[Tenant {ctx.userdata.tenant_id}] Setting reminder: '{reminder_text}' "
            f"for {minutes_from_now} minutes from now"
        )
        
        from datetime import datetime, timedelta
        reminder_time = datetime.now(self.tz) + timedelta(minutes=minutes_from_now)
        time_str = reminder_time.strftime("%I:%M %p")
        
        return (
            f"Reminder set! I'll remind you about '{reminder_text}' "
            f"at {time_str} (in {minutes_from_now} minutes). "
            f"This is a demonstration of the agent's scheduling capabilities."
        )

    @function_tool
    async def check_business_status(
        self,
        ctx: RunContext[TenantContext],
    ) -> str:
        """
        Check if the business is currently open or closed (Demo function for testing).
        """
        logger.info(f"[Tenant {ctx.userdata.tenant_id}] Checking business status")
        
        from datetime import datetime
        now = datetime.now(self.tz)
        current_hour = now.hour
        day_of_week = now.weekday()  # 0 = Monday, 6 = Sunday
        
        # Simple business hours logic (9 AM - 6 PM, Monday-Friday)
        if day_of_week >= 5:  # Weekend
            status = "closed (weekend)"
            next_open = "Monday at 9:00 AM"
        elif current_hour < 9:
            status = "closed (before opening hours)"
            next_open = "today at 9:00 AM"
        elif current_hour >= 18:
            status = "closed (after business hours)"
            next_open = "tomorrow at 9:00 AM"
        else:
            status = "open"
            next_open = None
        
        if next_open:
            return (
                f"{ctx.userdata.business_name} is currently {status}. "
                f"We'll be open {next_open}. This is demonstration data for testing."
            )
        else:
            return (
                f"{ctx.userdata.business_name} is currently {status}! "
                f"We're here to help you. Business hours: Monday-Friday, 9 AM - 6 PM. "
                f"This is demonstration data for testing."
            )


# Create the server instance
server = AgentServer()


@server.rtc_session()
async def initialize_tenant_agent(ctx: JobContext):
    """Entry point for agent initialization when a room is joined"""
    
    await ctx.connect()
    
    # Extract tenant_id from room metadata
    room = ctx.room
    metadata = room.metadata or {}
    
    logger.info(f"Room: {room.name}, Raw metadata: {metadata}, Type: {type(metadata)}")
    
    # Parse metadata (it's a JSON string)
    import json
    try:
        meta_dict = json.loads(metadata) if isinstance(metadata, str) else metadata
    except Exception as e:
        logger.warning(f"Failed to parse metadata: {e}")
        meta_dict = {}
    
    tenant_id = meta_dict.get("tenant_id")
    
    # Fallback: extract tenant_id from room name if not in metadata
    # Room name format: preview-{tenant_id}-{random}
    if not tenant_id and room.name.startswith("preview-"):
        parts = room.name.split("-")
        if len(parts) >= 2:
            tenant_id = parts[1]
            logger.info(f"Extracted tenant_id {tenant_id} from room name")
    
    if not tenant_id:
        logger.error(f"No tenant_id in room metadata or room name. Metadata: {metadata}, Room: {room.name}")
        raise ValueError("Missing tenant_id in room metadata")
    
    logger.info(f"Initializing agent for tenant: {tenant_id}")
    
    # Fetch tenant configuration from backend
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{backend_url}/api/v1/voice-agent/tenant-config/{tenant_id}"
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch tenant config: {response.status_code}")
                raise ValueError(f"Cannot fetch config for tenant {tenant_id}")
            
            config = response.json()
            logger.info(f"Fetched config for tenant {tenant_id}: {list(config.keys())}")
            
        except Exception as e:
            logger.error(f"Error fetching tenant config: {e}")
            raise
    
    # Extract configuration
    api_keys = config.get("api_keys", {})
    agent_config = config.get("agent_config", {})
    business_name = config.get("business_name", "Business")
    
    # Initialize LLM based on available API keys
    llm_model = agent_config.get("llm_model", "llama-3.3-70b-versatile")
    
    if "groq" in api_keys:
        logger.info(f"Using Groq LLM: {llm_model}")
        llm = groq.LLM(
            model=llm_model,
            api_key=api_keys["groq"]
        )
    elif "openai" in api_keys:
        logger.info(f"Using OpenAI LLM: {llm_model}")
        llm = openai.LLM(
            model=llm_model,
            api_key=api_keys["openai"]
        )
    else:
        logger.error("No LLM API key found")
        raise ValueError("No LLM API key configured for this tenant")
    
    # Initialize TTS based on voice provider
    voice_provider = agent_config.get("voice_provider", "cartesia")
    voice_id = agent_config.get("voice_id")
    
    if voice_provider == "elevenlabs" and "elevenlabs" in api_keys:
        logger.info(f"Using ElevenLabs TTS: {voice_id}")
        tts = elevenlabs.TTS(
            voice=voice_id or "rachel",
            api_key=api_keys["elevenlabs"]
        )
    elif "cartesia" in api_keys:
        logger.info(f"Using Cartesia TTS: {voice_id}")
        tts = cartesia.TTS(
            voice=voice_id or "79a125e8-cd45-4c13-8a67-188112f4dd22",  # Default voice
            speed="fast",
            api_key=api_keys["cartesia"]
        )
    elif "openai" in api_keys:
        # Fallback to OpenAI TTS if no Cartesia key
        logger.warning(f"No Cartesia key found, falling back to OpenAI TTS")
        tts = openai.TTS(
            voice="alloy",
            api_key=api_keys["openai"]
        )
    elif "groq" in api_keys:
        # Last resort: Try using Groq for TTS (if supported)
        logger.warning(f"No TTS provider configured, attempting Groq fallback")
        # Groq doesn't have TTS, so we'll use OpenAI with a demo key for testing
        # In production, you MUST add a proper Cartesia or OpenAI key
        logger.error("No TTS API key found - voice will not work!")
        raise ValueError("No TTS API key (Cartesia, ElevenLabs, or OpenAI) configured for this tenant")
    else:
        logger.error("No TTS API key found")
        raise ValueError("No TTS API key configured for this tenant")
    
    # Create tenant context for function tools
    tenant_context = TenantContext(
        tenant_id=tenant_id,
        business_name=business_name,
        backend_url=backend_url,
        webhook_url=config.get("webhook_url"),
    )
    
    # Initialize agent with system prompt
    system_prompt = agent_config.get("system_prompt", "You are a helpful AI assistant.")
    
    agent = CallFlowAgent(
        tenant_id=tenant_id,
        system_prompt=system_prompt,
        business_name=business_name,
        timezone="America/New_York",  # TODO: Make this configurable
    )
    
    # Start the agent session with the new API
    session = AgentSession[TenantContext](
        userdata=tenant_context,
        stt=deepgram.STT(),
        llm=llm,
        tts=tts,
        vad=silero.VAD.load(),
        preemptive_generation=True,  # Enable preemptive generation for faster responses
    )
    
    await session.start(agent=agent, room=ctx.room)
    
    logger.info(f"Agent session started for tenant {tenant_id} in room {room.name}")


if __name__ == "__main__":
    cli.run_app(server)
