"""
AI Prompt Templates for Conversation Management
"""

from utils.config import settings
from typing import Dict, Any


class PromptTemplates:
    """
    Centralized prompt templates for the AI receptionist
    """
    
    @staticmethod
    def get_system_prompt() -> str:
        """
        Main system prompt that defines the AI receptionist's personality
        and capabilities
        """
        return f"""You are Ava, the friendly and professional virtual receptionist for {settings.BUSINESS_NAME}.

BUSINESS INFORMATION:
- Name: {settings.BUSINESS_NAME}
- Phone: {settings.BUSINESS_PHONE}
- Hours: {settings.BUSINESS_HOURS}
- Services: {settings.AVAILABLE_SERVICES}

YOUR PERSONALITY:
- Warm, friendly, and conversational
- Professional but not overly formal
- Helpful and patient
- Use natural language, not robotic responses
- Keep responses concise (2-3 sentences max)
- Use emojis sparingly and only when appropriate

YOUR CAPABILITIES:
1. Book new appointments
2. Update existing appointments
3. Cancel appointments
4. Answer questions about services
5. Provide business hours and location info
6. Check availability

CONVERSATION GUIDELINES:
- Always greet new clients warmly
- Ask for missing information one piece at a time
- Confirm all booking details before finalizing
- Be understanding about cancellations or changes
- If unsure, offer to connect them with staff

BOOKING PROCESS:
1. Greet the client
2. Identify what they need (service)
3. Get their name
4. Get preferred date and time
5. Ask for barber preference (optional)
6. Confirm all details
7. Create the appointment

Remember: You're representing {settings.BUSINESS_NAME}. Make every interaction pleasant and efficient!"""
    
    @staticmethod
    def get_greeting_prompt() -> str:
        """Prompt for initial greeting"""
        return f"""Generate a warm, natural greeting for a new client contacting {settings.BUSINESS_NAME}.
        Introduce yourself as Ava, mention our main services, and ask how you can help.
        Keep it conversational and friendly. 2 sentences max."""
    
    @staticmethod
    def get_booking_confirmation_prompt(booking_details: Dict[str, Any]) -> str:
        """
        Prompt for confirming booking details
        
        Args:
            booking_details: Dictionary with name, service, date, time, etc.
        """
        details_str = "\n".join([f"- {k}: {v}" for k, v in booking_details.items()])
        
        return f"""The client has provided these booking details:
{details_str}

Generate a friendly confirmation message that:
1. Summarizes what they've booked
2. Thanks them
3. Mentions they'll get a confirmation
4. Asks if they need anything else

Keep it natural and warm, 2-3 sentences."""
    
    @staticmethod
    def get_missing_info_prompt(
        intent: str,
        collected_info: Dict[str, Any],
        missing_fields: list
    ) -> str:
        """
        Prompt for asking about missing information
        
        Args:
            intent: The conversation intent (e.g., "book_appointment")
            collected_info: Information already collected
            missing_fields: List of fields still needed
        """
        collected_str = "\n".join([f"- {k}: {v}" for k, v in collected_info.items()])
        missing_str = ", ".join(missing_fields)
        
        return f"""The client wants to {intent.replace('_', ' ')}.

Already collected:
{collected_str if collected_str else "Nothing yet"}

Still need: {missing_str}

Generate a friendly question to ask for the NEXT piece of missing information.
Ask for only ONE thing at a time. Be conversational and natural. 1-2 sentences."""
    
    @staticmethod
    def get_cancellation_prompt(appointment_details: Dict[str, Any]) -> str:
        """Prompt for appointment cancellation"""
        details_str = "\n".join([f"- {k}: {v}" for k, v in appointment_details.items()])
        
        return f"""The client wants to cancel this appointment:
{details_str}

Generate a professional but warm response that:
1. Confirms the cancellation
2. Expresses understanding
3. Invites them to rebook anytime
4. Thanks them

Keep it friendly and brief, 2 sentences."""
    
    @staticmethod
    def get_service_info_prompt(service_name: str = None) -> str:
        """Prompt for providing service information"""
        if service_name:
            return f"""The client is asking about the '{service_name}' service.
            
            Our services: {settings.AVAILABLE_SERVICES}
            
            Provide helpful information about this service in a friendly way.
            If you don't know specific details, describe it generally and offer to connect them with staff.
            2-3 sentences."""
        else:
            return f"""The client is asking about our services.
            
            Our services: {settings.AVAILABLE_SERVICES}
            
            List the services in a natural, conversational way and ask which one interests them.
            2-3 sentences."""
    
    @staticmethod
    def get_business_info_prompt(question_type: str = "general") -> str:
        """Prompt for business information questions"""
        return f"""The client is asking about {question_type} for {settings.BUSINESS_NAME}.

Business details:
- Hours: {settings.BUSINESS_HOURS}
- Phone: {settings.BUSINESS_PHONE}
- Services: {settings.AVAILABLE_SERVICES}

Provide a helpful, friendly response with the relevant information.
Keep it conversational. 2-3 sentences."""
    
    @staticmethod
    def get_rescheduling_prompt(
        old_details: Dict[str, Any],
        new_details: Dict[str, Any]
    ) -> str:
        """Prompt for appointment rescheduling"""
        return f"""The client wants to reschedule from:
{old_details.get('datetime')} 

To:
{new_details.get('datetime')}

Generate a friendly confirmation of the change.
Mention both the old and new times briefly.
2 sentences."""
    
    @staticmethod
    def get_error_prompt() -> str:
        """Prompt for error/confusion scenarios"""
        return f"""Generate a polite response indicating you didn't quite understand,
        and offer to either:
        1. Try rephrasing
        2. Connect them with a staff member at {settings.BUSINESS_PHONE}
        
        Be friendly and helpful. 2 sentences."""
    
    @staticmethod
    def get_availability_check_prompt(date: str, available: bool) -> str:
        """Prompt for checking availability"""
        if available:
            return f"""We have availability on {date}.
            Generate a response confirming this and asking what time would work best.
            Keep it friendly. 1-2 sentences."""
        else:
            return f"""We're fully booked on {date}.
            Generate a response apologizing and suggesting alternative dates nearby.
            Be helpful and accommodating. 2 sentences."""


# Singleton instance
prompt_templates = PromptTemplates()
