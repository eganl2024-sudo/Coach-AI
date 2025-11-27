"""Practice History - view, filter, and reuse past sessions."""
import calendar
import json
from datetime import date, timedelta
from pathlib import Path
import sys

import pandas as pd
import streamlit as st

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import config
import data_loader
import practice_history
import session_detail_view
import session_state
import session_state as ui_session
import ui_components
from models import PracticeConfig, PracticeSession, SessionDrill


st.set_page_config(page_title="Practice History", page_icon="⚽", layout="wide")

ui_components.render_nav(active_label="Past Sessions")
st.divider()

st.title("Past Sessions")
st.caption("See recent sessions and quickly reuse favorites.")

# --- session state setup ----------------------------------------------------
session_state.init_session_state()
if "data_path" not in st.session_state:
    st.session_state.data_path = config.get_data_path()

if st.session_state.drills_df is None:
    st.session_state.drills_df = data_loader.load_drills(st.session_state.data_path)
if st.session_state.teams_df is None:
    st.session_state.teams_df = data_loader.load_teams(st.session_state.data_path)
if st.session_state.selected_team is None and len(st.session_state.teams_df) > 0:
    st.session_state.selected_team = st.session_state.teams_df.iloc[0].to_dict()
if st.session_state.selected_team is None:
    st.warning("Please add a team to start tracking practice history.")
    st.stop()

team = st.session_state.selected_team
team_id = team["team_id"]
history_mtime = practice_history.get_history_mtime(team_id, st.session_state.data_path)
history_df = practice_history.load_practice_history(team_id, st.session_state.data_path, history_mtime).copy()
history_load_error = history_df.attrs.get("load_error")
history_repair = history_df.attrs.get("repair_info")

# ensure required columns
for col in ["avg_intensity_score", "intensity_level"]:
    if col not in history_df.columns:
        history_df[col] = None if col == "avg_intensity_score" else ""

if "season_segment" not in history_df.columns:
    history_df["season_segment"] = history_df["session_date"].apply(practice_history.infer_season_segment)
else:
    history_df["season_segment"] = history_df["season_segment"].fillna("").astype(str)
    mask_missing = history_df["season_segment"].str.strip().eq("")
    if mask_missing.any():
        history_df.loc[mask_missing, "season_segment"] = history_df.loc[mask_missing, "session_date"].apply(
            practice_history.infer_season_segment
        )

if len(history_df) == 0:
    if history_load_error:
        st.info(history_load_error)
    else:
        st.info("No practices saved yet. Generate a session from the Practice Generator page to populate history.")
    st.page_link("pages/2_Practice_Generator.py", label="Create your first practice")
    st.stop()

if history_repair and history_repair.get("was_repaired"):
    added = ", ".join(history_repair.get("added_columns", [])) or "columns"
    st.warning(f"Practice history file was missing {added}; defaults were applied.")

history_df["session_date"] = pd.to_datetime(history_df["session_date"]).dt.date
today = date.today()

# --- state defaults and reset handling before controls ----------------------
if "selected_day_history" not in st.session_state:
    st.session_state.selected_day_history = None
if "library_added_sessions" not in st.session_state:
    st.session_state.library_added_sessions = set()
if "time_window_selector_history2" not in st.session_state:
    st.session_state.time_window_selector_history2 = "Last 30 days"
if "favorites_only_toggle_history" not in st.session_state:
    st.session_state.favorites_only_toggle_history = False
if "intensity_filter_history" not in st.session_state:
    st.session_state.intensity_filter_history = ["Low", "Medium", "High"]

if st.session_state.get("reset_filters_history_trigger"):
    st.session_state.time_window_selector_history2 = "Last 30 days"
    st.session_state.favorites_only_toggle_history = False
    st.session_state.intensity_filter_history = ["Low", "Medium", "High"]
    st.session_state.selected_day_history = None
    st.session_state.reset_categories_history = True
    st.session_state.reset_filters_history_trigger = False

