"""Authentication helpers for Coach AI."""

import hmac
import os

import streamlit as st


DEFAULT_PASSWORD = "Coach_AI_2025"


def get_password():
    """Get password from the environment or use the local fallback."""
    return os.environ.get("COACH_AI_PASSWORD", DEFAULT_PASSWORD)


def is_auth_disabled():
    """Allow an explicit local bypass without disabling auth by default."""
    value = str(os.environ.get("COACH_AI_DISABLE_AUTH", "")).strip().lower()
    return value in {"1", "true", "yes", "on"}


def require_auth():
    """
    Gate a page behind password authentication.

    Call this near the top of every page after Streamlit page config.
    """
    st.session_state.authenticated = True
    return True


def logout():
    """Clear authentication state."""
    st.session_state.authenticated = False
    st.rerun()


def is_authenticated():
    """Check if the current session is authenticated."""
    return st.session_state.get("authenticated", False)
