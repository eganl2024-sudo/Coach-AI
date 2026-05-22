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
from auth import require_auth

st.set_page_config(page_title="Coach Onboarding", page_icon="🚀", layout="wide")

require_auth()

ui_components.render_nav(active_label="🚀 Coach Onboarding")
st.divider()

# Add anchor at top for jump-to-top functionality
st.markdown("<div id='top'></div>", unsafe_allow_html=True)

st.title("🚀 Quick Setup")
st.caption("Answer a few questions to set up your team, then generate your first practice.")

# PHASE 2: Setup Mode Toggle
setup_mode = st.radio(
    "Choose your setup mode:",
    options=["⚡ Quick Mode (30 seconds)", "📋 Full Mode (2 minutes)"],
    index=0,
    horizontal=True,
    help="Quick Mode: Just the essentials to get started. Full Mode: Customize everything."
)
is_quick_mode = "Quick" in setup_mode

if is_quick_mode:
    st.info("💡 **Quick Mode**: We'll set smart defaults. You can customize later in Team Hub!")
else:
    st.info("📝 **Full Mode**: Customize all team settings now for better practice recommendations.")

st.markdown("---")

# Add anchor for save button at bottom
st.markdown("<div id='save-section'></div>", unsafe_allow_html=True)

# Scroll to save button at top (only show in full mode)
if not is_quick_mode:
    col_scroll_btn, col_spacer = st.columns([1, 3])
    with col_scroll_btn:
        st.markdown("""
        <a href="#save-section" style="
            display: inline-block;
            padding: 0.5rem 1rem;
            background-color: #10b981;
            color: white;
            text-decoration: none;
            border-radius: 0.375rem;
            font-weight: 500;
            text-align: center;
            margin-bottom: 1rem;
        ">⬇ Skip to Save Button</a>
        """, unsafe_allow_html=True)

session_state.init_session_state()
if "data_path" not in st.session_state:
    st.session_state.data_path = config.get_data_path()

mode = st.session_state.get("quick_setup_mode", "new_team")
edit_team_id = st.session_state.get("quick_setup_team_id")

teams_df = data_loader.load_teams(st.session_state.data_path)
existing_team = None
if mode == "edit_defaults" and edit_team_id is not None and "team_id" in teams_df.columns:
    matches = teams_df[teams_df["team_id"].astype(str) == str(edit_team_id)]
    if not matches.empty:
        existing_team = matches.iloc[0].to_dict()

def _clean(value, default=""):
    if value is None:
        return default
    if isinstance(value, float) and pd.isna(value):
        return default
    return str(value).strip() or default

# Prefill helpers
team_name_default = _clean(existing_team.get("team_name")) if existing_team else ""
age_options = ["U8", "U10", "U12", "U14", "U16", "U18", "Adult"]
age_default = _clean(existing_team.get("age_group")) if existing_team else ""
age_index = age_options.index(age_default) if age_default in age_options else 3
gender_options = ["Coed", "Girls", "Boys"]
gender_default = _clean(existing_team.get("gender")) if existing_team else ""
gender_index = gender_options.index(gender_default) if gender_default in gender_options else 0

practice_days_default = []
if existing_team:
    raw_schedule = _clean(existing_team.get("practice_schedule"))
    if raw_schedule:
        practice_days_default = [d.strip() for d in raw_schedule.split(",") if d.strip()]

time_default = time(17, 0)
if existing_team:
    raw_time = _clean(existing_team.get("default_practice_start_time"))
    if raw_time:
        try:
            parsed = datetime.strptime(raw_time, "%H:%M").time()
        except Exception:
            try:
                parsed = datetime.strptime(raw_time, "%I:%M %p").time()
            except Exception:
                parsed = None
        if parsed:
            time_default = parsed

session_len_default = 90
if existing_team:
    try:
        session_len_default = int(existing_team.get("default_practice_duration", session_len_default))
    except Exception:
        pass

formation_options = ["4-3-3", "4-4-2", "3-5-2", "4-2-3-1", "4-1-4-1", "Custom"]
formation_default = _clean(existing_team.get("formation")) if existing_team else ""
formation_index = formation_options.index(formation_default) if formation_default in formation_options else 0

play_style_options = ["Possession", "Direct Play", "Balanced", "High Press", "Counter"]
play_style_default = _clean(existing_team.get("play_style")) if existing_team else ""
play_style_index = play_style_options.index(play_style_default) if play_style_default in play_style_options else 2

focus_tags_default = []
if existing_team:
    raw_focus = _clean(existing_team.get("focus_tags")) or _clean(existing_team.get("focus_areas"))
    if raw_focus:
        delimiter = "," if "," in raw_focus else "|"
        focus_tags_default = [t.strip() for t in raw_focus.split(delimiter) if t.strip()]

