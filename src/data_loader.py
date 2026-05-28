"""Data loading module with caching and auto-refresh"""
import os
import json
import shutil
import uuid
from typing import Optional
import pandas as pd
from pathlib import Path
import streamlit as st
import db
from utils import ensure_columns
import config
from validation import validate_drill, validate_team_profile

def _get_username() -> str | None:
    """
    Return the active username from session state, or None if auth is 
    disabled (local dev mode) or no user is logged in.
    """
    import os
    disable_auth = str(
        os.environ.get("COACH_AI_DISABLE_AUTH", "")
    ).strip().lower() in {"1", "true", "yes", "on"}
    if disable_auth:
        return None
    return st.session_state.get("username")


DRILL_COLUMNS = [
    'drill_id', 'drill_name', 'category', 'description',
    'players_min', 'players_max', 'duration_minutes', 'field_type',
    'setup_data', 'equipment', 'coaching_points', 'difficulty',
    'intensity', 'coach_rating', 'personal_notes', 'times_used',
    'last_used_date', 'tags', 'is_favorite', 'diagram_path', 'diagram_metadata',
    'positions', 'age_groups', 'coach_cues', 'progression', 'recommended_field_size',
    'diagram_url', 'video_youtube_url', 'video_local_url', 'video_start_time',
    'position_relevance', 'skill_category', 'solo_possible', 'min_equipment',
    'game_application', 'video_url', 'video_thumbnail', 'coaching_cues',
    'position_track', 'drill_type', 'series_name', 'series_order',
    'rrs_benchmark', 'space_required', 'position_primary', 'presenter_id',
    'college_context', 'pro_context', 'variations', 'prerequisite_drill',
    'next_drill', 'status', 'video_url_short', 'video_url_full',
    'video_status', 'filming_date', 'filming_notes', 'beta_ready',
    'date_published', 'slug', 'common_mistakes'
]
DRILL_DEFAULTS = {
    'drill_id': '',
    'drill_name': '',
    'category': '',
    'description': '',
    'players_min': 0,
    'players_max': 0,
    'duration_minutes': 0,
    'field_type': 'Other',
    'setup_data': '',
    'equipment': '',
    'coaching_points': '',
    'difficulty': 'intermediate',
    'intensity': 'medium',
    'coach_rating': 3,
    'personal_notes': '',
    'times_used': 0,
    'last_used_date': '',
    'tags': '',
    'is_favorite': False,
    'diagram_path': '',
    'diagram_metadata': '',
    'positions': '',
    'age_groups': '',
    'coach_cues': '',
    'progression': '',
    'recommended_field_size': '',
    'diagram_url': '',
    'video_youtube_url': '',
    'video_local_url': '',
    'video_start_time': '',
    'position_relevance': '',
    'skill_category': 'Technical',
    'solo_possible': True,
    'min_equipment': 'Ball only',
    'game_application': 'Game application notes coming soon',
    'video_url': '',
    'video_thumbnail': '',
    'coaching_cues': '',
    'position_track':    '',
    'drill_type':        'Isolation',
    'series_name':       '',
    'series_order':      0,
    'rrs_benchmark':     'Club Level',
    'space_required':    'Small area',
    'position_primary':  '',
    'presenter_id':      '',
    'college_context':   '',
    'pro_context':       '',
    'variations':        '',
    'prerequisite_drill': '',
    'next_drill':        '',
    'status':            'Published',
    'video_url_short':   '',
    'video_url_full':    '',
    'video_status':      'Not Filmed',
    'filming_date':      '',
    'filming_notes':     '',
    'beta_ready':        False,
    'date_published':    '',
    'slug':              '',
    'common_mistakes':   '',
}
def check_file_freshness(filepath, last_mtime):
    """
    Check if file has been modified since last load

    Args:
        filepath: Path to file
        last_mtime: Last known modification time

    Returns:
        (is_fresh: bool, new_mtime: float)
    """
    try:
        current_mtime = os.path.getmtime(filepath)
        is_fresh = (last_mtime is None) or (current_mtime > last_mtime)
        return is_fresh, current_mtime
    except FileNotFoundError:
        return False, None

