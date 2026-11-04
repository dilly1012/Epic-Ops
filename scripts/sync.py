"""Phase 1 sync: CourtReserve -> Supabase. Read-only against CourtReserve.

Run by hand with `python -m scripts.sync`, or every 10 minutes from GitHub Actions.
"""

from datetime import date, timedelta

from epic_ops.courtreserve.client import CourtReserve
from epic_ops.store.supabase_store import save_events, save_members, save_registrations, supabase_from_env


def day(offset: int) -> str:
    return (date.today() + timedelta(days=offset)).isoformat()


def main() -> None:
    cr, db = CourtReserve.from_env(), supabase_from_env()
    members = cr.members()
    save_members(db, members)
    events = cr.events(day(-14), day(42))
    save_events(db, events)
    regs = cr.registrations(day(-14), day(42))
    save_registrations(db, regs)
    print(f"Synced {len(members)} members, {len(events)} events, {len(regs)} registrations.")


if __name__ == "__main__":
    main()