# --- controls ---------------------------------------------------------------
controls_time, controls_fav, controls_sort = st.columns([1.6, 1.0, 1.2])
with controls_time:
    time_window = st.radio(
        "Time window",
        ["This week", "Last 30 days", "All time"],
        horizontal=True,
        key="time_window_selector_history2",
    )
with controls_fav:
    show_favorites_only = st.toggle("Show favorites only", value=False, key="favorites_only_toggle_history")
with controls_sort:
    sort_options = [
        "Date (newest)",
        "Date (oldest)",
        "Favorites first",
        "Intensity (low to high)",
        "Intensity (high to low)",
    ]
    sort_by = st.selectbox(
        "Sort by",
        sort_options,
        index=0,
        key="sort_by_select_history2",
    )
st.markdown("")  # spacer

# category/intensity filters
category_col = "primary_category" if "primary_category" in history_df.columns else ("categories" if "categories" in history_df.columns else None)
selected_categories = []
if category_col:
    all_categories = sorted(
        {
            part.strip()
            for cell in history_df[category_col].fillna("")
            for part in str(cell).split("|")
            if part.strip()
        }
    )
    # Ensure category filter state is initialized before widget instantiation
    if "category_filter_history" not in st.session_state:
        st.session_state.category_filter_history = all_categories
    if st.session_state.get("reset_categories_history"):
        st.session_state.category_filter_history = all_categories
        st.session_state.reset_categories_history = False

    selected_categories = st.multiselect(
        "Categories",
        options=all_categories,
        default=st.session_state.category_filter_history,
        key="category_filter_history",
    )

intensity_options = ["Low", "Medium", "High"]
selected_intensity_levels = st.multiselect(
    "Intensity levels",
    options=intensity_options,
    default=intensity_options,
    key="intensity_filter_history",
)

# Reset filters button to restore sensible defaults
if st.button("Reset filters", key="reset_filters_history"):
    st.session_state.reset_filters_history_trigger = True
    st.rerun()

# If a reset was deferred for categories (needs options), apply it before widget instantiation
if st.session_state.get("reset_categories_history") and category_col:
    st.session_state.category_filter_history = all_categories
    st.session_state.reset_categories_history = False

# --- filtering --------------------------------------------------------------
display_df = history_df.copy()
display_df["date_norm"] = pd.to_datetime(display_df["session_date"], errors="coerce").dt.date
display_df = display_df.dropna(subset=["date_norm"]).copy()

# category filter
if category_col and selected_categories:
    display_df = display_df[
        display_df[category_col].apply(
            lambda cell: any(part.strip() in selected_categories for part in str(cell).split("|") if part.strip())
        )
    ].copy()

# intensity filter
if selected_intensity_levels:
    display_df = display_df[display_df["intensity_level"].isin(selected_intensity_levels)].copy()

# time window filter (rolling windows)
start_date = end_date = None
if time_window == "This week":
    end_date = today
    start_date = today - timedelta(days=6)
elif time_window == "Last 30 days":
    end_date = today
    start_date = today - timedelta(days=29)

if start_date and end_date:
    mask = (display_df["date_norm"] >= start_date) & (display_df["date_norm"] <= end_date)
    display_df = display_df.loc[mask].copy()

# clear selected day if it's outside the current window
selected_day = st.session_state.selected_day_history
if selected_day and start_date and end_date:
    if not (start_date <= selected_day <= end_date):
        selected_day = None
        st.session_state.selected_day_history = None

# favorites
fav_col = "is_favorite" if "is_favorite" in display_df.columns else None
if show_favorites_only and fav_col:
    display_df = display_df[display_df[fav_col] == True].copy()

# snapshot before day filter
pre_day_df = display_df.copy()

# day selection UI

