import json
import pandas as pd
import pytest

import practice_history
from models import PracticeSession, PracticeConfig, SessionDrill


def test_sanitize_text_fields_replaces_bad_chars_and_preserves_nan():
    df = pd.DataFrame(
        {
            "session_name": ["TestÂ", None],
            "categories": ["Warmupâ€”Technical", float("nan")],
        }
    )
    cleaned = practice_history.sanitize_text_fields(df.copy())
    assert cleaned.loc[0, "session_name"] == "Test"
    assert cleaned.loc[0, "categories"] == "Warmup-Technical"
    assert pd.isna(cleaned.loc[1, "session_name"])
    assert pd.isna(cleaned.loc[1, "categories"])


def test_load_practice_session_from_record_valid_and_invalid():
    payload = {
        "session_id": "abc",
        "team_id": "team1",
        "team_name": "Team",
        "session_date": "2025-01-01",
        "duration_minutes": 60,
        "num_players": 12,
        "num_drills": 1,
        "selected_categories": ["Warmup"],
        "drills": [
            {
                "drill_id": "d1",
                "drill_name": "Drill 1",
                "category": "Warmup",
                "intensity": "low",
                "players_min": 0,
                "players_max": 0,
                "field_type": "",
                "description": "",
                "coaching_points": "",
                "equipment": "",
                "setup_data": "",
                "allocated_time": 10,
                "target_intensity": "",
            }
        ],
        "config": {
            "duration_minutes": 60,
            "num_players": 12,
            "num_drills": 1,
            "selected_categories": ["Warmup"],
            "session_date": "2025-01-01",
            "session_notes": "",
        },
    }
    row = {"session_structure": json.dumps(payload)}
    session = practice_history.load_practice_session_from_record(row)
    assert isinstance(session, PracticeSession)
    assert session.session_date == "2025-01-01"

    bad_session = practice_history.load_practice_session_from_record(None)
    assert bad_session is None


def test_save_session_as_template_duplicate(tmp_path):
    cfg = PracticeConfig(
        duration_minutes=60,
        num_players=12,
        num_drills=1,
        selected_categories=["Warmup"],
        session_date="2025-01-01",
        session_notes="",
    )
    drill = SessionDrill.from_dict(
        {
            "drill_id": "d1",
            "drill_name": "Drill 1",
            "category": "Warmup",
            "intensity": "low",
            "players_min": 0,
            "players_max": 0,
            "field_type": "",
            "description": "",
            "coaching_points": "",
            "equipment": "",
            "setup_data": "",
            "allocated_time": 10,
            "target_intensity": "",
        }
    )
    session = PracticeSession(
        session_id="abc",
        team_id="team1",
        team_name="Team",
        session_date="2025-01-01",
        config=cfg,
        duration_minutes=60,
        num_players=12,
        num_drills=1,
        selected_categories=["Warmup"],
        drills=[drill],
    )
    ok, name = practice_history.save_session_as_template(session, tmp_path)
    assert ok is True
    assert name
    ok2, msg2 = practice_history.save_session_as_template(session, tmp_path)
    assert ok2 is False
    assert msg2 == "duplicate"
