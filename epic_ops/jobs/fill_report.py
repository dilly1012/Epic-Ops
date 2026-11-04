"""Events in the next week with fill rate.

"low" = under 50% full, "full" = at capacity (a candidate for a second section).
The API doesn't return waitlist counts, so "full" is the best signal until it does.
"""

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from ..config import REPORTS


def fill_report(events: list[dict], now: datetime | None = None) -> list[dict]:
    now = now or datetime.now(timezone.utc)
    horizon = now + timedelta(days=REPORTS.window_days)
    rows = []
    for e in events:
        start = datetime.fromisoformat(e["StartDateTime"])
        cap = e.get("MaxRegistrants")
        if not cap or not (now <= start <= horizon):
            continue
        reg = e.get("RegisteredCount") or 0
        fill = reg / cap
        flag = "full" if fill >= 1 else "low" if fill < REPORTS.low_fill else None
        rows.append({"event_id": e["EventId"], "name": e["EventName"], "category": e["EventCategoryName"],
                     "start": e["StartDateTime"], "registered": reg, "capacity": cap, "fill": fill, "flag": flag})
    return sorted(rows, key=lambda r: datetime.fromisoformat(r["start"]))


def fill_by_category(rows: list[dict]) -> list[dict]:
    """Fill rate per category, e.g. to see how the Women's program is doing."""
    totals = defaultdict(lambda: [0, 0])
    for r in rows:
        totals[r["category"]][0] += r["registered"]
        totals[r["category"]][1] += r["capacity"]
    return [{"category": c, "registered": reg, "capacity": cap, "fill": reg / cap if cap else 0}
            for c, (reg, cap) in totals.items()]
