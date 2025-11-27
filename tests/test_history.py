import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

import practice_history  # noqa: E402


def test_get_recent_use_and_season_segment_fallback(tmp_path):
    history_file = tmp_path / "practice_history_team1.csv"
    df = pd.DataFrame([
        {"session_date": "2024-01-01", "drills_used": "D1|D2", "categories": "Warmup|Technical", "total_time": 60, "num_players": 12},
        {"session_date": "2024-01-05", "drills_used": "D3", "categories": "Cool Down", "total_time": 20, "num_players": 12},
    ])
    df.to_csv(history_file, index=False)
    loaded = practice_history._read_history("team1", tmp_path)
    assert "season_segment" in loaded.columns
    last_used = practice_history.get_recent_use("D3", loaded)
    assert pd.to_datetime(last_used).date().isoformat() == "2024-01-05"
