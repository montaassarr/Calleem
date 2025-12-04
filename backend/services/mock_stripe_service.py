"""
Mock Stripe Service for Local Testing
Simulates Stripe API without real API calls or charges
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import secrets

logger = logging.getLogger(__name__)

# Mock mode flag - set to False to use real Stripe
MOCK_MODE = True

class MockStripeService:
    """
    Simulates Stripe API for local testing
    No real charges, instant success responses
    """
    
    def __init__(self):
        self.mock_customers = {}
        self.mock_subscriptions = {}
        self.mock_checkout_sessions = {}
        logger.info("🧪 MockStripeService initialized - NO REAL CHARGES WILL BE MADE")
    
    def create_product(self) -> Dict[str, Any]:
        """Create mock product"""
        return {
            "id": "prod_mock_ai_receptionist",
            "name": "AI Receptionist Pro",
            "description": "$499/month - All features included",
            "active": True
        }
    
    def create_price(self, product_id: str) -> Dict[str, Any]:
        """Create mock price"""
        return {
            "id": "price_mock_499_monthly",
            "product": product_id,
            "currency": "usd",
            "unit_amount": 49900,  # $499.00 in cents
            "recurring": {
                "interval": "month",
                "interval_count": 1,
                "trial_period_days": 14
            },
            "active": True
        }
    
    def create_customer(self, email: str, name: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create mock Stripe customer"""
        customer_id = f"cus_mock_{secrets.token_hex(8)}"
        
        customer = {
            "id": customer_id,
            "email": email,
            "name": name,
            "metadata": metadata or {},
            "created": int(datetime.utcnow().timestamp()),
            "balance": 0,
            "default_source": None
        }
        
        self.mock_customers[customer_id] = customer
        logger.info(f"🧪 Mock customer created: {customer_id} ({email})")
        
        return customer
    
    def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create mock checkout session - instant success"""
        session_id = f"cs_mock_{secrets.token_hex(12)}"
        
        session = {
            "id": session_id,
            "customer": customer_id,
            "payment_status": "unpaid",  # Will be "paid" after mock completion
            "status": "open",
            "mode": "subscription",
            "success_url": success_url,
            "cancel_url": cancel_url,
            "metadata": metadata or {},
            "url": f"http://localhost:3000/payment/mock-checkout?session_id={session_id}",  # Mock checkout URL
            "created": int(datetime.utcnow().timestamp()),
            "expires_at": int((datetime.utcnow() + timedelta(hours=24)).timestamp())
        }
        
        self.mock_checkout_sessions[session_id] = session
        logger.info(f"🧪 Mock checkout session created: {session_id}")
        
        return session
    
    def complete_checkout_session(self, session_id: str) -> Dict[str, Any]:
        """Simulate successful checkout completion"""
        if session_id not in self.mock_checkout_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.mock_checkout_sessions[session_id]
        subscription_id = f"sub_mock_{secrets.token_hex(8)}"
        
        # Create mock subscription
        trial_end = datetime.utcnow() + timedelta(days=14)
        current_period_end = datetime.utcnow() + timedelta(days=14)
        
        subscription = {
            "id": subscription_id,
            "customer": session["customer"],
            "status": "trialing",
            "trial_start": int(datetime.utcnow().timestamp()),
            "trial_end": int(trial_end.timestamp()),
            "current_period_start": int(datetime.utcnow().timestamp()),
            "current_period_end": int(current_period_end.timestamp()),
            "plan": {
                "id": "price_mock_499_monthly",
                "amount": 49900,
                "currency": "usd",
                "interval": "month"
            },
            "metadata": session.get("metadata", {}),
            "cancel_at_period_end": False,
            "created": int(datetime.utcnow().timestamp())
        }
        
        self.mock_subscriptions[subscription_id] = subscription
        
        # Update session
        session["payment_status"] = "paid"
        session["status"] = "complete"
        session["subscription"] = subscription_id
        
        logger.info(f"🧪 Mock checkout completed: {session_id} → subscription {subscription_id}")
        
        return {
            "session": session,
            "subscription": subscription
        }
    
    def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get mock subscription"""
        return self.mock_subscriptions.get(subscription_id)
    
    def create_portal_session(self, customer_id: str, return_url: str) -> Dict[str, Any]:
        """Create mock customer portal session"""
        session_id = f"bps_mock_{secrets.token_hex(12)}"
        
        session = {
            "id": session_id,
            "customer": customer_id,
            "return_url": return_url,
            "url": f"http://localhost:3000/payment/mock-portal?customer_id={customer_id}",  # Mock portal URL
            "created": int(datetime.utcnow().timestamp())
        }
        
        logger.info(f"🧪 Mock portal session created: {session_id}")
        
        return session
    
    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel mock subscription"""
        if subscription_id not in self.mock_subscriptions:
            raise ValueError(f"Subscription {subscription_id} not found")
        
        subscription = self.mock_subscriptions[subscription_id]
        subscription["status"] = "canceled"
        subscription["canceled_at"] = int(datetime.utcnow().timestamp())
        subscription["cancel_at_period_end"] = False
        
        logger.info(f"🧪 Mock subscription canceled: {subscription_id}")
        
        return subscription
    
    def simulate_trial_end(self, subscription_id: str) -> Dict[str, Any]:
        """Simulate trial ending and conversion to active"""
        if subscription_id not in self.mock_subscriptions:
            raise ValueError(f"Subscription {subscription_id} not found")
        
        subscription = self.mock_subscriptions[subscription_id]
        subscription["status"] = "active"
        subscription["trial_end"] = None
        
        logger.info(f"🧪 Mock trial ended, subscription active: {subscription_id}")
        
        return subscription
    
    def simulate_webhook_event(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate Stripe webhook event"""
        event_id = f"evt_mock_{secrets.token_hex(8)}"
        
        event = {
            "id": event_id,
            "type": event_type,
            "data": {
                "object": data
            },
            "created": int(datetime.utcnow().timestamp()),
            "livemode": False
        }
        
        logger.info(f"🧪 Mock webhook event: {event_type}")
        
        return event


# Global mock instance
_mock_service = MockStripeService()


def get_mock_service() -> MockStripeService:
    """Get the global mock Stripe service"""
    return _mock_service


def is_mock_mode() -> bool:
    """Check if running in mock mode"""
    return MOCK_MODE
