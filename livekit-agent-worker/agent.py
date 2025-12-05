"""
CallFlow AI - Multi-Tenant Voice Agent
Using LiveKit Cloud Inference (FREE - no API keys needed)

LiveKit Cloud provides STT/LLM/TTS through their inference API.
All AI processing is billed through LiveKit, no external API keys required.
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


class CallFlowAgent(Agent):
    """Multi-tenant AI receptionist agent"""

    def __init__(self, tenant_id: str, config: dict):
        self.tenant_id = tenant_id
        self.config = config
        self.business_name = config.get("business_name", "Business")
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")

        # Simple system prompt
        super().__init__(
            instructions=f"""You are a friendly AI receptionist for {self.business_name}.
Help customers book appointments and answer questions.
Speak naturally and keep responses brief."""
        )
        logger.info(f"Agent initialized for tenant {tenant_id}")

    @function_tool
    async def book_appointment(
        self,
        ctx: RunContext,
        customer_name: str,
        date: str,
        time: str,
    ) -> str:
        """Book an appointment.

        Args:
            customer_name: Customer's name
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM format
        """
        logger.info(f"Booking: {customer_name} on {date} at {time}")
        return f"I've booked your appointment for {date} at {time}. See you then!"


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


@server.rtc_session()
async def voice_agent(ctx: JobContext):
    """Main entry point - uses LiveKit Cloud Inference (FREE)"""

    tenant_id = extract_tenant_id(ctx.room.name)
    logger.info(f"Starting agent for tenant: {tenant_id}, room: {ctx.room.name}")

    # Fetch tenant config (optional)
    config = {"business_name": "My Business", "tenant_id": tenant_id}
    try:
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{backend_url}/api/v1/voice-agent/tenant-config/{tenant_id}"
            )
            if response.status_code == 200:
                config = response.json()
    except Exception as e:
        logger.warning(f"Could not fetch tenant config: {e}")

    # =========================================================================
    # LiveKit Cloud Inference - FREE models (no API keys needed!)
    # These are provided by LiveKit Cloud and billed through your LiveKit account
    # =========================================================================
    session = AgentSession(
        # Speech-to-Text: Deepgram Nova 3 (via LiveKit Cloud)
        stt=inference.STT(model="deepgram/nova-3"),
        # LLM: OpenAI GPT-4o-mini (via LiveKit Cloud)
        llm=inference.LLM(model="openai/gpt-4o-mini"),
        # Text-to-Speech: Cartesia Sonic (via LiveKit Cloud)
        tts=inference.TTS(
            model="cartesia/sonic-2",
            voice="79a125e8-cd45-4c13-8a67-188112f4dd22",  # Default female voice
        ),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

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
    logger.info(f"Agent connected for tenant {tenant_id}")


if __name__ == "__main__":
    cli.run_app(server)
