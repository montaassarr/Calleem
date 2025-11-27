"""
WhatsApp Cloud API Webhook Router
Handles incoming messages from WhatsApp Cloud API
"""

from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import BaseModel
import logging
from typing import Optional, Dict, Any

from ai.conversation_manager import conversation_manager
from services.whatsapp_cloud import whatsapp_cloud
from services.whatsapp_cloud import whatsapp_cloud
from utils.text_formatter import text_formatter
from database.mongo_config import get_database

logger = logging.getLogger(__name__)

router = APIRouter()


class TestWhatsAppMessage(BaseModel):
    """Test WhatsApp message request model"""
    to: str
    message: str


@router.get("/sms")
async def webhook_verify(
    request: Request,
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token")
):
    """
    Verify WhatsApp webhook
    
    WhatsApp will call this endpoint with verification parameters
    
    Args:
        hub_mode: Should be "subscribe"
        hub_challenge: Challenge string to echo back
        hub_verify_token: Verification token to validate
        
    Returns:
        Plain text response with challenge if verification succeeds
    """
    logger.info(f"📋 Webhook verification request: mode={hub_mode}, token={hub_verify_token}")
    
    # Verify the webhook
    challenge = whatsapp_cloud.verify_webhook(
        mode=hub_mode or "",
        token=hub_verify_token or "",
        challenge=hub_challenge or ""
    )
    
    if challenge:
        logger.info("✅ Webhook verification successful")
        return PlainTextResponse(content=challenge, status_code=200)
    
    logger.warning("❌ Webhook verification failed")
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/sms")
async def webhook_message(request: Request):
    """
    Handle incoming WhatsApp messages
    
    WhatsApp Cloud API sends messages in the following format:
    {
      "object": "whatsapp_business_account",
      "entry": [{
        "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
        "changes": [{
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {...},
            "contacts": [{...}],
            "messages": [{
              "from": "PHONE_NUMBER",
              "id": "MESSAGE_ID",
              "timestamp": "TIMESTAMP",
              "text": {
                "body": "MESSAGE_TEXT"
              },
              "type": "text"
            }]
          },
          "field": "messages"
        }]
      }]
    }
    """
    try:
        # Parse incoming webhook payload
        body = await request.json()
        logger.info(f"📥 Incoming WhatsApp webhook: {body}")
        
        # Extract message data from WhatsApp webhook structure
        if "entry" not in body:
            logger.warning("Invalid webhook structure - no 'entry' field")
            return JSONResponse(content={"status": "error", "message": "Invalid payload"}, status_code=400)
        
        for entry in body.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                
                # Check if there are messages
                messages = value.get("messages", [])
                if not messages:
                    logger.info("No messages in webhook payload")
                    continue
                
                # Resolve tenant from phone_number_id
                metadata_obj = value.get("metadata", {})
                phone_number_id = metadata_obj.get("phone_number_id")
                tenant_id = None
                
                if phone_number_id:
                    db = get_database()
                    tenant = await db.tenants.find_one({"whatsapp_phone_number_id": phone_number_id})
                    if tenant:
                        tenant_id = str(tenant["_id"])
                        logger.info(f"🏢 Resolved tenant: {tenant.get('name')} ({tenant_id})")
                    else:
                        logger.warning(f"⚠️ No tenant found for phone_number_id: {phone_number_id}")
                
                # Process each message
                for message in messages:
                    # Extract message details
                    from_number = message.get("from")
                    message_id = message.get("id")
                    message_type = message.get("type")
                    timestamp = message.get("timestamp")
                    
                    # Only process text messages
                    if message_type != "text":
                        logger.info(f"Skipping non-text message type: {message_type}")
                        continue
                    
                    # Extract message text
                    message_text = message.get("text", {}).get("body", "")
                    
                    if not from_number or not message_text:
                        logger.warning("Missing from_number or message_text")
                        continue
                    
                    logger.info(f"📱 Processing WhatsApp message from {from_number}: {message_text[:50]}...")
                    
                    # Clean phone number
                    phone_number = text_formatter.clean_phone_number(from_number)
                    
                    # Prepare metadata
                    metadata = {
                        "whatsapp_message_id": message_id,
                        "whatsapp_from": from_number,
                        "whatsapp_timestamp": timestamp,
                        "message_type": message_type,
                        "phone_number_id": phone_number_id
                    }
                    
                    # Process message through conversation manager
                    result = await conversation_manager.process_message(
                        phone_number=phone_number,
                        message_text=message_text,
                        whatsapp_metadata=metadata,
                        tenant_id=tenant_id
                    )
                    
                    # Get AI response
                    ai_response = result.get("response", "I'm sorry, I couldn't process that.")
                    
                    logger.info(f"🤖 AI Response: {ai_response[:50]}...")
                    
                    # Send response back via WhatsApp
                    send_result = whatsapp_cloud.send_text_message(
                        to=from_number,
                        text=ai_response
                    )
                    
                    if "error" in send_result:
                        logger.error(f"Failed to send WhatsApp response: {send_result['error']}")
                    else:
                        logger.info(f"✅ Response sent successfully: {send_result.get('message_id')}")
        
        # Return success response (WhatsApp expects 200 OK)
        return JSONResponse(content={"status": "success"}, status_code=200)
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {e}", exc_info=True)
        # Still return 200 to prevent WhatsApp from retrying
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=200)


@router.post("/test-whatsapp")
async def test_whatsapp(message_data: TestWhatsAppMessage):
    """
    Test endpoint to send WhatsApp messages
    
    Args:
        message_data: Test message with 'to' and 'message' fields
        
    Returns:
        Result of sending the message
        
    Example:
        POST /api/v1/webhook/test-whatsapp
        {
            "to": "+21692034689",
            "message": "Hello from Cloud API"
        }
    """
    try:
        logger.info(f"🧪 Test WhatsApp message to {message_data.to}: {message_data.message}")
        
        result = whatsapp_cloud.send_text_message(
            to=message_data.to,
            text=message_data.message
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "status": "success",
            "message": "WhatsApp message sent",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error in test endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def webhook_status():
    """
    Webhook status check
    """
    return {
        "status": "active",
        "service": "WhatsApp Cloud API",
        "endpoints": {
            "webhook_verify": "GET /webhook/sms",
            "webhook_message": "POST /webhook/sms",
            "test": "POST /webhook/test-whatsapp",
            "status": "GET /webhook/status"
        }
    }
