"""Coach Onboarding - quick setup wizard"""
import streamlit as st
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import config
import data_loader
import session_state
import ui_components

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
st.write(f"**Practice:** {', '.join(days) or '—'} for {session_len} minutes")
st.write(f"**Style:** {play_style} | **Formation:** {formation}")
st.write(f"**Goals:** {', '.join(goals) or '—'}")

if st.button("Save & Continue", type="primary"):
    # Save to teams_df
    new_row = {
        "team_id": f"team_{len(teams_df)+1}",
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
    st.success("Team saved. You can generate your first practice now.")
    st.page_link("pages/2_Practice_Generator.py", label="Generate my first practice", icon="⚽")
