"""Session state management for Streamlit"""
import streamlit as st
from pathlib import Path
import data_loader
import config

USER_MODE_KEY = "user_mode"


def get_user_mode() -> str:
    """
    Returns the current UI mode, e.g. 'coach' or 'developer'.
    Defaults to config.DEFAULT_USER_MODE if not set.
    """
    return st.session_state.get(USER_MODE_KEY, config.DEFAULT_USER_MODE)


def set_user_mode(mode: str) -> None:
    """
    Sets the current UI mode in session state.
    """
    if mode not in ("coach", "developer"):
        mode = config.DEFAULT_USER_MODE
    st.session_state[USER_MODE_KEY] = mode


def is_coach_mode() -> bool:
    return get_user_mode() == "coach"


def is_developer_mode() -> bool:
    return get_user_mode() == "developer"


def init_session_state():
    """Initialize session state variables with defaults"""
    if 'drill_cache_mtime' not in st.session_state:
        st.session_state.drill_cache_mtime = None
    
    if 'drills_df' not in st.session_state:
        st.session_state.drills_df = None
    
    if 'teams_df' not in st.session_state:
        st.session_state.teams_df = None
    
    if 'templates' not in st.session_state:
        st.session_state.templates = None
    
    if 'selected_team' not in st.session_state:
        st.session_state.selected_team = None
    
    if 'generated_practice' not in st.session_state:
        st.session_state.generated_practice = None


def init_drills_in_session_state(data_path):
    """
    CANONICAL DRILL LOADER - Single source of truth for drills across the app.

    This function ensures that drills are loaded once and shared via session_state.
    Both the Drill Library page and Practice Generator page should call this function
    to ensure they're using the same drills_df.

    Args:
        data_path: Path to data directory

    Returns:
        None (loads into st.session_state["drills_df"])
    """
    if 'drills_df' not in st.session_state or st.session_state['drills_df'] is None:
        st.session_state.drills_df = data_loader.load_drills(data_path)


def get_cached_drills(data_path):
    """
    Load drills with file freshness caching.
    Only reloads if CSV file has been modified.

    Args:
        data_path: Path to data directory

    Returns:
        DataFrame with drills
    """
    drill_file = Path(data_path) / 'drill_library.csv'

    # Check if file has been modified
    is_fresh, new_mtime = data_loader.check_file_freshness(
        drill_file,
        st.session_state.drill_cache_mtime
    )

    # Reload if fresh or not cached
    if is_fresh or st.session_state.drills_df is None:
        st.session_state.drills_df = data_loader.load_drills(data_path)
        st.session_state.drill_cache_mtime = new_mtime

    return st.session_state.drills_df


def invalidate_drill_cache():
    """Force reload of drill library on next access"""
    st.session_state.drill_cache_mtime = None
    st.session_state.drills_df = None


def render_team_selector(container=None, label="Active Team", widget_key="team_selector", help_text=None):
    """
    Render a consistent team selector dropdown and keep session state in sync.

    Args:
        container: Optional Streamlit container/column to render within.
        label: Label for the selectbox.
        widget_key: Unique key for this selector instance.
        help_text: Optional helper text for the widget.

    Returns:
        The currently selected team dictionary or None.
    """
    target = container or st
    teams_df = st.session_state.get('teams_df')

    if teams_df is None or teams_df.empty:
        target.warning("No teams available. Add a team to start planning.")
        st.session_state.selected_team = None
        return None

    team_names = teams_df['team_name'].tolist()
    if st.session_state.selected_team is None or st.session_state.selected_team['team_name'] not in team_names:
        st.session_state.selected_team = teams_df.iloc[0].to_dict()

    default_index = team_names.index(st.session_state.selected_team['team_name'])

    selected_name = target.selectbox(
        label,
        options=team_names,
        index=default_index,
        key=widget_key,
        help=help_text,
    )

    if selected_name != st.session_state.selected_team['team_name']:
        st.session_state.selected_team = teams_df[teams_df['team_name'] == selected_name].iloc[0].to_dict()

    return st.session_state.selected_team


