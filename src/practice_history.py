from __future__ import annotations
def get_recent_use(drill_id: str, df: pd.DataFrame):
    """Return the most recent date the given drill_id was used in the practice history DataFrame, or None if never used."""
    if df is None or df.empty or "drills_used" not in df.columns or "session_date" not in df.columns:
        return None
    filtered = df[df["drills_used"].fillna("").apply(lambda x: drill_id in [d.strip() for d in str(x).split("|")])]
    if filtered.empty:
        return None
    return filtered["session_date"].max()
from datetime import timedelta
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

import json
from pathlib import Path
from typing import Optional, Tuple, Dict
from datetime import datetime, UTC

import pandas as pd

from models import PracticeSession, PracticeConfig, SessionDrill
from templates import BlockTemplate, load_block_templates, save_block_templates


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
    "session_notes",
    "total_time",
    "num_players",
    "drills_used",
    "categories",
    "is_favorite",
    "session_structure",
    "team_id",
    "team_name",
    "status",
    "session_id",
]


def _history_path(data_path: Path | str, team_id: str) -> Path:
    return Path(data_path) / f"practice_history_{team_id}.csv"


def get_history_mtime(data_path: Path | str, team_id: str) -> Optional[float]:
    path = _history_path(data_path, team_id)
    return path.stat().st_mtime if path.exists() else None


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
        return pd.DataFrame(columns=HISTORY_COLUMNS)
    try:
        df = pd.read_csv(path)
    except Exception as exc:
        print(f"Error loading practice history for team {team_id}: {exc}")
        return pd.DataFrame(columns=HISTORY_COLUMNS)

    if "session_date" in df.columns:
        df["session_date"] = pd.to_datetime(df["session_date"], errors="coerce")
        df = df.dropna(subset=["session_date"])
        df = df.sort_values("session_date", ascending=False)
        df["session_date"] = df["session_date"].dt.date

    if "is_favorite" in df.columns:
        df["is_favorite"] = df["is_favorite"].fillna(False).astype(bool)

    # Ensure status column exists (default to "completed" for backward compatibility)
    if "status" not in df.columns:
        df["status"] = "completed"

    # Ensure session_id column exists
    if "session_id" not in df.columns:
        import uuid
        df["session_id"] = [str(uuid.uuid4()) for _ in range(len(df))]

    df = sanitize_text_fields(df)
    return df


