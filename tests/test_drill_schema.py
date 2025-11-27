import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from drills import validate_drill_schema  # noqa: E402


def test_validate_drill_schema_valid():
    payload = {
        "drill_id": "WARM_001",
        "drill_name": "Warmup",
        "category": "Warmup",
        "duration_minutes": 10,
        "positions": ["GK", "DEF"],
        "age_groups": ["U12"],
        "focus_attributes": [],
    }
    assert validate_drill_schema(payload) is True


def test_validate_drill_schema_missing_required():
    payload = {
        "drill_id": "",
        "drill_name": "",
        "category": "",
        "duration_minutes": "abc",
    }
    with pytest.raises(ValueError):
        validate_drill_schema(payload)
