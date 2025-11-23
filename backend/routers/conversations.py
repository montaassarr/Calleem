"""
Conversations API Router
Provides read-only access to stored AI conversations for the dashboard
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from bson import ObjectId
import logging

from models.conversation import ConversationResponse
from database.mongo_config import get_database

logger = logging.getLogger(__name__)

router = APIRouter()


def _with_id(document: dict) -> dict:
    """Helper to attach string id to Mongo documents"""
    document["id"] = str(document["_id"])
    return document


@router.get("/", response_model=List[ConversationResponse])
async def list_conversations(
    search: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200)
):
    """Return recent conversations ordered by last update"""
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Database connection not initialized")

    query = {}
    if search:
        query["phone_number"] = {"$regex": search, "$options": "i"}

    cursor = db.conversations.find(query).sort("updated_at", -1).limit(limit)
    conversations = await cursor.to_list(length=limit)

    logger.info("Retrieved %s conversations", len(conversations))

    return [ConversationResponse(**_with_id(convo)) for convo in conversations]


@router.get("/{conversation_ref}", response_model=ConversationResponse)
async def get_conversation(conversation_ref: str):
    """Fetch a single conversation by Mongo _id or conversation_id"""
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Database connection not initialized")

    query = {"conversation_id": conversation_ref}
    if ObjectId.is_valid(conversation_ref):
        query = {"_id": ObjectId(conversation_ref)}

    conversation = await db.conversations.find_one(query)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return ConversationResponse(**_with_id(conversation))


@router.delete("/{conversation_ref}", status_code=204)
async def delete_conversation(conversation_ref: str):
    """Delete a conversation by Mongo _id or conversation_id"""
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Database connection not initialized")

    query = {"conversation_id": conversation_ref}
    if ObjectId.is_valid(conversation_ref):
        query = {"_id": ObjectId(conversation_ref)}

    # Delete the conversation
    result = await db.conversations.delete_one(query)
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Also delete related conversation history entries
    await db.conversation_history.delete_many({"conversationId": conversation_ref})
    
    logger.info(f"Deleted conversation: {conversation_ref}")
    
    return None
