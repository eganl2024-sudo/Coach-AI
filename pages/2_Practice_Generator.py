"""Player AI - My Training Plan"""
import streamlit as st
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import importlib
import config
import data_loader
import session_state
import ui_components
import completion_tracker
import training_plan_generator

# Force reload of custom modules to clear Streamlit's running process cache
try:
    importlib.reload(config)
    importlib.reload(data_loader)
    importlib.reload(session_state)
    importlib.reload(ui_components)
    importlib.reload(completion_tracker)
    importlib.reload(training_plan_generator)
except Exception:
    pass

from auth import require_auth

# Import Weasyprint for PDF Generation
try:
    from weasyprint import HTML as WeasyHTML
    WEASYPRINT_WARNING = None
except ImportError:
    WeasyHTML = None
    WEASYPRINT_WARNING = "Install 'weasyprint' to enable PDF exports."

# Page configuration
st.set_page_config(
    page_title="My Training Plan | Player AI",
    page_icon="⚽",
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
ui_components.render_nav(active_label="My Training Plan")

st.divider()

# Load athlete profile
athlete_profile = data_loader.load_athlete_profile(st.session_state.data_path)

# If no profile exists, route to Profile Setup
if not athlete_profile or not athlete_profile.get("name"):
    st.session_state.redirect_banner = "Please set up your Player Profile first to access your training plan!"
    st.switch_page("pages/5_Team_Hub.py")
    st.stop()

# Helper text functions
def _text(value):
    return str(value).strip() if value not in (None, "", "None", "nan") else ""

def _diagram_data_url(diagram_path):
    return ""

# Copied/Adapted block ordering and labels from legacy generator
BLOCK_ORDER = ["warmup", "technical", "cooldown"]
BLOCK_LABELS = {
    "warmup": "Activation & Warmup",
    "technical": "Skill Work & Technical Drills",
    "cooldown": "Game Application & Cool Down"
}

# The PDF Export HTML Builder
def build_printable_plan_html(practice, session_notes=None, export_mode="coach", include_qr=False):
    """Create a print-ready HTML plan with consolidated drill cards."""
    drill_cards = ""
    running_index = 1
    
    # Sort drills by block type
    for block_key in BLOCK_ORDER:
        block_drills = [
            d for d in practice["drills"]
            if d.get("block_type", "technical") == block_key
        ]
        if not block_drills:
            continue
            
        block_label = BLOCK_LABELS.get(block_key, block_key.title())
        drill_cards += f"<h2 class='block-heading'>{block_label}</h2>"
        
        for drill in block_drills:
            equipment = _text(drill.get('equipment', 'None')) or 'None'
            description = _text(drill.get("description")).replace("\n", "<br>")
            cues = _text(drill.get("coaching_points") or drill.get("coaching_cues")).replace("\n", "<br>")
            setup = _text(drill.get("setup_data") or drill.get("game_application")).replace("\n", "<br>")
            intensity_text = (_text(drill.get('intensity')) or "N/A").title()

            details_block = f"<p><strong>Coaching Cues:</strong> {cues or '—'}</p>"
            header_badge = ""
            
            drill_cards += f"""
            <div class="drill-card">
                <div class="drill-card__header">
                    <div class="drill-card__title">
                        <span class="drill-card__index">{running_index}.</span>
                        <strong>{drill['drill_name']}</strong>
                    </div>
                    <div>
                        {header_badge}
                        <span>{drill['allocated_time']} min</span>
                    </div>
                </div>
                <div class="drill-card__meta">
                    <span><strong>Category:</strong> {drill.get('category', 'Skills')}</span>
                    <span><strong>Intensity:</strong> {intensity_text}</span>
                    <span><strong>Equipment:</strong> {equipment}</span>
                </div>
                <div class="drill-card__body">
                    <div class="drill-card__text">
                        <p><strong>Overview:</strong> {description or '—'}</p>
                        <p><strong>Setup:</strong> {setup or '—'}</p>
                        {details_block}
                    </div>
                </div>
            </div>
            """
            running_index += 1

    notes_block = f"<p class='session-notes'><strong>Session Focus:</strong> {session_notes or '—'}</p>"

    # Load athlete profile details
    data_path = st.session_state.get('data_path', 'data')
    athlete_profile_data = data_loader.load_athlete_profile(data_path) or {}
    player_name = athlete_profile_data.get("name", "Player")
    focus_areas_str = ", ".join(athlete_profile_data.get("focus_areas", [])) or "—"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Training Plan - {player_name}</title>
    <style>
        body {{
            font-family: "Segoe UI", Arial, sans-serif;
            margin: 32px;
            color: #1f1f1f;
        }}
        header {{
            border-bottom: 2px solid #d0d7de;
            margin-bottom: 16px;
            padding-bottom: 12px;
        }}
        h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            margin-top: 8px;
            font-size: 14px;
        }}
        .meta span {{
            background: #f6f8fa;
            padding: 6px 10px;
            border-radius: 8px;
        }}
        .session-notes {{
            background: #edf2ff;
            padding: 10px 14px;
            border-radius: 10px;
            font-size: 14px;
        }}
        .block-heading {{
            margin-top: 28px;
            margin-bottom: 12px;
            font-size: 20px;
            color: #0f172a;
        }}
        .drill-card {{
            border: 1px solid #d0d7de;
            border-radius: 10px;
            padding: 14px;
            margin-bottom: 16px;
        }}
        .drill-card__header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}
        .drill-card__index {{
            color: #0969da;
            margin-right: 6px;
        }}
        .drill-card__meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            font-size: 13px;
            margin-bottom: 8px;
        }}
        .drill-card__body {{
            font-size: 14px;
            display: flex;
            gap: 12px;
            align-items: flex-start;
            flex-wrap: wrap;
        }}
        .drill-card__text {{
            flex: 1 1 220px;
        }}
        .fallback {{
            border-color: #f1c40f;
            background: #fffdef;
        }}
        .badge {{
            display: inline-block;
            background: #f1c40f;
            color: #5c3b00;
            font-size: 11px;
            padding: 2px 6px;
            border-radius: 6px;
            margin-right: 6px;
        }}
    </style>