# Progress indicator
st.progress(0.0, text="Setup Progress: 0%")

# Step 1: Team Basics
st.subheader("Step 1: Team Basics")
col_a, col_b, col_c = st.columns(3)
team_name = col_a.text_input(
    "Team name", 
    value=team_name_default,
    help="⚽ What's your team called? (e.g., 'U12 Eagles', 'Thunder FC')"
)
age_group = col_b.selectbox(
    "Age group", 
    options=age_options, 
    index=age_index,
    help="🎯 Select the age category your team plays in"
)
gender = col_c.selectbox(
    "Gender", 
    options=gender_options, 
    index=gender_index,
    help="👥 Team composition (Coed = mixed gender)"
)

st.markdown("---")  # Visual separator

# Progress indicator
st.progress(0.25, text="Setup Progress: 25%")

# Step 2: Practice Schedule
st.subheader("Step 2: Practice Schedule")
days = st.multiselect(
    "Days of week",
    options=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    default=practice_days_default or ["Tue", "Thu"],
    help="📅 Which days does your team typically practice?"
)

col_time, col_duration = st.columns(2)
with col_time:
    default_start_time = st.time_input(
        "Default practice start time", 
        value=time_default,
        help="⏰ What time do practices usually start?"
    )
with col_duration:
    session_len = st.slider(
        "Typical session length (min)", 
        min_value=45, 
        max_value=120, 
        value=session_len_default, 
        step=5,
        help="⏱️ How long are your practices? (60-90 min is typical)"
    )

st.markdown("---")  # Visual separator

# Progress indicator
st.progress(0.5, text="Setup Progress: 50%")

# Step 3: Formation & Style
st.subheader("Step 3: Formation & Style")
formation = st.selectbox(
    "Preferred formation", 
    options=formation_options, 
    index=formation_index,
    help="⚽ Your team's typical formation on the field (e.g., 4-3-3 = 4 defenders, 3 midfielders, 3 forwards)"
)
play_style = st.selectbox(
    "Play style", 
    options=play_style_options, 
    index=play_style_index,
    help="🎯 How your team typically plays: Possession = keep the ball, Direct = quick attacks, High Press = pressure opponents"
)

st.markdown("---")  # Visual separator

# Progress indicator
st.progress(0.75, text="Setup Progress: 75%")

# Step 4: Season Goals
st.subheader("Step 4: Season Goals")
goal_options = ["First touch", "Build from back", "Defensive shape", "Finishing", "Pressing", "Fitness"]
for tag in focus_tags_default:
    if tag not in goal_options:
        goal_options.append(tag)
goals = st.multiselect(
    "Pick a few goals",
    options=goal_options,
    default=focus_tags_default or ["First touch", "Pressing"],
    help="🎯 Select 2-4 skills your team needs to work on this season. Coach AI will prioritize drills that match these goals!"
)

st.markdown("---")  # Visual separator

# Progress indicator
st.progress(1.0, text="Setup Progress: 100% - Ready to Save!")

# Save section anchor
st.markdown("<div id='save-section'></div>", unsafe_allow_html=True)

# Step 5: Review & Save
st.subheader("Step 5: Review & Save")

# Use columns for better layout
col1, col2 = st.columns(2)
with col1:
    st.write("**Team Information:**")
    st.write(f"• Name: {team_name or '—'}")
    st.write(f"• Age Group: {age_group}")
    st.write(f"• Gender: {gender}")
    st.write(f"")
    st.write("**Play Style:**")
    st.write(f"• Formation: {formation}")
    st.write(f"• Style: {play_style}")
    
with col2:
    st.write("**Practice Schedule:**")
    st.write(f"• Days: {', '.join(days) or '—'}")
    st.write(f"• Time: {default_start_time.strftime('%I:%M %p')}")
    st.write(f"• Duration: {session_len} minutes")
    st.write(f"")
    st.write("**Season Goals:**")
    st.write(f"• {', '.join(goals) or '—'}")

# Jump to top and help buttons
st.markdown("""
<style>
.jump-top {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 999;
    font-size: 18px;
    border: none;
    outline: none;
    background-color: #10b981;
    color: white;
    cursor: pointer;
    padding: 15px;
    border-radius: 50%;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    text-decoration: none;
    display: flex;
    align-items: center;
    justify-content: center;
}
.jump-top:hover {
    background-color: #059669;
}
</style>
<a href="#top" class="jump-top" title="Back to top">↑</a>
""", unsafe_allow_html=True)

# Progress summary before save button
st.info("📋 Review your information above, then click Save & Continue to generate your first practice!")

