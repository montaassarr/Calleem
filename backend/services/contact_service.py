"""
Contact Service
================
Service for managing contact form submissions.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from bson import ObjectId
import logging

from database.mongo_config import get_database
from models.contact import ContactCreate, ContactUpdate, ContactStatus, ContactStats

logger = logging.getLogger(__name__)


class ContactService:
    """Service for contact form operations"""
    
    def __init__(self):
        self.db = None
    
    def _get_db(self):
        if self.db is None:
            self.db = get_database()
        return self.db
    
    async def create_contact(self, contact: ContactCreate) -> dict:
        """Create a new contact submission"""
        db = self._get_db()
        
        contact_dict = {
            "full_name": contact.full_name,
            "email": contact.email,
            "business_name": contact.business_name,
            "business_type": contact.business_type,
            "phone_number": contact.phone_number,
            "monthly_calls": contact.monthly_calls,
            "message": contact.message,
            "newsletter": contact.newsletter,
            "privacy_policy": contact.privacy_policy,
            "status": ContactStatus.NEW.value,
            "admin_notes": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        result = await db.contacts.insert_one(contact_dict)
        contact_dict["_id"] = str(result.inserted_id)
        
        logger.info(f"New contact submission from {contact.email} - {contact.business_name}")
        
        return contact_dict
    
    async def get_contact(self, contact_id: str) -> Optional[dict]:
        """Get a single contact by ID"""
        db = self._get_db()
        
        contact = await db.contacts.find_one({"_id": ObjectId(contact_id)})
        if contact:
            contact["_id"] = str(contact["_id"])
        return contact
    
    async def list_contacts(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[ContactStatus] = None,
        search: Optional[str] = None
    ) -> List[dict]:
        """List all contact submissions"""
        db = self._get_db()
        
        query = {}
        if status:
            query["status"] = status.value
        if search:
            query["$or"] = [
                {"full_name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
                {"business_name": {"$regex": search, "$options": "i"}},
                {"phone_number": {"$regex": search, "$options": "i"}},
            ]
        
        cursor = db.contacts.find(query).sort("created_at", -1).skip(skip).limit(limit)
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        
        return results
    
    async def update_contact(self, contact_id: str, update: ContactUpdate) -> Optional[dict]:
        """Update a contact submission"""
        db = self._get_db()
        
        update_dict = {"updated_at": datetime.utcnow()}
        
        if update.status is not None:
            update_dict["status"] = update.status.value
        if update.admin_notes is not None:
            update_dict["admin_notes"] = update.admin_notes
        
        result = await db.contacts.find_one_and_update(
            {"_id": ObjectId(contact_id)},
            {"$set": update_dict},
            return_document=True
        )
        
        if result:
            result["_id"] = str(result["_id"])
        return result
    
    async def delete_contact(self, contact_id: str) -> bool:
        """Delete a contact submission"""
        db = self._get_db()
        
        result = await db.contacts.delete_one({"_id": ObjectId(contact_id)})
        return result.deleted_count > 0
    
    async def mark_as_read(self, contact_id: str) -> Optional[dict]:
        """Mark a contact as read"""
        update = ContactUpdate(status=ContactStatus.READ)
        return await self.update_contact(contact_id, update)
    
    async def get_stats(self) -> ContactStats:
        """Get contact submission statistics"""
        db = self._get_db()
        
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=now.weekday())
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get counts by status
        total = await db.contacts.count_documents({})
        new = await db.contacts.count_documents({"status": ContactStatus.NEW.value})
        read = await db.contacts.count_documents({"status": ContactStatus.READ.value})
        responded = await db.contacts.count_documents({"status": ContactStatus.RESPONDED.value})
        archived = await db.contacts.count_documents({"status": ContactStatus.ARCHIVED.value})
        
        # Get time-based counts
        today = await db.contacts.count_documents({"created_at": {"$gte": today_start}})
        this_week = await db.contacts.count_documents({"created_at": {"$gte": week_start}})
        this_month = await db.contacts.count_documents({"created_at": {"$gte": month_start}})
        
        return ContactStats(
            total=total,
            new=new,
            read=read,
            responded=responded,
            archived=archived,
            today=today,
            this_week=this_week,
            this_month=this_month
        )


# Singleton instance
contact_service = ContactService()


def get_contact_service() -> ContactService:
    """Dependency injection for contact service"""
    return contact_service
