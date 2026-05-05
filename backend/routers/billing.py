"""
Billing Router - Subscription management with Stripe (Mock Mode for Testing)
Handles checkout, webhooks, portal, and subscription status
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Query, status
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from bson import ObjectId

from database.mongo_config import get_database
from routers.users import get_current_user
from services.stripe_service import get_stripe_service, is_mock_mode
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class CheckoutRequest(BaseModel):
    """Request to create checkout session"""
    pass  # No fields needed, uses current user


class SubscriptionResponse(BaseModel):
    """Subscription status response"""
    status: str
    plan_name: str
    plan_price: str
    trial_end: str | None
    current_period_end: str
    cancel_at_period_end: bool
    is_mock: bool


def _extract_plan_amount_cents(subscription: Dict[str, Any]) -> int | None:
    """Extract recurring plan amount in cents from Stripe or mock subscription payload."""
    if not subscription:
        return None

    plan = subscription.get("plan") or {}
    plan_amount = plan.get("amount")
    if isinstance(plan_amount, (int, float)):
        return int(plan_amount)

    items = subscription.get("items", {}).get("data", [])
    if items and isinstance(items, list):
        first_item = items[0] or {}
        price = first_item.get("price") or {}
        unit_amount = price.get("unit_amount")
        if isinstance(unit_amount, (int, float)):
            return int(unit_amount)

    return None


def _extract_plan_interval(subscription: Dict[str, Any]) -> str:
    """Extract recurring interval (month/year) with sensible default."""
    plan = subscription.get("plan") or {}
    interval = plan.get("interval")
    if isinstance(interval, str) and interval:
        return interval

    items = subscription.get("items", {}).get("data", [])
    if items and isinstance(items, list):
        first_item = items[0] or {}
        price = first_item.get("price") or {}
        recurring = price.get("recurring") or {}
        recurring_interval = recurring.get("interval")
        if isinstance(recurring_interval, str) and recurring_interval:
            return recurring_interval

    return "month"


def _format_plan_price(amount_cents: int | None, interval: str = "month") -> str:
    """Format plan amount to user-facing price string."""
    if amount_cents is None:
        return "$0/month"
    amount_dollars = amount_cents / 100
    return f"${amount_dollars:.0f}/{interval}"


@router.post("/checkout")
async def create_checkout_session(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Create Stripe checkout session for $499/month subscription
    In mock mode: instant success, no real charge
    """
    stripe_service = get_stripe_service()
    db = get_database()
    
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(status_code=400, detail="User has no tenant_id")
        
        # Check if tenant already has a subscription
        tenant_query = {"_id": ObjectId(tenant_id)} if ObjectId.is_valid(tenant_id) else {"$or": [{"_id": tenant_id}, {"tenant_id": tenant_id}]}
        tenant = await db.tenants.find_one(tenant_query)
        if tenant and tenant.get("stripe_subscription_id"):
            raise HTTPException(
                status_code=400,
                detail="You already have an active subscription"
            )
        
        # Get or create Stripe customer
        stripe_customer_id = tenant.get("stripe_customer_id") if tenant else None
        
        if not stripe_customer_id:
            # Create new customer
            email = current_user.get("email") or ""
            customer = await stripe_service.create_customer(
                email=email,
                name=current_user.get("full_name", ""),
                tenant_id=tenant_id
            )
            stripe_customer_id = customer["id"]
            
            # Save customer ID to tenant
            await db.tenants.update_one(
                {"_id": ObjectId(tenant_id)} if ObjectId.is_valid(tenant_id) else {"$or": [{"_id": tenant_id}, {"tenant_id": tenant_id}]},
                {"$set": {"stripe_customer_id": stripe_customer_id}}
            )
        
        # Create checkout session
        base_url = str(request.base_url).rstrip("/")
        success_url = f"{base_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{base_url}/payment/cancel"
        
        # Replace {CHECKOUT_SESSION_ID} with actual placeholder for Stripe
        if not is_mock_mode():
            success_url = success_url.replace("{CHECKOUT_SESSION_ID}", "{CHECKOUT_SESSION_ID}")
        
        session = await stripe_service.create_checkout_session(
            customer_id=stripe_customer_id,
            tenant_id=tenant_id,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        logger.info(f"{'🧪 Mock' if is_mock_mode() else '💳'} Checkout session created: {session['id']}")
        
        return {
            "checkout_url": session["url"],
            "session_id": session["id"],
            "is_mock": is_mock_mode()
        }
        
    except Exception as e:
        logger.error(f"Failed to create checkout session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mock-complete-checkout")
async def mock_complete_checkout(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Complete mock checkout (TEST MODE ONLY)
    Simulates successful payment without real charges
    """
    if not is_mock_mode():
        raise HTTPException(status_code=400, detail="This endpoint is only for mock mode")
    
    stripe_service = get_stripe_service()
    db = get_database()
    
    try:
        # Complete the checkout
        result = await stripe_service.complete_checkout(session_id)
        subscription = result["subscription"]
        
        # Get tenant_id from subscription metadata
        tenant_id = subscription["metadata"].get("tenant_id")
        if not tenant_id:
            raise HTTPException(status_code=400, detail="No tenant_id in subscription")
        
        # Update tenant with subscription info
        await db.tenants.update_one(
            {"_id": tenant_id},
            {
                "$set": {
                    "stripe_subscription_id": subscription["id"],
                    "subscription_status": subscription["status"],
                    "trial_start_date": datetime.fromtimestamp(subscription["trial_start"]),
                    "trial_end_date": datetime.fromtimestamp(subscription["trial_end"]),
                    "current_period_end": datetime.fromtimestamp(subscription["current_period_end"]),
                    "plan": "pro",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"🧪 Mock subscription activated for tenant {tenant_id}")
        
        return {
            "success": True,
            "subscription_id": subscription["id"],
            "status": subscription["status"],
            "message": "🧪 Mock payment successful! No real charges made."
        }
        
    except Exception as e:
        logger.error(f"Failed to complete mock checkout: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription_status(current_user: dict = Depends(get_current_user)):
    """
    Get current subscription status
    """
    db = get_database()
    
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(status_code=400, detail="User has no tenant_id")
        
        tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)} if ObjectId.is_valid(tenant_id) else {"$or": [{"_id": tenant_id}, {"tenant_id": tenant_id}]})
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        subscription_id = tenant.get("stripe_subscription_id")
        if not subscription_id:
            raise HTTPException(
                status_code=404,
                detail="No active subscription"
            )
        
        # Get subscription from Stripe (or mock)
        stripe_service = get_stripe_service()
        subscription = await stripe_service.get_subscription(subscription_id)
        
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        # Format response
        trial_end = None
        if subscription.get("trial_end"):
            trial_end = datetime.fromtimestamp(subscription["trial_end"]).isoformat()
        
        current_period_end = datetime.fromtimestamp(subscription["current_period_end"]).isoformat()
        
        amount_cents = _extract_plan_amount_cents(subscription)
        interval = _extract_plan_interval(subscription)
        plan_price = _format_plan_price(amount_cents, interval)

        return SubscriptionResponse(
            status=subscription["status"],
            plan_name="AI Receptionist Pro",
            plan_price=plan_price,
            trial_end=trial_end,
            current_period_end=current_period_end,
            cancel_at_period_end=subscription.get("cancel_at_period_end", False),
            is_mock=is_mock_mode()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get subscription status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/portal")
async def create_portal_session(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Create Stripe customer portal session
    Allows users to manage subscription, payment methods, invoices
    """
    stripe_service = get_stripe_service()
    db = get_database()
    
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(status_code=400, detail="User has no tenant_id")
        
        tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)} if ObjectId.is_valid(tenant_id) else {"$or": [{"_id": tenant_id}, {"tenant_id": tenant_id}]})
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        stripe_customer_id = tenant.get("stripe_customer_id")
        if not stripe_customer_id:
            raise HTTPException(
                status_code=400,
                detail="No Stripe customer ID found"
            )
        
        # Create portal session
        base_url = str(request.base_url).rstrip("/")
        return_url = f"{base_url}/dashboard/settings/billing"
        
        session = await stripe_service.create_portal_session(
            customer_id=stripe_customer_id,
            return_url=return_url
        )
        
        return {
            "portal_url": session["url"],
            "is_mock": is_mock_mode()
        }
        
    except Exception as e:
        logger.error(f"Failed to create portal session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard-summary")
