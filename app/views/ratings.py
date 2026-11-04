import streamlit as st

from app.common import sample_banner, state
from epic_ops.rating.elo import fmt
from epic_ops.rating.levels import band_for, ranked_tiers
from epic_ops.rating.reliability import reliability, reliability_label

s = state()
st.title("Ratings")
sample_banner()

tiers = ranked_tiers(list(s.players.values()), s.epic_size)
last_change = {}
for c in s.changes:
    last_change[c.member_id] = c

rows = []
for p in sorted(s.players.values(), key=lambda p: p.rating, reverse=True):
    rel = reliability(p.member_id, s.games, s.now())
    c = last_change.get(p.member_id)
    rows.append({
        "Player": p.name,
        "Epic Rating": fmt(p.rating),
        "Last game": f"{c.delta:+.2f}" if c else "",
        "Reliability": f"{rel}% ({reliability_label(rel)})",
        "Level in CourtReserve": p.level or "not set",
        "Rating's band": band_for(p.rating)["level"],
        "Ranked tier": tiers[p.member_id],
        "Rated games": p.rated_games,
    })
st.dataframe(rows, hide_index=True, use_container_width=True)
st.caption("Level drops wait for 2 weekly checks below the band, so \"Level in CourtReserve\" "
           "can differ from \"Rating's band\" for a week.")
