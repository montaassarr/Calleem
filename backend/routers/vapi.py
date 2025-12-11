"""
Vapi Webhook Router
Handles Vapi webhooks (call events, function calls, transcripts)
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Request, Header, BackgroundTasks
from datetime import datetime

from services.vapi_service import vapi_service
from services.socket_manager import socket_manager
from services.appointments import check_availability, book_appointment
from database.mongo_config import get_database

logger = logging.getLogger(__name__)

router = APIRouter(tags=["vapi-webhooks"])


@router.post("/webhook")
async def vapi_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_vapi_signature: str = Header(None)
):
    """
    Handle Vapi webhooks (call-start, call-end, function-call, transcript, etc.)
    """
    payload = await request.body()
    
    # Verify signature
    if not vapi_service.verify_webhook_signature(payload, x_vapi_signature or ""):
        logger.warning("Vapi webhook signature verification failed")
        # For now log warn, strict later
    
    data = await request.json()
    message_type = data.get("message", {}).get("type")
    
    logger.info(f"Received Vapi webhook: {message_type}")
    
    # Extract common fields
    call = data.get("message", {}).get("call", {})
    tenant_id = call.get("metadata", {}).get("tenant_id")
    
    # Route by message type
    if message_type == "call-start":
        if tenant_id:
            await socket_manager.broadcast_to_tenant(tenant_id, {
                "type": "call_started",
                "call_id": call.get("id"),
                "caller_number": call.get("customer", {}).get("number")
            })
    
    elif message_type == "transcript":
        if tenant_id:
            transcript_text = data.get("message", {}).get("transcript")
            role = data.get("message", {}).get("role", "assistant")
            await socket_manager.broadcast_to_tenant(tenant_id, {
                "type": "transcript",
                "role": role,
                "text": transcript_text
            })
    
    elif message_type == "function-call":
        return await handle_function_call(data)
    
    elif message_type == "tool-calls":
        # New Vapi format for tool calls
        return await handle_tool_calls(data)
    
    elif message_type == "end-of-call-report":
        background_tasks.add_task(store_call_log, data)
    
    return {"success": True}


async def resolve_tenant(call: dict) -> str:
    """Resolve tenant_id from call metadata or assistant_id"""
    metadata_tenant_id = call.get("metadata", {}).get("tenant_id")
    assistant_id = call.get("assistantId")
    
    db = get_database()
    tenant_id = metadata_tenant_id  # Fallback
    
    if assistant_id:
        tenant = await db.tenants.find_one({"vapi_assistant_id": assistant_id})
        if tenant:
            tenant_id = str(tenant.get("_id"))
            logger.info(f"Resolved tenant_id {tenant_id} from assistant {assistant_id}")
            
    return tenant_id


async def process_tool_call(name: str, args: dict, tenant_id: str) -> dict:
    """Process a single tool call execution and broadcasting"""
    logger.info(f"Processing Tool Call: {name} (tenant={tenant_id}) args={args}")
    
    # Broadcast available to tenant
    if tenant_id:
        await socket_manager.broadcast_to_tenant(tenant_id, {
            "type": "tool_usage",
            "tool": name,
            "args": args,
            "status": "started"
        })
    
    result_data = {}
    
    try:
        if name == "checkAvailability":
            date_str = args.get("date") or datetime.now().strftime("%Y-%m-%d")
            slots = await check_availability(tenant_id, date_str)
            result_data = {"available_slots": slots}
        
        elif name == "bookAppointment":
            app_result = await book_appointment(
                tenant_id=tenant_id,
                date=args.get("date"),
                time=args.get("time"),
                customer_name=args.get("name"),
                customer_phone=args.get("phone")
            )
            result_data = {"success": True, "details": app_result}
        
        else:
            result_data = {"error": f"Unknown function {name}"}
    
    except Exception as e:
        logger.error(f"Function call error: {e}")
        result_data = {"error": str(e)}
    
    # Broadcast result
    if tenant_id:
        await socket_manager.broadcast_to_tenant(tenant_id, {
            "type": "tool_usage",
            "tool": name,
            "result": result_data,
            "status": "completed"
        })
        
    return result_data


async def handle_function_call(data: dict) -> dict:
    """Handle legacy Vapi function calls (single tool)"""
    call = data.get("message", {}).get("call", {})
    function_call = data.get("message", {}).get("functionCall", {})
    name = function_call.get("name")
    args = function_call.get("parameters", {})
    
    tenant_id = await resolve_tenant(call)
    
    result_data = await process_tool_call(name, args, tenant_id)
    return {"result": str(result_data)}


async def handle_tool_calls(data: dict) -> dict:
    """Handle new Vapi tool calls (multiple tools)"""
    call = data.get("message", {}).get("call", {})
    tool_calls = data.get("message", {}).get("toolCalls", [])
    
    tenant_id = await resolve_tenant(call)
    
    results = []
    for tool_call in tool_calls:
        tc_id = tool_call.get("id")
        function = tool_call.get("function", {})
        name = function.get("name")
        try:
            # args can be string or dict depending on Vapi version
            args = function.get("arguments", {})
            if isinstance(args, str):
                import json
                args = json.loads(args)
        except:
            args = {}
            
        result_data = await process_tool_call(name, args, tenant_id)
        
        results.append({
            "toolCallId": tc_id,
            "result": str(result_data)
        })
        
    return {"results": results}


async def store_call_log(data: dict):
    """Store Vapi call report in MongoDB"""
    report = data.get("message", {})
    db = get_database()
    
    call_id = report.get("call", {}).get("id")
    tenant_id = report.get("call", {}).get("metadata", {}).get("tenant_id")
    
    # Broadcast call end
    if tenant_id:
        await socket_manager.broadcast_to_tenant(tenant_id, {
            "type": "call_ended",
            "call_id": call_id,
            "summary": report.get("summary"),
            "transcript": report.get("transcript"),
            "cost": report.get("cost")
        })
    
    # Build call record
    call_record = {
        "vapi_call_id": call_id,
        "assistant_id": report.get("call", {}).get("assistantId"),
        "tenant_id": tenant_id,
        "customer_phone": report.get("call", {}).get("customer", {}).get("number"),
        "transcript": report.get("transcript"),
        "summary": report.get("summary"),
        "cost": report.get("cost"),
        "duration": report.get("durationSeconds"),
        "started_at": report.get("startedAt"),
        "ended_at": report.get("endedAt"),
        "status": report.get("status"),
        "created_at": datetime.utcnow()
    }
    
    if tenant_id:
        await db.call_logs.insert_one(call_record)
        logger.info(f"Stored call log for tenant {tenant_id}: {call_id}")