def save_practice_history(df: pd.DataFrame, data_path: Path | str, team_id: str) -> None:
    """Persist a practice history dataframe to CSV."""
    path = _history_path(data_path, team_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


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
            cfg_data = payload.get("config") or {}
            drills_data = payload.get("drills", [])
            config = PracticeConfig(
                duration_minutes=int(cfg_data.get("duration_minutes", payload.get("duration_minutes", 0) or 0)),
                num_players=int(cfg_data.get("num_players", payload.get("num_players", 0) or 0)),
                num_drills=int(cfg_data.get("num_drills", len(drills_data))),
                selected_categories=cfg_data.get("selected_categories", payload.get("selected_categories", [])) or [],
                session_date=str(cfg_data.get("session_date", payload.get("session_date", ""))),
                session_notes=cfg_data.get("session_notes", ""),
                focus_tags=cfg_data.get("focus_tags", []),
                favorites_only=bool(cfg_data.get("favorites_only", False)),
                use_team_profile=bool(cfg_data.get("use_team_profile", True)),
                template_blocks=cfg_data.get("template_blocks"),
                focus_boost_categories=cfg_data.get("focus_boost_categories", []),
            )
            drills = [SessionDrill.from_dict(d) for d in drills_data]
            return PracticeSession(
                session_id=payload.get("session_id", ""),
                team_id=payload.get("team_id", "") or str(_safe_get(row, "team_id", "")),
                team_name=payload.get("team_name", _safe_get(row, "team_name", "")),
                session_date=str(payload.get("session_date", cfg_data.get("session_date", ""))),
                config=config,
                duration_minutes=int(payload.get("duration_minutes", config.duration_minutes)),
                num_players=int(payload.get("num_players", config.num_players)),
                num_drills=int(payload.get("num_drills", len(drills))),
                selected_categories=payload.get("selected_categories", config.selected_categories),
                drills=drills,
                team_profile_summary=payload.get("team_profile_summary", {}),
                equipment_needed=payload.get("equipment_needed", []),
                category_summary=payload.get("category_summary", {}),
                intensity_summary=payload.get("intensity_summary", {}),
                manual_adjustments=payload.get("manual_adjustments", {"reordered": 0, "replaced": 0}),
                block_duration_summaries=payload.get("block_duration_summaries", []),
                template_notes=payload.get("template_notes", []),
                warnings=payload.get("warnings", []),
            )

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
) -> tuple[bool, str | None]:
    """
    Save a generated PracticeSession to the team's practice history.

    This is the main entry point used by the Practice Generator UI.
    It loads existing history, appends a new row, and writes back to disk.

    Args:
        team_id: The team identifier
        session_obj: The PracticeSession object to save
        data_path: Path to the data directory
        session_dict: Optional pre-built row dictionary; if None, built from session_obj

    Returns:
        Tuple of (success: bool, status: str | None) where status is "planned" or "completed"
    """
    try:
        from datetime import date as date_cls

        # Load existing history for this team
        history_df = load_practice_history(team_id, data_path)

        # Build the new row from session_obj and optional session_dict
        if session_dict is None:
            session_dict = {}

        config_obj = getattr(session_obj, "config", None)
        # Generate a unique session_id if not already present
        import uuid
        session_id = getattr(session_obj, "session_id", None) or str(uuid.uuid4())

        # Determine session status: planned if future date, completed if past/today
        session_date_str = str(getattr(session_obj, "session_date", ""))
        try:
            session_date = pd.to_datetime(session_date_str).date()
        except Exception:
            session_date = date_cls.today()

        today = date_cls.today()
        status = "planned" if session_date > today else "completed"

        new_row = {
            "session_date": session_date_str,
            "session_name": session_dict.get(
                "session_name",
                getattr(session_obj, "session_name", f"Practice {session_obj.session_date}"),
            ),
            "session_notes": session_dict.get(
                "session_notes",
                getattr(config_obj, "session_notes", "") if config_obj else "",
            ),
            "total_time": int(session_dict.get("total_time", session_obj.duration_minutes)),
            "num_players": int(session_dict.get("num_players", session_obj.num_players)),
            "drills_used": "|".join(
                str(d) for d in session_dict.get("drills_used", [d.drill_id for d in session_obj.drills])
            ),
            "categories": "|".join(
                str(c) for c in session_dict.get("categories", session_obj.selected_categories)
            ),
            "is_favorite": session_dict.get("is_favorite", False),
            "session_structure": json.dumps(_session_to_payload_dict(session_obj)),
            "team_id": team_id,
            "team_name": getattr(session_obj, "team_name", ""),
            "status": status,
            "session_id": session_id,
        }

        # Append to history - reorder columns to match HISTORY_COLUMNS
        new_df = pd.DataFrame([new_row])
        # Select columns in the correct order, adding any missing columns from history_df
        all_columns = list(history_df.columns) if not history_df.empty else HISTORY_COLUMNS
        for col in HISTORY_COLUMNS:
            if col not in new_df.columns:
                new_df[col] = None
        new_df = new_df[all_columns]
        history_df = pd.concat([history_df, new_df], ignore_index=True)

        # Save back to disk
        save_practice_history(history_df, data_path, team_id)
        return True, status

    except Exception as exc:
        print(f"Error saving practice session: {exc}")
        return False, None


def _session_to_payload_dict(session: PracticeSession) -> Dict:
    """Convert a PracticeSession to a serializable dictionary for storage."""
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
        "block_duration_summaries": getattr(session, "block_duration_summaries", []),
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

        # Reconstruct drills with all required parameters
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

        # Reconstruct config
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

        # Reconstruct the session
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

        # Ensure usage column exists
        if "usage_count" not in work_df.columns:
            work_df["usage_count"] = 0

        # Increment usage for drills that were used
        for drill_id in drill_ids:
            if "drill_id" in work_df.columns:
                mask = work_df["drill_id"] == drill_id
                if mask.any():
                    for idx in work_df[mask].index:
                        try:
                            val = work_df.at[idx, "usage_count"]
                            current = int(float(val)) if val not in [None, "", "NaN"] else 0
                        except Exception:
                            current = 0
                        work_df.at[idx, "usage_count"] = current + 1

        # Save the updated drills dataframe
        drills_path = Path(data_path) / "drills.csv"
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
