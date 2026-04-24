"""
Vapi Webhook Router
Handles Vapi webhooks (call events, function calls, transcripts)
"""

import logging
import json
from typing import Dict, Any
from fastapi import APIRouter, Request, BackgroundTasks, HTTPException, status
from datetime import datetime

from services.vapi_service import vapi_service
from services.socket_manager import socket_manager
from services.appointments_service import AppointmentsService
from database.mongo_config import get_database

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Vapi Webhooks"])


@router.post("/webhook/{tenant_id}")
async def vapi_webhook_tenant(
    tenant_id: str,
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Tenant-specific webhook endpoint for Vapi
    """
    payload = await request.body()
    # Verify webhook auth via Vapi Credentials (Bearer or HMAC).
    if not vapi_service.verify_webhook_request(payload, dict(request.headers)):
        logger.warning("Vapi webhook auth verification failed (tenant endpoint)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_webhook_auth"
        )
    data = await request.json()
    message_type = data.get("message", {}).get("type")
    
    logger.info(f"Received Vapi webhook for tenant {tenant_id}: {message_type}")
    
    # Inject tenant_id into call metadata
    if "message" in data and "call" in data["message"]:
        if "metadata" not in data["message"]["call"]:
            data["message"]["call"]["metadata"] = {}
        data["message"]["call"]["metadata"]["tenant_id"] = tenant_id
    
    # Route by message type
    if message_type == "function-call":
        return await handle_function_call(data)
    
    elif message_type == "tool-calls":
        return await handle_tool_calls(data)
    
    elif message_type == "end-of-call-report":
        background_tasks.add_task(store_call_log, data)
    
    return {"success": True}


@router.post("/webhook")
async def vapi_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Handle Vapi webhooks (call-start, call-end, function-call, transcript, etc.)
    """
    payload = await request.body()
    
    # Verify webhook auth via Vapi Credentials (Bearer or HMAC).
    if not vapi_service.verify_webhook_request(payload, dict(request.headers)):
        logger.warning("Vapi webhook auth verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_webhook_auth"
        )
    
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
            # Persist initial call record for live analytics/history
            try:
                db = get_database()
                await db.call_logs.update_one(
                    {"vapi_call_id": call.get("id")},
                    {
                        "$set": {
                            "vapi_call_id": call.get("id"),
                            "assistant_id": call.get("assistantId"),
                            "tenant_id": tenant_id,
                            "customer_phone": call.get("customer", {}).get("number"),
                            "status": call.get("status", "started"),
                            "started_at": call.get("startedAt") or datetime.utcnow(),
                            "updated_at": datetime.utcnow(),
                            # Initialize messages array for incremental transcripts
                            "messages": []
                        }
                    },
                    upsert=True
                )
            except Exception as e:
                logger.error(f"Failed to upsert call-start record: {e}")
    
    elif message_type == "transcript":
        if tenant_id:
            transcript_text = data.get("message", {}).get("transcript")
            role = data.get("message", {}).get("role", "assistant")
            await socket_manager.broadcast_to_tenant(tenant_id, {
                "type": "transcript",
                "role": role,
                "text": transcript_text
            })
            # Append transcript message to call record for conversation history
            try:
                db = get_database()
                message_doc = {
                    "role": role,
                    "text": transcript_text,
                    "timestamp": datetime.utcnow()
                }
                await db.call_logs.update_one(
                    {"vapi_call_id": call.get("id"), "tenant_id": tenant_id},
                    {
                        "$push": {"messages": message_doc},
                        "$set": {"updated_at": datetime.utcnow()}
                    }
                )
            except Exception as e:
                logger.error(f"Failed to append transcript: {e}")

    elif message_type == "status-update":
        # Update call status and broadcast
        status_val = data.get("message", {}).get("call", {}).get("status")
        if tenant_id and status_val:
            await socket_manager.broadcast_to_tenant(tenant_id, {
                "type": "status_update",
                "call_id": call.get("id"),
                "status": status_val
            })
            try:
                db = get_database()
                await db.call_logs.update_one(
                    {"vapi_call_id": call.get("id"), "tenant_id": tenant_id},
                    {"$set": {"status": status_val, "updated_at": datetime.utcnow()}}
                )
            except Exception as e:
                logger.error(f"Failed to update status: {e}")
    
    elif message_type == "function-call":
        return await handle_function_call(data)
    
    elif message_type == "tool-calls":
        # New Vapi format for tool calls
        return await handle_tool_calls(data)
    
    elif message_type == "end-of-call-report":
        logger.info(f"🔔 Received end-of-call-report for call: {call.get('id')}")
        background_tasks.add_task(store_call_log, data)
        if tenant_id:
            await socket_manager.broadcast_to_tenant(tenant_id, {
                "type": "call_ended",
                "call_id": call.get("id"),
                "summary": data.get("message", {}).get("summary"),
                "transcript": data.get("message", {}).get("transcript"),
                "cost": data.get("message", {}).get("cost")
            })
    
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
    
    appointments_service = AppointmentsService()
    
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
        if name == "getCurrentDateTime":
            from utils.datetime_utils import DateTimeUtils
            current_time = DateTimeUtils.now()
            # Format for AI understanding: full datetime and readable date
            result_data = {
                "current_datetime": current_time.isoformat(),
                "date": current_time.strftime("%Y-%m-%d"),
                "time": current_time.strftime("%H:%M"),
                "day_of_week": current_time.strftime("%A"),
                "message": f"Current date and time: {current_time.strftime('%A, %B %d, %Y at %I:%M %p')}"
            }
            logger.info(f"✅ Current DateTime: {result_data['message']}")
        
        elif name == "checkAvailability":
            date_str = args.get("date") or datetime.now().strftime("%Y-%m-%d")
            time_str = args.get("time", "09:00")
            result = await appointments_service.check_availability(tenant_id, date_str, time_str)
            result_data = {"available": result.get("available", False), "details": result}
        
        elif name == "getAvailableServices":
            # Fetch services from database
            db = get_database()
            services_cursor = db.services.find({
                "tenant_id": tenant_id,
                "active": True
            })
            services = await services_cursor.to_list(length=100)
            
            services_list = []
            for svc in services:
                services_list.append({
                    "name": svc.get("name"),
                    "description": svc.get("description", ""),
                    "duration": f"{svc.get('duration_minutes', 30)} minutes",
                    "price": f"${svc.get('price', 0):.2f}" if svc.get('price') else "Price on request"
                })
            
            if not services_list:
                result_data = {
                    "services": [],
                    "message": "No services currently available. Please call for more information."
                }
            else:
                result_data = {
                    "services": services_list,
                    "count": len(services_list)
                }
            
            logger.info(f"Fetched {len(services_list)} services for AI agent")

        elif name == "getBusinessLocation":
            db = get_database()
            config = await db.business_config.find_one({"tenant_id": tenant_id}) if tenant_id else None
            tenant = None
            if tenant_id:
                try:
                    from bson import ObjectId
                    tenant_query = {"_id": ObjectId(tenant_id)} if ObjectId.is_valid(tenant_id) else {"_id": tenant_id}
                    tenant = await db.tenants.find_one(tenant_query)
                except Exception:
                    tenant = await db.tenants.find_one({"_id": tenant_id})

            location = (
                (config or {}).get("business_location")
                or (config or {}).get("business_address")
                or (tenant or {}).get("location")
                or (tenant or {}).get("address")
            )

            if location:
                result_data = {
                    "location": location,
                    "message": f"Our location is: {location}"
                }
            else:
                result_data = {
                    "location": None,
                    "message": "Our location is not configured yet. I can ask the team to share directions."
                }
        
        elif name == "bookAppointment":
            from models.appointment import AppointmentCreate
            from datetime import timezone
            import pytz
            from utils.config import settings
            from utils.datetime_utils import DateTimeUtils
            
            # Sanitize phone number (keep only digits, then validate 8-digit format)
            # Try both 'phone' and 'customerPhone' field names
            phone = args.get("phone") or args.get("customerPhone") or ""
            phone = "".join(c for c in phone if c.isdigit())
            
            # Ensure exactly 8 digits
            if len(phone) != 8:
                logger.error(f"Invalid phone format: '{phone}' - must be exactly 8 digits")
                return {"error": "Phone number must be exactly 8 digits (without country code)"}
            
            logger.info(f"✅ Phone sanitized and validated: {phone}")
            
            # Create timezone-aware datetime in business timezone
            date_str = args.get('date')
            time_str = args.get('time')
            
            # Log incoming values for debugging
            now = DateTimeUtils.now()
            logger.info(f"📅 Booking request - Date: {date_str}, Time: {time_str}, Current time: {now}")
            
            naive_dt = datetime.fromisoformat(f"{date_str}T{time_str}:00")
            # Localize to business timezone (user's local time)
            tz = pytz.timezone(settings.TIMEZONE)
            aware_dt = tz.localize(naive_dt)
            
            logger.info(f"⏰ Parsed datetime: {aware_dt}, Is future? {aware_dt > now}")
            
            appointment = AppointmentCreate(
                client_name=args.get("name") or args.get("customerName"),
                client_phone=phone,
                service=args.get("service", "Appointment"),
                datetime=aware_dt,
                duration_minutes=30
            )
            app_result = await appointments_service.create_appointment(tenant_id, appointment)
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
    
    # Convert to single-line JSON string per Vapi requirements
    if "error" in result_data:
        return {"error": str(result_data.get("error"))}
    else:
        result_str = json.dumps(result_data, default=str).replace('\n', ' ')
        return {"result": result_str}


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
                args = json.loads(args)
        except:
            args = {}
            
        result_data = await process_tool_call(name, args, tenant_id)
        
        # Convert result to single-line JSON string (Vapi requirement)
        if "error" in result_data:
            results.append({
                "toolCallId": tc_id,
                "error": str(result_data.get("error"))
            })
        else:
            # Return clean JSON string without Python representations
            result_str = json.dumps(result_data, default=str).replace('\n', ' ')
            results.append({
                "toolCallId": tc_id,
                "result": result_str
            })
        
    return {"results": results}


async def store_call_log(data: dict):
    """Store Vapi call report in MongoDB"""
    report = data.get("message", {})
    db = get_database()

    call_data = report.get("call", {})
    call_id = call_data.get("id")
    assistant_id = call_data.get("assistantId")
    tenant_id = call_data.get("metadata", {}).get("tenant_id")

    if not tenant_id and call_data:
        tenant_id = await resolve_tenant(call_data)
    
    logger.info(f"💾 Storing call log: call_id={call_id}, tenant_id={tenant_id}, assistant_id={assistant_id}")
    logger.debug(f"📋 Call summary: {report.get('summary')}")
    logger.debug(f"⏱️  Duration: {report.get('durationSeconds')}s, Cost: {report.get('cost')}")
    
    # Broadcast call end (duplicate broadcast to ensure delivery)
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
        "assistant_id": assistant_id,
        "tenant_id": tenant_id,
        "customer_phone": call_data.get("customer", {}).get("number"),
        "transcript": report.get("transcript"),
        "summary": report.get("summary"),
        "cost": report.get("cost"),
        "duration": report.get("durationSeconds"),
        "started_at": report.get("startedAt"),
        "ended_at": report.get("endedAt"),
        "status": report.get("status"),
        "updated_at": datetime.utcnow()
    }

    if tenant_id and call_id:
        await db.call_logs.update_one(
            {"vapi_call_id": call_id},
            {
                "$set": call_record,
                "$setOnInsert": {"created_at": datetime.utcnow()}
            },
            upsert=True
        )

        # Idempotent tenant debit (one ledger row per call id)
        raw_cost = report.get("cost")
        try:
            call_cost_usd = float(raw_cost or 0)
        except (TypeError, ValueError):
            call_cost_usd = 0.0

        if call_cost_usd > 0:
            ledger_key = f"call:{call_id}"
            existing_entry = await db.billing_ledger.find_one({"key": ledger_key})
            if not existing_entry:
                await db.billing_ledger.insert_one({
                    "key": ledger_key,
                    "type": "call_debit",
                    "tenant_id": tenant_id,
                    "assistant_id": assistant_id,
                    "vapi_call_id": call_id,
                    "amount_usd": call_cost_usd,
                    "duration_seconds": report.get("durationSeconds"),
                    "created_at": datetime.utcnow()
                })

                await db.tenants.update_one(
                    {"_id": tenant_id},
                    {
                        "$inc": {"credit_balance": -call_cost_usd},
                        "$set": {"updated_at": datetime.utcnow()}
                    }
                )

        logger.info(f"Stored call log for tenant {tenant_id}: {call_id}")