def render_day_grid(dates, events_by_day, key_prefix, show_weekday=False):
    """
    Render dates in rows of up to 7 columns. Dates with sessions are buttons;
    empty dates are shown as grey text. Clicking sets selected_day_history.
    """
    rows = [dates[i : i + 7] for i in range(0, len(dates), 7)]
    for row in rows:
        cols = st.columns(7)
        for day_obj, col in zip(row, cols):
            count = events_by_day.get(day_obj, 0)
            label = day_obj.strftime("%a %d" if show_weekday else "%d")
            is_selected = st.session_state.selected_day_history == day_obj
            if count > 0:
                display_label = label if count == 1 else f"{label} ({count})"
                if is_selected:
                    display_label = f"* {display_label}"
                if col.button(display_label, key=f"{key_prefix}_{day_obj.isoformat()}"):
                    st.session_state.selected_day_history = day_obj
            else:
                col.caption(label)


def _weekday_index_sun_first(d):
    """Map Monday(0)..Sunday(6) to Sun-first index 0..6."""
    return (d.weekday() + 1) % 7

if time_window == "This week":
    strip_start = today - timedelta(days=6)
    days = [strip_start + timedelta(days=i) for i in range(7)]
    events_by_day = pre_day_df["date_norm"].value_counts().to_dict()
    render_day_grid(days, events_by_day, key_prefix="week_day_btn", show_weekday=True)

elif time_window == "Last 30 days":
    start_30 = today - timedelta(days=29)
    days = [start_30 + timedelta(days=i) for i in range(30)]
    events_by_day = pre_day_df["date_norm"].value_counts().to_dict()
    # Build practice/game counts for dot indicators
    practice_by_day = {}
    game_by_day = {}
    type_col = None
    for col in ["event_type", "session_type", "type"]:
        if col in pre_day_df.columns:
            type_col = col
            break
    for _, row in pre_day_df.iterrows():
        d = row.get("date_norm")
        if d is None:
            continue
        t = (row.get(type_col) if type_col else "").strip().lower() if isinstance(row.get(type_col), str) else ""
        if t == "game":
            game_by_day[d] = game_by_day.get(d, 0) + 1
        else:
            practice_by_day[d] = practice_by_day.get(d, 0) + 1

    # Sun-Sat header
    header_cols = st.columns(7)
    for col, name in zip(header_cols, ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]):
        col.markdown(f"**{name}**")

    # Pad dates so the first appears under its weekday, and rows are full weeks
    start_idx = _weekday_index_sun_first(start_30)
    padded_dates = [None] * start_idx + days
    while len(padded_dates) % 7 != 0:
        padded_dates.append(None)

    rows = [padded_dates[i : i + 7] for i in range(0, len(padded_dates), 7)]
    for row in rows:
        cols = st.columns(7)
        for day_obj, col in zip(row, cols):
            if day_obj is None:
                col.markdown("&nbsp;")
                continue
            count = events_by_day.get(day_obj, 0)
            label = day_obj.strftime("%d") if count <= 1 else f"{day_obj.day} ({count})"
            is_selected = st.session_state.selected_day_history == day_obj
            if count > 0:
                display_label = f"[{label}]" if is_selected else label
                if col.button(display_label, key=f"last30_day_{day_obj.isoformat()}"):
                    st.session_state.selected_day_history = day_obj
            else:
                col.caption(label)
            # Dots for practice/game indicators
            practice_count = practice_by_day.get(day_obj, 0)
            game_count = game_by_day.get(day_obj, 0)
            dots = []
            if practice_count > 0:
                dots.append(
                    "<span style='display:inline-block;width:0.35rem;height:0.35rem;border-radius:50%;background-color:black;margin-right:2px;'></span>"
                )
            if game_count > 0:
                dots.append(
                    "<span style='display:inline-block;width:0.35rem;height:0.35rem;border-radius:50%;background-color:green;'></span>"
                )
            if dots:
                col.markdown(
                    "<div style='margin-top:2px; line-height:1;'>"
                    + "".join(dots)
                    + "</div>",
                    unsafe_allow_html=True,
                )

# clear date filter control (shows only when a date is selected)
if st.session_state.selected_day_history is not None and time_window in ("This week", "Last 30 days"):
    if st.button("Clear date filter", key="clear_date_filter_history"):
        st.session_state.selected_day_history = None

