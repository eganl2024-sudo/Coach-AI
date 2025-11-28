"""Team Hub - Deep dive into team profiles and context"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import config
import data_loader
import practice_history
import session_state
import session_state as ui_session
import ui_components
import schedule
import team_profile
import pandas as pd


CHECKLIST_LINK_CSS = """
<style>
.checklist-link {
    display: inline-block;
    padding: 6px 10px;
    border-radius: 6px;
    border: 1px solid #e5e7eb;
    background: #f9fafb;
    color: #111827;
    text-decoration: none;
    font-size: 13px;
}
.checklist-link:hover { background: #eef2ff; }
</style>
"""

CHECKLIST_SCROLL_JS = """
<script>
document.addEventListener('DOMContentLoaded', () => {
  const OFFSET = window.innerHeight * 0.3;  // scroll target ~30% down
  document.querySelectorAll('a.checklist-link').forEach(link => {
    link.addEventListener('click', (e) => {
      const targetId = link.getAttribute('href').replace('#','');
      const target = document.getElementById(targetId);
      if (!target) { return; }
      e.preventDefault();
      const rect = target.getBoundingClientRect();
      const scrollTop = window.pageYOffset + rect.top - OFFSET;
      window.scrollTo({ top: scrollTop, behavior: 'smooth' });
      setTimeout(() => {
        const focusable = Array.from(document.querySelectorAll('input, textarea, select'))
          .find(el => el.getBoundingClientRect().top > rect.top - 5);
        if (focusable) {
          focusable.focus({ preventScroll: true });
        }
      }, 400);
    });
  });
});
</script>
"""


def _persist_teams(df):
    data_path = st.session_state.get('data_path')
    if not data_path:
        return
    team_file = Path(data_path) / 'team_profiles.csv'
    df.to_csv(team_file, index=False)
    st.session_state.teams_df = df


def _explode(cell):
    return [item.strip() for item in str(cell).split("|") if item.strip()]

def _get_next_match_from_schedule(upcoming_df: pd.DataFrame | None):
    import pandas as pd
    if upcoming_df is None or upcoming_df.empty:
        return None
    df = upcoming_df.copy()
    if "event_date" not in df.columns:
        return None
    df["event_date"] = pd.to_datetime(df["event_date"]).dt.normalize()
    today = pd.Timestamp.today().normalize()
    df = df[df["event_date"] >= today]
    if df.empty:
        return None
    if "event_type" in df.columns:
        mask_game = df["event_type"].astype(str).str.lower().str.contains("game|match", na=False)
        games_df = df[mask_game]
        if not games_df.empty:
            df = games_df
    if "start_time" in df.columns:
        df["start_time"] = df["start_time"].astype(str)
        df = df.sort_values(["event_date", "start_time"])
    else:
        df = df.sort_values(["event_date"])
    return df.iloc[0]

def _render_week_view(upcoming_df: pd.DataFrame | None) -> None:
    import pandas as pd

    if upcoming_df is None or upcoming_df.empty or "event_date" not in upcoming_df.columns:
        st.info("No upcoming schedule found for this team. Upload and save a PDF schedule above to get started.")
        return

    upcoming_df = upcoming_df.copy()
    upcoming_df["event_date"] = pd.to_datetime(upcoming_df["event_date"]).dt.normalize()

    today_ts = pd.Timestamp.today().normalize()
    upcoming_df = upcoming_df[upcoming_df["event_date"] >= today_ts].copy()

    if upcoming_df.empty:
        st.info("No upcoming schedule found for this team. Upload and save a PDF schedule above to get started.")
        return

    first_date = upcoming_df["event_date"].min()
    weekday = first_date.weekday()  # Monday=0
    days_since_sunday = (weekday + 1) % 7
    default_week_start = (first_date - pd.Timedelta(days=days_since_sunday)).normalize()

    if "schedule_week_start" not in st.session_state:
        st.session_state["schedule_week_start"] = default_week_start

    week_start: pd.Timestamp = st.session_state["schedule_week_start"]
    week_days = [week_start + pd.Timedelta(days=i) for i in range(7)]
    week_end = week_start + pd.Timedelta(days=6)

    header_cols = st.columns([1, 2, 1])
    with header_cols[0]:
        if st.button("← Previous week", key="schedule_prev_week"):
            st.session_state["schedule_week_start"] = week_start - pd.Timedelta(days=7)
            st.rerun()
    with header_cols[1]:
        st.markdown(
            f"<div style='text-align:center; font-weight:600; margin-top:0.25rem;'>"
            f"Week of {week_start.strftime('%b %d')} – {week_end.strftime('%b %d')}"
            f"</div>",
            unsafe_allow_html=True,
        )
    with header_cols[2]:
        if st.button("Next week →", key="schedule_next_week"):
            st.session_state["schedule_week_start"] = week_start + pd.Timedelta(days=7)
            st.rerun()

    if "start_time" in upcoming_df.columns:
        upcoming_df["start_time"] = upcoming_df["start_time"].astype(str).fillna("")
    else:
        upcoming_df["start_time"] = ""

    week_df = upcoming_df[
        (upcoming_df["event_date"] >= week_start) & (upcoming_df["event_date"] <= week_end)
    ].copy()

    events_by_day = {
        day: week_df[week_df["event_date"] == day].sort_values(["event_date", "start_time"])
        for day in week_days
    }

    day_cols = st.columns(7)
    day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    today = pd.Timestamp.today().normalize()

    for idx, day in enumerate(week_days):
        day_events = events_by_day[day]
        with day_cols[idx]:
            st.markdown(
                f"<div style='text-align:center; font-size:0.75rem; color:#888;'>{day_names[idx]}</div>",
                unsafe_allow_html=True,
            )
            is_today = day == today
            border_color = "#4F8BF9" if is_today else "#e0e0e0"
            font_weight = "600" if is_today else "400"
            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    margin-top:0.25rem;
                    padding:0.15rem 0.4rem;
                    border-radius:999px;
                    border:1px solid {border_color};
                    font-size:0.85rem;
                    font-weight:{font_weight};
                ">{day.strftime('%d')}</div>
                """,
                unsafe_allow_html=True,
            )

            if day_events.empty:
                st.markdown(
                    "<div style='height:2.5rem; text-align:center; font-size:0.75rem; color:#bbb; margin-top:0.25rem;'>—</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown("<div style='height:0.25rem;'></div>", unsafe_allow_html=True)
                for _, row in day_events.iterrows():
                    event_type = str(row.get("event_type", "") or "").strip()
                    start_time = str(row.get("start_time", "") or "").strip()
                    opponent = str(row.get("opponent", "") or "").strip()
                    lower_type = event_type.lower()
                    if "game" in lower_type or "match" in lower_type:
                        icon = "⚽"
                    elif "lift" in lower_type or "strength" in lower_type:
                        icon = "💪"
                    elif "film" in lower_type or "video" in lower_type:
                        icon = "🎥"
                    else:
                        icon = "🟢"

                    opp_label = opponent
                    if len(opp_label) > 18:
                        opp_label = opp_label[:15].rstrip() + "…"

                    parts = [icon]
                    if start_time:
                        parts.append(start_time)
                    if event_type:
                        parts.append(event_type)
                    if opp_label:
                        parts.append(f"vs {opp_label}")
                    label = " ".join(parts)
                    st.markdown(
                        f"<div style='font-size:0.75rem; margin-bottom:0.25rem; line-height:1.25;'>{label}</div>",
                        unsafe_allow_html=True,
                    )


st.set_page_config(page_title="Team Hub", page_icon="👥", layout="wide")

ui_components.render_nav(active_label="👥 My Team")
st.divider()

st.title("👥 Team Hub")
st.caption("Capture formation, match notes, focus areas, and practice context for every squad.")
st.markdown(CHECKLIST_LINK_CSS + CHECKLIST_SCROLL_JS, unsafe_allow_html=True)

session_state.init_session_state()
is_coach = ui_session.is_coach_mode()
is_dev = ui_session.is_developer_mode()

if 'data_path' not in st.session_state:
    st.session_state.data_path = config.get_data_path()

if st.session_state.teams_df is None:
    st.session_state.teams_df = data_loader.load_teams(st.session_state.data_path)

if st.session_state.teams_df.attrs.get('load_error'):
    st.error(st.session_state.teams_df.attrs['load_error'])

session_state.render_team_selector(
    label="Active team",
    widget_key="team_selector_hub",
    help_text="Switch teams to edit a different profile."
)

teams_df = st.session_state.teams_df
team_repair = teams_df.attrs.get('repair_info')
if team_repair and team_repair.get("was_repaired"):
    added = ", ".join(team_repair.get("added_columns", [])) or "columns"
    st.warning(f"Team profiles CSV was missing {added}; defaults were applied.")

if st.session_state.selected_team is None or teams_df is None or len(teams_df) == 0:
    st.warning("Add a team to start using the Team Hub.")
    st.stop()

team = st.session_state.selected_team
team_id = team['team_id']
team_row = teams_df[teams_df['team_id'] == team_id].iloc[0]
profile_status = session_state.get_team_profile_status(team_id)
completion_percent, missing_fields = session_state.get_team_profile_completeness(team_row)
profile_data_path = Path(st.session_state.data_path)
stored_profile = team_profile.load_team_profile(profile_data_path, team_id)
next_match_row = _get_next_match_from_schedule(schedule.load_team_schedule(team_id, st.session_state.data_path))

profile_col, meta_col = st.columns([2, 1])
with profile_col:
    st.subheader(team['team_name'])
    st.markdown(f"**Age Group:** {team.get('age_group', '—')}")
    st.markdown(f"**Skill Level:** {team.get('skill_level', '—').title() if team.get('skill_level') else '—'}")
    st.markdown(f"**Formation:** {team_row.get('formation', 'Set in profile below') or 'Set in profile below'}")
    st.markdown(f"**Play Style:** {team_row.get('play_style', 'Set in profile below') or 'Set in profile below'}")
    st.markdown(f"**Notes:** {team_row.get('notes', '') or '—'}")
    if team_row.get('upcoming_match_date') or team_row.get('upcoming_match_opponent'):
        match_bits = []
        if team_row.get('upcoming_match_opponent'):
            match_bits.append(str(team_row['upcoming_match_opponent']))
        if team_row.get('upcoming_match_date'):
            match_bits.append(str(team_row['upcoming_match_date']))
        if team_row.get('upcoming_match_time'):
            match_bits.append(str(team_row['upcoming_match_time']))
        if match_bits:
            st.markdown(f"**Upcoming Match:** {' | '.join(match_bits)}")
    if team_row.get('season_objectives'):
        st.markdown(f"**Season Objective:** {team_row.get('season_objectives')}")

with meta_col:
    st.metric("Roster Size", team.get('typical_roster_size', 0))
    st.metric("Focus Areas", len(_explode(team_row.get('focus_areas', ''))))
    st.metric("Key Players Logged", len(_explode(team_row.get('key_players', ''))))

st.divider()
st.subheader("Quick Edit")
edit_sections = st.columns(3)
if edit_sections[0].button("Update team basics"):
    st.switch_page("pages/0_Coach_Onboarding.py")
if edit_sections[1].button("Update practice schedule"):
    st.switch_page("pages/0_Coach_Onboarding.py")
if edit_sections[2].button("Edit focus/style"):
    st.switch_page("pages/0_Coach_Onboarding.py")

st.divider()
st.subheader("Profile Details")

with st.expander("Setup Checklist", expanded=completion_percent < 80):
    st.markdown(f"Completion: **{completion_percent}%**")
    checklist_items = [
        ("age_group", "Select age group", "anchor_age_group"),
        ("formation", "Select formation", "anchor_formation"),
        ("play_style", "Select play style", "anchor_play_style"),
        ("focus_tags", "Add focus tags", "anchor_focus_tags"),
        ("key_players", "Add key players", "anchor_key_players"),
        ("injuries", "Add injuries or availability notes", "anchor_injuries"),
        ("practice_schedule", "Add practice schedule", "anchor_practice_schedule"),
    ]
    for key, label, link in checklist_items:
        status_icon = "✅" if key not in missing_fields else "⬜"
        cols = st.columns([3, 1])
        cols[0].markdown(f"{status_icon} {label}")
        cols[1].markdown(
            f"<a class='checklist-link' href='#{link}'>Go there</a>",
            unsafe_allow_html=True,
        )
    if completion_percent >= 80:
        st.success("Team profile complete — ready for multi-week cycle generation.")
    else:
        st.info("Fill the unchecked items above to unlock better recommendations.")

existing_focus_tags = _explode(team_row.get('focus_areas', ''))
key_players_default = "\n".join(_explode(team_row.get('key_players', '')))
injuries_default = "\n".join(_explode(team_row.get('injuries', '')))

if not profile_status["is_complete"]:
    missing = ", ".join(profile_status["missing_fields"])
    st.warning(
        f"Team profile is missing {missing}. Fill these in so the Practice Generator "
        "can tailor drill suggestions."
    )

st.markdown("---")
st.markdown("<a name='schedule-section'></a>", unsafe_allow_html=True)
st.header("Schedule (Upload & Calendar)")
st.caption("Upload a game/practice PDF, review parsed events, then save & view on the calendar.")

st.markdown("---")
st.subheader("Upload Schedule (PDF)")
uploaded_schedule = st.file_uploader(
    "Upload a game or practice schedule (PDF)",
    type=["pdf"],
    key="schedule_pdf",
)

if st.button("Parse PDF schedule"):
    if uploaded_schedule is None:
        st.warning("Please upload a PDF schedule first.")
    else:
        try:
            parsed_df = schedule.parse_pdf_schedule(uploaded_schedule.getvalue())
            st.session_state["draft_schedule_df"] = parsed_df
            st.success("Schedule parsed. Review and edit below before saving.")
        except Exception as exc:
            print("Error parsing PDF schedule:", exc)
            st.error(
                "We couldn't read this PDF. "
                f"Details: {exc}"
            )

# Editable draft table
if "draft_schedule_df" in st.session_state:
    st.subheader("Review & Edit Schedule")
    draft_df = st.session_state["draft_schedule_df"]
    edited_df = st.data_editor(
        draft_df,
        num_rows="dynamic",
        hide_index=True,
        use_container_width=True,
        key="schedule_editor",
    )
    st.session_state["draft_schedule_df"] = edited_df

    if st.button("Save schedule to team"):
        df_to_save = st.session_state.get("draft_schedule_df")
        if df_to_save is None:
            st.warning("Nothing to save yet. Parse a PDF schedule first.")
        else:
            try:
                schedule.save_team_schedule(st.session_state.data_path, team_id, df_to_save)
                st.success("Schedule saved for this team.")
            except Exception as e:
                print("Error saving team schedule:", e)
                st.error(f"We couldn't save this schedule. {e}")

st.markdown("---")
st.markdown("## Upcoming Schedule")
st.caption("Week-by-week view of games, training, and events for this team.")
upcoming_df = schedule.load_team_schedule(team_id, st.session_state.data_path)
_render_week_view(upcoming_df)

st.markdown("## This Week's Practices")
practice_types = {"practice", "film", "lift", "recovery", "walkthrough"}
today_norm = pd.Timestamp.today().normalize()
week_cutoff = today_norm + pd.Timedelta(days=7)
pr_df = None
if upcoming_df is not None and not upcoming_df.empty and "event_date" in upcoming_df.columns:
    pr_df = upcoming_df.copy()
    pr_df["event_date"] = pd.to_datetime(pr_df["event_date"], errors="coerce").dt.normalize()
    pr_df = pr_df[(pr_df["event_date"] >= today_norm) & (pr_df["event_date"] <= week_cutoff)]
    if "event_type" in pr_df.columns:
        pr_df = pr_df[pr_df["event_type"].astype(str).str.lower().isin(practice_types)]
    pr_df = pr_df.dropna(subset=["event_date"])
    pr_df = pr_df.sort_values(["event_date", "start_time"]) if not pr_df.empty else pr_df

if pr_df is None or pr_df.empty:
    st.info("No practices scheduled for the next 7 days.")
else:
    for idx, row in pr_df.iterrows():
        date_val = row.get("event_date")
        date_disp = ""
        if pd.notna(date_val):
            try:
                date_disp = pd.to_datetime(date_val).strftime("%a %b %d")
            except Exception:
                date_disp = str(date_val)
        time_raw = str(row.get("start_time", "") or "").strip()
        time_disp = time_raw
        if time_raw:
            try:
                parsed_time = pd.to_datetime(time_raw).time()
                time_disp = parsed_time.strftime("%I:%M %p").lstrip("0")
            except Exception:
                time_disp = time_raw
        type_disp = str(row.get("event_type", "") or "Practice").strip()
        loc_disp = str(row.get("location", "") or "").strip()
        notes_disp = str(row.get("notes", "") or "").strip()
        meta_parts = [p for p in [loc_disp, notes_disp] if p]
        meta_line = " | ".join(meta_parts)

        # Full-width card with integrated button
        with st.container():
            col_left, col_right = st.columns([4.5, 1.5])

            with col_left:
                st.markdown(
                    f"""
                    <div style="
                        border: 1px solid #e5e5e5;
                        border-radius: 8px;
                        padding: 0.75rem 1rem;
                        background-color: #fafafa;
                    ">
                        <div style="font-weight: 700; font-size: 0.95rem;">{date_disp} {time_disp}</div>
                        <div style="font-size: 0.85rem; margin-top: 0.3rem; color: #555;">{type_disp}</div>
                        {f'<div style="font-size: 0.8rem; color: #888; margin-top: 0.2rem;">{meta_line}</div>' if meta_line else ''}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col_right:
                # Vertical spacing to align button with card
                st.markdown("<div style='height: 0.35rem;'></div>", unsafe_allow_html=True)
                if st.button(
                    "⚽ Generate Practice",
                    key=f"gen_practice_{idx}",
                    help="Create a practice for this date",
                    use_container_width=True,
                ):
                    # Extract duration from duration field or default to 90
                    inferred_duration = 90
                    if "duration_minutes" in row and pd.notna(row["duration_minutes"]):
                        try:
                            inferred_duration = int(row["duration_minutes"])
                        except (TypeError, ValueError):
                            inferred_duration = 90

                    # Store values for Practice Generator to read
                    st.session_state.generator_target_date = date_val
                    st.session_state.generator_default_duration = inferred_duration

                    # Navigate to Practice Generator
                    st.switch_page("pages/2_Practice_Generator.py")

        # Subtle divider between cards
        st.markdown(
            "<div style='height: 0.5px; background-color: #f0f0f0; margin: 8px 0;'></div>",
            unsafe_allow_html=True,
        )

formation_options = ["4-3-3", "4-4-2", "3-5-2", "4-2-3-1", "4-1-4-1", "Custom"]
raw_formation = team_row.get('formation', '')
current_formation = str(raw_formation) if raw_formation is not None else ''
current_formation = current_formation.strip()
if current_formation and current_formation not in formation_options:
    formation_options.append(current_formation)
formation_index = formation_options.index(current_formation) if current_formation in formation_options else 0

st.divider()
st.markdown("## Match Plan & Coach Notes")
st.caption("Capture how you want this team to set up for the next match.")

# ============================================================================
# CALCULATE MATCH DATA FOR BANNER AND FORM
# ============================================================================
current_match_date = team_row.get('upcoming_match_date')
upcoming_match_date_default = stored_profile.get("upcoming_match_date") or current_match_date
kickoff_time_default = stored_profile.get("kickoff_time") or team_row.get('upcoming_match_time')
upcoming_opponent_default = stored_profile.get("upcoming_opponent") or team_row.get('upcoming_match_opponent', '')

kickoff_time_readonly = ""
upcoming_opponent_readonly = ""
location_readonly = ""
upcoming_match_date_display = ""

if next_match_row is not None:
    upcoming_match_date_default = next_match_row.get("event_date", upcoming_match_date_default)
    upcoming_opponent_readonly = str(next_match_row.get("opponent", "") or "").strip()
    location_readonly = str(next_match_row.get("location", "") or "").strip()
    raw_time = next_match_row.get("start_time", "")
    if pd.notna(raw_time) and str(raw_time).strip():
        try:
            if isinstance(raw_time, str):
                parsed = pd.to_datetime(raw_time).time()
            else:
                parsed = getattr(raw_time, "time", lambda: raw_time)()
            kickoff_time_readonly = parsed.strftime("%I:%M %p").lstrip("0")
        except Exception:
            kickoff_time_readonly = str(raw_time)

# Parse upcoming_match_date for banner display
match_date_value = None
if upcoming_match_date_default is not None and upcoming_match_date_default != "":
    try:
        parsed_date = pd.to_datetime(upcoming_match_date_default, errors='coerce')
        if pd.notna(parsed_date):
            match_date_value = parsed_date.date()
            upcoming_match_date_display = parsed_date.strftime("%a, %b %d")
    except Exception:
        match_date_value = None

# ============================================================================
# MATCH BANNER: OPPONENT | DATE | TIME | LOCATION
# ============================================================================
if upcoming_opponent_readonly or kickoff_time_readonly or location_readonly:
    opp_text = upcoming_opponent_readonly or "TBD"
    date_text = upcoming_match_date_display or "TBD"
    time_text = kickoff_time_readonly or "TBD"
    loc_text = location_readonly or "TBD"

    st.markdown(
        f"""
        <div style="
            background-color:#f7f7f9;
            padding:0.75rem 1rem;
            border-radius:8px;
            display:flex;
            justify-content:space-between;
            align-items:center;
            font-weight:600;
            font-size:15px;
            margin-bottom:1.5rem;
            gap:1rem;
        ">
            <div style="flex:1.2;">{opp_text}</div>
            <div style="flex:1;">{date_text}</div>
            <div style="flex:0.9;">{time_text}</div>
            <div style="flex:1.2;">{loc_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================================
# MAIN FORM CONTAINER
# ============================================================================
st.markdown("<a id='anchor_formation'></a>", unsafe_allow_html=True)
st.markdown("<a id='anchor_play_style'></a>", unsafe_allow_html=True)

# Row 1: Preferred formation & Play style / identity
col_form, col_style = st.columns(2)

with col_form:
    preferred_formation_value = st.selectbox(
        "Preferred formation",
        options=formation_options,
        index=formation_index,
        key="preferred_formation",
        help="Default shape for this team's next match.",
    )

with col_style:
    play_style_options = config.TEAM_PLAY_STYLES + ["Custom"]
    raw_play_style = team_row.get('play_style', '')
    current_play_style = str(raw_play_style) if raw_play_style is not None else ''
    current_play_style = current_play_style.strip()
    default_play_style = stored_profile.get("default_play_style", "Custom")
    match_play_style = stored_profile.get("play_style_identity", "") or current_play_style
    current_play_style_value = match_play_style or default_play_style
    if current_play_style_value in play_style_options:
        play_style_index = play_style_options.index(current_play_style_value)
        play_style_custom_value = ""
    elif current_play_style_value:
        play_style_index = len(play_style_options) - 1
        play_style_custom_value = current_play_style_value
    else:
        play_style_index = 0
        play_style_custom_value = ""

    def _on_play_style_change():
        value = st.session_state.get("play_style_identity")
        if value is not None:
            updated = stored_profile.copy()
            updated["play_style_identity"] = value
            team_profile.save_team_profile(profile_data_path, team_id, updated)

    play_style_choice = st.selectbox(
        "Play style / identity",
        options=play_style_options,
        index=play_style_index,
        key="play_style_identity",
        on_change=_on_play_style_change,
        help="How you want this team to behave with and without the ball.",
    )
    play_style_value = play_style_choice
    if play_style_choice == "Custom":
        play_style_custom_value = st.text_input(
            "Custom play style",
            value=play_style_custom_value,
            key="custom_play_style",
            placeholder="e.g. High press, possession-focused, counter-attacking",
        )
        play_style_value = play_style_custom_value.strip()

# Row 2: Season objective
st.markdown("<a id='anchor_season_objective'></a>", unsafe_allow_html=True)
season_objective_options = config.TEAM_SEASON_OBJECTIVES + ["Custom"]
raw_objective = team_row.get('season_objectives', '')
default_season_objective = stored_profile.get("default_season_objective", "Custom")
current_objective_val = stored_profile.get("season_objectives", "").strip() or str(raw_objective).strip() or default_season_objective
if current_objective_val in season_objective_options:
    season_index = season_objective_options.index(current_objective_val)
    season_custom_value = ""
elif current_objective_val:
    season_index = len(season_objective_options) - 1
    season_custom_value = current_objective_val
else:
    season_index = 0
    season_custom_value = ""

def _on_season_objective_change():
    value = st.session_state.get("season_objective")
    if value is not None:
        updated = stored_profile.copy()
        updated["season_objectives"] = value
        team_profile.save_team_profile(profile_data_path, team_id, updated)

season_choice = st.selectbox(
    "Season objective",
    options=season_objective_options,
    index=season_index,
    on_change=_on_season_objective_change,
    key="season_objective",
    help="Align everyone on the primary mission for this season.",
)
season_objectives_value = season_choice
if season_choice == "Custom":
    season_custom_value = st.text_area(
        "Custom objective",
        value=season_custom_value,
        key="custom_objective",
        placeholder="e.g. Develop young players, improve defensive shape, build possession habits",
        height=80,
    )
    season_objectives_value = season_custom_value.strip()

# Edit match details expander
with st.expander("Edit match details"):
    edit_col1, edit_col2 = st.columns(2)

    with edit_col1:
        opponent_edit = st.text_input(
            "Opponent",
            value=upcoming_opponent_readonly or upcoming_opponent_default,
            key="opponent_edit",
            placeholder="Team name",
        )
        match_date_edit = st.date_input(
            "Match date",
            value=match_date_value or pd.Timestamp.today().date(),
            key="match_date_edit",
        )

    with edit_col2:
        time_edit = st.text_input(
            "Kickoff time",
            value=kickoff_time_readonly or "",
            key="time_edit",
            placeholder="e.g., 7:00 PM",
        )
        location_edit = st.text_input(
            "Location",
            value=location_readonly or "",
            key="location_edit",
            placeholder="Stadium or field name",
        )

# Row 5: Focus areas
st.markdown("<a id='anchor_focus_tags'></a>", unsafe_allow_html=True)
focus_options = sorted(set(config.DRILL_TAGS).union(existing_focus_tags))
focus_selection = st.multiselect(
    "Focus areas (tagged)",
    options=focus_options,
    default=stored_profile.get("focus_tags", existing_focus_tags),
    help="These tags describe team priorities. Matching drill tags boosts recommendations."
)
extra_focus_input = st.text_input(
    "Additional focus tags (comma separated)",
    value=stored_profile.get("extra_focus_tags", ""),
    placeholder="Leadership, Mental Toughness, etc.",
    help="Add quick one-off tags separated by commas."
)

# Row 6: Expandable text areas for detailed notes
st.markdown("<a id='anchor_key_players'></a>", unsafe_allow_html=True)
with st.expander("Key players / notes"):
    key_players_input = st.text_area(
        "",
        value=stored_profile.get("key_players_notes", key_players_default),
        height=120,
        placeholder="One entry per line",
        key="key_players_area",
    )

st.markdown("<a id='anchor_injuries'></a>", unsafe_allow_html=True)
with st.expander("Injuries / availability"):
    injuries_input = st.text_area(
        "",
        value=stored_profile.get("injury_notes", injuries_default),
        height=120,
        placeholder="One entry per line",
        key="injuries_area",
    )

with st.expander("General notes"):
    notes_input = st.text_area(
        "",
        value=stored_profile.get("general_notes", team_row.get('notes', '')),
        height=120,
        placeholder="Scouting intel, training reminders, parent communication, etc.",
        key="general_notes_area",
    )

# ============================================================================
# SAVE BUTTON AND HANDLER
# ============================================================================
submitted = st.button("Save team profile", type="primary")

if submitted:
    extra_focus = [item.strip() for item in extra_focus_input.split(",") if item.strip()]
    focus_value = "|".join(dict.fromkeys([*focus_selection, *extra_focus]))
    key_players_value = "|".join([item.strip() for item in key_players_input.splitlines() if item.strip()])
    injuries_value = "|".join([item.strip() for item in injuries_input.splitlines() if item.strip()])

    # Use edited values if available, otherwise use readonly/default values
    final_opponent = opponent_edit.strip() if opponent_edit.strip() else upcoming_opponent_readonly
    final_date = match_date_edit.isoformat() if match_date_edit else ""
    final_time = time_edit.strip() if time_edit.strip() else kickoff_time_readonly
    final_location = location_edit.strip() if location_edit.strip() else location_readonly

    profile_payload = {
        "preferred_formation": preferred_formation_value,
        "play_style_identity": play_style_value,
        "custom_play_style": play_style_custom_value,
        "season_objective": season_objectives_value,
        "custom_objective": season_custom_value,
        "focus_tags": focus_selection,
        "extra_focus_tags": extra_focus_input.strip(),
        "key_players_notes": key_players_input,
        "injury_notes": injuries_input,
        "general_notes": notes_input.strip(),
        "upcoming_match_date": final_date,
        "kickoff_time": final_time,
        "upcoming_opponent": final_opponent,
        "location": final_location,
    }
    try:
        team_profile.save_team_profile(profile_data_path, team_id, profile_payload)
        st.success("Team profile saved.")
    except Exception as exc:
        st.error(f"Couldn't save team profile: {exc}")

st.divider()
st.subheader("Focus & Key Players")

focus_pills = _explode(teams_df.loc[teams_df['team_id'] == team_id, 'focus_areas'].iloc[0])
if focus_pills:
    st.markdown("**Focus Areas:** " + ", ".join(f"`{pill}`" for pill in focus_pills))
else:
    st.markdown("**Focus Areas:** Add focus areas above to drive planning suggestions.")

key_player_list = _explode(teams_df.loc[teams_df['team_id'] == team_id, 'key_players'].iloc[0])
injury_list = _explode(teams_df.loc[teams_df['team_id'] == team_id, 'injuries'].iloc[0])

cols_focus = st.columns(2)
with cols_focus[0]:
    st.markdown("**Key Players / Notes**")
    if key_player_list:
        for player in key_player_list:
            st.markdown(f"- {player}")
    else:
        st.caption("No key players logged yet.")

with cols_focus[1]:
    st.markdown("**Injuries / Availability**")
    if injury_list:
        for injury in injury_list:
            st.markdown(f"- {injury}")
    else:
        st.caption("Healthy squad! Keep it going.")

st.divider()
st.subheader("Recent Practice Snapshot")

history_mtime = practice_history.get_history_mtime(team_id, st.session_state.data_path)
history_df = practice_history.load_practice_history(team_id, st.session_state.data_path, history_mtime)
if len(history_df) == 0:
    st.info("No sessions saved yet for this team. Generate one from the Practice Generator.")
else:
    history_df['session_date'] = pd.to_datetime(history_df['session_date']).dt.date

    # Top KPIs
    sessions_metric_col, total_time_col, last_session_col = st.columns(3)
    sessions_metric_col.metric("Sessions Logged", len(history_df))
    total_time_col.metric("Total Minutes", int(history_df['total_time'].sum()))
    last_session_col.metric("Last Session", str(history_df['session_date'].max()))

    st.divider()

    # Last 5 Sessions table - improved layout
    st.markdown("**Last 5 Sessions**")

    # Prepare data for display
    recent_sessions = history_df.tail(5).copy()
    recent_sessions = recent_sessions.sort_values('session_date', ascending=False)

    # Format the display
    display_df = pd.DataFrame({
        "Date": pd.to_datetime(recent_sessions['session_date']).dt.strftime("%a, %b %d"),
        "Session": recent_sessions['session_name'],
        "Players": recent_sessions['num_players'].astype(int),
        "Duration (min)": recent_sessions['total_time'].astype(int),
        "Categories": recent_sessions['categories'].apply(lambda x: ", ".join(_explode(x)[:2]) if pd.notna(x) else "—")
    })

    st.dataframe(
        display_df,
        hide_index=True,
        use_container_width=True,
        height=250
    )
