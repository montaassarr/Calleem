"""
Stripe Service - Unified interface for real Stripe or mock testing
Set STRIPE_MOCK_MODE=true for local testing without real charges.

Live mode returns plain dicts: stripe-python 13+ objects are no longer dicts (no .get()).
How many minutes a payment buys travels in its metadata (see routers/billing.py).
"""

import json
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Check if we should use mock mode
MOCK_MODE = os.getenv("STRIPE_MOCK_MODE", "true").lower() == "true"

# Import dependencies based on mode
get_mock_service = None
stripe = None

if MOCK_MODE:
    logger.info("🧪 STRIPE MOCK MODE ENABLED - No real charges will be made")
    from services.mock_stripe_service import get_mock_service  # type: ignore
else:
    logger.info("💳 STRIPE LIVE MODE - Real API calls will be made")
    import stripe  # type: ignore
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")  # type: ignore
    if not stripe.api_key:  # type: ignore
        raise ValueError("STRIPE_SECRET_KEY environment variable is required when MOCK_MODE is disabled")


def _plain(obj: Any) -> Dict[str, Any]:
    return obj if isinstance(obj, dict) else obj.to_dict()


# Prices are computed per business (usage-based), so checkouts use inline price_data on these products.
PLAN_PRODUCT_ID = "calleem_monthly_plan"
MINUTES_PRODUCT_ID = "calleem_extra_minutes"


class StripeService:
    """
    Unified Stripe service that works in both mock and live mode
    """

    def __init__(self):
        self.mock_mode = MOCK_MODE
        self._products: set = set()
        if self.mock_mode:
            self.mock = get_mock_service()  # type: ignore

    async def create_customer(
        self,
        email: str,
        name: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Create a Stripe customer, tagged with the tenant it belongs to."""
        metadata = {"tenant_id": tenant_id}

        if self.mock_mode:
            customer = self.mock.create_customer(email, name, metadata)
        else:
            customer = _plain(stripe.Customer.create(  # type: ignore
                email=email,
                name=name,
                metadata=metadata
            ))

        logger.info(f"Created customer {customer['id']} for tenant {tenant_id}")
        return customer

    def _ensure_product(self, product_id: str, name: str) -> str:
        """Products have fixed ids, so they're created once per Stripe account and reused."""
        if product_id not in self._products:
            try:
                stripe.Product.retrieve(product_id)  # type: ignore
            except stripe.InvalidRequestError:  # type: ignore
                stripe.Product.create(id=product_id, name=name)  # type: ignore
            self._products.add(product_id)
        return product_id

    def _monthly_price_data(self, amount_cents: int) -> Dict[str, Any]:
        return {
            "currency": "usd",
            "product": self._ensure_product(PLAN_PRODUCT_ID, "Calleem AI receptionist - monthly plan"),
            "unit_amount": amount_cents,
            "recurring": {"interval": "month"},
        }

    async def create_checkout_session(
        self,
        customer_id: str,
        tenant_id: str,
        mode: str,
        amount_cents: int,
        metadata: Dict[str, str],
        success_url: str,
        cancel_url: str
    ) -> Dict[str, Any]:
        """
        Hosted Stripe Checkout with a price computed for this business: mode "subscription" for its
        monthly plan, "payment" for a one-time minutes pack. metadata (tenant_id, minutes...) is copied
        to the subscription or payment, so every renewal invoice says how many minutes it buys.
        """
        metadata = {**metadata, "tenant_id": tenant_id}

        if self.mock_mode:
            session = self.mock.create_checkout_session(
                customer_id=customer_id,
                price_id=f"price_mock_{amount_cents}",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata
            )
        else:
            if mode == "subscription":
                price_data = self._monthly_price_data(amount_cents)
                extra: Dict[str, Any] = {"subscription_data": {"metadata": metadata}}
            else:
                price_data = {
                    "currency": "usd",
                    "product": self._ensure_product(MINUTES_PRODUCT_ID, "Calleem extra call minutes"),
                    "unit_amount": amount_cents,
                }
                extra = {"payment_intent_data": {"metadata": metadata}}
            session = _plain(stripe.checkout.Session.create(  # type: ignore
                customer=customer_id,
                mode=mode,
                line_items=[{"price_data": price_data, "quantity": 1}],
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata,
                **extra
            ))

        logger.info(f"Created checkout session {session['id']} for tenant {tenant_id}")
        return session

    async def change_subscription_price(
        self,
        subscription_id: str,
        amount_cents: int,
        metadata: Dict[str, str]
    ) -> Dict[str, Any]:
        """New monthly price and minutes from the next renewal; no proration, nothing charged now."""
        if self.mock_mode:
            raise ValueError("change_subscription_price needs live Stripe")
        subscription = _plain(stripe.Subscription.retrieve(subscription_id))  # type: ignore
        item_id = subscription["items"]["data"][0]["id"]
        return _plain(stripe.Subscription.modify(  # type: ignore
            subscription_id,
            items=[{"id": item_id, "price_data": self._monthly_price_data(amount_cents)}],
            proration_behavior="none",
            metadata=metadata,
        ))

    async def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get subscription details"""
        if self.mock_mode:
            return self.mock.get_subscription(subscription_id)
        try:
            return _plain(stripe.Subscription.retrieve(subscription_id))  # type: ignore
        except stripe.StripeError as e:  # type: ignore
            logger.error(f"Failed to retrieve subscription {subscription_id}: {e}")
            return None

    async def create_portal_session(
        self,
        customer_id: str,
        return_url: str
    ) -> Dict[str, Any]:
        """Customer portal: change plan, update card, cancel, download invoices."""
        if self.mock_mode:
            session = self.mock.create_portal_session(customer_id, return_url)
        else:
            session = _plain(stripe.billing_portal.Session.create(  # type: ignore
                customer=customer_id,
                return_url=return_url
            ))

        logger.info(f"Created portal session for customer {customer_id}")
        return session

    async def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a subscription"""
        if self.mock_mode:
            return self.mock.cancel_subscription(subscription_id)
        return _plain(stripe.Subscription.cancel(subscription_id))  # type: ignore

    async def construct_webhook_event(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """
        Verify the Stripe-Signature header, then return the event as plain JSON.
        Mock mode never reaches here: the webhook route refuses unsigned events.
        """
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        if not webhook_secret:
            raise ValueError("STRIPE_WEBHOOK_SECRET is required for live mode")

        stripe.Webhook.construct_event(payload, sig_header, webhook_secret)  # type: ignore  # raises if invalid
        return json.loads(payload)


# Global service instance
_stripe_service = StripeService()


def get_stripe_service() -> StripeService:
    """Get the global Stripe service instance"""
    return _stripe_service


def is_mock_mode() -> bool:
    """Check if running in mock mode"""
    return MOCK_MODE
