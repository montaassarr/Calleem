"""
Stripe Service - Unified interface for real Stripe or mock testing
Set MOCK_MODE=True for local testing without real charges
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

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


class StripeService:
    """
    Unified Stripe service that works in both mock and live mode
    """
    
    def __init__(self):
        self.mock_mode = MOCK_MODE
        if self.mock_mode:
            self.mock = get_mock_service()  # type: ignore
        
        # Product and price IDs (create these once in Stripe dashboard for production)
        self.product_id = os.getenv("STRIPE_PRODUCT_ID", "prod_mock_ai_receptionist")
        self.price_id = os.getenv("STRIPE_PRICE_ID", "price_mock_499_monthly")
    
    async def ensure_product_and_price(self) -> tuple[str, str]:
        """
        Ensure product and price exist (for mock mode, creates them automatically)
        For live mode, these should be created in Stripe dashboard
        """
        if self.mock_mode:
            product = self.mock.create_product()
            price = self.mock.create_price(product["id"])
            return product["id"], price["id"]
        else:
            # In live mode, assume product/price already exist
            return self.product_id, self.price_id
    
    async def create_customer(
        self,
        email: str,
        name: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Create a Stripe customer
        
        Args:
            email: Customer email
            name: Customer name
            tenant_id: Tenant ID to store in metadata
            
        Returns:
            Customer object with 'id' field
        """
        metadata = {"tenant_id": tenant_id}
        
        if self.mock_mode:
            customer = self.mock.create_customer(email, name, metadata)
        else:
            customer = stripe.Customer.create(  # type: ignore
                email=email,
                name=name,
                metadata=metadata
            )
        
        logger.info(f"Created customer {customer['id']} for tenant {tenant_id}")
        return customer
    
    async def create_checkout_session(
        self,
        customer_id: str,
        tenant_id: str,
        success_url: str,
        cancel_url: str
    ) -> Dict[str, Any]:
        """
        Create a checkout session for subscription
        
        Args:
            customer_id: Stripe customer ID
            tenant_id: Tenant ID
            success_url: URL to redirect on success
            cancel_url: URL to redirect on cancel
            
        Returns:
            Checkout session with 'url' field
        """
        _, price_id = await self.ensure_product_and_price()
        
        metadata = {"tenant_id": tenant_id}
        
        if self.mock_mode:
            session = self.mock.create_checkout_session(
                customer_id=customer_id,
                price_id=price_id,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata
            )
        else:
            session = stripe.checkout.Session.create(  # type: ignore
                customer=customer_id,
                mode="subscription",
                payment_method_types=["card"],
                line_items=[{
                    "price": price_id,
                    "quantity": 1
                }],
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata,
                subscription_data={
                    "trial_period_days": 14,
                    "metadata": metadata
                }
            )
        
        logger.info(f"Created checkout session {session['id']} for tenant {tenant_id}")
        return session
    
    async def complete_checkout(self, session_id: str) -> Dict[str, Any]:
        """
        Complete checkout (mock mode only - simulates successful payment)
        In live mode, this happens automatically via Stripe
        """
        if not self.mock_mode:
            raise ValueError("complete_checkout is only for mock mode")
        
        result = self.mock.complete_checkout_session(session_id)
        logger.info(f"🧪 Mock checkout completed: {session_id}")
        return result
    
    async def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get subscription details"""
        if self.mock_mode:
            return self.mock.get_subscription(subscription_id)
        else:
            try:
                return stripe.Subscription.retrieve(subscription_id)  # type: ignore
            except stripe.error.StripeError as e:  # type: ignore
                logger.error(f"Failed to retrieve subscription {subscription_id}: {e}")
                return None
    
    async def create_portal_session(
        self,
        customer_id: str,
        return_url: str
    ) -> Dict[str, Any]:
        """
        Create customer portal session for managing subscription
        """
        if self.mock_mode:
            session = self.mock.create_portal_session(customer_id, return_url)
        else:
            session = stripe.billing_portal.Session.create(  # type: ignore
                customer=customer_id,
                return_url=return_url
            )
        
        logger.info(f"Created portal session for customer {customer_id}")
        return session
    
    async def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a subscription"""
        if self.mock_mode:
            return self.mock.cancel_subscription(subscription_id)
        else:
            return stripe.Subscription.delete(subscription_id)  # type: ignore
    
    async def construct_webhook_event(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """
        Construct and verify webhook event
        In mock mode, simulates webhook events
        """
        if self.mock_mode:
            # In mock mode, just parse the JSON payload
            import json
            return json.loads(payload)
        else:
            webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
            if not webhook_secret:
                raise ValueError("STRIPE_WEBHOOK_SECRET is required for live mode")
            
            return stripe.Webhook.construct_event(  # type: ignore
                payload, sig_header, webhook_secret
            )


# Global service instance
_stripe_service = StripeService()


def get_stripe_service() -> StripeService:
    """Get the global Stripe service instance"""
    return _stripe_service


def is_mock_mode() -> bool:
    """Check if running in mock mode"""
    return MOCK_MODE
