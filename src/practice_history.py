"""Practice history tracking and template utilities (lightweight rebuild)."""
from __future__ import annotations

import json
import os
from pathlib import Path
from datetime import datetime, UTC
from typing import Optional

import pandas as pd

from templates import BlockTemplate, load_block_templates, save_block_templates

# Basic columns for history files
HISTORY_COLUMNS = [
    "session_date",
    "session_name",
    "session_notes",
    "total_time",
    "num_players",
    "drills_used",
    "categories",
    "is_favorite",
    "session_structure",
]

BAD_CHARS = {
    "—": "-",
    "–": "-",
    "·": "|",
    "•": "-",
    "ðŸ“¬": "",
    "ðŸ“„": "",
}


def sanitize_text_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Replace common garbled characters with ASCII-safe equivalents."""
    if df is None or df.empty:
        return df
    text_cols = [
        "session_name",
        "session_notes",
        "session_structure",
        "categories",
        "session_tags",
        "coach_notes",
        "summary",
        "title",
        "notes",
    ]
    for col in text_cols:
        if col not in df.columns:
            continue
        series = df[col].astype(str)
        for bad, good in BAD_CHARS.items():
            series = series.str.replace(bad, good, regex=False)
        df[col] = series
    return df


def _history_file(team_id: str, data_path: Path | str) -> Path:
    return Path(data_path) / f"practice_history_{team_id}.csv"


def get_history_mtime(team_id: str, data_path: Path | str) -> Optional[float]:
    """Return mtime of the history file if it exists."""
    path = _history_file(team_id, data_path)
    return path.stat().st_mtime if path.exists() else None


def load_practice_history(team_id: str, data_path: Path | str, _mtime=None) -> pd.DataFrame:
    """Load practice history sorted by date desc."""
    history_file = _history_file(team_id, data_path)
    if not history_file.exists():
        return pd.DataFrame(columns=HISTORY_COLUMNS)
    try:
        df = pd.read_csv(history_file)
        if "session_date" in df.columns:
            df["session_date"] = pd.to_datetime(df["session_date"], errors="coerce")
            df = df.sort_values("session_date", ascending=False)
        if "is_favorite" in df.columns:
            df["is_favorite"] = df["is_favorite"].fillna(False).astype(bool)
        df = sanitize_text_fields(df)
        return df
    except Exception as exc:
        print(f"Failed to load practice history for {team_id}: {exc}")
        return pd.DataFrame(columns=HISTORY_COLUMNS)


def save_practice_session(team_id: str, session_dict: dict, data_path: Path | str) -> bool:
    """Append a session to history."""
    history_file = _history_file(team_id, data_path)
    try:
        history_file.parent.mkdir(parents=True, exist_ok=True)
        drills_str = "|".join(session_dict.get("drills_used", []))
        categories_str = "|".join(session_dict.get("categories", []))
        new_row = {
            "session_date": session_dict.get("session_date"),
            "session_name": session_dict.get("session_name", ""),
            "session_notes": session_dict.get("session_notes", ""),
            "total_time": session_dict.get("total_time", 0),
            "num_players": session_dict.get("num_players", 0),
            "drills_used": drills_str,
            "categories": categories_str,
            "is_favorite": bool(session_dict.get("is_favorite", False)),
            "session_structure": session_dict.get("session_structure", ""),
        }
        if history_file.exists():
            df = pd.read_csv(history_file)
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        else:
            df = pd.DataFrame([new_row])
        df.to_csv(history_file, index=False)
        return True
    except Exception as exc:
        print(f"Error saving practice session: {exc}")
        return False


def set_session_favorite(team_id: str, session_date, session_name: str, is_favorite: bool, data_path: Path | str) -> bool:
    """Toggle favorite flag for a specific session."""
    history_file = _history_file(team_id, data_path)
    if not history_file.exists():
        return False
    try:
        df = pd.read_csv(history_file)
        df["session_date"] = pd.to_datetime(df["session_date"], errors="coerce")
        mask = (df["session_date"] == pd.to_datetime(session_date)) & (df["session_name"] == session_name)
        if not mask.any():
            return False
        df.loc[mask, "is_favorite"] = bool(is_favorite)
        df.to_csv(history_file, index=False)
        return True
    except Exception as exc:
        print(f"Error updating favorite: {exc}")
        return False


def get_recent_drill_usage(history_df: pd.DataFrame, num_sessions: int = 2) -> dict:
    """Return mapping drill_id -> sessions ago."""
    recent_usage = {}
    if history_df is None or len(history_df) == 0:
        return recent_usage
    for idx, row in history_df.head(num_sessions).iterrows():
        drills_used = str(row.get("drills_used", "") or "")
        ids = [d.strip() for d in drills_used.split("|") if d.strip()]
        for drill_id in ids:
            if drill_id not in recent_usage:
                recent_usage[drill_id] = idx
    return recent_usage


def update_drill_library_usage(drill_ids, drills_df, data_path: Path | str) -> bool:
    """Increment times_used and last_used_date for drills used."""
    try:
        drill_library_file = Path(data_path) / "drill_library.csv"
        drill_library_file.parent.mkdir(parents=True, exist_ok=True)
        today = datetime.now(UTC).date().isoformat()
        for drill_id in drill_ids:
            mask = drills_df["drill_id"] == drill_id
            if mask.any():
                current_usage = drills_df.loc[mask, "times_used"].values[0]
                drills_df.loc[mask, "times_used"] = current_usage + 1
                drills_df.loc[mask, "last_used_date"] = today
        drills_df.to_csv(drill_library_file, index=False)
        return True
    except Exception as exc:
        print(f"Error updating drill library: {exc}")
        return False


def load_practice_session_from_record(record):
    """Reconstruct a simple session-like object from a history record."""
    if record is None:
        return None
    drills_used = str(record.get("drills_used", "") if isinstance(record, dict) else getattr(record, "drills_used", ""))
    drill_ids = [d.strip() for d in drills_used.split("|") if d.strip()]
    drills = [SimpleNamespace(drill_id=drill_id) for drill_id in drill_ids]
    session_name = record.get("session_name") if isinstance(record, dict) else getattr(record, "session_name", "")
    session_date = record.get("session_date") if isinstance(record, dict) else getattr(record, "session_date", "")
    return SimpleNamespace(session_name=session_name, session_date=session_date, drills=drills)


def save_session_as_template(session_obj, data_path: Path | str) -> bool:
    """Save a session as a simple block template using the templates store."""
    try:
        templates = load_block_templates(data_path)
    except Exception:
        templates = []
    template_name = session_obj.session_name or f"Session {session_obj.session_date}"
    if any(tpl.name == template_name for tpl in templates):
        return True
    drill_ids = [getattr(d, "drill_id", str(d)) for d in getattr(session_obj, "drills", []) or []]
    new_tpl = BlockTemplate(
        name=template_name,
        blocks={"session": drill_ids},
        description=f"Saved from history on {session_obj.session_date}",
        block_durations={},
        created_at=datetime.now(UTC).isoformat(),
    )
    templates.append(new_tpl)
    save_block_templates(templates, data_path)
    return True
