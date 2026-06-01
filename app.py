"""Player AI - Main Bootstrapper"""
from pathlib import Path
import sys
from datetime import datetime
import streamlit as st

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import importlib
import config
import data_loader

# Force reload of custom modules to clear Streamlit's running process cache
try:
    importlib.reload(config)
    importlib.reload(data_loader)
except Exception:
    pass

import session_state
import ui_components
import training_plan_generator
from auth import require_auth

# Page configuration
st.set_page_config(
    page_title="Player AI",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Enforce authentication
require_auth()

# Verify Supabase connection (skip if auth is disabled for local dev)
import os as _os
if not _os.environ.get("COACH_AI_DISABLE_AUTH", "").strip().lower() in {"1", "true", "yes", "on"}:
    try:
        import db as _db
        _db.get_client()
    except Exception as _e:
        st.error(
            f"⚠️ Database connection failed. "
            f"Check that SUPABASE_URL and SUPABASE_KEY are set in "
            f"Streamlit Cloud secrets. Error: {_e}"
        )
        st.stop()

# Initialize session state variables
session_state.init_session_state()

if "data_path" not in st.session_state:
    st.session_state.data_path = config.get_data_path()

# Load drills into session state
if st.session_state.drills_df is None:
    st.session_state.drills_df = data_loader.load_drills(st.session_state.data_path)

if st.session_state.get("presenters_df") is None:
    st.session_state["presenters_df"] = data_loader.load_presenters(
        st.session_state.data_path
    )

# Load Athlete Profile JSON
athlete_profile = data_loader.load_athlete_profile(st.session_state.data_path)

# Check if profile exists and has a name
if not athlete_profile or not athlete_profile.get("name"):
    # If no athlete profile exists, set redirect banner and route to Profile Setup
    st.session_state.redirect_banner = "Welcome! Please set up your Player Profile first to generate your custom training plans."
    st.switch_page("pages/5_Team_Hub.py")
    st.stop()

# Store in session state
st.session_state.athlete_profile = athlete_profile

# Check if a plan exists or if it requires rollover (silent 7-day rollover check)
plan = data_loader.load_weekly_training_plan(st.session_state.data_path)
needs_generation = False

if not plan:
    needs_generation = True
else:
    generated_date_str = plan.get("generated_date")
    if not generated_date_str:
        needs_generation = True
    else:
        try:
            generated_date = datetime.fromisoformat(generated_date_str)
            days_elapsed = (datetime.now() - generated_date).days
            if days_elapsed >= 7:
                needs_generation = True
        except Exception:
            needs_generation = True

if needs_generation:
    # Auto-generate a fresh week silently and save it
    drills = st.session_state.drills_df.to_dict('records')
    new_plan = training_plan_generator.generate_training_plan(athlete_profile, drills)
    data_loader.save_weekly_training_plan(new_plan, st.session_state.data_path)
    plan = new_plan

# Store the plan in session state
st.session_state.weekly_training_plan = plan

# Load completion log
completion_log = data_loader.load_completion_log(st.session_state.data_path)
st.session_state.completion_log = completion_log

# Redirect to Dashboard page
st.switch_page("pages/0_Coach_Home.py")
