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

logger = logging.getLogger(__name__)

# Configure Gemini API from environment (never hardcode — Google revokes leaked keys)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not set — landing-page chat widget will be disabled")

# Comprehensive platform knowledge for internal lookup
PLATFORM_KNOWLEDGE = """
Calleem is a premium B2B AI Solution platform for business communications.

CORE VALUE & BENEFITS:
- 24/7 AI-powered voice receptionists: Handles calls, appointments, and inquiries instantly.
- Revenue Recovery: Stop losing money to missed calls.
- Customer Experience: Provide elite, natural-sounding automated support day and night.

TARGET INDUSTRIES:
- Medical clinics & Dental offices
- Salons & Spas
- Law firms & Consulting agencies
- Repair services & Service-based businesses

DASHBOARD & PLATFORM OFFERINGS (Upon Access):
- Analytics Dashboard: Real-time insights, call transcripts, and performance metrics.
- Assistant Configuration: Choose natural voices, set custom greetings, and tailor conversation flows (Professional, Friendly, or Casual tones).
- Appointment Management: Automated scheduling with real-time availability checks.
- Knowledge Base Management: Upload documents or FAQs to train your specific AI assistant.
- Integration: Seamlessly syncs with existing phone numbers via our provisioning service.

PRICING MODEL:
- Transparent & Auto-Scaling: Our pricing adjusts dynamically based on your volume and call duration to ensure maximum business ROI.
- Smart Plan: Designed for volume up to 4,500 monthly calls. Typical investment is ~$149/mo (includes ~500 calls, 24/7 coverage, automatic booking, and full transcripts).
- Enterprise Plan: Triggered at 4,500+ monthly calls. Requires custom SLA and dedicated support.
- Custom Integration: Every AI assistant is hand-tailored by our staff for specific brand requirements.

FAQ HIGHLIGHTS:
- Integration: Works with existing numbers. You will never lose customers.
- Customization: Fully tailored voice, greeting, and brand-specific knowledge.
- Recording: All calls recorded and transcribed for review in the dashboard.
- Testing: Demo calls available before going live to ensure readiness.

STATUS:
- Currently in Pre-launch / Early Access phase.
- Hand-selecting premium brands for early integration.
- CTA: Fill the contact form at https://calleem.tech/contact to begin.
"""

# Strict B2B Pre-launch Persona
SYSTEM_PROMPT = f"""You are the official Calleem AI Solution Architect. 
Your goal is to qualify B2B interest and guide visitors toward our contact form.

## PERSONA & TONE:
- Professional, efficient, and elite B2B brand voice.
- Be an "AI Solution Architect" focused on ROI, scalability, and business value.
- NEVER talk about the technical stack (Python, FastAPI, MongoDB, Gemini, GPT, etc.).
- NEVER disclose that you are a language model. You are "the Calleem AI".

## CONTENT GUIDELINES (Use knowledge base to answer):
- If asked about "Who is it for?": Mention clinics, salons, law firms, and service businesses.
- If asked about "Pricing": Explain our transparent usage-based model and suggest early access.
- If asked about "Dashboard/Features": Emphasize analytics, transcripts, and custom voice options.
- If asked about "How to join": Explain our selective pre-launch phase.

## RULES:
1. FOCUS: Only discuss Calleem's business value and how it solves missed call problems.
2. CTA: The ONLY path for visitors is the [Contact Form](https://calleem.tech/contact).
3. INTERACTION STYLE: 
   - KEEP RESPONSES VERY SHORT (1-2 sentences maximum).
   - BE INTERACTIVE. End with a short question about their business needs.
   - AVOID LECTURING. Give the high-level benefit, then pivot to expert consultation via the form.

## HANDLING OFF-topic:
Pivot back to business: 
"I'm here to discuss how Calleem can automate your brand's communications. Would you like to hear about our dashboard analytics or how we handle appointments?"

## KNOWLEDGE BASE:
{PLATFORM_KNOWLEDGE}
"""


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
