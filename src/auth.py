"""Authentication helpers for Player AI (Streamlit app)."""

import hashlib
import hmac
import os
import json
import shutil
import re
import time
from collections import defaultdict
from pathlib import Path
import streamlit as st
import config
import db

# ---------------------------------------------------------------------------
# Rate limiting — simple in-memory token bucket per username.
# Resets when the Streamlit process restarts (acceptable for single-instance).
# ---------------------------------------------------------------------------
_login_attempts: dict[str, list[float]] = defaultdict(list)

_MAX_ATTEMPTS = 10
_WINDOW_SECONDS = 15 * 60  # 15 minutes

def _is_rate_limited(username: str) -> bool:
    """Return True if this username has exceeded the login attempt limit."""
    now = time.time()
    window_start = now - _WINDOW_SECONDS
    attempts = [t for t in _login_attempts[username] if t > window_start]
    _login_attempts[username] = attempts
    if len(attempts) >= _MAX_ATTEMPTS:
        return True
    _login_attempts[username].append(now)
    return False

# ---------------------------------------------------------------------------
# Session TTL — sessions expire after 8 hours of inactivity.
# ---------------------------------------------------------------------------
_SESSION_TTL_SECONDS = 8 * 60 * 60

def _session_is_expired() -> bool:
    login_at = st.session_state.get("login_at", 0)
    return (time.time() - login_at) > _SESSION_TTL_SECONDS

# ---------------------------------------------------------------------------
# Auth bypass for local development only.
# NEVER set COACH_AI_DISABLE_AUTH in production.
# ---------------------------------------------------------------------------
def is_auth_disabled():
    value = str(os.environ.get("COACH_AI_DISABLE_AUTH", "")).strip().lower()
    return value in {"1", "true", "yes", "on"}

# ---------------------------------------------------------------------------
# Password hashing — PBKDF2-SHA256.
# New hashes use 600 000 iterations (OWASP 2023 minimum).
# Legacy hashes (100 000 iterations) are transparently re-hashed on login.
# ---------------------------------------------------------------------------
_ITERATIONS_CURRENT = 600_000
_ITERATIONS_LEGACY  = 100_000

def hash_password(password: str, salt: bytes | None = None, iterations: int = _ITERATIONS_CURRENT) -> tuple[str, str]:
    if salt is None:
        salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
    return pwd_hash.hex(), salt.hex()

def verify_password(password: str, pwd_hash_hex: str, salt_hex: str) -> tuple[bool, bool]:
    """
    Return (valid, needs_rehash).
    needs_rehash is True when the stored hash used the legacy iteration count
    and should be upgraded on next successful login.
    """
    try:
        salt = bytes.fromhex(salt_hex)
        stored = bytes.fromhex(pwd_hash_hex)

        # Try current iteration count first
        current_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, _ITERATIONS_CURRENT)
        if hmac.compare_digest(current_hash, stored):
            return True, False

        # Fallback: try legacy iteration count
        legacy_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, _ITERATIONS_LEGACY)
        if hmac.compare_digest(legacy_hash, stored):
            return True, True  # valid but needs re-hash

        return False, False
    except Exception:
        return False, False


def bootstrap_user_sandbox(username: str) -> Path:
    """Bootstrap isolated sandboxed directory with starter files."""
    if username == "demo":
        user_dir = config.PRODUCTION_DATA_DIR / 'users' / 'demo'
        user_dir.mkdir(parents=True, exist_ok=True)
        _bootstrap_demo_sandbox(user_dir)
        return user_dir

    user_dir = config.PRODUCTION_DATA_DIR / 'users' / username
    user_dir.mkdir(parents=True, exist_ok=True)

    drill_src = config.PRODUCTION_DATA_DIR / 'drill_library.csv'
    drill_dst = user_dir / 'drill_library.csv'
    if not drill_dst.exists() and drill_src.exists():
        shutil.copy(drill_src, drill_dst)

    feed_src = config.PRODUCTION_DATA_DIR / 'mentor_feed.json'
    feed_dst = user_dir / 'mentor_feed.json'
    if not feed_dst.exists() and feed_src.exists():
        shutil.copy(feed_src, feed_dst)

    pres_src = config.DATA_DIR / 'presenters.csv'
    pres_dst = user_dir / 'presenters.csv'
    if not pres_dst.exists() and pres_src.exists():
        shutil.copy(pres_src, pres_dst)

    return user_dir


