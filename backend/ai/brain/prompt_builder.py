"""
Dynamic Prompt Builder
Constructs system prompts from business configuration
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)


class PromptBuilder:
    """
    Builds dynamic AI prompts based on business configuration
    Supports the Cyranius-style barber shop prompt template
    """
    
    @staticmethod
    def build_system_prompt(
        config: Dict[str, Any],
        current_time: Optional[datetime] = None
    ) -> str:
        """
        Build system prompt from business configuration
        
        Args:
            config: Business configuration dictionary
            current_time: Current datetime for context
            
        Returns:
            Complete system prompt string
        """
        if current_time is None:
            tz = pytz.timezone(config.get("timezone", "America/New_York"))
            current_time = datetime.now(tz)
        
        # Get AI config
        ai_config = config.get("ai_config", {})
        custom_prompt = ai_config.get("system_prompt", "")
        
        # If custom prompt exists, use it
        if custom_prompt:
            return PromptBuilder._inject_variables(custom_prompt, config, current_time)
        
        # Otherwise, use default barber shop prompt
        return PromptBuilder._build_default_barbershop_prompt(config, current_time)
    
    @staticmethod
    def _inject_variables(
        prompt_template: str,
        config: Dict[str, Any],
        current_time: datetime
    ) -> str:
        """
        Inject dynamic variables into prompt template
        
        Variables:
        - {business_name}
        - {business_phone}
        - {business_hours}
        - {services}
        - {current_datetime}
        - {timezone}
        """
        # Format current time
        formatted_time = current_time.strftime("%b %d, %Y, %I:%M %p")
        
        # Get services list
        services = config.get("services", [])
        service_names = ", ".join([s.get("name", "") for s in services if s.get("is_active", True)])
        
        # Get opening hours summary
        opening_hours = PromptBuilder._format_opening_hours(config.get("opening_hours", []))
        
        # Variable replacements
        replacements = {
            "{business_name}": config.get("business_name", "the business"),
            "{business_phone}": config.get("business_phone", ""),
            "{business_hours}": opening_hours,
            "{services}": service_names,
            "{current_datetime}": formatted_time,
            "{timezone}": config.get("timezone", "America/New_York")
        }
        
        prompt = prompt_template
        for placeholder, value in replacements.items():
            prompt = prompt.replace(placeholder, value)
        
        return prompt
    
    @staticmethod
    def _format_opening_hours(hours_list: list) -> str:
        """Format opening hours into readable string"""
        if not hours_list:
            return "Monday-Saturday 9:00 AM - 8:00 PM"
        
        # Group consecutive days with same hours
        day_groups = []
        current_group = None
        
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        # Sort hours by day_of_week
        sorted_hours = sorted(hours_list, key=lambda h: h.get("day_of_week", 0))
        
        for hours in sorted_hours:
            day_of_week = hours.get("day_of_week", 0)
            day_name = day_names[day_of_week]
            
            if not hours.get("is_open", False):
                if current_group:
                    day_groups.append(current_group)
                    current_group = None
                continue
            
            hours_str = f"{hours.get('open_time', '09:00')} - {hours.get('close_time', '17:00')}"
            
            if current_group is None:
                current_group = {
                    "start_day": day_name,
                    "end_day": day_name,
                    "hours": hours_str
                }
            elif current_group["hours"] == hours_str:
                current_group["end_day"] = day_name
            else:
                day_groups.append(current_group)
                current_group = {
                    "start_day": day_name,
                    "end_day": day_name,
                    "hours": hours_str
                }
        
        if current_group:
            day_groups.append(current_group)
        
        # Format groups
        parts = []
        for group in day_groups:
            start = group["start_day"]
            end = group["end_day"]
            hours = group["hours"]
            
            if start == end:
                parts.append(f"{start} {hours}")
            else:
                parts.append(f"{start}-{end} {hours}")
        
        return ", ".join(parts) if parts else "By appointment"
    
    @staticmethod
    def _build_default_barbershop_prompt(
        config: Dict[str, Any],
        current_time: datetime
    ) -> str:
        """
        Build default barber shop receptionist prompt
        Cyranius-style adapted for barber shop
        """
        business_name = config.get("business_name", "Royal Fade Barbershop")
        business_phone = config.get("business_phone", "")
        
        # Get services
        services = config.get("services", [])
        service_list = ", ".join([
            f"{s.get('name')} ({s.get('duration_minutes', 30)} min)"
            for s in services if s.get("is_active", True)
        ])
        
        opening_hours = PromptBuilder._format_opening_hours(config.get("opening_hours", []))
        formatted_time = current_time.strftime("%b %d, %Y, %I:%M %p")
        
        prompt = f"""<<< [Identity]
You are Ava, the friendly, knowledgeable receptionist for {business_name} – a modern barbershop specializing in precision haircuts, fades, beard grooming, and traditional hot shaves.

Current Date and Time: {formatted_time}

[Style]
- Warm, conversational tone with approachable, light humor
- Use natural speech fillers like "Umm...," "Well...," or "I mean," sparingly
- Keep replies brief, friendly, and inviting—natural conversation style
- Professional yet relaxed; reassure clients and reduce friction

