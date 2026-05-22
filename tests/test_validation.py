import sys
from pathlib import Path
import datetime
import pytest

# Ensure src is on path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from validation import (
    validate_drill,
    validate_team_profile,
    validate_practice_session,
)


def test_validate_drill_valid():
    data = {
        "drill_id": "D1",
        "drill_name": "Passing Warmup",
        "category": "Warmup",
        "players_min": "6",
        "players_max": 12,
        "duration_minutes": "10",
        "intensity": "low",
        "tags": "Passing|Warmup",
    }
    drill = validate_drill(data)
    assert drill.drill_id == "D1"
    assert drill.min_players == 6
    assert drill.max_players == 12
    assert drill.duration_minutes == 10
    assert drill.tags == ["Passing", "Warmup"]


def test_validate_drill_missing_name():
    with pytest.raises(ValueError):
        validate_drill({"drill_id": "X1", "category": "Warmup"})


def test_validate_team_profile_valid_and_defaults():
    profile = validate_team_profile(
        {"team_id": "T1", "team_name": "U12 Blue", "age_group": "U12", "typical_roster_size": "14"}
    )
    assert profile.schema_version == 1
    assert profile.team_id == "T1"
    assert profile.age_group == "U12"
    assert profile.typical_roster_size == 14


def test_validate_team_profile_missing_age_group():
    with pytest.raises(ValueError):
        validate_team_profile({"team_id": "T2", "team_name": "No Age"})


def test_validate_practice_session_minimal():
    session_dict = {
        "team_id": "T1",
        "team_name": "U12 Blue",
        "session_date": "2024-05-01",
        "duration_minutes": 60,
        "num_players": 12,
        "drills": [
            {
                "drill_id": "D1",
                "drill_name": "Warmup",
                "category": "Warmup",
                "intensity": "low",
                "players_min": 6,
                "players_max": 20,
                "allocated_time": 10,
            }
        ],
    }
    session = validate_practice_session(session_dict)
    assert session.schema_version == 1
    assert session.session_id
    assert session.duration_minutes == 60
    assert session.num_players == 12
    assert len(session.drills) == 1


def test_validate_practice_session_bad_block():
    bad_session = {
        "team_id": "T1",
        "team_name": "U12",
        "session_date": "2024-05-01",
        "duration_minutes": 60,
        "num_players": 10,
        "blocks": [{"block_type": "warmup", "duration_minutes": "abc", "drill_id": "D1", "order_index": 0}],
    }
    with pytest.raises(ValueError):
        validate_practice_session(bad_session)