# apply selected day filter for windows that support it
selected_day = st.session_state.selected_day_history
if selected_day and time_window in ("This week", "Last 30 days"):
    display_df = pre_day_df[pre_day_df["date_norm"] == selected_day].copy()
else:
    display_df = pre_day_df.copy()

# sorting
if sort_by == "Date (oldest)":
    display_df = display_df.sort_values(by="date_norm", ascending=True)
elif sort_by == "Favorites first" and fav_col:
    display_df = display_df.sort_values(by=[fav_col, "date_norm"], ascending=[False, False])
elif sort_by == "Intensity (low to high)":
    df_sorted = display_df.copy()
    df_sorted["intensity_sort"] = df_sorted["avg_intensity_score"].fillna(float("inf"))
    display_df = df_sorted.sort_values(by=["intensity_sort", "date_norm"], ascending=[True, False])
elif sort_by == "Intensity (high to low)":
    df_sorted = display_df.copy()
    df_sorted["intensity_sort"] = df_sorted["avg_intensity_score"].fillna(-float("inf"))
    display_df = df_sorted.sort_values(by=["intensity_sort", "date_norm"], ascending=[False, False])
else:
    display_df = display_df.sort_values(by="date_norm", ascending=False)

display_df = display_df.reset_index(drop=True)


# --- summary ---------------------------------------------------------------
def _summary_bar(df: pd.DataFrame) -> None:
    num_sessions = len(df)

    avg_minutes = "N/A"
    median_minutes = "N/A"
    if "total_time" in df.columns and len(df):
        try:
            avg_val = df["total_time"].mean()
            med_val = df["total_time"].median()
            avg_minutes = f"{int(round(avg_val))} min" if not pd.isna(avg_val) else "N/A"
            median_minutes = f"{int(round(med_val))} min" if not pd.isna(med_val) else "N/A"
        except Exception:
            pass

    avg_intensity_metric = "N/A"
    if "avg_intensity_score" in df.columns and len(df):
        try:
            intensity_val = df["avg_intensity_score"].mean(skipna=True)
            if not pd.isna(intensity_val):
                avg_intensity_metric = f"{intensity_val:.1f}"
        except Exception:
            pass

    common_focus = "N/A"
    if "session_tags" in df.columns and len(df):
        tags = []
        for entry in df["session_tags"].fillna(""):
            tags.extend([t.strip() for t in str(entry).split("|") if t.strip()])
        if tags:
            common_focus = pd.Series(tags).value_counts().idxmax()
    if common_focus == "N/A" and "categories" in df.columns and len(df):
        cats = []
        for entry in df["categories"].fillna(""):
            cats.extend([c.strip() for c in str(entry).split("|") if c.strip()])
        if cats:
            common_focus = pd.Series(cats).value_counts().idxmax()

    date_range = "No sessions in selected range"
    if len(df) and "date_norm" in df.columns:
        earliest = df["date_norm"].min()
        latest = df["date_norm"].max()
        date_range = f"{earliest:%Y-%m-%d} to {latest:%Y-%m-%d}"

    st.markdown("**Summary for displayed sessions**")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total sessions", num_sessions)
    c2.metric("Average length", avg_minutes)
    c3.metric("Median length", median_minutes)
    c4.metric("Most common category", common_focus)
    c5.metric("Date range", date_range)
    c6.metric("Average intensity", avg_intensity_metric)


# detail modal
if "viewing_session" in st.session_state:
    session_to_view = st.session_state["viewing_session"]

    st.markdown("---")
    st.markdown("## Session Details")
    session_detail_view.render_session_detail(session_to_view, team_id, st.session_state.data_path)
    st.markdown("---")
    if st.button("← Back to Past Sessions", type="primary"):
        del st.session_state["viewing_session"]
        st.rerun()
    st.stop()

# --- summary + timeline -----------------------------------------------------
_summary_bar(display_df)

