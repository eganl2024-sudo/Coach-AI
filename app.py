"""Soccer Practice Planner - Main Application"""
from pathlib import Path
import sys
import streamlit as st

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import config
import data_loader
import practice_history
import session_state
import session_state as ui_session
import ui_components

# Page configuration
st.set_page_config(
    page_title="Coach AI - Soccer Practice Planner",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

session_state.init_session_state()

# Initialize session state
if "data_path" not in st.session_state:
    st.session_state.data_path = config.get_data_path()

if st.session_state.drills_df is None:
    st.session_state.drills_df = data_loader.load_drills(st.session_state.data_path)
    st.session_state.drill_mtime = None

if st.session_state.teams_df is None:
    st.session_state.teams_df = data_loader.load_teams(st.session_state.data_path)

if st.session_state.templates is None:
    st.session_state.templates = data_loader.load_templates(st.session_state.data_path)

if st.session_state.drills_df.attrs.get("load_error"):
    st.error(st.session_state.drills_df.attrs["load_error"])
if st.session_state.teams_df.attrs.get("load_error"):
    st.error(st.session_state.teams_df.attrs["load_error"])

# Mode switch (sidebar) for devs
if config.is_dev():
    current_mode = ui_session.get_user_mode()
    st.sidebar.markdown("### Interface mode")
    selected_label = st.sidebar.radio(
        "Choose how to view the app:",
        options=["Coach view", "Developer view"],
        index=0 if current_mode == "coach" else 1,
        label_visibility="collapsed",
    )
    new_mode = "coach" if selected_label == "Coach view" else "developer"
    ui_session.set_user_mode(new_mode)
    st.sidebar.markdown(f"Mode: **{selected_label}**")
else:
    ui_session.set_user_mode("coach")
    st.sidebar.markdown("Mode: **Coach view**")

mode = "DEMO" if config.is_demo() else "PRODUCTION"
ui_indicator = "Coach Mode" if ui_session.is_coach_mode() else "Developer Mode"

ui_components.render_nav(active_label="Home")

st.caption(f"Data path: {st.session_state.get('data_path')} | {ui_indicator}")

st.divider()

# Main content
col_hero_left, col_hero_right = st.columns([2, 1])

with col_hero_left:
    st.title("Soccer Practice Planner")
    st.markdown("#### AI-powered planning for busy coaches")
    st.write(
        "Build balanced practices with intelligent drill selection, track session history, "
        "and grow your drill library all in one place."
    )

st.subheader("Team Focus")
session_state.render_team_selector(
    label="Active team",
    widget_key="team_selector_home",
    help_text="Switch teams here to update all pages of the app.",
)

with col_hero_right:
    st.metric("Drills Available", len(st.session_state.drills_df))
    st.metric(
        "Practice Sessions Saved",
        sum(
            1
            for path in Path(st.session_state.data_path).glob("practice_history_*.csv")
            if path.stat().st_size > 0
        ),
    )
    st.metric("Mode", mode)

health_entries = []
for label, df in [
    ("Drill library", st.session_state.drills_df),
    ("Team profiles", st.session_state.teams_df),
]:
    info = df.attrs.get("repair_info")
    if info:
        health_entries.append((label, info))
if any(info.get("was_repaired") for _, info in health_entries):
    st.warning(
        "Some CSV files were missing fields and were auto-repaired. "
        "See the Data Health panel below for details."
    )

st.divider()

st.subheader("Workflow Overview")
row1_col1, row1_col2, row1_col3 = st.columns(3)
row2_col1, row2_col2 = st.columns(2)


def feature_card(container, title, description, page_path):
    with container:
        st.page_link(page_path, label=title)
        st.write(description)


feature_card(
    row1_col1,
    "âš½ Generate Practice",
    "Create tonight's session and tweak drills.",
    "pages/2_Practice_Generator.py",
)
feature_card(
    row1_col2,
    "ðŸ‘¥ My Team",
    "Update team info, practice schedule, and play style.",
    "pages/5_Team_Hub.py",
)
feature_card(
    row1_col3,
    "Past Sessions",
    "See recent sessions and reuse favorites.",
    "pages/3_Practice_History.py",
)
feature_card(
    row2_col1,
    "Practice Cycle",
    "Generate multi-week cycles with modular/scripted mixes.",
    "pages/8_Practice_Cycle.py",
)
feature_card(
    row2_col2,
    "Add Drills",
    "Add single drills or bulk upload CSVs to expand your library.",
    "pages/4_Add_Drills.py",
)
if config.is_dev():
    feature_card(
        row2_col2,
        "Dev Diagnostics",
        "Inspect data, templates, scoring, and repairs.",
        "pages/13_Dev_Diagnostics.py",
    )

if st.session_state.selected_team:
    st.success(
        f"Ready to build for **{st.session_state.selected_team['team_name']}** "
        f"({st.session_state.selected_team['age_group']})"
    )
else:
    st.warning("Select a team in the sidebar to personalize your planning experience.")

# Get Started Checklist
has_drills = len(st.session_state.drills_df) > 0
history_count = sum(
    1
    for path in Path(st.session_state.data_path).glob("practice_history_*.csv")
    if path.stat().st_size > 0
)
has_history = history_count > 0
profile_status = session_state.get_team_profile_status()
team_profile_complete = profile_status["is_complete"]

if not (has_drills and has_history and team_profile_complete):
    st.divider()
    st.subheader("Get Started Checklist")

    def checklist_item(condition, text, link_path, link_label):
        status = "[x]" if condition else "[ ]"
        st.markdown(f"{status} {text}")
        if not condition:
            st.page_link(link_path, label=link_label)

    checklist_item(
        team_profile_complete,
        "Complete your team profile (play style, focus tags, injuries).",
        "pages/5_Team_Hub.py",
        "Go to Team Hub",
    )
    checklist_item(
        has_drills,
        "Add drills to your library.",
        "pages/4_Add_Drills.py",
        "Add Drills",
    )
    checklist_item(
        has_history,
        "Generate and save your first practice.",
        "pages/2_Practice_Generator.py",
        "Create a Session",
    )

# Footer
st.divider()
with st.expander("Data Health"):
    if health_entries:
        for label, info in health_entries:
            status = "Repaired" if info.get("was_repaired") else "OK"
            st.markdown(f"**{label}:** {status}")
            if info.get("was_repaired"):
                added = ", ".join(info.get("added_columns", [])) or "columns"
                st.caption(f"Added columns: {added}")
    if st.session_state.selected_team:
        team_id = st.session_state.selected_team.get("team_id")
        if team_id:
            try:
                history_df = practice_history.load_practice_history(
                    team_id,
                    st.session_state.data_path,
                    practice_history.get_history_mtime(
                        team_id, st.session_state.data_path
                    ),
                )
                report = practice_history.repair_history_report(
                    history_df, st.session_state.teams_df
                )
                st.caption(
                    f"History repairs - invalid dates: {report.get('invalid_dates',0)}, "
                    f"missing cols: {', '.join(report.get('missing_columns', [])) or 'none'}, "
                    f"orphaned sessions: {report.get('orphaned_sessions',0)}"
                )
            except Exception:
                st.caption("History repair summary unavailable.")
    else:
        st.write("No data issues detected in drills or team profiles.")
    st.caption("Practice History warnings appear on the Practice History page.")

st.divider()
st.caption("Built with Streamlit | AI-Powered Drill Selection")





