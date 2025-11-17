"""
Intent Classification Engine
Uses Instructor + Pydantic for structured LLM outputs
"""

import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class IntentType(str, Enum):
    """Supported conversation intents"""
    GREETING = "greeting"
    BOOK_APPOINTMENT = "book_appointment"
    UPDATE_APPOINTMENT = "update_appointment"
    CANCEL_APPOINTMENT = "cancel_appointment"
    CHECK_AVAILABILITY = "check_availability"
    SERVICE_INFO = "service_info"
    BUSINESS_INFO = "business_info"
    GENERAL_QUESTION = "general_question"
    UNKNOWN = "unknown"


class IntentClassification(BaseModel):
    """Structured intent classification result"""
    intent: IntentType
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = Field(min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "intent": "book_appointment",
                "confidence": 0.95,
                "reasoning": "User explicitly mentioned wanting to schedule a haircut"
            }
        }


class EntityExtraction(BaseModel):
    """Structured entity extraction result"""
    client_name: Optional[str] = None
    client_email: Optional[str] = None
    client_phone: Optional[str] = None
    service: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    barber_preference: Optional[str] = None
    notes: Optional[str] = None
    duration_minutes: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "client_name": "John Smith",
                "service": "Haircut",
                "date": "tomorrow",
                "time": "2pm",
                "duration_minutes": 30
            }
        }