st.subheader("Timeline")
if len(display_df) == 0:
    if st.session_state.selected_day_history:
        selected_label = st.session_state.selected_day_history.strftime("%a %b %d")
        st.info(
            f"No sessions on **{selected_label}** with the current filters. "
            "Try changing categories, intensity levels, or clear the date filter."
        )
    else:
        st.info(
            "No sessions match the current time window and filters. "
            "Try changing the time window, categories, or intensity levels."
        )
else:
    if time_window == "This week":
        timeline_label = "This Week"
    elif time_window == "Last 30 days":
        timeline_label = "Last 30 days"
    else:
        timeline_label = "All time"

    if selected_day:
        timeline_label = f"{timeline_label} - {selected_day:%a %b %d}"

    st.markdown(f"### {timeline_label}")

    for idx, session_row in display_df.iterrows():
        session_date = session_row.get("date_norm")
        session_name = session_row.get("session_name") or "Practice"
        total_time = session_row.get("total_time", 0)
        categories = session_row.get("categories", "")
        num_players = session_row.get("num_players", 0)
        is_favorite = bool(session_row.get("is_favorite", False))
        coach_notes = str(session_row.get("coach_notes", "") or "").strip()
        intensity_level = session_row.get("intensity_level", "") or ""
        intensity_score = session_row.get("avg_intensity_score", None)
        session_key = f"{team_id}_{session_date}_{session_name}"

        with st.container():
            main_cols = st.columns([0.5, 5, 1.5])

            with main_cols[0]:
                star_label = "?" if is_favorite else "?"
                if st.button(star_label, key=f"star_{idx}", help="Add to Practice Library"):
                    success = practice_history.set_session_favorite(
                        team_id,
                        session_date,
                        session_name,
                        not is_favorite,
                        st.session_state.data_path,
                    )
                    if success:
                        st.rerun()

            with main_cols[1]:
                nice_date = session_date.strftime("%a %b %d, %Y") if hasattr(session_date, "strftime") else str(session_date)
                st.markdown(f"**{nice_date} - {session_name} ({total_time} min)**")
                if intensity_level and intensity_score is not None and not pd.isna(intensity_score):
                    intensity_str = f"Intensity: {intensity_level} ({intensity_score:.1f})"
                elif intensity_level:
                    intensity_str = f"Intensity: {intensity_level}"
                else:
                    intensity_str = ""
                cat_list = [c.strip() for c in str(categories).split("|") if c.strip()]
                cat_text = ", ".join(cat_list) if cat_list else "None"
                meta_parts = [f"Categories: {cat_text}", f"Players: {num_players}"]
                if intensity_str:
                    meta_parts.append(intensity_str)
                st.caption(" | ".join(meta_parts))

                if coach_notes:
                    preview = coach_notes[:80] + ("..." if len(coach_notes) > 80 else "")
                    st.caption(f"Notes: {preview}")

            with main_cols[2]:
                if not is_favorite:
                    if session_key in st.session_state.library_added_sessions:
                        st.button("Saved to Practice Library", key=f"fav_{idx}", disabled=True)
                    else:
                        if st.button("Add to Practice Library", key=f"fav_{idx}", type="primary"):
                            added = False
                            try:
                                session_obj = practice_history.load_practice_session_from_record(session_row)
                                if session_obj:
                                    added = practice_history.save_session_as_template(session_obj, st.session_state.data_path)
                                else:
                                    added = practice_history.set_session_favorite(
                                        team_id,
                                        session_date,
                                        session_name,
                                        True,
                                        st.session_state.data_path,
                                    )
                            except Exception as exc:
                                added = False
                                print(f"Library add failed: {exc}")
                            if added:
                                st.session_state.library_added_sessions.add(session_key)
                                st.success("Added to Practice Library")
                                st.rerun()
                            else:
                                st.error("Could not add to Practice Library")
                else:
                    if st.button("Remove from Library", key=f"unfav_{idx}", type="secondary"):
                        success = practice_history.set_session_favorite(
                            team_id,
                            session_date,
                            session_name,
                            False,
                            st.session_state.data_path,
                        )
                        if success:
                            st.success("Removed from Practice Library")
                            st.rerun()
                        else:
                            st.error("Could not update Practice Library")

                if st.button("View Details", key=f"view_{idx}"):
                    st.session_state["viewing_session"] = session_row.to_dict()
                    st.rerun()
                if st.button("Reuse session", key=f"reuse_{idx}", type="secondary"):
                    session_structure = session_row.get("session_structure", "")
                    if session_structure:
                        try:
                            data = json.loads(session_structure)
                            drills = [SessionDrill.from_dict(d) for d in data.get("drills", [])]
                            cfg_dict = data.get("config", {})
                            config_obj = PracticeConfig(**cfg_dict) if cfg_dict else PracticeConfig(
                                duration_minutes=data.get("duration_minutes", 90),
                                num_players=data.get("num_players", 16),
                                num_drills=len(drills),
                                selected_categories=data.get("selected_categories", []),
                                session_date=str(session_date),
                                session_notes=data.get("session_notes", ""),
                            )
                            session_obj = PracticeSession(
                                session_id=data.get("session_id", "reuse"),
                                team_id=data.get("team_id", team_id),
                                team_name=data.get("team_name", team.get("team_name", "")),
                                session_date=data.get("session_date", str(session_date)),
                                config=config_obj,
                                duration_minutes=data.get("duration_minutes", config_obj.duration_minutes),
                                num_players=data.get("num_players", config_obj.num_players),
                                num_drills=len(drills),
                                selected_categories=data.get("selected_categories", config_obj.selected_categories),
                                drills=drills,
                                team_profile_summary=data.get("team_profile_summary", {}),
                                equipment_needed=data.get("equipment_needed", []),
                                category_summary=data.get("category_summary", {}),
                                intensity_summary=data.get("intensity_summary", {}),
                            )
                            st.session_state.current_session = session_obj
                        except Exception:
                            st.session_state.current_session = None
                    else:
                        ui_session.set_practice_config(
                            duration_minutes=total_time or 90,
                            num_players=num_players or 16,
                            num_drills=5,
                            selected_categories=[c.strip() for c in str(categories).split("|") if c.strip()],
                            session_notes=str(session_row.get("session_notes", "") or ""),
                        )
                        st.session_state.current_session = None
                    st.switch_page("pages/2_Practice_Generator.py")

