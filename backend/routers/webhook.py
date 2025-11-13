"""
Twilio Webhook Router
Handles incoming SMS and voice calls from Twilio
"""

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import Response
import logging
from typing import Optional

from ai.conversation_manager import conversation_manager
from utils.twilio_handler import twilio_handler
from utils.text_formatter import text_formatter

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/sms")
async def webhook_sms(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...),
    MessageSid: str = Form(...),
    To: Optional[str] = Form(None)
):
    """
    Handle incoming SMS messages from Twilio
    
    Args:
        From: Sender's phone number
        Body: Message text
        MessageSid: Twilio message ID
        To: Recipient (our Twilio number)
    """
    try:
        logger.info(f"📱 Incoming SMS from {From}: {Body[:50]}...")
        
        # Clean phone number
        phone_number = text_formatter.clean_phone_number(From)
        
        # Prepare metadata
        metadata = {
            "twilio_message_sid": MessageSid,
            "twilio_from": From,
            "twilio_to": To
        }
        
        # Process message through conversation manager
        result = await conversation_manager.process_message(
            phone_number=phone_number,
            message_text=Body,
            twilio_metadata=metadata
        )
        
        # Get AI response
        ai_response = result.get("response", "I'm sorry, I couldn't process that.")
        
        logger.info(f"🤖 AI Response: {ai_response[:50]}...")
        
        # Create TwiML response
        twiml_response = twilio_handler.create_sms_response(ai_response)
        
        return Response(content=twiml_response, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error processing SMS webhook: {e}", exc_info=True)
        
        # Return error response
        error_response = twilio_handler.create_sms_response(
            "I apologize, but I'm having trouble right now. Please try again or call us directly."
        )
        return Response(content=error_response, media_type="application/xml")


@router.post("/voice")
async def webhook_voice(
    request: Request,
    From: str = Form(...),
    To: Optional[str] = Form(None),
    CallSid: Optional[str] = Form(None)
):
    """
    Handle incoming voice calls from Twilio
    
    Args:
        From: Caller's phone number
        To: Recipient (our Twilio number)
        CallSid: Twilio call ID
    """
    try:
        logger.info(f"📞 Incoming call from {From}")
        
        # Create voice greeting
        greeting = f"""Hello! Thank you for calling {settings.BUSINESS_NAME}. 
        This is Ava, your virtual receptionist. 
        To book an appointment, press 1. 
        To speak with a staff member, press 2. 
        Or stay on the line and I can help you."""
        
        twiml_response = twilio_handler.create_voice_response(greeting)
        
        return Response(content=twiml_response, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error processing voice webhook: {e}", exc_info=True)
        
        error_greeting = "We're sorry, but we're experiencing technical difficulties. Please try again later."
        error_response = twilio_handler.create_voice_response(error_greeting)
        
        return Response(content=error_response, media_type="application/xml")


@router.post("/voice/menu")
async def webhook_voice_menu(
    request: Request,
    Digits: str = Form(...),
    From: str = Form(...),
    CallSid: str = Form(...)
):
    """
    Handle voice menu selections
    
    Args:
        Digits: Pressed digit
        From: Caller's phone number
        CallSid: Twilio call ID
    """
    try:
        logger.info(f"Voice menu selection: {Digits} from {From}")
        
        if Digits == "1":
            # Book appointment flow
            message = """Great! I can help you book an appointment. 
            Please send us a text message with your preferred date and time, 
            or call back during business hours to speak with our team."""
        elif Digits == "2":
            # Transfer to staff
            message = f"""One moment please, I'll connect you with our staff. 
            If no one is available, please call {settings.BUSINESS_PHONE} during business hours."""
        else:
            message = "I didn't understand that selection. Goodbye!"
        
        twiml_response = twilio_handler.create_voice_response(message)
        
        return Response(content=twiml_response, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error processing voice menu: {e}", exc_info=True)
        error_response = twilio_handler.create_voice_response("Thank you for calling. Goodbye.")
        return Response(content=error_response, media_type="application/xml")


@router.get("/status")
async def webhook_status():
    """
    Webhook status check
    """
    return {
        "status": "active",
        "endpoints": {
            "sms": "/webhook/sms",
            "voice": "/webhook/voice",
            "voice_menu": "/webhook/voice/menu"
        }
    }


# Import settings for voice responses
from utils.config import settings
