from dataclasses import dataclass, field
from typing import Literal, Optional

GameSource = Literal["rating_night", "ranked_court", "league", "epic_series"]


@dataclass
class Player:
    member_id: int
    name: str
    rating: float  # exact Epic Rating, shown to 2 decimals
    level: Optional[str] = None  # level currently set on the CourtReserve profile
    rated_games: int = 0
    updates_below_band: int = 0
    shield_games_left: int = 0
    boosted_games_left: int = 0  # games left at double movement
    last_rated_game_at: Optional[str] = None


@dataclass
class Game:
    id: str
    played_at: str  # ISO 8601 with offset
    source: GameSource
    team_a: list[int]  # doubles: two member ids, singles: one
    team_b: list[int]
    score_a: int
    score_b: int


@dataclass
class RatingChange:
    member_id: int
    game_id: str
    before: float
    after: float

    @property
    def delta(self) -> float:
        return round(self.after - self.before, 2)


@dataclass
class LevelDecision:
    member_id: int
    name: str
    from_level: Optional[str]
    to_level: str
    reason: Literal["first placement", "promoted", "dropped"]
