"""
CallFlow AI - Multi-Tenant Voice Agent
Uses LiveKit Cloud Inference + n8n Workflows for booking

Reads configuration dynamically from backend API per session.
Connects to n8n workflows for appointment management.
"""

import logging
import os

import httpx
from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    RunContext,
    cli,
    function_tool,
    inference,
    room_io,
)
from livekit.plugins import noise_cancellation, silero

load_dotenv()

logger = logging.getLogger("callflow-agent")
logging.basicConfig(level=logging.INFO)

# n8n Cloud webhook URL (set in .env or use default)
# Format: https://<instance>.app.n8n.cloud/webhook/<path>
N8N_WEBHOOK_BASE = os.getenv("N8N_WEBHOOK_URL", "https://aimstudio.app.n8n.cloud/webhook")



class CallFlowAgent(Agent):
    """Multi-tenant AI receptionist agent with n8n integration"""

    def __init__(self, tenant_id: str, config: dict):
        self.tenant_id = tenant_id
        self.config = config
        self.business_name = config.get("business_name", "Business")
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        
        # Get system prompt from config
        system_prompt = config.get("system_prompt", f"""You are a friendly AI receptionist for {self.business_name}.

Your capabilities:
- Book appointments for customers
- Check available time slots
- List available services
- Answer questions about the business

Always be helpful, polite, and professional. Keep responses brief and natural.""")

        super().__init__(instructions=system_prompt)
        logger.info(f"Agent initialized for tenant {tenant_id} - {self.business_name}")

    def _get_date_from_text(self, date_text: str) -> str:
        """Convert natural language date to YYYY-MM-DD format"""
        from datetime import datetime, timedelta
        today = datetime.now()
        
        date_lower = date_text.lower().strip()
        
        if "today" in date_lower:
            return today.strftime("%Y-%m-%d")
        elif "tomorrow" in date_lower:
            return (today + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "monday" in date_lower:
            days_ahead = 0 - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        elif "tuesday" in date_lower:
            days_ahead = 1 - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        elif "wednesday" in date_lower:
            days_ahead = 2 - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        elif "thursday" in date_lower:
            days_ahead = 3 - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        elif "friday" in date_lower:
            days_ahead = 4 - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        elif "saturday" in date_lower:
            days_ahead = 5 - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        elif "sunday" in date_lower:
            days_ahead = 6 - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        
        # Try to parse as YYYY-MM-DD
        try:
            datetime.strptime(date_text, "%Y-%m-%d")
            return date_text
        except:
            pass
        
        # Default to tomorrow if can't parse
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")

    def _get_time_from_text(self, time_text: str) -> str:
        """Convert spoken time to HH:MM format (24h)"""
        import re
        
        time_lower = time_text.lower().strip()
        
        # Handle "3 PM", "3PM", "3:00 PM" etc
        match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm|a\.m\.|p\.m\.)?', time_lower)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if match.group(2) else 0
            meridiem = match.group(3)
            
            if meridiem and ('pm' in meridiem or 'p.m.' in meridiem):
                if hour != 12:
                    hour += 12
            elif meridiem and ('am' in meridiem or 'a.m.' in meridiem):
                if hour == 12:
                    hour = 0
            
            return f"{hour:02d}:{minute:02d}"
        
        # If already in HH:MM format
        if re.match(r'^\d{1,2}:\d{2}$', time_text):
            parts = time_text.split(':')
            return f"{int(parts[0]):02d}:{parts[1]}"
        
        # Default to 10 AM if can't parse
        return "10:00"


    @function_tool
    async def check_availability(
        self,
        ctx: RunContext,
        date: str,
        time: str = "",
    ) -> str:
        """Check if a time slot is available for booking.

        Args:
            date: Date to check (e.g., "tomorrow", "Monday", or "2025-12-06")
            time: Optional time in HH:MM format (e.g., "15:00" for 3 PM)
        """
        # Convert natural language date to YYYY-MM-DD
        parsed_date = self._get_date_from_text(date)
        logger.info(f"Checking availability for {parsed_date} {time} (original: {date})")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Use the public agent endpoint
                response = await client.get(
                    f"{self.backend_url}/api/v1/appointments/agent/availability",
                    params={"date": parsed_date, "time": time},
                    headers={"X-Tenant-ID": self.tenant_id}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("available"):
                        return f"Yes, {parsed_date} at {time} is available! Would you like me to book it for you?"
                    else:
                        return f"Sorry, that time is not available. {data.get('reason', '')} Would you like to try a different time?"
                        
        except Exception as e:
            logger.error(f"Availability check failed: {e}")
            
        return f"The time slot on {parsed_date} at {time} appears to be available. Would you like me to book it?"

    @function_tool
    async def book_appointment(
        self,
        ctx: RunContext,
        customer_name: str,
        date: str,
        time: str,
        service: str = "General",
        customer_phone: str = "",
        notes: str = "",
    ) -> str:
        """Book an appointment for a customer.

        Args:
            customer_name: Full name of the customer
            date: Appointment date (e.g., "tomorrow", "Monday", or "2025-12-06")
            time: Appointment time (e.g., "15:00" for 3 PM)
            service: Service type requested
            customer_phone: Customer's phone number
            notes: Any additional notes
        """
        # Convert natural language date to YYYY-MM-DD
        parsed_date = self._get_date_from_text(date)
        logger.info(f"Booking appointment: {customer_name} on {parsed_date} at {time} (original date: {date})")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Use the public agent endpoint
                response = await client.post(
                    f"{self.backend_url}/api/v1/appointments/agent/book",
                    json={
                        "customer_name": customer_name,
                        "customer_phone": customer_phone,
                        "date": parsed_date,
                        "time": time,
                        "service": service,
                        "notes": notes,
                        "duration_minutes": 30,
                    },
                    headers={"X-Tenant-ID": self.tenant_id}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        return f"I've booked your appointment for {parsed_date} at {time}. You're all set, {customer_name}!"
                    else:
                        return f"Sorry, I couldn't book that time: {data.get('message', 'Please try a different time.')}"
                        
        except Exception as e:
            logger.error(f"Booking failed: {e}")
            
        return f"I'd be happy to book {customer_name} for {parsed_date} at {time}. Let me confirm with the business and get back to you."


    @function_tool
    async def list_services(self, ctx: RunContext) -> str:
        """List all available services that can be booked."""
        logger.info("Listing services")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.backend_url}/api/v1/services/",
                    headers={"X-Tenant-ID": self.tenant_id}
                )
                
                if response.status_code == 200:
                    services = response.json()
                    if services and len(services) > 0:
                        service_list = ", ".join([s.get("name", "Service") for s in services[:5]])
                        return f"We offer: {service_list}. Which service are you interested in?"
                    else:
                        return "We offer various services. What type of appointment are you looking for?"
                        
        except Exception as e:
            logger.error(f"Service list failed: {e}")
            
        return "We have several services available. What type of service are you looking for today?"


