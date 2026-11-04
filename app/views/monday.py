import streamlit as st

from app.common import sample_banner, state
from epic_ops.config import CR_RATING_CATEGORY, LEVEL_BANDS
from epic_ops.rating.elo import fmt

s = state()
st.title("Monday level list")
sample_banner()

OPTION = {b["level"]: b["cr_option"] for b in LEVEL_BANDS}
todo = s.preview_level_changes()

st.write(f"Change each player's band in CourtReserve (member profile › Ratings › **{CR_RATING_CATEGORY}**), "
         "then tick them off here.")

if not todo:
    st.success("No level changes this week.")
for d in sorted(todo, key=lambda d: d.name):
    old = OPTION[d.from_level] if d.from_level else "(none)"
    col1, col2 = st.columns([5, 1])
    col1.markdown(f"**{d.name}** · {fmt(s.players[d.member_id].rating)} · {old} → **{OPTION[d.to_level]}** · _{d.reason}_")
    if col2.button("Done", key=f"done-{d.member_id}", use_container_width=True):
        s.mark_level_done(d.member_id)
        st.rerun()

if s.levels_done:
    st.caption(f"Done this session: {', '.join(s.players[i].name for i in sorted(s.levels_done))}")
