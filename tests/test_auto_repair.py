import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

import practice_generator  # noqa: E402
from models import PracticeConfig, PracticeSession, SessionDrill  # noqa: E402


def test_auto_repair_inserts_missing_blocks():
    drills_df = pd.DataFrame([
        {"drill_id": "WARM_1", "drill_name": "Warm", "category": "Warmup", "players_min": 1, "players_max": 20, "intensity": "low", "coach_rating": 3},
        {"drill_id": "COOL_1", "drill_name": "Cool", "category": "Cool Down", "players_min": 1, "players_max": 20, "intensity": "low", "coach_rating": 3},
    ])
    cfg = PracticeConfig(
        duration_minutes=20,
        num_players=10,
        num_drills=1,
        selected_categories=["Warmup"],
        session_date="2024-01-01",
        session_notes="",
    )
    session = PracticeSession.create(
        team_name="Test",
        team_id="T1",
        session_date="2024-01-01",
        config=cfg,
        drills=[],
    )
    repaired, changes = practice_generator.auto_repair_session(session, drills_df)
    ids = [d.drill_id for d in repaired.drills]
    assert "WARM_1" in ids
    assert "COOL_1" in ids
