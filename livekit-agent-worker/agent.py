import logging
import os
import json
from typing import Any
from datetime import datetime

import httpx
from dotenv import load_dotenv

from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    llm,
    Agent,
    inference,
)
import uuid
from livekit.agents.voice import AgentSession
from livekit.plugins import silero


load_dotenv()

logger = logging.getLogger("callflow-agent")
logging.basicConfig(level=logging.INFO)

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
# Pointing to the new Python Backend Agent endpoint
AGENT_API_URL = f"{BACKEND_URL}/api/v1/ai/chat"
logger.info(f"Connecting to AI Agent at: {AGENT_API_URL}")


class N8NLLM(llm.LLM):
    """
    Custom LLM adapter that offloads reasoning to n8n via webhook.
    """
    def __init__(self, tenant_id: str, business_name: str, session_id: str):
        super().__init__()
        self.tenant_id = tenant_id
        self.business_name = business_name
        self.session_id = session_id
        
    def chat(
        self,
        *,
        chat_ctx: llm.ChatContext,
        tools: list[llm.FunctionTool | llm.RawFunctionTool] | None = None,
        conn_options: Any = None,
        parallel_tool_calls: Any = None,
        tool_choice: Any = None,
        extra_kwargs: Any = None,
    ) -> "N8NLLMStream":
        return N8NLLMStream(self, chat_ctx=chat_ctx, conn_options=conn_options)


class N8NLLMStream(llm.LLMStream):
    def __init__(self, n8n_llm: N8NLLM, chat_ctx: llm.ChatContext, conn_options: Any):
        super().__init__(
            llm=n8n_llm, 
            chat_ctx=chat_ctx, 
            tools=[], 
            conn_options=conn_options or llm.APIConnectOptions()
        )
        self.n8n_llm = n8n_llm

    async def _run(self) -> None:
        # Get the last user message
        if not self._chat_ctx.items:
            return

        last_msg = self._chat_ctx.items[-1]
        if last_msg.role != "user":
            return

        user_text = last_msg.content
        if isinstance(user_text, list):
            user_text = " ".join([c for c in user_text if isinstance(c, str)])

        logger.info(f"Sending to n8n: {user_text}")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    AGENT_API_URL,
                    json={
                        "message": user_text,
                        "session_id": self.n8n_llm.session_id,
                        "tenant_id": self.n8n_llm.tenant_id,
                        "business_name": self.n8n_llm.business_name,
                        "chat_history": [
                            {"role": m.role, "content": m.content} 
                            for m in self._chat_ctx.items
                        ]
                    }
                )
                
                logger.info(f"n8n raw response ({response.status_code}): {response.text}")

                if response.status_code == 200:
                    try:
                        data = response.json()
                        text = data.get("response", "I'm sorry, I didn't catch that.")
                    except json.JSONDecodeError:
                        logger.error("Failed to parse n8n JSON response, likely workflow didn't hit 'Respond to Webhook' node")
                        text = "I'm having trouble connecting to my brain right now."
                    
                    logger.info(f"Parsed response text: {text}")

                    # Yield the full text as a single chunk
                    chunk = llm.ChatChunk(
                        id=str(uuid.uuid4()),
                        delta=llm.ChoiceDelta(content=text, role="assistant")
                    )
                    await self._event_ch.send(chunk)
                else:
                    logger.error(f"n8n returned status {response.status_code}. Raw response: {response.text}")
                    chunk = llm.ChatChunk(
                        id=str(uuid.uuid4()),
                        delta=llm.ChoiceDelta(content="I'm having trouble connecting to my brain right now.", role="assistant")
                    )
                    await self._event_ch.send(chunk)

        except Exception as e:
            logger.error(f"Failed to call n8n: {e}", exc_info=True)
            chunk = llm.ChatChunk(
                id=str(uuid.uuid4()),
                delta=llm.ChoiceDelta(content="I'm sorry, I'm experiencing technical difficulties.", role="assistant")
            )
            await self._event_ch.send(chunk)


async def fetch_tenant_config(tenant_id: str) -> dict:
    """Fetch tenant configuration from backend"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{BACKEND_URL}/api/v1/voice-agent/tenant-config/{tenant_id}"
            )
            if response.status_code == 200:
                config = response.json()
                logger.info(f"Loaded config for tenant {tenant_id}")
                return config
    except Exception as e:
        logger.warning(f"Could not fetch tenant config: {e}")
    
    return {"business_name": "Valued Business", "tenant_id": tenant_id}


def extract_tenant_id(room_name: str) -> str:
    parts = room_name.split("-")
    if len(parts) >= 2 and parts[0] == "preview":
        return parts[1]
    return "default"


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    tenant_id = extract_tenant_id(ctx.room.name)
    logger.info(f"Starting agent job for tenant: {tenant_id}")

    # Fetch Config
    config = await fetch_tenant_config(tenant_id)
    business_name = config.get("business_name", "Valued Business")

    # Initialize Models using Cloud Inference
    # Extract provider from model string (e.g. "deepgram/nova-3" -> "deepgram")
    stt_model_str = config.get("stt_model", "deepgram")
    stt_provider = stt_model_str.split("/")[0] if "/" in stt_model_str else stt_model_str
    
    tts_model_str = config.get("tts_model", "cartesia")
    tts_provider = tts_model_str.split("/")[0] if "/" in tts_model_str else tts_model_str

    logger.info(f"Using STT Provider: {stt_provider}, TTS Provider: {tts_provider}")

    stt = inference.STT(model=stt_provider) 
    tts = inference.TTS(model=tts_provider)

    # Custom N8N LLM
    n8n_llm = N8NLLM(
        tenant_id=tenant_id, 
        business_name=business_name,
        session_id=ctx.room.name
    )

    # Prepare System Prompt
    system_prompt = config.get("system_prompt", f"You are a helpful AI receptionist for {business_name}.")
    system_prompt += f"\nToday is {datetime.now().strftime('%A, %B %d, %Y')}."

    # Voice Pipeline Config (Agent)
    agent_config = Agent(
        vad=ctx.proc.userdata["vad"],
        stt=stt,
        llm=n8n_llm,
        tts=tts,
        instructions=system_prompt  
    )

    # Runner (AgentSession)
    session = AgentSession()
    session.update_agent(agent_config)

    # Connect to Room
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    
    # Wait for Participant
    participant = await ctx.wait_for_participant()
    logger.info(f"Participant joined: {participant.identity}")

    # Start Session
    # Signature: start(agent, *, room=...)
    await session.start(agent_config, room=ctx.room)
    
    # Initial Greeting
    # Note: ensure session handles the greeting correctly
    await session.say(f"Hi, thanks for calling {business_name}. How can I help you today?")


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        )
    )
