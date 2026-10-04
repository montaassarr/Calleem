"""
Usage billing: every business has its own prepaid wallet of call minutes.

- Payments (Stripe checkout, or a manual invoice recorded in the admin console)
  add minutes to one business's wallet.
- Every finished call takes its duration (billed per second) from the wallet of the business
  that owns the assistant, and from no one else's.
- With BILLING_ENFORCEMENT_ENABLED, a business at zero minutes has its phone number detached
  from its assistant (calls go to its fallback number, if it set one) until minutes are added,
  and its assistant's maximum call length is capped to the minutes it has left.

The Vapi balance itself is shared by all businesses; these wallets are what keep each
business's spending separate. The real Vapi cost of every call is still stored on the ledger
(amount_usd) so the admin console can show the margin.
"""

import logging
import math
import re
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from services.vapi_service import vapi_service
from utils.config import settings

logger = logging.getLogger(__name__)

# Usage-based pricing: the client picks calls per month and average call length, and the monthly
# price comes from the same model as the landing page calculator. The frontend copy lives in
# frontend_next/lib/pricing.ts; keep the numbers and the arithmetic identical in both.
PRICING: Dict[str, Any] = {
    "cost_per_minute": 0.082,  # voice cost per minute (Vapi + telephony)
    "cost_per_call": 0.10,  # fixed cost per call
    "infra_per_month": 30,  # hosting and overhead per business
    "margin": 0.40,  # target share of the price kept as profit
    "min_calls": 100,
    "max_calls": 4500,  # above this, "Talk to us" (enterprise)
    "min_avg_minutes": 1,
    "max_avg_minutes": 15,
}
TOPUP_PACKS = (100, 500)  # minutes
TYPICAL_CALL_MINUTES = 3

PLANS: Dict[str, Dict[str, Any]] = {
    "trial": {"name": "Free trial"},
    "monthly": {"name": "Monthly plan"},
    "custom": {"name": "Custom"},
}
BILLING_PERIOD = timedelta(days=30)


def quote(calls: int, avg_minutes: float) -> Dict[str, Any]:
    """Monthly price for a usage level; same steps as the landing page calculator."""
    p = PRICING
    variable_cost = calls * (p["cost_per_call"] + (avg_minutes * p["cost_per_minute"]))
    total_cost = variable_cost + p["infra_per_month"]
    margin = min(p["margin"], 0.95)
    raw_revenue = total_cost / (1 - margin)
    price = math.ceil(raw_revenue / 10) * 10 - 1
    floor_price = math.ceil((p["infra_per_month"] * 1.5) / 10) * 10 - 1
    price = max(price, floor_price)
    return {
        "calls": calls,
        "avg_minutes": avg_minutes,
        "minutes": int(round(calls * avg_minutes)),
        "price_usd": price,
    }


def validate_usage(calls: Any, avg_minutes: Any) -> Tuple[int, float]:
    """Raise ValueError unless the usage is something the self-serve plan covers."""
    try:
        calls = int(calls)
        avg_minutes = round(float(avg_minutes) * 2) / 2  # half-minute steps, like the slider
    except (TypeError, ValueError):
        raise ValueError("Choose calls per month and average call length")
    if not PRICING["min_calls"] <= calls <= PRICING["max_calls"]:
        raise ValueError(f"Self-serve plans cover {PRICING['min_calls']} to {PRICING['max_calls']:,} calls a month; talk to us for more")
    if not PRICING["min_avg_minutes"] <= avg_minutes <= PRICING["max_avg_minutes"]:
        raise ValueError("Average call length must be between 1 and 15 minutes")
    return calls, avg_minutes


def topup_price_per_minute() -> float:
    """Extra minutes cost what they would inside a plan of typical 3-minute calls, rounded up to the cent."""
    p = PRICING
    per_minute_cost = p["cost_per_minute"] + p["cost_per_call"] / TYPICAL_CALL_MINUTES
    return math.ceil(per_minute_cost / (1 - p["margin"]) * 100) / 100


def topup_quote(minutes: int) -> Dict[str, Any]:
    return {"minutes": minutes, "price_usd": round(minutes * topup_price_per_minute(), 2)}


def checkout_options(online_checkout: bool) -> Dict[str, Any]:
    """What the client billing page offers: Stripe checkout when it's live, otherwise a request form."""
    return {
        "provider": "stripe" if online_checkout else "invoice",
        "pricing": PRICING,
        "topups": [topup_quote(m) for m in TOPUP_PACKS],
        "topup_price_per_minute_usd": topup_price_per_minute(),
    }


def plan_fields(calls: int, avg_minutes: float, price_usd: float) -> Dict[str, Any]:
    """Tenant fields describing its monthly plan."""
    return {
        "billing_plan": "monthly",
        "plan_calls": calls,
        "plan_avg_minutes": avg_minutes,
        "plan_minutes": int(round(calls * avg_minutes)),
        "plan_price_usd": price_usd,
    }


