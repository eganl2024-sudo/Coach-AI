"""Practice Cycle Planner - multi-week session generator"""
import json
from datetime import date
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import config
import data_loader
import practice_generator
import practice_history
import templates
import session_state
import ui_components
from models import PracticeConfig
import diagram_renderer
from utils import sanitize_filename
from auth import require_auth

st.set_page_config(page_title="Practice Cycle", page_icon="🗓️", layout="wide")

require_auth()
ui_components.require_page_access("pages/8_Practice_Cycle.py")

ui_components.render_nav(active_label="🗓️ Practice Cycle")
st.divider()

st.title("🗓️ Practice Cycle Planner")
st.caption("Generate a multi-week plan (2 sessions per week) blending scripted templates and modular blocks.")

session_state.init_session_state()

if 'data_path' not in st.session_state:
    st.session_state.data_path = config.get_data_path()

if st.session_state.drills_df is None:
    st.session_state.drills_df = data_loader.load_drills(st.session_state.data_path)

if st.session_state.teams_df is None:
    st.session_state.teams_df = data_loader.load_teams(st.session_state.data_path)

session_state.render_team_selector(
    label="Active team",
    widget_key="team_selector_cycle",
    help_text="Sets the team context for all generated sessions."
)

team = st.session_state.selected_team
if team is None:
    st.warning("Select or add a team to generate a cycle.")
    st.stop()

template_list = data_loader.load_session_templates(st.session_state.data_path)
template_issues = templates.validate_templates(template_list, st.session_state.drills_df)
valid_templates = template_list
template_names = ["None"]
for tpl in template_list:
    issues = template_issues.get(tpl.name, {})
    if issues.get("missing_drill_ids") or issues.get("bad_durations"):
        template_names.append(f"{tpl.name} (Repair Needed)")
    else:
        template_names.append(tpl.name)

team_id = team['team_id']
history_mtime = practice_history.get_history_mtime(team_id, st.session_state.data_path)
history_df = practice_history.load_practice_history(team_id, st.session_state.data_path, history_mtime)
recent_usage = practice_history.get_recent_drill_usage(history_df)
drill_recency = practice_history.get_cached_recency(history_df)

team_row = st.session_state.teams_df[st.session_state.teams_df['team_id'] == team_id].iloc[0]
focus_tags = [t.strip() for t in str(team_row.get('focus_areas', '') or '').split("|") if t.strip()]
team_profile_context = {
    "play_style": str(team_row.get('play_style', '') or ''),
    "focus_tags": focus_tags,
    "season_objectives": str(team_row.get('season_objectives', '') or ''),
    "injuries": [i.strip() for i in str(team_row.get('injuries', '') or '').split("|") if i.strip()],
}

st.subheader("Cycle Configuration")
col_a, col_b, col_c = st.columns(3)
weeks = col_a.number_input("Weeks", min_value=1, max_value=12, value=4, step=1)
duration = col_b.slider("Session duration (min)", min_value=45, max_value=120, value=90, step=5)
num_players = col_c.slider("Expected players", min_value=6, max_value=30, value=12, step=1)

categories = st.multiselect(
    "Categories to include",
    options=config.CATEGORIES,
    default=config.CATEGORIES,
)
num_drills = st.slider("Drills per session", min_value=4, max_value=10, value=6, step=1)
favorites_only = st.checkbox("Use favorites only", value=False)
use_profile = st.checkbox("Use team profile weighting", value=True)
session_notes = st.text_input("Session notes (applied to all)", value="")
selected_template_name = st.selectbox(
    "Template for scripted blocks (optional)",
    options=template_names,
)
if len(valid_templates) < len(template_list):
    st.info("Some templates are hidden because they reference missing drills or have invalid durations. Repair them in Template Studio.")

generate_clicked = st.button("Generate Cycle", type="primary")

if generate_clicked:
    practice_config = PracticeConfig(
        duration_minutes=duration,
        num_players=num_players,
        num_drills=num_drills,
        selected_categories=categories or config.CATEGORIES,
        session_date=str(date.today()),
        session_notes=session_notes,
        favorites_only=favorites_only,
        use_team_profile=use_profile,
    )
    result = practice_generator.generate_multiweek_cycle(
        practice_config,
        team_profile=team,
        drills_df=st.session_state.drills_df,
        recent_usage=recent_usage,
        team_profile_context=team_profile_context,
        drill_recency=drill_recency,
        template_blocks=(
            next((
                tpl.blocks for tpl in template_list 
                if tpl.name == selected_template_name.replace(" (Repair Needed)", "")
            ), None)
            if selected_template_name != "None" else None
        ),
        weeks=weeks,
        history_df=history_df,
    )
    if not result.get("success"):
        st.error(result.get("error", "Failed to generate cycle."))
        if result.get("suggestion"):
            st.info(result["suggestion"])
    else:
        st.success(f"Generated {result['total_sessions']} sessions across {weeks} week(s).")
        weeks_data = result.get("weeks", [])
        exports = []
        for week_entry in weeks_data:
            week_num = week_entry["week"]
            st.markdown(f"### Week {week_num}")
            metrics_cols = st.columns(3)
            metrics_cols[0].metric("Total minutes", week_entry.get("total_minutes", 0))
            metrics_cols[1].metric("Sessions", len(week_entry.get("sessions", [])))
            metrics_cols[2].metric("Categories", ", ".join(week_entry.get("category_counts", {}).keys()) or "—")
            for sess in week_entry.get("sessions", []):
                with st.expander(f"{sess.session_date} — {sess.team_name} ({sess.duration_minutes} min)"):
                    st.markdown(", ".join(sess.selected_categories))
                    st.markdown(f"Equipment: {', '.join(sess.equipment_needed) if sess.equipment_needed else '—'}")
                    drill_table = pd.DataFrame([d.to_dict() for d in sess.drills])[
                        ["block_type", "drill_id", "drill_name", "allocated_time", "intensity"]
                    ]
                    st.dataframe(drill_table, hide_index=True, use_container_width=True)
                    warnings = sess.collect_warnings(
                        drills_df=st.session_state.drills_df,
                        team_profile=team,
                        history_df=history_df,
                        template_blocks=next((tpl.blocks for tpl in templates if tpl.name == selected_template_name), None) if selected_template_name != "None" else None
                    )
                    if warnings:
                        with st.expander("Session Warnings", expanded=False):
                            for w in warnings:
                                st.warning(w)
                    for d in sess.drills:
                        with st.expander(f"Diagram: {d.drill_name}", expanded=False):
                            diagram_renderer.render_diagram(d.drill_id, getattr(d, "diagram_path", ""))
            exports.extend([s.to_dict() for s in week_entry.get("sessions", [])])

        st.download_button(
            "Download cycle (JSON)",
            data=json.dumps(exports, indent=2),
            file_name=f"{sanitize_filename(team['team_name']).lower()}_cycle.json",
            mime="application/json",
        )
