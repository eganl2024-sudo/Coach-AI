import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from models import PracticeConfig, PracticeSession, SessionDrill  # noqa: E402


def _session_with_drills(drills):
    cfg = PracticeConfig(
        duration_minutes=sum(d.allocated_time for d in drills),
        num_players=10,
        num_drills=len(drills),
        selected_categories=["Warmup", "Technical", "Cool Down"],
        session_date="2024-01-01",
        session_notes="",
    )
    return PracticeSession.create(
        team_name="Test",
        team_id="t1",
        session_date="2024-01-01",
        config=cfg,
        drills=drills,
        team_profile_summary={},
    )


def test_validate_session_missing_warmup():
    drills = [
        SessionDrill.from_dict({"drill_id": "TECH1", "drill_name": "Tech", "category": "Technical", "allocated_time": 20, "intensity": "medium", "players_min": 1, "players_max": 20}),
        SessionDrill.from_dict({"drill_id": "COOL1", "drill_name": "Cool", "category": "Cool Down", "allocated_time": 10, "intensity": "low", "players_min": 1, "players_max": 20}),
    ]
    session = _session_with_drills(drills)
    errors = session.validate()
    assert any("Warmup block must be first." in err for err in errors)


def test_validate_session_missing_cooldown():
    drills = [
        SessionDrill.from_dict({"drill_id": "WARM1", "drill_name": "Warm", "category": "Warmup", "allocated_time": 10, "intensity": "low", "players_min": 1, "players_max": 20}),
        SessionDrill.from_dict({"drill_id": "TECH1", "drill_name": "Tech", "category": "Technical", "allocated_time": 20, "intensity": "medium", "players_min": 1, "players_max": 20}),
    ]
    session = _session_with_drills(drills)
    errors = session.validate()
    assert any("Cool Down block must be last." in err for err in errors)


def test_validate_session_negative_duration():
    drills = [
        SessionDrill.from_dict({"drill_id": "WARM1", "drill_name": "Warm", "category": "Warmup", "allocated_time": -5, "intensity": "low", "players_min": 1, "players_max": 20}),
        SessionDrill.from_dict({"drill_id": "COOL1", "drill_name": "Cool", "category": "Cool Down", "allocated_time": 10, "intensity": "low", "players_min": 1, "players_max": 20}),
    ]
    session = _session_with_drills(drills)
    errors = session.validate()
    assert any("non-positive duration" in err for err in errors)


def test_validate_session_total_duration_mismatch():
    drills = [
        SessionDrill.from_dict({"drill_id": "WARM1", "drill_name": "Warm", "category": "Warmup", "allocated_time": 5, "intensity": "low", "players_min": 1, "players_max": 20}),
        SessionDrill.from_dict({"drill_id": "COOL1", "drill_name": "Cool", "category": "Cool Down", "allocated_time": 5, "intensity": "low", "players_min": 1, "players_max": 20}),
    ]
    session = _session_with_drills(drills)
    session.duration_minutes = 30
    errors = session.validate()
    assert any("Total allocated time" in err for err in errors)
