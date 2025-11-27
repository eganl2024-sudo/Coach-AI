"""Coach Home - dashboard landing for coaches."""
import sys
from pathlib import Path
import streamlit as st

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import config
import data_loader
import practice_history
import session_state
import ui_components

st.set_page_config(
    page_title="Coach Home",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state and core data
session_state.init_session_state()
data_path = st.session_state.get("data_path") or config.get_data_path()
st.session_state.data_path = data_path
if st.session_state.drills_df is None:
    st.session_state.drills_df = data_loader.load_drills(data_path)
if st.session_state.teams_df is None:
    st.session_state.teams_df = data_loader.load_teams(data_path)

ui_components.render_nav(active_label="Home")
st.divider()

st.title("Coach Dashboard")
st.caption("Start here to plan and review your sessions.")

teams_df = st.session_state.teams_df

# Empty-state: no teams yet
if teams_df is None or teams_df.empty:
    st.info("You don't have any teams set up yet.")
    st.page_link("pages/0_Coach_Onboarding.py", label="Create your first team")
    st.stop()

# Team selector and summary
selected_team = session_state.render_team_selector(
    label="Active team",
    widget_key="coach_home_team_selector",
    help_text="Pick a team to personalize focus and recommendations.",
)
if not selected_team:
    st.warning("Select a team above to get started.")
    st.stop()

team_id = selected_team.get("team_id")
team_name = selected_team.get("team_name", "Team")
age_group = selected_team.get("age_group", "")

# History summary
practice_count = 0
last_practice_date = None
history_df = None
if team_id:
    history_mtime = practice_history.get_history_mtime(team_id, data_path)
    history_df = practice_history.load_practice_history(team_id, data_path, history_mtime)
    practice_count = len(history_df) if history_df is not None else 0
    if practice_count:
        try:
            last_practice_date = practice_history.load_practice_history(team_id, data_path, history_mtime)['session_date'].max()
        except Exception:
            last_practice_date = None

with st.container():
    st.markdown(
        """
        <div style="padding: 10px 12px; background-color: #f6f8fa; border-radius: 8px; border: 1px solid #e5e7eb;">
        """,
        unsafe_allow_html=True,
    )
    summary_cols = st.columns(3)
    summary_cols[0].markdown("**⚽ Team**")
    summary_cols[0].markdown(f"<div style='font-size:20px; font-weight:600'>{team_name} {f'({age_group})' if age_group else ''}</div>", unsafe_allow_html=True)
    summary_cols[1].markdown("**Saved practices**")
    summary_cols[1].markdown(f"<div style='font-size:20px; font-weight:600'>{practice_count}</div>", unsafe_allow_html=True)
    summary_cols[2].markdown("**📅 Last practice**")
    summary_cols[2].markdown(
        f"<div style='font-size:20px; font-weight:600'>{str(last_practice_date.date()) if last_practice_date else 'None yet'}</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# Main CTA cards
st.subheader("Quick actions")
cta_items = [
    ("Generate practice", "Build today's session using your team profile and history.", "pages/2_Practice_Generator.py", "Generate"),
    ("Past sessions", "Review and reuse past sessions.", "pages/3_Practice_History.py", "Open history"),
    ("Team profile", "Edit formation, style, and season goals.", "pages/5_Team_Hub.py", "Edit team"),
    ("Drill library", "Browse and filter your drill collection.", "pages/1_Drill_Library.py", "Browse drills"),
]
cta_cols = st.columns(len(cta_items))
for col, (title, desc, page, btn_label) in zip(cta_cols, cta_items):
    with col:
        with st.container():
            st.markdown(f"**{title}**")
            st.caption(desc)
            if st.button(btn_label, use_container_width=True, key=f"cta_{title}"):
                st.switch_page(page)

st.divider()

# Focus overview for selected team
st.subheader("Recent focus & gaps")
if history_df is None or len(history_df) == 0:
    st.info("Once you've saved a few practices, we'll highlight which areas need more attention.")
else:
    try:
        focus = practice_history.compute_recent_focus(history_df, days=28, drills_df=st.session_state.drills_df)
        cat_minutes = focus.get("category_minutes", {})
        total = focus.get("total_minutes") or 0
        if total == 0 or not cat_minutes:
            st.info("No recent practices to analyze. Generate your next session to start tracking focus.")
        else:
            cat_sorted = sorted(cat_minutes.items(), key=lambda kv: kv[1], reverse=True)
            top = cat_sorted[0][0] if cat_sorted else None
            weak = cat_sorted[-1] if cat_sorted else None
            if top and weak:
                st.caption(f"Last 4 weeks: most time on **{top}**, least on **{weak[0]}**.")
            threshold = total * 0.10
            weak_categories = [cat for cat, mins in cat_minutes.items() if mins < threshold]
            if weak_categories:
                st.markdown("Under-focused areas:")
                for cat in weak_categories[:3]:
                    st.markdown(f"- `{cat}`")
                if st.button("Plan a session for weak areas", type="primary"):
                    session_state.set_focus_boost_attributes(weak_categories)
                    st.switch_page("pages/2_Practice_Generator.py")
            else:
                with st.container():
                    st.success("Balanced training", icon="✅")
                    st.caption("Training time looks evenly distributed across your main areas.")
    except Exception:
        st.info("Focus overview is unavailable right now.")

st.divider()

# Data health / repairs (coach-safe)
def _has_repairs(df):
    repairs = getattr(df, "attrs", {}).get("repairs")
    if not repairs:
        return False
    return any(repairs.get(key) for key in ("added_columns", "coerced_columns", "filled_values"))

coach_mode = config.DEFAULT_USER_MODE == "coach" or session_state.is_coach_mode()
drill_repairs = _has_repairs(st.session_state.drills_df)
team_repairs = _has_repairs(st.session_state.teams_df)
history_repairs = _has_repairs(history_df) if history_df is not None else False

if coach_mode and (drill_repairs or team_repairs or history_repairs):
    st.info("We fixed some data issues behind the scenes. Everything is safe to use. Detailed repair logs are available in dev mode.")
elif not coach_mode:
    # Dev mode: show quick link to diagnostics
    st.caption("Dev mode: See detailed repairs in Dev Diagnostics.")
    st.page_link("pages/13_Dev_Diagnostics.py", label="Open Dev Diagnostics")

st.caption("Looking for advanced tools? Turn on developer mode to access templates and diagnostics in the sidebar.")