E164_PATTERN = re.compile(r"^\+[1-9]\d{6,14}$")


def normalize_fallback_number(value: str) -> Optional[str]:
    """Return the number in E.164 form, None for an empty value; raise ValueError otherwise."""
    number = re.sub(r"[\s\-().]", "", value or "")
    if not number:
        return None
    if not E164_PATTERN.match(number):
        raise ValueError("Use international format, e.g. +14155550123")
    return number


def tenant_query(tenant_id: str) -> Dict[str, Any]:
    if ObjectId.is_valid(tenant_id):
        return {"_id": ObjectId(tenant_id)}
    return {"$or": [{"_id": tenant_id}, {"tenant_id": tenant_id}]}


def minutes_for_seconds(seconds: Any) -> float:
    try:
        value = float(seconds or 0)
    except (TypeError, ValueError):
        return 0.0
    return round(max(value, 0.0) / 60, 4)


def call_cap_seconds(balance_minutes: float) -> int:
    """Longest call a business can afford right now, kept within [MIN_CALL_SECONDS, MAX_CALL_SECONDS]."""
    affordable = int(max(balance_minutes, 0) * 60)
    return max(settings.MIN_CALL_SECONDS, min(settings.MAX_CALL_SECONDS, affordable))


def is_enforced(tenant: Dict[str, Any]) -> bool:
    return settings.BILLING_ENFORCEMENT_ENABLED and not tenant.get("billing_exempt")


def should_pause(tenant: Dict[str, Any]) -> bool:
    return is_enforced(tenant) and float(tenant.get("minutes_balance") or 0) <= 0


def wallet_summary(tenant: Dict[str, Any]) -> Dict[str, Any]:
    balance = float(tenant.get("minutes_balance") or 0)
    plan_id = tenant.get("billing_plan") or "trial"
    period_end = tenant.get("billing_period_end")
    return {
        "minutes_balance": round(balance, 1),
        "plan": plan_id,
        "plan_name": PLANS.get(plan_id, PLANS["custom"])["name"],
        "period_end": period_end.isoformat() if isinstance(period_end, datetime) else period_end,
        "calls_paused": bool(tenant.get("calls_paused")),
        "low_balance": balance <= settings.LOW_BALANCE_MINUTES,
        "enforcement_enabled": settings.BILLING_ENFORCEMENT_ENABLED,
        "billing_exempt": bool(tenant.get("billing_exempt")),
        "fallback_number": tenant.get("billing_fallback_number"),
        "plan_calls": tenant.get("plan_calls"),
        "plan_avg_minutes": tenant.get("plan_avg_minutes"),
        "plan_minutes": tenant.get("plan_minutes"),
        "plan_price_usd": tenant.get("plan_price_usd"),
        "plan_next": tenant.get("plan_next"),  # set by Change plan until the next renewal applies it
    }


async def sync_call_access(db, tenant: Dict[str, Any]) -> Dict[str, Any]:
    """
    Make the business's Vapi phone number and call-length cap match its wallet.
    Vapi failures are logged and retried on the next sync instead of failing the caller.
    Returns the fields that changed on the tenant.
    """
    changes: Dict[str, Any] = {}
    if not vapi_service.is_configured():
        return changes

    phone_config = tenant.get("phone_config") or {}
    phone_id = phone_config.get("vapi_phone_number_id") if phone_config.get("is_active") else None
    assistant_id = tenant.get("vapi_assistant_id")
    pause = should_pause(tenant)
    paused = bool(tenant.get("calls_paused"))

    try:
        if pause and not paused:
            if phone_id:
                fields: Dict[str, Any] = {"assistantId": None}
                fallback = tenant.get("billing_fallback_number")
                if fallback:
                    fields["fallbackDestination"] = {"type": "number", "number": fallback}
                await vapi_service.update_phone_number(phone_id, fields)
            changes.update(calls_paused=True, calls_paused_at=datetime.utcnow(), calls_paused_reason="no_minutes")
            logger.info(f"Paused calls for tenant {tenant.get('_id')}: no minutes left")
        elif paused and not pause:
            if phone_id and assistant_id:
                await vapi_service.update_phone_number(phone_id, {"assistantId": assistant_id})
            changes.update(calls_paused=False, calls_paused_reason=None)
            logger.info(f"Resumed calls for tenant {tenant.get('_id')}")

        if assistant_id and is_enforced(tenant):
            cap = call_cap_seconds(float(tenant.get("minutes_balance") or 0))
            if tenant.get("call_cap_seconds") != cap:
                await vapi_service.patch_assistant(assistant_id, {"maxDurationSeconds": cap})
                changes["call_cap_seconds"] = cap
    except Exception as e:
        logger.error(f"Could not sync call access for tenant {tenant.get('_id')}: {e}")

    if changes:
        await db.tenants.update_one({"_id": tenant["_id"]}, {"$set": changes})
    return changes