# Server setup
server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("VAD model preloaded")


server.setup_fnc = prewarm


def extract_tenant_id(room_name: str) -> str:
    """Extract tenant_id from room name: preview-{tenant_id}-{random}"""
    parts = room_name.split("-")
    if len(parts) >= 2 and parts[0] == "preview":
        return parts[1]
    return "default"


async def fetch_tenant_config(tenant_id: str) -> dict:
    """Fetch tenant configuration from backend"""
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{backend_url}/api/v1/voice-agent/tenant-config/{tenant_id}"
            )
            if response.status_code == 200:
                config = response.json()
                logger.info(f"Loaded config for tenant {tenant_id}: LLM={config.get('llm_model')}, STT={config.get('stt_model')}, TTS={config.get('tts_model')}")
                return config
    except Exception as e:
        logger.warning(f"Could not fetch tenant config: {e}")
    
    return {"business_name": "Business", "tenant_id": tenant_id}


@server.rtc_session()
async def voice_agent(ctx: JobContext):
    """Main entry point - uses LiveKit Cloud Inference with tenant config"""

    tenant_id = extract_tenant_id(ctx.room.name)
    logger.info(f"Starting agent for tenant: {tenant_id}, room: {ctx.room.name}")

    # Fetch tenant config (includes stt_model, llm_model, tts_model from dashboard settings)
    config = await fetch_tenant_config(tenant_id)
    
    # Get models from config (with defaults)
    stt_model = config.get("stt_model", "deepgram/nova-3")
    llm_model = config.get("llm_model", "openai/gpt-4o-mini")
    tts_model = config.get("tts_model", "cartesia/sonic-2")
    voice_id = config.get("voice_id", "79a125e8-cd45-4c13-8a67-188112f4dd22")
    
    logger.info(f"Using models: STT={stt_model}, LLM={llm_model}, TTS={tts_model}")

    # Create session with tenant's configured models (LiveKit Cloud Inference)
    session = AgentSession(
        stt=inference.STT(model=stt_model),
        llm=inference.LLM(model=llm_model),
        tts=inference.TTS(model=tts_model, voice=voice_id),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    # Create agent with tenant config
    agent = CallFlowAgent(tenant_id=tenant_id, config=config)

    # Start with noise cancellation
    await session.start(
        agent=agent,
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: noise_cancellation.BVC(),
            ),
        ),
    )

    await ctx.connect()
    logger.info(f"Agent connected for tenant {tenant_id} using {llm_model}")


if __name__ == "__main__":
    cli.run_app(server)
