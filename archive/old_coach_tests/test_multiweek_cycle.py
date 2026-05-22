import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

import practice_generator  # noqa: E402
from models import PracticeConfig  # noqa: E402


def _sample_drills():
    rows = [
        {"drill_id": "WARM_001", "drill_name": "Warmup A", "category": "Warmup", "players_min": 6, "players_max": 18, "duration_minutes": 10, "field_type": "Grid", "description": "", "coaching_points": "", "difficulty": "intermediate", "intensity": "low", "coach_rating": 3},
        {"drill_id": "TECH_001", "drill_name": "Technical A", "category": "Technical", "players_min": 6, "players_max": 18, "duration_minutes": 12, "field_type": "Grid", "description": "", "coaching_points": "", "difficulty": "intermediate", "intensity": "medium", "coach_rating": 4},
        {"drill_id": "TACT_001", "drill_name": "Tactical A", "category": "Tactical", "players_min": 6, "players_max": 18, "duration_minutes": 15, "field_type": "Grid", "description": "", "coaching_points": "", "difficulty": "intermediate", "intensity": "medium", "coach_rating": 4},
        {"drill_id": "SSG_001", "drill_name": "SSG A", "category": "Small Sided Games", "players_min": 6, "players_max": 18, "duration_minutes": 15, "field_type": "Grid", "description": "", "coaching_points": "", "difficulty": "intermediate", "intensity": "high", "coach_rating": 5},
        {"drill_id": "COND_001", "drill_name": "Conditioning A", "category": "Conditioning", "players_min": 6, "players_max": 18, "duration_minutes": 8, "field_type": "Grid", "description": "", "coaching_points": "", "difficulty": "intermediate", "intensity": "high", "coach_rating": 3},
        {"drill_id": "COOL_001", "drill_name": "Cool Down A", "category": "Cool Down", "players_min": 6, "players_max": 18, "duration_minutes": 8, "field_type": "Grid", "description": "", "coaching_points": "", "difficulty": "intermediate", "intensity": "low", "coach_rating": 3},
    ]
    return pd.DataFrame(rows)


def test_multiweek_cycle_sessions_count():
    df = _sample_drills()
    config = PracticeConfig(
        duration_minutes=60,
        num_players=12,
        num_drills=5,
        selected_categories=["Warmup", "Technical", "Tactical", "Small Sided Games", "Cool Down"],
        session_date="2024-01-01",
        session_notes="",
    )
    team_profile = {"team_id": "team1", "team_name": "Team One", "skill_level": "intermediate"}
    result = practice_generator.generate_multiweek_cycle(
        config,
        team_profile,
        df,
        recent_usage={},
        weeks=2,
    )
    assert result["success"]
    assert result["total_sessions"] == 4
    assert len(result["weeks"]) == 2
    for week_entry in result["weeks"]:
        assert len(week_entry["sessions"]) == 2
        for sess in week_entry["sessions"]:
            assert not sess.validate()  # expect no errors
