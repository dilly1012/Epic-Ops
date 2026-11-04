from datetime import datetime, timezone

from ..config import RELIABILITY as R
from ..models import Game


def _days(at: str, now: datetime) -> float:
    return (now - datetime.fromisoformat(at)).total_seconds() / 86400


def reliability(member_id: int, games: list[Game], now: datetime | None = None) -> int:
    """Epic Reliability, 0-100.

    Recency of last Rating Night (40) + rated games in 6 months (40) + different opponents (20).
    No Rating Night in 90+ days caps it at 59.
    """
    now = now or datetime.now(timezone.utc)
    # Games dated after `now` are ignored, so a wrong clock can never push a score past 100.
    mine = [g for g in games if (member_id in g.team_a or member_id in g.team_b) and _days(g.played_at, now) >= 0]

    nights = [_days(g.played_at, now) for g in mine if g.source == "rating_night"]
    last_night = min(nights, default=float("inf"))
    recency = max(0.0, R.recency_max * (1 - last_night / R.recency_window_days))

    recent = [g for g in mine if _days(g.played_at, now) <= R.volume_window_days]
    volume = min(R.volume_max, len(recent) * R.per_game)

    opponents = {o for g in recent for o in (g.team_b if member_id in g.team_a else g.team_a)}
    variety = min(R.variety_max, len(opponents) * R.per_opponent)

    score = round(recency + volume + variety)
    if last_night > R.recency_window_days:
        score = min(score, R.stale_cap)
    return score


def reliability_label(score: int) -> str:
    if score >= R.reliable_at:
        return "Reliable"
    if score >= R.provisional_below:
        return "Low"
    return "Provisional"
