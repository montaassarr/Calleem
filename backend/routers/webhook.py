"""
Webhook Router
Handles inbound SMS/WhatsApp from Twilio and status endpoints
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, HTTPException, status
from twilio.twiml.messaging_response import MessagingResponse
from fastapi.responses import Response
from datetime import datetime
from bson import ObjectId

from database.mongo_config import get_database
from services.twilio_messaging import twilio_messaging
from utils.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


async def resolve_tenant_from_phone(phone_number: str) -> Optional[str]:
    """
    Resolve tenant_id from incoming phone number.
    Looks up by Twilio number mapping or returns None.
    
    Future: Can be enhanced to lookup by phone number in appointments/conversations.
    """
    try:
        db = get_database()
        
        # Resolve only from tenant-owned phone configuration.
        tenant = await db.tenants.find_one({
            "$or": [
                {"phone_config.phone_number": phone_number},
                {"phone_config.twilio_credentials.phone_number": phone_number},
                {"phone_config.is_active": True, "phone_config.phone_number": phone_number},
            ]
        })
        
        if tenant:
            return str(tenant.get("_id"))
        
        return None
    except Exception as e:
        logger.error(f"Error resolving tenant from phone {phone_number}: {e}")
        return None


@router.post("/sms")
async def receive_sms(request: Request):
    """
    Receive inbound SMS from Twilio Messaging Service.
    Twilio sends a POST with form-encoded data.
    """
    try:
        # Parse Twilio webhook payload
        form_data = await request.form()
        
        from_number = form_data.get("From", "")  # Sender's number
        to_number = form_data.get("To", "")      # Twilio number that received it
        message_text = form_data.get("Body", "")
        message_sid = form_data.get("MessageSid", "")
        account_sid = form_data.get("AccountSid", "")
        
        logger.info(f"📨 Received inbound SMS from {from_number} to {to_number}: {message_text[:50]}...")
        
        # Optional: Validate Twilio signature (recommended for production)
        # TODO: Implement signature validation using Twilio auth token
        
        # Resolve tenant from phone number
        tenant_id = await resolve_tenant_from_phone(to_number)
        
        if not tenant_id:
            logger.warning(f"Could not resolve tenant for Twilio number {to_number}")
            # Return TwiML response anyway (Twilio expects valid XML/TwiML)
            resp = MessagingResponse()
            resp.message("Thank you for your message. Unable to process at this time.")
            return Response(str(resp), media_type="application/xml")
        
        logger.info(f"Resolved tenant {tenant_id} for inbound SMS")
        
        # Store inbound conversation in database
        db = get_database()
        conversation_doc = {
            "tenant_id": tenant_id,
            "type": "sms",
            "customer_phone": from_number,
            "twilio_number": to_number,
            "message_sid": message_sid,
            "direction": "inbound",
            "message": message_text,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "status": "received"
        }
        
        inserted = await db.sms_conversations.insert_one(conversation_doc)
        logger.info(f"Stored inbound SMS: {inserted.inserted_id}")
        
        # TODO: Forward to Vapi assistant for processing (requires Vapi chat API integration)
        # For now, send a simple acknowledgment
        
        # Build TwiML response (required by Twilio)
        resp = MessagingResponse()
        resp.message("Thank you for your message! We'll get back to you shortly.")
        
        return Response(str(resp), media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error processing inbound SMS: {e}")
        # Still return valid TwiML to acknowledge receipt
        resp = MessagingResponse()
        resp.message("Thank you for your message.")
        return Response(str(resp), media_type="application/xml")


@router.post("/whatsapp")
async def receive_whatsapp(request: Request):
    """
    Receive inbound WhatsApp messages from Twilio WhatsApp Sandbox.
    Similar to SMS but with WhatsApp-specific handling.
    """
    try:
        # Parse Twilio webhook payload
        form_data = await request.form()
        
        from_number = form_data.get("From", "")  # whatsapp:+1234567890
        to_number = form_data.get("To", "")      # whatsapp:+1234567890
        message_text = form_data.get("Body", "")
        message_sid = form_data.get("MessageSid", "")
        
        logger.info(f"💬 Received inbound WhatsApp from {from_number}: {message_text[:50]}...")
        
        # Remove "whatsapp:" prefix for phone lookup
        from_phone = from_number.replace("whatsapp:", "")
        to_phone = to_number.replace("whatsapp:", "")
        
        # Resolve tenant
        tenant_id = await resolve_tenant_from_phone(to_phone)
        
        if not tenant_id:
            logger.warning(f"Could not resolve tenant for WhatsApp number {to_phone}")
            resp = MessagingResponse()
            resp.message("Thank you for your message. Unable to process at this time.")
            return Response(str(resp), media_type="application/xml")
        
        # Store conversation
        db = get_database()
        conversation_doc = {
            "tenant_id": tenant_id,
            "type": "whatsapp",
            "customer_phone": from_phone,
            "whatsapp_number": to_phone,
            "message_sid": message_sid,
            "direction": "inbound",
            "message": message_text,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "status": "received"
        }
        
        inserted = await db.whatsapp_conversations.insert_one(conversation_doc)
        logger.info(f"Stored inbound WhatsApp: {inserted.inserted_id}")
        
        # TODO: Forward to Vapi assistant
        
        resp = MessagingResponse()
        resp.message("Thank you for your message! We'll get back to you shortly.")
        
        return Response(str(resp), media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error processing inbound WhatsApp: {e}")
        resp = MessagingResponse()
        resp.message("Thank you for your message.")
        return Response(str(resp), media_type="application/xml")


@router.get("/status")
async def webhook_status():
    """
    Simple status check endpoint for webhooks.
    Can be used by frontend to verify webhook connectivity.
    """
    try:
        twilio_configured = twilio_messaging.is_configured()
        
        return {
            "status": "healthy",
            "webhooks": {
                "sms": {
                    "endpoint": f"{settings.API_V1_PREFIX}/webhook/sms",
                    "configured": True
                },
                "whatsapp": {
                    "endpoint": f"{settings.API_V1_PREFIX}/webhook/whatsapp",
                    "configured": True
                }
            },
            "twilio": {
                "configured": twilio_configured,
                "messaging_service_sid": "***" if twilio_messaging.messaging_service_sid else None
            }
        }
    except Exception as e:
        logger.error(f"Error checking webhook status: {e}")
        raise HTTPException(status_code=500, detail="Failed to check webhook status")
