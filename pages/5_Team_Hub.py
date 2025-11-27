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
    st.switch_page("pages/0_🚀_Coach_Onboarding.py")
if edit_sections[1].button("Update practice schedule"):
    st.switch_page("pages/0_🚀_Coach_Onboarding.py")
if edit_sections[2].button("Edit focus/style"):
    st.switch_page("pages/0_🚀_Coach_Onboarding.py")

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

# --- Schedule load/state -----------------------------------------------------
data_path = st.session_state.get("data_path") or config.get_data_path()
schedule_df = schedule.load_schedule(Path(data_path), team_id)
if "schedule_edit_df" not in st.session_state:
    st.session_state.schedule_edit_df = schedule_df.copy()

# Upload & parse
uploader = st.file_uploader("Upload PDF schedule", type=["pdf"])
if uploader and st.button("Parse PDF into draft schedule"):
    try:
        events = schedule.parse_schedule_pdf(uploader)
        parsed_df = schedule.events_to_dataframe(events)
        if parsed_df.empty:
            st.warning("No events detected. Check that the PDF has selectable text and visible dates.")
        else:
            combined = pd.concat([st.session_state.schedule_edit_df, parsed_df], ignore_index=True)
            combined = combined.drop_duplicates(subset=["date", "time", "type", "opponent", "location"])
            st.session_state.schedule_edit_df = combined
            st.success(f"Parsed {len(parsed_df)} event(s) from PDF.")
    except Exception as exc:
        st.error(f"Could not parse PDF: {exc}")

st.markdown("#### Review & Edit Schedule")
edited_df = st.data_editor(
    st.session_state.schedule_edit_df,
    num_rows="dynamic",
    hide_index=True,
    use_container_width=True,
    column_config={
        "date": st.column_config.DateColumn("Date"),
        "time": st.column_config.TextColumn("Time"),
        "type": st.column_config.SelectboxColumn("Type", options=["practice", "game"]),
        "opponent": st.column_config.TextColumn("Opponent"),
        "location": st.column_config.TextColumn("Location"),
        "notes": st.column_config.TextColumn("Notes"),
        "source": st.column_config.SelectboxColumn("Source", options=["parsed", "manual"]),
    },
)
st.session_state.schedule_edit_df = edited_df

save_col, download_col = st.columns(2)
with save_col:
    if st.button("💾 Save schedule"):
        try:
            schedule.save_schedule(Path(data_path), team_id, edited_df)
            st.success("Schedule saved for this team.")
        except Exception as exc:
            st.error(f"Could not save schedule: {exc}")

with download_col:
    if not schedule_df.empty:
        csv_bytes = schedule_df.to_csv(index=False).encode()
        st.download_button(
            "⬇️ Download current schedule CSV",
            data=csv_bytes,
            file_name=f"practice_game_schedule_{team_id}.csv",
            mime="text/csv",
        )
    else:
        st.caption("No saved schedule yet.")

st.markdown("#### Calendar View")
if edited_df.empty:
    st.info("No events to show yet. Add or parse events above.")
else:
    show_practice = st.checkbox("Show practices", value=True)
    show_games = st.checkbox("Show games", value=True)
    filtered = edited_df.copy()
    if not show_practice:
        filtered = filtered[filtered["type"] != "practice"]
    if not show_games:
        filtered = filtered[filtered["type"] != "game"]
    filtered["date_obj"] = pd.to_datetime(filtered["date"], errors="coerce").dt.date
    filtered = filtered.dropna(subset=["date_obj"])
    if filtered.empty:
        st.info("No events match the current filters.")
    else:
        min_date = min(filtered["date_obj"])
        max_date = max(filtered["date_obj"])
        today = pd.Timestamp.today().date()
        default_month = date(today.year, today.month, 1)
        first_day = date(min_date.year, min_date.month, 1)
        last_day = date(max_date.year, max_date.month, 1)
        selected_month = st.date_input(
            "Month",
            value=default_month,
            min_value=first_day,
            max_value=last_day,
        )

        def render_monthly_calendar(df: pd.DataFrame, month_start: date):
            import calendar as cal

            def _icon(evt_type: str) -> str:
                return "🟢" if evt_type == "practice" else "🔵"

            events_map = {}
            for row in df.itertuples():
                events_map.setdefault(row.date_obj, []).append(row)

            month_calendar = cal.Calendar(firstweekday=0).monthdatescalendar(month_start.year, month_start.month)
            st.markdown("##### Calendar")
            # Weekday header
            header_cols = st.columns(7)
            for idx, name in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
                header_cols[idx].markdown(f"**{name}**")

            for week in month_calendar:
                cols = st.columns(7)
                for idx, day in enumerate(week):
                    if day.month != month_start.month:
                        cols[idx].markdown("&nbsp;", unsafe_allow_html=True)
                        continue
                    cols[idx].markdown(f"**{day.day}**")
                    events = events_map.get(day, [])
                    for evt in events[:3]:
                        parts = [f"{_icon(evt.type)}"]
                        if evt.time:
                            parts.append(evt.time)
                        parts.append(evt.type.title())
                        if evt.opponent:
                            parts.append(f"vs {evt.opponent}")
                        cols[idx].markdown(" · ".join(parts))
                    if len(events) > 3:
                        cols[idx].caption(f"+{len(events) - 3} more")

        render_monthly_calendar(filtered, selected_month)