async def apply_fallback_number(tenant: Dict[str, Any]) -> None:
    """Push the business's fallback number to its Vapi phone number; it only rings while calls are paused."""
    phone_config = tenant.get("phone_config") or {}
    phone_id = phone_config.get("vapi_phone_number_id") if phone_config.get("is_active") else None
    if not phone_id or not vapi_service.is_configured():
        return
    fallback = tenant.get("billing_fallback_number")
    try:
        await vapi_service.update_phone_number(
            phone_id, {"fallbackDestination": {"type": "number", "number": fallback} if fallback else None}
        )
    except Exception as e:
        logger.error(f"Could not set fallback number for tenant {tenant.get('_id')}: {e}")


async def credit_minutes(
    db,
    tenant_id: str,
    minutes: float,
    *,
    source: str,
    key: str,
    plan: Optional[str] = None,
    amount_paid: Optional[float] = None,
    currency: str = "USD",
    reference: Optional[str] = None,
    note: Optional[str] = None,
    period_end: Optional[datetime] = None,
    sync: bool = True,
) -> Optional[Dict[str, Any]]:
    """
    Add minutes to one business, at most once per key (payment id, invoice reference...).
    Returns the updated tenant, or None if the tenant is unknown or the key was already used.
    """
    if minutes <= 0:
        raise ValueError("minutes must be positive")

    query = tenant_query(tenant_id)
    if not await db.tenants.find_one(query, {"_id": 1}):
        logger.error(f"Cannot credit minutes: tenant {tenant_id} not found")
        return None

    try:
        await db.billing_ledger.insert_one({
            "key": key,
            "type": "minutes_credit",
            "tenant_id": tenant_id,
            "minutes": round(minutes, 4),
            "source": source,
            "plan": plan,
            "amount_paid": amount_paid,
            "currency": currency,
            "reference": reference,
            "note": note,
            "created_at": datetime.utcnow(),
        })
    except DuplicateKeyError:
        logger.info(f"Minutes for {key} were already credited; skipping")
        return None

    set_fields: Dict[str, Any] = {"updated_at": datetime.utcnow()}
    if plan:
        set_fields["billing_plan"] = plan
    if period_end:
        set_fields["billing_period_end"] = period_end

    tenant = await db.tenants.find_one_and_update(
        query,
        {"$inc": {"minutes_balance": round(minutes, 4)}, "$set": set_fields},
        return_document=ReturnDocument.AFTER,
    )
    if tenant and sync:
        await sync_call_access(db, tenant)
    return tenant


async def ensure_wallet(db, tenant: Dict[str, Any]) -> Dict[str, Any]:
    """Give a business that never had a wallet its one-time free trial minutes."""
    if tenant.get("billing_plan"):
        return tenant

    tenant_id = str(tenant["_id"])
    if settings.TRIAL_MINUTES > 0:
        await credit_minutes(
            db, tenant_id, settings.TRIAL_MINUTES,
            source="trial", key=f"trial:{tenant_id}", plan="trial",
            note="Free trial minutes", sync=False,
        )
    await db.tenants.update_one(
        {"_id": tenant["_id"], "billing_plan": {"$exists": False}},
        {"$set": {"billing_plan": "trial"}},
    )
    return await db.tenants.find_one({"_id": tenant["_id"]}) or tenant


async def record_call_usage(
    db,
    tenant_id: str,
    call_id: str,
    *,
    assistant_id: Optional[str],
    duration_seconds: Any,
    vapi_cost_usd: float,
    synced_from_vapi: bool = False,
) -> Optional[Dict[str, Any]]:
    """Take one call's minutes from its business's wallet, once per call id."""
    minutes = minutes_for_seconds(duration_seconds)
    if minutes <= 0 and vapi_cost_usd <= 0:
        return None

    tenant = await db.tenants.find_one(tenant_query(tenant_id))
    if not tenant:
        logger.error(f"Call {call_id} belongs to unknown tenant {tenant_id}; not billed")
        return None
    tenant = await ensure_wallet(db, tenant)

    entry = {
        "key": f"call:{call_id}",
        "type": "call_debit",
        "tenant_id": tenant_id,
        "assistant_id": assistant_id,
        "vapi_call_id": call_id,
        "amount_usd": vapi_cost_usd,
        "duration_seconds": duration_seconds,
        "minutes": minutes,
        "created_at": datetime.utcnow(),
    }
    if synced_from_vapi:
        entry["synced_from_vapi"] = True
    try:
        await db.billing_ledger.insert_one(entry)
    except DuplicateKeyError:
        return None

    tenant = await db.tenants.find_one_and_update(
        {"_id": tenant["_id"]},
        {"$inc": {"minutes_balance": -minutes}, "$set": {"updated_at": datetime.utcnow()}},
        return_document=ReturnDocument.AFTER,
    )
    if tenant:
        await sync_call_access(db, tenant)
    return tenant
