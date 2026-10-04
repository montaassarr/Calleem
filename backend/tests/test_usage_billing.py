"""
Tests for the per-business minutes wallet (services/usage_billing.py).

Uses a small in-memory stand-in for the Mongo collections and a fake Vapi client, so
nothing here touches a real database or the real Vapi account.
"""

import copy
import hashlib
import hmac
import json
import os
import sys
from unittest.mock import AsyncMock, MagicMock

import pytest
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import stripe_events, usage_billing  # noqa: E402


# ---------- in-memory Mongo stand-in ----------

def _matches(doc, query):
    for field, expected in query.items():
        if field == "$or":
            if not any(_matches(doc, sub) for sub in expected):
                return False
        elif isinstance(expected, dict) and "$exists" in expected:
            if (field in doc) != expected["$exists"]:
                return False
        elif doc.get(field) != expected:
            return False
    return True


def _apply(doc, update):
    for field, amount in update.get("$inc", {}).items():
        doc[field] = (doc.get(field) or 0) + amount
    for field, value in update.get("$set", {}).items():
        doc[field] = value


class FakeCollection:
    def __init__(self, unique_key=None):
        self.docs = []
        self.unique_key = unique_key

    async def find_one(self, query, projection=None):
        for doc in self.docs:
            if _matches(doc, query):
                return copy.deepcopy(doc)
        return None

    async def insert_one(self, doc):
        key = self.unique_key
        if key and doc.get(key) is not None and any(d.get(key) == doc[key] for d in self.docs):
            raise DuplicateKeyError("duplicate key")
        self.docs.append(copy.deepcopy(doc))

    async def update_one(self, query, update):
        for doc in self.docs:
            if _matches(doc, query):
                _apply(doc, update)
                return

    async def find_one_and_update(self, query, update, return_document=None):
        for doc in self.docs:
            if _matches(doc, query):
                _apply(doc, update)
                return copy.deepcopy(doc)
        return None


class FakeDB:
    def __init__(self):
        self.tenants = FakeCollection()
        self.billing_ledger = FakeCollection(unique_key="key")


@pytest.fixture
def db():
    return FakeDB()


@pytest.fixture
def vapi(monkeypatch):
    fake = MagicMock()
    fake.is_configured.return_value = True
    fake.update_phone_number = AsyncMock(return_value={})
    fake.patch_assistant = AsyncMock(return_value={})
    monkeypatch.setattr(usage_billing, "vapi_service", fake)
    return fake


@pytest.fixture
def enforcement(monkeypatch):
    monkeypatch.setattr(usage_billing.settings, "BILLING_ENFORCEMENT_ENABLED", True)
    monkeypatch.setattr(usage_billing.settings, "TRIAL_MINUTES", 30)
    monkeypatch.setattr(usage_billing.settings, "MAX_CALL_SECONDS", 600)
    monkeypatch.setattr(usage_billing.settings, "MIN_CALL_SECONDS", 60)


async def _add_tenant(db, **fields):
    tenant = {
        "_id": ObjectId(),
        "name": "Joe's Plumbing",
        "vapi_assistant_id": "asst_joe",
        "phone_config": {"is_active": True, "vapi_phone_number_id": "pn_joe"},
        **fields,
    }
    await db.tenants.insert_one(tenant)
    return str(tenant["_id"])


async def _tenant(db, tenant_id):
    return await db.tenants.find_one({"_id": ObjectId(tenant_id)})


# ---------- pure helpers ----------

