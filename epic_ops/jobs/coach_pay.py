"""Draft pay sheet for group sessions.

Event names follow "Category · Level · Coach" (set up in Phase 0),
e.g. "Clinic · L4 · Dillon", so the coach is the last part.
"""

from datetime import datetime

# Proposed, not final. Group rate is per hour.
GROUP_PER_HOUR = 45


def coach_from_event_name(name: str) -> str | None:
    parts = [p.strip() for p in name.split("·")]
    return parts[-1] if len(parts) >= 3 else None


def coach_pay_sheet(registrations: list[dict]) -> tuple[list[dict], list[str]]:
    """One line per coach for sessions that had at least one player, plus unmatched event names."""
    sessions = {r["EventDateId"]: r for r in registrations if not r.get("CancelledOnUtc")}
    lines: dict[str, dict] = {}
    unmatched: set[str] = set()
    for s in sessions.values():
        coach = coach_from_event_name(s["EventName"])
        if not coach:
            unmatched.add(s["EventName"])
            continue
        hours = (datetime.fromisoformat(s["EndTime"]) - datetime.fromisoformat(s["StartTime"])).total_seconds() / 3600
        line = lines.setdefault(coach, {"coach": coach, "sessions": 0, "hours": 0.0, "amount": 0.0})
        line["sessions"] += 1
        line["hours"] += hours
        line["amount"] += hours * GROUP_PER_HOUR
    return sorted(lines.values(), key=lambda l: l["coach"]), sorted(unmatched)
