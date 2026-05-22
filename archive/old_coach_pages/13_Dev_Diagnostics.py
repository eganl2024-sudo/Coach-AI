"""Developer Diagnostics - surfacing data health and config for debugging."""
import streamlit as st
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import config
import data_loader
import practice_history
import templates
import session_state
import ui_components
import practice_generator
from auth import require_auth

st.set_page_config(page_title="Dev Diagnostics", page_icon="🧪", layout="wide")

require_auth()
session_state.init_session_state()  # Initialize to get developer_mode

# ✅ FIX: Check both config.is_dev() AND session_state developer_mode
if not config.is_dev() and not st.session_state.get('developer_mode', False):
    st.error("🔒 This page requires developer mode.")
    st.info("💡 Add `?dev=true` to the URL to enable developer mode")
    st.stop()

ui_components.render_nav(active_label="🧪 Dev Diagnostics")
st.divider()
st.title("🧪 Dev Diagnostics")

session_state.init_session_state()
if "data_path" not in st.session_state:
    st.session_state.data_path = config.get_data_path()

drills_df = data_loader.load_drills(st.session_state.data_path)
teams_df = data_loader.load_teams(st.session_state.data_path)
templates_list = data_loader.load_session_templates(st.session_state.data_path)

col_a, col_b, col_c = st.columns(3)
col_a.metric("Drills loaded", len(drills_df))
col_b.metric("Teams loaded", len(teams_df))
col_c.metric("Templates loaded", len(templates_list))

st.subheader("Repair summaries")
def _repairs_summary(df, label):
    repairs = df.attrs.get("repairs") if hasattr(df, "attrs") else None
    if not repairs:
        st.caption(f"{label}: no repairs recorded.")
        return
    added = repairs.get("added_columns", [])
    coerced = repairs.get("coerced_columns", [])
    filled = repairs.get("filled_values", {})
    parts = []
    if added:
        parts.append(f"added {len(added)} column(s): {', '.join(added)}")
    if coerced:
        parts.append(f"coerced columns: {', '.join(coerced)}")
    if filled:
        filled_cols = [f"{k}({v})" for k, v in filled.items() if v]
        if filled_cols:
            parts.append(f"filled missing in {', '.join(filled_cols)}")
    if parts:
        st.caption(f"{label}: " + "; ".join(parts))
    else:
        st.caption(f"{label}: no repairs needed.")

_repairs_summary(drills_df, "Drills")
_repairs_summary(teams_df, "Teams")

st.subheader("Drill sample")
st.dataframe(drills_df.head(5), use_container_width=True)

st.subheader("Templates")
if templates_list:
    template_issues = templates.validate_templates(templates_list, drills_df)
    broken = [name for name, issue in template_issues.items() if issue.get("missing_drill_ids") or issue.get("bad_durations")]
    if broken:
        st.warning(f"{len(broken)} template(s) need repair (missing drills or bad durations).")
    for tpl in templates_list:
        issue = template_issues.get(tpl.name, {})
        status = "OK"
        if issue.get("missing_drill_ids") or issue.get("bad_durations"):
            status = "Needs repair"
        st.markdown(f"- **{tpl.name}**: {len(tpl.blocks)} blocks ({status})")
        if issue.get("missing_drill_ids"):
            st.caption(f"Missing drills: {', '.join(issue['missing_drill_ids'])}")
        if issue.get("bad_durations"):
            st.caption(f"Bad durations in blocks: {', '.join(issue['bad_durations'])}")
else:
    st.caption("No templates found.")

st.subheader("Scoring parameters")
st.json({
    "DEMO_MODE": config.DEMO_MODE,
    "DEVELOPER_MODE": config.DEVELOPER_MODE,
    "data_path": str(st.session_state.data_path),
})

st.subheader("Templates detail")
if templates_list:
    for tpl in templates_list:
        st.markdown(f"**{tpl.name}** — {tpl.description or 'No description'}")
        st.json({
            "blocks": tpl.blocks,
            "block_durations": tpl.block_durations,
        })
else:
    st.caption("No templates found.")

st.subheader("Scoring dry-run")
block_choice = st.selectbox("Block type", options=practice_generator.BLOCK_ORDER)
top_n = st.slider("Top N", min_value=1, max_value=10, value=5)
if st.button("Run scoring dry-run"):
    if len(drills_df) == 0:
        st.warning("No drills loaded.")
    else:
        cfg = practice_generator.PracticeConfig(
            duration_minutes=60,
            num_players=12,
            num_drills=5,
            selected_categories=list(config.CATEGORIES),
            session_date="2024-01-01",
            session_notes="",
        )
        team_profile = {"team_id": "DEV", "team_name": "Dev", "skill_level": "intermediate"}
        scores = []
        for _, row in drills_df.iterrows():
            bd = practice_generator.score_drill_candidate(
                row.to_dict(),
                block_type=block_choice,
                team_profile=team_profile,
                practice_config=cfg,
                history_df=None,
            )
            scores.append({
                "drill_id": row["drill_id"],
                "drill_name": row.get("drill_name"),
                "score": bd.total_score,
                "focus": bd.focus_match,
                "recency": bd.recency_penalty,
                "intensity": bd.intensity_match,
                "players": bd.player_fit_score,
            })
        scores_df = pd.DataFrame(scores).sort_values("score", ascending=False).head(top_n)
        st.dataframe(scores_df, use_container_width=True, hide_index=True)

st.subheader("History repair report (selected team)")
team_options = teams_df['team_id'].tolist() if len(teams_df) else []
selected_team = st.selectbox("Team", options=team_options) if team_options else None
if selected_team:
    mtime = practice_history.get_history_mtime(selected_team, st.session_state.data_path)
    hist_df = practice_history.load_practice_history(selected_team, st.session_state.data_path, mtime)
    _repairs_summary(hist_df, "History")
    report = practice_history.repair_history_report(hist_df, teams_df)
    st.json(report)
else:
    st.caption("No team selected for history report.")

st.caption("Inspect additional internals as needed. Developer-only page.")
