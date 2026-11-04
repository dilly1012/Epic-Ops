"""Where the web app gets its data.

Sample mode (the default) keeps everything in memory, starting from the sample data.
Once CourtReserve and Supabase are connected, swap SampleState for a version that
reads and writes the Supabase tables; the pages only use these methods.
"""

import copy
from dataclasses import dataclass, field
from datetime import datetime

from .config import EPIC_TIER_SIZE
from .models import Game, Player, RatingChange
from .rating.elo import apply_game
from .rating.levels import decide_level


@dataclass
class SampleState:
    players: dict[int, Player]
    games: list[Game]
    events: list[dict]
    registrations: list[dict]
    changes: list[RatingChange] = field(default_factory=list)
    levels_done: set[int] = field(default_factory=set)
    # Sample mode runs on a fixed clock (the Monday after the sample Rating Night).
    clock: datetime | None = None
    # Only 8 sample players, so show the top 2 as the "Epic" tier instead of the top 10.
    epic_size: int = EPIC_TIER_SIZE

    @classmethod
    def load(cls) -> "SampleState":
        from sample.data import SAMPLE_EVENTS, SAMPLE_GAMES, SAMPLE_PLAYERS, SAMPLE_REGISTRATIONS

        players = {pid: Player(pid, name, rating, level, games, last_rated_game_at="2026-12-27T17:00:00-06:00")
                   for pid, name, rating, level, games in SAMPLE_PLAYERS}
        state = cls(players, [], list(SAMPLE_EVENTS), list(SAMPLE_REGISTRATIONS),
                    clock=datetime.fromisoformat("2027-01-11T09:00:00-06:00"), epic_size=2)
        for g in SAMPLE_GAMES:
            state.record_game(g)
        return state

    def record_game(self, game: Game) -> list[RatingChange]:
        changes = apply_game(game, self.players)
        self.games.append(game)
        self.changes.extend(changes)
        return changes

    def preview_level_changes(self):
        """This week's level changes, worked out on a copy so nothing changes until staff tick it off."""
        return [d for d in (decide_level(copy.deepcopy(p)) for p in self.players.values()) if d]

    def mark_level_done(self, member_id: int) -> None:
        """Staff changed the band in CourtReserve: apply the same decision here."""
        decide_level(self.players[member_id])
        self.levels_done.add(member_id)

    def now(self) -> datetime:
        return self.clock or datetime.now().astimezone()

    def next_game_id(self) -> str:
        return f"g{len(self.games) + 1}-{datetime.now().strftime('%H%M%S')}"
