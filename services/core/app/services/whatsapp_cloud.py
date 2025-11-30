"""
WhatsApp Cloud API Handler
Manages all WhatsApp Cloud API interactions for messaging
"""

import requests
import logging
import time
from typing import Optional, Dict, Any, List
from utils.config import settings

logger = logging.getLogger(__name__)


class WhatsAppCloudAPI:
    """
    Handles all WhatsApp Cloud API interactions
    """
    
    BASE_URL = "https://graph.facebook.com/v22.0"
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    
    def __init__(self):
        """Initialize WhatsApp Cloud API handler"""
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.access_token = settings.WHATSAPP_TOKEN
        self.verify_token = settings.WHATSAPP_VERIFY_TOKEN
        
        if not self.access_token or not self.phone_number_id:
            logger.warning("WhatsApp Cloud API credentials not configured")
        else:
            logger.info("WhatsApp Cloud API handler initialized successfully")
    
    def _format_phone_number(self, phone: str) -> str:
        """
        Format phone number for WhatsApp Cloud API
        Removes + prefix and any non-numeric characters
        
        Args:
            phone: Phone number (e.g., +21692034689)
            
        Returns:
            Formatted phone number (e.g., 21692034689)
        """
        # Remove all non-numeric characters
        formatted = ''.join(filter(str.isdigit, phone))
        
        # Remove leading + if present (already handled by filter)
        # WhatsApp Cloud API expects numbers without +
        return formatted
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Make HTTP request to WhatsApp Cloud API with retry logic
        
        Args:
            method: HTTP method (GET, POST)
            endpoint: API endpoint
            data: Request payload
            retry_count: Current retry attempt
            
        Returns:
            API response as dictionary
        """
        url = f"{self.BASE_URL}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            if method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=10)
            else:
                response = requests.get(url, headers=headers, timeout=10)
            
            # Handle rate limiting (429)
            if response.status_code == 429:
                if retry_count < self.MAX_RETRIES:
                    wait_time = self.RETRY_DELAY * (retry_count + 1)
                    logger.warning(f"Rate limited. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    return self._make_request(method, endpoint, data, retry_count + 1)
                else:
                    logger.error("Max retries reached for rate limiting")
                    return {"error": "Rate limit exceeded"}
            
            # Check for other errors
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"WhatsApp API request failed: {e}")
            
            # Retry on network errors
            if retry_count < self.MAX_RETRIES:
                logger.info(f"Retrying request... (attempt {retry_count + 1}/{self.MAX_RETRIES})")
                time.sleep(self.RETRY_DELAY)
                return self._make_request(method, endpoint, data, retry_count + 1)
            
            return {"error": str(e)}
    
    def send_text_message(
        self,
        to: str,
        text: str
    ) -> Dict[str, Any]:
        """
        Send a text message via WhatsApp Cloud API
        
        Args:
            to: Recipient phone number (e.g., +21692034689)
            text: Message text
            
        Returns:
            Dictionary with message ID and status
        """
        if not self.access_token or not self.phone_number_id:
            logger.error("WhatsApp Cloud API not configured")
            return {"error": "WhatsApp not configured"}
        
        # Format phone number
        formatted_phone = self._format_phone_number(to)
        
        # Prepare message payload
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": formatted_phone,
            "type": "text",
            "text": {
                "body": text
            }
        }
        
        logger.info(f"📤 Sending WhatsApp message to {formatted_phone}: {text[:50]}...")
        
        # Make API request
        endpoint = f"{self.phone_number_id}/messages"
        result = self._make_request("POST", endpoint, payload)
        
        if "error" in result:
            logger.error(f"Failed to send message: {result['error']}")
            return result
        
        # Extract message ID from response
        message_id = result.get("messages", [{}])[0].get("id")
        
        logger.info(f"✅ Message sent successfully. ID: {message_id}")
        
        return {
            "message_id": message_id,
            "status": "sent",
            "to": formatted_phone
        }
    
    def send_template_message(
        self,
        to: str,
        template_name: str,
        language_code: str = "en",
        params: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Send a template message via WhatsApp Cloud API
        
        Templates must be pre-approved in Meta Business Manager
        
        Args:
            to: Recipient phone number
            template_name: Template name (e.g., "appointment_confirmation")
            language_code: Template language code (default: "en")
            params: List of parameter values for template placeholders
            
        Returns:
            Dictionary with message ID and status
        """
        if not self.access_token or not self.phone_number_id:
            logger.error("WhatsApp Cloud API not configured")
            return {"error": "WhatsApp not configured"}
        
        # Format phone number
        formatted_phone = self._format_phone_number(to)
        
        # Prepare template components
        components = []
        if params:
            components.append({
                "type": "body",
                "parameters": [
                    {"type": "text", "text": param}
                    for param in params
                ]
            })
        
        # Prepare message payload
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": formatted_phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                },
                "components": components
            }
        }
        
        logger.info(f"📤 Sending WhatsApp template '{template_name}' to {formatted_phone}")
        
        # Make API request
        endpoint = f"{self.phone_number_id}/messages"
        result = self._make_request("POST", endpoint, payload)
        
        if "error" in result:
            logger.error(f"Failed to send template: {result['error']}")
            return result
        
        # Extract message ID from response
        message_id = result.get("messages", [{}])[0].get("id")
        
        logger.info(f"✅ Template sent successfully. ID: {message_id}")
        
        return {
            "message_id": message_id,
            "status": "sent",
            "to": formatted_phone,
            "template": template_name
        }
    
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """
        Verify webhook for WhatsApp Cloud API
        
        Args:
            mode: Verification mode
            token: Verification token
            challenge: Challenge string to echo back
            
        Returns:
            Challenge string if verification succeeds, None otherwise
        """
        if mode == "subscribe" and token == self.verify_token:
            logger.info("✅ Webhook verified successfully")
            return challenge
        
        logger.warning("❌ Webhook verification failed")
        return None


# Create global instance
whatsapp_cloud = WhatsAppCloudAPI()
