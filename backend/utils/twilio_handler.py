"""
Twilio API Handler - SMS and Voice Communication
"""

from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse
import logging
from typing import Optional, Dict, Any
from utils.config import settings

logger = logging.getLogger(__name__)


class TwilioHandler:
    """
    Handles all Twilio API interactions for SMS and Voice
    """
    
    def __init__(self):
        """Initialize Twilio client"""
        try:
            self.client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            self.phone_number = settings.TWILIO_PHONE_NUMBER
            logger.info("Twilio client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {e}")
            self.client = None
    
    def send_sms(
        self,
        to_number: str,
        message: str,
        media_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send SMS message to a phone number
        
        Args:
            to_number: Recipient phone number
            message: Message text
            media_url: Optional media URL for MMS
            
        Returns:
            Dictionary with message SID and status
        """
        if not self.client:
            logger.error("Twilio client not initialized")
            return {"error": "Twilio not configured"}
        
        try:
            kwargs = {
                "body": message,
                "from_": self.phone_number,
                "to": to_number
            }
            
            if media_url:
                kwargs["media_url"] = [media_url]
            
            message_obj = self.client.messages.create(**kwargs)
            
            logger.info(f"SMS sent to {to_number}, SID: {message_obj.sid}")
            
            return {
                "sid": message_obj.sid,
                "status": message_obj.status,
                "to": to_number
            }
            
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return {"error": str(e)}
    
    def create_sms_response(self, message: str) -> str:
        """
        Create TwiML response for SMS webhook
        
        Args:
            message: Response message text
            
        Returns:
            TwiML XML string
        """
        response = MessagingResponse()
        response.message(message)
        return str(response)
    
    def create_voice_response(
        self,
        message: str,
        voice: str = "Polly.Joanna",
        language: str = "en-US"
    ) -> str:
        """
        Create TwiML response for voice webhook
        
        Args:
            message: Text to speak
            voice: Voice name (Amazon Polly voices)
            language: Language code
            
        Returns:
            TwiML XML string
        """
        response = VoiceResponse()
        response.say(message, voice=voice, language=language)
        
        # Add option to press key for more options
        gather = response.gather(
            num_digits=1,
            action='/webhook/voice/menu',
            method='POST',
            timeout=5
        )
        gather.say(
            "Press 1 to book an appointment, 2 to speak with staff, or stay on the line.",
            voice=voice
        )
        
        return str(response)
    
    def get_message_details(self, message_sid: str) -> Optional[Dict]:
        """
        Get details of a sent message
        
        Args:
            message_sid: Twilio message SID
            
        Returns:
            Message details dictionary
        """
        if not self.client:
            return None
        
        try:
            message = self.client.messages(message_sid).fetch()
            
            return {
                "sid": message.sid,
                "status": message.status,
                "to": message.to,
                "from": message.from_,
                "body": message.body,
                "date_sent": message.date_sent,
                "error_code": message.error_code,
                "error_message": message.error_message
            }
            
        except Exception as e:
            logger.error(f"Error fetching message details: {e}")
            return None
    
    def send_appointment_confirmation(
        self,
        phone_number: str,
        appointment_details: Dict[str, Any]
    ) -> Dict:
        """
        Send appointment confirmation SMS
        
        Args:
            phone_number: Client's phone number
            appointment_details: Dictionary with appointment info
            
        Returns:
            Send result
        """
        message = self._format_confirmation_message(appointment_details)
        return self.send_sms(phone_number, message)
    
    def send_appointment_reminder(
        self,
        phone_number: str,
        appointment_details: Dict[str, Any]
    ) -> Dict:
        """
        Send appointment reminder SMS
        
        Args:
            phone_number: Client's phone number
            appointment_details: Dictionary with appointment info
            
        Returns:
            Send result
        """
        message = self._format_reminder_message(appointment_details)
        return self.send_sms(phone_number, message)
    
    def _format_confirmation_message(self, details: Dict) -> str:
        """Format appointment confirmation message"""
        return f"""✅ Appointment Confirmed!

{settings.BUSINESS_NAME}

Client: {details.get('client_name')}
Service: {details.get('service')}
Date & Time: {details.get('datetime_formatted')}
Duration: {details.get('duration_minutes')} minutes

We look forward to seeing you! 
Reply CANCEL to cancel this appointment.

{settings.BUSINESS_PHONE}"""
    
    def _format_reminder_message(self, details: Dict) -> str:
        """Format appointment reminder message"""
        return f"""⏰ Appointment Reminder

{settings.BUSINESS_NAME}

Your {details.get('service')} appointment is coming up!

When: {details.get('datetime_formatted')}
Where: {settings.BUSINESS_ADDRESS}

See you soon! Reply CANCEL to cancel.

{settings.BUSINESS_PHONE}"""
    
    def validate_phone_number(self, phone_number: str) -> bool:
        """
        Validate phone number format
        
        Args:
            phone_number: Phone number string
            
        Returns:
            True if valid, False otherwise
        """
        if not self.client:
            # Basic validation if Twilio not available
            import re
            pattern = r'^\+?1?\d{9,15}$'
            return bool(re.match(pattern, phone_number))
        
        try:
            # Use Twilio lookup API
            phone = self.client.lookups.v1.phone_numbers(phone_number).fetch()
            return phone is not None
        except Exception as e:
            logger.warning(f"Phone validation failed: {e}")
            return False


# Singleton instance
twilio_handler = TwilioHandler()
