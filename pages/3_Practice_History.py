"""Player Development Platform - My Progress"""
import streamlit as st
import pandas as pd
import json
import sys
from pathlib import Path
from datetime import datetime, date

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
    page_title="My Progress - Player Development Platform",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Enforce authentication
require_auth()

# Initialize session state
session_state.init_session_state()
if "data_path" not in st.session_state:
    st.session_state.data_path = config.get_data_path()

# Render standard navigation
ui_components.render_nav(active_label="My Progress")

st.divider()

# Load profile and logs
athlete_profile = data_loader.load_athlete_profile(st.session_state.data_path) or {}
completion_log = data_loader.load_completion_log(st.session_state.data_path) or {}
plan = data_loader.load_weekly_training_plan(st.session_state.data_path)

drills_df = st.session_state.get("drills_df")
rrs = rrs_calculator.calculate_rrs(
    athlete_profile, completion_log, drills_df, plan
)
rrs_history = data_loader.load_rrs_history(st.session_state.data_path)

if not athlete_profile or not athlete_profile.get("name"):
    st.warning("Please complete your Profile Setup first to begin tracking progress!", icon="⚠️")
    if st.button("Set Up Profile Now"):
        st.switch_page("pages/5_Team_Hub.py")
    st.stop()

st.title("📅 My Progress")
st.write("Track your training metrics, keep your active streaks going, and view your completed session history.")

# Beautiful CSS for Premium Styling
st.markdown("""
<style>
.metric-container {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 24px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    text-align: center;
    margin-bottom: 16px;
}
.metric-value-huge {
    font-size: 48px;
    font-weight: 800;
    color: #1d4ed8;
    margin-bottom: 8px;
}
.metric-title-sub {
    font-size: 14px;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
}
.timeline-card {
    background-color: #ffffff;
    border-left: 5px solid #10b981;
    border-radius: 8px;
    padding: 16px;
    border-top: 1px solid #e2e8f0;
    border-right: 1px solid #e2e8f0;
    border-bottom: 1px solid #e2e8f0;
    margin-bottom: 12px;
}
.timeline-date {
    font-size: 12px;
    font-weight: 700;
    color: #64748b;
}
.timeline-title {
    font-size: 16px;
    font-weight: 800;
    color: #1e293b;
    margin: 4px 0;
}
.timeline-desc {
    font-size: 14px;
    color: #475569;
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
</style>
""", unsafe_allow_html=True)

# Fetch stats from completion tracker
total_completed = completion_tracker.get_total_sessions_completed(st.session_state.data_path)
current_streak = completion_tracker.get_current_streak(st.session_state.data_path)

# Weekly progression metrics
completed_this_week = 0
total_this_week = 0
active_sessions = []
if plan:
    for week in plan.get("weeks", []):
        if week.get("week_number") == 1:
            active_sessions = week.get("sessions", [])
            total_this_week = len(active_sessions)
            completed_this_week = sum(1 for s in active_sessions if s.get("completed", False))

