import pandas as pd
import streamlit as st

from app.common import sample_banner, state
from epic_ops.jobs.coach_pay import GROUP_PER_HOUR, coach_pay_sheet

s = state()
st.title("Coach pay")
sample_banner()

lines, unmatched = coach_pay_sheet(s.registrations)
st.write(f"Draft for group sessions at ${GROUP_PER_HOUR}/hour. Only sessions with at least one player count.")

if lines:
    df = pd.DataFrame(lines).rename(columns={"coach": "Coach", "sessions": "Sessions", "hours": "Hours", "amount": "Pay"})
    st.dataframe(df, hide_index=True, use_container_width=True,
                 column_config={"Pay": st.column_config.NumberColumn(format="$%.2f")})
    st.metric("Total", f"${df['Pay'].sum():,.2f}")
    st.download_button("Download CSV", df.to_csv(index=False), "coach-pay.csv", "text/csv")
if unmatched:
    st.warning("These events don't follow the \"Category · Level · Coach\" name pattern, so no coach was found: "
               + ", ".join(unmatched))
