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

def test_rrs_resilient_streak():
    from rrs_calculator import _calculate_streak
    
    today = date.today()
    
    # Strictly consecutive completions
    completions_consecutive = [
        {"date": (today - timedelta(days=2)).isoformat()},
        {"date": (today - timedelta(days=1)).isoformat()},
        {"date": today.isoformat()},
    ]
    assert _calculate_streak(completions_consecutive) == 3
    
    # 3-day gap completions (e.g. Mon, Wed, Fri)
    completions_gaps = [
        {"date": (today - timedelta(days=6)).isoformat()},
        {"date": (today - timedelta(days=3)).isoformat()},
        {"date": today.isoformat()},
    ]
    assert _calculate_streak(completions_gaps) == 3
    
    # Over 3 days gap completion (e.g. gap of 4 days)
    completions_large_gap = [
        {"date": (today - timedelta(days=5)).isoformat()},
        {"date": today.isoformat()},
    ]
    assert _calculate_streak(completions_large_gap) == 1
    
    # Inactive streak (last session was 8 days ago)
    completions_inactive = [
        {"date": (today - timedelta(days=10)).isoformat()},
        {"date": (today - timedelta(days=8)).isoformat()},
    ]
    assert _calculate_streak(completions_inactive) == 0

    # Cooling streak (last session was 5 days ago, so halved)
    completions_cooling = [
        {"date": (today - timedelta(days=7)).isoformat()},
        {"date": (today - timedelta(days=5)).isoformat()},
    ]
    assert _calculate_streak(completions_cooling) == 1

def test_rrs_multi_tier_progression():
    from rrs_calculator import _calculate_progression
    
    completions = [
        {"date": "2026-05-28", "week": 1, "day": 1},
        {"date": "2026-05-28", "week": 1, "day": 2},
        {"date": "2026-05-28", "week": 1, "day": 3},
    ]
    plan = {
        "weeks": [
            {
                "week_number": 1,
                "sessions": [
                    {"day_number": 1, "drills": [{"drill_name": "Drill A"}]},
                    {"day_number": 2, "drills": [{"drill_name": "Drill B"}]},
                    {"day_number": 3, "drills": [{"drill_name": "Drill C"}]},
                ]
            }
        ]
    }
    drills_df = [
        {"drill_name": "Drill A", "difficulty": "beginner"},
        {"drill_name": "Drill B", "difficulty": "advanced"},
        {"drill_name": "Drill C", "difficulty": "elite"},
    ]
    
    # Recreational player:
    # beginner -> 1.0, intermediate -> 1.0, advanced -> 1.2, elite -> 1.4
    recreational_prog = _calculate_progression(completions, "Recreational", plan, drills_df)
    assert recreational_prog == 100.0
    
    # Academy player:
    # beginner -> 0.2, intermediate -> 0.6, advanced -> 1.0, elite -> 1.0
    # Expected points: 0.2 + 1.0 + 1.0 = 2.2. 2.2 / 3 = 0.733 -> 73%
    academy_prog = _calculate_progression(completions, "Academy/Select", plan, drills_df)
    assert academy_prog == 73.0

def test_rrs_coverage_secondary_position():
    from rrs_calculator import _calculate_coverage
    
    completions = [
        {"date": date.today().isoformat(), "week": 1, "day": 1}
    ]
    plan = {
        "weeks": [
            {
                "week_number": 1,
                "sessions": [
                    {"day_number": 1, "drills": [{"drill_name": "Drill A"}]}
                ]
            }
        ]
    }
    drills_df = [
        {
            "drill_name": "Drill A",
            "skill_category": "Dribbling",
            "tags": "dribbling|weak foot",
            "position_relevance": ""
        }
    ]
    
    # Expected under fuzzy matching: Both focus areas Dribbling and Weak Foot Development (matched via "weak" and "foot" in tags) are trained.
    # combined: 0.7 * 1.0 + 0.3 * 1.0 = 1.0 -> 100%
    score = _calculate_coverage(completions, ["Dribbling", "Weak Foot Development"], drills_df, plan, "Striker", "Winger")
    assert score == 100.0


def test_calculate_skill_radar_has_data_false_if_fewer_than_2_sessions():
    from rrs_calculator import calculate_skill_radar
    profile = {"name": "Alex", "position": "Striker", "focus_areas": ["Finishing"]}
    completions = [{"date": "2026-05-28", "week": 1, "day": 1}]
    completion_log = {"completions": completions}
    plan = {}
    drills_df = []
    
    res = calculate_skill_radar(profile, completion_log, plan, drills_df)
    assert res["has_data"] is False
    assert len(res["axes"]) == 0
    assert len(res["scores"]) == 0

