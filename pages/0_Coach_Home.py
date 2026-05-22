"""Player Development Platform - My Dashboard"""
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import importlib
import config
import data_loader
import session_state
import ui_components
import completion_tracker
import rrs_calculator

# Force reload of custom modules to clear Streamlit's running process cache
try:
    importlib.reload(config)
    importlib.reload(data_loader)
    importlib.reload(session_state)
    importlib.reload(ui_components)
    importlib.reload(completion_tracker)
    importlib.reload(rrs_calculator)
except Exception:
    pass

from auth import require_auth

# Page configuration
st.set_page_config(
    page_title="My Dashboard | Player AI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Enforce authentication
require_auth()

# Initialize session state
session_state.init_session_state()
if "data_path" not in st.session_state:
    st.session_state.data_path = config.get_data_path()

# Load profile details
athlete_profile = data_loader.load_athlete_profile(st.session_state.data_path)

# If no profile exists, route to Profile Setup
if not athlete_profile or not athlete_profile.get("name"):
    st.session_state.redirect_banner = "Please set up your Player Profile first to access your dashboard!"
    st.switch_page("pages/5_Team_Hub.py")
    st.stop()

# Store in session state
st.session_state.athlete_profile = athlete_profile

# Load weekly plan and completion log
plan = data_loader.load_weekly_training_plan(st.session_state.data_path)
completion_log = data_loader.load_completion_log(st.session_state.data_path)

# Calculate RRS
drills_df = st.session_state.get("drills_df")
rrs = rrs_calculator.calculate_rrs(
    athlete_profile,
    completion_log,
    drills_df,
    plan
)

# Render standard navigation
ui_components.render_nav(active_label="My Dashboard")

st.divider()

# Get stats
total_completed = completion_tracker.get_total_sessions_completed(st.session_state.data_path)
current_streak = completion_tracker.get_current_streak(st.session_state.data_path)

# Calculate weekly progress
completed_this_week = 0
total_this_week = 0
active_sessions = []

if plan:
    for week in plan.get("weeks", []):
        if week.get("week_number") == 1:
            active_sessions = week.get("sessions", [])
            total_this_week = len(active_sessions)
            completed_this_week = sum(1 for s in active_sessions if s.get("completed", False))

# Beautiful CSS for Premium Styling
st.markdown("""
<style>
.dashboard-header {
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
    color: white;
    border-radius: 12px;
    padding: 32px;
    margin-bottom: 24px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
.stat-card {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    text-align: center;
    transition: transform 0.2s;
}
.stat-card:hover {
    transform: translateY(-2px);
}
.stat-value {
    font-size: 36px;
    font-weight: 800;
    color: #1e3a8a;
    margin-bottom: 4px;
}
.stat-label {
    font-size: 13px;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
}
.session-row {
    background-color: #ffffff;
    border-radius: 8px;
    padding: 16px;
    border: 1px solid #e2e8f0;
    margin-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.session-title {
    font-size: 16px;
    font-weight: 700;
    color: #1e293b;
}
.session-meta {
    font-size: 13px;
    color: #64748b;
}
.status-badge-complete {
    background-color: #dcfce7;
    color: #166534;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
}
.status-badge-remaining {
    background-color: #f1f5f9;
    color: #475569;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
}
.rrs-locked-card {
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
    border-radius: 12px;
    padding: 32px;
    text-align: center;
    color: white;
    margin-bottom: 16px;
}
.rrs-locked-title {
    font-size: 22px;
    font-weight: 800;
    margin-bottom: 8px;
}
.rrs-locked-sub {
    font-size: 16px;
    opacity: 0.9;
    margin-bottom: 16px;
}
.rrs-locked-progress-label {
    font-size: 14px;
    font-weight: 600;
    opacity: 0.8;
}
.rrs-score-card {
    background: white;
    border-radius: 12px;
    padding: 28px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.07);
    text-align: center;
    height: 100%;
}
.rrs-label {
    font-size: 11px;
    font-weight: 700;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
}
.rrs-number {
    font-size: 72px;
    font-weight: 900;
    line-height: 1;
    margin-bottom: 8px;
}
.rrs-benchmark-label {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 8px;
}
.rrs-delta {
    font-size: 14px;
    font-weight: 600;
}
.milestone-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #3b82f6;
    border-radius: 8px;
    padding: 20px 24px;
    margin-top: 16px;
    margin-bottom: 16px;
}
.milestone-title {
    font-size: 16px;
    font-weight: 800;
    color: #1e293b;
    margin-bottom: 8px;
}
.milestone-sub {
    font-size: 14px;
    color: #475569;
    margin-bottom: 8px;
}
.milestone-actions {
    margin: 0;
    padding-left: 20px;
    color: #334155;
    font-size: 14px;
}
.milestone-actions li {
    margin-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)

# 1. Header Banner
player_name = athlete_profile.get("name", "Player")
focus_areas_str = ", ".join(athlete_profile.get("focus_areas", [])) or "None selected"
st.markdown(f"""
<div class="dashboard-header">
    <h1 style="margin:0 0 8px 0; color:white;">⚽ Welcome Back, {player_name}!</h1>
    <p style="margin:0; font-size:16px; opacity:0.9;">Playing Level: <strong>{athlete_profile.get('level')}</strong> | Target: <strong>{focus_areas_str}</strong></p>
</div>
""", unsafe_allow_html=True)

# 2. Stats Grid / RRS Metrics
if not rrs["unlocked"]:
    sessions_done = completion_tracker.get_total_sessions_completed(st.session_state.data_path)
    sessions_needed = 5
    progress_val = min(1.0, sessions_done / sessions_needed)

    st.markdown(f"""
    <div class="rrs-locked-card">
        <div class="rrs-locked-title">🎯 Recruit Readiness Score</div>
        <div class="rrs-locked-sub">
            Complete your first 5 sessions to unlock your score
        </div>
        <div class="rrs-locked-progress-label">
            {sessions_done} of {sessions_needed} sessions completed
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.progress(progress_val)
    st.caption("Most players see their first score after completing one full week of training.")
else:
    col_l, col_r = st.columns([3, 2])
    with col_l:
        benchmark = rrs["benchmark"]
        overall = rrs["overall"]
        delta = rrs["weekly_delta"]
        delta_str = f"▲ +{delta} this week" if delta > 0 else (
                    f"▼ {delta} this week" if delta < 0 else "No change this week")
        delta_color = "#10b981" if delta > 0 else ("#ef4444" if delta < 0 else "#64748b")

        st.markdown(f"""
        <div class="rrs-score-card">
            <div class="rrs-label">RECRUIT READINESS SCORE</div>
            <div class="rrs-number" style="color:{benchmark['current_color']}">
                {overall}
            </div>
            <div class="rrs-benchmark-label" style="color:{benchmark['current_color']}">
                {benchmark['current_label']}
            </div>
            <div class="rrs-delta" style="color:{delta_color}">{delta_str}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_r:
        # Keep streak + weekly progress but smaller, styled to match
        st.markdown(f"""
        <div class="stat-card" style="margin-bottom:12px;">
            <div class="stat-value" style="font-size:28px;">🔥 {current_streak}</div>
            <div class="stat-label" style="font-size:11px;">Day Streak</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="font-size:28px;">🎯 {completed_this_week}/{total_this_week}</div>
            <div class="stat-label" style="font-size:11px;">Weekly Progress</div>
        </div>
        """, unsafe_allow_html=True)
        
    # Next Milestone Card - always show when unlocked
    benchmark = rrs["benchmark"]
    if benchmark["next_label"]:
        actions_html = "".join(
            f'<li>{a}</li>' for a in rrs["next_actions"]
        )
        st.markdown(f"""
        <div class="milestone-card">
            <div class="milestone-title">
                🎯 Next Milestone: {benchmark['next_label']}
                ({benchmark['next_threshold']})
            </div>
            <div class="milestone-sub">
                You need <strong>{benchmark['points_needed']} more points</strong>.
                Focus on:
            </div>
            <ul class="milestone-actions">{actions_html}</ul>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.success("🏆 You've reached D1 Ready status. Elite level achieved.", icon="🏆")

st.write("")
st.write("")

# 3. Call To Action (Start Today's Session)
next_session = None
if active_sessions:
    for session in active_sessions:
        if not session.get("completed", False):
            next_session = session
            break

if next_session:
    st.subheader("🔥 Next Up")
    # Show attractive CTA panel
    cta_cols = st.columns([3, 1])
    with cta_cols[0]:
        st.info(f"💡 **Session {next_session['day_number']}** is waiting! Ready to build your skill category? Let's check the details, watch the video cues, and get to training.", icon="⚽")
    with cta_cols[1]:
        if st.button("🚀 Start Training", type="primary", use_container_width=True):
            st.switch_page("pages/2_Practice_Generator.py")
else:
    st.success("🎉 Incredible work! You've finished all your custom training sessions for this week. Enjoy your rest or head over to the **Drill Library** to practice solo!", icon="🎉")

st.divider()

# Mentor Feed teaser
feed = data_loader.load_mentor_feed(st.session_state.data_path)
latest_posts = feed.get("posts", [])[:2]  # show 2 most recent

if latest_posts:
    st.markdown("#### 🎙️ Latest from Your Mentors")
    teaser_cols = st.columns(len(latest_posts))

    for idx, post in enumerate(latest_posts):
        # Look up presenter
        presenter_name = ""
        presenters_df = st.session_state.get("presenters_df")
        if presenters_df is None:
            presenters_df = data_loader.load_presenters(st.session_state.data_path)
            st.session_state["presenters_df"] = presenters_df

        if presenters_df is not None:
            match = presenters_df[
                presenters_df["presenter_id"] ==
                post.get("presenter_id", "")
            ]
            if not match.empty:
                presenter_name = match.iloc[0].get("display_name", "")

        with teaser_cols[idx]:
            st.markdown(f"""
            <div style="background:white; border:1px solid #e2e8f0;
                        border-left:4px solid #3b82f6; border-radius:8px;
                        padding:14px; height:100%;">
                <div style="font-size:11px; font-weight:700; color:#3b82f6;
                            text-transform:uppercase; margin-bottom:6px;">
                    {presenter_name}
                </div>
                <div style="font-size:14px; font-weight:700; color:#0f172a;
                            line-height:1.4;">
                    {post.get("title", "")}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.write("")
    if st.button("View all mentor posts →", use_container_width=False):
        st.switch_page("pages/6_Mentor_Feed.py")
    st.write("")

st.divider()

# 4. Weekly Plan Overview
st.subheader("📅 Weekly Training Schedule")
if not active_sessions:
    st.info("No training schedule generated yet. Head to My Training Plan to generate one.")
else:
    for s in active_sessions:
        # Build drill names preview
        drills_list = s.get("drills", [])
        drill_names = [d.get("drill_name", "") for d in drills_list]
        drill_preview = " ➔ ".join(drill_names) if drill_names else "No drills selected"
        
        status_badge = '<span class="status-badge-complete">✅ Completed</span>' if s.get("completed") else '<span class="status-badge-remaining">⏳ Remaining</span>'
        
        st.markdown(f"""
        <div class="session-row">
            <div>
                <div class="session-title">Session {s.get('day_number')} - {s.get('duration_minutes')} Min Session</div>
                <div class="session-meta">{drill_preview}</div>
            </div>
            <div>
                {status_badge}
            </div>
        </div>
        """, unsafe_allow_html=True)
