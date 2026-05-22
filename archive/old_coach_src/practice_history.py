"""Practice history tracking, sanitization, and template helpers."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Tuple, Dict
from datetime import datetime, timedelta, UTC

import pandas as pd

from models import PracticeSession, PracticeConfig, SessionDrill
from templates import BlockTemplate, load_block_templates, save_block_templates
from validation import validate_practice_session


def get_recent_use(drill_id: str, df: pd.DataFrame):
    """Return the most recent date the given drill_id was used in the practice history DataFrame, or None if never used."""
    if df is None or df.empty or "drills_used" not in df.columns or "session_date" not in df.columns:
        return None
    filtered = df[df["drills_used"].fillna("").apply(lambda x: drill_id in [d.strip() for d in str(x).split("|")])]
    if filtered.empty:
        return None
    return filtered["session_date"].max()
def get_cached_recency(df: pd.DataFrame) -> dict:
    """Return a dictionary mapping drill_id to recency info (label) based on last usage date."""
    if df is None or df.empty or "drills_used" not in df.columns or "session_date" not in df.columns:
        return {}
    recency = {}
    now = datetime.now(UTC)
    for _, row in df.iterrows():
        session_date = row.get("session_date")
        if pd.isna(session_date):
            continue
        try:
            date_val = pd.to_datetime(session_date)
            # Make date_val timezone-aware in UTC if naive
            if date_val.tzinfo is None or date_val.tzinfo.utcoffset(date_val) is None:
                date_val = date_val.tz_localize("UTC")
            else:
                date_val = date_val.tz_convert("UTC")
        except Exception:
            continue
        for drill_id in str(row["drills_used"]).split("|"):
            drill_id = drill_id.strip()
            if not drill_id:
                continue
            prev = recency.get(drill_id)
            if prev is None or date_val > prev["date"]:
                recency[drill_id] = {"date": date_val}
    # Assign recency labels
    for drill_id, info in recency.items():
        days_ago = (now - info["date"]).days
        if days_ago < 7:
            label = "Fresh"
        elif days_ago < 30:
            label = "Recent"
        else:
            label = "Stale"
        info["label"] = label
    return {k: {"label": v["label"]} for k, v in recency.items()}


"""Practice history tracking, sanitization, and template helpers."""

def get_recent_drill_usage(df: pd.DataFrame) -> dict:
    """Return a dictionary mapping drill_id to usage count from COMPLETED sessions only."""
    if df is None or df.empty or "drills_used" not in df.columns:
        return {}

    # Only count completed sessions for recency (exclude planned sessions)
    if "status" in df.columns:
        completed_df = df[(df["status"] == "completed") | (df["status"].isna())]
    else:
        # Backward compatibility: assume all sessions are completed if no status column
        completed_df = df

    usage = {}
    for drills in completed_df["drills_used"].dropna():
        for drill_id in str(drills).split("|"):
            drill_id = drill_id.strip()
            if drill_id:
                usage[drill_id] = usage.get(drill_id, 0) + 1
    return usage



# Tag parsing helper for session tags field
def parse_session_tags(raw_tags):
    """Return a list of clean tags from a session_tags cell (supports comma or pipe delim)."""
    if raw_tags is None or (isinstance(raw_tags, float) and pd.isna(raw_tags)):
        return []
    raw = str(raw_tags)
    delimiter = "," if "," in raw else "|"
    return [t.strip() for t in raw.split(delimiter) if t.strip()]


# Garbled character cleanup
BAD_CHARS = {
    "\u00a0": " ",   # non-breaking space
    "\ufffd": "",    # replacement char
    "Â": "",
    "â€™": "'",
    "â€œ": '"',
    "â€": '"',
    "â€“": "-",
    "â€”": "-",
}

# History columns baseline (extend if needed by callers)
HISTORY_COLUMNS = [
    "session_date",
    "session_name",
    "session_title",
    "session_notes",
    "coach_notes",
    "total_time",
    "num_players",
    "drills_used",
    "categories",
    "season_segment",
    "session_tags",
    "avg_intensity_score",
    "intensity_level",
    "is_favorite",
    "session_structure",
    "session_json",
    "team_id",
    "team_name",
    "status",
    "session_id",
    "event_id",
    "kickoff_time",
    "opponent",
    "duration_min",
    "created_at",
]

HISTORY_DEFAULTS = {
    "session_date": None,
    "session_name": "",
    "session_title": "",
    "session_notes": "",
    "coach_notes": "",
    "total_time": 0,
    "num_players": 0,
    "drills_used": "",
    "categories": "",
    "season_segment": "",
    "session_tags": "",
    "avg_intensity_score": None,
    "intensity_level": "",
    "is_favorite": False,
    "session_structure": "",
    "session_json": "",
    "team_id": "",
    "team_name": "",
    "status": "completed",
    "session_id": "",
    "event_id": "",
    "kickoff_time": "",
    "opponent": "",
    "duration_min": None,
    "created_at": None,
}


def _normalize_history_args(arg1, arg2) -> tuple[Path, str]:
    """
    Accept both (data_path, team_id) and legacy (team_id, data_path) ordering.
    """
    first = Path(str(arg1))
    second = Path(str(arg2))

    first_looks_like_path = first.exists() or any(sep in str(arg1) for sep in ("\\", "/"))
    second_looks_like_path = second.exists() or any(sep in str(arg2) for sep in ("\\", "/"))

    if first_looks_like_path and not second_looks_like_path:
        return first, str(arg2)
    if second_looks_like_path and not first_looks_like_path:
        return second, str(arg1)
    if first_looks_like_path:
        return first, str(arg2)
    return second, str(arg1)


def _history_path(data_path: Path | str, team_id: str) -> Path:
    return Path(data_path) / f"practice_history_{team_id}.csv"


def get_history_mtime(arg1, arg2) -> Optional[float]:
    data_path, team_id = _normalize_history_args(arg1, arg2)
    path = _history_path(data_path, team_id)
    return path.stat().st_mtime if path.exists() else None


def _ensure_history_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure history dataframes always expose the full current schema."""
    work_df = df.copy()

    for col in HISTORY_COLUMNS:
        if col not in work_df.columns:
            default = HISTORY_DEFAULTS.get(col)
            if col == "session_id":
                import uuid
                work_df[col] = [str(uuid.uuid4()) for _ in range(len(work_df))]
            else:
                work_df[col] = default

    if "is_favorite" in work_df.columns:
        work_df["is_favorite"] = work_df["is_favorite"].fillna(False).astype(bool)

    for col in [
        "session_name",
        "session_title",
        "session_notes",
        "coach_notes",
        "drills_used",
        "categories",
        "season_segment",
        "session_tags",
        "session_structure",
        "session_json",
        "team_id",
        "team_name",
        "status",
        "event_id",
        "kickoff_time",
        "opponent",
        "intensity_level",
    ]:
        work_df[col] = work_df[col].fillna("").astype("object")

    return work_df[HISTORY_COLUMNS]


