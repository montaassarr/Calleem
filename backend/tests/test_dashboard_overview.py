"""
Tests for the dashboard overview (routers/appointments.get_dashboard_overview): revenue booked
this month from service prices, and bookings per day / week / month.
"""

import os
import sys
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytz
from bson import ObjectId

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database.mongo_config as mongo_config  # noqa: E402
from routers import appointments  # noqa: E402

TENANT_ID = "64b000000000000000000001"
TZ = pytz.timezone("America/New_York")


class _Cursor:
    def __init__(self, docs):
        self.docs = docs

    async def to_list(self, length=None):
        return self.docs


def _utc(local: datetime) -> datetime:
    """Mongo hands back naive UTC datetimes."""
    return TZ.localize(local).astimezone(pytz.utc).replace(tzinfo=None)


@pytest.fixture
def overview(monkeypatch):
    def run(appointment_docs, services):
        db = MagicMock()
        db.services.find = MagicMock(return_value=_Cursor(services))
        db.business_config.find_one = AsyncMock(return_value={"currency": "USD"})
        db.appointments.find = MagicMock(return_value=_Cursor(appointment_docs))
        monkeypatch.setattr(mongo_config, "get_database", lambda: db)
        monkeypatch.setattr(appointments.appointments_service, "_resolve_tenant_timezone", AsyncMock(return_value=TZ))
        return appointments.get_dashboard_overview({"tenant_id": TENANT_ID})
    return run


@pytest.mark.asyncio
async def test_revenue_uses_service_prices_and_compares_with_last_month(overview):
    haircut_id = ObjectId()
    services = [{"_id": haircut_id, "name": "Haircut", "price": 25}, {"_id": ObjectId(), "name": "Beard Trim", "price": 15}]
    now = datetime.now(TZ).replace(tzinfo=None)
    first_of_month = now.replace(day=1, hour=10, minute=0, second=0, microsecond=0)
    last_month = first_of_month - timedelta(days=3)
    docs = [
        {"datetime": _utc(first_of_month), "service": "anything", "service_id": str(haircut_id)},  # by id: 25
        {"datetime": _utc(first_of_month), "service": " beard trim "},  # by name, any case: 15
        {"datetime": _utc(first_of_month), "service": "Unknown service"},  # no price
        {"datetime": _utc(last_month), "service": "Haircut"},  # last month: 25
    ]

    result = await overview(docs, services)

    assert result["revenue"]["this_month"] == 40
    assert result["revenue"]["last_month"] == 25
    assert result["revenue"]["change_pct"] == 60
    assert result["revenue"]["unpriced_appointments"] == 1
    assert len(result["bookings"]["7days"]) == 7
    assert len(result["bookings"]["1month"]) == 4
    assert len(result["bookings"]["all"]) == 6
    assert sum(p["count"] for p in result["bookings"]["all"]) == 4


@pytest.mark.asyncio
async def test_today_counts_in_the_last_bar(overview):
    now = datetime.now(TZ).replace(tzinfo=None, second=0, microsecond=0)
    result = await overview([{"datetime": _utc(now), "service": "Haircut"}], [])
    assert result["bookings"]["7days"][-1]["count"] == 1
    assert result["bookings"]["1month"][-1]["count"] == 1
    assert result["bookings"]["all"][-1]["count"] == 1
    assert result["revenue"]["change_pct"] is None
