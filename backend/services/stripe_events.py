"""
Read the fields billing needs from Stripe webhook objects, whatever the account's API version.

Since API version 2025-03-31 ("basil") Stripe moved several fields:
- invoice.subscription        -> invoice.parent.subscription_details.subscription
- invoice line .price.id      -> line.pricing.price_details.price
- subscription.current_period_end -> subscription.items.data[].current_period_end
These helpers accept both shapes so a new Stripe account works as well as an old one.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


def object_id(value: Any) -> Optional[str]:
    """An id field may be a plain id or an expanded object."""
    if isinstance(value, dict):
        return value.get("id")
    return value or None


def _timestamp(value: Any) -> Optional[datetime]:
    try:
        return datetime.utcfromtimestamp(int(value)) if value else None
    except (TypeError, ValueError, OverflowError):
        return None


def invoice_subscription_id(invoice: Dict[str, Any]) -> Optional[str]:
    details = (invoice.get("parent") or {}).get("subscription_details") or {}
    return object_id(invoice.get("subscription")) or object_id(details.get("subscription"))


def invoice_metadata(invoice: Dict[str, Any]) -> Dict[str, Any]:
    details = (invoice.get("parent") or {}).get("subscription_details") or {}
    return details.get("metadata") or (invoice.get("subscription_details") or {}).get("metadata") or {}


def invoice_items(invoice: Dict[str, Any]) -> List[Tuple[Optional[str], Any]]:
    """(price_id, quantity) for every line of the invoice."""
    items = []
    for line in (invoice.get("lines") or {}).get("data") or []:
        price_id = object_id(line.get("price")) or (
            ((line.get("pricing") or {}).get("price_details") or {}).get("price")
        )
        items.append((object_id(price_id), line.get("quantity")))
    return items


def invoice_period_end(invoice: Dict[str, Any]) -> Optional[datetime]:
    ends = [
        (line.get("period") or {}).get("end")
        for line in (invoice.get("lines") or {}).get("data") or []
    ]
    return _timestamp(max((e for e in ends if e), default=None))


def subscription_period_end(subscription: Dict[str, Any]) -> Optional[datetime]:
    if subscription.get("current_period_end"):
        return _timestamp(subscription["current_period_end"])
    ends = [item.get("current_period_end") for item in (subscription.get("items") or {}).get("data") or []]
    return _timestamp(max((e for e in ends if e), default=None))


def subscription_amount_cents(subscription: Dict[str, Any]) -> Optional[int]:
    """Monthly amount of the subscription's first item, in cents."""
    plan = subscription.get("plan") or {}
    if isinstance(plan.get("amount"), (int, float)):
        return int(plan["amount"])
    for item in (subscription.get("items") or {}).get("data") or []:
        amount = (item.get("price") or {}).get("unit_amount")
        if isinstance(amount, (int, float)):
            return int(amount)
    return None