[Response Guideline]
- Never use technical narration (e.g., "asterisk"); stay natural
- Give bite-sized info; pause for client input
- Redirect off-topic chats back to appointments, services, or business info
- Assume 30-minute default appointment if client does not specify duration
- Always ask: "Can you spell your email please?" before accepting it
- Do not book past dates; gently joke if they try ("I wish we had a time machine!")
- Never proceed to finalizing anything until NAME, EMAIL (spelled), and TIMING are confirmed
- Phone number (if asked): {business_phone}

[Reminder]
- Use {business_name} knowledge: services offered, appointment booking, general inquiries
- Current Date and Time: {formatted_time}
- Do not repeat the client verbatim; paraphrase naturally
- {business_name} operates {opening_hours}
- ONLY MOVE FORWARD when you have correct NAME, spelled EMAIL, and TIMING
- Email spelling rule: Read names letter-by-letter (e.g., "J - O - H - N"), then say domain normally (e.g., "at gmail dot com")

[Number, Time & Date Speech]
- Say times slowly: "One PM," "Three thirty PM," "Eight forty-five AM"
- Always include AM or PM
- Never say "O'Clock" (prefer plain time)
- Dates: speak month name clearly; pause between parts

[Service Information]
Available services at {business_name}:
{service_list}

[Tasks]

**Service Questions**
- Provide concise service descriptions
- Mention typical duration and what's included
- For pricing: Provide transparent info if available, otherwise suggest booking consultation

**Appointment Booking**
Flow:
1. Collect name → "Can you spell your email please?" → desired date/time → service
2. Validate future date (reject past with light humor)
3. Confirm all details before booking
4. Create appointment and send confirmation

Required info:
- Client name
- Email (spelled letter-by-letter)
- Phone number
- Service
- Date and time
- Duration (default 30 min)

**Update Appointment (Reschedule)**
- Gather original appointment time + new desired timing
- Confirm name and contact info
- Update booking and confirm new time

**Cancel Appointment**
- Confirm name, email, appointment time
- Process cancellation with understanding
- Invite them to rebook anytime

[Email Spelling Protocol]
- Names: spell letter-by-letter ("M - A - R - I - A")
- Domains: speak plainly ("at gmail dot com")
- Hyphens: say "dash"; underscores: "underscore"; periods: "dot"
- Confirm back: "I have J - O - H - N at email dot com—does that look right?"

[Data Validation Before Booking]
Required for any booking action:
- Name (full)
- Spelled + confirmed email
- Time (future, within operating hours)
- Service selected

[Boundaries & Redirects]
- Off-topic: "Let's bring it back to your appointment—how can I help with booking or service info?"
- Financial specifics: offer to schedule consultation for detailed quotes

[Error & Edge Cases]
- Past date request: reject with playful line ("If we master time travel, you'll be first to know!")
- Missing email spelling: always prompt again—never assume
- Holiday or off-hours request: offer alternative days

[Do Not Do]
- Do not fabricate availability or appointments
- Do not skip email spelling
- Do not proceed without all required fields
- Do not alter client's intended time unless confirming alternatives
- Do not promise services not listed

[Closing Behavior]
- Confirm next step ("I'll lock in that appointment now")
- After booking: summarize (date, time, service) and thank them
- End politely: "Looking forward to seeing you at {business_name}!"

--- END OF {business_name.upper()} PROMPT ---"""
        
        return prompt
    
    @staticmethod
    def build_intent_classification_prompt() -> str:
        """Build prompt for intent classification"""
        return """You are an intent classifier for a barbershop receptionist AI.

Classify the user's message into ONE of these intents:
- greeting: Initial hello, hi, or opening message
- book_appointment: Wants to schedule a new appointment
- update_appointment: Wants to reschedule an existing appointment
- cancel_appointment: Wants to cancel an appointment
- check_availability: Asking about available time slots
- service_info: Asking about services offered, prices, duration
- business_info: Asking about hours, location, contact info
- general_question: Other general questions
- unknown: Cannot determine intent

Respond with ONLY a JSON object:
{
  "intent": "intent_name",
  "confidence": 0.95,
  "reasoning": "brief explanation"
}

Be precise. Consider the full context."""
    
    @staticmethod
    def build_entity_extraction_prompt() -> str:
        """Build prompt for entity extraction"""
        return """Extract booking information from the conversation.

CRITICAL RULES FOR CLIENT NAME:
- Only extract a name if the customer explicitly provides it with phrases like:
  * "My name is [Name]"
  * "I'm [Name]"
  * "This is [Name]"
  * "Call me [Name]"
- DO NOT extract words like "want", "to", "book", "appointment" as names
- If the customer says "I want to book" - this is NOT a name, return null
- If no explicit name is given, return null for client_name

IMPORTANT: Respond with ONLY a valid JSON object, no other text.

Return JSON with these fields (use null if not mentioned):
{
  "client_name": "string or null",
  "client_email": "string or null",
  "client_phone": "string or null",
  "service": "string or null",
  "date": "YYYY-MM-DD or description like 'tomorrow'",
  "time": "HH:MM or description like '3pm'",
  "barber_preference": "string or null",
  "notes": "string or null",
  "duration_minutes": number or null
}

Examples:
- "I want to book a haircut" → {"client_name": null, "service": "haircut", ...}
- "My name is John" → {"client_name": "John", ...}
- "Book me for tomorrow at 3" → {"date": "tomorrow", "time": "3pm", ...}
"""


# Singleton instance
prompt_builder = PromptBuilder()
