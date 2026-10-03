"""
Gemini Chat Service
====================
Provides chat functionality using Google's Gemini API for the landing page chat widget.
Trained specifically on Calleem AI Receptionist platform data.
"""

import os
from google import genai
from google.genai import types
from typing import List, Optional
import logging

from services.chat_prompt import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Configure Gemini API from environment (never hardcode — Google revokes leaked keys)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not set — landing-page chat widget will be disabled")



class GeminiChatService:
    """Service for handling chat interactions using Gemini API"""

    def __init__(self):
        self.chat_sessions: dict = {}  # Store chat sessions by session_id

    def get_or_create_session(self, session_id: str):
        """Get an existing chat session or create a new one"""
        if session_id not in self.chat_sessions:
            if not GEMINI_API_KEY or client is None:
                raise RuntimeError("GEMINI_API_KEY is not configured")
                
            self.chat_sessions[session_id] = client.chats.create(
                model='gemini-2.5-flash',
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.7,
                    max_output_tokens=500,
                ),
                history=[
                    types.Content(
                        role="user", 
                        parts=[types.Part.from_text(text="Hello")]
                    ),
                    types.Content(
                        role="model", 
                        parts=[types.Part.from_text(text="Understood! I'm the Calleem AI assistant, exclusively focused on helping visitors learn about our AI receptionist platform. I will only discuss Calleem's features, pricing, capabilities, and how we help businesses automate their customer communications. I will politely redirect any off-topic questions back to Calleem. I'm ready to assist!")]
                    )
                ]
            )
        return self.chat_sessions[session_id]
    
    async def send_message(self, session_id: str, message: str) -> str:
        """Send a message and get a response from Gemini"""
        try:
            chat = self.get_or_create_session(session_id)
            response = chat.send_message(message)
            return response.text
        except Exception as e:
            logger.error(f"Error sending message to Gemini: {e}")
            raise
    
    def clear_session(self, session_id: str):
        """Clear a chat session"""
        if session_id in self.chat_sessions:
            del self.chat_sessions[session_id]


# Singleton instance
gemini_chat_service = GeminiChatService()