class IntentClassifierEngine:
    """
    Advanced intent classification using structured outputs
    Can use Instructor library for guaranteed JSON responses
    """
    
    def __init__(self):
        self.use_instructor = False  # Will be enabled when instructor is available
        try:
            import instructor
            self.use_instructor = True
            logger.info("Instructor library available - using structured outputs")
        except ImportError:
            logger.warning("Instructor not available - using JSON parsing fallback")
    
    async def classify_intent(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        groq_client: Any = None
    ) -> IntentClassification:
        """
        Classify user intent with structured output
        
        Args:
            message: User's message text
            context: Optional conversation context
            groq_client: Groq API client (if using Instructor)
            
        Returns:
            IntentClassification object
        """
        if self.use_instructor and groq_client:
            return await self._classify_with_instructor(message, context, groq_client)
        else:
            return await self._classify_with_json_parsing(message, context)
    
    async def extract_entities(
        self,
        message: str,
        conversation_history: Optional[str] = None,
        groq_client: Any = None
    ) -> EntityExtraction:
        """
        Extract entities with structured output
        
        Args:
            message: User's message text
            conversation_history: Full conversation transcript
            groq_client: Groq API client
            
        Returns:
            EntityExtraction object
        """
        if self.use_instructor and groq_client:
            return await self._extract_with_instructor(message, conversation_history, groq_client)
        else:
            return await self._extract_with_json_parsing(message, conversation_history)
    
    async def _classify_with_instructor(
        self,
        message: str,
        context: Optional[Dict[str, Any]],
        groq_client: Any
    ) -> IntentClassification:
        """Classify using Instructor for guaranteed structured output"""
        try:
            import instructor
            
            # Wrap Groq client with Instructor
            client = instructor.patch(groq_client.client)
            
            prompt = f"""Classify the intent of this message: "{message}"

Context: {json.dumps(context) if context else 'None'}

Determine the user's primary intent."""
            
            response = client.chat.completions.create(
                model=groq_client.model,
                messages=[
                    {"role": "system", "content": "You are an intent classifier for a barbershop."},
                    {"role": "user", "content": prompt}
                ],
                response_model=IntentClassification,
                temperature=0.3
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Instructor classification failed: {e}")
            return await self._classify_with_json_parsing(message, context)
    
    async def _classify_with_json_parsing(
        self,
        message: str,
        context: Optional[Dict[str, Any]]
    ) -> IntentClassification:
        """Fallback classification with JSON parsing"""
        # Simple rule-based classification
        message_lower = message.lower()
        
        # Check for keywords
        if any(word in message_lower for word in ["hi", "hello", "hey", "good morning"]):
            return IntentClassification(
                intent=IntentType.GREETING,
                confidence=0.9,
                reasoning="Greeting keywords detected"
            )
        
        if any(word in message_lower for word in ["book", "appointment", "schedule", "haircut", "trim"]):
            return IntentClassification(
                intent=IntentType.BOOK_APPOINTMENT,
                confidence=0.85,
                reasoning="Booking-related keywords detected"
            )
        
        if any(word in message_lower for word in ["cancel", "can't make it"]):
            return IntentClassification(
                intent=IntentType.CANCEL_APPOINTMENT,
                confidence=0.9,
                reasoning="Cancellation keywords detected"
            )
        
        if any(word in message_lower for word in ["change", "reschedule", "move"]):
            return IntentClassification(
                intent=IntentType.UPDATE_APPOINTMENT,
                confidence=0.85,
                reasoning="Rescheduling keywords detected"
            )
        
        if any(word in message_lower for word in ["available", "free", "open"]):
            return IntentClassification(
                intent=IntentType.CHECK_AVAILABILITY,
                confidence=0.8,
                reasoning="Availability check keywords detected"
            )
        
        if any(word in message_lower for word in ["service", "price", "cost", "how much"]):
            return IntentClassification(
                intent=IntentType.SERVICE_INFO,
                confidence=0.8,
                reasoning="Service information keywords detected"
            )
        
        if any(word in message_lower for word in ["hours", "location", "address", "where"]):
            return IntentClassification(
                intent=IntentType.BUSINESS_INFO,
                confidence=0.8,
                reasoning="Business information keywords detected"
            )
        
        return IntentClassification(
            intent=IntentType.UNKNOWN,
            confidence=0.5,
            reasoning="No clear intent detected"
        )
    
    async def _extract_with_instructor(
        self,
        message: str,
        conversation_history: Optional[str],
        groq_client: Any
    ) -> EntityExtraction:
        """Extract entities using Instructor"""
        try:
            import instructor
            
            client = instructor.patch(groq_client.client)
            
            context = conversation_history if conversation_history else message
            
            prompt = f"""Extract booking information from this conversation:

{context}

Extract all relevant details. If a detail isn't mentioned, leave it as null."""
            
            response = client.chat.completions.create(
                model=groq_client.model,
                messages=[
                    {"role": "system", "content": "You extract booking details from conversations."},
                    {"role": "user", "content": prompt}
                ],
                response_model=EntityExtraction,
                temperature=0.2
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Instructor extraction failed: {e}")
            return await self._extract_with_json_parsing(message, conversation_history)
    
    async def _extract_with_json_parsing(
        self,
        message: str,
        conversation_history: Optional[str]
    ) -> EntityExtraction:
        """Fallback entity extraction with regex"""
        import re
        
        entities = EntityExtraction()
        text = conversation_history if conversation_history else message
        
        # Extract phone number
        phone_match = re.search(r'(\+?1?\d{9,15})', text)
        if phone_match:
            entities.client_phone = phone_match.group(1)
        
        # Extract email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text.lower())
        if email_match:
            entities.client_email = email_match.group(0)
        
        # Extract time
        time_patterns = [
            r'(\d{1,2}:\d{2}\s*(?:am|pm)?)',
            r'(\d{1,2}\s*(?:am|pm))'
        ]
        for pattern in time_patterns:
            time_match = re.search(pattern, text.lower())
            if time_match:
                entities.time = time_match.group(1)
                break
        
        # Extract date keywords
        date_keywords = ["today", "tomorrow", "monday", "tuesday", "wednesday",
                        "thursday", "friday", "saturday", "sunday"]
        for keyword in date_keywords:
            if keyword in text.lower():
                entities.date = keyword
                break
        
        return entities


# Singleton instance
intent_classifier_engine = IntentClassifierEngine()