def load_drills(data_path):
    """
    Load drills from CSV file or Supabase Database

    Args:
        data_path: Path to data folder

    Returns:
        DataFrame with drills
    """
    loaded_from_supabase = False
    drills_df = None

    # 1. Try loading from Supabase first
    import os as _os
    if not _os.environ.get("COACH_AI_DISABLE_AUTH", "").strip().lower() in {"1", "true", "yes", "on"}:
        try:
            client = db.get_client()
            response = client.table("drills").select("*").execute()
            if response.data:
                drills_df = pd.DataFrame(response.data)
                drills_df.attrs['load_info'] = "Drill library loaded from Supabase Cloud"
                loaded_from_supabase = True
        except Exception:
            pass

    # 2. Local fallback loading
    if not loaded_from_supabase:
        drill_path = Path(data_path) / 'drill_library.csv'
        try:
            if drill_path.exists():
                drills_df = pd.read_csv(drill_path)
            else:
                # Bootstrap from seed drills if available
                seed_path = config.get_seed_drills_path()
                if seed_path and seed_path.exists():
                    drill_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(seed_path, drill_path)
                    drills_df = pd.read_csv(drill_path)
                    drills_df.attrs['load_info'] = f"Drill library bootstrapped from seed file {seed_path}"
                else:
                    drills_df = pd.DataFrame(columns=DRILL_COLUMNS)
                    drills_df.attrs['load_error'] = f"Drill library not found at {drill_path}."
                    drills_df.attrs['repair_info'] = {"dataset": "drills", "was_repaired": False, "added_columns": []}
                    return drills_df
        except Exception as exc:
            drills_df = pd.DataFrame(columns=DRILL_COLUMNS)
            drills_df.attrs['load_error'] = f"Failed to load drill library: {exc}"
            drills_df.attrs['repair_info'] = {"dataset": "drills", "was_repaired": False, "added_columns": []}
            return drills_df

    repairs, drills_df = ensure_columns(drills_df, DRILL_DEFAULTS)


    validation_errors = []
    validated_rows = []
    for idx, row in drills_df.iterrows():
        try:
            drill_obj = validate_drill(row.to_dict())
            validated_rows.append(drill_obj.to_record(preferred_fields=list(drills_df.columns)))
        except ValueError as exc:
            validation_errors.append({"row": int(idx), "error": str(exc)})
    drills_df = pd.DataFrame(validated_rows) if validated_rows else pd.DataFrame(columns=drills_df.columns)

    if 'tags' not in drills_df.columns:
        drills_df['tags'] = ''
    else:
        drills_df['tags'] = drills_df['tags'].fillna('')

    if 'is_favorite' not in drills_df.columns:
        drills_df['is_favorite'] = False
    else:
        def _to_bool(value):
            if isinstance(value, bool):
                return value
            if pd.isna(value):
                return False
            if isinstance(value, (int, float)):
                return value == 1
            return str(value).strip().lower() in {'1', 'true', 'yes', 'y'}

        drills_df['is_favorite'] = drills_df['is_favorite'].apply(_to_bool)

    for column in ['positions', 'age_groups', 'coach_cues', 'progression', 'recommended_field_size',
                   'diagram_url', 'video_youtube_url', 'video_local_url', 'video_start_time',
                   'position_relevance', 'skill_category', 'min_equipment', 'game_application',
                   'video_url', 'video_thumbnail', 'coaching_cues']:
        if column in drills_df.columns:
            drills_df[column] = drills_df[column].fillna('')

    if 'solo_possible' not in drills_df.columns:
        drills_df['solo_possible'] = True
    else:
        def _to_bool_solo(value):
            if isinstance(value, bool):
                return value
            if pd.isna(value) or value is None:
                return True
            if isinstance(value, (int, float)):
                return value == 1
            return str(value).strip().lower() not in {'0', 'false', 'no', 'n'}
        drills_df['solo_possible'] = drills_df['solo_possible'].apply(_to_bool_solo)

    if 'beta_ready' not in drills_df.columns:
        drills_df['beta_ready'] = False
    else:
        def _to_bool_beta(value):
            if isinstance(value, bool):
                return value
            if pd.isna(value) or value is None:
                return False
            if isinstance(value, (int, float)):
                return value == 1
            return str(value).strip().lower() in {'1', 'true', 'yes', 'y'}
        drills_df['beta_ready'] = drills_df['beta_ready'].apply(_to_bool_beta)

    if 'series_order' in drills_df.columns:
        drills_df['series_order'] = pd.to_numeric(
            drills_df['series_order'], errors='coerce'
        ).fillna(0).astype(int)

    for column in [
        'position_track', 'drill_type', 'series_name', 'rrs_benchmark',
        'space_required', 'position_primary', 'presenter_id',
        'college_context', 'pro_context', 'variations',
        'prerequisite_drill', 'next_drill', 'status', 'video_url_short',
        'video_url_full', 'video_status', 'filming_date', 'filming_notes',
        'date_published', 'slug', 'common_mistakes'
    ]:
        if column in drills_df.columns:
            drills_df[column] = drills_df[column].fillna('')

    repairs_info = {
        "dataset": "drills",
        "was_repaired": bool(repairs.get("added_columns") or repairs.get("coerced_columns") or repairs.get("filled_values")),
        "added_columns": repairs.get("added_columns", [])
    }
    drills_df.attrs['repair_info'] = repairs_info
    drills_df.attrs['repairs'] = repairs
    if validation_errors:
        drills_df.attrs['load_errors'] = validation_errors

    return drills_df



