"""
Chat Completions Router
Handles AI chat requests using OpenAI with function calling for real tool usage
"""

import logging
import os
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import httpx
import json
from datetime import datetime

from routers.users import get_current_user
from database.mongo_config import get_database
from services.appointments import check_availability, book_appointment
from bson import ObjectId

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


class ChatMessage(BaseModel):
    role: str  # 'system', 'user', 'assistant'
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    assistant_id: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 500


class ChatResponse(BaseModel):
    response: str
    tool_used: Optional[str] = None
    tool_result: Optional[Dict[str, Any]] = None


# Define tools that match the voice AI
CHAT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "checkAvailability",
            "description": "Check available appointment slots for a specific date",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date to check in YYYY-MM-DD format. Use today's date if not specified."
                    }
                },
                "required": ["date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "bookAppointment",
            "description": "Book an appointment for the customer",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Date YYYY-MM-DD"},
                    "time": {"type": "string", "description": "Time HH:MM (24 hour)"},
                    "name": {"type": "string", "description": "Customer full name"},
                    "phone": {"type": "string", "description": "Customer phone number"},
                    "service": {"type": "string", "description": "Service requested"}
                },
                "required": ["date", "time", "name", "phone"]
            }
        }
    }
]


async def execute_tool(tool_name: str, args: dict, tenant_id: str) -> dict:
    """Execute a tool and return result"""
    logger.info(f"Executing tool: {tool_name} with args: {args} for tenant: {tenant_id}")
    
    if tool_name == "checkAvailability":
        date_str = args.get("date") or datetime.now().strftime("%Y-%m-%d")
        result = await check_availability(tenant_id, date_str)
        return {"available_slots": result}
    
    elif tool_name == "bookAppointment":
        result = await book_appointment(
            tenant_id=tenant_id,
            date=args.get("date"),
            time=args.get("time"),
            customer_name=args.get("name"),
            customer_phone=args.get("phone")
        )
        return result
    
    return {"error": f"Unknown tool: {tool_name}"}


@router.post("/chat/completions", response_model=ChatResponse)
async def chat_completions(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Process chat messages and return AI response using OpenAI with function calling
    """
    tenant_id = str(current_user.get("tenant_id"))
    db = get_database()
    
    # Get tenant's system prompt if not provided
    messages = [msg.dict() for msg in request.messages]
    
    # If no system message, add one from tenant config
    if not any(m.get("role") == "system" for m in messages):
        try:
            tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
        except:
            tenant = await db.tenants.find_one({"tenant_id": tenant_id})
        
        if tenant:
            ai_config = tenant.get("ai_config", {})
            system_prompt = ai_config.get("system_prompt") or """You are Sarah, the AI receptionist for Bella's Hair Salon.

Services: Women's Haircut $45, Men's Haircut $30, Full Color $85, Highlights $120
Hours: Tuesday-Friday 9AM-7PM, Saturday 9AM-6PM, Sunday 10AM-4PM. Closed Monday.

IMPORTANT: When a customer wants to book an appointment:
1. First use checkAvailability to find open slots
2. Ask for their name, phone number, and preferred service
3. Use bookAppointment to confirm the booking
4. Always confirm the details back to the customer

Be warm, professional, and helpful!"""
            messages.insert(0, {"role": "system", "content": system_prompt})
    
    # Get OpenAI API key
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        # Try to use intelligent fallback with tool execution
        return await handle_fallback_with_tools(messages, tenant_id)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # First call with tools
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openai_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": messages,
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens,
                    "tools": CHAT_TOOLS,
                    "tool_choice": "auto"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})
            
            # Check if tool call requested
            if message.get("tool_calls"):
                tool_call = message["tool_calls"][0]
                tool_name = tool_call["function"]["name"]
                tool_args = json.loads(tool_call["function"]["arguments"])
                
                # Execute the tool
                tool_result = await execute_tool(tool_name, tool_args, tenant_id)
                
                # Add tool result to messages and get final response
                messages.append(message)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(tool_result)
                })
                
                # Get final response
                final_response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {openai_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4o-mini",
                        "messages": messages,
                        "temperature": request.temperature,
                        "max_tokens": request.max_tokens
                    }
                )
                final_response.raise_for_status()
                final_data = final_response.json()
                
                ai_response = final_data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                return ChatResponse(
                    response=ai_response,
                    tool_used=tool_name,
                    tool_result=tool_result
                )
            
            # No tool call, just return response
            ai_response = message.get("content", "")
            return ChatResponse(response=ai_response)
    
    except httpx.HTTPError as e:
        logger.error(f"OpenAI API error: {e}")
        return await handle_fallback_with_tools(messages, tenant_id)
    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        return await handle_fallback_with_tools(messages, tenant_id)


async def handle_fallback_with_tools(messages: List[dict], tenant_id: str) -> ChatResponse:
    """Handle chat with intelligent fallback + real tool execution"""
    logger.warning("Using fallback with real tool execution")
    
    # Get the last user message
    user_message = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_message = msg.get("content", "").lower()
            break
    
    # Check if user wants availability
    if any(word in user_message for word in ["available", "slot", "time", "when", "book", "appointment", "schedule"]):
        # Detect date
        date_str = datetime.now().strftime("%Y-%m-%d")
        if "tomorrow" in user_message:
            from datetime import timedelta
            date_str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "saturday" in user_message:
            # Find next Saturday
            from datetime import timedelta
            today = datetime.now()
            days_ahead = 5 - today.weekday()  # Saturday is 5
            if days_ahead <= 0:
                days_ahead += 7
            date_str = (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        
        # Actually check availability
        availability = await check_availability(tenant_id, date_str)
        slots = availability.get("slots", [])
        
        if slots:
            slots_str = ", ".join(slots[:6])
            response = f"Great news! I have these times available on {date_str}: {slots_str}. Which time works best for you? I'll need your name and phone number to complete the booking."
        else:
            response = f"I'm sorry, we don't have any available slots on {date_str}. Would you like to try a different day?"
        
        return ChatResponse(
            response=response,
            tool_used="checkAvailability",
            tool_result={"date": date_str, "slots": slots}
        )
    
    # Check if user is providing booking info
    if any(word in user_message for word in ["name is", "i'm ", "my name", "phone", "call me"]):
        response = "Thank you! And what time would you like to come in? I have slots available at 9:00 AM, 10:00 AM, 11:00 AM, 2:00 PM, and 3:00 PM."
        return ChatResponse(response=response)
    
    # Price inquiry
    if any(word in user_message for word in ["price", "cost", "how much", "rate"]):
        response = """Here are our services and prices:

• Women's Haircut: $45-65 (45 min)
• Men's Haircut: $30-40 (30 min)  
• Full Color: $85-120 (2 hours)
• Highlights: $95-185 (2 hours)
• Blowout: $45 (45 min)

Would you like to book an appointment for any of these services?"""
        return ChatResponse(response=response)
    
    # Hours inquiry
    if any(word in user_message for word in ["hour", "open", "close", "when are you"]):
        response = """Our business hours are:
• Tuesday - Friday: 9 AM - 7 PM
• Saturday: 9 AM - 6 PM  
• Sunday: 10 AM - 4 PM
• Monday: CLOSED

Would you like to schedule an appointment?"""
        return ChatResponse(response=response)
    
    # Default helpful response
    return ChatResponse(
        response="I'm here to help! I can check appointment availability, book appointments, or answer questions about our services and pricing. What would you like to do?"
    )