def _bootstrap_demo_sandbox(user_dir: Path) -> None:
    demo_src = config.DEMO_DATA_DIR
    files_to_copy = [
        "athlete_profile.json",
        "completion_log.json",
        "weekly_training_plan.json",
        "rrs_history.json",
        "mentor_feed.json",
        "drill_library.csv",
        "presenters.csv",
    ]
    for filename in files_to_copy:
        src = demo_src / filename
        dst = user_dir / filename
        if src.exists():
            shutil.copy(src, dst)

def _seed_demo_to_supabase() -> None:
    demo_src = config.DEMO_DATA_DIR
    files = {
        "athlete_profile.json":      "athlete_profile",
        "completion_log.json":        "completion_log",
        "weekly_training_plan.json":  "weekly_training_plan",
        "rrs_history.json":           "rrs_history",
        "mentor_feed.json":           "mentor_feed",
    }
    for filename, data_key in files.items():
        src = demo_src / filename
        if not src.exists():
            continue
        try:
            with open(src, "r", encoding="utf-8") as f:
                data_value = f.read()
            db.save_user_data("demo", data_key, data_value)
        except Exception:
            pass


def is_valid_username(username: str) -> bool:
    return bool(re.match(r'^[a-zA-Z0-9_\-\.@]+$', username)) and len(username) >= 3


def signup_user(username, password) -> bool:
    username = username.strip().lower()
    if not username:
        st.error("Username cannot be empty.")
        return False
    if not is_valid_username(username):
        st.error("Username must be at least 3 characters and contain only "
                 "letters, numbers, and symbols (@ . _ -).")
        return False
    if len(password) < 8:
        st.error("Password must be at least 8 characters.")
        return False
    try:
        existing = db.get_user(username)
    except RuntimeError as e:
        st.error(f"Database error: {e}")
        return False
    if existing:
        st.error("Username is already taken.")
        return False
    pwd_hash, salt = hash_password(password)
    try:
        db.create_user(username, pwd_hash, salt)
    except RuntimeError as e:
        st.error(f"Could not create account: {e}")
        return False
    bootstrap_user_sandbox(username)
    return True


def login_user(username, password) -> bool:
    username = username.strip().lower()
    if not username or not password:
        st.error("Username and password cannot be empty.")
        return False

    if _is_rate_limited(username):
        st.error("Too many login attempts. Please wait 15 minutes and try again.")
        return False

    try:
        user_data = db.get_user(username)
    except RuntimeError as e:
        st.error(f"Database error: {e}")
        return False
    if not user_data:
        st.error("Invalid username or password.")
        return False

    valid, needs_rehash = verify_password(password, user_data["password_hash"], user_data["salt"])

    if not valid:
        st.error("Invalid username or password.")
        return False

    # Transparently re-hash legacy passwords to current iteration count
    if needs_rehash:
        try:
            new_hash, new_salt = hash_password(password)
            db.update_password(username, new_hash, new_salt)
        except Exception:
            pass  # Never fail login because of a re-hash error

    if username == "demo":
        _seed_demo_to_supabase()

    st.session_state.authenticated = True
    st.session_state.username = username
    st.session_state.login_at = time.time()
    st.session_state.data_path = config.PRODUCTION_DATA_DIR / "users" / username
    return True


