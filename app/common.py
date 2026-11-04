import hmac

import streamlit as st

from epic_ops.state import SampleState


def require_login() -> None:
    """Simple shared password. Set `app_password` in .streamlit/secrets.toml (or the host's secrets).

    With no password set, the app is open, which is fine for trying it locally.
    """
    password = st.secrets.get("app_password") if _has_secrets() else None
    if not password or st.session_state.get("signed_in"):
        return
    st.title("Epic Ops")
    entered = st.text_input("Staff password", type="password")
    if entered and hmac.compare_digest(entered, password):
        st.session_state.signed_in = True
        st.rerun()
    elif entered:
        st.error("Wrong password.")
    st.stop()


def _has_secrets() -> bool:
    try:
        return len(st.secrets) > 0
    except Exception:
        return False


def state() -> SampleState:
    if "epic_state" not in st.session_state:
        st.session_state.epic_state = SampleState.load()
    return st.session_state.epic_state


def sample_banner() -> None:
    st.caption("Sample data. Nothing here touches CourtReserve yet, and changes reset when the app restarts.")
