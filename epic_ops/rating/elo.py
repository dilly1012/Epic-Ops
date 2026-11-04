from datetime import datetime

from ..config import RATING
from ..models import Game, Player, RatingChange


def expected_score(a: float, b: float, spread: float = RATING.spread) -> float:
    """Chance that a team rated `a` beats a team rated `b`."""
    return 1 / (1 + 10 ** ((b - a) / spread))


def movement(won: bool, expected: float, boosted: bool) -> float:
    """How far one game moves a player.

    An upset moves close to max_move, the expected result close to min_move.
    Boosted (placement or return) games move double.
    """
    surprise = abs((1 if won else 0) - expected)
    size = min(RATING.max_move, max(RATING.min_move, RATING.max_move * surprise))
    return (1 if won else -1) * size * (2 if boosted else 1)


def _days_between(a: str, b: str) -> float:
    return (datetime.fromisoformat(b) - datetime.fromisoformat(a)).total_seconds() / 86400


def _return_boost(p: Player, played_at: str) -> None:
    """No rank decay: a player back after a long break gets double-movement games instead."""
    if p.last_rated_game_at and p.boosted_games_left == 0:
        if _days_between(p.last_rated_game_at, played_at) >= RATING.return_after_days:
            p.boosted_games_left = RATING.return_games


def _team_rating(ids: list[int], players: dict[int, Player]) -> float:
    missing = [i for i in ids if i not in players]
    if missing:
        raise KeyError(f"Unknown players in game: {missing}")
    return sum(players[i].rating for i in ids) / len(ids)


def apply_game(game: Game, players: dict[int, Player]) -> list[RatingChange]:
    """Apply one game (mutates `players`) and return each player's change.

    Every player on a team moves by their own amount, so boosted players move more.
    """
    if game.score_a == game.score_b:
        raise ValueError(f"Game {game.id} has no winner")
    ra, rb = _team_rating(game.team_a, players), _team_rating(game.team_b, players)
    e_a = expected_score(ra, rb)
    a_won = game.score_a > game.score_b

    changes: list[RatingChange] = []
    for ids, won, expected in ((game.team_a, a_won, e_a), (game.team_b, not a_won, 1 - e_a)):
        for mid in ids:
            p = players[mid]
            _return_boost(p, game.played_at)
            before = p.rating
            p.rating = max(RATING.floor, round(before + movement(won, expected, p.boosted_games_left > 0), 2))
            p.rated_games += 1
            p.last_rated_game_at = game.played_at
            p.boosted_games_left = max(0, p.boosted_games_left - 1)
            p.shield_games_left = max(0, p.shield_games_left - 1)
            changes.append(RatingChange(mid, game.id, before, p.rating))
    return changes


def new_player(member_id: int, name: str, seed_rating: float) -> Player:
    """A brand-new player, seeded from their Welcome Video Lesson placement."""
    return Player(member_id, name, round(max(RATING.floor, seed_rating), 2), boosted_games_left=RATING.placement_games)


def fmt(rating: float) -> str:
    return f"{rating:.2f}"
