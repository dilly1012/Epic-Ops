from datetime import datetime

import pytest

from epic_ops.models import Game, Player
from epic_ops.rating.elo import apply_game, expected_score, movement, new_player
from epic_ops.rating.levels import band_for, decide_level
from epic_ops.rating.reliability import reliability


def player(pid, rating, **kw):
    defaults = dict(level=band_for(rating)["level"], rated_games=10, last_rated_game_at="2027-01-01T00:00:00+00:00")
    defaults.update(kw)
    return Player(pid, f"P{pid}", rating, **defaults)


def game(a, b, sa, sb, source="rating_night", at="2027-01-10T00:00:00+00:00"):
    return Game("g", at, source, a, b, sa, sb)


@pytest.mark.parametrize("expected", [0.01, 0.2, 0.5, 0.8, 0.99])
@pytest.mark.parametrize("won", [True, False])
def test_movement_stays_between_001_and_006(expected, won):
    assert 0.01 <= abs(movement(won, expected, False)) <= 0.06


def test_placement_moves_double():
    assert movement(True, 0.5, True) == pytest.approx(2 * movement(True, 0.5, False))


def test_upset_moves_more_than_expected_win():
    assert movement(True, 0.2, False) > movement(True, 0.8, False)


def test_half_point_favourite_is_big_favourite():
    assert expected_score(3.5, 3.0) > 0.85


def test_winners_up_losers_down_two_decimals():
    ps = {i: player(i, 3.25) for i in (1, 2, 3, 4)}
    changes = apply_game(game([1, 2], [3, 4], 11, 7), ps)
    assert [c.member_id for c in changes if c.delta > 0] == [1, 2]
    assert all(c.after == round(c.after, 2) for c in changes)


def test_return_after_three_months_gets_boost_not_decay():
    ps = {i: player(i, 3.25, last_rated_game_at="2026-09-01T00:00:00+00:00") for i in (1, 2)}
    apply_game(game([1], [2], 11, 5), ps)
    assert ps[1].boosted_games_left == 2  # 3 granted, 1 used


def test_new_players_get_five_placement_games():
    assert new_player(9, "New", 2.7).boosted_games_left == 5


def test_tie_is_rejected():
    with pytest.raises(ValueError):
        apply_game(game([1], [2], 9, 9), {i: player(i, 3.0) for i in (1, 2)})


@pytest.mark.parametrize("rating,level", [(2.49, "L1"), (2.50, "L2"), (3.99, "L4"), (4.00, "L5")])
def test_even_half_point_bands(rating, level):
    assert band_for(rating)["level"] == level


def test_promotes_straight_away_and_starts_shield():
    p = player(1, 3.50, level="L3")
    assert decide_level(p).reason == "promoted"
    assert p.shield_games_left == 3


def test_drops_only_after_two_weekly_checks_below():
    p = player(1, 3.41, level="L4")
    assert decide_level(p) is None
    assert decide_level(p).to_level == "L3"


def test_never_drops_during_shield():
    p = player(1, 3.41, level="L4", shield_games_left=2)
    assert decide_level(p) is None
    assert decide_level(p) is None


NOW = datetime.fromisoformat("2027-01-11T00:00:00+00:00")


def test_reliability_capped_without_recent_rating_night():
    games = [game([1], [100 + i], 11, 5, source="league", at=f"2027-01-0{i % 9 + 1}T00:00:00+00:00") for i in range(12)]
    assert reliability(1, games, NOW) == 59


def test_regular_rating_night_player_is_reliable():
    games = [game([1], [200 + i], 11, 5) for i in range(8)]
    assert reliability(1, games, NOW) >= 60


def test_future_games_do_not_push_reliability_past_100():
    games = [game([1], [300 + i], 11, 5, at="2027-03-01T00:00:00+00:00") for i in range(20)]
    assert reliability(1, games, NOW) <= 100
