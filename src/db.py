"""Supabase database client — single source of truth for all DB access."""
import os
from datetime import datetime, timezone
import streamlit as st

def _is_auth_disabled() -> bool:
    value = str(os.environ.get("COACH_AI_DISABLE_AUTH", "")).strip().lower()
    return value in {"1", "true", "yes", "on"}

@st.cache_resource
def get_client():
    """Lazily initialize and cache the Supabase client."""
    from supabase import create_client
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_KEY environment variables are not set. "
            "Add them to Streamlit Cloud secrets or your local .env file."
        )
    return create_client(url, key)

def get_user(username: str) -> dict | None:
    """Return user row as dict, or None if not found."""
    try:
        client = get_client()
        response = (
            client.table("users")
            .select("*")
            .eq("username", username)
            .execute()
        )
        return response.data[0] if response.data else None
    except Exception as e:
        raise RuntimeError(f"get_user failed for '{username}': {e}") from e

def create_user(username: str, password_hash: str, salt: str) -> None:
    """Insert a new user. Raises RuntimeError if username already exists."""
    try:
        client = get_client()
        client.table("users").insert({
            "username": username,
            "password_hash": password_hash,
            "salt": salt,
        }).execute()
    except Exception as e:
        raise RuntimeError(f"create_user failed for '{username}': {e}") from e

def load_user_data(username: str, data_key: str) -> str | None:
    """Return data_value string for (username, data_key), or None if not found."""
    try:
        client = get_client()
        response = (
            client.table("user_data")
            .select("data_value")
            .eq("username", username)
            .eq("data_key", data_key)
            .execute()
        )
        return response.data[0]["data_value"] if response.data else None
    except Exception as e:
        raise RuntimeError(
            f"load_user_data failed for '{username}'/'{data_key}': {e}"
        ) from e

def save_user_data(username: str, data_key: str, data_value: str) -> None:
    """Upsert (insert or update) a user_data row.
    
    Both username and data_key are included in the dict so Postgres can
    resolve the composite primary key conflict automatically.
    updated_at is passed explicitly because the default only fires on INSERT.
    """
    try:
        client = get_client()
        client.table("user_data").upsert({
            "username": username,
            "data_key": data_key,
            "data_value": data_value,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
    except Exception as e:
        raise RuntimeError(
            f"save_user_data failed for '{username}'/'{data_key}': {e}"
        ) from e
