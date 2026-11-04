"""Epic Ops web app. Run with:  streamlit run app/streamlit_app.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # so `epic_ops` imports without installing

import streamlit as st

from app.common import require_login

st.set_page_config(page_title="Epic Ops", page_icon="🏓", layout="wide")
require_login()

views = Path(__file__).parent / "views"
nav = st.navigation([
    st.Page(views / "scores.py", title="Score entry", icon="📝", default=True),
    st.Page(views / "ratings.py", title="Ratings", icon="📈", url_path="ratings"),
    st.Page(views / "monday.py", title="Monday level list", icon="✅", url_path="monday"),
    st.Page(views / "fill.py", title="Fill report", icon="📅", url_path="fill"),
    st.Page(views / "pay.py", title="Coach pay", icon="💵", url_path="pay"),
])
nav.run()
