"""Authentication helpers for Coach AI."""

import hashlib
import os
import json
import shutil
import re
from pathlib import Path
import streamlit as st
import config

DEFAULT_PASSWORD = "Coach_AI_2025"

def get_password():
    """Get password from the environment or use the local fallback."""
    return os.environ.get("COACH_AI_PASSWORD", DEFAULT_PASSWORD)

def is_auth_disabled():
    """Allow an explicit local bypass without disabling auth by default."""
    value = str(os.environ.get("COACH_AI_DISABLE_AUTH", "")).strip().lower()
    return value in {"1", "true", "yes", "on"}

def hash_password(password: str, salt: bytes = None) -> tuple[str, str]:
    """Hash password using robust PBKDF2 with SHA-256."""
    if salt is None:
        salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000
    )
    return pwd_hash.hex(), salt.hex()

def verify_password(password: str, pwd_hash_hex: str, salt_hex: str) -> bool:
    """Verify a password against stored PBKDF2 hash and salt."""
    try:
        salt = bytes.fromhex(salt_hex)
        pwd_hash = bytes.fromhex(pwd_hash_hex)
        test_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        )
        return pwd_hash == test_hash
    except Exception:
        return False

def get_users_file_path() -> Path:
    """Get path to the users database file."""
    return config.PRODUCTION_DATA_DIR / 'users.json'

def load_users() -> dict:
    """Load user credentials from file."""
    users_file = get_users_file_path()
    if users_file.exists():
        try:
            with open(users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_users(users: dict) -> None:
    """Save user credentials to file."""
    users_file = get_users_file_path()
    users_file.parent.mkdir(parents=True, exist_ok=True)
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)

def bootstrap_user_sandbox(username: str) -> Path:
    """Bootstrap isolated sandboxed directory with starter files."""
    user_dir = config.PRODUCTION_DATA_DIR / 'users' / username
    user_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Drill library
    drill_src = config.PRODUCTION_DATA_DIR / 'drill_library.csv'
    drill_dst = user_dir / 'drill_library.csv'
    if not drill_dst.exists() and drill_src.exists():
        shutil.copy(drill_src, drill_dst)
        
    # 2. Mentor feed
    feed_src = config.PRODUCTION_DATA_DIR / 'mentor_feed.json'
    feed_dst = user_dir / 'mentor_feed.json'
    if not feed_dst.exists() and feed_src.exists():
        shutil.copy(feed_src, feed_dst)
        
    # 3. Presenters
    pres_src = config.DATA_DIR / 'presenters.csv'
    pres_dst = user_dir / 'presenters.csv'
    if not pres_dst.exists() and pres_src.exists():
        shutil.copy(pres_src, pres_dst)
        
    return user_dir

def is_valid_username(username: str) -> bool:
    """Validate username formats (e.g. email or standard names)."""
    return bool(re.match(r'^[a-zA-Z0-9_\-\.@]+$', username)) and len(username) >= 3

def signup_user(username, password) -> bool:
    """Register a new user."""
    username = username.strip().lower()
    if not username:
        st.error("Username cannot be empty.")
        return False
    if not is_valid_username(username):
        st.error("Username must be at least 3 characters and contain only letters, numbers, and symbols (@ . _ -).")
        return False
    if len(password) < 6:
        st.error("Password must be at least 6 characters.")
        return False
        
    users = load_users()
    if username in users:
        st.error("Username is already taken.")
        return False
        
    pwd_hash, salt = hash_password(password)
    from datetime import datetime
    users[username] = {
        "password_hash": pwd_hash,
        "salt": salt,
        "created_at": datetime.now().isoformat()
    }
    save_users(users)
    
    # Bootstrap user directory
    bootstrap_user_sandbox(username)
    return True

def login_user(username, password) -> bool:
    """Verify login credentials."""
    username = username.strip().lower()
    if not username or not password:
        st.error("Username and password cannot be empty.")
        return False
        
    users = load_users()
    if username not in users:
        st.error("Invalid username or password.")
        return False
        
    user_data = users[username]
    if verify_password(password, user_data["password_hash"], user_data["salt"]):
        st.session_state.authenticated = True
        st.session_state.username = username
        
        # Point data path dynamically to their sandbox
        st.session_state.data_path = config.PRODUCTION_DATA_DIR / 'users' / username
        return True
    else:
        st.error("Invalid username or password.")
        return False

def logout():
    """Clear authentication state and reset cached objects."""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.athlete_profile = None
    st.session_state.drills_df = None
    st.session_state.weekly_training_plan = None
    st.session_state.completion_log = None
    st.session_state.redirect_banner = None
    st.rerun()

def is_authenticated():
    """Check if the current session is authenticated."""
    if is_auth_disabled():
        return True
    return st.session_state.get("authenticated", False) and bool(st.session_state.get("username"))

def render_auth_sidebar():
    """Render the sidebar logged-in identity card and log out button."""
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
    """Render a premium glassmorphic centered Login & Sign Up screen."""
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
        
        /* Clean radio / toggles styling */
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
        
        st.markdown('<div class="login-header-text">⚽ Coach AI</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subheader-text">Player Development Platform</div>', unsafe_allow_html=True)
        
        # Tabs for login vs signup
        mode = st.radio(
            "Select Access Mode",
            ["Log In", "Create Account"],
            horizontal=True,
            label_visibility="collapsed",
            index=0 if st.session_state.auth_mode == "login" else 1,
            key="access_mode_toggle"
        )
        
        if mode == "Log In":
            st.session_state.auth_mode = "login"
        else:
            st.session_state.auth_mode = "signup"
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.session_state.auth_mode == "login":
            username = st.text_input("Username or Email", placeholder="e.g. coach_john", key="login_username")
            password = st.text_input("Password", type="password", placeholder="••••••••", key="login_password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Log In to Dashboard", use_container_width=True, type="primary", key="submit_login"):
                if login_user(username, password):
                    st.success("Successfully logged in! Redirecting...")
                    st.rerun()
        else:
            username = st.text_input("New Username or Email", placeholder="e.g. coach_john", key="signup_username")
            password = st.text_input("Password (min 6 characters)", type="password", placeholder="••••••••", key="signup_password")
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
    """Gate a page behind password authentication and sandbox isolation."""
    if is_auth_disabled():
        st.session_state.authenticated = True
        if "username" not in st.session_state or not st.session_state.username:
            st.session_state.username = "local_coach"
        if "data_path" not in st.session_state or not st.session_state.data_path:
            st.session_state.data_path = config.get_data_path()
        return True

    if st.session_state.get("authenticated", False) and st.session_state.get("username"):
        username = st.session_state.username
        user_dir = config.PRODUCTION_DATA_DIR / 'users' / username
        if not user_dir.exists():
            bootstrap_user_sandbox(username)
        st.session_state.data_path = user_dir
        
        render_auth_sidebar()
        return True
        
    render_login_screen()
    st.stop()
