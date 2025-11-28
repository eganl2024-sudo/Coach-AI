"""Coach Onboarding - quick setup wizard"""
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, time, timedelta
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import config
import data_loader
import session_state
import ui_components
import team_profile
import schedule

st.set_page_config(page_title="Coach Onboarding", page_icon="🚀", layout="wide")

ui_components.render_nav(active_label="🚀 Coach Onboarding")
st.divider()

st.title("🚀 Quick Setup")
st.caption("Answer a few questions to set up your team, then generate your first practice.")

session_state.init_session_state()
if "data_path" not in st.session_state:
    st.session_state.data_path = config.get_data_path()

teams_df = data_loader.load_teams(st.session_state.data_path)

# Step 1: Team Basics
st.subheader("Step 1: Team Basics")
col_a, col_b, col_c = st.columns(3)
team_name = col_a.text_input("Team name", value="")
age_group = col_b.selectbox("Age group", options=["U8", "U10", "U12", "U14", "U16", "U18", "Adult"], index=3)
gender = col_c.selectbox("Gender", options=["Coed", "Girls", "Boys"], index=0)

# Step 2: Practice Schedule
st.subheader("Step 2: Practice Schedule")
days = st.multiselect("Days of week", options=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], default=["Tue", "Thu"])

col_time, col_duration = st.columns(2)
with col_time:
    default_start_time = st.time_input("Default practice start time", value=time(17, 0))
with col_duration:
    session_len = st.slider("Typical session length (min)", min_value=45, max_value=120, value=90, step=5)

# Step 3: Formation & Style
st.subheader("Step 3: Formation & Style")
formation = st.selectbox("Preferred formation", options=["4-3-3", "4-4-2", "3-5-2", "4-2-3-1", "4-1-4-1", "Custom"], index=0)
play_style = st.selectbox("Play style", options=["Possession", "Direct Play", "Balanced", "High Press", "Counter"], index=2)

# Step 4: Season Goals
st.subheader("Step 4: Season Goals")
goals = st.multiselect(
    "Pick a few goals",
    options=["First touch", "Build from back", "Defensive shape", "Finishing", "Pressing", "Fitness"],
    default=["First touch", "Pressing"]
)

# Step 5: Review & Save
st.subheader("Step 5: Review & Save")
st.write(f"**Team:** {team_name or '—'} | **Age:** {age_group} | **Gender:** {gender}")
st.write(f"**Practice:** {', '.join(days) or '—'} at {default_start_time.strftime('%I:%M %p')} for {session_len} minutes")
st.write(f"**Style:** {play_style} | **Formation:** {formation}")
st.write(f"**Goals:** {', '.join(goals) or '—'}")

if st.button("Save & Continue", type="primary"):
    # Save to teams_df
    new_team_id = f"team_{len(teams_df)+1}"
    new_row = {
        "team_id": new_team_id,
        "team_name": team_name or "My Team",
        "age_group": age_group,
        "skill_level": "intermediate",
        "typical_roster_size": 0,
        "notes": "",
        "created_date": "",
        "formation": formation,
        "play_style": play_style,
        "focus_areas": "|".join(goals),
        "practice_schedule": ", ".join(days),
        "season_objectives": ", ".join(goals),
        "gender": gender,
    }
    teams_df = pd.concat([teams_df, pd.DataFrame([new_row])], ignore_index=True)
    teams_df.to_csv(Path(st.session_state.data_path) / "team_profiles.csv", index=False)
    st.session_state.teams_df = teams_df
    st.session_state.selected_team = new_row

    # Save to team profile with practice schedule defaults
    data_path = Path(st.session_state.data_path)
    profile_data = {
        "practice_days": days,
        "default_practice_start_time": default_start_time.strftime("%H:%M"),
        "default_practice_duration": session_len,
        "play_style_identity": play_style,
        "season_objectives": ", ".join(goals),
    }
    team_profile.save_team_profile(data_path, new_team_id, profile_data)

    # Seed the schedule with future practices (next 6 weeks)
    try:
        existing_schedule = schedule.load_team_schedule(new_team_id, data_path)
        today = pd.Timestamp.today().normalize()
        future_practices = existing_schedule[
            (pd.to_datetime(existing_schedule.get("event_date", ""), errors="coerce") >= today) &
            (existing_schedule.get("event_type", "").astype(str).str.lower().isin(["practice", "film", "lift", "recovery", "walkthrough"]))
        ] if not existing_schedule.empty else pd.DataFrame()

        if future_practices.empty:
            # No future practices exist, seed the schedule
            schedule_rows = []

            # Generate practices for the next 6 weeks
            for week in range(6):
                week_start = today + timedelta(days=week * 7)
                for day_name in days:
                    day_map = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
                    target_day = day_map.get(day_name, 0)

                    # Find the date of this weekday in the current week
                    current_weekday = week_start.weekday()
                    days_offset = (target_day - current_weekday) % 7
                    practice_date = week_start + timedelta(days=days_offset)

                    # Only add if it's in the future
                    if practice_date >= today:
                        schedule_rows.append({
                            "event_date": practice_date.strftime("%Y-%m-%d"),
                            "start_time": default_start_time.strftime("%I:%M %p"),
                            "end_time": (datetime.combine(practice_date.date(), default_start_time) + timedelta(minutes=session_len)).strftime("%I:%M %p") if default_start_time else "",
                            "event_type": "Practice",
                            "opponent": "",
                            "location": "",
                            "notes": "",
                        })

            if schedule_rows:
                new_schedule_df = pd.DataFrame(schedule_rows)
                new_schedule_df.insert(0, "team_id", new_team_id)
                schedule.save_team_schedule(data_path, new_team_id, new_schedule_df)
    except Exception as e:
        st.warning(f"Could not seed schedule: {e}")

    st.success("Team saved. You can generate your first practice now.")
    st.page_link("pages/2_Practice_Generator.py", label="Generate my first practice", icon="⚽")