def test_calculate_skill_radar_axis_construction_and_scores():
    from rrs_calculator import calculate_skill_radar
    profile = {
        "name": "Alex",
        "position": "Striker",
        "focus_areas": ["Finishing", "First Touch"]
    }
    
    # 2 completions in last 28 days
    completions = [
        {"date": date.today().isoformat(), "week": 1, "day": 1},
        {"date": (date.today() - timedelta(days=2)).isoformat(), "week": 1, "day": 2}
    ]
    completion_log = {"completions": completions}
    
    plan = {
        "weeks": [
            {
                "week_number": 1,
                "sessions": [
                    {"day_number": 1, "drills": [{"drill_name": "Shooting Drill", "drill_id": "DRILL_01"}]},
                    {"day_number": 2, "drills": [{"drill_name": "Passing Drill", "drill_id": "DRILL_02"}]}
                ]
            }
        ]
    }
    
    drills_df = [
        {
            "drill_id": "DRILL_01",
            "drill_name": "Shooting Drill",
            "skill_category": "Finishing",
            "series_name": "Finishing Program",
            "tags": "finishing|shooting"
        },
        {
            "drill_id": "DRILL_02",
            "drill_name": "Passing Drill",
            "skill_category": "Passing",
            "series_name": "Midfield Passing",
            "tags": "passing"
        }
    ]
    
    res = calculate_skill_radar(profile, completion_log, plan, drills_df)
    assert res["has_data"] is True
    # Finishing is a focus area. We also have Passing from completions (skill_category = Passing).
    # Since len(axes) is 3 (Finishing, First Touch, Passing), which is < 4, it should add position defaults:
    # Striker defaults are Finishing, Movement, First Touch. Finishing and First Touch are already there.
    # So it should add "Movement". Total axes = 4: Finishing, First Touch, Passing, Movement.
    assert "Finishing" in res["axes"]
    assert "First Touch" in res["axes"]
    assert "Passing" in res["axes"]
    assert "Movement" in res["axes"]
    assert len(res["axes"]) == 4
    
    # Scores check:
    # Finishing: 1 completed drill. 1 * 15 = 15. Focus bonus = +10. Total = 25.
    # First Touch: 0 completed drills. Default = 20. Focus bonus = +10. Total = 30.
    # Passing: 1 completed drill. 1 * 15 = 15. No focus bonus. Total = 15.
    # For Movement: 0 completed drills -> 20.
    finishing_idx = res["axes"].index("Finishing")
    first_touch_idx = res["axes"].index("First Touch")
    passing_idx = res["axes"].index("Passing")
    movement_idx = res["axes"].index("Movement")
    
    assert res["scores"][finishing_idx] == 25
    assert res["scores"][first_touch_idx] == 30
    assert res["scores"][passing_idx] == 15
    assert res["scores"][movement_idx] == 20

def test_calculate_coverage_fuzzy_matching_and_floor():
    from rrs_calculator import _calculate_coverage
    # Dribbling matches Drill A (tags "dribbling").
    # "1v1 Attacking" (focus area) has words ["1v1", "attacking"]. "attacking" has length 9 > 3.
    # "attacking" is in tags for Drill B, so it should match!
    # No completions for the other focus areas.
    completions = [
        {"date": date.today().isoformat(), "week": 1, "day": 1},
        {"date": date.today().isoformat(), "week": 1, "day": 2}
    ]
    plan = {
        "weeks": [
            {
                "week_number": 1,
                "sessions": [
                    {"day_number": 1, "drills": [{"drill_name": "Drill A"}]},
                    {"day_number": 2, "drills": [{"drill_name": "Drill B"}]}
                ]
            }
        ]
    }
    drills_df = [
        {
            "drill_name": "Drill A",
            "skill_category": "Technical",
            "tags": "dribbling",
            "position_relevance": ""
        },
        {
            "drill_name": "Drill B",
            "skill_category": "Technical",
            "tags": "attacking",
            "position_relevance": ""
        }
    ]
    
    # 2 drills trained, 2 focus areas: "Dribbling", "1v1 Attacking".
    # Focus area ratio should be 2/2 = 1.0 (both trained due to fuzzy match of "1v1 Attacking" -> "attacking").
    # Primary position matches are 2/2 = 1.0.
    # Coverage score should be 0.7 * 1.0 + 0.3 * 1.0 = 1.0 -> 100.
    score = _calculate_coverage(completions, ["Dribbling", "1v1 Attacking"], drills_df, plan, "Striker")
    assert score == 100.0

    # Also test empty completions returns 30.0 floor
    empty_score = _calculate_coverage([], ["Dribbling"], drills_df, plan, "Striker")
    assert empty_score == 30.0

