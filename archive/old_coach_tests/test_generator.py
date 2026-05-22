import pandas as pd
import sys
from pathlib import Path

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


def _base_config():
    return PracticeConfig(
        duration_minutes=60,
        num_players=12,
        num_drills=5,
        selected_categories=[
            "Warmup",
            "Technical",
            "Tactical",
            "Small Sided Games",
            "Cool Down",
        ],
        session_date="2024-01-01",
        session_notes="",
    )


def test_warmup_and_cooldown_present():
    df = _sample_drills()
    config = _base_config()
    team_profile = {"team_id": "team1", "team_name": "Team One", "skill_level": "intermediate"}
    result = practice_generator.generate_practice_plan(config, team_profile, df, recent_usage={})
    assert result["success"]
    session = result["session"]
    blocks = {d.block_type for d in session.drills}
    assert "warmup" in blocks
    assert "cooldown" in blocks


def test_drills_sorted_by_block_order():
    df = _sample_drills()
    config = _base_config()
    team_profile = {"team_id": "team1", "team_name": "Team One", "skill_level": "intermediate"}
    session = practice_generator.generate_practice_plan(config, team_profile, df, recent_usage={})["session"]
    order_map = {b: i for i, b in enumerate(practice_generator.BLOCK_ORDER)}
    block_sequence = [order_map.get(d.block_type, 99) for d in session.drills]
    assert block_sequence == sorted(block_sequence)


def test_no_duplicate_drill_ids():
    df = _sample_drills()
    config = _base_config()
    team_profile = {"team_id": "team1", "team_name": "Team One", "skill_level": "intermediate"}
    session = practice_generator.generate_practice_plan(config, team_profile, df, recent_usage={})["session"]
    drill_ids = [d.drill_id for d in session.drills]
    assert len(drill_ids) == len(set(drill_ids))


def test_durations_sum_to_target():
    df = _sample_drills()
    config = _base_config()
    config.duration_minutes = 70
    team_profile = {"team_id": "team1", "team_name": "Team One", "skill_level": "intermediate"}
    session = practice_generator.generate_practice_plan(config, team_profile, df, recent_usage={})["session"]
    total = sum(d.allocated_time for d in session.drills)
    assert total == config.duration_minutes
