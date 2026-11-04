from datetime import datetime, time

import pandas as pd
import streamlit as st

from app.common import sample_banner, state
from epic_ops.jobs.fill_report import fill_by_category, fill_report

s = state()
st.title("Fill report")
sample_banner()

as_of = st.date_input("Week starting", value=s.now().date())
now = datetime.combine(as_of, time(0, 0)).astimezone()
rows = fill_report(s.events, now)

if not rows:
    st.info("No events with a capacity in the 7 days from that date.")
else:
    table = pd.DataFrame([{
        "Starts": r["start"][:16].replace("T", " "),
        "Event": r["name"],
        "Category": r["category"],
        "Booked": f"{r['registered']}/{r['capacity']}",
        "Full": r["fill"],
        "Flag": {"full": "Full: add a section?", "low": "Under half full", None: ""}[r["flag"]],
    } for r in rows])
    st.dataframe(table, hide_index=True, use_container_width=True,
                 column_config={"Full": st.column_config.ProgressColumn("Full", min_value=0, max_value=1, format="percent")})

    st.subheader("By category")
    cats = pd.DataFrame(fill_by_category(rows)).set_index("category")
    st.bar_chart(cats["fill"], y_label="Share of spots booked", horizontal=True)
    st.caption("CourtReserve's API doesn't return waitlist counts, so a full event is the signal to add a section.")
