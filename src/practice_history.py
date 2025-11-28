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
    """Return a dictionary mapping drill_id to usage count from the practice history DataFrame."""
    if df is None or df.empty or "drills_used" not in df.columns:
        return {}
    usage = {}
    for drills in df["drills_used"].dropna():
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
