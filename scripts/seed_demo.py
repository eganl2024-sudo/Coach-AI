import os
import json
import shutil
import sys
import csv
from pathlib import Path
from datetime import date, timedelta, datetime

# Reconfigure stdout to handle UTF-8 checkmarks safely on Windows cp1252 terminals
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def seed():
    # 1. Define paths
    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / 'data'
    prod_dir = data_dir / 'production'
    demo_dir = data_dir / 'demo'
    
    # Create demo directory if it doesn't exist
    demo_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Copy drill_library.csv and presenters.csv to make the sandbox self-contained
    shutil.copy(prod_dir / 'drill_library.csv', demo_dir / 'drill_library.csv')
    shutil.copy(data_dir / 'presenters.csv', demo_dir / 'presenters.csv')
    
    # 3. Create athlete_profile.json
    today = date.today()
    athlete_profile = {
        "name": "Alex",
        "age": 16,
        "preferred_foot": "Right",
        "position": "Striker",
        "secondary_position": "None",
        "level": "Competitive Club",
        "target_level": "College Prospect",
        "sessions_per_week": 4,
        "session_duration": 60,
        "focus_areas": ["Finishing", "First Touch", "1v1 Attacking"],
        "equipment_available": ["Ball only", "Cones", "Goal"],
        "age_group": "U17",
        "created_date": (today - timedelta(days=28)).isoformat()
    }
    
    with open(demo_dir / 'athlete_profile.json', 'w', encoding='utf-8') as f:
        json.dump(athlete_profile, f, indent=2)
    print("✓ data/demo/athlete_profile.json")
    
    # 4. Load drills from drill_library.csv to build the weekly plan dynamically
    drills_dict = {}
    with open(prod_dir / 'drill_library.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Perform basic type conversions to match production schema
            d = dict(row)
            d["players_min"] = int(float(d["players_min"])) if d.get("players_min") else 0
            d["players_max"] = int(float(d["players_max"])) if d.get("players_max") else 0
            d["duration_minutes"] = int(float(d["duration_minutes"])) if d.get("duration_minutes") else 0
            d["series_order"] = int(float(d["series_order"])) if d.get("series_order") else 0
            d["coach_rating"] = int(float(d["coach_rating"])) if d.get("coach_rating") else 3
            d["is_favorite"] = d.get("is_favorite", "").strip().lower() in ("true", "1", "yes")
            d["solo_possible"] = d.get("solo_possible", "").strip().lower() not in ("false", "0", "no")
            d["beta_ready"] = d.get("beta_ready", "").strip().lower() in ("true", "1", "yes")
            drills_dict[d["drill_id"]] = d

    # Monday of the current week
    monday = today - timedelta(days=today.weekday())
    
    # 5. Create completion_log.json — 10 sessions across 3 plan weeks
    # Week 1 (3 weeks ago): 4 sessions
    # Week 2 (2 weeks ago): 4 sessions
    # Week 3 / current week: 2 sessions complete
    w1 = today - timedelta(weeks=3)
    w2 = today - timedelta(weeks=2)
    w3 = today - timedelta(weeks=1)
    completions = [
        # Week 1 sessions
        {
            "session_id": "demo_session_001",
            "timestamp": w1.isoformat() + "T16:30:00",
            "date": w1.isoformat(),
            "week": 1,
            "day": 1,
            "drills_completed": ["TACT_001", "WARM_006", "TECH_003", "WARM_004"],
            "duration_minutes": 60,
            "difficulty": "Intermediate",
            "focus_areas": ["Finishing"]
        },
        {
            "session_id": "demo_session_002",
            "timestamp": (w1 + timedelta(days=1)).isoformat() + "T17:25:00",
            "date": (w1 + timedelta(days=1)).isoformat(),
            "week": 1,
            "day": 2,
            "drills_completed": ["WARM_001", "TECH_002", "COOL_003", "COOL_005"],
            "duration_minutes": 55,
            "difficulty": "Intermediate",
            "focus_areas": ["First Touch"]
        },
        {
            "session_id": "demo_session_003",
            "timestamp": (w1 + timedelta(days=3)).isoformat() + "T15:00:00",
            "date": (w1 + timedelta(days=3)).isoformat(),
            "week": 1,
            "day": 3,
            "drills_completed": ["WARM_004", "TECH_007", "SSG_001", "COOL_002"],
            "duration_minutes": 60,
            "difficulty": "Advanced",
            "focus_areas": ["1v1 Attacking"]
        },
        {
            "session_id": "demo_session_004",
            "timestamp": (w1 + timedelta(days=5)).isoformat() + "T16:45:00",
            "date": (w1 + timedelta(days=5)).isoformat(),
            "week": 1,
            "day": 4,
            "drills_completed": ["WARM_006", "TECH_003", "TECH_001", "COOL_004"],
            "duration_minutes": 50,
            "difficulty": "Advanced",
            "focus_areas": ["First Touch"]
        },
        # Week 2 sessions
        {
            "session_id": "demo_session_005",
            "timestamp": w2.isoformat() + "T16:00:00",
            "date": w2.isoformat(),
            "week": 2,
            "day": 1,
            "drills_completed": ["WARM_001", "TECH_007", "TACT_001", "COOL_002"],
            "duration_minutes": 60,
            "difficulty": "Advanced",
            "focus_areas": ["Finishing"]
        },
        {
            "session_id": "demo_session_006",
            "timestamp": (w2 + timedelta(days=2)).isoformat() + "T17:00:00",
            "date": (w2 + timedelta(days=2)).isoformat(),
            "week": 2,
            "day": 2,
            "drills_completed": ["WARM_006", "TECH_003", "COOL_003", "COOL_004"],
            "duration_minutes": 55,
            "difficulty": "Intermediate",
            "focus_areas": ["First Touch"]
        },
        {
            "session_id": "demo_session_007",
            "timestamp": (w2 + timedelta(days=4)).isoformat() + "T15:30:00",
            "date": (w2 + timedelta(days=4)).isoformat(),
            "week": 2,
            "day": 3,
            "drills_completed": ["WARM_004", "TECH_002", "SSG_001", "COOL_005"],
            "duration_minutes": 60,
            "difficulty": "Advanced",
            "focus_areas": ["1v1 Attacking"]
        },
        {
            "session_id": "demo_session_008",
            "timestamp": (w2 + timedelta(days=5)).isoformat() + "T16:15:00",
            "date": (w2 + timedelta(days=5)).isoformat(),
            "week": 2,
            "day": 4,
            "drills_completed": ["WARM_001", "TECH_007", "TACT_001", "COOL_002"],
            "duration_minutes": 50,
            "difficulty": "Advanced",
            "focus_areas": ["First Touch"]
        },
        # Week 3 (current) — 2 of 4 complete
        {
            "session_id": "demo_session_009",
            "timestamp": w3.isoformat() + "T16:30:00",
            "date": w3.isoformat(),
            "week": 3,
            "day": 1,
            "drills_completed": ["TACT_001", "WARM_006", "TECH_003", "WARM_004"],
            "duration_minutes": 60,
            "difficulty": "Intermediate",
            "focus_areas": ["Finishing"]
        },
        {
            "session_id": "demo_session_010",
            "timestamp": (w3 + timedelta(days=1)).isoformat() + "T17:25:00",
            "date": (w3 + timedelta(days=1)).isoformat(),
            "week": 3,
            "day": 2,
            "drills_completed": ["WARM_001", "TECH_002", "COOL_003", "COOL_005"],
            "duration_minutes": 55,
            "difficulty": "Intermediate",
            "focus_areas": ["First Touch"]
        }
    ]
    
    completion_log = {
        "completions": completions
    }
    
    with open(demo_dir / 'completion_log.json', 'w', encoding='utf-8') as f:
        json.dump(completion_log, f, indent=2)
    print("✓ data/demo/completion_log.json")
    
    # 6. Create rrs_history.json
    rrs_history = {
        "snapshots": [
            {
                "date": (today - timedelta(days=28)).isoformat(),
                "overall": 51,
                "pillars": {
                    "consistency": 48,
                    "volume": 52,
                    "coverage": 44,
                    "progression": 58
                }
            },
            {
                "date": (today - timedelta(days=21)).isoformat(),
                "overall": 55,
                "pillars": {
                    "consistency": 54,
                    "volume": 55,
                    "coverage": 49,
                    "progression": 61
                }
            },
            {
                "date": (today - timedelta(days=14)).isoformat(),
                "overall": 58,
                "pillars": {
                    "consistency": 61,
                    "volume": 57,
                    "coverage": 52,
                    "progression": 63
                }
            },
            {
                "date": (today - timedelta(days=7)).isoformat(),
                "overall": 62,
                "pillars": {
                    "consistency": 68,
                    "volume": 60,
                    "coverage": 57,
                    "progression": 64
                }
            }
        ]
    }
    
    with open(demo_dir / 'rrs_history.json', 'w', encoding='utf-8') as f:
        json.dump(rrs_history, f, indent=2)
    print("✓ data/demo/rrs_history.json")
    
    # Helper to construct SessionDrill lists
    def make_drills(ids, times, block_types):
        res = []
        for idx, (d_id, t, bt) in enumerate(zip(ids, times, block_types)):
            base = dict(drills_dict[d_id])
            base["allocated_time"] = t
            base["block_type"] = bt
            base["block_index"] = idx
            res.append(base)
        return res

    # 7. Create weekly_training_plan.json — 3-week multi-week format
    # Week 1: fully archived, 4/4 sessions complete (3 weeks ago)
    week1_monday = today - timedelta(weeks=3)
    week1_sessions = [
        {
            "day_number": 1,
            "name": "Session 1: Alex's Development Plan - Finishing Focus",
            "duration_minutes": 60,
            "drills": make_drills(
                ["TACT_001", "WARM_006", "TECH_003", "WARM_004"],
                [20, 10, 20, 10],
                ["technical", "warmup", "technical", "warmup"]
            ),
            "completed": True,
            "completed_date": week1_monday.isoformat() + "T16:30:00"
        },
        {
            "day_number": 2,
            "name": "Session 2: Alex's Development Plan - First Touch & Passing Focus",
            "duration_minutes": 55,
            "drills": make_drills(
                ["WARM_001", "TECH_002", "COOL_003", "COOL_005"],
                [10, 20, 15, 10],
                ["warmup", "technical", "cooldown", "cooldown"]
            ),
            "completed": True,
            "completed_date": (week1_monday + timedelta(days=1)).isoformat() + "T17:25:00"
        },
        {
            "day_number": 3,
            "name": "Session 3: Alex's Development Plan - 1v1 Attacking",
            "duration_minutes": 60,
            "drills": make_drills(
                ["WARM_004", "TECH_007", "SSG_001", "COOL_002"],
                [10, 20, 25, 5],
                ["warmup", "technical", "technical", "cooldown"]
            ),
            "completed": True,
            "completed_date": (week1_monday + timedelta(days=3)).isoformat() + "T15:00:00"
        },
        {
            "day_number": 4,
            "name": "Session 4: Alex's Development Plan - Weak Foot & Technical Focus",
            "duration_minutes": 50,
            "drills": make_drills(
                ["WARM_006", "TECH_003", "TECH_001", "COOL_004"],
                [10, 20, 15, 5],
                ["warmup", "technical", "technical", "cooldown"]
            ),
            "completed": True,
            "completed_date": (week1_monday + timedelta(days=5)).isoformat() + "T16:45:00"
        }
    ]

    # Week 2: fully archived, 4/4 sessions complete (2 weeks ago)
    week2_monday = today - timedelta(weeks=2)
    week2_sessions = [
        {
            "day_number": 1,
            "name": "Session 1: Alex's Development Plan - Defensive Shape",
            "duration_minutes": 60,
            "drills": make_drills(
                ["WARM_001", "TECH_007", "TACT_001", "COOL_002"],
                [10, 20, 20, 10],
                ["warmup", "technical", "technical", "cooldown"]
            ),
            "completed": True,
            "completed_date": week2_monday.isoformat() + "T16:00:00"
        },
        {
            "day_number": 2,
            "name": "Session 2: Alex's Development Plan - Ball Mastery",
            "duration_minutes": 55,
            "drills": make_drills(
                ["WARM_006", "TECH_003", "COOL_003", "COOL_004"],
                [10, 20, 15, 10],
                ["warmup", "technical", "cooldown", "cooldown"]
            ),
            "completed": True,
            "completed_date": (week2_monday + timedelta(days=2)).isoformat() + "T17:00:00"
        },
        {
            "day_number": 3,
            "name": "Session 3: Alex's Development Plan - Pressing & Transitions",
            "duration_minutes": 60,
            "drills": make_drills(
                ["WARM_004", "TECH_002", "SSG_001", "COOL_005"],
                [10, 20, 20, 10],
                ["warmup", "technical", "technical", "cooldown"]
            ),
            "completed": True,
            "completed_date": (week2_monday + timedelta(days=4)).isoformat() + "T15:30:00"
        },
        {
            "day_number": 4,
            "name": "Session 4: Alex's Development Plan - Game Application",
            "duration_minutes": 50,
            "drills": make_drills(
                ["WARM_001", "TECH_007", "TACT_001", "COOL_002"],
                [10, 15, 20, 5],
                ["warmup", "technical", "technical", "cooldown"]
            ),
            "completed": True,
            "completed_date": (week2_monday + timedelta(days=5)).isoformat() + "T16:15:00"
        }
    ]

    # Week 3: current week, 2/4 sessions complete (this week)
    week3_monday = today - timedelta(weeks=1)
    week3_sessions = [
        {
            "day_number": 1,
            "name": "Session 1: Alex's Development Plan - Finishing Focus",
            "duration_minutes": 60,
            "drills": make_drills(
                ["TACT_001", "WARM_006", "TECH_003", "WARM_004"],
                [20, 10, 20, 10],
                ["technical", "warmup", "technical", "warmup"]
            ),
            "completed": True,
            "completed_date": week3_monday.isoformat() + "T16:30:00"
        },
        {
            "day_number": 2,
            "name": "Session 2: Alex's Development Plan - First Touch & Passing Focus",
            "duration_minutes": 55,
            "drills": make_drills(
                ["WARM_001", "TECH_002", "COOL_003", "COOL_005"],
                [10, 20, 15, 10],
                ["warmup", "technical", "cooldown", "cooldown"]
            ),
            "completed": True,
            "completed_date": (week3_monday + timedelta(days=1)).isoformat() + "T17:25:00"
        },
        {
            "day_number": 3,
            "name": "Session 3: Alex's Development Plan - 1v1 Attacking",
            "duration_minutes": 60,
            "drills": make_drills(
                ["WARM_004", "TECH_007", "SSG_001", "COOL_002"],
                [10, 20, 25, 5],
                ["warmup", "technical", "technical", "cooldown"]
            ),
            "completed": False,
            "completed_date": None
        },
        {
            "day_number": 4,
            "name": "Session 4: Alex's Development Plan - Weak Foot & Technical Focus",
            "duration_minutes": 50,
            "drills": make_drills(
                ["WARM_006", "TECH_003", "TECH_001", "COOL_004"],
                [10, 20, 15, 5],
                ["warmup", "technical", "technical", "cooldown"]
            ),
            "completed": False,
            "completed_date": None
        }
    ]

    week1_gen = (today - timedelta(weeks=3)).isoformat()
    week2_gen = (today - timedelta(weeks=2)).isoformat()
    week3_gen = (today - timedelta(weeks=1)).isoformat()
    week1_archived = (today - timedelta(weeks=2)).isoformat()
    week2_archived = (today - timedelta(weeks=1)).isoformat()

    weekly_training_plan = {
        "current_week_number": 3,
        "generated_date": week3_gen,
        "weeks": [
            {
                "week_number": 1,
                "generated_date": week1_gen,
                "archived_date": week1_archived,
                "sessions": week1_sessions
            },
            {
                "week_number": 2,
                "generated_date": week2_gen,
                "archived_date": week2_archived,
                "sessions": week2_sessions
            },
            {
                "week_number": 3,
                "generated_date": week3_gen,
                "archived_date": None,
                "sessions": week3_sessions
            }
        ]
    }

    with open(demo_dir / 'weekly_training_plan.json', 'w', encoding='utf-8') as f:
        json.dump(weekly_training_plan, f, indent=2)
    print("✓ data/demo/weekly_training_plan.json")
    
    # 8. Create mentor_feed.json
    mentor_feed = {
      "posts": [
        {
          "post_id": "POST_001",
          "presenter_id": "KC-01",
          "title": "What Professional CBs Actually Work On in Preseason",
          "description": "Most youth defenders think preseason is about fitness. At the professional level it is about building habits \u2014 the defensive shape, the trigger moments, and the distribution patterns you will run on autopilot for the next 9 months. Here is what we have been drilling at KC 2 this week.",
          "video_url": "",
          "date_posted": (today - timedelta(days=12)).isoformat(),
          "tags": "defending|playing out|professional training|center back",
          "position_tags": "Center Back|Full Back",
          "coming_soon": True
        },
        {
          "post_id": "POST_003",
          "presenter_id": "UNLV-01",
          "title": "The 1v1 Attacking Checklist for Striking Prospects",
          "description": "Alex, if you want to dominate at the next level, your 1v1 attacking can't just be about speed. You need to read the defender's front foot, take a decisive first touch into space, and finish cleanly with either foot. Here is my exact three-step checklist for attacking defenders in the final third.",
          "video_url": "",
          "date_posted": (today - timedelta(days=17)).isoformat(),
          "tags": "1v1|attacking|first touch|finishing|technical",
          "position_tags": "Striker|Winger",
          "coming_soon": True
        },
        {
          "post_id": "POST_004",
          "presenter_id": "YOU-01",
          "title": "The Distribution Mistake That Gets Goalkeepers Dropped",
          "description": "College and professional coaches do not drop goalkeepers for letting in goals. They drop them for ball-in-hand distribution mistakes. Specifically for playing into pressure when a simple long ball was available. Here is how to read a high press and make the right call every time.",
          "video_url": "",
          "date_posted": (today - timedelta(days=20)).isoformat(),
          "tags": "goalkeeper|distribution|pressing|decision making",
          "position_tags": "Goalkeeper",
          "coming_soon": True
        },
        {
          "post_id": "POST_005",
          "presenter_id": "ND-01",
          "title": "What I'd Tell My 15-Year-Old Self About Playing Goalkeeper",
          "description": "Most young goalkeepers focus on making saves. What actually determines whether you play at the next level is everything else \u2014 your distribution, your communication, your positioning before the shot even comes. Here is what I wish someone had told me when I was coming up.",
          "video_url": "",
          "date_posted": (today - timedelta(days=4)).isoformat(),
          "tags": "goalkeeping|positioning|distribution|college recruiting",
          "position_tags": "Goalkeeper",
          "coming_soon": True
        }
      ]
    }
    
    with open(demo_dir / 'mentor_feed.json', 'w', encoding='utf-8') as f:
        json.dump(mentor_feed, f, indent=2)
    print("✓ data/demo/mentor_feed.json")

    print("Demo account ready. Set DEMO_MODE = True in src/config.py to use it.")

    # Refresh the live demo sandbox if it exists locally
    # (i.e. create_demo_account.py has already run and created the directory)
    demo_user_dir = project_root / "data" / "production" / "users" / "demo"
    if demo_user_dir.exists():
        import shutil as _shutil
        files = [
            "athlete_profile.json",
            "completion_log.json",
            "weekly_training_plan.json",
            "rrs_history.json",
            "mentor_feed.json",
            "drill_library.csv",
            "presenters.csv",
        ]
        for f in files:
            src = demo_dir / f
            dst = demo_user_dir / f
            if src.exists():
                _shutil.copy(src, dst)
        print("✓ data/production/users/demo/ — sandbox refreshed")
    else:
        print("  Demo user sandbox not found locally — run on"
              " Streamlit Cloud or after create_demo_account.py")

if __name__ == '__main__':
    seed()
