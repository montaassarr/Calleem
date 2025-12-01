"""
Billing Router - Subscription management with Stripe (Mock Mode for Testing)
Handles checkout, webhooks, portal, and subscription status
"""

from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.responses import JSONResponse
from typing import Dict, Any
from datetime import datetime
import logging

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
        tenant = await db.tenants.find_one({"_id": tenant_id})
        if tenant and tenant.get("stripe_subscription_id"):
            raise HTTPException(
                status_code=400,
                detail="You already have an active subscription"
            )
        
        # Get or create Stripe customer
        stripe_customer_id = tenant.get("stripe_customer_id") if tenant else None
        
        if not stripe_customer_id:
            # Create new customer
            customer = await stripe_service.create_customer(
                email=current_user.get("email"),
                name=current_user.get("full_name", ""),
                tenant_id=tenant_id
            )
            stripe_customer_id = customer["id"]
            
            # Save customer ID to tenant
            await db.tenants.update_one(
                {"_id": tenant_id},
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
        
        tenant = await db.tenants.find_one({"_id": tenant_id})
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
        
        return SubscriptionResponse(
            status=subscription["status"],
            plan_name="AI Receptionist Pro",
            plan_price="$499/month",
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
        
        tenant = await db.tenants.find_one({"_id": tenant_id})
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
        await db.tenants.update_one(
            {"_id": tenant["_id"]},
            {
                "$set": {
                    "subscription_status": "active",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        logger.info(f"Invoice paid for subscription {subscription_id}")


async def handle_subscription_updated(subscription: Dict[str, Any], db):
    """Handle subscription updates"""
    subscription_id = subscription["id"]
    
    tenant = await db.tenants.find_one({"stripe_subscription_id": subscription_id})
    if tenant:
        await db.tenants.update_one(
            {"_id": tenant["_id"]},
            {
                "$set": {
                    "subscription_status": subscription["status"],
                    "current_period_end": datetime.fromtimestamp(subscription["current_period_end"]),
                    "cancel_at_period_end": subscription.get("cancel_at_period_end", False),
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