class TestHelpers:
    def test_minutes_billed_per_second(self):
        assert usage_billing.minutes_for_seconds(90) == 1.5
        assert usage_billing.minutes_for_seconds(None) == 0
        assert usage_billing.minutes_for_seconds("bad") == 0
        assert usage_billing.minutes_for_seconds(-5) == 0

    def test_call_cap_stays_within_limits(self, enforcement):
        assert usage_billing.call_cap_seconds(100) == 600  # plenty left: normal 10 min cap
        assert usage_billing.call_cap_seconds(3) == 180  # 3 minutes left: call can't run longer
        assert usage_billing.call_cap_seconds(0.2) == 60  # never below one minute
        assert usage_billing.call_cap_seconds(-4) == 60

    def test_should_pause_only_when_enforced_and_empty(self, monkeypatch):
        monkeypatch.setattr(usage_billing.settings, "BILLING_ENFORCEMENT_ENABLED", False)
        assert not usage_billing.should_pause({"minutes_balance": 0})
        monkeypatch.setattr(usage_billing.settings, "BILLING_ENFORCEMENT_ENABLED", True)
        assert usage_billing.should_pause({"minutes_balance": 0})
        assert usage_billing.should_pause({"minutes_balance": -1.5})
        assert not usage_billing.should_pause({"minutes_balance": 0.5})
        assert not usage_billing.should_pause({"minutes_balance": 0, "billing_exempt": True})

    # Expected prices come from the landing page calculator (components/landing/Pricing.tsx).
    @pytest.mark.parametrize("calls, avg_minutes, price", [
        (100, 1, 89), (100, 3, 109), (200, 2.5, 159), (300, 3, 229), (500, 3, 339),
        (1000, 5, 899), (2500, 4.5, 2009), (4500, 15, 10029), (1700, 7.5, 2079),
    ])
    def test_quote_matches_landing_page(self, calls, avg_minutes, price):
        q = usage_billing.quote(calls, avg_minutes)
        assert q["price_usd"] == price
        assert q["minutes"] == round(calls * avg_minutes)

    def test_quote_keeps_target_margin(self):
        q = usage_billing.quote(500, 3)
        cost = 500 * (0.10 + 3 * 0.082) + 30
        assert (q["price_usd"] - cost) / q["price_usd"] >= 0.40

    def test_validate_usage(self):
        assert usage_billing.validate_usage("500", "3.2") == (500, 3.0)
        for calls, avg in ((50, 3), (5000, 3), (500, 0.5), (500, 20), ("x", 3)):
            with pytest.raises(ValueError):
                usage_billing.validate_usage(calls, avg)

    def test_topups_priced_like_plan_minutes(self):
        assert usage_billing.topup_price_per_minute() == 0.20
        assert usage_billing.topup_quote(500) == {"minutes": 500, "price_usd": 100.0}

    def test_checkout_is_a_request_until_stripe_is_live(self):
        assert usage_billing.checkout_options(False)["provider"] == "invoice"
        live = usage_billing.checkout_options(True)
        assert live["provider"] == "stripe"
        assert [t["minutes"] for t in live["topups"]] == [100, 500]
        assert live["pricing"]["margin"] == 0.40


# ---------- Stripe event shapes (old API and 2025-03-31+ API) ----------

class TestStripeEvents:
    OLD_INVOICE = {
        "id": "in_old", "customer": "cus_1", "subscription": "sub_1",
        "lines": {"data": [{"price": {"id": "price_starter"}, "quantity": 1, "period": {"end": 1793750400}}]},
    }
    NEW_INVOICE = {
        "id": "in_new", "customer": "cus_1",
        "parent": {"type": "subscription_details", "subscription_details": {
            "subscription": "sub_1", "metadata": {"tenant_id": "t1", "price_id": "price_starter"}}},
        "lines": {"data": [{
            "pricing": {"type": "price_details", "price_details": {"price": "price_starter", "product": "prod_1"}},
            "quantity": 1, "period": {"end": 1793750400},
        }]},
    }

    def test_invoice_subscription_id_both_shapes(self):
        assert stripe_events.invoice_subscription_id(self.OLD_INVOICE) == "sub_1"
        assert stripe_events.invoice_subscription_id(self.NEW_INVOICE) == "sub_1"

    def test_invoice_items_both_shapes(self):
        assert stripe_events.invoice_items(self.OLD_INVOICE) == [("price_starter", 1)]
        assert stripe_events.invoice_items(self.NEW_INVOICE) == [("price_starter", 1)]

    def test_plan_minutes_reach_renewal_invoices(self):
        new = {"parent": {"subscription_details": {"metadata": {"minutes": "1500"}}}}
        old = {"subscription_details": {"metadata": {"minutes": "1500"}}}
        assert stripe_events.invoice_metadata(new)["minutes"] == "1500"
        assert stripe_events.invoice_metadata(old)["minutes"] == "1500"

    def test_invoice_metadata_and_period(self):
        assert stripe_events.invoice_metadata(self.NEW_INVOICE)["tenant_id"] == "t1"
        assert stripe_events.invoice_period_end(self.NEW_INVOICE).year == 2026

    def test_subscription_period_end_both_shapes(self):
        old = {"current_period_end": 1793750400}
        new = {"items": {"data": [{"current_period_end": 1793750400}]}}
        assert stripe_events.subscription_period_end(old) == stripe_events.subscription_period_end(new)
        assert stripe_events.subscription_period_end({}) is None

    def test_expanded_ids(self):
        assert stripe_events.object_id({"id": "cus_9"}) == "cus_9"
        assert stripe_events.object_id("cus_9") == "cus_9"
        assert stripe_events.object_id(None) is None


# ---------- wallet flows ----------