def load_templates(data_path):
    """
    Legacy loader for session templates (JSON). Prefer load_session_templates.
    """
    return load_session_templates(data_path)


def load_session_templates(data_path):
    """
    Load session/block templates from a single source of truth.

    Currently proxies to templates.load_block_templates() stored under data/templates/block_templates.json.
    """
    try:
        from templates import load_block_templates
    except Exception:
        return []
    return load_block_templates(data_path)

def load_pending_changes():
    """
    Load pending changes from temp file

    Returns:
        Dict with pending changes or empty dict
    """
    from config import PENDING_CHANGES_FILE

    if PENDING_CHANGES_FILE.exists():
        with open(PENDING_CHANGES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {
            'drills_to_add': [],
            'drills_to_update': [],
            'drills_to_delete': [],
            'templates_to_save': [],
            'practice_to_save': []
        }

def save_pending_changes(changes_dict):
    """
    Save pending changes to temp file

    Args:
        changes_dict: Dict with pending changes
    """
    from config import PENDING_CHANGES_FILE

    # Ensure temp directory exists
    PENDING_CHANGES_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(PENDING_CHANGES_FILE, 'w', encoding='utf-8') as f:
        json.dump(changes_dict, f, indent=2)

def load_athlete_profile(data_path) -> Optional[dict]:
    username = _get_username()
    if username:
        try:
            raw = db.load_user_data(username, "athlete_profile")
            if raw:
                profile = json.loads(raw)
                return profile if profile.get("name") else None
            return None
        except Exception:
            pass
    # Filesystem fallback for local dev
    profile_path = Path(data_path) / "athlete_profile.json"
    if profile_path.exists():
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

def save_athlete_profile(profile: dict, data_path) -> None:
    username = _get_username()
    if username:
        try:
            db.save_user_data(username, "athlete_profile", json.dumps(profile, default=str))
            return
        except Exception:
            pass
    # Filesystem fallback for local dev
    profile_path = Path(data_path) / "athlete_profile.json"
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, default=str)

def load_completion_log(data_path) -> dict:
    username = _get_username()
    if username:
        try:
            raw = db.load_user_data(username, "completion_log")
            return json.loads(raw) if raw else {}
        except Exception:
            pass
    # Filesystem fallback
    log_path = Path(data_path) / "completion_log.json"
    if log_path.exists():
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_completion_log(log: dict, data_path) -> None:
    username = _get_username()
    if username:
        try:
            db.save_user_data(username, "completion_log", json.dumps(log, default=str))
            return
        except Exception:
            pass
    # Filesystem fallback
    log_path = Path(data_path) / "completion_log.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, default=str)

