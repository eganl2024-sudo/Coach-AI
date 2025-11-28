"""Simple JSON-based team profile storage."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

PROFILE_FILENAME = "team_profiles.json"


def _get_profile_path(data_path: Path) -> Path:
    return Path(data_path) / PROFILE_FILENAME


def load_team_profile(data_path: Path, team_id: str) -> Dict[str, Any]:
    path = _get_profile_path(data_path)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data.get(team_id, {})


def save_team_profile(data_path: Path, team_id: str, profile: Dict[str, Any]) -> None:
    path = _get_profile_path(data_path)
    if path.exists():
        try:
            all_profiles = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            all_profiles = {}
    else:
        all_profiles = {}
    all_profiles[team_id] = profile
    path.write_text(json.dumps(all_profiles, indent=2, ensure_ascii=True), encoding="utf-8")
