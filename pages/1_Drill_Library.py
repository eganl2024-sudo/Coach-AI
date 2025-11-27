"""Drill Library - Browse and manage drills"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import config
import data_loader
import session_state
import practice_history
import drills
import ui_components
from datetime import datetime, timedelta
from filter_presets import load_presets, save_presets, PRESETS_VERSION


def _split_tags(cell):
    return [tag.strip() for tag in str(cell).split("|") if tag and tag.strip()]


FILTER_DEFAULTS = {
    "categories": ["All"],
    "difficulty": ["All"],
    "intensity": ["All"],
    "tags": ["All"],
    "search": "",
    "favorites_only": False,
    "hide_recent": False,
    "sort": "Most Recent",
}
FILTER_PRESET_FILE = "drill_filter_presets.json"
FILTER_WIDGET_KEYS = {
    "categories": "library_filter_categories",
    "difficulty": "library_filter_difficulty",
    "intensity": "library_filter_intensity",
    "tags": "library_filter_tags",
    "search": "library_filter_search",
    "favorites_only": "library_filter_favorites",
    "hide_recent": "library_filter_hide_recent",
    "sort": "library_filter_sort",
}


def _persist_drills(df):
    data_path = st.session_state.get('data_path')
    if not data_path:
        return
    drill_file = Path(data_path) / 'drill_library.csv'
    df.to_csv(drill_file, index=False)
    st.session_state.drills_df = df


def _filter_preset_path():
    data_path = st.session_state.get('data_path')
    if not data_path:
        return None
    return Path(data_path) / FILTER_PRESET_FILE


def _set_filter_state(state, rerun=False):
    normalized = {}
    for field, value in state.items():
        if isinstance(value, list):
            normalized[field] = list(value)
        else:
            normalized[field] = value
    st.session_state.library_filters = normalized
    for field, key in FILTER_WIDGET_KEYS.items():
        st.session_state[key] = normalized[field]
    if rerun:
        st.experimental_rerun()

st.set_page_config(page_title="Drill Library", page_icon="📚", layout="wide")

ui_components.render_nav(active_label="📚 Drill Library")
st.divider()

st.title("📚 Drill Library")
st.markdown("Browse and search your complete drill collection")

session_state.init_session_state()

if 'data_path' not in st.session_state:
    st.session_state.data_path = config.get_data_path()

if st.session_state.drills_df is None:
    st.session_state.drills_df = data_loader.load_drills(st.session_state.data_path)

if st.session_state.teams_df is None:
    st.session_state.teams_df = data_loader.load_teams(st.session_state.data_path)

if 'library_filters' not in st.session_state:
    st.session_state.library_filters = FILTER_DEFAULTS.copy()
for field, key in FILTER_WIDGET_KEYS.items():
    if key not in st.session_state:
        st.session_state[key] = st.session_state.library_filters[field]
if 'library_filters_expanded' not in st.session_state:
    st.session_state.library_filters_expanded = True

session_state.render_team_selector(
    label="Active team",
    widget_key="team_selector_library"
)

drills_df = st.session_state.drills_df
drill_load_error = drills_df.attrs.get('load_error')
if drill_load_error:
    st.error(drill_load_error)
if len(drills_df) == 0:
    st.info("Starter drills are preloaded for you. Add or edit drills anytime to customize your library.")
    st.page_link("pages/4_Add_Drills.py", label="➕ Add a Drill")
    st.stop()

drill_repair = drills_df.attrs.get('repair_info')
if drill_repair and drill_repair.get("was_repaired"):
    added = ", ".join(drill_repair.get("added_columns", [])) or "columns"
    st.warning(f"Drill library CSV was missing {added}; defaults were added automatically.")

profile_status = session_state.get_team_profile_status()
if profile_status["has_team"] and not profile_status["is_complete"]:
    missing = ", ".join(profile_status["missing_fields"])
    st.info(
        f"Your team profile is missing {missing}. Update the Team Hub so suggestions "
        "and filters can better reflect your priorities."
    )

team_profile_context = {}
drill_recency = {}
history_df = pd.DataFrame()
if st.session_state.selected_team is not None:
    team_id = st.session_state.selected_team['team_id']
    history_mtime = practice_history.get_history_mtime(team_id, st.session_state.data_path)
    history_df = practice_history.load_practice_history(team_id, st.session_state.data_path, history_mtime)
    drill_recency = practice_history.get_cached_recency(history_df)
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
        team_profile_context = {
            "play_style": _clean(team_data.get('play_style', '')),
            "focus_tags": focus_tags,
        }

def get_recency_label(drill_id):
    info = drill_recency.get(drill_id)
    if not info:
        return "New"
    return info.get("label", "New")
all_tags = set()
for tags_str in drills_df.get('tags', pd.Series([], dtype=str)).fillna(''):
    all_tags.update(_split_tags(tags_str))
tag_filter_options = sorted(all_tags.union(set(config.DRILL_TAGS)))
tag_filter_choices = ['All'] + tag_filter_options if tag_filter_options else ['All']

# Suggestions
if history_df is not None and len(history_df):
    with st.expander("Team suggestions", expanded=False):
        recent_window = history_df.copy()
        try:
            recent_window['session_date'] = pd.to_datetime(recent_window['session_date'])
            cutoff = datetime.utcnow() - timedelta(days=30)
            recent_window = recent_window[recent_window['session_date'] >= cutoff]
        except Exception:
            recent_window = pd.DataFrame()
        recent_cats = set()
        if len(recent_window):
            for cats in recent_window['categories'].fillna(""):
                recent_cats.update([c.strip() for c in str(cats).split("|") if c.strip()])
        underused = [cat for cat in config.CATEGORIES if cat not in recent_cats]
        if underused:
            st.markdown("**Underused categories this month:** " + ", ".join(underused))
        else:
            st.markdown("Balanced category usage this month.")

        focus_tags = team_profile_context.get("focus_tags", [])
        if focus_tags and drill_recency:
            tag_set = {tag.lower() for tag in focus_tags}
            recommended = []
            for _, drill in drills_df.iterrows():
                label = get_recency_label(drill['drill_id'])
                drill_tags = {tag.strip().lower() for tag in str(drill.get('tags', '')).split("|") if tag.strip()}
                if label == "Fresh" and drill_tags.intersection(tag_set):
                    recommended.append(drill['drill_name'])
                if len(recommended) >= 5:
                    break
            if recommended:
                st.markdown("**Fresh drills aligned with team focus:**")
                for name in recommended:
                    st.markdown(f"- {name}")
            else:
                st.markdown("Focus tags set but no fresh drills match yet.")
        else:
            st.markdown("Add focus tags in Team Hub to receive drill suggestions.")

# Summary metrics
st.subheader("Library Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Drills", len(drills_df))
with col2:
    avg_duration = int(drills_df['duration_minutes'].mean()) if len(drills_df) > 0 else 0
    st.metric("Avg Duration", f"{avg_duration} min")
with col3:
    avg_rating = round(drills_df['coach_rating'].mean(), 1) if len(drills_df) > 0 else 0
    st.metric("Avg Rating", f"{'⭐' * int(avg_rating)}")
with col4:
    unique_categories = drills_df['category'].nunique() if len(drills_df) > 0 else 0
    st.metric("Categories", unique_categories)

if len(drills_df) < 5:
    st.info("Tip: add more drills to unlock richer planning suggestions. Use the Add Drills page to grow your library.")

st.divider()

filter_state = st.session_state.library_filters
preset_payload = load_presets(_filter_preset_path())
presets = preset_payload.get("presets", [])
preset_warning = preset_payload.get("warning")
sort_options = ["Most Recent", "Most Used", "Highest Rated", "Alphabetical"]

with st.expander("Filters & Sorting", expanded=st.session_state.library_filters_expanded):
    if preset_warning:
        st.warning(preset_warning + " You can recreate presets below.")
    col1, col2, col3, col4 = st.columns(4)

    category_filter = col1.multiselect(
        "Category",
        options=['All'] + config.CATEGORIES,
        default=filter_state["categories"],
        key=FILTER_WIDGET_KEYS["categories"]
    )

    difficulty_filter = col2.multiselect(
        "Difficulty",
        options=['All'] + config.DIFFICULTY_LEVELS,
        default=filter_state["difficulty"],
        key=FILTER_WIDGET_KEYS["difficulty"]
    )

    intensity_filter = col3.multiselect(
        "Intensity",
        options=['All'] + config.INTENSITY_LEVELS,
        default=filter_state["intensity"],
        key=FILTER_WIDGET_KEYS["intensity"]
    )

    tag_filter = col4.multiselect(
        "Tags",
        options=tag_filter_choices,
        default=filter_state["tags"],
        key=FILTER_WIDGET_KEYS["tags"],
        help="Filter by drill tags like Finishing, Transition, etc."
    )

    col_search, col_fav = st.columns([3, 1])
    search_query = col_search.text_input(
        "Search drills",
        placeholder="Enter drill name...",
        value=filter_state["search"],
        key=FILTER_WIDGET_KEYS["search"]
    )
    favorites_only = col_fav.toggle(
        "Favorites only",
        value=filter_state["favorites_only"],
        key=FILTER_WIDGET_KEYS["favorites_only"],
        help="Show only drills you've starred as favorites."
    )
    hide_recent_drills = st.toggle(
        "Hide recency 'Recent'",
        value=filter_state["hide_recent"],
        key=FILTER_WIDGET_KEYS["hide_recent"],
        help="Exclude drills used within the last 7 days to encourage variety."
    )

    sort_choice = st.selectbox(
        "Sort by",
        options=sort_options,
        index=sort_options.index(filter_state["sort"]) if filter_state["sort"] in sort_options else 0,
        key=FILTER_WIDGET_KEYS["sort"]
    )

    action_cols = st.columns([1, 2])
    with action_cols[0]:
        if st.button("Clear all filters"):
            _set_filter_state(FILTER_DEFAULTS.copy(), rerun=True)
    with action_cols[1]:
        preset_name = st.text_input("Save current filters as", placeholder="e.g. Defensive Focus")
        if st.button("Save preset"):
            if preset_name:
                new_state = {
                    "categories": list(category_filter) or ["All"],
                    "difficulty": list(difficulty_filter) or ["All"],
                    "intensity": list(intensity_filter) or ["All"],
                    "tags": list(tag_filter) or ["All"],
                    "search": search_query or "",
                    "favorites_only": favorites_only,
                    "hide_recent": hide_recent_drills,
                    "sort": sort_choice,
                }
                existing = [p for p in presets if p.get("name") == preset_name]
                presets = [p for p in presets if p.get("name") != preset_name]
                presets.append({"name": preset_name, "filters": new_state})
                save_presets(_filter_preset_path(), presets)
                st.success(f"Preset '{preset_name}' saved.")
            else:
                st.warning("Enter a preset name before saving.")

    preset_options = ["Select preset"] + [p["name"] for p in presets]
    preset_choice = st.selectbox("Load preset", options=preset_options)
    preset_action_cols = st.columns(2)
    with preset_action_cols[0]:
        if st.button("Apply preset") and preset_choice != "Select preset":
            preset = next((p for p in presets if p["name"] == preset_choice), None)
            if preset:
                _set_filter_state(preset["filters"].copy(), rerun=True)
    with preset_action_cols[1]:
        if st.button("Delete preset") and preset_choice != "Select preset":
            presets = [p for p in presets if p["name"] != preset_choice]
            save_presets(_filter_preset_path(), presets)
            st.success(f"Preset '{preset_choice}' deleted.")
            st.experimental_rerun()

filter_state = {
    "categories": list(category_filter) or ["All"],
    "difficulty": list(difficulty_filter) or ["All"],
    "intensity": list(intensity_filter) or ["All"],
    "tags": list(tag_filter) or ["All"],
    "search": search_query or "",
    "favorites_only": favorites_only,
    "hide_recent": hide_recent_drills,
    "sort": sort_choice,
}
st.session_state.library_filters = filter_state

# Apply filters
category_filter = filter_state["categories"]
difficulty_filter = filter_state["difficulty"]
intensity_filter = filter_state["intensity"]
tag_filter = filter_state["tags"]
search_query = filter_state["search"]
favorites_only = filter_state["favorites_only"]
hide_recent_drills = filter_state["hide_recent"]
sort_choice = filter_state["sort"]

filtered_df = drills_df.copy()

if 'All' not in category_filter and len(category_filter) > 0:
    filtered_df = filtered_df[filtered_df['category'].isin(category_filter)]

if 'All' not in difficulty_filter and len(difficulty_filter) > 0:
    filtered_df = filtered_df[filtered_df['difficulty'].isin(difficulty_filter)]

if 'All' not in intensity_filter and len(intensity_filter) > 0:
    filtered_df = filtered_df[filtered_df['intensity'].isin(intensity_filter)]

if search_query:
    filtered_df = filtered_df[
        filtered_df['drill_name'].str.contains(search_query, case=False, na=False)
    ]

if 'All' not in tag_filter:
    tag_set = set(tag_filter)
    filtered_df = filtered_df[
        filtered_df['tags'].apply(
            lambda cell: bool(set(_split_tags(cell)).intersection(tag_set))
        )
    ]

if favorites_only:
    filtered_df = filtered_df[filtered_df['is_favorite'] == True]  # noqa: E712
if hide_recent_drills:
    filtered_df = filtered_df[
        filtered_df['drill_id'].apply(lambda x: get_recency_label(x) != "Recent")
    ]

# Sorting
if len(filtered_df):
    if sort_choice == "Most Recent":
        filtered_df['__last_used'] = pd.to_datetime(filtered_df.get('last_used_date'), errors='coerce')
        filtered_df = filtered_df.sort_values('__last_used', ascending=False, na_position='last')
    elif sort_choice == "Most Used":
        filtered_df = filtered_df.sort_values('times_used', ascending=False, na_position='last')
    elif sort_choice == "Highest Rated":
        filtered_df = filtered_df.sort_values('coach_rating', ascending=False, na_position='last')
    elif sort_choice == "Alphabetical":
        filtered_df = filtered_df.sort_values('drill_name', ascending=True)
    filtered_df = filtered_df.drop(columns=[col for col in ['__last_used'] if col in filtered_df.columns])

st.divider()

# Category breakdown
st.subheader(f"Drills ({len(filtered_df)} found)")

if len(filtered_df) > 0:
    # Show category tabs
    categories = sorted(filtered_df['category'].unique())

    if len(categories) > 1:
        tabs = st.tabs(categories)

        for idx, category in enumerate(categories):
            with tabs[idx]:
                category_drills = filtered_df[filtered_df['category'] == category]

                st.markdown(f"**{len(category_drills)} {category} drills**")

                # Display drills in this category
                for _, drill in category_drills.iterrows():
                    favorite_icon = "⭐ " if drill.get('is_favorite') else ""
                    with st.expander(f"{favorite_icon}{drill['drill_name']} ({drill['duration_minutes']} min)"):
                        col1, col2 = st.columns([2, 1])

                        with col1:
                            st.markdown(f"**Description:** {drill['description']}")
                            st.markdown(f"**Coaching Points:** {drill['coaching_points']}")
                            if drill['equipment']:
                                st.markdown(f"**Equipment:** {drill['equipment']}")
                            st.markdown(f"**Setup:** {drill['setup_data']}")
                            current_tags = _split_tags(drill.get('tags', ''))
                            tag_options = sorted(set(tag_filter_options).union(set(current_tags)))
                            new_tags = st.multiselect(
                                "Tags",
                                options=tag_options if tag_options else current_tags,
                                default=current_tags,
                                key=f"tags_{drill['drill_id']}"
                            )
                        if set(new_tags) != set(current_tags):
                            drills_df.loc[drills_df['drill_id'] == drill['drill_id'], 'tags'] = "|".join(new_tags)
                            _persist_drills(drills_df)

                        diagram_path = str(drill.get('diagram_path', '') or '').strip()
                        if diagram_path:
                            diagram_file = config.get_diagram_file(diagram_path)
                            st.markdown("**Diagram**")
                            if diagram_file and diagram_file.exists():
                                st.image(str(diagram_file), use_column_width=True)
                            else:
                                st.caption("Diagram coming soon.")

                    with col2:
                        st.markdown(f"**ID:** `{drill['drill_id']}`")
                        st.markdown(f"**Recency:** {get_recency_label(drill['drill_id'])}")
                        st.markdown(f"**Players:** {drill['players_min']}-{drill['players_max']}")
                        st.markdown(f"**Duration:** {drill['duration_minutes']} min")
                        st.markdown(f"**Field:** {drill['field_type']}")
                        st.markdown(f"**Difficulty:** {drill['difficulty'].title()}")
                        st.markdown(f"**Intensity:** {drill['intensity'].title()}")
                        favorite_state = bool(drill.get('is_favorite', False))
                        new_favorite = st.checkbox(
                            "⭐ Favorite",
                            value=favorite_state,
                            key=f"favorite_{drill['drill_id']}"
                        )
                        if new_favorite != favorite_state:
                            drills_df.loc[drills_df['drill_id'] == drill['drill_id'], 'is_favorite'] = new_favorite
                            _persist_drills(drills_df)

                        rating = drill['coach_rating']
                        if pd.notna(rating):
                            st.markdown(f"**Rating:** {'⭐' * int(rating)}")

                        action_col1, action_col2 = st.columns(2)
                        with action_col1:
                            if st.button("Edit Drill", key=f"edit_{drill['drill_id']}"):
                                st.session_state.prefill_drill = drill.to_dict()
                                st.session_state.selected_drill_id = drill['drill_id']
                                st.switch_page("pages/6_✏️_Edit_Drill.py")
                        with action_col2:
                            if st.button("Duplicate Drill", key=f"duplicate_{drill['drill_id']}"):
                                new_id = drills.suggest_next_drill_id(drills_df, category=drill['category'])
                                duplicate_data = drill.to_dict()
                                duplicate_data['drill_id'] = new_id
                                duplicate_name = duplicate_data['drill_name']
                                duplicate_data['drill_name'] = f"{duplicate_name} Copy"
                                st.session_state.prefill_drill = duplicate_data
                                st.session_state.selected_drill_id = new_id
                                st.switch_page("pages/6_✏️_Edit_Drill.py")
    else:
        # Single category - just show drills
        category = categories[0]
        st.markdown(f"**{len(filtered_df)} drills**")

        for _, drill in filtered_df.iterrows():
            favorite_icon = "⭐ " if drill.get('is_favorite') else ""
            with st.expander(f"{favorite_icon}{drill['drill_name']} ({drill['duration_minutes']} min)"):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"**Description:** {drill['description']}")
                    st.markdown(f"**Coaching Points:** {drill['coaching_points']}")
                    if drill['equipment']:
                        st.markdown(f"**Equipment:** {drill['equipment']}")
                    st.markdown(f"**Setup:** {drill['setup_data']}")
                    current_tags = _split_tags(drill.get('tags', ''))
                    tag_options = sorted(set(tag_filter_options).union(set(current_tags)))
                    new_tags = st.multiselect(
                        "Tags",
                        options=tag_options if tag_options else current_tags,
                        default=current_tags,
                        key=f"tags_{drill['drill_id']}"
                    )
                    if set(new_tags) != set(current_tags):
                        drills_df.loc[drills_df['drill_id'] == drill['drill_id'], 'tags'] = "|".join(new_tags)
                        _persist_drills(drills_df)

                with col2:
                    st.markdown(f"**ID:** `{drill['drill_id']}`")
                    st.markdown(f"**Recency:** {get_recency_label(drill['drill_id'])}")
                    st.markdown(f"**Players:** {drill['players_min']}-{drill['players_max']}")
                    st.markdown(f"**Duration:** {drill['duration_minutes']} min")
                    st.markdown(f"**Field:** {drill['field_type']}")
                    st.markdown(f"**Difficulty:** {drill['difficulty'].title()}")
                    st.markdown(f"**Intensity:** {drill['intensity'].title()}")
                    favorite_state = bool(drill.get('is_favorite', False))
                    new_favorite = st.checkbox(
                        "⭐ Favorite",
                        value=favorite_state,
                        key=f"favorite_{drill['drill_id']}"
                    )
                    if new_favorite != favorite_state:
                        drills_df.loc[drills_df['drill_id'] == drill['drill_id'], 'is_favorite'] = new_favorite
                        _persist_drills(drills_df)

                    rating = drill['coach_rating']
                    if pd.notna(rating):
                        st.markdown(f"**Rating:** {'⭐' * int(rating)}")

                action_col1, action_col2 = st.columns(2)
                with action_col1:
                    st.page_link(
                        "pages/6_✏️_Edit_Drill.py",
                        label="Edit Drill",
                        args={"drill_id": drill['drill_id']},
                        use_container_width=True
                    )
                with action_col2:
                    if st.button("Duplicate Drill", key=f"duplicate_{drill['drill_id']}"):
                        new_id = drills.suggest_next_drill_id(drills_df, category=drill['category'])
                        duplicate_data = drill.to_dict()
                        duplicate_data['drill_id'] = new_id
                        duplicate_name = duplicate_data['drill_name']
                        duplicate_data['drill_name'] = f"{duplicate_name} Copy"
                        st.session_state.prefill_drill = duplicate_data
                        st.session_state.selected_drill_id = new_id
                        st.switch_page("pages/6_✏️_Edit_Drill.py")
else:
    st.warning("No drills found matching your filters. Try adjusting the filters above.")

# Footer
st.divider()
st.caption(f"Showing {len(filtered_df)} of {len(drills_df)} total drills")