formation_options = ["4-3-3", "4-4-2", "3-5-2", "4-2-3-1", "4-1-4-1", "Custom"]
raw_formation = team_row.get('formation', '')
current_formation = str(raw_formation) if raw_formation is not None else ''
current_formation = current_formation.strip()
if current_formation and current_formation not in formation_options:
    formation_options.append(current_formation)
formation_index = formation_options.index(current_formation) if current_formation in formation_options else 0

col_a, col_b = st.columns(2)
st.markdown("<a id='anchor_age_group'></a>", unsafe_allow_html=True)
st.markdown("<a id='anchor_formation'></a>", unsafe_allow_html=True)
formation = col_a.selectbox(
    "Preferred formation",
    options=formation_options,
    index=formation_index,
    help="Select the formation you run most often."
)
play_style_options = config.TEAM_PLAY_STYLES + ["Custom"]
raw_play_style = team_row.get('play_style', '')
current_play_style = str(raw_play_style) if raw_play_style is not None else ''
current_play_style = current_play_style.strip()
if current_play_style in config.TEAM_PLAY_STYLES:
    play_style_index = play_style_options.index(current_play_style)
    play_style_custom_value = ""
elif current_play_style:
    play_style_index = len(play_style_options) - 1
    play_style_custom_value = current_play_style
else:
    play_style_index = 0
    play_style_custom_value = ""
st.markdown("<a id='anchor_play_style'></a>", unsafe_allow_html=True)
play_style_choice = col_b.selectbox(
    "Play style / identity",
    options=play_style_options,
    index=play_style_index,
    help="Choose the style that best matches this team."
)
play_style_value = play_style_choice
if play_style_choice == "Custom":
    with col_b:
        play_style_custom_value = st.text_input(
            "Custom play style",
            value=play_style_custom_value,
            placeholder="Describe the unique identity",
            key=f"custom_play_style_input_{team_id}"
        )
        play_style_value = play_style_custom_value.strip()

current_match_date = team_row.get('upcoming_match_date')
match_date_value = None
if current_match_date:
    try:
        parsed_date = pd.to_datetime(current_match_date, errors='coerce')
        if pd.notna(parsed_date):
            match_date_value = parsed_date.date()
    except Exception:
        match_date_value = None
match_date = col_a.date_input(
    "Upcoming match date",
    value=match_date_value or pd.Timestamp.today().date(),
    help="Select the next fixture date."
)
time_options = [f"{hour:02d}:{minute:02d}" for hour in range(0, 24) for minute in (0, 30)]
stored_time = team_row.get('upcoming_match_time') or "18:00"
if stored_time not in time_options:
    stored_time = "18:00"
match_time = col_a.selectbox(
    "Kickoff time",
    options=time_options,
    index=time_options.index(stored_time),
    help="Set the kickoff time (24h)."
)
upcoming_opponent = col_a.text_input(
    "Upcoming opponent/team",
    value=team_row.get('upcoming_match_opponent', ''),
    placeholder="Opponent name"
)
season_objective_options = config.TEAM_SEASON_OBJECTIVES + ["Custom"]
raw_objective = team_row.get('season_objectives', '')
current_objective = str(raw_objective) if raw_objective is not None else ''
current_objective = current_objective.strip()
if current_objective in config.TEAM_SEASON_OBJECTIVES:
    season_index = season_objective_options.index(current_objective)
    season_custom_value = ""
