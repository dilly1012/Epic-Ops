"""Epic Pickleball programming rules. Change numbers here, not in the logic.

Source: the Epic programming plan and rating decisions (Nov 2026).
"""

import math

# Level bands. Placement uses the Epic Rating alone (DUPR is display only).
LEVEL_BANDS = [
    {"level": "L1", "min": 2.00, "cr_option": "L1 2.00-2.49"},
    {"level": "L2", "min": 2.50, "cr_option": "L2 2.50-2.99"},
    {"level": "L3", "min": 3.00, "cr_option": "L3 3.00-3.49"},
    {"level": "L4", "min": 3.50, "cr_option": "L4 3.50-3.99"},
    {"level": "L5", "min": 4.00, "cr_option": "L5 4.00+"},
]
LEVELS = [b["level"] for b in LEVEL_BANDS]

# Name of the CourtReserve custom rating category that events gate on.
CR_RATING_CATEGORY = "Epic Rating"

# Epic Ranked tiers. Same cutoffs as the levels, but a separate thing.
RANKED_TIERS = [("Bronze", 2.00), ("Silver", 2.50), ("Gold", 3.00), ("Platinum", 3.50), ("Diamond", 4.00)]
EPIC_TIER_SIZE = 10  # the club's top N ranked players get the "Epic" tier


class RATING:
    floor = 2.00
    min_move = 0.01  # every rated game moves the number at least this much...
    max_move = 0.06  # ...and at most this much
    spread = 0.5  # a team 0.50 higher is expected to win ~91%
    placement_games = 5  # new players: double movement
    return_games = 3  # back after 3+ months away: double movement
    return_after_days = 90
    demotion_shield_games = 3  # games after a promotion with no demotion
    demote_after_updates_below = 2  # weekly checks in a row below the band before dropping


class RELIABILITY:
    recency_max = 40  # points for a recent Rating Night, falling to 0 at 90 days
    recency_window_days = 90
    per_game = 4  # points per rated game in the last 6 months
    volume_max = 40
    volume_window_days = 182
    per_opponent = 2  # points per different opponent
    variety_max = 20
    stale_cap = 59  # no Rating Night in 90+ days caps reliability here
    reliable_at = 60
    provisional_below = 30


class REPORTS:
    low_fill = 0.5  # flag events under this share of capacity...
    window_days = 7  # ...that start within this many days


INF = math.inf
