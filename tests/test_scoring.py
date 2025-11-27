import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

import practice_generator  # noqa: E402
from models import PracticeConfig  # noqa: E402


def _config():
    return PracticeConfig(
        duration_minutes=60,
        num_players=12,
        num_drills=5,
        selected_categories=["Warmup", "Technical", "Cool Down"],
        session_date="2024-01-01",
        session_notes="",
    )


def test_score_drill_candidate_focus_and_recency():
    cfg = _config()
    team_profile = {"team_id": "t1", "team_name": "Team", "skill_level": "intermediate"}
    drill = {
        "drill_id": "TECH_1",
        "drill_name": "Tech",
        "category": "Technical",
        "intensity": "medium",
        "players_min": 8,
        "players_max": 16,
        "tags": "passing|press",
        "coach_rating": 4,
    }
    breakdown = practice_generator.score_drill_candidate(
        drill,
        block_type="technical",
        team_profile=team_profile,
        practice_config=cfg,
        history_df=None,
        target_intensity="medium",
        focus_tags=["press"],
        recent_usage={"TECH_1": 0},
    )
    # Focus match should be positive
    assert breakdown.focus_match > 0
    # Recency penalty should be applied via recent_usage
    assert breakdown.recency_penalty <= 0


def test_score_drill_candidate_intensity_penalty():
    cfg = _config()
    team_profile = {"team_id": "t1", "team_name": "Team", "skill_level": "intermediate"}
    drill_a = {
        "drill_id": "TECH_A",
        "drill_name": "Tech A",
        "category": "Technical",
        "intensity": "medium",
        "players_min": 8,
        "players_max": 16,
    }
    drill_b = dict(drill_a, drill_id="TECH_B", intensity="high")
    score_a = practice_generator.score_drill_candidate(
        drill_a, "technical", team_profile, cfg, target_intensity="medium"
    )
    score_b = practice_generator.score_drill_candidate(
        drill_b, "technical", team_profile, cfg, target_intensity="medium"
    )
    assert score_a.total_score > score_b.total_score
