"""
Conversation Service - Handles conversation queries
"""

from typing import List, Optional, Dict, Any
from bson import ObjectId
import logging

from database.mongo_config import get_database
from services.vapi_service import vapi_service

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for managing conversation data"""
    
    async def list_conversations(
        self, 
        tenant_id: str, 
        limit: int = 50, 
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List conversations for a tenant"""
        try:
            db = get_database()
            
            # Build query
            query = {"tenant_id": tenant_id}
            if search:
                query["$or"] = [
                    {"customer_name": {"$regex": search, "$options": "i"}},
                    {"customer_phone": {"$regex": search, "$options": "i"}},
                    {"conversation_id": {"$regex": search, "$options": "i"}}
                ]
            
            # Fetch conversations
            cursor = db.conversations.find(query).sort("updated_at", -1).limit(limit)
            conversations = await cursor.to_list(length=limit)
            
            # Convert ObjectId to string
            for conv in conversations:
                conv["_id"] = str(conv["_id"])
            
            return conversations
            
        except Exception as e:
            logger.error(f"Error listing conversations: {e}")
            return []
    
    async def get_conversation(self, conversation_ref: str, tenant_id: str) -> Dict[str, Any]:
        """Get a single conversation by ID or conversation_id"""
        try:
            db = get_database()
            
            # Try as ObjectId first
            query = {"tenant_id": tenant_id}
            try:
                query["_id"] = ObjectId(conversation_ref)
            except:
                # If not valid ObjectId, try as conversation_id
                query = {"tenant_id": tenant_id, "conversation_id": conversation_ref}
            
            conversation = await db.conversations.find_one(query)
            
            if not conversation:
                raise ValueError(f"Conversation {conversation_ref} not found")
            
            conversation["_id"] = str(conversation["_id"])
            return conversation
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error getting conversation: {e}")
            raise ValueError(f"Failed to retrieve conversation: {str(e)}")
    
    async def get_vapi_call_details(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Get Vapi call details including recording and transcript"""
        try:
            if not vapi_service.api_key:
                logger.warning("Vapi API key not configured")
                return None
            
            return await vapi_service.get_call_details(call_id)
            
        except Exception as e:
            logger.error(f"Error getting Vapi call details: {e}")
            return None
