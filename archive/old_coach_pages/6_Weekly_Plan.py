"""Weekly Plan - Layer 1 hub for planning your week's practice sessions"""
import streamlit as st
import pandas as pd
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import config
import data_loader
import practice_history
import schedule
import session_state
import ui_components
from auth import require_auth

st.set_page_config(page_title="Weekly Plan", page_icon="📅", layout="wide")

require_auth()
ui_components.require_page_access("pages/6_Weekly_Plan.py")

ui_components.render_nav(active_label="📅 Weekly Plan")
st.divider()

st.title("📅 Weekly Plan")
st.caption("Plan your week in minutes. Generate, edit, and review sessions for each upcoming practice.")

# ============================================================================
# SESSION STATE SETUP
# ============================================================================
session_state.init_session_state()
if "data_path" not in st.session_state:
    st.session_state.data_path = config.get_data_path()

# Load teams and drills
if st.session_state.teams_df is None:
    st.session_state.teams_df = data_loader.load_teams(st.session_state.data_path)

if st.session_state.drills_df is None:
    st.session_state.drills_df = data_loader.load_drills(st.session_state.data_path)

# Initialize selected team
if st.session_state.selected_team is None and len(st.session_state.teams_df) > 0:
    st.session_state.selected_team = st.session_state.teams_df.iloc[0].to_dict()

# Handle team context from session state
current_team_id = st.session_state.get("current_team_id")
if current_team_id and st.session_state.teams_df is not None:
    matches = st.session_state.teams_df[st.session_state.teams_df["team_id"].astype(str) == str(current_team_id)]
    if not matches.empty:
        st.session_state.selected_team = matches.iloc[0].to_dict()

# Check if team is selected
if st.session_state.selected_team is None:
    st.error("No team selected.")
    if st.button("Go to Team Selection"):
        st.switch_page("pages/0_Coach_Home.py")
    st.stop()

team = st.session_state.selected_team
team_id = team.get("team_id")
team_name = team.get("team_name", "Team")

# ============================================================================
# WEEK SELECTOR
# ============================================================================
st.divider()

# Get current week boundaries
today = datetime.today().date()
week_start = today - timedelta(days=today.weekday())  # Monday
week_end = week_start + timedelta(days=6)  # Sunday

# Week navigation columns
col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    if st.button("⬅️ Previous Week", use_container_width=True):
        # Shift to previous week
        week_start = week_start - timedelta(days=7)
        week_end = week_start + timedelta(days=6)

with col2:
    # Show week range
    week_label = f"{week_start.strftime('%b %d')} – {week_end.strftime('%b %d, %Y')}"
    st.markdown(f"<div style='text-align: center; padding: 8px;'><strong>{week_label}</strong></div>", unsafe_allow_html=True)

with col3:
    if st.button("Next Week ➡️", use_container_width=True):
        # Shift to next week
        week_start = week_start + timedelta(days=7)
        week_end = week_start + timedelta(days=6)

st.divider()

# ============================================================================
# LOAD SCHEDULE AND SESSIONS
# ============================================================================
# Load team schedule
schedule_df = schedule.load_team_schedule(team_id, st.session_state.data_path)

# Convert event_date to datetime for comparison
if not schedule_df.empty:
    schedule_df["event_date_dt"] = pd.to_datetime(schedule_df["event_date"], errors="coerce")
else:
    schedule_df["event_date_dt"] = pd.NaT

# Filter to current week
week_events = schedule_df[
    (schedule_df["event_date_dt"] >= pd.Timestamp(week_start)) &
    (schedule_df["event_date_dt"] <= pd.Timestamp(week_end))
].copy()

# Sort by date and time
if not week_events.empty:
    week_events = week_events.sort_values(["event_date_dt", "start_time"], ascending=[True, True])

# Load saved sessions for this team
sessions_df = practice_history.load_sessions_for_team(st.session_state.data_path, team_id)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def safe_str(value) -> str:
    """Convert any value to a safe string."""
    if value is None:
        return ""
    try:
        if isinstance(value, float) and pd.isna(value):
            return ""
    except Exception:
        pass
    return str(value).strip()


def find_session_for_event(event_row, sessions_df):
    """
    Try to find a saved session for this event.
    Matches by event_id first, then by date + team_id.
    Returns (session_row, session_id) or (None, None).
    """
    if sessions_df.empty:
        return None, None
    
    # Try event_id match first
    event_id = safe_str(event_row.get("event_id", ""))
    if event_id:
        mask = sessions_df["event_id"].astype(str).str.strip() == str(event_id)
        matches = sessions_df[mask]
        if not matches.empty:
            return matches.iloc[0], matches.iloc[0].get("session_id")
    
    # Fallback: match by date + team_id
    try:
        event_date_str = safe_str(event_row.get("event_date", ""))
        event_date = pd.to_datetime(event_date_str, errors="coerce")
        if pd.notna(event_date):
            event_date_normalized = event_date.normalize()
            
            # Normalize session dates for comparison
            sessions_df_copy = sessions_df.copy()
            sessions_df_copy["session_date_normalized"] = pd.to_datetime(
                sessions_df_copy.get("session_date", []), errors="coerce"
            ).dt.normalize()
            
            mask = (
                (sessions_df_copy["session_date_normalized"] == event_date_normalized) &
                (sessions_df_copy["team_id"].astype(str) == str(team_id))
            )
            matches = sessions_df_copy[mask]
            if not matches.empty:
                return matches.iloc[0], matches.iloc[0].get("session_id")
    except Exception:
        pass
    
    return None, None


