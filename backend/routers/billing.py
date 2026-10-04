"""
Billing Router - Subscription management with Stripe (Mock Mode for Testing)
Handles checkout, webhooks, portal, and subscription status
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Query, status
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Literal, Optional
from datetime import datetime
import logging
from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from database.mongo_config import get_database
from routers.users import get_current_admin, get_current_user
from services import stripe_events, usage_billing
from services.stripe_service import get_stripe_service, is_mock_mode
from utils.config import settings
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


ACTIVE_SUBSCRIPTION_STATUSES = ("active", "trialing", "past_due")


class CheckoutRequest(BaseModel):
    """A monthly plan sized by usage (calls + avg_minutes), or a one-time pack of minutes."""
    kind: Literal["plan", "minutes"]
    calls: Optional[int] = None
    avg_minutes: Optional[float] = None
    minutes: Optional[int] = None


class ChangePlanRequest(BaseModel):
    calls: int
    avg_minutes: float


class SubscriptionResponse(BaseModel):
    """Subscription status response"""
    status: str
    plan_name: str
    plan_price: str
    trial_end: str | None
    current_period_end: str | None
    cancel_at_period_end: bool
    is_mock: bool


def _extract_plan_amount_cents(subscription: Dict[str, Any]) -> int | None:
    """Extract recurring plan amount in cents from Stripe or mock subscription payload."""
    if not subscription:
        return None
    return stripe_events.subscription_amount_cents(subscription)


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


def _frontend_url(path: str) -> str:
    return f"{settings.FRONTEND_URL.rstrip('/')}{path}"


def online_checkout_ready() -> bool:
    """Stripe is live (not mock mode): clients can pay by card from the billing page."""
    return not is_mock_mode()


def _plan_metadata(plan: Dict[str, Any]) -> Dict[str, str]:
    """Stripe metadata is strings; every renewal invoice carries it, so minutes follow the plan."""
    return {
        "kind": "plan",
        "calls": str(plan["calls"]),
        "avg_minutes": str(plan["avg_minutes"]),
        "minutes": str(plan["minutes"]),
        "price_usd": str(plan["price_usd"]),
    }


def _usage_quote(calls: Any, avg_minutes: Any) -> Dict[str, Any]:
    try:
        calls, avg_minutes = usage_billing.validate_usage(calls, avg_minutes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return usage_billing.quote(calls, avg_minutes)


@router.post("/checkout")
async def create_checkout_session(
    body: CheckoutRequest,
    current_admin: dict = Depends(get_current_admin),
):
    """Start Stripe Checkout for a monthly plan or a minutes pack; returns the page to redirect to."""
    if is_mock_mode():
        raise HTTPException(status_code=503, detail="Online payment is not set up yet")
    if body.kind == "plan":
        plan = _usage_quote(body.calls, body.avg_minutes)
        mode, amount_cents, metadata = "subscription", plan["price_usd"] * 100, _plan_metadata(plan)
    else:
        if body.minutes not in usage_billing.TOPUP_PACKS:
            raise HTTPException(status_code=400, detail="Unknown minutes pack")
        pack = usage_billing.topup_quote(body.minutes)
        mode, amount_cents = "payment", int(round(pack["price_usd"] * 100))
        metadata = {"kind": "minutes", "minutes": str(pack["minutes"])}

    db = get_database()
    tenant_id = _current_tenant_id(current_admin)
    tenant = await db.tenants.find_one(usage_billing.tenant_query(tenant_id))
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    if (
        mode == "subscription"
        and tenant.get("stripe_subscription_id")
        and tenant.get("subscription_status") in ACTIVE_SUBSCRIPTION_STATUSES
    ):
        raise HTTPException(status_code=409, detail="You already have a plan. Use Change plan instead.")

    stripe_service = get_stripe_service()
    try:
        customer_id = tenant.get("stripe_customer_id")
        if not customer_id:
            customer = await stripe_service.create_customer(
                email=tenant.get("email") or current_admin.get("email") or "",
                name=tenant.get("name") or current_admin.get("full_name") or "",
                tenant_id=tenant_id,
            )
            customer_id = customer["id"]
            # Saved before payment so invoice webhooks can find this business by customer id.
            await db.tenants.update_one({"_id": tenant["_id"]}, {"$set": {"stripe_customer_id": customer_id}})

        session = await stripe_service.create_checkout_session(
            customer_id=customer_id,
            tenant_id=tenant_id,
            mode=mode,
            amount_cents=amount_cents,
            metadata=metadata,
            success_url=_frontend_url("/dashboard/billing?paid=1"),
            cancel_url=_frontend_url("/dashboard/billing"),
        )
    except Exception as e:
        logger.error(f"Failed to create checkout session for tenant {tenant_id}: {e}")
        raise HTTPException(status_code=502, detail="Could not start the checkout. Please try again.")

    return {"checkout_url": session["url"]}


@router.post("/change-plan")
async def change_plan(body: ChangePlanRequest, current_admin: dict = Depends(get_current_admin)):
    """New usage level for an active monthly plan; the new price and minutes start at the next renewal."""
    if is_mock_mode():
        raise HTTPException(status_code=503, detail="Online payment is not set up yet")
    plan = _usage_quote(body.calls, body.avg_minutes)
    db = get_database()
    tenant_id = _current_tenant_id(current_admin)
    tenant = await db.tenants.find_one(usage_billing.tenant_query(tenant_id))
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    subscription_id = tenant.get("stripe_subscription_id")
    if not subscription_id or tenant.get("subscription_status") not in ACTIVE_SUBSCRIPTION_STATUSES:
        raise HTTPException(status_code=400, detail="You don't have an active monthly plan")

    try:
        await get_stripe_service().change_subscription_price(
            subscription_id, plan["price_usd"] * 100, {**_plan_metadata(plan), "tenant_id": tenant_id}
        )
    except Exception as e:
        logger.error(f"Failed to change plan for tenant {tenant_id}: {e}")
        raise HTTPException(status_code=502, detail="Could not change the plan. Please try again.")

    await db.tenants.update_one({"_id": tenant["_id"]}, {"$set": {"plan_next": plan, "updated_at": datetime.utcnow()}})
    return {"success": True, "next_plan": plan}


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription_status(current_user: dict = Depends(get_current_user)):
    """
    Get current subscription status
    """
    db = get_database()
    tenant_id = _current_tenant_id(current_user)
    tenant = await db.tenants.find_one(usage_billing.tenant_query(tenant_id))
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    subscription_id = tenant.get("stripe_subscription_id")
    if not subscription_id:
        raise HTTPException(status_code=404, detail="No active subscription")

    subscription = await get_stripe_service().get_subscription(subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    trial_end = subscription.get("trial_end")
    period_end = stripe_events.subscription_period_end(subscription)
    return SubscriptionResponse(
        status=subscription.get("status", "unknown"),
        plan_name=usage_billing.PLANS.get(tenant.get("billing_plan") or "", {}).get("name", "Monthly plan"),
        plan_price=_format_plan_price(_extract_plan_amount_cents(subscription), _extract_plan_interval(subscription)),
        trial_end=datetime.utcfromtimestamp(trial_end).isoformat() if trial_end else None,
        current_period_end=period_end.isoformat() if period_end else None,
        cancel_at_period_end=bool(subscription.get("cancel_at_period_end")),
        is_mock=is_mock_mode(),
    )


@router.post("/portal")
async def create_portal_session(current_admin: dict = Depends(get_current_admin)):
    """Stripe customer portal: change plan, update the card, cancel, download invoices."""
    if is_mock_mode():
        raise HTTPException(status_code=503, detail="Online payment is not set up yet")
    db = get_database()
    tenant_id = _current_tenant_id(current_admin)
    tenant = await db.tenants.find_one(usage_billing.tenant_query(tenant_id))
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    if not tenant.get("stripe_customer_id"):
        raise HTTPException(status_code=400, detail="No payments yet")

    try:
        session = await get_stripe_service().create_portal_session(
            customer_id=tenant["stripe_customer_id"],
            return_url=_frontend_url("/dashboard/billing"),
        )
    except Exception as e:
        logger.error(f"Failed to create portal session for tenant {tenant_id}: {e}")
        raise HTTPException(status_code=502, detail="Could not open the billing portal. Please try again.")
    return {"portal_url": session["url"]}


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

        tenant = await usage_billing.ensure_wallet(db, tenant)

        return {
            "wallet": usage_billing.wallet_summary(tenant),
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
    Stripe notifications (signature-checked). Paid invoices (first month, renewals) and paid
    one-time checkouts add the minutes recorded in their metadata when the checkout was created.
    """
    if is_mock_mode():
        # Mock events are unsigned JSON; accepting them would let anyone grant themselves minutes.
        raise HTTPException(status_code=404, detail="Not found")

    payload = await request.body()
    try:
        event = await get_stripe_service().construct_webhook_event(payload, request.headers.get("stripe-signature", ""))
    except Exception as e:
        logger.warning(f"Rejected Stripe webhook: {e}")
        raise HTTPException(status_code=400, detail="invalid_signature")

    db = get_database()
    event_type = event.get("type", "")
    obj = (event.get("data") or {}).get("object") or {}
    logger.info(f"💳 Stripe webhook received: {event_type} {obj.get('id')}")

    # Stripe retries until it gets a 2xx. A retry of an event that failed halfway is processed
    # again; adding minutes is idempotent per payment id, so nothing is counted twice.
    event_key = f"stripe:{event.get('id')}"
    seen = await db.payment_events.find_one({"_id": event_key})
    if seen and seen.get("status") in ("processed", "unmatched"):
        return {"success": True, "duplicate": True}
    if not seen:
        try:
            await db.payment_events.insert_one({
                "_id": event_key,
                "provider": "stripe",
                "type": event_type,
                "object_id": obj.get("id"),
                "status": "received",
                "created_at": datetime.utcnow(),
            })
        except DuplicateKeyError:
            pass

    handlers = {
        "checkout.session.completed": handle_checkout_completed,
        "invoice.paid": handle_invoice_paid,
        "customer.subscription.created": handle_subscription_updated,
        "customer.subscription.updated": handle_subscription_updated,
        "customer.subscription.deleted": handle_subscription_deleted,
    }
    handler = handlers.get(event_type)
    matched = await handler(obj, db) if handler else True
    await db.payment_events.update_one(
        {"_id": event_key}, {"$set": {"status": "processed" if matched else "unmatched"}}
    )
    return {"success": True}