def sanitize_text_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Replace bad characters across text columns while preserving NaN."""
    if df is None or df.empty:
        return df
    text_cols = [
        "session_name",
        "session_notes",
        "categories",
        "team_name",
        "coach_notes",
        "session_tags",
        "title",
        "summary",
        "notes",
    ]
    for col in text_cols:
        if col not in df.columns:
            continue
        # Ensure object dtype to avoid list/float coercion issues
        df[col] = df[col].astype("object")
        series = df[col]
        mask = ~series.isna()
        cleaned = series.copy()
        cleaned.loc[mask] = (
            cleaned.loc[mask]
            .astype(str)
            .apply(
                lambda val: _replace_chars(val)
            )
        )
        df[col] = cleaned
    return df


def _replace_chars(text: str) -> str:
    result = text
    for bad, good in BAD_CHARS.items():
        result = result.replace(bad, good)
    return result


def load_practice_history(team_id: str, data_path: Path | str, _mtime=None) -> pd.DataFrame:
    """Load practice history for a team, sanitize text, and sort newest first."""
    path = _history_path(data_path, team_id)
    if not path.exists():
        return _ensure_history_columns(pd.DataFrame(columns=HISTORY_COLUMNS))
    try:
        df = pd.read_csv(path)
    except Exception as exc:
        print(f"Error loading practice history for team {team_id}: {exc}")
        return _ensure_history_columns(pd.DataFrame(columns=HISTORY_COLUMNS))

    df = _ensure_history_columns(df)

    if "session_date" in df.columns:
        df["session_date"] = pd.to_datetime(df["session_date"], errors="coerce")
        df = df.dropna(subset=["session_date"])
        df = df.sort_values("session_date", ascending=False)
        df["session_date"] = df["session_date"].dt.date

    df = sanitize_text_fields(df)
    return _ensure_history_columns(df)


def save_practice_history(df: pd.DataFrame, data_path: Path | str, team_id: str) -> None:
    """Persist a practice history dataframe to CSV."""
    import os
    import traceback

    path = _history_path(data_path, team_id)

    try:
        # Ensure directory exists
        print(f"[FILE] Creating directory: {path.parent}")
        path.parent.mkdir(parents=True, exist_ok=True)

        # Check directory is writable
        if not os.access(path.parent, os.W_OK):
            raise PermissionError(f"Directory not writable: {path.parent}")

        print(f"[FILE] Writing CSV to: {path}")
        print(f"[FILE] File size will be ~{len(df) * 100} bytes with {len(df)} rows")

        df.to_csv(path, index=False)

        # Verify file was written
        if not path.exists():
            raise FileNotFoundError(f"File was not created after writing: {path}")

        file_size = os.path.getsize(path)
        print(f"[FILE] Successfully wrote {file_size} bytes to {path}")

    except PermissionError as e:
        error_msg = f"Permission denied writing to {path}. Check if file is open in Excel or another program."
        print(f"[ERROR] {error_msg}")
        print(f"[ERROR] {traceback.format_exc()}")
        raise PermissionError(error_msg) from e
    except Exception as e:
        error_msg = f"Failed to write practice history to {path}: {e}"
        print(f"[ERROR] {error_msg}")
        print(f"[ERROR] {traceback.format_exc()}")
        raise


def set_session_favorite_df(df: pd.DataFrame, session_id: str, favorite: bool) -> pd.DataFrame:
    """Set favorite flag by session_id column when present; otherwise no-op."""
    if "session_id" not in df.columns:
        return df
    mask = df["session_id"] == session_id
    if mask.any():
        df = df.copy()
        df.loc[mask, "is_favorite"] = bool(favorite)
    return df


def set_session_favorite(team_id: str, session_date, session_name: str, favorite: bool, data_path: Path | str) -> bool:
    """File-based favorite toggle used by UI; matches on date + name."""
    path = _history_path(data_path, team_id)
    if not path.exists():
        return False
    try:
        df = pd.read_csv(path)
    except Exception as exc:
        print(f"Error reading history for favorites: {exc}")
        return False
    try:
        df["session_date"] = pd.to_datetime(df["session_date"], errors="coerce").dt.date
        target_date = pd.to_datetime(session_date, errors="coerce").date()
        mask = (df["session_date"] == target_date) & (df["session_name"] == session_name)
        if not mask.any():
            return False
        df.loc[mask, "is_favorite"] = bool(favorite)
        df.to_csv(path, index=False)
        return True
    except Exception as exc:
        print(f"Error updating favorite: {exc}")
        return False


def _update_session_field(
    team_id: str,
    session_date,
    session_name: str,
    field_name: str,
    field_value,
    data_path: Path | str,
) -> bool:
    """Update one history field for a session identified by date + name."""
    path = _history_path(data_path, team_id)
    df = _ensure_history_columns(df)
    if not path.exists():
        return False
    try:
        df = pd.read_csv(path)
        df = _ensure_history_columns(df)
        df["session_date"] = pd.to_datetime(df["session_date"], errors="coerce").dt.date
        target_date = pd.to_datetime(session_date, errors="coerce").date()
        mask = (df["session_date"] == target_date) & (df["session_name"] == session_name)
        if not mask.any():
            return False
        df.loc[mask, field_name] = field_value
        df.to_csv(path, index=False)
        return True
    except Exception as exc:
        print(f"Error updating {field_name}: {exc}")
        return False


def update_session_notes(team_id: str, session_date, session_name: str, notes: str, data_path: Path | str) -> bool:
    """Update coach notes for a saved session."""
    return _update_session_field(team_id, session_date, session_name, "coach_notes", notes or "", data_path)


def update_session_title(team_id: str, session_date, session_name: str, title: str, data_path: Path | str) -> bool:
    """Update the optional display title for a saved session."""
    return _update_session_field(team_id, session_date, session_name, "session_title", title or "", data_path)


def update_session_tags(team_id: str, session_date, session_name: str, tags: list[str], data_path: Path | str) -> bool:
    """Update the stored session tags for a saved session."""
    payload = "|".join(str(tag).strip() for tag in (tags or []) if str(tag).strip())
    return _update_session_field(team_id, session_date, session_name, "session_tags", payload, data_path)


def compute_recent_focus(history_df: pd.DataFrame, days: int = 28) -> dict:
    """
    Summarize recent category and tag minutes across completed sessions.

    Returns a stable payload for analytics/UI callers.
    """
    empty = {"category_minutes": {}, "attribute_minutes": {}, "total_minutes": 0.0}
    if history_df is None or history_df.empty:
        return empty

    df = history_df.copy()
    if "status" in df.columns:
        df = df[(df["status"] == "completed") | (df["status"].isna())]
    if df.empty:
        return empty

    df["session_date"] = pd.to_datetime(df["session_date"], errors="coerce")
    df = df.dropna(subset=["session_date"])
    if df.empty:
        return empty

    cutoff = pd.Timestamp.now().normalize() - pd.Timedelta(days=days)
    df = df[df["session_date"] >= cutoff]
    if df.empty:
        return empty

    category_minutes: dict[str, float] = {}
    attribute_minutes: dict[str, float] = {}

    for _, row in df.iterrows():
        total_time = row.get("total_time", 0)
        try:
            total_time = float(total_time)
        except Exception:
            total_time = 0.0

        categories = [c.strip() for c in str(row.get("categories", "")).split("|") if c.strip()]
        if categories:
            share = total_time / len(categories) if total_time else 0.0
            for category in categories:
                category_minutes[category] = category_minutes.get(category, 0.0) + share

        for tag in parse_session_tags(row.get("session_tags", "")):
            attribute_minutes[tag] = attribute_minutes.get(tag, 0.0) + total_time

    total_minutes = float(sum(category_minutes.values()))
    return {
        "category_minutes": category_minutes,
        "attribute_minutes": attribute_minutes,
        "total_minutes": total_minutes,
    }


def _category_title(category: str) -> str:
    mapping = {
        "Small Sided Games": "SSG",
        "Cool Down": "Cooldown",
    }
    category = str(category or "").strip()
    return mapping.get(category, category)


def build_session_name(session_obj: PracticeSession, session_dict: Dict | None = None) -> str:
    """Stable internal name for matching saved sessions."""
    session_dict = session_dict or {}
    explicit = str(session_dict.get("session_name", "") or "").strip()
    if explicit:
        return explicit
    return f"Practice {getattr(session_obj, 'session_date', '')}".strip()


def build_session_title(session_obj: PracticeSession, session_dict: Dict | None = None) -> str:
    """Human-friendly display title for history, details, and favorites."""
    session_dict = session_dict or {}
    explicit = str(session_dict.get("session_title", "") or "").strip()
    if explicit:
        return explicit

    notes = str(
        session_dict.get("session_notes", "")
        or getattr(getattr(session_obj, "config", None), "session_notes", "")
        or ""
    ).strip()
    if notes:
        return notes[:80]

    opponent = str(session_dict.get("opponent", "") or "").strip()
    if opponent:
        return f"Match Prep vs {opponent}"

    categories = session_dict.get("categories", getattr(session_obj, "selected_categories", []))
    if isinstance(categories, str):
        categories = [c.strip() for c in categories.split("|") if c.strip()]
    categories = [_category_title(cat) for cat in (categories or []) if str(cat).strip()]

    if len(categories) >= 2:
        return f"{categories[0]} + {categories[1]} Session"
    if len(categories) == 1:
        return f"{categories[0]} Session"
    return f"Practice {getattr(session_obj, 'session_date', '')}".strip()


def _safe_get(row: pd.Series, key: str, default=None):
    if isinstance(row, dict):
        return row.get(key, default)
    try:
        return getattr(row, key, default)
    except Exception:
        return default


def load_practice_session_from_record(row: pd.Series) -> Optional[PracticeSession]:
    """Rebuild a PracticeSession from a history row; return None if not possible."""
    if row is None:
        return None
    try:
        # Attempt to parse structured payload first
        raw_structure = _safe_get(row, "session_structure", "")
        if isinstance(raw_structure, str) and raw_structure.strip():
            try:
                payload = json.loads(raw_structure)
            except Exception:
                payload = None
        elif isinstance(raw_structure, dict):
            payload = raw_structure
        else:
            payload = None

        if payload:
            try:
                return validate_practice_session(payload)
            except Exception:
                # fall back to legacy reconstruction below
                pass

        # Fallback: minimal reconstruction using drills_used
        drills_used = str(_safe_get(row, "drills_used", "") or "")
        drill_ids = [d.strip() for d in drills_used.split("|") if d.strip()]
        drills = [SessionDrill.from_dict({"drill_id": d, "drill_name": d, "category": "", "intensity": "", "players_min": 0, "players_max": 0, "field_type": "", "description": "", "coaching_points": "", "equipment": "", "setup_data": "", "allocated_time": 0, "target_intensity": ""}) for d in drill_ids]
        categories = _safe_get(row, "categories", "")
        cat_list = [c.strip() for c in str(categories).split("|") if c.strip()]
        config = PracticeConfig(
            duration_minutes=int(_safe_get(row, "total_time", 0) or 0),
            num_players=int(_safe_get(row, "num_players", 0) or 0),
            num_drills=len(drills) if drills else 0,
            selected_categories=cat_list,
            session_date=str(_safe_get(row, "session_date", "")),
            session_notes=str(_safe_get(row, "session_notes", "") or ""),
            focus_tags=[],
            favorites_only=False,
            use_team_profile=True,
        )
        return PracticeSession(
            session_id="",
            team_id=str(_safe_get(row, "team_id", "")),
            team_name=str(_safe_get(row, "team_name", "")),
            session_date=config.session_date,
            config=config,
            duration_minutes=config.duration_minutes,
            num_players=config.num_players,
            num_drills=config.num_drills,
            selected_categories=config.selected_categories,
            drills=drills,
        )
    except Exception:
        return None


def save_practice_session(
    team_id: str,
    session_obj: PracticeSession,
    data_path: Path | str,
    session_dict: Dict | None = None,
    event_id: str | None = None,
) -> None:
    """
    Save a generated PracticeSession to the team's practice history.

    This is the main entry point used by the Practice Generator UI.
    It loads existing history, appends a new row, and writes back to disk.

    Args:
        team_id: The team identifier
        session_obj: The PracticeSession object to save
        data_path: Path to the data directory
        session_dict: Optional pre-built row dictionary; if None, built from session_obj

    Raises:
        Exception: If the save operation fails; the exception message describes the error.
    """
    try:
        from datetime import date as date_cls

        print(f"[HISTORY] Starting save_practice_session for team {team_id}")

        # Validate and migrate session payload when possible (non-fatal)
        try:
            if not isinstance(session_obj, PracticeSession):
                session_obj = validate_practice_session(session_obj)
            else:
                session_obj = validate_practice_session(session_obj.to_dict())
        except Exception:
            pass

        # Load existing history for this team
        print(f"[HISTORY] Loading practice history...")
        history_df = load_practice_history(team_id, data_path)
        print(f"[HISTORY] Loaded {len(history_df)} existing rows")

        # Build the new row from session_obj and optional session_dict
        if session_dict is None:
            session_dict = {}

        config_obj = getattr(session_obj, "config", None)
        # Generate a unique session_id if not already present
        import uuid
        session_id = getattr(session_obj, "session_id", None) or str(uuid.uuid4())
        event_id_val = (
            event_id
            if event_id is not None
            else session_dict.get("event_id")
            if session_dict
            else getattr(session_obj, "event_id", "")
        )

        # Determine session status: planned if future date, completed if past/today
        session_date_str = str(getattr(session_obj, "session_date", ""))
        try:
            session_date = pd.to_datetime(session_date_str).date()
        except Exception:
            session_date = date_cls.today()

        today = date_cls.today()
        status = "planned" if session_date > today else "completed"
        print(f"[HISTORY] Session status: {status} (date: {session_date_str})")

        avg_intensity_score = session_dict.get("avg_intensity_score")
        intensity_level = session_dict.get("intensity_level", "")
        if avg_intensity_score in (None, "") and isinstance(session_obj, PracticeSession):
            avg_intensity_score = session_obj.compute_avg_intensity()
        if not intensity_level and isinstance(session_obj, PracticeSession):
            intensity_level = session_obj.classify_intensity(avg_intensity_score)

        print(f"[HISTORY] Building new row...")
        try:
            # Prefer a full session_structure if provided
            if session_dict and isinstance(session_dict.get("session_structure"), dict):
                payload_dict = session_dict.get("session_structure")
            else:
                payload_dict = _session_to_payload_dict(session_obj)
            new_row = {
                "session_date": session_date_str,
                "session_name": build_session_name(session_obj, session_dict),
                "session_title": build_session_title(session_obj, session_dict),
                "session_notes": session_dict.get(
                    "session_notes",
                    getattr(config_obj, "session_notes", "") if config_obj else "",
                ),
                "coach_notes": session_dict.get("coach_notes", ""),
                "total_time": int(session_dict.get("total_time", session_obj.duration_minutes)),
                "num_players": int(session_dict.get("num_players", session_obj.num_players)),
                "drills_used": "|".join(
                    str(d) for d in session_dict.get("drills_used", [d.drill_id for d in session_obj.drills])
                ),
                "categories": "|".join(
                    str(c) for c in session_dict.get("categories", session_obj.selected_categories)
                ),
                "season_segment": session_dict.get("season_segment", ""),
                "session_tags": "|".join(
                    str(tag).strip()
                    for tag in session_dict.get("session_tags", [])
                    if str(tag).strip()
                ) if isinstance(session_dict.get("session_tags"), list) else str(session_dict.get("session_tags", "") or ""),
                "avg_intensity_score": avg_intensity_score,
                "intensity_level": intensity_level,
                "is_favorite": session_dict.get("is_favorite", False),
                "session_structure": json.dumps(payload_dict),
                "team_id": team_id,
                "team_name": getattr(session_obj, "team_name", ""),
                "status": status,
                "session_id": session_id,
                "event_id": event_id_val or "",
                "kickoff_time": session_dict.get("kickoff_time") if session_dict else None,
                "opponent": session_dict.get("opponent") if session_dict else None,
                "duration_min": session_dict.get("duration_min") if session_dict else None,
                "session_json": json.dumps(payload_dict),
                "created_at": datetime.now().isoformat(),
            }
            print(f"[HISTORY] New row built successfully")
        except Exception as e:
            print(f"[ERROR] Failed to build new_row: {e}")
            import traceback
            print(f"[ERROR] Traceback:\n{traceback.format_exc()}")
            raise

        # Append to history - reorder columns to match existing history_df
        try:
            print(f"[HISTORY] Creating DataFrame from new row...")
            new_df = pd.DataFrame([new_row])
            print(f"[HISTORY] New DataFrame created with columns: {list(new_df.columns)}")

            # Use the columns from the existing history_df, or HISTORY_COLUMNS if history is empty
            if not history_df.empty:
                target_columns = list(history_df.columns)
                print(f"[HISTORY] Using existing columns from history_df: {target_columns}")
            else:
                target_columns = HISTORY_COLUMNS
                print(f"[HISTORY] Using default HISTORY_COLUMNS: {target_columns}")

            # Add any missing columns to new_df with None values
            for col in target_columns:
                if col not in new_df.columns:
                    print(f"[HISTORY] Adding missing column to new_row: {col}")
                    new_df[col] = None

            # Select only the target columns in order
            new_df = new_df[target_columns]
            print(f"[HISTORY] DataFrame reordered successfully")

            history_df = pd.concat([history_df, new_df], ignore_index=True)
            print(f"[HISTORY] Concatenation successful, now have {len(history_df)} rows")
        except Exception as e:
            print(f"[ERROR] Failed during DataFrame manipulation: {e}")
            import traceback
            print(f"[ERROR] Traceback:\n{traceback.format_exc()}")
            raise

        # Save back to disk
        try:
            print(f"[HISTORY] About to save {len(history_df)} rows for team {team_id}")
            print(f"[HISTORY] Data path: {data_path}")
            save_practice_history(history_df, data_path, team_id)
            print(f"[HISTORY] Successfully saved practice session with status={status}")
        except Exception as e:
            print(f"[ERROR] Failed during save_practice_history: {e}")
            import traceback
            print(f"[ERROR] Traceback:\n{traceback.format_exc()}")
            raise

    except Exception as exc:
        import traceback
        print(f"[ERROR] Error saving practice session: {exc}")
        print(f"[ERROR] Traceback:\n{traceback.format_exc()}")
        raise


def _session_to_payload_dict(session: PracticeSession) -> Dict:
    """Convert a PracticeSession to a serializable dictionary for storage."""
    # Helper to convert BlockDurationSummary objects to dicts
    def _serialize_block_duration(block_duration):
        if hasattr(block_duration, '__dict__'):
            return block_duration.__dict__
        return block_duration

    return {
        "session_id": getattr(session, "session_id", ""),
        "team_id": getattr(session, "team_id", ""),
        "team_name": getattr(session, "team_name", ""),
        "session_date": getattr(session, "session_date", ""),
        "duration_minutes": getattr(session, "duration_minutes", 0),
        "num_players": getattr(session, "num_players", 0),
        "num_drills": getattr(session, "num_drills", 0),
        "selected_categories": getattr(session, "selected_categories", []),
        "config": {
            "duration_minutes": getattr(getattr(session, "config", None), "duration_minutes", 0),
            "num_players": getattr(getattr(session, "config", None), "num_players", 0),
            "session_date": getattr(getattr(session, "config", None), "session_date", ""),
            "session_notes": getattr(getattr(session, "config", None), "session_notes", ""),
            "selected_categories": getattr(getattr(session, "config", None), "selected_categories", []),
            "focus_tags": getattr(getattr(session, "config", None), "focus_tags", []),
            "favorites_only": getattr(getattr(session, "config", None), "favorites_only", False),
            "use_team_profile": getattr(getattr(session, "config", None), "use_team_profile", True),
            "template_blocks": getattr(getattr(session, "config", None), "template_blocks", None),
        },
        "drills": [
            {
                "drill_id": getattr(d, "drill_id", ""),
                "drill_name": getattr(d, "drill_name", ""),
                "category": getattr(d, "category", ""),
                "intensity": getattr(d, "intensity", ""),
                "allocated_time": getattr(d, "allocated_time", 0),
                "target_intensity": getattr(d, "target_intensity", ""),
            }
            for d in getattr(session, "drills", [])
        ],
        "team_profile_summary": getattr(session, "team_profile_summary", {}),
        "equipment_needed": getattr(session, "equipment_needed", []),
        "category_summary": getattr(session, "category_summary", {}),
        "intensity_summary": getattr(session, "intensity_summary", {}),
        "manual_adjustments": getattr(session, "manual_adjustments", {}),
        "block_duration_summaries": [
            _serialize_block_duration(b) for b in getattr(session, "block_duration_summaries", [])
        ],
        "template_notes": getattr(session, "template_notes", []),
        "warnings": getattr(session, "warnings", []),
    }


def load_practice_session_by_id(team_id: str, session_id: str, data_path: Path | str) -> PracticeSession | None:
    """
    Load and reconstruct a PracticeSession from history by its session_id.

    This enables the "Reuse session" functionality by loading the exact
    session that was saved previously, with all drills in the same order.

    Args:
        team_id: The team identifier
        session_id: The session_id to load
        data_path: Path to the data directory

    Returns:
        A reconstructed PracticeSession object, or None if not found
    """
    from datetime import date as date_cls

    try:
        history_df = load_practice_history(team_id, data_path)
        if history_df.empty:
            return None

        # Find the row with matching session_id
        mask = history_df["session_id"] == session_id
        if not mask.any():
            return None

        row = history_df[mask].iloc[0]

        # Reconstruct from the saved session_structure JSON
        if pd.isna(row.get("session_structure")) or row.get("session_structure") == "":
            return None

        session_dict = json.loads(row["session_structure"])
        try:
            return validate_practice_session(session_dict)
        except Exception:
            # fall back to legacy reconstruction if validation fails
            pass

        # Legacy reconstruction
        drills = []
        for drill_data in session_dict.get("drills", []):
            drill = SessionDrill(
                drill_id=drill_data.get("drill_id", ""),
                drill_name=drill_data.get("drill_name", ""),
                category=drill_data.get("category", ""),
                intensity=drill_data.get("intensity", ""),
                players_min=drill_data.get("players_min", 6),
                players_max=drill_data.get("players_max", 30),
                field_type=drill_data.get("field_type", "Full"),
                description=drill_data.get("description", ""),
                coaching_points=drill_data.get("coaching_points", ""),
                equipment=drill_data.get("equipment", ""),
                setup_data=drill_data.get("setup_data", ""),
                allocated_time=drill_data.get("allocated_time", 0),
                target_intensity=drill_data.get("target_intensity", ""),
            )
            drills.append(drill)

        config_data = session_dict.get("config", {})
        num_drills_val = len(drills)
        config = PracticeConfig(
            duration_minutes=config_data.get("duration_minutes", 90),
            num_players=config_data.get("num_players", 12),
            num_drills=num_drills_val,
            selected_categories=config_data.get("selected_categories", []),
            session_date=config_data.get("session_date", str(date_cls.today())),
            session_notes=config_data.get("session_notes", ""),
            focus_tags=config_data.get("focus_tags", []),
            favorites_only=config_data.get("favorites_only", False),
            use_team_profile=config_data.get("use_team_profile", True),
            template_blocks=config_data.get("template_blocks"),
        )

        session = PracticeSession(
            team_id=session_dict.get("team_id", team_id),
            team_name=session_dict.get("team_name", ""),
            session_date=session_dict.get("session_date", str(date_cls.today())),
            duration_minutes=session_dict.get("duration_minutes", 90),
            num_players=session_dict.get("num_players", 12),
            num_drills=num_drills_val,
            selected_categories=session_dict.get("selected_categories", []),
            drills=drills,
            config=config,
            session_id=session_id,
            team_profile_summary=session_dict.get("team_profile_summary", {}),
            equipment_needed=session_dict.get("equipment_needed", []),
            category_summary=session_dict.get("category_summary", {}),
            intensity_summary=session_dict.get("intensity_summary", {}),
            manual_adjustments=session_dict.get("manual_adjustments", {}),
            block_duration_summaries=session_dict.get("block_duration_summaries", []),
            template_notes=session_dict.get("template_notes", []),
            warnings=session_dict.get("warnings", []),
        )

        return session

    except Exception as exc:
        print(f"Error loading practice session {session_id}: {exc}")
        return None


def load_sessions_for_team(data_path: Path | str, team_id: str) -> pd.DataFrame:
    """
    Load all saved practice sessions for the given team into a DataFrame.
    Returns empty DataFrame with expected columns if none exist.
    """
    mtime = get_history_mtime(data_path, team_id)
    sessions_df = load_practice_history(team_id, data_path, mtime)
    if sessions_df is None or sessions_df.empty:
        return pd.DataFrame(columns=HISTORY_COLUMNS)
    # ensure session_id present
    if "session_id" not in sessions_df.columns:
        import uuid
        sessions_df["session_id"] = [str(uuid.uuid4()) for _ in range(len(sessions_df))]
    sessions_df["team_id"] = sessions_df.get("team_id", team_id)
    return sessions_df


def save_session_for_team(
    data_path: Path | str,
    team_id: str,
    session: dict,
) -> dict:
    """
    Save a single practice session for this team through the canonical CSV path.
    Ensures session_id and team_id are set.
    """
    payload = dict(session or {})
    payload["team_id"] = payload.get("team_id") or team_id
    if not payload.get("session_id"):
        import uuid
        payload["session_id"] = str(uuid.uuid4())
    # Build PracticeSession-like object, preferring full structure if present
    try:
        from models import PracticeSession
        session_data = payload.get("session_structure") if isinstance(payload.get("session_structure"), dict) else payload
        session_obj = PracticeSession.from_dict(session_data)
    except Exception:
        session_obj = payload

    save_practice_session(
        team_id=team_id,
        session_obj=session_obj if isinstance(session_obj, PracticeSession) else session_obj,
        data_path=data_path,
        session_dict=payload,
        event_id=payload.get("event_id"),
    )
    return payload


def load_full_session_by_id(
    data_path: Path | str,
    team_id: str,
    session_id: str,
) -> Optional[dict]:
    """
    Load the full PracticeSession payload (including drills/blocks) for a team/session_id.
    """
    sessions_df = load_sessions_for_team(data_path, team_id)
    if sessions_df is None or sessions_df.empty:
        return None
    try:
        mask = sessions_df["session_id"].astype(str) == str(session_id)
        match = sessions_df[mask]
        if match.empty:
            return None
        row = match.iloc[0]
        for field in ["session_json", "session_structure"]:
            val = row.get(field)
            if isinstance(val, str) and val.strip():
                try:
                    return json.loads(val)
                except Exception:
                    continue
            if isinstance(val, dict):
                return val
    except Exception:
        return None
    return None


def delete_session_for_team(
    data_path: Path | str,
    team_id: str,
    session_id: str,
) -> bool:
    """
    Delete a practice session for the given team_id + session_id.
    Uses the same storage as load_sessions_for_team.
    """
    sessions_df = load_sessions_for_team(data_path, team_id)
    if sessions_df is None or sessions_df.empty:
        return False
    mask = sessions_df["session_id"].astype(str) == str(session_id)
    if not mask.any():
        return False
    updated = sessions_df[~mask].copy()
    # Persist back to the canonical history CSV
    path = _history_path(data_path, team_id)
    updated.to_csv(path, index=False)
    # If there were any per-session files, remove them (optional best-effort)
    try:
        sessions_dir = Path(data_path) / "sessions" / str(team_id)
        session_file = sessions_dir / f"{session_id}.json"
        if session_file.exists():
            session_file.unlink()
    except Exception:
        pass
    return True


def get_last_session_for_team(team_id: str, data_path: Path | str) -> PracticeSession | None:
    """
    Return the most recent saved session (as PracticeSession) for this team.
    """
    history_df = load_practice_history(team_id, data_path)
    if history_df is None or history_df.empty:
        return None
    history_df = history_df.sort_values("session_date", ascending=False)
    latest_row = history_df.iloc[0]
    session_id = latest_row.get("session_id", "")
    if session_id:
        return load_practice_session_by_id(team_id, session_id, data_path)
    return load_practice_session_from_record(latest_row)


def get_session_by_id(sessions_df: pd.DataFrame, session_id: str) -> Optional[dict]:
    """
    Return a single session dict matching session_id, or None.
    """
    if sessions_df is None or sessions_df.empty or not session_id:
        return None
    try:
        mask = sessions_df["session_id"].astype(str) == str(session_id)
        match = sessions_df[mask]
        if not match.empty:
            return match.iloc[0].to_dict()
    except Exception:
        return None
    return None


def summarize_focus_and_gaps(sessions_df: pd.DataFrame, last_n: int = 6) -> dict:
    """
    Look at the last N completed sessions and return category minutes and gaps.
    """
    if sessions_df is None or sessions_df.empty:
        return {"total_minutes_by_category": {}, "pct_by_category": {}, "missing_categories": []}

    df = sessions_df.copy()
    if "status" in df.columns:
        df = df[(df["status"] == "completed") | (df["status"].isna())]
    df = df.head(last_n)

    totals: dict[str, float] = {}
    for _, row in df.iterrows():
        structure = row.get("session_structure") or row.get("session_json") or ""
        payload = None
        if isinstance(structure, str) and structure.strip():
            try:
                payload = json.loads(structure)
            except Exception:
                payload = None
        if payload and isinstance(payload, dict):
            drills = payload.get("drills", [])
            for drill in drills:
                cat = drill.get("category") or ""
                minutes = drill.get("allocated_time") or 0
                try:
                    minutes = float(minutes)
                except Exception:
                    minutes = 0
                if cat:
                    totals[cat] = totals.get(cat, 0) + minutes
        else:
            cats = row.get("categories", "")
            cats_list = [c.strip() for c in str(cats).split("|") if c.strip()]
            time_each = 0
            try:
                time_each = float(row.get("total_time", 0)) / max(1, len(cats_list))
            except Exception:
                time_each = 0
            for cat in cats_list:
                totals[cat] = totals.get(cat, 0) + time_each

    total_minutes = sum(totals.values())
    pct = {cat: (mins / total_minutes) * 100 if total_minutes else 0 for cat, mins in totals.items()}

    try:
        from config import CATEGORIES

        missing = [c for c in CATEGORIES if totals.get(c, 0) == 0]
    except Exception:
        missing = []

    return {
        "total_minutes_by_category": totals,
        "pct_by_category": pct,
        "missing_categories": missing,
    }


def update_drill_library_usage(drill_ids: list, drills_df: pd.DataFrame, data_path: Path | str) -> bool:
    """
    Update usage counts for drills in the drill library.

    Increments the usage count for each drill that was used in the session.

    Args:
        drill_ids: List of drill_id strings that were used
        drills_df: The drills DataFrame
        data_path: Path to the data directory

    Returns:
        True if successfully updated, False otherwise
    """
    if drills_df is None or drills_df.empty:
        return False

    try:
        work_df = drills_df.copy()

        if "times_used" not in work_df.columns:
            work_df["times_used"] = 0
        if "last_used_date" not in work_df.columns:
            work_df["last_used_date"] = ""

        today_str = datetime.now().date().isoformat()
        for drill_id in drill_ids:
            if "drill_id" in work_df.columns:
                mask = work_df["drill_id"] == drill_id
                if mask.any():
                    for idx in work_df[mask].index:
                        try:
                            val = work_df.at[idx, "times_used"]
                            current = int(float(val)) if val not in [None, "", "NaN"] else 0
                        except Exception:
                            current = 0
                        work_df.at[idx, "times_used"] = current + 1
                        work_df.at[idx, "last_used_date"] = today_str

        drills_path = Path(data_path) / "drill_library.csv"
        work_df.to_csv(drills_path, index=False)
        return True

    except Exception as exc:
        print(f"Error updating drill library usage: {exc}")
        return False


def save_session_as_template(session: PracticeSession, data_path: Path | str) -> Tuple[bool, str]:
    """Persist a PracticeSession as a block template; duplicate-safe."""
    try:
        templates = load_block_templates(data_path)
    except Exception:
        templates = []

    # Build a deterministic template name
    parts = []
    if getattr(session, "session_name", ""):
        parts.append(str(session.session_name))
    if getattr(session, "team_name", ""):
        parts.append(str(session.team_name))
    if getattr(session, "session_date", ""):
        parts.append(str(session.session_date))
    try:
        dur = int(session.duration_minutes)
        if dur > 0:
            parts.append(f"{dur}min")
    except Exception:
        pass
    template_name = " - ".join(parts) if parts else "Session Template"

    if any(tpl.name == template_name for tpl in templates):
        return False, "duplicate"

    # Build blocks: group by block_type if present, else single block
    blocks: Dict[str, list] = {}
    for drill in session.drills or []:
        block = getattr(drill, "block_type", None) or "session"
        blocks.setdefault(block, []).append(drill.drill_id)

    new_tpl = BlockTemplate(
        name=template_name,
        description=f"Saved from history on {session.session_date}",
        blocks=blocks or {"session": []},
        block_durations={},
    )
    try:
        templates.append(new_tpl)
        save_block_templates(templates, data_path)
        return True, template_name
    except Exception as exc:
        return False, f"error: {exc}"