# Stats Grid / RRS Score Summary Row
if not rrs["unlocked"]:
    sessions_done = total_completed
    sessions_needed = 5
    progress_val = min(1.0, sessions_done / sessions_needed)

    st.markdown(f"""
    <div class="rrs-locked-card">
        <div class="rrs-locked-title">🎯 Recruit Readiness Score Locked</div>
        <div class="rrs-locked-sub">
            Complete at least 5 sessions to unlock your proprietary Recruit Readiness Score (RRS) & advanced analytics.
        </div>
        <div class="rrs-locked-progress-label">
            {sessions_done} of {sessions_needed} sessions completed
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.progress(progress_val)
    st.caption("Unlock advanced skill analysis, historical tracking, and development actions by completing scheduled sessions.")
    
    # Weekly Goal visual bar
    if total_this_week > 0:
        st.write(f"**This Week's Goal Progress ({completed_this_week} of {total_this_week} sessions completed):**")
        st.progress(completed_this_week / total_this_week)
else:
    # Section 1: Score Summary row
    benchmark = rrs["benchmark"]
    overall = rrs["overall"]
    delta = rrs["weekly_delta"]
    delta_str = f"▲ +{delta} this week" if delta > 0 else (
                f"▼ {delta} this week" if delta < 0 else "0 change this week")
    delta_color = "#10b981" if delta > 0 else ("#ef4444" if delta < 0 else "#64748b")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value-huge" style="color: {benchmark['current_color']}">{overall}</div>
            <div class="metric-title-sub">Recruit Readiness Score</div>
            <div style="font-weight: 700; color: {benchmark['current_color']}; font-size: 14px; margin-top: 4px;">{benchmark['current_label']}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value-huge">🔥 {current_streak}</div>
            <div class="metric-title-sub">Active Day Streak</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value-huge">🏆 {total_completed}</div>
            <div class="metric-title-sub">Total Completed Sessions</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value-huge" style="color: {delta_color}">{delta_str}</div>
            <div class="metric-title-sub">Weekly Score Delta</div>
        </div>
        """, unsafe_allow_html=True)

    # Weekly Goal visual bar
    if total_this_week > 0:
        st.write(f"**This Week's Goal Progress ({completed_this_week} of {total_this_week} sessions completed):**")
        st.progress(completed_this_week / total_this_week)

    st.divider()

    # Section 2: Charts (History Chart & Plotly Skills Radar Chart)
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.subheader("📈 Score History")
        snapshots = rrs_history.get("snapshots", [])
        if len(snapshots) >= 2:
            history_df = pd.DataFrame(snapshots)
            history_df["Date"] = pd.to_datetime(history_df["date"])
            history_df = history_df.sort_values("Date")
            history_df["Display Date"] = history_df["Date"].dt.strftime("%b %d")
            chart_data = history_df.set_index("Display Date")[["overall"]]
            chart_data.columns = ["RRS Score"]
            st.line_chart(chart_data)
        else:
            st.info("📈 Score history tracking will appear here as you complete more daily sessions. At least 2 completed sessions on different days are required to render the history trend line.")
            
    with chart_col2:
        st.subheader("🕸️ Skills Radar")
        import plotly.graph_objects as go
        
        # Extract scores
        pillars_dict = rrs["pillars"]
        consistency = pillars_dict["consistency"]["score"]
        volume = pillars_dict["volume"]["score"]
        coverage = pillars_dict["coverage"]["score"]
        progression = pillars_dict["progression"]["score"]

        categories = ["Consistency", "Volume", "Coverage", "Progression"]
        categories_closed = categories + [categories[0]]
        r_current = [consistency, volume, coverage, progression, consistency]

        # Target level threshold
        next_threshold = rrs["benchmark"]["next_threshold"]
        target_val = next_threshold if next_threshold is not None else 88
        r_target = [target_val] * 5

        fig = go.Figure()

        # Trace 1: Current Score
        fig.add_trace(go.Scatterpolar(
            r=r_current,
            theta=categories_closed,
            fill="toself",
            fillcolor="rgba(59, 130, 246, 0.2)",
            line=dict(color="#3b82f6"),
            name="Your Score"
        ))

        # Trace 2: Target Level
        fig.add_trace(go.Scatterpolar(
            r=r_target,
            theta=categories_closed,
            fill=None,
            mode="lines",
            line=dict(color="#cbd5e1", dash="dot", width=2),
            name="Target Level"
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    gridcolor="#e2e8f0"
                ),
                angularaxis=dict(
                    gridcolor="#e2e8f0"
                ),
                bgcolor="rgba(0,0,0,0)"
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            margin=dict(l=40, r=40, t=20, b=40),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=320,
        )
        
        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"responsive": True}
        )

    st.divider()

    # Section 3: Four pillar metric cards with bottom borders
    st.subheader("⚡ Recruit Readiness Pillars")
    p_cols = st.columns(4)
    pillar_keys = [
        ("consistency", "Consistency", "30%", "Consistency indicates your weekly training habit regularity (last 4 weeks)."),
        ("volume", "Volume", "20%", "Volume measures your total session completions compared to active weeks."),
        ("coverage", "Coverage", "25%", "Coverage tracks how well you train your stated focus areas (last 14 days)."),
        ("progression", "Progression", "25%", "Progression measures whether your drill difficulty matches playing level expectations.")
    ]

    for idx, (key, name, weight, tooltip) in enumerate(pillar_keys):
        score = rrs["pillars"][key]["score"]
        
        # Determine color by health
        if score >= 70:
            health_color = "#22c55e" # Green
            health_label = "Strong"
        elif score >= 45:
            health_color = "#eab308" # Amber
            health_label = "Moderate"
        else:
            health_color = "#ef4444" # Red
            health_label = "Needs Focus"
            
        with p_cols[idx]:
            st.markdown(f"""
            <div class="metric-container" style="border-bottom: 5px solid {health_color}; margin-bottom: 24px; position: relative;">
                <div style="font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">{name} (w: {weight})</div>
                <div style="font-size: 32px; font-weight: 800; color: #1e293b; line-height: 1.2;">{score}</div>
                <div style="font-size: 12px; font-weight: 700; color: {health_color}; margin-top: 4px;">{health_label}</div>
            </div>
            """, unsafe_allow_html=True)
            st.caption(f"_{tooltip}_")

st.divider()