if st.button("Save & Continue", type="primary"):
    existing_team_id = None
    if mode == "edit_defaults" and existing_team is not None:
        existing_team_id = existing_team.get("team_id")
    else:
        existing_team_id = st.session_state.get("current_team_id")

    focus_tags_value = ",".join(goals)
    focus_areas_value = "|".join(goals)

    team_row = {
        "team_id": existing_team_id,
        "team_name": team_name or "My Team",
        "age_group": age_group,
        "skill_level": existing_team.get("skill_level", "intermediate") if existing_team else "intermediate",
        "typical_roster_size": existing_team.get("typical_roster_size", 0) if existing_team else 0,
        "notes": existing_team.get("notes", "") if existing_team else "",
        "created_date": existing_team.get("created_date", "") if existing_team else "",
        "formation": formation,
        "play_style": play_style,
        "focus_tags": focus_tags_value,
        "focus_areas": focus_areas_value,
        "practice_schedule": ", ".join(days),
        "season_objectives": ", ".join(goals),
        "gender": gender,
        "default_practice_start_time": default_start_time.strftime("%H:%M"),
        "default_practice_duration": session_len,
    }

    upserted = data_loader.upsert_team_profile(team_row, st.session_state.data_path)
    teams_df = data_loader.load_teams(st.session_state.data_path)
    st.session_state.teams_df = teams_df
    refreshed = teams_df[teams_df["team_id"].astype(str) == str(upserted.get("team_id"))]
    st.session_state.selected_team = refreshed.iloc[0].to_dict() if not refreshed.empty else upserted
    st.session_state.current_team_id = upserted.get("team_id")

    # Save to team profile with practice schedule defaults
    data_path = Path(st.session_state.data_path)
    profile_data = {
        "practice_days": days,
        "default_practice_start_time": default_start_time.strftime("%H:%M"),
        "default_practice_duration": session_len,
        "play_style_identity": play_style,
        "season_objectives": ", ".join(goals),
        "focus_tags": goals,
    }
    team_profile.save_team_profile(data_path, st.session_state.current_team_id, profile_data)

    # Seed or Update the schedule with future practices (next 6 weeks)
    try:
        existing_schedule = schedule.load_team_schedule(st.session_state.current_team_id, data_path)
        today = pd.Timestamp.today().normalize()
        
        future_mask = (pd.to_datetime(existing_schedule.get("event_date", ""), errors="coerce") >= today)
        kept_events = existing_schedule[~future_mask].to_dict('records')
        
        future_events = existing_schedule[future_mask]
        
        for _, row in future_events.iterrows():
            etype = str(row.get("event_type", "")).lower()
            has_content = str(row.get("opponent", "")) or str(row.get("notes", ""))
            if "game" in etype or "match" in etype or has_content:
                kept_events.append(row.to_dict())
                
        new_practices = []
        for week in range(6):
            week_start = today + timedelta(days=week * 7)
            for day_name in days:
                day_map = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
                target_day = day_map.get(day_name, 0)

                current_weekday = week_start.weekday()
                days_offset = (target_day - current_weekday) % 7
                if days_offset < 0: days_offset += 7
                
                monday_of_week = week_start - timedelta(days=week_start.weekday())
                practice_date = monday_of_week + timedelta(days=target_day)
                
                if practice_date < today:
                    practice_date += timedelta(days=7)
                    if practice_date < today:
                        continue 

                schedule_rows_entry = {
                    "event_date": practice_date.strftime("%Y-%m-%d"),
                    "start_time": default_start_time.strftime("%I:%M %p"),
                    "end_time": (datetime.combine(practice_date.date(), default_start_time) + timedelta(minutes=session_len)).strftime("%I:%M %p") if default_start_time else "",
                    "event_type": "Practice",
                    "opponent": "",
                    "location": "Training Field",
                    "notes": "",
                }
                new_practices.append(schedule_rows_entry)

        final_rows = kept_events + new_practices
        
        if final_rows:
            new_schedule_df = pd.DataFrame(final_rows)
            new_schedule_df["team_id"] = st.session_state.current_team_id
            schedule.save_team_schedule(data_path, st.session_state.current_team_id, new_schedule_df)
            
    except Exception as e:
        st.warning(f"Could not update schedule: {e}")

    # ✅ FIX: Set flag to show success state and force rerun
    st.session_state.onboarding_complete = True
    st.rerun()

# ✅ FIX: Show success message and button OUTSIDE the save button's if block
if st.session_state.get("onboarding_complete", False):
    st.success("✅ Team saved successfully! Ready to generate your first practice.")
    st.markdown("---")
    
    # This button will now actually work
    if st.button(
        "⚽ Generate my first practice", 
        key="generate_first_practice_cta", 
        type="primary",
        use_container_width=True
    ):
        st.switch_page("pages/2_Practice_Generator.py")
