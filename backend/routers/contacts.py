"""
Contact API Router
==================
Public endpoints for contact form submissions and admin endpoints for management.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
import logging

from models.contact import ContactCreate, ContactUpdate, ContactResponse, ContactStatus, ContactStats
from services.contact_service import get_contact_service, ContactService

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== PUBLIC ENDPOINTS ====================

@router.post("", response_model=ContactResponse, status_code=201)
async def submit_contact(
    contact: ContactCreate,
    service: ContactService = Depends(get_contact_service)
):
    """
    Submit a contact form (public endpoint - no auth required).
    This is called from the landing page contact form.
    """
    try:
        created = await service.create_contact(contact)
        return ContactResponse(
            id=created["_id"],
            full_name=created["full_name"],
            email=created["email"],
            business_name=created["business_name"],
            business_type=created["business_type"],
            phone_number=created["phone_number"],
            monthly_calls=created["monthly_calls"],
            message=created.get("message"),
            newsletter=created.get("newsletter", False),
            status=created.get("status", ContactStatus.NEW),
            admin_notes=created.get("admin_notes"),
            created_at=created.get("created_at"),
            updated_at=created.get("updated_at"),
        )
    except Exception as e:
        logger.error(f"Failed to submit contact form: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit contact form")


# ==================== ADMIN ENDPOINTS ====================

@router.get("", response_model=List[ContactResponse])
async def list_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[ContactStatus] = None,
    search: Optional[str] = None,
    service: ContactService = Depends(get_contact_service)
):
    """List all contact submissions (admin endpoint)"""
    results = await service.list_contacts(skip, limit, status, search)
    return [
        ContactResponse(
            id=c["_id"],
            full_name=c["full_name"],
            email=c["email"],
            business_name=c["business_name"],
            business_type=c["business_type"],
            phone_number=c["phone_number"],
            monthly_calls=c["monthly_calls"],
            message=c.get("message"),
            newsletter=c.get("newsletter", False),
            status=c.get("status", ContactStatus.NEW),
            admin_notes=c.get("admin_notes"),
            created_at=c.get("created_at"),
            updated_at=c.get("updated_at"),
        )
        for c in results
    ]


@router.get("/stats", response_model=ContactStats)
async def get_contact_stats(
    service: ContactService = Depends(get_contact_service)
):
    """Get contact submission statistics"""
    return await service.get_stats()


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: str,
    service: ContactService = Depends(get_contact_service)
):
    """Get a single contact submission"""
    contact = await service.get_contact(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return ContactResponse(
        id=contact["_id"],
        full_name=contact["full_name"],
        email=contact["email"],
        business_name=contact["business_name"],
        business_type=contact["business_type"],
        phone_number=contact["phone_number"],
        monthly_calls=contact["monthly_calls"],
        message=contact.get("message"),
        newsletter=contact.get("newsletter", False),
        status=contact.get("status", ContactStatus.NEW),
        admin_notes=contact.get("admin_notes"),
        created_at=contact.get("created_at"),
        updated_at=contact.get("updated_at"),
    )


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: str,
    update: ContactUpdate,
    service: ContactService = Depends(get_contact_service)
):
    """Update a contact submission (change status, add notes)"""
    updated = await service.update_contact(contact_id, update)
    if not updated:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return ContactResponse(
        id=updated["_id"],
        full_name=updated["full_name"],
        email=updated["email"],
        business_name=updated["business_name"],
        business_type=updated["business_type"],
        phone_number=updated["phone_number"],
        monthly_calls=updated["monthly_calls"],
        message=updated.get("message"),
        newsletter=updated.get("newsletter", False),
        status=updated.get("status", ContactStatus.NEW),
        admin_notes=updated.get("admin_notes"),
        created_at=updated.get("created_at"),
        updated_at=updated.get("updated_at"),
    )


@router.post("/{contact_id}/mark-read", response_model=ContactResponse)
async def mark_contact_read(
    contact_id: str,
    service: ContactService = Depends(get_contact_service)
):
    """Mark a contact as read"""
    updated = await service.mark_as_read(contact_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return ContactResponse(
        id=updated["_id"],
        full_name=updated["full_name"],
        email=updated["email"],
        business_name=updated["business_name"],
        business_type=updated["business_type"],
        phone_number=updated["phone_number"],
        monthly_calls=updated["monthly_calls"],
        message=updated.get("message"),
        newsletter=updated.get("newsletter", False),
        status=updated.get("status", ContactStatus.NEW),
        admin_notes=updated.get("admin_notes"),
        created_at=updated.get("created_at"),
        updated_at=updated.get("updated_at"),
    )


@router.delete("/{contact_id}", status_code=204)
async def delete_contact(
    contact_id: str,
    service: ContactService = Depends(get_contact_service)
):
    """Delete a contact submission"""
    deleted = await service.delete_contact(contact_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Contact not found")