def load_weekly_training_plan(data_path) -> Optional[dict]:
    username = _get_username()
    if username:
        try:
            raw = db.load_user_data(username, "weekly_training_plan")
            if raw:
                plan = json.loads(raw)
                return plan if plan else None
            return None
        except Exception:
            pass
    # Filesystem fallback
    plan_path = Path(data_path) / "weekly_training_plan.json"
    if plan_path.exists():
        try:
            with open(plan_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

def save_weekly_training_plan(plan: dict, data_path) -> None:
    username = _get_username()
    if username:
        try:
            db.save_user_data(username, "weekly_training_plan", json.dumps(plan, default=str))
            return
        except Exception:
            pass
    # Filesystem fallback
    plan_path = Path(data_path) / "weekly_training_plan.json"
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    with open(plan_path, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2, default=str)

def load_rrs_history(data_path) -> dict:
    username = _get_username()
    if username:
        try:
            raw = db.load_user_data(username, "rrs_history")
            if raw:
                content = json.loads(raw)
                if isinstance(content, dict) and "snapshots" in content:
                    return content
            return {"snapshots": []}
        except Exception:
            pass
    # Filesystem fallback
    history_path = Path(data_path) / "rrs_history.json"
    if history_path.exists():
        try:
            with open(history_path, "r", encoding="utf-8") as f:
                content = json.load(f)
                if isinstance(content, dict) and "snapshots" in content:
                    return content
                return {"snapshots": []}
        except Exception:
            return {"snapshots": []}
    return {"snapshots": []}

def save_rrs_history(history: dict, data_path) -> None:
    username = _get_username()
    if username:
        try:
            db.save_user_data(username, "rrs_history", json.dumps(history, default=str))
            return
        except Exception:
            pass
    # Filesystem fallback
    history_path = Path(data_path) / "rrs_history.json"
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, default=str)


PRESENTER_COLUMNS = [
    'presenter_id', 'full_name', 'display_name', 'current_team',
    'team_level', 'position', 'college', 'graduation_year',
    'bio_short', 'headshot_url', 'active', 'position_tracks'
]

PRESENTER_DEFAULTS = {
    'presenter_id': '',
    'full_name': '',
    'display_name': '',
    'current_team': '',
    'team_level': '',
    'position': '',
    'college': '',
    'graduation_year': '',
    'bio_short': '',
    'headshot_url': '',
    'active': True,
    'position_tracks': '',
}

def load_presenters(data_path) -> pd.DataFrame:
    """
    Load presenter profiles from presenters.csv.
    Returns empty DataFrame with correct columns if file not found.
    Never raises — uses ensure_columns for auto-repair.
    """
    presenter_path = Path(data_path) / 'presenters.csv'
    try:
        if presenter_path.exists():
            df = pd.read_csv(presenter_path)
        else:
            df = pd.DataFrame(columns=PRESENTER_COLUMNS)
    except Exception:
        df = pd.DataFrame(columns=PRESENTER_COLUMNS)
    _, df = ensure_columns(df, PRESENTER_DEFAULTS)
    df['active'] = df['active'].apply(
        lambda v: str(v).strip().lower() not in {'0', 'false', 'no', 'n'}
        if pd.notna(v) else True
    )
    return df

def save_presenters(presenters_df: pd.DataFrame, data_path) -> None:
    """Save presenter profiles to presenters.csv."""
    presenter_path = Path(data_path) / 'presenters.csv'
    presenter_path.parent.mkdir(parents=True, exist_ok=True)
    presenters_df.to_csv(presenter_path, index=False)


def load_mentor_feed(data_path) -> dict:
    """
    Load mentor feed posts from mentor_feed.json.
    Returns {"posts": []} if file does not exist or is malformed.
    Posts are returned sorted newest first by date_posted.
    """
    feed_path = Path(data_path) / "mentor_feed.json"
    if feed_path.exists():
        try:
            with open(feed_path, "r", encoding="utf-8") as f:
                content = json.load(f)
                if isinstance(content, dict) and "posts" in content:
                    posts = content["posts"]
                    # Sort newest first
                    posts.sort(
                        key=lambda p: p.get("date_posted", ""),
                        reverse=True
                    )
                    return {"posts": posts}
                return {"posts": []}
        except Exception:
            return {"posts": []}
    return {"posts": []}