def format_event_date(date_str):
    """Format event date as readable string."""
    try:
        dt = pd.to_datetime(date_str)
        return dt.strftime("%a, %b %d")
    except Exception:
        return date_str


def format_event_time(time_str):
    """Format time as 12-hour with AM/PM."""
    if not time_str:
        return "—"
    time_str = safe_str(time_str).upper()
    
    # If already in 12-hour format, return as-is
    if "AM" in time_str or "PM" in time_str:
        return time_str
    
    # Try to parse 24-hour and convert
    try:
        dt = datetime.strptime(time_str, "%H:%M")
        return dt.strftime("%I:%M %p")
    except Exception:
        return time_str


# ============================================================================
# RENDER WEEK VIEW
# ============================================================================
if week_events.empty:
    st.info(f"No scheduled practices for the week of {week_label}.")
else:
    st.markdown(f"### {len(week_events)} session(s) this week")
    
    for idx, event_row in week_events.iterrows():
        event_id = safe_str(event_row.get("event_id", ""))
        event_date = safe_str(event_row.get("event_date", ""))
        start_time = safe_str(event_row.get("start_time", ""))
        event_type = safe_str(event_row.get("event_type", "Practice"))
        opponent = safe_str(event_row.get("opponent", ""))
        location = safe_str(event_row.get("location", ""))
        notes = safe_str(event_row.get("notes", ""))
        
        # Find matching session
        saved_session, session_id = find_session_for_event(event_row, sessions_df)
        is_planned = saved_session is not None
        
        # Format display strings
        date_display = format_event_date(event_date)
        time_display = format_event_time(start_time)
        event_label = event_type if event_type else "Practice"
        
        # Build card
        with st.container(border=True):
            # Header row: Date + Time + Type
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"**{date_display}** • {time_display}")
            with col2:
                status_badge = "✅ Planned" if is_planned else "⭕ Not Planned"
                st.markdown(f"*{status_badge}*")
            with col3:
                st.caption(event_label)
            
            # Event details
            details_parts = []
            if opponent:
                details_parts.append(f"vs {opponent}")
            if location:
                details_parts.append(f"@ {location}")
            
            if details_parts:
                st.caption(" | ".join(details_parts))
            
            # Session info if planned
            if is_planned and saved_session is not None:
                session_structure = safe_str(saved_session.get("session_structure", ""))
                if session_structure:
                    try:
                        import json
                        session_dict = json.loads(session_structure)
                        session_title = safe_str(session_dict.get("session_title", ""))
                        focus_areas = session_dict.get("config", {}).get("selected_categories", [])
                        duration = safe_str(session_dict.get("duration_minutes", ""))
                        
                        info_parts = []
                        if session_title:
                            info_parts.append(f"**{session_title}**")
                        if focus_areas:
                            if isinstance(focus_areas, list):
                                focus_str = " • ".join(focus_areas)
                            else:
                                focus_str = str(focus_areas)
                            info_parts.append(focus_str)
                        if duration:
                            info_parts.append(f"{duration} min")
                        
                        if info_parts:
                            st.write(" | ".join(info_parts))
                    except Exception:
                        pass
            
            # Action buttons
            button_col1, button_col2, button_col3 = st.columns(3)
            
            if is_planned:
                # Edit Session button
                with button_col1:
                    if st.button(
                        "✏️ Edit Session",
                        key=f"edit_{event_id or idx}",
                        use_container_width=True
                    ):
                        st.session_state.current_team_id = team_id
                        st.session_state.current_event_id = event_id
                        if session_id:
                            st.session_state.view_session_id = session_id
                        st.switch_page("pages/6_Edit_Practice.py")
                
                # View Details button
                with button_col2:
                    if st.button(
                        "👁️ View Details",
                        key=f"view_{event_id or idx}",
                        use_container_width=True
                    ):
                        st.session_state.current_team_id = team_id
                        st.session_state.current_event_id = event_id
                        if session_id:
                            st.session_state.view_session_id = session_id
                        st.switch_page("pages/Practice_Details.py")
            else:
                # Generate Session button
                with button_col1:
                    if st.button(
                        "🎯 Generate Session",
                        key=f"gen_{event_id or idx}",
                        use_container_width=True
                    ):
                        st.session_state.current_team_id = team_id
                        st.session_state.current_event_id = event_id
                        # Pass event details to generator
                        st.session_state.generator_event_date = event_date
                        st.session_state.generator_opponent = opponent
                        st.session_state.generator_location = location
                        st.session_state.generator_event_type = event_type
                        st.switch_page("pages/2_Practice_Generator.py")

st.divider()

# Footer
col1, col2 = st.columns([1, 4])
with col1:
    if st.button("← Back", use_container_width=True):
        st.switch_page("pages/5_Team_Hub.py")
