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


def test_default_values_autofill_simulation():
    from utils import ensure_columns
    from data_loader import DRILL_DEFAULTS
    import pandas as pd

    # Create df lacking many new columns
    df = pd.DataFrame([{
        "drill_id": "TEST-001",
        "drill_name": "Autofill Test",
        "category": "Technical",
    }])
    repairs, repaired_df = ensure_columns(df, DRILL_DEFAULTS)
    assert "drill_type" in repaired_df.columns
    assert repaired_df.loc[0, "drill_type"] == "Isolation"
    assert repaired_df.loc[0, "solo_possible"] == True
    assert repaired_df.loc[0, "common_mistakes"] == ""


def test_validator_parsing_and_types():
    from validation import validate_drill

    data = {
        "drill_id": "TEST-002",
        "drill_name": "Parser Test",
        "category": "Tactical",
        "solo_possible": "yes",
        "beta_ready": "1",
        "series_order": "4.2",
    }
    drill = validate_drill(data)
    assert drill.solo_possible == True
    assert drill.beta_ready == True
    assert drill.series_order == 4


def test_fallback_values_handling():
    from validation import validate_drill

    data = {
        "drill_id": "TEST-F1",
        "drill_name": "Fallback Test",
        "category": "Physical",
        "space_required": "",
        "min_equipment": None,
    }
    drill = validate_drill(data)
    assert drill.space_required == "Small area"
    assert drill.min_equipment == "Ball only"


def test_presenters_empty_loading_behaviour(tmp_path):
    from data_loader import load_presenters, save_presenters, PRESENTER_COLUMNS
    import pandas as pd

    # Test missing file
    df = load_presenters(tmp_path)
    assert isinstance(df, pd.DataFrame)
    for col in PRESENTER_COLUMNS:
        assert col in df.columns

    # Test loading with some custom active values
    test_df = pd.DataFrame([{
        "presenter_id": "P1",
        "full_name": "Test Presenter",
        "active": "no",
    }, {
        "presenter_id": "P2",
        "full_name": "Test Presenter 2",
        "active": "1",
    }])
    save_presenters(test_df, tmp_path)
    loaded_df = load_presenters(tmp_path)
    assert loaded_df.loc[loaded_df["presenter_id"] == "P1", "active"].values[0] == False
    assert loaded_df.loc[loaded_df["presenter_id"] == "P2", "active"].values[0] == True


def test_ensure_columns_migration_safety():
    from utils import ensure_columns
    from data_loader import DRILL_DEFAULTS
    import pandas as pd

    # Pre-existing df with old fields and specific values
    df = pd.DataFrame([{
        "drill_id": "M1",
        "drill_name": "Migration Test",
        "solo_possible": False,
        "difficulty": "advanced",
    }])
    repairs, repaired_df = ensure_columns(df, DRILL_DEFAULTS)
    
    # Assert missing columns are filled
    assert "drill_type" in repaired_df.columns
    assert repaired_df.loc[0, "drill_type"] == "Isolation"
    
    # Assert pre-existing columns and values are preserved
    assert repaired_df.loc[0, "solo_possible"] == False
    assert repaired_df.loc[0, "difficulty"] == "advanced"


def test_common_mistakes_is_first_class_field():
    from validation import validate_drill
    data = {
        "drill_id": "TEST-003",
        "drill_name": "Test Drill",
        "category": "Technical",
        "common_mistakes": "Foot behind the ball|Hips closed on reception",
    }
    drill = validate_drill(data)
    assert drill.common_mistakes == "Foot behind the ball|Hips closed on reception"
    record = drill.to_record()
    assert "common_mistakes" in record

