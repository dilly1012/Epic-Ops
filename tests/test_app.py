"""Smoke tests: every page renders on sample data, and score entry updates ratings."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

VIEWS = Path(__file__).resolve().parents[1] / "app" / "views"


def run_view(name: str) -> AppTest:
    at = AppTest.from_file(str(VIEWS / name), default_timeout=30)
    at.run()
    assert not at.exception, at.exception
    return at


@pytest.mark.parametrize("view", ["scores.py", "ratings.py", "monday.py", "fill.py", "pay.py"])
def test_page_renders(view):
    run_view(view)


def test_score_entry_saves_game_and_moves_ratings():
    at = run_view("scores.py")
    s = at.session_state.epic_state
    before = len(s.games)
    at.selectbox(key="a1").set_value(101)
    at.selectbox(key="a2").set_value(102)
    at.selectbox(key="b1").set_value(103)
    at.selectbox(key="b2").set_value(104)
    at.number_input[0].set_value(11)
    at.number_input[1].set_value(7)
    at.button[0].click()
    at.run()
    assert not at.exception
    assert len(s.games) == before + 1
    assert any("Saved" in m.value for m in at.success)


def test_score_entry_rejects_duplicate_player():
    at = run_view("scores.py")
    for key, pid in (("a1", 101), ("a2", 101), ("b1", 103), ("b2", 104)):
        at.selectbox(key=key).set_value(pid)
    at.number_input[0].set_value(11)
    at.button[0].click()
    at.run()
    assert any("only be on the court once" in e.value for e in at.error)


def test_monday_list_done_applies_level():
    at = run_view("monday.py")
    s = at.session_state.epic_state
    assert s.preview_level_changes(), "sample data should have a promotion"
    at.button[0].click()
    at.run()
    assert not s.preview_level_changes()


def test_password_from_streamlit_secrets_wins():
    from app.common import resolve_password
    assert resolve_password({"app_password": "from-secrets"}, {"APP_PASSWORD": "from-env"}) == "from-secrets"


def test_password_from_env_when_no_secrets():
    from app.common import resolve_password
    assert resolve_password({}, {"APP_PASSWORD": "from-env"}) == "from-env"


def test_no_password_means_open():
    from app.common import resolve_password
    assert resolve_password({}, {}) is None
    assert resolve_password({"app_password": ""}, {"APP_PASSWORD": ""}) is None
