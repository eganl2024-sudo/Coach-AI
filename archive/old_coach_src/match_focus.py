"""
Map match issues to practice focus suggestions.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import List, Dict

from team_profile import load_team_profile

ISSUE_TO_FOCUS: Dict[str, Dict[str, List[str]]] = {
    "Conceded on crosses": {
        "focus_tags": ["Defending crosses", "Box defending"],
        "categories": ["Defending", "Wide areas", "Heading"],
    },
    "Struggled building from the back": {
        "focus_tags": ["Build-up play", "Playing out"],
        "categories": ["Technical", "Tactical"],
    },
    "Created few chances": {
        "focus_tags": ["Chance creation", "Final third"],
        "categories": ["Finishing", "Attacking"],
    },
    "Pressing disorganized": {
        "focus_tags": ["Pressing", "Defensive shape"],
        "categories": ["Tactical", "Defending"],
    },
    "Too many turnovers in build-up": {
        "focus_tags": ["Decision making", "Playing out"],
        "categories": ["Technical", "Tactical"],
    },
}


def suggest_focus_from_last_match(team_id: str, practice_date: dt.date, data_path: Path | str) -> List[Dict]:
    """
    Load the last match before practice_date for this team and emit focus/tag suggestions.
    """
    profile = load_team_profile(Path(data_path), team_id)
    issues_by_date = profile.get("match_issues_by_date", {}) if isinstance(profile, dict) else {}
    if not issues_by_date:
        return []
    try:
        parsed = [
            (dt.datetime.fromisoformat(date_str).date(), issues)
            for date_str, issues in issues_by_date.items()
        ]
    except Exception:
        parsed = []
    parsed = [item for item in parsed if item[0] <= practice_date]
    if not parsed:
        return []
    parsed.sort(key=lambda tup: tup[0], reverse=True)
    latest_date, issues = parsed[0]
    suggestions = []
    for issue in issues or []:
        mapping = ISSUE_TO_FOCUS.get(issue)
        if mapping:
            suggestions.append(
                {
                    "label": issue,
                    "focus_tags": mapping.get("focus_tags", []),
                    "categories": mapping.get("categories", []),
                    "match_date": latest_date,
                }
            )
    return suggestions
