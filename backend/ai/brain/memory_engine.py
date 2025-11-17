"""
Memory Engine
Manages conversation memory and context tracking
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class ConversationMemory:
    """In-memory conversation context"""
    
    def __init__(self, conversation_id: str, phone_number: str):
        self.conversation_id = conversation_id
        self.phone_number = phone_number
        self.messages: List[Dict[str, Any]] = []
        self.context: Dict[str, Any] = {}
        self.collected_info: Dict[str, Any] = {}
        self.last_intent: Optional[str] = None
        self.pending_confirmation: bool = False
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def add_message(self, role: str, text: str, metadata: Dict[str, Any] = None):
        """Add a message to conversation history"""
        message = {
            "role": role,
            "text": text,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
    
    def update_context(self, key: str, value: Any):
        """Update conversation context"""
        self.context[key] = value
        self.updated_at = datetime.utcnow()
    
    def update_collected_info(self, updates: Dict[str, Any]):
        """Update collected booking information"""
        self.collected_info.update(updates)
        self.updated_at = datetime.utcnow()
    
    def get_recent_messages(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent messages for context"""
        return self.messages[-limit:]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "conversation_id": self.conversation_id,
            "phone_number": self.phone_number,
            "messages": self.messages,
            "context": self.context,
            "collected_info": self.collected_info,
            "last_intent": self.last_intent,
            "pending_confirmation": self.pending_confirmation,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class MemoryEngine:
    """
    Manages conversation memory with MongoDB persistence
    Provides short-term and long-term memory capabilities
    """
    
    def __init__(self):
        self._short_term_cache: Dict[str, ConversationMemory] = {}
    
    async def get_or_create_memory(
        self,
        db: AsyncIOMotorDatabase,
        phone_number: str,
        conversation_id: Optional[str] = None
    ) -> ConversationMemory:
        """
        Get existing conversation memory or create new one
        
        Args:
            db: MongoDB database
            phone_number: Client's phone number
            conversation_id: Optional specific conversation ID
            
        Returns:
            ConversationMemory instance
        """
        # Check short-term cache first
        cache_key = conversation_id or phone_number
        if cache_key in self._short_term_cache:
            memory = self._short_term_cache[cache_key]
            # Refresh if older than 1 hour
            age_seconds = (datetime.utcnow() - memory.updated_at).total_seconds()
            if age_seconds < 3600:
                logger.debug(f"Using cached memory for {cache_key}")
                return memory
        
        # Load from database
        if conversation_id:
            conv_doc = await db.conversations.find_one({"conversation_id": conversation_id})
        else:
            # Get most recent conversation for this phone number
            conv_doc = await db.conversations.find_one(
                {"phone_number": phone_number},
                sort=[("updated_at", -1)]
            )
        
        if conv_doc:
            # Reconstruct memory from database
            memory = self._memory_from_doc(conv_doc)
            logger.info(f"Loaded memory from DB: {memory.conversation_id}")
        else:
            # Create new memory
            from uuid import uuid4
            new_conv_id = f"conv_{uuid4().hex[:12]}"
            memory = ConversationMemory(new_conv_id, phone_number)
            logger.info(f"Created new memory: {new_conv_id}")
        
        # Cache it
        self._short_term_cache[cache_key] = memory
        return memory
    
    async def save_memory(
        self,
        db: AsyncIOMotorDatabase,
        memory: ConversationMemory
    ):
        """
        Persist conversation memory to MongoDB
        
        Args:
            db: MongoDB database
            memory: ConversationMemory to save
        """
        memory_dict = memory.to_dict()
        
        await db.conversations.update_one(
            {"conversation_id": memory.conversation_id},
            {"$set": memory_dict},
            upsert=True
        )
        
        logger.debug(f"Saved memory: {memory.conversation_id}")
    
    async def get_conversation_history(
        self,
        db: AsyncIOMotorDatabase,
        phone_number: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history for a phone number
        
        Args:
            db: MongoDB database
            phone_number: Client's phone number
            limit: Max conversations to return
            
        Returns:
            List of conversation documents
        """
        cursor = db.conversations.find(
            {"phone_number": phone_number}
        ).sort("created_at", -1).limit(limit)
        
        conversations = await cursor.to_list(length=limit)
        return conversations
    
    async def get_user_preferences(
        self,
        db: AsyncIOMotorDatabase,
        phone_number: str
    ) -> Dict[str, Any]:
        """
        Extract user preferences from conversation history
        
        Args:
            db: MongoDB database
            phone_number: Client's phone number
            
        Returns:
            Dictionary of preferences (favorite service, barber, time, etc.)
        """
        conversations = await self.get_conversation_history(db, phone_number, limit=10)
        
        preferences = {
            "favorite_service": None,
            "favorite_barber": None,
            "preferred_time": None,
            "typical_duration": 30,
            "last_service": None,
            "total_appointments": 0
        }
        
        # Analyze past appointments
        appointments = await db.appointments.find(
            {"client_phone": phone_number}
        ).sort("datetime", -1).to_list(length=20)
        
        preferences["total_appointments"] = len(appointments)
        
        if appointments:
            # Get most common service
            service_counts = {}
            barber_counts = {}
            time_hours = []
            
            for apt in appointments:
                service = apt.get("service")
                if service:
                    service_counts[service] = service_counts.get(service, 0) + 1
                
                barber = apt.get("barber_preference")
                if barber:
                    barber_counts[barber] = barber_counts.get(barber, 0) + 1
                
                apt_time = apt.get("datetime")
                if apt_time:
                    time_hours.append(apt_time.hour)
            
            # Determine favorites
            if service_counts:
                preferences["favorite_service"] = max(service_counts, key=service_counts.get)
                preferences["last_service"] = appointments[0].get("service")
            
            if barber_counts:
                preferences["favorite_barber"] = max(barber_counts, key=barber_counts.get)
            
            if time_hours:
                avg_hour = sum(time_hours) // len(time_hours)
                preferences["preferred_time"] = f"{avg_hour}:00"
        
        return preferences
    
    def _memory_from_doc(self, doc: Dict[str, Any]) -> ConversationMemory:
        """Reconstruct ConversationMemory from database document"""
        memory = ConversationMemory(
            doc.get("conversation_id"),
            doc.get("phone_number")
        )
        
        memory.messages = doc.get("messages", [])
        memory.context = doc.get("context", {})
        memory.collected_info = doc.get("collected_info", {})
        memory.last_intent = doc.get("last_intent")
        memory.pending_confirmation = doc.get("pending_confirmation", False)
        memory.created_at = doc.get("created_at", datetime.utcnow())
        memory.updated_at = doc.get("updated_at", datetime.utcnow())
        
        return memory
    
    def clear_cache(self, phone_number: Optional[str] = None):
        """Clear short-term memory cache"""
        if phone_number:
            keys_to_delete = [k for k in self._short_term_cache.keys() if phone_number in k]
            for key in keys_to_delete:
                del self._short_term_cache[key]
        else:
            self._short_term_cache.clear()


# Singleton instance
memory_engine = MemoryEngine()