async def get_dashboard_billing_summary(current_user: dict = Depends(get_current_user)):
    """
    Get compact billing + usage stats for dashboard navbar/sidebar.
    """
    db = get_database()

    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(status_code=400, detail="User has no tenant_id")

        tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)} if ObjectId.is_valid(tenant_id) else {"$or": [{"_id": tenant_id}, {"tenant_id": tenant_id}]})
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")

        assistant_id = tenant.get("vapi_assistant_id")

        # Subscription details (if available)
        plan_price = "$0/month"
        subscription_status = tenant.get("subscription_status") or "inactive"
        current_period_end = tenant.get("current_period_end")

        subscription_id = tenant.get("stripe_subscription_id")
        if subscription_id:
            stripe_service = get_stripe_service()
            subscription = await stripe_service.get_subscription(subscription_id)
            if subscription:
                amount_cents = _extract_plan_amount_cents(subscription)
                interval = _extract_plan_interval(subscription)
                plan_price = _format_plan_price(amount_cents, interval)
                subscription_status = subscription.get("status", subscription_status)
                if subscription.get("current_period_end"):
                    current_period_end = datetime.fromtimestamp(subscription["current_period_end"])

        # Usage stats (last 30 days), limited to this tenant and assistant
        usage_query: Dict[str, Any] = {"tenant_id": tenant_id}
        if assistant_id:
            usage_query["assistant_id"] = assistant_id

        call_logs = await db.call_logs.find(usage_query).to_list(length=5000)

        usage_entries = [
            call for call in call_logs
            if call.get("duration") is not None or call.get("cost") is not None
        ]

        total_calls = len(usage_entries)
        total_duration_seconds = sum((call.get("duration") or 0) for call in usage_entries)
        total_cost = sum((call.get("cost") or 0) for call in usage_entries)

        total_minutes = round(total_duration_seconds / 60, 2) if total_duration_seconds else 0.0
        avg_cost_per_minute = round(total_cost / total_minutes, 4) if total_minutes > 0 else 0.0

        # Optional tenant-level credit fields (if present in DB)
        tenant_credit_balance = (
            tenant.get("vapi_credit_balance")
            if tenant.get("vapi_credit_balance") is not None
            else tenant.get("credit_balance")
        )
        if tenant_credit_balance is not None:
            try:
                tenant_credit_balance = round(float(tenant_credit_balance), 2)
            except (TypeError, ValueError):
                tenant_credit_balance = None

        return {
            "plan": tenant.get("plan", "free"),
            "plan_price": plan_price,
            "subscription_status": subscription_status,
            "current_period_end": current_period_end.isoformat() if isinstance(current_period_end, datetime) else current_period_end,
            "assistant_id": assistant_id,
            "usage": {
                "total_calls": total_calls,
                "total_minutes": total_minutes,
                "total_cost": round(total_cost, 4),
                "avg_cost_per_minute": avg_cost_per_minute
            },
            "tenant_credit_balance": tenant_credit_balance,
            "is_mock": is_mock_mode()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get dashboard billing summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhooks
    Events: checkout.session.completed, invoice.paid, customer.subscription.deleted, etc.
    
    In mock mode: simulates webhook processing
    In live mode: verifies signature and processes real events
    """
    stripe_service = get_stripe_service()
    db = get_database()
    
    try:
        # Get raw body and signature
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature", "")
        
        # Construct and verify event
        event = await stripe_service.construct_webhook_event(payload, sig_header)
        
        event_type = event["type"]
        logger.info(f"{'🧪' if is_mock_mode() else '💳'} Webhook received: {event_type}")
        
        # Handle different event types
        if event_type == "checkout.session.completed":
            await handle_checkout_completed(event["data"]["object"], db)
        
        elif event_type == "invoice.paid":
            await handle_invoice_paid(event["data"]["object"], db)
        
        elif event_type == "customer.subscription.updated":
            await handle_subscription_updated(event["data"]["object"], db)
        
        elif event_type == "customer.subscription.deleted":
            await handle_subscription_deleted(event["data"]["object"], db)
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        )


async def handle_checkout_completed(session: Dict[str, Any], db):
    """Handle successful checkout"""
    subscription_id = session.get("subscription")
    tenant_id = session.get("metadata", {}).get("tenant_id")
    
    if not tenant_id or not subscription_id:
        logger.error("Missing tenant_id or subscription_id in checkout session")
        return
    
    # Get subscription details
    stripe_service = get_stripe_service()
    subscription = await stripe_service.get_subscription(subscription_id)
    
    if not subscription:
        logger.error(f"Subscription {subscription_id} not found")
        return

    amount_cents = _extract_plan_amount_cents(subscription)
    plan_amount_usd = round((amount_cents or 0) / 100, 2)
    
    # Update tenant
    await db.tenants.update_one(
        {"_id": tenant_id},
        {
            "$set": {
                "stripe_subscription_id": subscription_id,
                "subscription_status": subscription["status"],
                "trial_start_date": datetime.fromtimestamp(subscription.get("trial_start", 0)) if subscription.get("trial_start") else None,
                "trial_end_date": datetime.fromtimestamp(subscription.get("trial_end", 0)) if subscription.get("trial_end") else None,
                "current_period_end": datetime.fromtimestamp(subscription["current_period_end"]),
                "plan": "pro",
                "monthly_subscription_amount_usd": plan_amount_usd,
                "credit_balance": plan_amount_usd,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    logger.info(f"Subscription {subscription_id} activated for tenant {tenant_id}")


async def handle_invoice_paid(invoice: Dict[str, Any], db):
    """Handle successful payment"""
    subscription_id = invoice.get("subscription")
    if not subscription_id:
        return
    
    # Update tenant's current period
    tenant = await db.tenants.find_one({"stripe_subscription_id": subscription_id})
    if tenant:
        amount_paid_cents = invoice.get("amount_paid")
        recharge_amount = None
        if isinstance(amount_paid_cents, (int, float)):
            recharge_amount = round(float(amount_paid_cents) / 100, 2)
        elif tenant.get("monthly_subscription_amount_usd") is not None:
            recharge_amount = float(tenant.get("monthly_subscription_amount_usd"))

        update_doc: Dict[str, Any] = {
            "$set": {
                "subscription_status": "active",
                "updated_at": datetime.utcnow()
            }
        }
        if recharge_amount and recharge_amount > 0:
            update_doc["$inc"] = {"credit_balance": recharge_amount}

        await db.tenants.update_one(
            {"_id": tenant["_id"]},
            update_doc
        )
        logger.info(f"Invoice paid for subscription {subscription_id}")


async def handle_subscription_updated(subscription: Dict[str, Any], db):
    """Handle subscription updates"""
    subscription_id = subscription["id"]
    
    tenant = await db.tenants.find_one({"stripe_subscription_id": subscription_id})
    if tenant:
        amount_cents = _extract_plan_amount_cents(subscription)
        plan_amount_usd = round((amount_cents or 0) / 100, 2)

        await db.tenants.update_one(
            {"_id": tenant["_id"]},
            {
                "$set": {
                    "subscription_status": subscription["status"],
                    "current_period_end": datetime.fromtimestamp(subscription["current_period_end"]),
                    "cancel_at_period_end": subscription.get("cancel_at_period_end", False),
                    "monthly_subscription_amount_usd": plan_amount_usd,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        logger.info(f"Subscription {subscription_id} updated: {subscription['status']}")


async def handle_subscription_deleted(subscription: Dict[str, Any], db):
    """Handle subscription cancellation"""
    subscription_id = subscription["id"]

    tenant = await db.tenants.find_one({"stripe_subscription_id": subscription_id})
    if tenant:
        await db.tenants.update_one(
            {"_id": tenant["_id"]},
            {
                "$set": {
                    "subscription_status": "canceled",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        logger.info(f"Subscription {subscription_id} canceled")


# ==================== USAGE & LEDGER ====================

@router.get("/usage")
async def get_billing_usage(current_user: dict = Depends(get_current_user)):
    """
    Per-assistant usage breakdown for the current tenant.
    Shows total calls, minutes, and cost grouped by Vapi assistant ID,
    plus the tenant's current credit balance and subscription amount.
    """
    db = get_database()
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="User has no tenant_id")

    tenant_query = (
        {"_id": ObjectId(tenant_id)} if ObjectId.is_valid(tenant_id)
        else {"$or": [{"_id": tenant_id}, {"tenant_id": tenant_id}]}
    )
    tenant = await db.tenants.find_one(tenant_query)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Aggregate billing_ledger by assistant_id for this tenant
    pipeline = [
        {"$match": {"tenant_id": tenant_id, "type": "call_debit"}},
        {
            "$group": {
                "_id": "$assistant_id",
                "total_calls": {"$sum": 1},
                "total_cost_usd": {"$sum": "$amount_usd"},
                "total_duration_seconds": {"$sum": "$duration_seconds"},
            }
        },
        {"$sort": {"total_cost_usd": -1}},
    ]
    rows = await db.billing_ledger.aggregate(pipeline).to_list(length=200)

    assistants: List[Dict[str, Any]] = []
    for row in rows:
        duration_s = row.get("total_duration_seconds") or 0
        total_minutes = round(duration_s / 60, 2)
        cost = round(row.get("total_cost_usd") or 0, 4)
        avg_cost_per_min = round(cost / total_minutes, 4) if total_minutes > 0 else 0.0
        assistants.append({
            "assistant_id": row["_id"],
            "total_calls": row.get("total_calls", 0),
            "total_minutes": total_minutes,
            "total_cost_usd": cost,
            "avg_cost_per_minute": avg_cost_per_min,
        })

    summary = {
        "total_calls": sum(a["total_calls"] for a in assistants),
        "total_minutes": round(sum(a["total_minutes"] for a in assistants), 2),
        "total_cost_usd": round(sum(a["total_cost_usd"] for a in assistants), 4),
    }

    credit_balance = tenant.get("credit_balance") or tenant.get("vapi_credit_balance") or 0
    monthly_sub = tenant.get("monthly_subscription_amount_usd") or 0

    return {
        "tenant_id": tenant_id,
        "credit_balance": round(float(credit_balance), 2),
        "monthly_subscription_usd": round(float(monthly_sub), 2),
        "assistants": assistants,
        "summary": summary,
    }


@router.get("/ledger")
async def get_billing_ledger(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    assistant_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """
    Paginated billing ledger for the current tenant.
    Each entry represents one call debit (cost charged after a Vapi call).
    Optionally filter by assistant_id.
    """
    db = get_database()
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="User has no tenant_id")

    match: Dict[str, Any] = {"tenant_id": tenant_id, "type": "call_debit"}
    if assistant_id:
        match["assistant_id"] = assistant_id

    skip = (page - 1) * limit
    total = await db.billing_ledger.count_documents(match)
    cursor = (
        db.billing_ledger.find(match, {"_id": 0, "key": 0})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )
    entries = await cursor.to_list(length=limit)

    for entry in entries:
        if isinstance(entry.get("created_at"), datetime):
            entry["created_at"] = entry["created_at"].isoformat()

    return {
        "entries": entries,
        "page": page,
        "limit": limit,
        "total": total,
        "has_more": (skip + limit) < total,
    }


@router.post("/sync-vapi")
@limiter.limit("2/minute")
async def sync_vapi_usage(request: Request, current_user: dict = Depends(get_current_user)):
    """
    Pull all calls for this tenant's Vapi assistant and create any missing
    billing_ledger entries + credit_balance debits.
    Safe to call repeatedly — fully idempotent (one ledger row per call_id).
    Returns the number of new entries created and total amount reconciled.
    """
    from services.vapi_service import vapi_service

    db = get_database()
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="User has no tenant_id")

    tenant_query = (
        {"_id": ObjectId(tenant_id)} if ObjectId.is_valid(tenant_id)
        else {"$or": [{"_id": tenant_id}, {"tenant_id": tenant_id}]}
    )
    tenant = await db.tenants.find_one(tenant_query)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    assistant_id = tenant.get("vapi_assistant_id")
    if not assistant_id:
        raise HTTPException(status_code=400, detail="Tenant has no Vapi assistant configured")

    if not vapi_service.is_configured():
        raise HTTPException(status_code=503, detail="Vapi not configured")

    # Fetch up to 1000 calls for this assistant from Vapi
    vapi_calls = await vapi_service.list_calls(assistant_id=assistant_id, limit=1000)
    if not isinstance(vapi_calls, list):
        vapi_calls = vapi_calls.get("results") or vapi_calls.get("data") or []

    created_count = 0
    reconciled_usd = 0.0

    for call in vapi_calls:
        call_id = call.get("id")
        if not call_id:
            continue

        raw_cost = call.get("cost")
        if isinstance(raw_cost, dict):
            call_cost = float(raw_cost.get("total") or raw_cost.get("amount") or 0)
        else:
            try:
                call_cost = float(raw_cost or 0)
            except (TypeError, ValueError):
                call_cost = 0.0

        if call_cost <= 0:
            continue

        ledger_key = f"call:{call_id}"
        existing = await db.billing_ledger.find_one({"key": ledger_key})
        if existing:
            continue

        duration_s = call.get("durationSeconds") or 0

        await db.billing_ledger.insert_one({
            "key": ledger_key,
            "type": "call_debit",
            "tenant_id": tenant_id,
            "assistant_id": assistant_id,
            "vapi_call_id": call_id,
            "amount_usd": call_cost,
            "duration_seconds": duration_s,
            "created_at": datetime.utcnow(),
            "synced_from_vapi": True,
        })

        await db.tenants.update_one(
            tenant_query,
            {
                "$inc": {"credit_balance": -call_cost},
                "$set": {"updated_at": datetime.utcnow()},
            },
        )

        # Upsert a minimal call_log entry so the calls page shows it
        await db.call_logs.update_one(
            {"vapi_call_id": call_id},
            {
                "$setOnInsert": {
                    "vapi_call_id": call_id,
                    "assistant_id": assistant_id,
                    "tenant_id": tenant_id,
                    "customer_phone": (call.get("customer") or {}).get("number"),
                    "cost": call_cost,
                    "duration": duration_s,
                    "status": call.get("status"),
                    "started_at": call.get("startedAt") or call.get("createdAt"),
                    "ended_at": call.get("endedAt"),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
            },
            upsert=True,
        )

        created_count += 1
        reconciled_usd += call_cost

    logger.info(
        f"Vapi sync for tenant {tenant_id}: {created_count} new entries, ${reconciled_usd:.4f} reconciled"
    )

    return {
        "synced": created_count,
        "reconciled_usd": round(reconciled_usd, 4),
        "message": f"Created {created_count} missing ledger entries totalling ${reconciled_usd:.4f}",
    }