</head>
<body>
    <header>
        <h1>Training Plan</h1>
        <div class="meta">
            <span><strong>Player:</strong> {player_name}</span>
            <span><strong>Date:</strong> {practice.get('session_date','')}</span>
            <span><strong>Duration:</strong> {practice.get('duration_minutes','')} min</span>
            <span><strong>Focus:</strong> {session_notes or '—'}</span>
        </div>
        <div style="margin-top: 8px; font-size: 14px;">
            <strong>Focus Areas:</strong> {focus_areas_str}
        </div>
    </header>
    {notes_block}
    {drill_cards}
    <h2>Equipment Needed</h2>
    <p>{", ".join(practice.get("equipment_needed", [])) or "—"}</p>
</body>
</html>"""
    return html

# Load or generate plan
plan = data_loader.load_weekly_training_plan(st.session_state.data_path)

# ── 7-day rollover check ─────────────────────────────────────────────────────
if plan:
    current_week = data_loader.get_current_week(plan)
    if current_week:
        gen_date_str = current_week.get("generated_date", "")
        if gen_date_str:
            try:
                gen_date = datetime.fromisoformat(gen_date_str)
                if (datetime.now() - gen_date) > timedelta(days=7):
                    drills_df = st.session_state.get("drills_df")
                    if drills_df is not None and not drills_df.empty:
                        drills = drills_df.to_dict("records")
                        rolled_plan = training_plan_generator.generate_training_plan(
                            athlete_profile, drills, existing_plan=plan
                        )
                        data_loader.save_weekly_training_plan(
                            rolled_plan, st.session_state.data_path
                        )
                        plan = rolled_plan
                        st.toast(
                            "🗓️ New week auto-generated! Your previous "
                            "sessions are preserved in History.",
                            icon="✅"
                        )
                    # If drills_df not loaded yet, skip rollover silently
                    # — it will trigger on the next page load when drills
                    # are available.
            except (ValueError, TypeError):
                pass  # unparseable date — skip rollover

if not plan:
    st.subheader("⚽ Generate Your Weekly Training Plan")
    st.write("Click the button below to generate a customized week of training matching your profile parameters.")
    if st.button("Generate Training Plan", type="primary", use_container_width=True):
        drills = st.session_state.drills_df.to_dict('records')
        new_plan = training_plan_generator.generate_training_plan(athlete_profile, drills)
        data_loader.save_weekly_training_plan(new_plan, st.session_state.data_path)
        st.success("Plan generated successfully! Reloading...")
        st.rerun()
    st.stop()

st.title("⚽ My Weekly Training Plan")
st.write("Follow these custom-curated training sessions to boost your skills and performance.")

# Styling for premium cards
st.markdown("""
<style>
.session-container {
    background-color: #f8fafc;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    border: 1px solid #e2e8f0;
}
.drill-block-title {
    font-size: 16px;
    font-weight: 700;
    color: #1e3a8a;
    margin-top: 15px;
    margin-bottom: 8px;
    text-transform: uppercase;
}
.drill-info-title {
    font-size: 18px;
    font-weight: 700;
    color: #0f172a;
}
.drill-info-badge {
    background-color: #dbeafe;
    color: #1e40af;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
    display: inline-block;
    margin-right: 8px;
}
.detail-label {
    font-weight: 700;
    color: #475569;
}
</style>
""", unsafe_allow_html=True)

# Loop through weeks and sessions
for week in plan.get("weeks", []):
    st.header(f"📅 Week {week.get('week_number')}")
    
    for session in week.get("sessions", []):
        week_num = week.get("week_number", 1)
        day_num = session.get("day_number")
        completed = session.get("completed", False)
        duration = session.get("duration_minutes")
        
        title_suffix = " (Completed ✅)" if completed else " (Remaining ⏳)"
        expander_label = f"Session {day_num}: {duration} min Player Session {title_suffix}"
        
        with st.expander(expander_label, expanded=not completed):
            st.subheader(session.get("name"))
            
            # Action Row
            act_col1, act_col2 = st.columns(2)
            
            with act_col1:
                if not completed:
                    if st.button(f"✅ Mark Session {day_num} Complete", key=f"complete_btn_w{week_num}_s{day_num}", type="primary", use_container_width=True):
                        completion_tracker.mark_session_complete(week.get("week_number"), day_num, st.session_state.data_path)
                        st.success(f"Great job completing Session {day_num}! Keep up the streak! 🎉")
                        st.rerun()
                else:
                    st.success(f"🎉 Session completed on {session.get('completed_date', '')[:10]}")
            
            with act_col2:
                # PDF Exporter Payload Assembly
                drills_list = session.get("drills", [])
                eq_needed = set()
                for d in drills_list:
                    eq_needed.add(d.get("min_equipment", "Ball only"))
                
                practice_payload = {
                    "team_name": athlete_profile.get("name", "Player"),
                    "session_date": datetime.today().strftime("%Y-%m-%d"),
                    "duration_minutes": duration,
                    "selected_categories": athlete_profile.get("focus_areas", []),
                    "equipment_needed": list(eq_needed) or ["Ball only"],
                    "drills": drills_list
                }
                
                html_export = build_printable_plan_html(practice_payload, "Personal Skill Plan")
                
                # HTML download always active
                st.download_button(
                    label="📄 Download HTML Plan",
                    data=html_export,
                    file_name=f"training_plan_session_{day_num}.html",
                    mime="text/html",
                    key=f"dl_html_w{week_num}_s{day_num}",
                    use_container_width=True
                )
                
            # Render drills inside the session
            drills = session.get("drills", [])
            for d in drills:
                block_type = d.get("block_type", "technical")
                block_label = BLOCK_LABELS.get(block_type, block_type.title())
                
                st.markdown(f'<div class="drill-block-title">{block_label}</div>', unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="drill-info-title">⭐ {d.get('drill_name')}</div>
                <div style="margin-top: 5px; margin-bottom: 12px;">
                    <span class="drill-info-badge">⏱️ {d.get('allocated_time')} Min</span>
                    <span class="drill-info-badge">📦 {d.get('min_equipment', 'Ball only')}</span>
                    <span class="drill-info-badge">🚀 {d.get('difficulty', 'Intermediate')}</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Video block
                ui_components.render_video(d.get("video_url"))
                
                st.write("")
                st.markdown(f"<span class='detail-label'>Overview & Setup:</span>", unsafe_allow_html=True)
                st.write(d.get("description", "No description available."))
                
                cues_list = d.get("coaching_cues") or d.get("coaching_points")
                if isinstance(cues_list, str):
                    cues_list = [c.strip() for c in cues_list.split("|") if c.strip()]
                
                if cues_list:
                    st.markdown(f"<span class='detail-label'>Coaching Cues:</span>", unsafe_allow_html=True)
                    for cue in cues_list:
                        st.markdown(f"- {cue}")
                        
                game_app = d.get("game_application")
                if game_app and game_app != "nan" and game_app != "None":
                    st.markdown(f"<span class='detail-label'>🎮 Game Application:</span>", unsafe_allow_html=True)
                    st.info(game_app)
                
                st.divider()

# Overwrite Plan Confirmation
st.subheader("🔄 Reset Training Plan")
confirm_reset = st.checkbox("I want to regenerate my weekly plan (a new week will be created and your history preserved)")
if confirm_reset:
    if st.button("Regenerate Weekly Plan", type="primary", use_container_width=True):
        drills = st.session_state.drills_df.to_dict('records')
        new_plan = training_plan_generator.generate_training_plan(
            athlete_profile, drills, existing_plan=plan
        )
        data_loader.save_weekly_training_plan(new_plan, st.session_state.data_path)
        st.success("A fresh, customized week of training has been created — your history is preserved! Reloading...")
        st.rerun()