st.divider()
if ui_session.is_developer_mode():
    with st.expander("Analytics (Advanced)", expanded=False):
        drill_lookup = {}
        if st.session_state.drills_df is not None and len(st.session_state.drills_df):
            name_col = (
                "drill_name"
                if "drill_name" in st.session_state.drills_df.columns
                else ("name" if "name" in st.session_state.drills_df.columns else None)
            )
            if name_col:
                drill_lookup = st.session_state.drills_df.set_index("drill_id")[name_col].to_dict()
        history_df["drill_ids_list"] = history_df["drills_used"].apply(
            lambda cell: [d.strip() for d in str(cell).split("|") if d.strip()]
        )
        history_df["drill_names_list"] = history_df["drill_ids_list"].apply(
            lambda drills: [drill_lookup.get(drill_id, drill_id) for drill_id in drills]
        )
        history_df["drill_count"] = history_df["drill_ids_list"].apply(len)
        category_minutes_df = practice_history.allocate_category_minutes(history_df)

        st.subheader("Recency by Drill")
        # TODO: replace use_container_width with width=\"stretch\" when Streamlit deprecates it.
        recency_table = practice_history.compute_recency_table(history_df)
        st.dataframe(recency_table, use_container_width=True)

        st.subheader("Category Usage (minutes)")
        if len(category_minutes_df):
            grouped = (
                category_minutes_df.groupby("category")["minutes"]
                .sum()
                .reset_index()
                .sort_values("minutes", ascending=False)
            )
            st.bar_chart(grouped, x="category", y="minutes")
        else:
            st.caption("No category usage yet.")








