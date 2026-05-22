import pytest
import os
import json
from pathlib import Path
from training_plan_generator import generate_training_plan
import completion_tracker

def _sample_drills():
    return [
        {
            "drill_id": "DRILL_001",
            "drill_name": "Solo Dribbling",
            "category": "Technical",
            "difficulty": "beginner",
            "intensity": "medium",
            "solo_possible": True,
            "min_equipment": "Ball only",
            "position_relevance": "Universal",
            "tags": "dribbling|ball control"
        },
        {
            "drill_id": "DRILL_002",
            "drill_name": "Partner Passing",
            "category": "Technical",
            "difficulty": "intermediate",
            "intensity": "medium",
            "solo_possible": False,
            "min_equipment": "Partner",
            "position_relevance": "Midfielder",
            "tags": "passing"
        },
        {
            "drill_id": "DRILL_003",
            "drill_name": "Warmup Jog",
            "category": "Warmup",
            "difficulty": "beginner",
            "intensity": "low",
            "solo_possible": True,
            "min_equipment": "Ball only",
            "position_relevance": "Universal",
            "tags": "warmup"
        },
        {
            "drill_id": "DRILL_004",
            "drill_name": "Elite Shooting",
            "category": "Tactical",
            "difficulty": "elite",
            "intensity": "high",
            "solo_possible": True,
            "min_equipment": "Goal",
            "position_relevance": "Forward",
            "tags": "shooting"
        }
    ]

def test_generate_training_plan_solo_only():
    profile = {
        "name": "Alex",
        "sessions_per_week": 2,
        "session_duration": 30,
        "position": "Defender",
        "secondary_position": "",
        "level": "Recreational",
        "equipment_available": ["Agility Cones"],
        "focus_areas": ["Dribbling"]
    }
    
    plan = generate_training_plan(profile, _sample_drills())
    assert "generated_date" in plan
    assert len(plan["weeks"]) == 1
    
    sessions = plan["weeks"][0]["sessions"]
    assert len(sessions) == 2
    
    # Check that partner drills are excluded because no partner in equipment_available
    for session in sessions:
        for drill in session["drills"]:
            # Alex is solo, so DRILL_002 (Partner Passing) must NOT be included
            assert drill["drill_id"] != "DRILL_002"
            
            # Recreational level means only beginner or intermediate drills
            assert drill["difficulty"] in ["beginner", "intermediate"]

def test_generate_training_plan_with_partner_and_goal():
    profile = {
        "name": "Sam",
        "sessions_per_week": 1,
        "session_duration": 45,
        "position": "Forward",
        "secondary_position": "Midfielder",
        "level": "Academy/Select",
        "equipment_available": ["Soccer Goal", "Training partner available"],
        "focus_areas": ["Shooting"]
    }
    
    plan = generate_training_plan(profile, _sample_drills())
    sessions = plan["weeks"][0]["sessions"]
    
    # Forward/Midfielder + Academy/Select + partner + goal can select Elite Shooting
    drill_ids = [d["drill_id"] for s in sessions for d in s["drills"]]
    assert "DRILL_004" in drill_ids

def test_completion_tracker_and_streak(tmp_path):
    # Setup files in tmp_path
    plan_data = {
        "generated_date": "2026-05-21T01:00:34",
        "weeks": [
            {
                "week_number": 1,
                "sessions": [
                    {"day_number": 1, "completed": False, "drills": []},
                    {"day_number": 2, "completed": False, "drills": []}
                ]
            }
        ]
    }
    
    # Save plan
    plan_path = tmp_path / "weekly_training_plan.json"
    with open(plan_path, "w") as f:
        json.dump(plan_data, f)
        
    # Mark complete
    completion_tracker.mark_session_complete(1, 1, str(tmp_path))
    
    # Reload and check
    with open(plan_path, "r") as f:
        loaded_plan = json.load(f)
    assert loaded_plan["weeks"][0]["sessions"][0]["completed"] is True
    
    # Check completion count
    total = completion_tracker.get_total_sessions_completed(str(tmp_path))
    assert total == 1
    
    # Check week status
    status = completion_tracker.get_week_completion_status(1, str(tmp_path))
    assert status["completed"] == 1
    assert status["total"] == 2
    
    # Check streak
    streak = completion_tracker.get_current_streak(str(tmp_path))
    assert streak == 1
