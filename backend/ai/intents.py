"""
Intent Classification and Recognition
"""

from enum import Enum
from typing import Dict, List, Optional
import re
from models.communication.conversations import ConversationIntent


class IntentKeywords:
    """Keyword patterns for intent recognition"""
    
    BOOKING_KEYWORDS = [
        "book", "appointment", "schedule", "reserve", "haircut",
        "trim", "cut", "fade", "shave", "make an appointment",
        "set up", "want to come in", "need a"
    ]
    
    UPDATE_KEYWORDS = [
        "change", "reschedule", "move", "update", "switch",
        "different time", "different day", "modify"
    ]
    
    CANCEL_KEYWORDS = [
        "cancel", "delete", "remove", "can't make it",
        "won't make it", "need to cancel"
    ]
    
    AVAILABILITY_KEYWORDS = [
        "available", "availability", "open", "free",
        "time slots", "when can", "do you have"
    ]
    
    SERVICE_INFO_KEYWORDS = [
        "services", "what do you offer", "what services",
        "types of", "kind of cuts", "what can you do",
        "price", "cost", "how much"
    ]
    
    BUSINESS_INFO_KEYWORDS = [
        "hours", "when are you open", "location", "address",
        "where are you", "how to get there", "phone",
        "contact", "email"
    ]
    
    GREETING_KEYWORDS = [
        "hi", "hello", "hey", "good morning", "good afternoon",
        "good evening", "what's up", "greetings"
    ]


class IntentClassifier:
    """
    Rule-based and keyword-based intent classification
    (Fallback for when Groq API is not used)
    """
    
    @staticmethod
    def classify(message: str, conversation_history: List[Dict] = None) -> ConversationIntent:
        """
        Classify user message intent
        
        Args:
            message: User's message text
            conversation_history: Previous messages for context
            
        Returns:
            ConversationIntent enum value
        """
        message_lower = message.lower()
        
        # Check for greeting (usually at start of conversation)
        if IntentClassifier._is_greeting(message_lower, conversation_history):
            return ConversationIntent.GREETING
        
        # Check for cancellation
        if any(keyword in message_lower for keyword in IntentKeywords.CANCEL_KEYWORDS):
            return ConversationIntent.CANCEL_APPOINTMENT
        
        # Check for rescheduling/update
        if any(keyword in message_lower for keyword in IntentKeywords.UPDATE_KEYWORDS):
            return ConversationIntent.UPDATE_APPOINTMENT
        
        # Check for availability
        if any(keyword in message_lower for keyword in IntentKeywords.AVAILABILITY_KEYWORDS):
            return ConversationIntent.CHECK_AVAILABILITY
        
        # Check for service information
        if any(keyword in message_lower for keyword in IntentKeywords.SERVICE_INFO_KEYWORDS):
            return ConversationIntent.SERVICE_INFO
        
        # Check for business information
        if any(keyword in message_lower for keyword in IntentKeywords.BUSINESS_INFO_KEYWORDS):
            return ConversationIntent.BUSINESS_INFO
        
        # Check for booking (default for many messages)
        if any(keyword in message_lower for keyword in IntentKeywords.BOOKING_KEYWORDS):
            return ConversationIntent.BOOK_APPOINTMENT
        
        # If in active booking conversation, continue as booking
        if conversation_history and IntentClassifier._is_in_booking_flow(conversation_history):
            return ConversationIntent.BOOK_APPOINTMENT
        
        # Default to general question
        return ConversationIntent.GENERAL_QUESTION
    
    @staticmethod
    def _is_greeting(message: str, history: List[Dict] = None) -> bool:
        """Check if message is a greeting"""
        # Only consider it a greeting if it's the first message or very short
        if history and len(history) > 1:
            return False
        
        # Check for greeting keywords
        return any(keyword in message for keyword in IntentKeywords.GREETING_KEYWORDS)
    
    @staticmethod
    def _is_in_booking_flow(history: List[Dict]) -> bool:
        """
        Check if conversation is currently in booking flow
        """
        # Look at last few messages for booking-related content
        recent_messages = history[-3:] if len(history) >= 3 else history
        
        for msg in recent_messages:
            if isinstance(msg, dict) and 'text' in msg:
                text = msg['text'].lower()
                if any(kw in text for kw in IntentKeywords.BOOKING_KEYWORDS):
                    return True
        
        return False
    
    @staticmethod
    def extract_entities(message: str) -> Dict[str, Optional[str]]:
        """
        Extract entities from message using regex patterns
        
        Args:
            message: User's message text
            
        Returns:
            Dictionary of extracted entities
        """
        entities = {
            "name": None,
            "phone": None,
            "email": None,
            "time": None,
            "date": None,
            "service": None
        }
        
        # Extract phone number
        phone_pattern = r'(\+?1?\d{9,15})'
        phone_match = re.search(phone_pattern, message)
        if phone_match:
            entities["phone"] = phone_match.group(1)
        
        # Extract email
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        email_match = re.search(email_pattern, message.lower())
        if email_match:
            entities["email"] = email_match.group(0)
        
        # Extract time (simple patterns)
        time_patterns = [
            r'(\d{1,2}:\d{2}\s*(?:am|pm)?)',
            r'(\d{1,2}\s*(?:am|pm))',
            r'(noon|midnight)'
        ]
        for pattern in time_patterns:
            time_match = re.search(pattern, message.lower())
            if time_match:
                entities["time"] = time_match.group(1)
                break
        
        # Extract date keywords
        date_keywords = ["today", "tomorrow", "monday", "tuesday", "wednesday",
                        "thursday", "friday", "saturday", "sunday",
                        "next week", "this week"]
        for keyword in date_keywords:
            if keyword in message.lower():
                entities["date"] = keyword
                break
        
        # Extract service mentions
        from utils.config import settings
        services = settings.AVAILABLE_SERVICES.lower().split(",")
        for service in services:
            if service.strip() in message.lower():
                entities["service"] = service.strip()
                break
        
        return entities


# Singleton instance
intent_classifier = IntentClassifier()