async def _find_stripe_tenant(db, *, metadata: Optional[Dict[str, Any]] = None,
                              subscription_id: Optional[str] = None,
                              customer_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    tenant_id = (metadata or {}).get("tenant_id")
    if tenant_id:
        tenant = await db.tenants.find_one(usage_billing.tenant_query(str(tenant_id)))
        if tenant:
            return tenant
    if subscription_id:
        tenant = await db.tenants.find_one({"stripe_subscription_id": subscription_id})
        if tenant:
            return tenant
    if customer_id:
        return await db.tenants.find_one({"stripe_customer_id": customer_id})
    return None


def _metadata_int(metadata: Optional[Dict[str, Any]], key: str) -> Optional[int]:
    try:
        value = int(float((metadata or {}).get(key) or 0))
    except (TypeError, ValueError):
        return None
    return value if value > 0 else None


def _unmatched(kind: str, object_id: Optional[str]) -> bool:
    logger.error(f"Stripe {kind} {object_id}: no matching business; review payment_events")
    return False


async def handle_checkout_completed(session: Dict[str, Any], db) -> bool:
    """Link the subscription to the business; a paid one-time checkout adds its minutes here."""
    customer_id = stripe_events.object_id(session.get("customer"))
    subscription_id = stripe_events.object_id(session.get("subscription"))
    tenant = await _find_stripe_tenant(db, metadata=session.get("metadata"), customer_id=customer_id)
    if not tenant:
        return _unmatched("checkout", session.get("id"))

    links: Dict[str, Any] = {"updated_at": datetime.utcnow()}
    if customer_id:
        links["stripe_customer_id"] = customer_id
    if subscription_id:
        links["stripe_subscription_id"] = subscription_id
        links["subscription_status"] = "active"
        metadata = session.get("metadata") or {}
        if metadata.get("calls") and metadata.get("avg_minutes"):
            links.update(usage_billing.plan_fields(
                int(metadata["calls"]), float(metadata["avg_minutes"]), float(metadata.get("price_usd") or 0)
            ))
    await db.tenants.update_one({"_id": tenant["_id"]}, {"$set": links})

    # Subscriptions get their minutes from invoice.paid; one-time packs only come through here.
    if session.get("mode") == "payment" and session.get("payment_status") == "paid":
        minutes = _metadata_int(session.get("metadata"), "minutes")
        if minutes:
            amount = session.get("amount_total")
            await usage_billing.credit_minutes(
                db,
                str(tenant["_id"]),
                minutes,
                source="stripe",
                key=f"stripe:{session.get('id')}",
                amount_paid=round(amount / 100, 2) if isinstance(amount, (int, float)) else None,
                currency=(session.get("currency") or "usd").upper(),
                reference=session.get("id"),
                note="Minutes pack",
            )
        else:
            logger.error(f"Paid checkout {session.get('id')} has no minutes in its metadata")
    return True


async def handle_invoice_paid(invoice: Dict[str, Any], db) -> bool:
    """Each paid invoice (first month and every renewal) adds the plan's minutes."""
    subscription_id = stripe_events.invoice_subscription_id(invoice)
    customer_id = stripe_events.object_id(invoice.get("customer"))
    tenant = await _find_stripe_tenant(
        db, metadata=stripe_events.invoice_metadata(invoice),
        subscription_id=subscription_id, customer_id=customer_id,
    )
    if not tenant:
        return _unmatched("invoice", invoice.get("id"))

    # The subscription's metadata says which usage level this invoice pays for (it changes after Change plan).
    metadata = stripe_events.invoice_metadata(invoice)
    fields: Dict[str, Any] = {"subscription_status": "active", "updated_at": datetime.utcnow()}
    if subscription_id:
        fields["stripe_subscription_id"] = subscription_id
    if customer_id:
        fields["stripe_customer_id"] = customer_id
    if metadata.get("calls") and metadata.get("avg_minutes"):
        fields.update(usage_billing.plan_fields(
            int(metadata["calls"]), float(metadata["avg_minutes"]), float(metadata.get("price_usd") or 0)
        ))
        fields["plan_next"] = None
    await db.tenants.update_one({"_id": tenant["_id"]}, {"$set": fields})

    minutes = _metadata_int(metadata, "minutes") or tenant.get("plan_minutes")
    if not minutes:
        logger.error(f"Invoice {invoice.get('id')} paid but no plan minutes are known for tenant {tenant['_id']}")
        return True

    amount_paid = invoice.get("amount_paid")
    await usage_billing.credit_minutes(
        db,
        str(tenant["_id"]),
        minutes,
        source="stripe",
        key=f"stripe:{invoice.get('id')}",
        plan="monthly",
        amount_paid=round(amount_paid / 100, 2) if isinstance(amount_paid, (int, float)) else None,
        currency=(invoice.get("currency") or "usd").upper(),
        reference=invoice.get("id"),
        note="Monthly plan",
        period_end=stripe_events.invoice_period_end(invoice) or datetime.utcnow() + usage_billing.BILLING_PERIOD,
    )
    logger.info(f"Invoice {invoice.get('id')} paid for tenant {tenant['_id']}")
    return True


async def handle_subscription_updated(subscription: Dict[str, Any], db) -> bool:
    """Keep status, renewal date and cancel-at-period-end in sync."""
    tenant = await _find_stripe_tenant(
        db, metadata=subscription.get("metadata"),
        subscription_id=subscription.get("id"),
        customer_id=stripe_events.object_id(subscription.get("customer")),
    )
    if not tenant:
        return _unmatched("subscription", subscription.get("id"))

    fields: Dict[str, Any] = {
        "stripe_subscription_id": subscription.get("id"),
        "subscription_status": subscription.get("status"),
        "cancel_at_period_end": bool(subscription.get("cancel_at_period_end")),
        "updated_at": datetime.utcnow(),
    }
    period_end = stripe_events.subscription_period_end(subscription)
    if period_end:
        fields["billing_period_end"] = period_end
    amount_cents = _extract_plan_amount_cents(subscription)
    if amount_cents is not None:
        fields["monthly_subscription_amount_usd"] = round(amount_cents / 100, 2)
    await db.tenants.update_one({"_id": tenant["_id"]}, {"$set": fields})
    logger.info(f"Subscription {subscription.get('id')} updated: {subscription.get('status')}")
    return True


async def handle_subscription_deleted(subscription: Dict[str, Any], db) -> bool:
    """Cancelled: no more renewals. Minutes already bought stay usable."""
    tenant = await db.tenants.find_one({"stripe_subscription_id": subscription.get("id")})
    if tenant:
        await db.tenants.update_one(
            {"_id": tenant["_id"]},
            {"$set": {"subscription_status": "canceled", "updated_at": datetime.utcnow()}}
        )
        logger.info(f"Subscription {subscription.get('id')} canceled")
    return True


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

        duration_s = call.get("durationSeconds") or 0

        billed = await usage_billing.record_call_usage(
            db,
            tenant_id,
            call_id,
            assistant_id=assistant_id,
            duration_seconds=duration_s,
            vapi_cost_usd=call_cost,
            synced_from_vapi=True,
        )
        if not billed:
            continue

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


# ==================== MINUTES WALLET ====================

def _current_tenant_id(current_user: dict) -> str:
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="User has no tenant_id")
    return tenant_id


