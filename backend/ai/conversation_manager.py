"""
Conversation State Management
Tracks conversation flow and manages state across multiple messages
"""

import uuid
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from models.conversation import (
    Message, MessageRole, ConversationIntent,
    ConversationState, ConversationInDB
)
from ai.groq_agent import groq_agent
from ai.prompt_templates import prompt_templates
from ai.intents import intent_classifier
from database.mongo_config import get_database

logger = logging.getLogger(__name__)


class ConversationManager:
    """
    Manages conversation state and generates appropriate AI responses
    """
    
    def __init__(self):
        """Initialize conversation manager"""
        self.db = None
    
    async def initialize(self):
        """Initialize database connection"""
        self.db = get_database()
    
    async def process_message(
        self,
        phone_number: str,
        message_text: str,
        twilio_metadata: Dict = None
    ) -> Dict[str, Any]:
        """
        Process incoming message and generate response
        
        Args:
            phone_number: Client's phone number
            message_text: The message text
            twilio_metadata: Optional Twilio message metadata
            
        Returns:
            Dictionary with AI response and updated state
        """
        try:
            # Ensure DB is initialized
            if not self.db:
                await self.initialize()
            
            # Get or create conversation
            conversation = await self._get_or_create_conversation(phone_number)
            
            # Add client message to conversation
            client_message = Message(
                role=MessageRole.CLIENT,
                text=message_text,
                timestamp=datetime.utcnow(),
                metadata=twilio_metadata
            )
            conversation["messages"].append(client_message.dict())
            
            # Determine intent if not already set or if new conversation
            if not conversation["state"]["intent"] or conversation["state"]["intent"] == "unknown":
                intent = await self._classify_intent(message_text, conversation["messages"])
                conversation["state"]["intent"] = intent
            else:
                intent = conversation["state"]["intent"]
            
            # Extract entities from message
            entities = intent_classifier.extract_entities(message_text)
            
            # Update collected information
            for key, value in entities.items():
                if value:
                    conversation["state"]["collected_info"][key] = value
            
            # Generate AI response based on intent and state
            ai_response_text = await self._generate_response(
                intent=intent,
                message_text=message_text,
                conversation=conversation
            )
            
            # Add AI response to conversation
            ai_message = Message(
                role=MessageRole.AI,
                text=ai_response_text,
                timestamp=datetime.utcnow()
            )
            conversation["messages"].append(ai_message.dict())
            
            # Update conversation in database
            conversation["updated_at"] = datetime.utcnow()
            await self._save_conversation(conversation)
            
            return {
                "response": ai_response_text,
                "intent": intent,
                "conversation_id": conversation["conversation_id"],
                "state": conversation["state"]
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return {
                "response": "I apologize, but I'm having trouble right now. Please try again.",
                "error": str(e)
            }
    
    async def _get_or_create_conversation(self, phone_number: str) -> Dict:
        """Get existing conversation or create new one"""
        
        # Try to find recent conversation (within last 24 hours)
        recent_conversation = await self.db.conversations.find_one({
            "phone_number": phone_number,
            "created_at": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0)}
        }, sort=[("created_at", -1)])
        
        if recent_conversation:
            logger.info(f"Found existing conversation: {recent_conversation['conversation_id']}")
            return recent_conversation
        
        # Create new conversation
        conversation_id = f"conv_{uuid.uuid4().hex[:12]}"
        conversation = {
            "conversation_id": conversation_id,
            "phone_number": phone_number,
            "messages": [],
            "state": {
                "intent": "unknown",
                "collected_info": {},
                "next_question": None,
                "completed": False
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "appointment_id": None
        }
        
        logger.info(f"Created new conversation: {conversation_id}")
        return conversation
    
    async def _classify_intent(
        self,
        message: str,
        conversation_history: List[Dict]
    ) -> str:
        """Classify the intent of the message"""
        
        try:
            # Use Groq for intent classification
            result = await groq_agent.classify_intent(message)
            intent = result.get("intent", "unknown")
            
            logger.info(f"Intent classified as: {intent}")
            return intent
            
        except Exception as e:
            logger.error(f"Error in AI intent classification: {e}")
            # Fallback to rule-based classification
            intent = intent_classifier.classify(message, conversation_history)
            logger.info(f"Fallback intent: {intent}")
            return intent.value
    
    async def _generate_response(
        self,
        intent: str,
        message_text: str,
        conversation: Dict
    ) -> str:
        """Generate AI response based on intent and conversation state"""
        
        try:
            # Build conversation context for AI
            messages = []
            
            # Add recent message history (last 10 messages)
            recent_messages = conversation["messages"][-10:]
            for msg in recent_messages:
                messages.append({
                    "role": "user" if msg["role"] == "client" else "assistant",
                    "content": msg["text"]
                })
            
            # Get appropriate system prompt based on intent
            system_prompt = prompt_templates.get_system_prompt()
            
            # Special handling for first message (greeting)
            if len(conversation["messages"]) == 1:
                system_prompt += "\n\n" + prompt_templates.get_greeting_prompt()
            
            # Generate response using Groq
            response = await groq_agent.generate_response(
                messages=messages,
                system_prompt=system_prompt,
                temperature=0.7
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble right now. Please try again in a moment."
    
    async def _save_conversation(self, conversation: Dict):
        """Save or update conversation in database"""
        
        try:
            result = await self.db.conversations.update_one(
                {"conversation_id": conversation["conversation_id"]},
                {"$set": conversation},
                upsert=True
            )
            
            logger.debug(f"Conversation saved: {conversation['conversation_id']}")
            
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
    
    async def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Retrieve a conversation by ID"""
        
        conversation = await self.db.conversations.find_one({
            "conversation_id": conversation_id
        })
        
        return conversation
    
    async def complete_conversation(
        self,
        conversation_id: str,
        appointment_id: str = None
    ):
        """Mark conversation as completed"""
        
        await self.db.conversations.update_one(
            {"conversation_id": conversation_id},
            {
                "$set": {
                    "state.completed": True,
                    "appointment_id": appointment_id,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Conversation {conversation_id} marked as completed")


# Singleton instance
conversation_manager = ConversationManager()