def get_team_profile_status(team_id=None):
    """
    Summarize whether the selected team has key profile fields populated.

    Args:
        team_id: Optional explicit team_id. Defaults to currently selected team.

    Returns:
        dict with keys:
            - has_team: bool
            - has_play_style: bool
            - has_focus_tags: bool
            - has_injuries: bool
            - is_complete: bool (play style + focus tags present)
            - missing_fields: list of human-readable field names
            - team_name: name of the evaluated team (or None)
    """
    teams_df = st.session_state.get('teams_df')
    selected_team = st.session_state.get('selected_team')

    status = {
        "has_team": False,
        "has_play_style": False,
        "has_focus_tags": False,
        "has_injuries": False,
        "is_complete": False,
        "missing_fields": [],
        "team_name": None,
    }

    if teams_df is None or teams_df.empty:
        return status

    if team_id is None and selected_team:
        team_id = selected_team.get('team_id')

    if team_id is None:
        return status

    team_rows = teams_df[teams_df['team_id'] == team_id]
    if team_rows.empty:
        return status

    team_row = team_rows.iloc[0]
    status["has_team"] = True
    status["team_name"] = team_row.get('team_name')

    play_style = str(team_row.get('play_style', '') or '').strip()
    focus_tags = [
        tag.strip() for tag in str(team_row.get('focus_areas', '') or '').split("|") if tag.strip()
    ]
    injuries = [
        entry.strip() for entry in str(team_row.get('injuries', '') or '').split("|") if entry.strip()
    ]

    status["has_play_style"] = bool(play_style)
    status["has_focus_tags"] = len(focus_tags) > 0
    status["has_injuries"] = len(injuries) > 0

    if not status["has_play_style"]:
        status["missing_fields"].append("play style")
    if not status["has_focus_tags"]:
        status["missing_fields"].append("focus tags")

    status["is_complete"] = status["has_play_style"] and status["has_focus_tags"]
    return status


def get_team_profile_completeness(team_row):
    """
    Return (percent_complete, missing_fields list) for a team profile row.
    """
    if team_row is None:
        return 0, []
    checks = {
        "age_group": bool(str(team_row.get("age_group", "")).strip()),
        "formation": bool(str(team_row.get("formation", "")).strip()),
        "play_style": bool(str(team_row.get("play_style", "")).strip()),
        "focus_tags": len([t for t in str(team_row.get("focus_areas", "")).split("|") if t.strip()]) > 0,
        "key_players": len([t for t in str(team_row.get("key_players", "")).split("|") if t.strip()]) > 0,
        "injuries": len([t for t in str(team_row.get("injuries", "")).split("|") if t.strip()]) > 0,
        "practice_schedule": bool(str(team_row.get("practice_schedule", "")).strip()),
    }
    total = len(checks)
    completed = sum(1 for v in checks.values() if v)
    percent = int((completed / total) * 100) if total else 0
    missing = [label for label, done in checks.items() if not done]
    return percent, missing


# Focus Tracker - Boost Attributes for Practice Generation
FOCUS_BOOST_KEY = "focus_boost_attributes"


def set_focus_boost_attributes(attrs):
    """
    Set focus boost attributes in session state.
    These are category names that should be prioritized in practice generation.

    Args:
        attrs: List of category names (e.g., ['Tactical', 'Conditioning'])
               or None to clear
    """
    st.session_state[FOCUS_BOOST_KEY] = attrs if attrs else []


def get_focus_boost_attributes():
    """
    Get focus boost attributes from session state.

    Returns:
        List of category names to boost, or empty list if none set
    """
    return list(st.session_state.get(FOCUS_BOOST_KEY, []))


def clear_focus_boost_attributes():
    """Clear focus boost attributes from session state."""
    st.session_state[FOCUS_BOOST_KEY] = []
