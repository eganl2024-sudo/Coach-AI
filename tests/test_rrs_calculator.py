import sys
from pathlib import Path
import pytest
from datetime import date, timedelta

# Ensure src is on path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from rrs_calculator import (
    calculate_rrs,
    get_benchmark_for_score,
)

def test_locked_state_0_completions():
    athlete_profile = {"name": "Test Player", "level": "Recreational", "sessions_per_week": 3}
    completion_log = {"completions": []}
    drills_df = None
    plan = None
    
    rrs = calculate_rrs(athlete_profile, completion_log, drills_df, plan)
    
    assert rrs["unlocked"] is False
    assert rrs["sessions_until_unlock"] == 5
    assert rrs["overall"] == 0
    assert rrs["pillars"]["consistency"]["score"] == 0
    assert rrs["pillars"]["volume"]["score"] == 0
    assert rrs["pillars"]["coverage"]["score"] == 0
    assert rrs["pillars"]["progression"]["score"] == 0
    assert len(rrs["next_actions"]) > 0
    assert "Complete at least 5 sessions" in rrs["next_actions"][0]

def test_unlock_exactly_5_sessions():
    athlete_profile = {
        "name": "Test Player",
        "level": "Recreational",
        "sessions_per_week": 3,
        "created_date": (date.today() - timedelta(weeks=4)).isoformat()
    }
    # 5 completions on different days
    completions = []
    for i in range(5):
        day_date = date.today() - timedelta(days=i)
        completions.append({
            "date": day_date.isoformat(),
            "week": 1,
            "day": i + 1
        })
    completion_log = {"completions": completions}
    drills_df = None
    plan = None
    
    rrs = calculate_rrs(athlete_profile, completion_log, drills_df, plan)
    
    assert rrs["unlocked"] is True
    assert rrs["sessions_until_unlock"] == 0
    assert rrs["overall"] > 0

def test_overall_score_weighted_sum():
    # Test that overall score matches the weighted combination of pillars:
    # 0.3 * consistency + 0.2 * volume + 0.25 * coverage + 0.25 * progression
    athlete_profile = {
        "name": "Test Player",
        "level": "Recreational",
        "sessions_per_week": 3,
        "created_date": (date.today() - timedelta(weeks=4)).isoformat(),
        "focus_areas": ["Dribbling"]
    }
    completions = []
    # 6 completions in past week to ensure unlock
    for i in range(6):
        day_date = date.today() - timedelta(days=i)
        completions.append({
            "date": day_date.isoformat(),
            "week": 1,
            "day": i + 1
        })
    completion_log = {"completions": completions}
    
    # We will pass a simple drills_df and plan to verify scores
    plan = {
        "weeks": [
            {
                "week_number": 1,
                "sessions": [
                    {
                        "day_number": i + 1,
                        "drills": [{"drill_name": "Dribble Drill"}]
                    }
                    for i in range(6)
                ]
            }
        ]
    }
    drills_df = [
        {
            "drill_name": "Dribble Drill",
            "skill_category": "Dribbling",
            "tags": "Dribbling",
            "difficulty": "intermediate"
        }
    ]
    
    rrs = calculate_rrs(athlete_profile, completion_log, drills_df, plan)
    
    p = rrs["pillars"]
    c = p["consistency"]["score"]
    v = p["volume"]["score"]
    cov = p["coverage"]["score"]
    prog = p["progression"]["score"]
    
    expected_overall = round(c * 0.30 + v * 0.20 + cov * 0.25 + prog * 0.25)
    assert rrs["overall"] == expected_overall

def test_benchmark_label_ranges():
    # BENCHMARKS ranges check
    # 0-24: Getting Started
    # 25-44: Recreational Player
    # 45-59: Club Level
    # 60-74: Varsity Starter
    # 75-87: College Prospect
    # 88-100: D1 Ready
    
    assert get_benchmark_for_score(10)[0] == "Getting Started"
    assert get_benchmark_for_score(30)[0] == "Recreational Player"
    assert get_benchmark_for_score(50)[0] == "Club Level"
    assert get_benchmark_for_score(70)[0] == "Varsity Starter"
    assert get_benchmark_for_score(80)[0] == "College Prospect"
    assert get_benchmark_for_score(95)[0] == "D1 Ready"
    
    # Check boundaries
    assert get_benchmark_for_score(0)[0] == "Getting Started"
    assert get_benchmark_for_score(24)[0] == "Getting Started"
    assert get_benchmark_for_score(25)[0] == "Recreational Player"
    assert get_benchmark_for_score(44)[0] == "Recreational Player"
    assert get_benchmark_for_score(45)[0] == "Club Level"
    assert get_benchmark_for_score(59)[0] == "Club Level"
    assert get_benchmark_for_score(60)[0] == "Varsity Starter"
    assert get_benchmark_for_score(74)[0] == "Varsity Starter"
    assert get_benchmark_for_score(75)[0] == "College Prospect"
    assert get_benchmark_for_score(87)[0] == "College Prospect"
    assert get_benchmark_for_score(88)[0] == "D1 Ready"
    assert get_benchmark_for_score(100)[0] == "D1 Ready"

def test_next_actions_post_unlock():
    athlete_profile = {
        "name": "Test Player",
        "level": "Recreational",
        "sessions_per_week": 3,
        "created_date": (date.today() - timedelta(weeks=4)).isoformat(),
        "focus_areas": ["Dribbling"]
    }
    completions = []
    # 5 completions to unlock
    for i in range(5):
        day_date = date.today() - timedelta(days=i)
        completions.append({
            "date": day_date.isoformat(),
            "week": 1,
            "day": i + 1
        })
    completion_log = {"completions": completions}
    drills_df = None
    plan = None
    
    rrs = calculate_rrs(athlete_profile, completion_log, drills_df, plan)
    
    assert rrs["unlocked"] is True
    assert len(rrs["next_actions"]) >= 2
    # Ensure they are descriptive strings and not locked placeholder
    assert "Complete at least 5 sessions" not in rrs["next_actions"][0]

def test_resiliency_none_and_empty():
    # Pass empty or None inputs and make sure it does not crash
    rrs = calculate_rrs({}, {}, None, {})
    assert rrs["unlocked"] is False
    assert rrs["overall"] == 0
    assert rrs["sessions_until_unlock"] == 5
    assert rrs["pillars"]["consistency"]["score"] == 0
