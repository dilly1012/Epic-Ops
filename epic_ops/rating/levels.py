from ..config import EPIC_TIER_SIZE, LEVEL_BANDS, LEVELS, RANKED_TIERS, RATING
from ..models import LevelDecision, Player


def band_for(rating: float) -> dict:
    r = round(rating, 2)  # bands are checked on the 2-decimal number players see
    for band in reversed(LEVEL_BANDS):
        if r >= band["min"]:
            return band
    return LEVEL_BANDS[0]


def decide_level(p: Player) -> LevelDecision | None:
    """Decide a player's level after the week's games (mutates the player).

    Up: as soon as the rating reaches the next band.
    Down: one level, only after `demote_after_updates_below` weekly checks in a row
    below the band, and never during the shield after a promotion.
    """
    target = band_for(p.rating)["level"]
    if p.level is None:
        p.level = target
        return LevelDecision(p.member_id, p.name, None, target, "first placement")

    cur, nxt = LEVELS.index(p.level), LEVELS.index(target)
    if nxt > cur:
        old, p.level = p.level, target
        p.updates_below_band = 0
        p.shield_games_left = RATING.demotion_shield_games
        return LevelDecision(p.member_id, p.name, old, target, "promoted")
    if nxt < cur:
        if p.shield_games_left > 0:
            return None
        p.updates_below_band += 1
        if p.updates_below_band < RATING.demote_after_updates_below:
            return None
        old, p.level = p.level, LEVELS[cur - 1]
        p.updates_below_band = 0
        return LevelDecision(p.member_id, p.name, old, p.level, "dropped")
    p.updates_below_band = 0
    return None


def ranked_tiers(players: list[Player], epic_size: int = EPIC_TIER_SIZE) -> dict[int, str]:
    """Epic Ranked tier per player, with the top `epic_size` ranked players shown as "Epic"."""
    out = {}
    for i, p in enumerate(sorted(players, key=lambda p: p.rating, reverse=True)):
        tier = next((t for t, lo in reversed(RANKED_TIERS) if p.rating >= lo), "Bronze")
        out[p.member_id] = "Epic" if i < epic_size and p.rated_games > 0 else tier
    return out