class TestWallet:
    @pytest.mark.asyncio
    async def test_trial_granted_once(self, db, vapi, enforcement):
        tenant_id = await _add_tenant(db)
        tenant = await usage_billing.ensure_wallet(db, await _tenant(db, tenant_id))
        assert tenant["minutes_balance"] == 30
        assert tenant["billing_plan"] == "trial"

        tenant = await usage_billing.ensure_wallet(db, tenant)
        assert tenant["minutes_balance"] == 30

    @pytest.mark.asyncio
    async def test_call_debits_only_its_own_business(self, db, vapi, enforcement):
        joe = await _add_tenant(db, billing_plan="starter", minutes_balance=100)
        ann = await _add_tenant(db, name="Ann Law", vapi_assistant_id="asst_ann",
                                phone_config={"is_active": True, "vapi_phone_number_id": "pn_ann"},
                                billing_plan="pro", minutes_balance=500)

        await usage_billing.record_call_usage(db, joe, "call_1", assistant_id="asst_joe",
                                              duration_seconds=180, vapi_cost_usd=0.42)

        assert (await _tenant(db, joe))["minutes_balance"] == 97
        assert (await _tenant(db, ann))["minutes_balance"] == 500
        entry = await db.billing_ledger.find_one({"key": "call:call_1"})
        assert entry["minutes"] == 3 and entry["amount_usd"] == 0.42 and entry["tenant_id"] == joe

    @pytest.mark.asyncio
    async def test_same_call_is_billed_once(self, db, vapi, enforcement):
        joe = await _add_tenant(db, billing_plan="starter", minutes_balance=100)
        for _ in range(3):
            await usage_billing.record_call_usage(db, joe, "call_1", assistant_id="asst_joe",
                                                  duration_seconds=60, vapi_cost_usd=0.1)
        assert (await _tenant(db, joe))["minutes_balance"] == 99

    @pytest.mark.asyncio
    async def test_running_out_pauses_and_payment_resumes(self, db, vapi, enforcement):
        joe = await _add_tenant(db, billing_plan="starter", minutes_balance=2,
                                billing_fallback_number="+14155550123")

        await usage_billing.record_call_usage(db, joe, "call_1", assistant_id="asst_joe",
                                              duration_seconds=150, vapi_cost_usd=0.3)
        tenant = await _tenant(db, joe)
        assert tenant["calls_paused"] is True
        vapi.update_phone_number.assert_any_await("pn_joe", {
            "assistantId": None,
            "fallbackDestination": {"type": "number", "number": "+14155550123"},
        })

        vapi.update_phone_number.reset_mock()
        await usage_billing.credit_minutes(db, joe, 300, source="manual", key="manual:inv-001", plan="starter")
        tenant = await _tenant(db, joe)
        assert tenant["calls_paused"] is False
        assert tenant["minutes_balance"] == pytest.approx(299.5)
        vapi.update_phone_number.assert_awaited_once_with("pn_joe", {"assistantId": "asst_joe"})
        vapi.patch_assistant.assert_awaited_with("asst_joe", {"maxDurationSeconds": 600})

    @pytest.mark.asyncio
    async def test_low_balance_caps_call_length(self, db, vapi, enforcement):
        joe = await _add_tenant(db, billing_plan="starter", minutes_balance=10)
        await usage_billing.record_call_usage(db, joe, "call_1", assistant_id="asst_joe",
                                              duration_seconds=420, vapi_cost_usd=0.9)
        vapi.patch_assistant.assert_awaited_once_with("asst_joe", {"maxDurationSeconds": 180})
        assert (await _tenant(db, joe))["call_cap_seconds"] == 180

    @pytest.mark.asyncio
    async def test_enforcement_off_never_touches_vapi(self, db, vapi, monkeypatch):
        monkeypatch.setattr(usage_billing.settings, "BILLING_ENFORCEMENT_ENABLED", False)
        joe = await _add_tenant(db, billing_plan="starter", minutes_balance=1)
        await usage_billing.record_call_usage(db, joe, "call_1", assistant_id="asst_joe",
                                              duration_seconds=600, vapi_cost_usd=1.2)
        tenant = await _tenant(db, joe)
        assert tenant["minutes_balance"] == -9
        assert not tenant.get("calls_paused")
        vapi.update_phone_number.assert_not_awaited()
        vapi.patch_assistant.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_exempt_business_is_never_paused(self, db, vapi, enforcement):
        demo = await _add_tenant(db, billing_plan="custom", minutes_balance=0, billing_exempt=True)
        await usage_billing.record_call_usage(db, demo, "call_1", assistant_id="asst_joe",
                                              duration_seconds=120, vapi_cost_usd=0.2)
        assert not (await _tenant(db, demo)).get("calls_paused")
        vapi.update_phone_number.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_vapi_failure_does_not_break_billing(self, db, vapi, enforcement):
        vapi.update_phone_number.side_effect = RuntimeError("vapi down")
        joe = await _add_tenant(db, billing_plan="starter", minutes_balance=1)
        await usage_billing.record_call_usage(db, joe, "call_1", assistant_id="asst_joe",
                                              duration_seconds=120, vapi_cost_usd=0.2)
        tenant = await _tenant(db, joe)
        assert tenant["minutes_balance"] == -1
        assert not tenant.get("calls_paused")  # retried on the next sync

    @pytest.mark.asyncio
    async def test_payment_reference_recorded_once(self, db, vapi, enforcement):
        joe = await _add_tenant(db, billing_plan="trial", minutes_balance=0)
        first = await usage_billing.credit_minutes(db, joe, 300, source="manual", key="manual:inv-7")
        second = await usage_billing.credit_minutes(db, joe, 300, source="manual", key="manual:inv-7")
        assert first is not None and second is None
        assert (await _tenant(db, joe))["minutes_balance"] == 300
