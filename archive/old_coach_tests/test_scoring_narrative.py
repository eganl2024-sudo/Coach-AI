import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

import practice_generator  # noqa: E402
from models import DrillScoreBreakdown  # noqa: E402


def test_build_scoring_narrative_basic():
    bd = DrillScoreBreakdown(
        drill_id="D1",
        total_score=50,
        focus_match=5,
        intensity_match=5,
        player_fit_score=5,
        category_match=5,
        block_alignment=10,
        recency_penalty=-5,
        rating_adjustment=2,
    )
    text = practice_generator.build_scoring_narrative(bd)
    assert "Selected because" in text
    assert "total 50" in text
