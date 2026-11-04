"""Copies of CourtReserve data in Supabase, for reports. CourtReserve stays the source of truth."""

import os
from datetime import datetime, timezone

from supabase import Client, create_client

from ..config import CR_RATING_CATEGORY
from ..courtreserve.client import cr_level


def supabase_from_env(env=os.environ) -> Client:
    url, key = env.get("SUPABASE_URL"), env.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise RuntimeError("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _dupr(m: dict) -> str | None:
    return next((r["ValueRatingName"] for r in m.get("Ratings") or [] if "dupr" in r["CategoryName"].lower()), None)


def save_members(db: Client, members: list[dict]) -> None:
    db.table("members").upsert([{
        "member_id": m["OrganizationMemberId"], "first_name": m["FirstName"], "last_name": m["LastName"],
        "email": m.get("Email"), "gender": m.get("Gender"), "membership": m.get("MembershipTypeName"),
        "status": m.get("MembershipStatus"), "dupr": _dupr(m), "cr_level": cr_level(m, CR_RATING_CATEGORY),
        "synced_at": _now(),
    } for m in members]).execute()


def save_events(db: Client, events: list[dict]) -> None:
    db.table("events").upsert([{
        "event_id": e["EventId"], "name": e["EventName"], "category": e["EventCategoryName"],
        "starts_at": e["StartDateTime"], "ends_at": e["EndDateTime"],
        "max_registrants": e.get("MaxRegistrants"), "registered": e.get("RegisteredCount"), "synced_at": _now(),
    } for e in events]).execute()


def save_registrations(db: Client, regs: list[dict]) -> None:
    db.table("registrations").upsert([{
        "event_date_id": r["EventDateId"], "event_id": r["EventId"], "member_id": r["OrganizationMemberId"],
        "price_to_pay": r.get("PriceToPay"), "paid": r.get("PaidAmount"), "cancelled_at": r.get("CancelledOnUtc"),
    } for r in regs]).execute()
