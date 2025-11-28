"""Practice Generator - Create intelligent practice sessions"""
import json
import base64
import io
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import date, datetime, timedelta, UTC
import datetime as dt
import altair as alt

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

import config
import data_loader
import practice_generator
import templates
import practice_history
import session_state
import session_state as ui_session
import ui_components
import diagram_renderer
from models import (
    PracticeConfig,
    SessionDrill,
    validate_session_consistency,
    move_drill_in_session,
    can_move_up_down,
)
from utils import sanitize_filename
try:
    import qrcode
except ImportError:
    qrcode = None
    QR_WARNING = "QR code library not installed. Install 'qrcode' to enable QR exports."
else:
    QR_WARNING = ""

# Optional PDF export dependency
try:
    from weasyprint import HTML as WeasyHTML
except Exception:
    WeasyHTML = None
    WEASYPRINT_WARNING = "Install 'weasyprint' to enable PDF exports."
else:
    WEASYPRINT_WARNING = ""

BLOCK_LABELS = {
    "warmup": "Warmup",
    "technical": "Technical Block",
    "tactical": "Tactical Block",
    "ssg": "Small-Sided Games",
    "conditioning": "Conditioning",
    "cooldown": "Cool Down",
}

BLOCK_DURATION_PILL_CSS = """
<style>
.block-duration-pill {
    display: inline-block;
    padding: 4px 10px;
    margin-right: 6px;
    margin-bottom: 4px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 500;
    border: 1px solid #e5e7eb;
    background-color: #f9fafb;
    color: #111827;
}
.block-duration-pill.block-ok {
    border-color: #22c55e55;
    background-color: #dcfce7;
}
.block-duration-pill.block-low {
    border-color: #eab30855;
    background-color: #fef9c3;
}
.block-duration-pill.block-high {
    border-color: #ef444455;
    background-color: #fee2e2;
}
</style>
"""

PILL_CSS = """
<style>
.pill-row { margin: 6px 0 2px; display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.pill-row strong { margin-right: 4px; }
.pill { background: #eef2ff; color: #111827; padding: 6px 10px; border-radius: 999px;
        font-size: 13px; border: 1px solid #e5e7eb; }
</style>
"""


def generate_qr_data_url(text):
    if not qrcode:
        return None
    qr = qrcode.QRCode(box_size=2, border=1)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("utf-8")


def _text(value):
    """Convert mixed data types (including NaN floats) into safe strings."""
    if value is None:
        return ""
    if isinstance(value, float):
        if pd.isna(value):
            return ""
        return str(value)
    return str(value)


def _diagram_data_url(diagram_path):
    """Return a base64 data URI for the supplied diagram path."""
    if not diagram_path:
        return None
    file_path = config.get_diagram_file(diagram_path)
    if not file_path or not file_path.exists():
        return None
    try:
        data = file_path.read_bytes()
    except OSError:
        return None
    suffix = file_path.suffix.lower()
    if suffix == '.svg':
        mime = 'image/svg+xml'
    elif suffix in ('.jpg', '.jpeg'):
        mime = 'image/jpeg'
    else:
        mime = 'image/png'
    encoded = base64.b64encode(data).decode('utf-8')
    return f"data:{mime};base64,{encoded}"


def _resolve_block(drill):
    block = getattr(drill, "block_type", None)
    if block:
        return block
    category = getattr(drill, "category", None)
    return practice_generator.CATEGORY_TO_BLOCK.get(category, "technical")


def _refresh_block_indices(drills):
    counters = {}
    for drill in drills:
        block_key = _resolve_block(drill)
        counters.setdefault(block_key, 0)
        drill.block_index = counters[block_key]
        counters[block_key] += 1


def _render_pills(title, data):
    """Render a compact pill row for small dict summaries."""
    if not data:
        return
    pills = " ".join([f"<span class='pill'>{k}: {v}</span>" for k, v in data.items()])
    st.markdown(f"<div class='pill-row'><strong>{title}:</strong> {pills}</div>", unsafe_allow_html=True)


