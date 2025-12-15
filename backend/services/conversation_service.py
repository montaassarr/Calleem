import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException

from database.mongo_config import get_database
from models.conversation import ConversationResponse
from services.vapi_service import VapiService

logger = logging.getLogger(__name__)

class ConversationService:
    def __init__(self):
        self.vapi_service = VapiService()

    @property
    def db(self):
        return get_database()

    async def list_conversations(
        self, 
        tenant_id: str, 
        limit: int = 50, 
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List conversations from the database.
        """
        try:
            query = {}
            if tenant_id:
                query["tenant_id"] = tenant_id
            
            if search:
                query["phone_number"] = {"$regex": search, "$options": "i"}

            cursor = self.db.conversations.find(query).sort("updated_at", -1).limit(limit)
            conversations = await cursor.to_list(length=limit)

            formatted = []
            for conv in conversations:
                conv["id"] = str(conv["_id"])
                conv["_id"] = str(conv["_id"])
                formatted.append(conv)
            
            return formatted
        except Exception as e:
            logger.error(f"Error listing conversations: {e}")
            return []

    async def get_conversation(self, conversation_ref: str, tenant_id: str) -> Dict[str, Any]:
        """
        Get a single conversation by ID (Mongo ID or Conversation ID).
        If it's a Vapi call ID, try to enrich with Vapi data.
        """
        try:
            query = {}
            if ObjectId.is_valid(conversation_ref):
                query["_id"] = ObjectId(conversation_ref)
            else:
                query["conversation_id"] = conversation_ref
            
            if tenant_id:
                query["tenant_id"] = tenant_id

            conversation = await self.db.conversations.find_one(query)
            
            # If not found in DB, checks if it looks like a Vapi Call ID and user wants to fetch it?
            # For now, if not found locally, we return 404. 
            # But if found, we can check if we have missing details (transcript/recording) and fetch from Vapi.
            
            if conversation:
                conversation["id"] = str(conversation["_id"])
                conversation["_id"] = str(conversation["_id"])
                
                # Check if we need to enrich from Vapi
                # We assume 'source' or some metadata indicates it's a Vapi call
                # or if we map conversation_id to Vapi call ID.
                # Let's assume conversation_id IS the Vapi call ID for voice calls.
                
                # If specifically requested or if data missing, we could fetch details.
                # For now, let's expose a method to explicitly fetch Vapi details.
                
                return conversation
            else:
                raise HTTPException(status_code=404, detail="Conversation not found")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting conversation: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve conversation")

    async def get_vapi_call_details(self, call_id: str) -> Dict[str, Any]:
        """
        Fetch call details directly from Vapi API (recording, transcript).
        """
        if not self.vapi_service.is_configured():
             raise HTTPException(status_code=503, detail="Vapi service not configured")

        call_details = await self.vapi_service.get_call(call_id)
        if not call_details:
            raise HTTPException(status_code=404, detail="Call not found in Vapi")
            
        return call_details

    async def sync_vapi_calls(self, tenant_id: str, limit: int = 20):
        """
        Optional: Sync recent calls from Vapi to local DB.
        This could be useful if webhooks missed some calls.
        """
        if not self.vapi_service.is_configured():
            return
            
        # Get assistant ID for this tenant if possible, or just list all calls
        # Ideally we filter by assistant_id associated with tenant
        # For now, just listing calls and assuming we can map them back or they are global key
        
        calls = await self.vapi_service.list_calls(limit=limit)
        
        for call in calls:
            # Upsert into DB
            # Logic to map Vapi Call -> Conversation Model
            # This requires careful mapping of fields
            pass
