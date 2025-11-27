"""Lightweight sanity checks for practice history aggregations."""
import pandas as pd
from datetime import datetime

from practice_history import compute_recency_table, allocate_category_minutes


def run_checks():
    history = pd.DataFrame([
        {
            "session_date": "2025-01-05",
            "total_time": 90,
            "categories": "Warmup|Technical|Technical",
            "drills_used": "A|B|C",
            "season_segment": "Preseason"
        },
        {
            "session_date": "2025-02-10",
            "total_time": 60,
            "categories": "Warmup|Tactical",
            "drills_used": "B|D",
            "season_segment": "Early Season"
        },
    ])

    minutes = allocate_category_minutes(history)
    assert abs(minutes.groupby('category')['minutes'].sum().sum() - 150) < 0.01

    recency = compute_recency_table(history)
    assert set(recency['drill_id']) == {"A", "B", "C", "D"}

    print("Aggregation checks passed.")


if __name__ == "__main__":
    run_checks()