def build_printable_plan_html(practice, session_notes=None, export_mode="coach", include_qr=False):
    """Create a print-ready HTML plan with consolidated drill cards.

    Expects each drill dict to optionally include `diagram_path`, which will be
    resolved to a data URI so exports can embed the image inline.
    """
    drill_cards = ""
    running_index = 1
    for block_key in practice_generator.BLOCK_ORDER:
        block_drills = [
            drill for drill in practice["drills"]
            if (drill.get("block_type") or practice_generator.CATEGORY_TO_BLOCK.get(drill.get("category"), "technical")) == block_key
        ]
        block_drills.sort(key=lambda d: d.get("block_index", 0))
        if not block_drills:
            continue
        block_label = BLOCK_LABELS.get(block_key, block_key.title())
        drill_cards += f"<h2 class='block-heading'>{block_label}</h2>"
        for drill in block_drills:
            equipment = _text(drill.get('equipment', 'None')) or 'None'
            description = _text(drill.get("description")).replace("\n", "<br>")
            cues = _text(drill.get("coaching_points")).replace("\n", "<br>")
            setup = _text(drill.get("setup_data")).replace("\n", "<br>")
            intensity_text = (_text(drill.get('intensity')) or "N/A").title()
            diagram_url = _diagram_data_url(drill.get('diagram_path'))

            details_block = f"<p><strong>Coaching Cues:</strong> {cues or '—'}</p>" if export_mode == "coach" else ""
            header_badge = "<span class='badge'>Fallback</span>" if drill.get('fallback') else ""
            qr_img = ""
            if include_qr:
                qr_url = generate_qr_data_url(drill['drill_id'])
                if qr_url:
                    qr_img = f"<img class='qr' src='{qr_url}' alt='QR for {drill['drill_id']}'>"
            header_badge += qr_img
            drill_cards += f"""
            <div class="drill-card{' fallback' if drill.get('fallback') else ''}">
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
                    <span><strong>Category:</strong> {drill['category']}</span>
                    <span><strong>Intensity:</strong> {intensity_text}</span>
                    <span><strong>Players:</strong> {drill['players_min']}–{drill['players_max']}</span>
                    <span><strong>Equipment:</strong> {equipment}</span>
                </div>
                <div class="drill-card__body">
                    <div class="drill-card__text">
                        <p><strong>Overview:</strong> {description or '—'}</p>
                        <p><strong>Setup:</strong> {setup or '—'}</p>
                        {details_block}
                    </div>
                    {f"<div class='drill-card__diagram'><img src='{diagram_url}' alt='Diagram for {drill['drill_name']}' /></div>" if diagram_url else ''}
                </div>
            </div>
            """
            running_index += 1

    notes_block = f"<p class='session-notes'><strong>Session Focus:</strong> {session_notes or '—'}</p>"

    categories = ", ".join(practice.get('selected_categories', [])) or "—"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{practice['team_name']} Practice Plan</title>
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
        .drill-card__diagram {{
            flex: 0 0 auto;
            max-width: 240px;
        }}
        .drill-card__diagram img {{
            width: 100%;
            height: auto;
            border: 1px solid #d0d7de;
            border-radius: 8px;
            background: #ffffff;
            padding: 4px;
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
        .qr {{
            width: 56px;
            height: 56px;
            margin-left: 8px;
            vertical-align: middle;
        }}
    </style>
</head>
<body>
    <header>
        <h1>{practice.get('team_name','Practice Plan')}</h1>
        <div class="meta">
            <span><strong>Date:</strong> {practice.get('session_date','')}</span>
            <span><strong>Duration:</strong> {practice.get('duration_minutes','')} min</span>
            <span><strong>Players:</strong> {practice.get('num_players','')}</span>
            <span><strong>Focus:</strong> {session_notes or '—'}</span>
        </div>
    </header>
    {notes_block}
    {drill_cards}
    <h2>Equipment</h2>
    <p>{", ".join(practice.get("equipment_needed", [])) or "—"}</p>
</body>
</html>"""
    return html


def _build_export_payload(session):
    """Assemble a dict for printable exports from the current session."""
    practice_dict = {
        "team_name": session.team_name,
        "session_date": session.session_date,
        "duration_minutes": session.duration_minutes,
        "num_players": session.num_players,
        "selected_categories": session.selected_categories,
        "equipment_needed": getattr(session, "equipment_needed", []),
        "drills": [d.to_dict() for d in session.drills],
    }
    cfg = st.session_state.get("practice_config") or {}
    if isinstance(cfg, dict):
        practice_dict |= cfg
    return practice_dict


def _save_session_to_history(session):
    """Persist the session to practice history using the shared helper."""
    team = st.session_state.get("selected_team") or {}
    team_id = team.get("team_id")
    if not team_id:
        return False, "No team selected."

    session_name = session.config.session_notes or f"Session {session.session_date}"
    payload = {
        "session_date": str(session.session_date),
        "session_name": session_name,
        "session_notes": session.config.session_notes or "",
        "total_time": session.duration_minutes,
        "num_players": session.num_players,
        "drills_used": [d.drill_id for d in session.drills],
        "categories": session.selected_categories,
    }

    try:
        saved = practice_history.save_practice_session(
            team_id=team_id,
            session_dict=payload,
            data_path=st.session_state.data_path,
            session_obj=session,
        )
    except Exception as exc:
        return False, f"Failed to save: {exc}"

    if not saved:
        return False, "Could not write to practice history."

    try:
        practice_history.update_drill_library_usage(
            payload["drills_used"],
            st.session_state.drills_df,
            st.session_state.data_path,
        )
    except Exception:
        pass

    try:
        practice_history.load_practice_history.clear()
    except Exception:
        pass

    return True, "Saved to Past Sessions."


def _recompute_session_details(session):
    equipment_items = []
    category_summary = {}
    intensity_summary = {}
    for drill in session.drills:
        eq_value = str(drill.equipment or "").strip()
        if eq_value:
            for item in eq_value.split(","):
                clean = item.strip()
                if clean:
                    equipment_items.append(clean)
        category_summary[drill.category] = category_summary.get(drill.category, 0) + 1
        intensity_summary[drill.intensity] = intensity_summary.get(drill.intensity, 0) + 1
    session.equipment_needed = list(dict.fromkeys(equipment_items))
    session.category_summary = category_summary
    session.intensity_summary = intensity_summary


def _get_current_session():
    return st.session_state.get("current_session")


def _full_session_validation(session):
    errors = []
    errors.extend(validate_session_consistency(session, drills_df=st.session_state.get("drills_df")))
    try:
        errors.extend(session.validate())
    except Exception:
        pass
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for err in errors:
        if err not in seen:
            seen.add(err)
            unique.append(err)
    return unique


def _regenerate_block(session, block_key, config_data, drills_df, recency_map):
    """Replace drills within a block with fresh candidates."""
    replaced = 0
    history_df = st.session_state.get("practice_history_df")
    practice_config = PracticeConfig(
        duration_minutes=config_data.get("duration_minutes", 60),
        num_players=config_data.get("num_players", session.num_players),
        num_drills=config_data.get("num_drills", len(session.drills)),
        selected_categories=config_data.get("selected_categories", []),
        session_date=config_data.get("session_date", ""),
        session_notes=config_data.get("session_notes", ""),
        focus_tags=config_data.get("focus_tags", []),
        favorites_only=config_data.get("favorites_only", False),
        use_team_profile=config_data.get("use_team_profile", True),
        focus_boost_categories=config_data.get("focus_boost_categories", []),
    )
    try:
        for idx, drill in enumerate(session.drills):
            if _resolve_block(drill) != block_key:
                continue
            replacement_bundle = practice_generator.find_best_replacement_for_block(
                block_key,
                session,
                drills_df,
                st.session_state.selected_team,
                practice_config,
                history_df=history_df,
                recency_map=st.session_state.get("team_drill_recency", {}),
                debug=st.session_state.show_scoring_debug,
                debug_top_n=5
            )
            if not replacement_bundle:
                continue
            replacement, debug_bundle = replacement_bundle
            if replacement is None:
                continue
            replacement.allocated_time = drill.allocated_time
            replacement.target_intensity = getattr(drill, "target_intensity", drill.intensity)
            session.drills[idx] = replacement
            replaced += 1
            if st.session_state.show_scoring_debug and debug_bundle:
                st.session_state.scoring_debug = st.session_state.get("scoring_debug", [])
                st.session_state.scoring_debug.append(debug_bundle)
    except Exception:
        st.warning("Could not find an ideal replacement, using a fallback option.")
        # relaxed fallback: ignore recency
        for idx, drill in enumerate(session.drills):
            if _resolve_block(drill) != block_key:
                continue
            candidates = drills_df[drills_df['category'] == practice_generator.BLOCK_TO_CATEGORY.get(block_key, drill.category)]
            candidates = candidates[(candidates['players_min'] <= practice_config.num_players + config.PLAYER_TOLERANCE) &
                                     (candidates['players_max'] >= practice_config.num_players - config.PLAYER_TOLERANCE)]
            candidates = candidates[~candidates['drill_id'].eq(drill.drill_id)]
            if candidates.empty:
                st.warning("No suitable replacement found; keeping original drill.")
                continue
            candidate_dict = candidates.iloc[0].to_dict()
            candidate_dict['allocated_time'] = drill.allocated_time
            candidate_dict['target_intensity'] = getattr(drill, "target_intensity", drill.intensity)
            candidate_dict['block_type'] = block_key
            session.drills[idx] = SessionDrill.from_dict(candidate_dict)
            replaced += 1

    _refresh_block_indices(session.drills)
    _recompute_session_details(session)
    return True, f"Regenerated {replaced} drill(s) in {BLOCK_LABELS.get(block_key, block_key.title())}."


def _split_tags(cell):
    return [tag.strip() for tag in str(cell).split("|") if tag and tag.strip()]
st.set_page_config(page_title="Practice Generator", page_icon="⚽", layout="wide")

mode = "DEMO" if config.DEMO_MODE else "PRODUCTION"
ui_components.render_nav(active_label="⚽ Generate Practice")
st.divider()

if not st.session_state.get("block_duration_css_injected"):
    st.markdown(BLOCK_DURATION_PILL_CSS + PILL_CSS, unsafe_allow_html=True)
    st.session_state.block_duration_css_injected = True

team_label = st.session_state.selected_team['team_name'] if st.session_state.get("selected_team") else "your team"
st.header(f"Tonight's Practice for {team_label}")
st.caption("Pick the basics, generate, then make quick tweaks.")

# --- Step 1: initialize shared data/state -------------------------------------

session_state.init_session_state()

if 'data_path' not in st.session_state:
    st.session_state.data_path = config.get_data_path()

# Initialize session_date once per session (default to today)
# Check if Practice Generator was invoked from Team Hub with a target date
if st.session_state.get("generator_target_date") is not None:
    target_date = st.session_state.generator_target_date
    try:
        st.session_state.session_date = pd.to_datetime(target_date).date()
    except (TypeError, ValueError):
        st.session_state.session_date = dt.date.today()
    # Clear the flag
    st.session_state.pop("generator_target_date", None)
elif "session_date" not in st.session_state:
    st.session_state.session_date = dt.date.today()

block_templates = data_loader.load_session_templates(st.session_state.data_path)
if 'selected_block_template' not in st.session_state:
    st.session_state.selected_block_template = "None"

# Ensure drills and teams are loaded for this page
if st.session_state.drills_df is None:
    st.session_state.drills_df = data_loader.load_drills(st.session_state.data_path)

if st.session_state.teams_df is None:
    st.session_state.teams_df = data_loader.load_teams(st.session_state.data_path)

# Template validation against current drill library
template_issues = templates.validate_templates(block_templates, st.session_state.drills_df)
valid_block_templates = [
    tpl for tpl in block_templates
    if not template_issues.get(tpl.name, {}).get("missing_drill_ids")
    and not template_issues.get(tpl.name, {}).get("bad_durations")
]

if st.session_state.selected_team is None and len(st.session_state.teams_df) > 0:
    st.session_state.selected_team = st.session_state.teams_df.iloc[0].to_dict()

if 'current_session' not in st.session_state:
    st.session_state.current_session = None
if 'generation_error' not in st.session_state:
    st.session_state.generation_error = None
if 'show_scoring_debug' not in st.session_state:
    st.session_state.show_scoring_debug = False

is_coach = ui_session.is_coach_mode()
is_dev = ui_session.is_developer_mode()

if is_dev:
    st.session_state.show_scoring_debug = st.sidebar.checkbox(
        "Show advanced scoring debug",
        value=st.session_state.show_scoring_debug,
        help="Display why each drill was selected and the top alternatives."
    )

drill_load_error = st.session_state.drills_df.attrs.get('load_error')
if drill_load_error:
    st.error(drill_load_error)
    if len(st.session_state.drills_df) == 0:
        st.page_link("pages/4_Add_Drills.py", label="➕ Add a Drill to continue")
        st.stop()

team_load_error = st.session_state.teams_df.attrs.get('load_error')
if team_load_error:
    st.error(team_load_error)

session_state.render_team_selector(
    label="Active team",
    widget_key="team_selector_generator",
    help_text="Switch teams to generate sessions for a different squad."
)

# Simple config panel
config_col1, config_col2, config_col3 = st.columns(3)
practice_date = config_col1.date_input(
    "Practice date",
    value=st.session_state.session_date,
    key="session_date_input",
)
st.session_state.session_date = practice_date
session_length = config_col2.number_input("Session length (minutes)", min_value=45, max_value=120, value=90, step=5)
focus_choice = config_col3.selectbox(
    "Session focus (optional)",
    options=["Mixed", "Technical", "Tactical", "Fitness"],
    help="Helps guide drill selection and notes."
)

# Load practice history + recency info for the selected team (used in later steps)
practice_history_df = pd.DataFrame()
recent_usage = {}
team_profile_context = {}
team_drill_recency = {}
profile_status = session_state.get_team_profile_status()
if st.session_state.selected_team is not None:
    team_id = st.session_state.selected_team['team_id']
    history_mtime = practice_history.get_history_mtime(team_id, st.session_state.data_path)
    practice_history_df = practice_history.load_practice_history(team_id, st.session_state.data_path, history_mtime)
    st.session_state.practice_history_df = practice_history_df
    recent_usage = practice_history.get_recent_drill_usage(practice_history_df)
    team_drill_recency = practice_history.get_cached_recency(practice_history_df)
    st.session_state.team_drill_recency = team_drill_recency
    team_row = st.session_state.teams_df[st.session_state.teams_df['team_id'] == team_id]
    if len(team_row):
        team_data = team_row.iloc[0].to_dict()
        def _clean(value):
            if value is None:
                return ""
            return str(value).strip()
        focus_tags = [
            tag.strip() for tag in _clean(team_data.get('focus_areas', '')).split("|") if tag.strip()
        ]
        injuries = [
            entry.strip() for entry in _clean(team_data.get('injuries', '')).split("|") if entry.strip()
        ]
        team_profile_context = {
            "formation": _clean(team_data.get('formation', '')),
            "play_style": _clean(team_data.get('play_style', '')),
            "focus_tags": focus_tags,
            "injuries": injuries,
            "season_objectives": _clean(team_data.get('season_objectives', '')),
            "upcoming_match": {
                "date": _clean(team_data.get('upcoming_match_date', '')),
                "time": _clean(team_data.get('upcoming_match_time', '')),
                "opponent": _clean(team_data.get('upcoming_match_opponent', '')),
            }
        }
        st.session_state.team_profile_context = team_profile_context

profile_container = st.container()
with profile_container:
    if not team_profile_context:
        st.warning("This team does not have profile details set. Visit the Team Hub to capture play style, focus tags, and injuries.")
    else:
        col_style, col_tags, col_objective, col_formation = st.columns([1, 1.3, 1.3, 1])

        # Play Style (left)
        with col_style:
            st.markdown(
                f"""
                <div style="font-size:13px; color:#666; margin-bottom:4px;"><strong>Play Style</strong></div>
                <div style="font-size:14px; font-weight:500;">{team_profile_context.get("play_style") or "—"}</div>
                """,
                unsafe_allow_html=True,
            )

        # Focus Tags (as pills with edit button)
        with col_tags:
            focus_tags_list = team_profile_context.get("focus_tags", [])
            col_tag_preview, col_tag_btn = st.columns([3, 1])

            with col_tag_preview:
                if focus_tags_list:
                    pills_html = " ".join(
                        f"<span style='background-color:#eef2ff; padding:5px 10px; border-radius:6px; margin-right:4px; margin-bottom:4px; font-size:12px; border:1px solid #d5dce3; display:inline-block;'>{tag}</span>"
                        for tag in focus_tags_list
                    )
                    st.markdown(
                        f"<div style='font-size:13px; color:#666; margin-bottom:6px;'><strong>Focus Tags</strong></div><div>{pills_html}</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown("<div style='font-size:13px; color:#666; margin-bottom:4px;'><strong>Focus Tags</strong></div><div style='font-size:14px;'>—</div>", unsafe_allow_html=True)

            with col_tag_btn:
                if st.button("✏️ Edit", key="edit_focus_tags_top", help="Edit focus tags"):
                    st.session_state["open_focus_tags_expander"] = True
                    st.rerun()

        # Season Objective (with wrapping text)
        with col_objective:
            season_obj = team_profile_context.get("season_objectives") or "—"
            st.markdown(
                f"""
                <div style="font-size:13px; color:#666; margin-bottom:4px;"><strong>Season Objective</strong></div>
                <div style="font-size:14px; font-weight:500; word-wrap:break-word; word-break:break-word;">{season_obj}</div>
                """,
                unsafe_allow_html=True,
            )

        # Formation (right)
        with col_formation:
            st.markdown(
                f"""
                <div style="font-size:13px; color:#666; margin-bottom:4px;"><strong>Formation</strong></div>
                <div style="font-size:14px; font-weight:500;">{team_profile_context.get("formation") or "—"}</div>
                """,
                unsafe_allow_html=True,
            )

        # Show injuries if present
        injuries = team_profile_context.get("injuries", [])
        if injuries:
            injury_pills = " ".join(
                f"<span style='background-color:#fee2e2; padding:3px 8px; border-radius:5px; margin-right:3px; margin-bottom:3px; font-size:11px; border:1px solid #fca5a5; display:inline-block;'>{inj}</span>"
                for inj in injuries
            )
            st.markdown(
                f"<div style='margin-top:8px; font-size:12px; color:#666; margin-bottom:4px;'><strong>Injuries</strong></div><div>{injury_pills}</div>",
                unsafe_allow_html=True,
            )

        # Match info below
        if team_profile_context.get("upcoming_match", {}).get("opponent"):
            match = team_profile_context["upcoming_match"]
            st.caption(
                f"📅 Upcoming match: {match.get('opponent')} "
                f"({match.get('date') or 'date TBA'} {match.get('time') or ''})"
            )

    if profile_status["has_team"] and not profile_status["is_complete"]:
        missing = ", ".join(profile_status["missing_fields"])
        st.info(
            f"Team Hub is missing {missing}. Add them to improve drill scoring and suggestions."
        )

if team_profile_context and team_drill_recency:
    suggested_drills = []
    focus_tags = team_profile_context.get("focus_tags", [])
    if focus_tags:
        tag_set = {tag.lower() for tag in focus_tags}
        for _, drill in st.session_state.drills_df.iterrows():
            drill_tags = {tag.strip().lower() for tag in str(drill.get('tags', '')).split("|") if tag.strip()}
            recency_label = team_drill_recency.get(drill['drill_id'], {}).get("label", "New")
            if recency_label == "Fresh" and drill_tags.intersection(tag_set):
                suggested_drills.append(f"{drill['drill_name']} ({drill['category']})")
            if len(suggested_drills) >= 5:
                break
    underused_text = ""
    recent_window = practice_history_df.copy()
    if len(recent_window):
        try:
            recent_window['session_date'] = pd.to_datetime(recent_window['session_date'])
            cutoff = datetime.now(UTC) - timedelta(days=30)
            recent_window = recent_window[recent_window['session_date'] >= cutoff]
        except Exception:
            recent_window = pd.DataFrame()
    recent_cats = set()
    if len(recent_window):
        for cats in recent_window['categories'].fillna(""):
            recent_cats.update([c.strip() for c in str(cats).split("|") if c.strip()])
    underused = [cat for cat in config.CATEGORIES if cat not in recent_cats]

    with st.expander("Team-aware suggestions", expanded=False):
        if underused:
            st.markdown("**Underused categories this month:** " + ", ".join(underused))
        if focus_tags and suggested_drills:
            st.markdown("**Fresh drills aligned with focus tags:**")
            for drill_name in suggested_drills:
                st.markdown(f"- {drill_name}")
        elif focus_tags:
            st.markdown("Focus tags set but no fresh drills match yet.")
        else:
            st.markdown("Set focus tags in the Team Hub to receive suggestions.")

# --- Practice configuration form ---------------------------------------------

all_tags = set()
if st.session_state.drills_df is not None and 'tags' in st.session_state.drills_df.columns:
    for tags_str in st.session_state.drills_df['tags'].fillna(''):
        all_tags.update(_split_tags(tags_str))
available_tags = sorted(all_tags)

if 'use_team_profile' not in st.session_state:
    st.session_state.use_team_profile = True

if st.session_state.selected_team is None:
    st.warning("Please select or add a team before configuring a practice.")
else:
    with st.form("practice_config_form"):
        st.subheader("Session Configuration")

        col1, col2 = st.columns(2)

        with col1:
            # Check if a default duration was set from Team Hub
            default_duration = st.session_state.get("generator_default_duration", 90)
            if default_duration is not None:
                try:
                    default_duration = int(default_duration)
                    default_duration = max(45, min(120, default_duration))  # Clamp to valid range
                except (TypeError, ValueError):
                    default_duration = 90
                # Clear the flag
                st.session_state.pop("generator_default_duration", None)
            else:
                default_duration = 90

            duration = st.slider("Duration (minutes)", min_value=45, max_value=120, value=default_duration, step=5)
            raw_roster_size = st.session_state.selected_team.get('typical_roster_size')
            try:
                roster_size = int(raw_roster_size)
                roster_size = roster_size if roster_size > 0 else 0
            except (TypeError, ValueError):
                roster_size = 0
            default_players = max(6, min(30, roster_size)) if roster_size else 12
            player_count = st.number_input(
                "Expected Players",
                min_value=6,
                max_value=30,
                value=default_players
            )

        with col2:
            num_drills = st.slider("Number of Drills", min_value=3, max_value=8, value=5)

        categories = st.multiselect(
            "Drill Categories",
            options=config.CATEGORIES,
            default=["Warmup", "Technical", "Small Sided Games", "Cool Down"]
        )

        if len(valid_block_templates) < len(block_templates):
            st.info("Some templates are hidden because they reference missing drills or have invalid durations. Repair them in Template Studio.")
        template_options = ["None"] + [tpl.name for tpl in valid_block_templates]
        default_template = st.session_state.get("selected_block_template", "None")
        if default_template not in template_options:
            default_template = "None"
        template_index = template_options.index(default_template)
        template_choice = st.selectbox(
            "Load block template (optional)",
            options=template_options,
            index=template_index,
            help="Preload specific drills for each block. Generator will fill any remaining gaps.",
        )
        st.session_state.selected_block_template = template_choice
        template_descr = ""
        if template_choice != "None":
            match_tpl = next((tpl for tpl in valid_block_templates if tpl.name == template_choice), None)
            if match_tpl and match_tpl.description:
                template_descr = match_tpl.description
        if template_descr:
            st.caption(f"Template details: {template_descr}")

        use_team_profile = st.checkbox(
            "Use Team Profile To Influence Session",
            value=st.session_state.use_team_profile,
            help="Blend Team Hub focus tags, play style, and injuries into drill scoring for this session."
        )

        # Focus Tags expander with state-based opening
        focus_tags_expanded = st.session_state.get("open_focus_tags_expander", False)
        with st.expander("Focus tags (optional)", expanded=focus_tags_expanded):
            focus_tags = st.multiselect(
                "Select tags to filter drills",
                options=available_tags,
                help="Filter to drills that match these tags. Use focus tags from Team Hub for best results."
            )
            # Clear the expander state flag after reading
            if focus_tags_expanded:
                st.session_state["open_focus_tags_expander"] = False

        favorites_only = st.checkbox(
            "Use favorites only",
            value=False,
            help="Only choose drills you've marked as favorites."
        )

        session_notes = st.text_area(
            "Coach Notes / Focus", placeholder="Key objectives, player focus areas, etc."
        )

        generate_clicked = st.form_submit_button("Generate Practice")

    selected_template = None
    if st.session_state.selected_block_template != "None":
        selected_template = next(
            (tpl for tpl in valid_block_templates if tpl.name == st.session_state.selected_block_template),
            None
        )

    # Get focus boost categories from session state (set by Focus Tracker)
    focus_boost_categories = session_state.get_focus_boost_attributes()

    # Display notification if focus boost is active
    if focus_boost_categories:
        st.info(f"🎯 **Focus Mode Active:** Prioritizing under-trained areas: {', '.join(focus_boost_categories)}")

    if generate_clicked:
        if len(categories) == 0:
            st.warning("Select at least one category to generate a practice.")
        else:
            config_obj = PracticeConfig(
                duration_minutes=session_length,
                num_players=player_count,
                num_drills=num_drills,
                selected_categories=categories,
                session_date=st.session_state.session_date.isoformat(),
                session_notes=session_notes or (focus_choice if focus_choice != "Mixed" else ""),
                focus_tags=focus_tags,
                favorites_only=favorites_only,
                use_team_profile=use_team_profile,
                template_blocks=selected_template.blocks if selected_template else None,
                focus_boost_categories=focus_boost_categories,
            )
            try:
                config_obj.validate()
            except ValueError as exc:
                st.error(str(exc))
                st.stop()

            config_payload = config_obj.to_dict()
            config_payload.update({
                "team": st.session_state.selected_team,
                "recent_usage": recent_usage,
                "team_profile_context": team_profile_context,
                "drill_recency": team_drill_recency,
                "template_name": selected_template.name if selected_template else "",
            })
            config_payload["template_blocks"] = config_obj.template_blocks
            st.session_state.practice_config = config_payload
            st.session_state.use_team_profile = use_team_profile

            drills_source = st.session_state.drills_df.copy()
            if favorites_only:
                drills_source = drills_source[drills_source['is_favorite'] == True]  # noqa: E712
            if focus_tags:
                tag_set = set(focus_tags)
                drills_source = drills_source[
                    drills_source['tags'].apply(
                        lambda cell: bool(set(_split_tags(cell)).intersection(tag_set))
                    )
                ]

            if len(drills_source) == 0:
                result = {
                    "success": False,
                    "error": "No drills match the selected tags/favorites filter.",
                    "suggestion": "Adjust focus tags or disable the favorites-only toggle to expand options.",
                    "actions": {
                        "can_clear_tags": bool(focus_tags),
                        "can_disable_favorites": favorites_only
                    }
                }
            else:
                result = practice_generator.generate_practice_plan(
                    config=config_obj,
                    team_profile=config_payload["team"],
                    drills_df=drills_source,
                    recent_usage=config_payload.get("recent_usage", {}),
                    team_profile_context=team_profile_context if use_team_profile else None,
                    drill_recency=config_payload.get("drill_recency", {}),
                    template_blocks=config_obj.template_blocks,
                    history_df=practice_history_df,
                    debug=st.session_state.show_scoring_debug,
                )
            if result.get("success"):
                st.success("Practice generated! Review details below.")
                st.session_state.current_session = result["session"]
                st.session_state.current_session.manual_adjustments = {"reordered": 0, "replaced": 0}
                st.session_state.scoring_debug = result.get("debug") or []
                st.session_state.generation_error = None
                st.session_state.pop("replace_target_index", None)

                # Clear focus boost categories after successful generation
                if focus_boost_categories:
                    session_state.clear_focus_boost_attributes()
            else:
                st.session_state.current_session = None
                st.session_state.scoring_debug = []
                st.session_state.generation_error = result
                st.error(result.get("error", "Unable to generate practice."))
                actions = result.get("actions", {})
                if actions.get("can_clear_tags"):
                    if st.button("Clear focus tags and retry"):
                        st.session_state.practice_config["focus_tags"] = []
                        st.session_state.generation_error = None
                        st.rerun()
                if actions.get("can_disable_favorites"):
                    if st.button("Disable favorites-only filter and retry"):
                        st.session_state.practice_config["favorites_only"] = False
                        st.session_state.generation_error = None
                        st.rerun()


# --- Step 2: Generate practice plan and show results --------------------------

if st.session_state.get("practice_config"):
    config_data = st.session_state.practice_config

    if len(config_data.get("selected_categories", [])) == 0:
        st.warning("Select at least one category to generate a practice.")
    else:
        st.subheader("Session Snapshot")
        info_cols = st.columns([1.5, 1.5, 1])
        team_info = config_data["team"]
        with info_cols[0]:
            st.markdown(
                f"""
                <div style="font-size:13px; color:#666; margin-bottom:4px;"><strong>Team</strong></div>
                <div style="font-size:14px; font-weight:500; margin-bottom:8px;">{team_info['team_name']}</div>
                <div style="font-size:13px; color:#666; margin-bottom:4px;"><strong>Age Group</strong></div>
                <div style="font-size:14px; font-weight:500; margin-bottom:8px;">{team_info['age_group']}</div>
                <div style="font-size:13px; color:#666; margin-bottom:4px;"><strong>Skill</strong></div>
                <div style="font-size:14px; font-weight:500;">{team_info['skill_level'].title()}</div>
                """,
                unsafe_allow_html=True,
            )
        with info_cols[1]:
            st.markdown(
                f"""
                <div style="font-size:13px; color:#666; margin-bottom:4px;"><strong>Date</strong></div>
                <div style="font-size:14px; font-weight:500; margin-bottom:8px;">{config_data['session_date']}</div>
                <div style="font-size:13px; color:#666; margin-bottom:4px;"><strong>Duration</strong></div>
                <div style="font-size:14px; font-weight:500; margin-bottom:8px;">{config_data['duration_minutes']} min</div>
                <div style="font-size:13px; color:#666; margin-bottom:4px;"><strong>Players</strong></div>
                <div style="font-size:14px; font-weight:500;">{config_data['num_players']}</div>
                """,
                unsafe_allow_html=True,
            )
        with info_cols[2]:
            st.markdown(
                f"""
                <div style="font-size:13px; color:#666; margin-bottom:4px;"><strong>Categories</strong></div>
                <div style="font-size:14px; font-weight:500; margin-bottom:8px;">{", ".join(config_data['selected_categories']) or "—"}</div>
                <div style="font-size:13px; color:#666; margin-bottom:4px;"><strong>Options</strong></div>
                <div style="font-size:13px;">
                    Favorites: {'Yes' if config_data.get('favorites_only') else 'No'}<br/>
                    Team Profile: {'On' if config_data.get('use_team_profile') else 'Off'}
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Additional details in expander if needed
        with st.expander("Session notes & tags", expanded=False):
            if config_data.get("session_notes"):
                st.markdown(f"**Coach Notes:** {config_data['session_notes']}")
            if config_data.get("focus_tags"):
                focus_pills = " ".join(
                    f"<span style='background-color:#e8f4fd; padding:4px 8px; border-radius:6px; margin-right:4px; font-size:12px; border:1px solid #b3d9e8;'>{tag}</span>"
                    for tag in config_data["focus_tags"]
                )
                st.markdown(f"<div style='margin-top:8px;'><strong>Focus Tags:</strong><br/>{focus_pills}</div>", unsafe_allow_html=True)

        with st.expander("Recency watchlist (advanced)", expanded=False):
            if config_data.get("recent_usage"):
                name_map = {}
                try:
                    df = st.session_state.get("drills_df")
                    if df is not None and "drill_id" in df.columns:
                        name_col = "drill_name" if "drill_name" in df.columns else ("name" if "name" in df.columns else None)
                        if name_col:
                            name_map = df.set_index("drill_id")[name_col].to_dict()
                except Exception:
                    name_map = {}
                rows = []
                for drill, sessions in config_data["recent_usage"].items():
                    label = name_map.get(drill, drill)
                    row = {"Drill": label, "Sessions Ago": sessions}
                    if ui_session.is_developer_mode():
                        row["ID"] = drill
                    rows.append(row)
                recency_df = pd.DataFrame(rows)

                # Sort toggle
                sort_mode = st.radio(
                    "Sort by",
                    options=["Most recent first", "Least recent first"],
                    index=0,
                    horizontal=True,
                    key="recency_sort_mode"
                )

                # Apply sorting
                if sort_mode == "Most recent first":
                    recency_sorted = recency_df.sort_values("Sessions Ago", ascending=True)
                else:
                    recency_sorted = recency_df.sort_values("Sessions Ago", ascending=False)

                st.dataframe(recency_sorted, use_container_width=True, hide_index=True, height=200)
            else:
                st.write("No recent drills logged for this team.")

        st.divider()
        st.caption("Need tweaks? Jump to other pages via the sidebar.")
        if st.button("Reset"):
            st.session_state.pop("practice_config", None)
            st.session_state.pop("current_session", None)
            st.session_state.pop("generation_error", None)
            st.session_state.pop("replace_target_index", None)
            st.rerun()

        current_session = _get_current_session()
        generation_error = st.session_state.get("generation_error")
        if generation_error and not current_session:
            st.error(generation_error.get("error", "Unable to generate practice."))
            if generation_error.get("suggestion"):
                st.info(generation_error["suggestion"])

        if current_session:
            session = current_session

            # ======== Consolidated Status Banners ========
            status_col1, status_col2 = st.columns(2)

            with status_col1:
                st.markdown(
                    f"""
                    <div style="
                        background-color:#d4edda;
                        border:1px solid #c3e6cb;
                        border-radius:8px;
                        padding:10px 12px;
                        font-size:13px;
                        color:#155724;
                    ">
                        ✓ Generated {session.num_drills} drills for {session.team_name} ({session.duration_minutes} min)
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with status_col2:
                validation_errors = _full_session_validation(session)
                if validation_errors:
                    st.markdown(
                        f"""
                        <div style="
                            background-color:#fff3cd;
                            border:1px solid #ffeaa7;
                            border-radius:8px;
                            padding:10px 12px;
                            font-size:13px;
                            color:#856404;
                        ">
                            ⚠️ Session needs attention
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"""
                        <div style="
                            background-color:#cfe2ff;
                            border:1px solid #b6d4fe;
                            border-radius:8px;
                            padding:10px 12px;
                            font-size:13px;
                            color:#084298;
                        ">
                            ✓ Session passed validation checks
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            checklist = st.sidebar.container()
            checklist.subheader("Block Checklist")
            block_counts = {}
            for drill in session.drills:
                block = _resolve_block(drill)
                block_counts[block] = block_counts.get(block, 0) + 1
            for block in practice_generator.BLOCK_ORDER:
                status_icon = "[x]" if block_counts.get(block) else "[ ]"
                checklist.markdown(f"{status_icon} {BLOCK_LABELS.get(block, block.title())}")

            # Show detailed validation errors in expander if needed
            if validation_errors:
                with st.expander("Validation details", expanded=False):
                    for error in validation_errors:
                        st.warning(error)

            team_summary = session.team_profile_summary
            if team_summary:
                summary_lines = []
                if team_summary.get("focus_matches"):
                    summary_lines.append(f"{team_summary['focus_matches']} drills matched focus tags")
                if team_summary.get("playstyle_matches"):
                    summary_lines.append(f"{team_summary['playstyle_matches']} matched play style")
                if team_summary.get("objective_matches"):
                    summary_lines.append(f"{team_summary['objective_matches']} matched objectives")
                recency_line = (
                    f"Fresh: {team_summary.get('fresh_selected', 0)}, "
                    f"Neutral: {team_summary.get('neutral_selected', 0)}, "
                    f"Recent: {team_summary.get('recent_selected', 0)}"
                )
                summary_lines.append(recency_line)
                if team_summary.get("recent_skipped"):
                    summary_lines.append(f"Skipped {team_summary['recent_skipped']} recent drills")
                st.caption("Team-aware summary: " + " | ".join(summary_lines))

            auto_blocks = team_summary.get("auto_inserted_blocks") if team_summary else []
            auto_removed = team_summary.get("auto_removed_drills") if team_summary else 0
            if auto_blocks:
                labels = ", ".join(BLOCK_LABELS.get(block, block.title()) for block in auto_blocks)
                st.warning(
                    f"Added automatic block(s): {labels}. Adjust the drill library if you want manual control.",
                    icon="ℹ️"
                )
            if auto_removed:
                st.warning(
                    f"Removed {auto_removed} lower-intensity drills to keep session length consistent.",
                    icon="⚠️"
                )

            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

            # ========================================================================
            # SESSION SUMMARY CARD (Overview + Structure + Intensity Curve)
            # ========================================================================
            with st.container():
                st.markdown(
                    """
                    <div style="
                        background-color:#fafafa;
                        border:1px solid #eee;
                        border-radius:10px;
                        padding:18px 22px 22px 22px;
                        margin-bottom:18px;
                    ">
                    """,
                    unsafe_allow_html=True,
                )

                # Main hero title
                st.markdown(f"#### Tonight's plan for {session.team_name}")
                focus_label = session.config.session_notes or "Session focus"
                st.caption(f"{session.session_date} · Focus: {focus_label}")

                # Session Overview with icons and pills
                st.markdown("### Session Overview")
                overview_cols = st.columns([1.3, 1, 2])

                with overview_cols[0]:
                    st.markdown(
                        f"""
                        <div style="font-size:14px; font-weight:600; color:#444; margin-bottom:6px;">
                            ⏱ Duration
                        </div>
                        <div style="font-size:22px; font-weight:600; margin-top:-2px;">
                            {session.duration_minutes} min
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with overview_cols[1]:
                    st.markdown(
                        f"""
                        <div style="font-size:14px; font-weight:600; color:#444; margin-bottom:6px;">
                            👥 Players
                        </div>
                        <div style="font-size:22px; font-weight:600; margin-top:-2px;">
                            {session.num_players}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with overview_cols[2]:
                    # Category pills
                    pill_html = " ".join(
                        f"<span style='background-color:#f3f4f6; padding:3px 10px; border-radius:999px; margin-right:6px; font-size:12px;'>{cat}</span>"
                        for cat in session.selected_categories
                    )
                    st.markdown(
                        f"""
                        <div style="font-size:14px; font-weight:600; color:#444; margin-bottom:6px;">
                            🎯 Categories
                        </div>
                        <div style="margin-top:2px; display:flex; flex-wrap:wrap; gap:6px;">
                            {pill_html}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # ========================================================================
                # SESSION STRUCTURE SECTION (Block durations + Categories & Intensity)
                # ========================================================================
                st.markdown("#### Session structure")
                struct_col_left, struct_col_right = st.columns(2)

                # LEFT COLUMN: Block durations
                with struct_col_left:
                    st.markdown("<div style='font-size:12px; font-weight:600; margin-bottom:8px; color:#555;'>Block durations</div>", unsafe_allow_html=True)
                    duration_summaries = getattr(session, "block_duration_summaries", []) or []
                    if duration_summaries:
                        block_html = ""
                        for summary in duration_summaries:
                            data = summary if isinstance(summary, dict) else summary.__dict__
                            label = BLOCK_LABELS.get(data.get("block_type"), data.get("block_type", "").title())
                            total_min = data.get("total_minutes", 0)
                            target_min = data.get("target_min", 0)
                            target_max = data.get("target_max", 0)
                            block_html += (
                                f"<div style='font-size:13px; line-height:1.5; margin-bottom:6px;'>"
                                f"<strong>{label}:</strong> {total_min} min "
                                f"<span style='color:#999;'>(target {target_min}–{target_max})</span>"
                                f"</div>"
                            )
                        st.markdown(block_html, unsafe_allow_html=True)
                    else:
                        st.caption("No block durations available.")

                # RIGHT COLUMN: Categories & Intensity summary
                with struct_col_right:
                    st.markdown("<div style='font-size:12px; font-weight:600; margin-bottom:8px; color:#555;'>Categories & intensity</div>", unsafe_allow_html=True)

                    # Categories
                    category_summary = session.category_summary or {}
                    if category_summary:
                        cat_html = ""
                        for cat_name, count in category_summary.items():
                            cat_html += f"<div style='font-size:13px; line-height:1.5; margin-bottom:2px;'>• {cat_name}: {count}</div>"
                        st.markdown(cat_html, unsafe_allow_html=True)

                        # Intensity
                        intensity_summary = session.intensity_summary or {}
                        if intensity_summary:
                            st.markdown(
                                "<div style='font-size:12px; font-weight:600; margin-top:10px; margin-bottom:4px; color:#555;'>Intensity</div>",
                                unsafe_allow_html=True,
                            )
                            intensity_line = " · ".join(
                                f"{name.capitalize()}: {count}" for name, count in intensity_summary.items()
                            )
                            st.markdown(
                                f"<div style='font-size:13px; line-height:1.5;'>{intensity_line}</div>",
                                unsafe_allow_html=True,
                            )

                # ========================================================================
                # INTENSITY CURVE CHART
                # ========================================================================
                st.markdown("#### Intensity curve (start → finish)")

                # Build intensity data from current session drills
                intensity_map = {"low": 1, "medium": 2, "high": 3}
                intensity_data = []
                for idx, drill in enumerate(session.drills, start=1):
                    intensity_score = intensity_map.get(
                        (drill.intensity or "medium").lower(), 2
                    )
                    intensity_data.append({
                        "index": idx,
                        "drill_name": drill.drill_name[:20],  # truncate for readability
                        "intensity_score": intensity_score,
                    })

                if intensity_data:
                    df_intensity = pd.DataFrame(intensity_data)

                    intensity_chart = (
                        alt.Chart(df_intensity)
                        .mark_line(point=True, strokeWidth=2, color="#4F8BF9")
                        .encode(
                            x=alt.X(
                                "index:O",
                                title="Drill order (start → finish)",
                                axis=alt.Axis(labelAngle=0)
                            ),
                            y=alt.Y(
                                "intensity_score:Q",
                                title="Intensity",
                                scale=alt.Scale(domain=[1, 3]),
                                axis=alt.Axis(
                                    values=[1, 2, 3],
                                    labelExpr="datum.value == 1 ? 'Low' : datum.value == 2 ? 'Medium' : 'High'"
                                ),
                            ),
                            tooltip=["index", "drill_name", "intensity_score"],
                        )
                        .properties(height=220)
                        .interactive()
                    )

                    st.altair_chart(intensity_chart, use_container_width=True)

                st.markdown("</div>", unsafe_allow_html=True)

            if session.manual_adjustments.get("reordered") or session.manual_adjustments.get("replaced"):
                st.info(
                    f"Manual adjustments applied — reordered: {session.manual_adjustments.get('reordered', 0)}, "
                    f"replaced: {session.manual_adjustments.get('replaced', 0)}."
                )

            template_name_applied = config_data.get("template_name")
            if template_name_applied:
                st.caption(f"Block template applied: {template_name_applied}")
            if getattr(session, "template_notes", None):
                st.warning("Template notes: " + "; ".join(session.template_notes), icon="⚠")

            st.markdown("#### Session Order (top to bottom)")
            display_counter = 1
            for global_idx, drill in enumerate(session.drills):
                st.divider()
                block_key = _resolve_block(drill)
                col_desc, col_details, col_diagram = st.columns([2, 1.2, 1.2])

                with col_desc:
                    st.markdown(
                        f"**{display_counter}. {drill.drill_name} ({drill.allocated_time} min)** · "
                        f"{BLOCK_LABELS.get(block_key, block_key.title())}"
                    )
                    display_counter += 1
                    if drill.fallback:
                        st.warning("Fallback drill added due to limited options.", icon="i")

                    show_detail_key = f"show_details_{block_key}_{global_idx}"
                    show_details = st.session_state.get(show_detail_key, False)
                    ctrl_cols = st.columns(5)
                    if ctrl_cols[0].button("Swap", key=f"swap_{block_key}_{global_idx}"):
                        ok, msg = _regenerate_block(
                            session,
                            block_key,
                            config_data,
                            st.session_state.drills_df,
                            st.session_state.get("team_drill_recency", {}),
                        )
                        st.session_state.current_session = session
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.warning(msg)
                    if ctrl_cols[1].button("Details", key=f"details_{block_key}_{global_idx}"):
                        show_details = not show_details
                        st.session_state[show_detail_key] = show_details
                    if ctrl_cols[2].button("Edit", key=f"edit_{block_key}_{global_idx}"):
                        st.session_state.prefill_drill = drill.to_dict()
                        st.switch_page("pages/6_Edit_Drill.py")
                    can_move_up, can_move_down = can_move_up_down(len(session.drills), global_idx)
                    if ctrl_cols[3].button("↑", key=f"move_up_{global_idx}", disabled=not can_move_up, help="Move this drill up"):
                        if move_drill_in_session(session, global_idx, "up"):
                            _refresh_block_indices(session.drills)
                            _recompute_session_details(session)
                            st.session_state.current_session = session
                            st.rerun()
                    if ctrl_cols[4].button("↓", key=f"move_down_{global_idx}", disabled=not can_move_down, help="Move this drill down"):
                        if move_drill_in_session(session, global_idx, "down"):
                            _refresh_block_indices(session.drills)
                            _recompute_session_details(session)
                            st.session_state.current_session = session
                            st.rerun()

                    st.markdown("**Overview**")
                    st.write(drill.description)
                    st.markdown("**Coaching Points**")
                    st.write(drill.coaching_points or "—")
                    st.markdown("**Equipment**")
                    st.write(drill.equipment or "None")

                with col_details:
                    st.markdown("**Drill Details**")
                    st.write(f"Category: {drill.category}")
                    st.write(f"Intensity: {drill.intensity.title()} (target {drill.target_intensity})")
                    st.write(f"Players: {drill.players_min}-{drill.players_max}")
                    st.write(f"Field: {drill.field_type or '—'}")
                    st.write(f"Recency: {drill.recency_label or 'New'}")

                    # Recency warning: only show if used in last 3 practices
                    sessions_ago = config_data.get("recent_usage", {}).get(drill.drill_id)
                    if sessions_ago and isinstance(sessions_ago, int) and 1 <= sessions_ago <= 3:
                        if sessions_ago == 1:
                            recency_message = "You used this last practice"
                        else:
                            recency_message = f"You used this {sessions_ago} practices ago"

                        st.markdown(
                            f"""
                            <div style="
                                background-color:#FFF8E1;
                                border-radius:6px;
                                padding:8px 10px;
                                margin-top:8px;
                                font-size:12px;
                                display:flex;
                                align-items:center;
                            ">
                                <span style="margin-right:6px;">⚠️</span>
                                <span>{recency_message}</span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    if show_details:
                        st.write(f"Tags: {', '.join(_split_tags(drill.tags)) if getattr(drill, 'tags', '') else '—'}")
                        st.write(f"Positions: {getattr(drill, 'positions', '') or '—'}")
                        st.write(f"Age Groups: {getattr(drill, 'age_groups', '') or '—'}")
                        st.write(f"Coach Cues: {getattr(drill, 'coach_cues', '') or '—'}")
                        st.write(f"Progression: {getattr(drill, 'progression', '') or '—'}")
                        st.write(f"Recommended Field Size: {getattr(drill, 'recommended_field_size', '') or '—'}")

                with col_diagram:
                    st.markdown("**Diagram**")
                    rendered = diagram_renderer.render_diagram(drill.drill_id, getattr(drill, "diagram_path", ""))
                    if not rendered:
                        st.caption("No diagram available yet.")

                warnings = session.collect_warnings(
                    drills_df=st.session_state.drills_df,
                    team_profile=st.session_state.selected_team,
                    history_df=st.session_state.get("practice_history_df"),
                    template_blocks=config_data.get("template_blocks")
                )
                if warnings:
                    with st.expander("Session Warnings", expanded=False):
                        for w in warnings:
                            st.warning(w)

                if st.session_state.show_scoring_debug:
                    debug_entries = [
                        entry for entry in st.session_state.get("scoring_debug", []) or []
                        if entry.get("block_type") == _resolve_block(drill)
                    ]
                    if debug_entries:
                        for dbg in debug_entries:
                            with st.expander("Scoring Debug", expanded=False):
                                st.caption(f"Chosen: {dbg.get('chosen')}")
                                cand_rows = []
                                for cand in dbg.get("candidates", []):
                                    bd = cand.get("breakdown", {})
                                    cand_rows.append({
                                        "drill_id": cand.get("drill_id"),
                                        "score": cand.get("score"),
                                        "focus": bd.get("focus_match"),
                                        "players": bd.get("player_fit_score"),
                                        "block": bd.get("block_alignment"),
                                        "intensity": bd.get("intensity_match"),
                                        "recency": bd.get("recency_penalty"),
                                    })
                                if cand_rows:
                                    st.dataframe(pd.DataFrame(cand_rows), use_container_width=True, hide_index=True)
                                if dbg.get("candidates"):
                                    chosen_bd = dbg["candidates"][0].get("breakdown")
                                    if chosen_bd:
                                        st.caption(practice_generator.build_scoring_narrative(
                                            practice_generator.DrillScoreBreakdown(**chosen_bd)
                                        ))


            with st.expander("Block Template Tools", expanded=False):
                st.markdown("**Save current session as a block template**")
                template_name_input = st.text_input(
                    "Template name",
                    key="template_save_name",
                    help="Name must be unique. Saving with an existing name will overwrite it."
                )
                template_desc_input = st.text_area(
                    "Description",
                    key="template_save_desc",
                    placeholder="Optional: describe the focus of this template."
                )
                if st.button("Save Template", key="save_template_btn"):
                    name_clean = template_name_input.strip()
                    if not name_clean:
                        st.warning("Template name is required.")
                    else:
                        # Use shared helper to save template
                        session.session_name = name_clean
                        ok, msg = practice_history.save_session_as_template(session, st.session_state.data_path)
                        if ok:
                            st.success(f"Template saved as '{msg}'.")
                            st.session_state.selected_block_template = msg
                            st.rerun()
                        else:
                            if msg == "duplicate":
                                st.info("A template with this name already exists.")
                            else:
                                st.error(f"Could not save template: {msg}")
                existing_templates = templates.load_block_templates()
                if existing_templates:
                    st.markdown("**Existing templates**")
                    for tpl in existing_templates:
                        desc = tpl.description or "No description"
                        st.caption(f"- {tpl.name}: {desc}")

            st.divider()
            st.markdown("### Save & Export")
            actions = st.columns(3)

            export_payload = _build_export_payload(session)
            html_payload = build_printable_plan_html(
                practice=export_payload,
                session_notes=session.config.session_notes,
            )

            with actions[0]:
                saving = st.session_state.get("saving_session", False)
                if st.button("Save Practice", disabled=saving):
                    st.session_state.saving_session = True
                    ok, msg = _save_session_to_history(session)
                    st.session_state.saving_session = False
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

            with actions[1]:
                st.download_button(
                    "Download Practice (HTML)",
                    data=html_payload,
                    file_name=f"practice_{session.session_date}.html",
                    mime="text/html",
                )

            with actions[2]:
                if WeasyHTML is None:
                    st.button("Download Practice (PDF)", disabled=True)
                    st.caption(WEASYPRINT_WARNING or "PDF export unavailable.")
                else:
                    pdf_bytes = b""
                    try:
                        pdf_bytes = WeasyHTML(string=html_payload).write_pdf()
                    except Exception as exc:
                        st.error(f"PDF export failed: {exc}")
                    st.download_button(
                        "Download Practice (PDF)",
                        data=pdf_bytes,
                        file_name=f"practice_{session.session_date}.pdf",
                        mime="application/pdf",
                        disabled=not pdf_bytes,
                    )



