#!/usr/bin/env python3
"""
Unit tests for training plan generator time allocations, duration splits, 
and remainder distribution logic.
"""

import sys
from pathlib import Path
import pytest
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from training_plan_generator import generate_training_plan

def get_mock_drills():
    return [
        {
            "drill_name": "Warmup Drill Low",
            "category": "warmup",
            "intensity": "low",
            "difficulty": "beginner",
            "solo_possible": True,
            "min_equipment": "Ball only",
            "position_relevance": "",
            "status": "Published"
        },
        {
            "drill_name": "Warmup Drill High",
            "category": "warmup",
            "intensity": "high",
            "difficulty": "beginner",
            "solo_possible": True,
            "min_equipment": "Ball only",
            "position_relevance": "",
            "status": "Published"
        },
        {
            "drill_name": "Technical Isolation Medium",
            "category": "technical",
            "drill_type": "isolation",
            "intensity": "medium",
            "difficulty": "intermediate",
            "solo_possible": True,
            "min_equipment": "Ball only",
            "position_relevance": "",
            "status": "Published"
        },
        {
            "drill_name": "Technical Pressure High",
            "category": "technical",
            "drill_type": "pressure",
            "intensity": "high",
            "difficulty": "intermediate",
            "solo_possible": True,
            "min_equipment": "Ball only",
            "position_relevance": "",
            "status": "Published"
        },
        {
            "drill_name": "Technical Isolation Low",
            "category": "technical",
            "drill_type": "isolation",
            "intensity": "low",
            "difficulty": "intermediate",
            "solo_possible": True,
            "min_equipment": "Ball only",
            "position_relevance": "",
            "status": "Published"
        },
        {
            "drill_name": "Game App High",
            "category": "game application",
            "drill_type": "game application",
            "intensity": "high",
            "difficulty": "intermediate",
            "solo_possible": True,
            "min_equipment": "Ball only",
            "position_relevance": "",
            "status": "Published"
        },
        {
            "drill_name": "Cooldown Drill Low",
            "category": "cooldown",
            "intensity": "low",
            "difficulty": "beginner",
            "solo_possible": True,
            "min_equipment": "Ball only",
            "position_relevance": "",
            "status": "Published"
        }
    ]

def test_session_duration_splits_75():
    athlete_profile = {
        "name": "Test Player",
        "level": "Competitive Club",
        "sessions_per_week": 1,
        "session_duration": 75,
        "position": "Striker",
        "equipment_available": ["Ball"],
        "focus_areas": ["Passing"]
    }
    
    plan = generate_training_plan(athlete_profile, get_mock_drills())
    session = plan["weeks"][0]["sessions"][0]
    
    assert session["duration_minutes"] == 75
    drills = session["drills"]
    
    warmup = [d for d in drills if d["block_type"] == "warmup"][0]
    technicals = [d for d in drills if d["block_type"] == "technical"]
    cooldown = [d for d in drills if d["block_type"] == "cooldown"][0]
    
    assert warmup["allocated_time"] == 10
    assert len(technicals) == 3
    for t in technicals:
        assert t["allocated_time"] == 18
    assert cooldown["allocated_time"] == 11

def test_session_duration_splits_90():
    athlete_profile = {
        "name": "Test Player",
        "level": "Competitive Club",
        "sessions_per_week": 1,
        "session_duration": 90,
        "position": "Striker",
        "equipment_available": ["Ball"],
        "focus_areas": ["Passing"]
    }
    
    plan = generate_training_plan(athlete_profile, get_mock_drills())
    session = plan["weeks"][0]["sessions"][0]
    
    assert session["duration_minutes"] == 90
    drills = session["drills"]
    
    warmup = [d for d in drills if d["block_type"] == "warmup"][0]
    technicals = [d for d in drills if d["block_type"] == "technical"]
    cooldown = [d for d in drills if d["block_type"] == "cooldown"][0]
    
    assert warmup["allocated_time"] == 15
    assert len(technicals) == 3
    for t in technicals:
        assert t["allocated_time"] == 20
    assert cooldown["allocated_time"] == 15

def test_session_duration_splits_120():
    athlete_profile = {
        "name": "Test Player",
        "level": "Competitive Club",
        "sessions_per_week": 1,
        "session_duration": 120,
        "position": "Striker",
        "equipment_available": ["Ball"],
        "focus_areas": ["Passing"]
    }
    
    plan = generate_training_plan(athlete_profile, get_mock_drills())
    session = plan["weeks"][0]["sessions"][0]
    
    assert session["duration_minutes"] == 120
    drills = session["drills"]
    
    warmup = [d for d in drills if d["block_type"] == "warmup"][0]
    technicals = [d for d in drills if d["block_type"] == "technical"]
    cooldown = [d for d in drills if d["block_type"] == "cooldown"][0]
    
    assert warmup["allocated_time"] == 15
    assert len(technicals) == 4
    for t in technicals:
        assert t["allocated_time"] == 22
    assert cooldown["allocated_time"] == 17

def test_remainder_distribution_logic():
    athlete_profile = {
        "name": "Test Player",
        "level": "Competitive Club",
        "sessions_per_week": 1,
        "session_duration": 80,
        "position": "Striker",
        "equipment_available": ["Ball"],
        "focus_areas": ["Passing"]
    }
    
    plan = generate_training_plan(athlete_profile, get_mock_drills())
    session = plan["weeks"][0]["sessions"][0]
    
    assert session["duration_minutes"] == 80
    drills = session["drills"]
    
    # 80m falls under <= 90m split.
    # Initial values: warmup=15, mains=3*20=60, cooldown=15. Total = 90.
    # Difference = 80 - 90 = -10.
    # Remainder logic: diff = -10, len(technical_drills) = 3
    # base_diff = -10 // 3 = -4. rem = -10 % 3 = 2.
    # Index 0 gets: 20 + base_diff + 1 = 20 - 4 + 1 = 17.
    # Index 1 gets: 20 + base_diff + 1 = 20 - 4 + 1 = 17.
    # Index 2 gets: 20 + base_diff = 20 - 4 = 16.
    # Sum = 17 + 17 + 16 = 50. Total session = 15 + 50 + 15 = 80.
    
    technicals = [d for d in drills if d["block_type"] == "technical"]
    assert len(technicals) == 3
    assert technicals[0]["allocated_time"] == 17
    assert technicals[1]["allocated_time"] == 17
    assert technicals[2]["allocated_time"] == 16
    assert sum(d["allocated_time"] for d in drills) == 80

def test_intensity_bell_curve_preferring_low():
    athlete_profile = {
        "name": "Test Player",
        "level": "Competitive Club",
        "sessions_per_week": 1,
        "session_duration": 45,
        "position": "Striker",
        "equipment_available": ["Ball"],
        "focus_areas": ["Passing"]
    }
    
    plan = generate_training_plan(athlete_profile, get_mock_drills())
    session = plan["weeks"][0]["sessions"][0]
    drills = session["drills"]
    
    # Warmup drill selected should be "Warmup Drill Low" because of preferred_intensity="low"
    warmup_drill = [d for d in drills if d["block_type"] == "warmup"][0]
    assert warmup_drill["drill_name"] == "Warmup Drill Low"