@router.get("/wallet")
async def get_wallet(current_user: dict = Depends(get_current_user)):
    """Minutes left, plan, this month's usage and how this business can buy more minutes."""
    db = get_database()
    tenant_id = _current_tenant_id(current_user)
    tenant = await db.tenants.find_one(usage_billing.tenant_query(tenant_id))
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant = await usage_billing.ensure_wallet(db, tenant)

    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    usage = await db.billing_ledger.aggregate([
        {"$match": {"tenant_id": tenant_id, "type": "call_debit", "created_at": {"$gte": month_start}}},
        {"$group": {"_id": None, "calls": {"$sum": 1}, "seconds": {"$sum": "$duration_seconds"}}},
    ]).to_list(length=1)
    month = usage[0] if usage else {}

    return {
        **usage_billing.wallet_summary(tenant),
        "this_month": {
            "calls": month.get("calls", 0),
            "minutes": usage_billing.minutes_for_seconds(month.get("seconds")),
        },
        "checkout": usage_billing.checkout_options(online_checkout_ready()),
        "has_subscription": bool(tenant.get("stripe_subscription_id"))
        and tenant.get("subscription_status") in ACTIVE_SUBSCRIPTION_STATUSES,
        "tenant_id": tenant_id,
    }


class FallbackNumberRequest(BaseModel):
    fallback_number: str = ""


