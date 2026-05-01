"""
Twilio Messaging Service
Handles SMS and WhatsApp message sending via Twilio
"""

import os
import logging
from typing import Optional, Dict, Any
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

logger = logging.getLogger(__name__)


class TwilioMessagingService:
    """
    Service for sending SMS and WhatsApp messages via Twilio.
    Uses MessagingServiceSid for scalable message delivery.
    """
    
    def __init__(self):
        """Initialize Twilio client with credentials from environment"""
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.messaging_service_sid = os.getenv("TWILIO_MESSAGING_SERVICE_SID")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
            logger.info("Twilio messaging service initialized")
        else:
            logger.warning("Twilio credentials not configured - messaging disabled")
            self.client = None
    
    def is_configured(self) -> bool:
        """Check if Twilio is properly configured for API access."""
        return bool(self.client)
    
    async def send_sms(
        self,
        to: str,
        body: str,
        from_: Optional[str] = None,
        messaging_service_sid: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send an SMS message via Twilio
        
        Args:
            to: Recipient phone number (E.164 format, e.g., +1234567890)
            body: Message text (max 160 chars per segment; split automatically by Twilio)
            from_: Sender phone number (optional, uses default if not provided)
            messaging_service_sid: MessagingServiceSid (optional, uses default if not provided)
            
        Returns:
            Dictionary with message SID and status
        """
        if not self.is_configured():
            logger.warning("Twilio not configured - SMS not sent")
            return {"success": False, "error": "Twilio not configured"}
        
        try:
            # Determine which sender to use
            sender_sid = messaging_service_sid
            sender_phone = from_
            
            if not sender_sid and not sender_phone:
                logger.error("No tenant sender configured")
                return {"success": False, "error": "No tenant sender configured"}
            
            # Build message creation kwargs
            message_kwargs = {
                "to": to,
                "body": body
            }
            
            # Use MessagingServiceSid if available (recommended for confirmations)
            if sender_sid:
                message_kwargs["messaging_service_sid"] = sender_sid
            else:
                # Fallback to direct phone number
                message_kwargs["from_"] = sender_phone
            
            logger.info(f"Sending SMS to {to} (length: {len(body)} chars)")
            message = self.client.messages.create(**message_kwargs)
            
            logger.info(f"✅ SMS sent successfully. SID: {message.sid}, Status: {message.status}")
            
            return {
                "success": True,
                "message_sid": message.sid,
                "status": message.status,
                "to": message.to,
                "segments": message.num_segments
            }
            
        except TwilioRestException as e:
            logger.error(f"Twilio API error ({e.status}): {e.msg}")
            return {
                "success": False,
                "error": f"Twilio error: {e.msg}",
                "status_code": e.status
            }
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_whatsapp(
        self,
        to: str,
        body: str,
        from_: Optional[str] = None,
        media_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a WhatsApp message via Twilio
        
        Args:
            to: Recipient WhatsApp number (E.164 format, e.g., +1234567890)
            body: Message text
            from_: Sender WhatsApp number (Twilio sandbox or production number)
            media_url: Optional media URL (image, document, etc.)
            
        Returns:
            Dictionary with message SID and status
        """
        if not self.is_configured():
            logger.warning("Twilio not configured - WhatsApp message not sent")
            return {"success": False, "error": "Twilio not configured"}
        
        try:
            sender_phone = from_ or self.twilio_phone_number
            
            if not sender_phone:
                logger.error("No WhatsApp sender phone configured")
                return {"success": False, "error": "No sender configured"}
            
            # WhatsApp requires "whatsapp:" prefix in Twilio API
            whatsapp_to = f"whatsapp:{to}" if not to.startswith("whatsapp:") else to
            whatsapp_from = f"whatsapp:{sender_phone}" if not sender_phone.startswith("whatsapp:") else sender_phone
            
            message_kwargs = {
                "from_": whatsapp_from,
                "to": whatsapp_to,
                "body": body
            }
            
            if media_url:
                message_kwargs["media_url"] = media_url
            
            logger.info(f"Sending WhatsApp message to {whatsapp_to}")
            message = self.client.messages.create(**message_kwargs)
            
            logger.info(f"✅ WhatsApp message sent. SID: {message.sid}, Status: {message.status}")
            
            return {
                "success": True,
                "message_sid": message.sid,
                "status": message.status,
                "to": message.to
            }
            
        except TwilioRestException as e:
            logger.error(f"Twilio WhatsApp error ({e.status}): {e.msg}")
            return {
                "success": False,
                "error": f"Twilio error: {e.msg}",
                "status_code": e.status
            }
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def build_confirmation_sms(
        self,
        appointment_data: Dict[str, Any],
        business_name: str = "Our business"
    ) -> str:
        """
        Build a professional SMS confirmation message
        
        Args:
            appointment_data: Dict with keys: date, time, service, name, etc.
            business_name: Name of the business
            
        Returns:
            Formatted SMS text (kept under 160 chars if possible)
        """
        date = appointment_data.get("date", "")
        time = appointment_data.get("time", "")
        service = appointment_data.get("service", "appointment")
        name = appointment_data.get("name", "")
        
        # Build compact confirmation
        if date and time:
            message = f"Hi {name}! Your {service} at {business_name} is confirmed for {date} at {time}. Reply STOP to opt out."
        else:
            message = f"Hi {name}! Your appointment at {business_name} is confirmed. Reply STOP to opt out."
        
        # If message is too long, shorten it
        if len(message) > 160:
            message = f"Confirmed: {service} on {date} at {time}. Reply STOP to opt out."
        
        return message


# Create global instance
twilio_messaging = TwilioMessagingService()
