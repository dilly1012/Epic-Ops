import streamlit as st

from app.common import sample_banner, state
from epic_ops.models import Game
from epic_ops.rating.elo import fmt

s = state()
st.title("Score entry")
sample_banner()

names = {p.member_id: p.name for p in s.players.values()}
ids = sorted(names, key=lambda i: names[i])
label = lambda i: f"{names[i]} ({fmt(s.players[i].rating)})"

SOURCES = {"Rating Night": "rating_night", "Ranked court": "ranked_court", "League": "league", "Epic Series": "epic_series"}

with st.form("score", clear_on_submit=True):
    source = st.selectbox("Game type", list(SOURCES))
    st.markdown("**Team A**")
    a1, a2 = st.columns(2)
    pa1 = a1.selectbox("Player 1", ids, format_func=label, key="a1", index=None, placeholder="Pick a player")
    pa2 = a2.selectbox("Player 2", ids, format_func=label, key="a2", index=None, placeholder="Pick a player")
    st.markdown("**Team B**")
    b1, b2 = st.columns(2)
    pb1 = b1.selectbox("Player 1", ids, format_func=label, key="b1", index=None, placeholder="Pick a player")
    pb2 = b2.selectbox("Player 2", ids, format_func=label, key="b2", index=None, placeholder="Pick a player")
    sa, sb = st.columns(2)
    score_a = sa.number_input("Team A score", min_value=0, max_value=30, step=1, value=0)
    score_b = sb.number_input("Team B score", min_value=0, max_value=30, step=1, value=0)
    submitted = st.form_submit_button("Save game", type="primary", use_container_width=True)

if submitted:
    picked = [p for p in (pa1, pa2, pb1, pb2) if p is not None]
    if len(picked) != 4:
        st.error("Pick all four players.")
    elif len(set(picked)) != 4:
        st.error("A player can only be on the court once.")
    elif score_a == score_b:
        st.error("A game needs a winner.")
    else:
        game = Game(s.next_game_id(), s.now().isoformat(), SOURCES[source],
                    [pa1, pa2], [pb1, pb2], int(score_a), int(score_b))
        changes = s.record_game(game)
        st.success("Saved. New Epic Ratings:")
        for c in changes:
            st.write(f"{names[c.member_id]}: {fmt(c.before)} → **{fmt(c.after)}** ({c.delta:+.2f})")

st.subheader("Recent games")
if s.games:
    rows = []
    for g in reversed(s.games[-15:]):
        rows.append({
            "When": g.played_at[:16].replace("T", " "),
            "Type": next(k for k, v in SOURCES.items() if v == g.source),
            "Team A": " / ".join(names[i] for i in g.team_a),
            "Score": f"{g.score_a}–{g.score_b}",
            "Team B": " / ".join(names[i] for i in g.team_b),
        })
    st.dataframe(rows, hide_index=True, use_container_width=True)