def save_mentor_feed(feed: dict, data_path) -> None:
    """Save mentor feed to mentor_feed.json."""
    feed_path = Path(data_path) / "mentor_feed.json"
    feed_path.parent.mkdir(parents=True, exist_ok=True)
    with open(feed_path, "w", encoding="utf-8") as f:
        json.dump(feed, f, indent=2, default=str)


# --- LEGACY COACH CODE (unused) ---

TEAM_BASE_COLUMNS = [
    'team_id', 'team_name', 'age_group', 'skill_level',
    'typical_roster_size', 'notes', 'created_date'
]

TEAM_PROFILE_COLUMNS = [
    'formation',
    'play_style',
    'key_players',
    'focus_areas',
    'injuries',
    'practice_schedule',
    'upcoming_match',
    'upcoming_match_date',
    'upcoming_match_time',
    'upcoming_match_opponent',
    'season_objectives'
]

TEAM_DEFAULTS = {
    'team_id': '',
    'team_name': '',
    'age_group': '',
    'skill_level': 'intermediate',
    'typical_roster_size': 0,
    'notes': '',
    'created_date': '',
}
for col in TEAM_PROFILE_COLUMNS:
    TEAM_DEFAULTS.setdefault(col, '')

HISTORY_COLUMNS = [
    'session_date', 'session_name', 'session_notes',
    'total_time', 'num_players', 'drills_used', 'categories'
]

HISTORY_DEFAULTS = {
    'session_date': '',
    'session_name': '',
    'session_notes': '',
    'total_time': 0,
    'num_players': 0,
    'drills_used': '',
    'categories': '',
}

def _ensure_columns(df, defaults):
    added_columns = []
    for column, default in defaults.items():
        if column not in df.columns:
            df[column] = default
            added_columns.append(column)
    return df, added_columns

def load_teams(data_path):
    """
    Load team profiles from CSV
    """
    team_path = Path(data_path) / 'team_profiles.csv'
    if team_path.exists():
        try:
            teams_df = pd.read_csv(team_path)
        except Exception as exc:
            teams_df = pd.DataFrame(columns=TEAM_BASE_COLUMNS + TEAM_PROFILE_COLUMNS)
            teams_df.attrs['load_error'] = f"Failed to load team profiles: {exc}"
            teams_df.attrs['repair_info'] = {"dataset": "teams", "was_repaired": False, "added_columns": []}
            return teams_df
    else:
        teams_df = pd.DataFrame(columns=TEAM_BASE_COLUMNS + TEAM_PROFILE_COLUMNS)
        teams_df.attrs['load_error'] = f"Team profiles file not found at {team_path}."
        teams_df.attrs['repair_info'] = {"dataset": "teams", "was_repaired": False, "added_columns": []}

    repairs, teams_df = ensure_columns(teams_df, TEAM_DEFAULTS)

    if 'typical_roster_size' in teams_df.columns:
        teams_df['typical_roster_size'] = pd.to_numeric(
            teams_df['typical_roster_size'], errors='coerce'
        ).fillna(0).astype(int)

    repairs_info = {
        "dataset": "teams",
        "was_repaired": bool(repairs.get("added_columns") or repairs.get("coerced_columns") or repairs.get("filled_values")),
        "added_columns": repairs.get("added_columns", [])
    }
    teams_df.attrs['repair_info'] = repairs_info
    teams_df.attrs['repairs'] = repairs

    return teams_df

def save_teams(data_path, teams_df):
    """
    Save team profiles to CSV
    """
    team_path = Path(data_path) / 'team_profiles.csv'
    teams_df.to_csv(team_path, index=False)

def upsert_team_profile(data_path, profile: dict):
    """
    Upsert a single team profile
    """
    teams_df = load_teams(data_path)
    team_id = profile.get('team_id')
    if not team_id:
        return
    
    if team_id in teams_df['team_id'].values:
        for col in profile:
            if col in teams_df.columns:
                teams_df.loc[teams_df['team_id'] == team_id, col] = profile[col]
    else:
        new_row = pd.DataFrame([profile])
        teams_df = pd.concat([teams_df, new_row], ignore_index=True)
    
    save_teams(data_path, teams_df)