def logout():
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.login_at = None
    st.session_state.athlete_profile = None
    st.session_state.drills_df = None
    st.session_state.weekly_training_plan = None
    st.session_state.completion_log = None
    st.session_state.redirect_banner = None
    st.rerun()


def is_authenticated():
    if is_auth_disabled():
        return True
    if not (st.session_state.get("authenticated", False) and st.session_state.get("username")):
        return False
    if _session_is_expired():
        # Session TTL exceeded — force re-login
        logout()
        return False
    return True


def render_auth_sidebar():
    with st.sidebar:
        st.markdown("---")
        st.markdown(
            f"""
            <div style="
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 15px;
                margin-bottom: 15px;
            ">
                <div style="font-size: 11px; color: #888; letter-spacing: 0.5px; text-transform: uppercase;">👤 Logged In As</div>
                <div style="font-size: 15px; font-weight: 600; color: #fff; overflow-wrap: break-word; margin-top: 4px;">{st.session_state.username}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Log Out", use_container_width=True, key="auth_logout_button"):
            logout()


def render_login_screen():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #0b0f19;
            background-image:
                radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.12) 0, transparent 50%),
                radial-gradient(at 100% 100%, rgba(139, 92, 246, 0.12) 0, transparent 50%);
        }
        .glass-container {
            background: rgba(17, 24, 39, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
            max-width: 480px;
            margin: 40px auto;
        }
        .login-header-text {
            text-align: center;
            font-weight: 800;
            color: #ffffff;
            font-size: 2.2rem;
            margin-bottom: 6px;
            letter-spacing: -0.5px;
        }
        .login-subheader-text {
            text-align: center;
            color: #9ca3af;
            font-size: 0.95rem;
            margin-bottom: 25px;
        }
        div.stRadio > div {
            background-color: rgba(255, 255, 255, 0.03);
            border-radius: 10px;
            padding: 5px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-header-text">⚽ Player AI</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subheader-text">Player AI</div>', unsafe_allow_html=True)

        mode = st.radio(
            "Select Access Mode",
            ["Log In", "Create Account"],
            horizontal=True,
            label_visibility="collapsed",
            index=0 if st.session_state.auth_mode == "login" else 1,
            key="access_mode_toggle"
        )

        st.session_state.auth_mode = "login" if mode == "Log In" else "signup"
        st.markdown("<br>", unsafe_allow_html=True)

        if st.session_state.auth_mode == "login":
            username = st.text_input("Username or Email", placeholder="e.g. player_john", key="login_username")
            password = st.text_input("Password", type="password", placeholder="••••••••", key="login_password")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Log In to Dashboard", use_container_width=True, type="primary", key="submit_login"):
                if login_user(username, password):
                    st.success("Successfully logged in! Redirecting...")
                    st.rerun()
        else:
            username = st.text_input("New Username or Email", placeholder="e.g. player_john", key="signup_username")
            password = st.text_input("Password (min 8 characters)", type="password", placeholder="••••••••", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="••••••••", key="signup_confirm")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Register & Initialize Account", use_container_width=True, type="primary", key="submit_signup"):
                if password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    if signup_user(username, password):
                        st.success("Account created successfully! Logging you in...")
                        if login_user(username, password):
                            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


def require_auth():
    """Gate a page behind authentication and sandbox isolation."""
    if is_auth_disabled():
        st.session_state.authenticated = True
        if "username" not in st.session_state or not st.session_state.username:
            st.session_state.username = "local_player"
        if "data_path" not in st.session_state or not st.session_state.data_path:
            st.session_state.data_path = config.get_data_path()
        return True

    if st.session_state.get("authenticated", False) and st.session_state.get("username"):
        if _session_is_expired():
            logout()
            return False
        username = st.session_state.username
        user_dir = config.PRODUCTION_DATA_DIR / 'users' / username
        if not user_dir.exists():
            bootstrap_user_sandbox(username)
        st.session_state.data_path = user_dir
        render_auth_sidebar()
        return True

    render_login_screen()
    st.stop()
