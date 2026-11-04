"""The Monday level list: who staff need to move to a new band in CourtReserve.

Run once a week, after the weekend's Rating Night.
"""

from ..config import CR_RATING_CATEGORY, LEVEL_BANDS
from ..models import LevelDecision, Player
from ..rating.elo import fmt
from ..rating.levels import decide_level

_OPTION = {b["level"]: b["cr_option"] for b in LEVEL_BANDS}


def monday_level_list(players: list[Player]) -> list[LevelDecision]:
    return [d for d in (decide_level(p) for p in players) if d]


def format_monday_list(decisions: list[LevelDecision], players: dict[int, Player]) -> str:
    if not decisions:
        return "No level changes this week."
    lines = [f"Level changes to make in CourtReserve (member profile > Ratings > {CR_RATING_CATEGORY}):"]
    for d in sorted(decisions, key=lambda d: d.name):
        old = _OPTION[d.from_level] if d.from_level else "(none)"
        lines.append(f"- {d.name} (#{d.member_id}), {fmt(players[d.member_id].rating)}: "
                     f"{old} -> {_OPTION[d.to_level]} [{d.reason}]")
    return "\n".join(lines)
