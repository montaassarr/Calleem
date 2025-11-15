"""
Conversation State Management
Tracks conversation flow and manages state across multiple messages
"""

import uuid
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from models.conversation import (
    Message, MessageRole, ConversationIntent,
    ConversationState, ConversationInDB
)
from models.appointment import AppointmentCreate, AppointmentStatus
from ai.groq_agent import groq_agent
from ai.prompt_templates import prompt_templates
from ai.intents import intent_classifier
from database.mongo_config import get_database
from utils.datetime_utils import datetime_utils
from utils.text_formatter import text_formatter
from services.whatsapp_cloud import whatsapp_cloud
from utils.config import settings

logger = logging.getLogger(__name__)


class ConversationManager:
    """
    Manages conversation state and generates appropriate AI responses
    """
    
    def __init__(self):
        """Initialize conversation manager"""
        self.db = None
    
    async def initialize(self):
        """Initialize database connection"""
        self.db = get_database()
    
    async def process_message(
        self,
        phone_number: str,
        message_text: str,
        whatsapp_metadata: Dict = None
    ) -> Dict[str, Any]:
        """
        Process incoming message and generate response
        
        Args:
            phone_number: Client's phone number
            message_text: The message text
            whatsapp_metadata: Optional WhatsApp message metadata
            
        Returns:
            Dictionary with AI response and updated state
        """
        try:
            # Ensure DB is initialized
            if self.db is None:
                await self.initialize()
            
            # Get or create conversation
            conversation = await self._get_or_create_conversation(phone_number)
            
            # Add client message to conversation
            client_message = Message(
                role=MessageRole.CLIENT,
                text=message_text,
                timestamp=datetime.utcnow(),
                metadata=whatsapp_metadata
            )
            conversation["messages"].append(client_message.dict())
            
            # Determine intent
            # If already in an active booking flow, maintain book_appointment intent
            # unless user explicitly changes intent (cancel, update, etc.)
            current_intent = conversation["state"].get("intent")
            collected_info = conversation["state"].get("collected_info", {})
            has_booking_data = bool(collected_info.get("service") or collected_info.get("date") or collected_info.get("time"))
            
            is_in_booking = (
                current_intent == ConversationIntent.BOOK_APPOINTMENT.value and
                has_booking_data and  # Has some booking data collected
                not conversation["state"].get("completed")  # Not completed yet
            )
            
            if is_in_booking:
                # Check if user is explicitly changing intent (cancel, update, etc.)
                message_lower = message_text.lower()
                intent_changing_keywords = [
                    'cancel', 'nevermind', 'forget it', 'wait', 'stop', 'no thanks'
                ]
                if any(keyword in message_lower for keyword in intent_changing_keywords):
                    # User wants to change intent, reclassify
                    intent = await self._classify_intent(message_text, conversation["messages"])
                    logger.info(f"🔄 Intent changed during booking: {current_intent} → {intent}")
                    conversation["state"]["intent"] = intent
                else:
                    # Continue with booking intent - DO NOT CHANGE
                    intent = ConversationIntent.BOOK_APPOINTMENT.value
                    logger.info(f"📋 Maintaining booking flow intent (has booking data: {has_booking_data})")
            else:
                # Not in active booking flow, classify normally
                intent = await self._classify_intent(message_text, conversation["messages"])
                old_intent = conversation["state"].get("intent")
                if intent != old_intent:
                    logger.info(f"🔄 Intent changed: {old_intent} → {intent}")
                conversation["state"]["intent"] = intent
            
            # Extract entities from message
            entities = intent_classifier.extract_entities(message_text)
            
            self._update_collected_info(
                conversation=conversation,
                entities=entities,
                phone_number=phone_number,
                message_text=message_text
            )
            
            # Generate AI response based on intent and state
            ai_response_text = await self._generate_response(
                intent=intent,
                message_text=message_text,
                conversation=conversation
            )
            
            # Add AI response to conversation
            ai_message = Message(
                role=MessageRole.AI,
                text=ai_response_text,
                timestamp=datetime.utcnow()
            )
            conversation["messages"].append(ai_message.dict())
            
            # Handle appointment creation or update
            logger.info(f"🔍 Appointment flow check - intent: {intent}, existing appointment_id: {conversation.get('appointment_id')}")
            
            if intent == ConversationIntent.UPDATE_APPOINTMENT.value or (
                conversation.get("appointment_id") and 
                intent == ConversationIntent.BOOK_APPOINTMENT.value
            ):
                logger.info(f"📝 Taking UPDATE appointment path")
                # Try to update existing appointment
                update_result = await self._attempt_appointment_update(conversation)
                if update_result and update_result.get("confirmation_text"):
                    ai_response_text = f"{ai_response_text}\n\n{update_result['confirmation_text']}"
                    conversation["messages"][-1]["text"] = ai_response_text
                elif update_result and update_result.get("error"):
                    conversation["state"]["next_question"] = "new time"
                    ai_response_text = f"{ai_response_text}\n\n{update_result['error']}"
                    conversation["messages"][-1]["text"] = ai_response_text
            else:
                logger.info(f"✨ Taking CREATE appointment path")
                # Try to create new appointment
                booking_result = await self._attempt_appointment_creation(conversation)
                if booking_result and booking_result.get("confirmation_text"):
                    ai_response_text = f"{ai_response_text}\n\n{booking_result['confirmation_text']}"
                    conversation["messages"][-1]["text"] = ai_response_text
                elif booking_result and booking_result.get("error"):
                    conversation["state"]["next_question"] = "new time"
                    ai_response_text = f"{ai_response_text}\n\n{booking_result['error']}"
                    conversation["messages"][-1]["text"] = ai_response_text

            # Update conversation in database
            conversation["updated_at"] = datetime.utcnow()
            await self._save_conversation(conversation)
            
            return {
                "response": ai_response_text,
                "intent": intent,
                "conversation_id": conversation["conversation_id"],
                "state": conversation["state"]
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return {
                "response": "I apologize, but I'm having trouble right now. Please try again.",
                "error": str(e)
            }
    
    async def _get_or_create_conversation(self, phone_number: str) -> Dict:
        """Get existing conversation or create new one"""
        
        # Try to find recent conversation (within last 24 hours)
        recent_conversation = await self.db.conversations.find_one({
            "phone_number": phone_number,
            "created_at": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0)}
        }, sort=[("created_at", -1)])
        
        if recent_conversation:
            logger.info(f"Found existing conversation: {recent_conversation['conversation_id']}")
            return recent_conversation
        
        # Create new conversation
        conversation_id = f"conv_{uuid.uuid4().hex[:12]}"
        conversation = {
            "conversation_id": conversation_id,
            "phone_number": phone_number,
            "messages": [],
            "state": {
                "intent": "unknown",
                "collected_info": {},
                "next_question": None,
                "completed": False
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "appointment_id": None
        }
        
        logger.info(f"Created new conversation: {conversation_id}")
        return conversation
    
    async def _classify_intent(
        self,
        message: str,
        conversation_history: List[Dict]
    ) -> str:
        """Classify the intent of the message"""
        
        try:
            # Use Groq for intent classification
            result = await groq_agent.classify_intent(message)
            intent = result.get("intent", "unknown")
            
            logger.info(f"Intent classified as: {intent}")
            return intent
            
        except Exception as e:
            logger.error(f"Error in AI intent classification: {e}")
            # Fallback to rule-based classification
            intent = intent_classifier.classify(message, conversation_history)
            logger.info(f"Fallback intent: {intent}")
            return intent.value
    
    async def _generate_response(
        self,
        intent: str,
        message_text: str,
        conversation: Dict
    ) -> str:
        """Generate AI response based on intent and conversation state"""
        
        try:
            # Build conversation context for AI
            messages = []
            
            # Add recent message history (last 10 messages)
            recent_messages = conversation["messages"][-10:]
            for msg in recent_messages:
                messages.append({
                    "role": "user" if msg["role"] == "client" else "assistant",
                    "content": msg["text"]
                })
            
            # Get appropriate system prompt based on intent
            system_prompt = prompt_templates.get_system_prompt()
            
            # Special handling for first message (greeting)
            if len(conversation["messages"]) == 1:
                system_prompt += "\n\n" + prompt_templates.get_greeting_prompt()
            
            # Generate response using Groq
            response = await groq_agent.generate_response(
                messages=messages,
                system_prompt=system_prompt,
                temperature=0.7
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble right now. Please try again in a moment."
    
    async def _save_conversation(self, conversation: Dict):
        """Save or update conversation in database"""
        
        try:
            result = await self.db.conversations.update_one(
                {"conversation_id": conversation["conversation_id"]},
                {"$set": conversation},
                upsert=True
            )
            
            logger.debug(f"Conversation saved: {conversation['conversation_id']}")
            
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
    
    async def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Retrieve a conversation by ID"""
        
        conversation = await self.db.conversations.find_one({
            "conversation_id": conversation_id
        })
        
        return conversation
    
    async def complete_conversation(
        self,
        conversation_id: str,
        appointment_id: str = None
    ):
        """Mark conversation as completed"""
        
        await self.db.conversations.update_one(
            {"conversation_id": conversation_id},
            {
                "$set": {
                    "state.completed": True,
                    "appointment_id": appointment_id,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Conversation {conversation_id} marked as completed")

    def _update_collected_info(
        self,
        conversation: Dict,
        entities: Dict[str, Any],
        phone_number: str,
        message_text: str
    ):
        """Normalize and store extracted booking information"""
        state = conversation.setdefault("state", ConversationState().dict())
        info = state.setdefault("collected_info", {})
        if phone_number and not info.get("client_phone"):
            info["client_phone"] = phone_number
        if entities.get("phone"):
            info["client_phone"] = text_formatter.clean_phone_number(entities["phone"])
        if entities.get("email"):
            info["client_email"] = entities["email"].strip()
        if entities.get("service"):
            info["service"] = text_formatter.format_service_name(entities["service"])
        if entities.get("date"):
            info["date"] = entities["date"].strip()
        if entities.get("time"):
            info["time"] = entities["time"].strip()
        if entities.get("name"):
            info["client_name"] = text_formatter.capitalize_name(entities["name"])

        # Attempt to pull name from free text if still missing
        # Only extract from messages that explicitly mention a name
        if message_text and not info.get("client_name"):
            # Check if message contains name indicators
            name_indicators = ["name is", "i'm", "i am", "call me", "this is"]
            message_lower = message_text.lower()
            if any(indicator in message_lower for indicator in name_indicators):
                extracted = text_formatter.extract_name_from_text(message_text)
                if extracted:
                    info["client_name"] = extracted

        # Track duration if user specifies (e.g., "60 min")
        if "duration" in entities and entities["duration"]:
            try:
                info["duration_minutes"] = int(entities["duration"])
            except (TypeError, ValueError):
                pass

    async def _aggregate_booking_info(self, conversation: Dict) -> Dict[str, Any]:
        """Combine collected info with AI extraction for booking"""
        state = conversation.get("state", {})
        info = dict(state.get("collected_info", {}))
        info.setdefault("client_phone", conversation.get("phone_number"))
        missing_core = [field for field in ["client_name", "service", "date", "time"] if not info.get(field)]
        if missing_core:
            transcript = self._build_conversation_transcript(conversation.get("messages", []))
            ai_info = await groq_agent.extract_booking_info(transcript) or {}
            
            # FALLBACK: If AI extraction failed to get client_name, use regex
            if not ai_info.get("client_name") and not info.get("client_name"):
                logger.info("🔍 AI extraction missed name, trying regex fallback...")
                extracted_name = text_formatter.extract_name_from_text(transcript)
                if extracted_name:
                    logger.info(f"✅ Regex extracted name: {extracted_name}")
                    ai_info["client_name"] = extracted_name
                else:
                    logger.warning("❌ Regex also failed to extract name")
            
            mapping = {
                "client_name": "client_name",
                "service": "service",
                "date": "date",
                "time": "time",
                "barber": "barber_preference",
                "notes": "notes"
            }
            for ai_key, target_key in mapping.items():
                value = ai_info.get(ai_key)
                if value and not info.get(target_key):
                    if target_key == "service":
                        info[target_key] = text_formatter.format_service_name(value)
                    elif target_key == "client_name":
                        info[target_key] = text_formatter.capitalize_name(value)
                    else:
                        info[target_key] = value
        return info

    def _build_conversation_transcript(self, messages: List[Dict[str, Any]]) -> str:
        """Flatten last few messages for AI extraction"""
        if not messages:
            return ""
        lines = []
        recent = messages[-12:]
        for msg in recent:
            role = msg.get("role")
            speaker = "Client" if role in [MessageRole.CLIENT, "client"] else "Ava"
            lines.append(f"{speaker}: {msg.get('text', '')}")
        return "\n".join(lines)

    def _is_booking_intent(self, intent: Any) -> bool:
        """Check whether conversation intent targets booking"""
        if isinstance(intent, ConversationIntent):
            return intent == ConversationIntent.BOOK_APPOINTMENT
        return str(intent or "").lower() == ConversationIntent.BOOK_APPOINTMENT.value

    async def _attempt_appointment_creation(self, conversation: Dict) -> Optional[Dict[str, Any]]:
        """Create appointment when enough info collected"""
        state = conversation.get("state", {})
        
        # Check if appointment already exists
        if conversation.get("appointment_id"):
            logger.info(f"⏭️ Skipping - appointment already exists: {conversation.get('appointment_id')}")
            return None
        
        # Check if this is a booking intent
        current_intent = state.get("intent")
        if not self._is_booking_intent(current_intent):
            logger.info(f"⏭️ Skipping - not a booking intent (current: {current_intent})")
            return None
        
        # Aggregate all collected info
        info = await self._aggregate_booking_info(conversation)
        
        logger.info(f"📋 Collected appointment info: {json.dumps(info, default=str)}")
        
        required = ["client_name", "service", "date", "time"]
        missing = [field for field in required if not info.get(field)]
        
        # Validate client_name is not a booking keyword
        if info.get("client_name"):
            name_lower = info["client_name"].lower()
            invalid_names = ["want", "to", "book", "appointment", "want to", "to book", "i want", "looking", "would like"]
            if any(invalid_word in name_lower for invalid_word in invalid_names):
                logger.warning(f"⚠️ REJECTED invalid client name: '{info['client_name']}' - contains booking keywords")
                info["client_name"] = None
                if "client_name" not in missing:
                    missing.append("client_name")
        
        if missing:
            logger.info(f"⚠️ Missing required fields for appointment: {missing}")
            if missing:
                state["next_question"] = missing[0]
            return None
        appointment_dt = datetime_utils.parse_datetime_expression(info.get("date"), info.get("time"))
        if not appointment_dt:
            logger.warning(f"⚠️ Could not parse date/time: date={info.get('date')}, time={info.get('time')}")
            state["next_question"] = "clarify appointment time"
            return None
        is_valid, error_msg = datetime_utils.is_valid_appointment_time(appointment_dt)
        if not is_valid:
            logger.warning(f"Proposed appointment invalid: {error_msg}")
            return {"error": error_msg}
        duration = info.get("duration_minutes") or settings.DEFAULT_APPOINTMENT_DURATION
        try:
            duration = int(duration)
        except (TypeError, ValueError):
            duration = settings.DEFAULT_APPOINTMENT_DURATION
        base_phone = info.get("client_phone") or conversation.get("phone_number")
        client_phone = text_formatter.clean_phone_number(base_phone) if base_phone else None
        if not client_phone:
            state["next_question"] = "client phone number"
            return None

        payload = AppointmentCreate(
            client_name=text_formatter.capitalize_name(info["client_name"]),
            client_phone=client_phone,
            client_email=info.get("client_email"),
            service=text_formatter.format_service_name(info["service"]),
            datetime=appointment_dt,
            duration_minutes=duration,
            barber_preference=info.get("barber_preference"),
            notes=info.get("notes")
        )
        appointment_doc = payload.dict()
        appointment_doc.update({
            "status": AppointmentStatus.CONFIRMED,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "conversation_id": conversation.get("conversation_id")
        })
        try:
            logger.info(f"🔄 Attempting to create appointment for {payload.client_name}")
            result = await self.db.appointments.insert_one(appointment_doc)
            created = await self.db.appointments.find_one({"_id": result.inserted_id})
            created["id"] = str(created["_id"])
            conversation["appointment_id"] = created["id"]
            state["completed"] = True
            state["next_question"] = None
            state.setdefault("collected_info", {})["datetime_iso"] = appointment_dt.isoformat()
            state["collected_info"]["status"] = AppointmentStatus.CONFIRMED.value
            
            logger.info(f"✅ Appointment created successfully! ID: {created['id']}")
            
            appointment_details = {
                "client_name": payload.client_name,
                "service": payload.service,
                "datetime_formatted": text_formatter.format_datetime_display(
                    appointment_dt.astimezone(datetime_utils.get_timezone())
                ),
                "duration_minutes": duration
            }
            
            # Send confirmation via WhatsApp
            confirmation_msg = f"""✅ Appointment Confirmed!

{appointment_details['client_name']}, your {appointment_details['service']} appointment is confirmed for:
📅 {appointment_details['datetime_formatted']}
⏱️ Duration: {appointment_details['duration_minutes']} minutes

Looking forward to seeing you! - {settings.BUSINESS_NAME}"""
            
            whatsapp_cloud.send_text_message(payload.client_phone, confirmation_msg)
            
            confirmation_text = self._format_confirmation_text(created)
            return {"appointment": created, "confirmation_text": confirmation_text}
        except Exception as exc:
            logger.error(f"❌ Failed to create appointment from conversation: {exc}", exc_info=True)
            return {"error": "I couldn't finalize the booking automatically. Let's confirm the time manually."}

    async def _attempt_appointment_update(self, conversation: Dict) -> Optional[Dict[str, Any]]:
        """Update existing appointment when new time/date is provided"""
        appointment_id = conversation.get("appointment_id")
        if not appointment_id:
            logger.info("No existing appointment to update")
            return None
        
        state = conversation.get("state", {})
        info = await self._aggregate_booking_info(conversation)
        
        # Check if new date or time was mentioned
        new_date = info.get("date")
        new_time = info.get("time")
        
        if not (new_date or new_time):
            logger.info("No new date/time provided for update")
            return None
        
        # Parse the new datetime
        appointment_dt = datetime_utils.parse_datetime_expression(new_date, new_time)
        if not appointment_dt:
            return {"error": "I couldn't understand that time. Could you specify the date and time again?"}
        
        # Validate the new time
        is_valid, error_msg = datetime_utils.is_valid_appointment_time(appointment_dt)
        if not is_valid:
            return {"error": error_msg}
        
        # Update the appointment in database
        try:
            from bson import ObjectId
            update_data = {
                "datetime": appointment_dt,
                "updated_at": datetime.utcnow()
            }
            
            result = await self.db.appointments.update_one(
                {"_id": ObjectId(appointment_id)},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                logger.warning(f"Appointment {appointment_id} not found or not modified")
                return {"error": "I couldn't find that appointment. Would you like to book a new one?"}
            
            # Get updated appointment
            updated = await self.db.appointments.find_one({"_id": ObjectId(appointment_id)})
            updated["id"] = str(updated["_id"])
            
            # Update conversation state
            state.setdefault("collected_info", {})["datetime_iso"] = appointment_dt.isoformat()
            state["completed"] = True
            
            logger.info(f"✅ Appointment {appointment_id} updated to {appointment_dt}")
            
            # Send update confirmation SMS
            appointment_details = {
                "client_name": updated.get("client_name", ""),
                "service": updated.get("service", "appointment"),
                "datetime_formatted": text_formatter.format_datetime_display(
                    appointment_dt.astimezone(datetime_utils.get_timezone())
                ),
                "duration_minutes": updated.get("duration_minutes", 30)
            }
            
            phone = updated.get("client_phone") or conversation.get("phone_number")
            if phone:
                update_msg = f"""🔄 Appointment Updated!

Your {appointment_details['service']} appointment has been rescheduled to:
📅 {appointment_details['datetime_formatted']}

Looking forward to seeing you! - {settings.BUSINESS_NAME}"""
                whatsapp_cloud.send_text_message(phone, update_msg)
            
            confirmation_text = f"Perfect! I've updated your {updated.get('service', 'appointment').lower()} to {text_formatter.format_datetime_display(appointment_dt.astimezone(datetime_utils.get_timezone()))}."
            return {"appointment": updated, "confirmation_text": confirmation_text}
            
        except Exception as exc:
            logger.error(f"Failed to update appointment: {exc}", exc_info=True)
            return {"error": "I had trouble updating the appointment. Please try again."}

    def _format_confirmation_text(self, appointment: Dict[str, Any]) -> str:
        """Build a conversational confirmation string"""
        dt_value = appointment.get("datetime")
        formatted_time = "your requested time"
        try:
            if isinstance(dt_value, datetime):
                dt_obj = dt_value
            else:
                iso_value = str(dt_value).replace("Z", "+00:00")
                dt_obj = datetime.fromisoformat(iso_value)
            formatted_time = text_formatter.format_datetime_display(
                dt_obj.astimezone(datetime_utils.get_timezone())
            )
        except Exception:
            pass
        service = appointment.get("service", "appointment")
        return (
            f"All set! I've booked your {service.lower()} for {formatted_time}. "
            "You'll receive a confirmation text and reminder before the visit."
        )


# Singleton instance
conversation_manager = ConversationManager()
