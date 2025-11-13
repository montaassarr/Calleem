"""
Groq API Integration for Natural Language Understanding
"""

from groq import Groq
import logging
from typing import List, Dict, Any
from utils.config import settings

logger = logging.getLogger(__name__)


class GroqAgent:
    """
    Groq AI Agent for handling natural language conversations
    with barbershop clients
    """
    
    def __init__(self):
        """Initialize Groq client"""
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        logger.info(f"Groq Agent initialized with model: {self.model}")
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """
        Generate AI response using Groq API
        
        Args:
            messages: List of conversation messages
            system_prompt: Optional system prompt to guide the AI
            temperature: Creativity level (0.0 to 1.0)
            max_tokens: Maximum response length
            
        Returns:
            AI-generated response text
        """
        try:
            # Prepare messages
            formatted_messages = []
            
            if system_prompt:
                formatted_messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            formatted_messages.extend(messages)
            
            # Call Groq API
            logger.debug(f"Sending {len(formatted_messages)} messages to Groq API")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1,
                stream=False
            )
            
            ai_response = response.choices[0].message.content
            logger.debug(f"Groq API response: {ai_response[:100]}...")
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            # Return fallback response
            return self._get_fallback_response()
    
    async def classify_intent(self, user_message: str) -> Dict[str, Any]:
        """
        Classify the intent of a user message
        
        Args:
            user_message: The user's message text
            
        Returns:
            Dictionary with intent and confidence
        """
        system_prompt = """You are an intent classifier for a barbershop receptionist.
        Classify the user's message into ONE of these intents:
        - greeting
        - book_appointment
        - update_appointment
        - cancel_appointment
        - check_availability
        - service_info
        - business_info
        - general_question
        
        Respond ONLY with a JSON object: {"intent": "intent_name", "confidence": 0.95}
        """
        
        try:
            messages = [{"role": "user", "content": user_message}]
            
            response = await self.generate_response(
                messages=messages,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=100
            )
            
            # Parse JSON response
            import json
            result = json.loads(response)
            
            logger.info(f"Intent classified: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error classifying intent: {e}")
            return {"intent": "unknown", "confidence": 0.0}
    
    async def extract_booking_info(self, conversation_text: str) -> Dict[str, Any]:
        """
        Extract booking information from conversation
        
        Args:
            conversation_text: Full conversation transcript
            
        Returns:
            Extracted booking details
        """
        system_prompt = """Extract booking information from the conversation.
        Return a JSON object with these fields (use null if not mentioned):
        {
            "client_name": "string",
            "service": "string",
            "date": "YYYY-MM-DD or description like 'tomorrow'",
            "time": "HH:MM or description like '3pm'",
            "barber": "string or null",
            "notes": "string or null"
        }
        """
        
        try:
            messages = [{"role": "user", "content": conversation_text}]
            
            response = await self.generate_response(
                messages=messages,
                system_prompt=system_prompt,
                temperature=0.2,
                max_tokens=200
            )
            
            # Parse JSON response
            import json
            info = json.loads(response)
            
            logger.info(f"Extracted booking info: {info}")
            return info
            
        except Exception as e:
            logger.error(f"Error extracting booking info: {e}")
            return {}
    
    def _get_fallback_response(self) -> str:
        """
        Return a fallback response when AI service is unavailable
        """
        return (
            "I apologize, but I'm having trouble processing your request right now. "
            "Please call us directly at " + settings.BUSINESS_PHONE + " "
            "or try again in a few moments."
        )


# Singleton instance
groq_agent = GroqAgent()
