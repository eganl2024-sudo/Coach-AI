"""Data loading module with caching and auto-refresh"""
import os
import json
import shutil
import pandas as pd
from pathlib import Path
from utils import ensure_columns
import config

DRILL_COLUMNS = [
    'drill_id', 'drill_name', 'category', 'description',
    'players_min', 'players_max', 'duration_minutes', 'field_type',
    'setup_data', 'equipment', 'coaching_points', 'difficulty',
    'intensity', 'coach_rating', 'personal_notes', 'times_used',
    'last_used_date', 'tags', 'is_favorite', 'diagram_path', 'diagram_metadata',
    'positions', 'age_groups', 'coach_cues', 'progression', 'recommended_field_size'
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
}
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
    Load drills from CSV file

    Args:
        data_path: Path to data folder

    Returns:
        DataFrame with drills
    """
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

    for column in ['positions', 'age_groups', 'coach_cues', 'progression', 'recommended_field_size']:
        if column in drills_df.columns:
            drills_df[column] = drills_df[column].fillna('')

    repairs_info = {
        "dataset": "drills",
        "was_repaired": bool(repairs.get("added_columns") or repairs.get("coerced_columns") or repairs.get("filled_values")),
        "added_columns": repairs.get("added_columns", [])
    }
    drills_df.attrs['repair_info'] = repairs_info
    drills_df.attrs['repairs'] = repairs

    return drills_df

def load_teams(data_path):
    """
    Load team profiles from CSV

    Args:
        data_path: Path to data folder

    Returns:
        DataFrame with team profiles
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

    # Normalize roster size to numeric when possible
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