elif current_objective:
    season_index = len(season_objective_options) - 1
    season_custom_value = current_objective
else:
    season_index = 0
    season_custom_value = ""
season_choice = col_b.selectbox(
    "Season objective",
    options=season_objective_options,
    index=season_index,
    help="Align everyone on the primary mission."
)
season_objectives_value = season_choice
if season_choice == "Custom":
    with col_b:
        season_custom_value = st.text_input(
            "Custom objective",
            value=season_custom_value,
            placeholder="Describe your specific goal",
            key=f"custom_objective_input_{team_id}"
        )
        season_objectives_value = season_custom_value.strip()

st.markdown("<a id='anchor_practice_schedule'></a>", unsafe_allow_html=True)
practice_schedule = st.text_input(
    "Practice schedule (e.g., Mon/Wed 6-7:30p)",
    value=str(team_row.get('practice_schedule', '') or '').strip(),
    placeholder="Days/times",
)

st.markdown("<a id='anchor_focus_tags'></a>", unsafe_allow_html=True)
focus_options = sorted(set(config.DRILL_TAGS).union(existing_focus_tags))
focus_selection = st.multiselect(
    "Focus areas (tagged)",
    options=focus_options,
    default=existing_focus_tags,
    help="These tags describe team priorities. Matching drill tags boosts recommendations."
)
extra_focus_input = st.text_input(
    "Additional focus tags (comma separated)",
    value="",
    placeholder="Leadership, Mental Toughness, etc.",
    help="Add quick one-off tags separated by commas; they're appended to the list above."
)
st.markdown("<a id='anchor_key_players'></a>", unsafe_allow_html=True)
key_players_input = st.text_area(
    "Key players / notes (one per line)",
    value=key_players_default,
    height=120
)
st.markdown("<a id='anchor_injuries'></a>", unsafe_allow_html=True)
injuries_input = st.text_area(
    "Injuries / availability (one per line)",
    value=injuries_default,
    height=120
)
notes_input = st.text_area(
    "General notes",
    value=team_row.get('notes', ''),
    placeholder="Scouting intel, training reminders, parent communication, etc."
)
submitted = st.button("Save team profile", type="primary")

if submitted:
    extra_focus = [item.strip() for item in extra_focus_input.split(",") if item.strip()]
    focus_value = "|".join(dict.fromkeys([*focus_selection, *extra_focus]))
    key_players_value = "|".join([item.strip() for item in key_players_input.splitlines() if item.strip()])
    injuries_value = "|".join([item.strip() for item in injuries_input.splitlines() if item.strip()])
    update_fields = {
        'formation': formation,
        'play_style': play_style_value,
        'upcoming_match_date': match_date.isoformat(),
        'upcoming_match_time': match_time,
        'upcoming_match_opponent': upcoming_opponent.strip(),
        'season_objectives': season_objectives_value,
        'focus_areas': focus_value,
        'key_players': key_players_value,
        'injuries': injuries_value,
        'practice_schedule': practice_schedule.strip(),
        'notes': notes_input.strip(),
    }
    for field, value in update_fields.items():
        teams_df.loc[teams_df['team_id'] == team_id, field] = value
    _persist_teams(teams_df)
    st.session_state.selected_team = teams_df[teams_df['team_id'] == team_id].iloc[0].to_dict()
    st.success("Team profile updated.")

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
    sessions_metric_col, total_time_col, last_session_col = st.columns(3)
    sessions_metric_col.metric("Sessions Logged", len(history_df))
    total_time_col.metric("Total Minutes", int(history_df['total_time'].sum()))
    last_session_col.metric("Last Session", str(history_df['session_date'].max()))

    all_categories = []
    for entry in history_df['categories'].fillna(""):
        all_categories.extend(_explode(entry))
    cat_series = pd.Series(all_categories)
    if not cat_series.empty:
        st.bar_chart(cat_series.value_counts(), use_container_width=True)

    st.markdown("**Last 5 Sessions**")
    st.dataframe(
        history_df[['session_date', 'session_name', 'num_players', 'total_time']].tail(5),
        hide_index=True,
        use_container_width=True
    )