# Left panel for Timeline and Right panel for Profile summary
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📋 Session Completion History")
    
    completions = completion_log.get("completions", [])
    
    if not completions:
        st.info("No training sessions completed yet. Head to your Training Plan and mark your first session complete to start logging history!")
        if st.button("Open My Training Plan", type="primary"):
            st.switch_page("pages/2_Practice_Generator.py")
    else:
        # Display completions in reverse chronological order
        sorted_completions = sorted(completions, key=lambda x: x.get("timestamp", ""), reverse=True)
        
        for entry in sorted_completions:
            # Format date beautifully
            ts_str = entry.get("timestamp", "")
            formatted_date = ""
            if ts_str:
                try:
                    dt = datetime.fromisoformat(ts_str)
                    formatted_date = dt.strftime("%A, %b %d, %Y • %I:%M %p")
                except ValueError:
                    formatted_date = entry.get("date", "")
            else:
                formatted_date = entry.get("date", "")
                
            week = entry.get("week", 1)
            day = entry.get("day", 1)
            
            # Find the drill titles for this session
            drill_titles_str = "Custom Practice Workout"
            session_drills = []
            if plan:
                for w in plan.get("weeks", []):
                    if w.get("week_number") == week:
                        for s in w.get("sessions", []):
                            if s.get("day_number") == day:
                                session_drills = s.get("drills", [])
                                drill_names = [d.get("drill_name", "") for d in session_drills]
                                if drill_names:
                                    drill_titles_str = " ➔ ".join(drill_names)
                                break
                                
            # Calculate dynamic contributed pillars
            contributed = ["Consistency", "Volume"]
            focus_areas = athlete_profile.get("focus_areas", [])
            has_coverage = False
            has_progression = False
            
            for sd in session_drills:
                name = sd.get("drill_name", "")
                d_info = rrs_calculator._get_drill_info(name, drills_df)
                if d_info:
                    # Coverage check
                    cat = str(d_info.get("skill_category", "")).lower()
                    tags = str(d_info.get("tags", "")).lower()
                    for fa in focus_areas:
                        if fa.lower() in cat or fa.lower() in tags:
                            has_coverage = True
                            break
                            
                    # Progression check
                    level = athlete_profile.get("level", "Recreational")
                    if level == "Recreational":
                        expected_min = 1
                    elif level == "Competitive Club":
                        expected_min = 2
                    elif level == "Academy/Select":
                        expected_min = 3
                    else:
                        expected_min = 1
                        
                    diff = str(d_info.get("difficulty", "intermediate")).lower().strip()
                    if diff in rrs_calculator.TIER_VALUES:
                        if rrs_calculator.TIER_VALUES[diff] >= expected_min:
                            has_progression = True
            
            if has_coverage:
                contributed.append("Coverage")
            if has_progression:
                contributed.append("Progression")
                
            contributed_str = ", ".join(contributed)
            
            st.markdown(f"""
            <div class="timeline-card">
                <div class="timeline-date">🗓️ {formatted_date}</div>
                <div class="timeline-title">Week {week}, Session {day}</div>
                <div class="timeline-desc" style="margin-bottom: 8px;"><strong>Completed Drills:</strong> {drill_titles_str}</div>
                <div style="font-size: 13px; font-weight: 700; color: #1e3a8a;">💪 Contributed to: <span style="font-weight: 600; color: #475569;">{contributed_str}</span></div>
            </div>
            """, unsafe_allow_html=True)


with col_right:
    st.subheader("👤 Athlete Profile")
    st.markdown(f"**Name:** {athlete_profile.get('name')}")
    st.markdown(f"**Age:** {athlete_profile.get('age')} years old")
    st.markdown(f"**Preferred Foot:** {athlete_profile.get('preferred_foot')}")
    st.markdown(f"**Level:** {athlete_profile.get('level')}")
    st.markdown(f"**Primary Position:** {athlete_profile.get('position')}")
    st.markdown(f"**Secondary Position:** {athlete_profile.get('secondary_position')}")
    
    st.markdown("**Focus Areas:**")
    for focus in athlete_profile.get("focus_areas", []):
        st.markdown(f"- 🎯 {focus}")
        
    st.markdown("**Available Gear:**")
    for eq in athlete_profile.get("equipment_available", []):
        st.markdown(f"- 🛡️ {eq}")
        
    st.divider()
    
    # Let users download their completion log data or reset it if needed
    st.subheader("⚙️ Progress Settings")
    
    # Download JSON
    json_log = json.dumps(completion_log, indent=2)
    st.download_button(
        label="📥 Export Completion Log (JSON)",
        data=json_log,
        file_name="completion_log.json",
        mime="application/json",
        use_container_width=True
    )
    
    # Reset history safety lock
    if st.checkbox("Enable progress reset lock"):
        if st.button("🛑 Reset Completion Logs", type="primary", use_container_width=True):
            empty_log = {"completions": []}
            data_loader.save_completion_log(empty_log, st.session_state.data_path)
            
            # Reset plan status
            if plan:
                for w in plan.get("weeks", []):
                    for s in w.get("sessions", []):
                        s["completed"] = False
                        s.pop("completed_date", None)
                data_loader.save_weekly_training_plan(plan, st.session_state.data_path)
                
            st.success("Your completion logs and session progress have been successfully reset!")
            st.rerun()