@router.put("/fallback-number")
async def set_fallback_number(
    body: FallbackNumberRequest,
    current_admin: dict = Depends(get_current_admin),
):
    """The business owner's own number that takes calls while the AI is paused for lack of minutes."""
    db = get_database()
    tenant_id = _current_tenant_id(current_admin)
    try:
        number = usage_billing.normalize_fallback_number(body.fallback_number)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    tenant = await db.tenants.find_one_and_update(
        usage_billing.tenant_query(tenant_id),
        {"$set": {"billing_fallback_number": number, "updated_at": datetime.utcnow()}},
        return_document=ReturnDocument.AFTER,
    )
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    await usage_billing.apply_fallback_number(tenant)
    return usage_billing.wallet_summary(tenant)


@router.get("/history")
async def get_wallet_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    """Minutes added (payments, trial) and minutes used (calls), newest first."""
    db = get_database()
    tenant_id = _current_tenant_id(current_user)
    match = {"tenant_id": tenant_id, "type": {"$in": ["minutes_credit", "call_debit"]}}
    skip = (page - 1) * limit
    total = await db.billing_ledger.count_documents(match)
    rows = await (
        db.billing_ledger.find(match, {"_id": 0, "key": 0})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
        .to_list(length=limit)
    )

    entries = []
    for row in rows:
        is_credit = row.get("type") == "minutes_credit"
        minutes = row.get("minutes")
        if minutes is None:
            minutes = usage_billing.minutes_for_seconds(row.get("duration_seconds"))
        created_at = row.get("created_at")
        entries.append({
            "type": "credit" if is_credit else "call",
            "minutes": round(float(minutes or 0), 2) * (1 if is_credit else -1),
            "source": row.get("source") if is_credit else "call",
            "plan": row.get("plan"),
            "reference": row.get("reference"),
            "note": row.get("note"),
            "duration_seconds": row.get("duration_seconds"),
            "created_at": created_at.isoformat() if isinstance(created_at, datetime) else created_at,
        })

    return {"entries": entries, "page": page, "limit": limit, "total": total, "has_more": (skip + limit) < total}
