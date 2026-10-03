"""
Bedrock Chat Service
====================
Landing-page chat widget backed by Amazon Bedrock (Converse API).
Enabled with CHAT_PROVIDER=bedrock. Credentials come from the standard AWS
environment variables (AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY) or an IAM role.
"""

import asyncio
import logging
import os
from typing import Dict, List

import boto3
from botocore.config import Config

from services.chat_prompt import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# EU cross-region inference profile: requests stay inside EU regions.
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "eu.amazon.nova-lite-v1:0")
BEDROCK_REGION = os.getenv("BEDROCK_REGION") or os.getenv("AWS_REGION") or "eu-west-3"
MAX_HISTORY_MESSAGES = 20  # user + assistant messages kept per session
MAX_SESSIONS = 1000  # oldest sessions are dropped beyond this


class BedrockChatService:
    """Same interface as GeminiChatService, backed by Bedrock Converse."""

    def __init__(self):
        self.chat_sessions: Dict[str, List[dict]] = {}
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=BEDROCK_REGION,
            config=Config(retries={"max_attempts": 4, "mode": "adaptive"}, read_timeout=30),
        )

    def get_or_create_session(self, session_id: str) -> List[dict]:
        """Get an existing conversation history or start a new one"""
        if session_id not in self.chat_sessions:
            if len(self.chat_sessions) >= MAX_SESSIONS:
                self.chat_sessions.pop(next(iter(self.chat_sessions)))
            self.chat_sessions[session_id] = []
        return self.chat_sessions[session_id]

    async def send_message(self, session_id: str, message: str) -> str:
        """Send a message and get a response from Bedrock"""
        history = self.get_or_create_session(session_id)
        history.append({"role": "user", "content": [{"text": message}]})
        try:
            # boto3 is blocking; keep the event loop free for other requests.
            response = await asyncio.to_thread(
                self.client.converse,
                modelId=BEDROCK_MODEL_ID,
                system=[{"text": SYSTEM_PROMPT}],
                messages=history,
                inferenceConfig={"maxTokens": 300, "temperature": 0.7},
            )
        except Exception as e:
            history.pop()  # drop the unanswered message so the next turn stays valid
            logger.error(f"Error sending message to Bedrock: {e}")
            raise

        reply = response["output"]["message"]
        history.append(reply)
        # Turns are appended in pairs, so trimming to an even count keeps a user message first.
        del history[:-MAX_HISTORY_MESSAGES]
        return "".join(block.get("text", "") for block in reply["content"])

    def clear_session(self, session_id: str):
        """Clear a chat session"""
        self.chat_sessions.pop(session_id, None)
