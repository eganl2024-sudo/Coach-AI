"""
Recruit Readiness Score (RRS) Calculation Engine.

Provides core scoring logic, benchmarks, and actionable insights.
"""
from datetime import date, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
import pandas as pd

BENCHMARKS = [
    (0,  24,  "Getting Started",     "#94a3b8"),
    (25, 44,  "Recreational Player", "#60a5fa"),
    (45, 59,  "Club Level",          "#34d399"),
    (60, 74,  "Varsity Starter",     "#fbbf24"),
    (75, 87,  "College Prospect",    "#f97316"),
    (88, 100, "D1 Ready",            "#a855f7"),
]

TARGET_LEVEL_TO_THRESHOLD = {
    "Recreational":     45,
    "Competitive Club": 60,
    "Academy/Select":   75,
}

TIERS = ["beginner", "intermediate", "advanced", "elite"]
TIER_VALUES = {"beginner": 1, "intermediate": 2, "advanced": 3, "elite": 4}

def get_benchmark_for_score(score: int) -> Tuple[str, str]:
    """
    Public helper to get the benchmark label and hex color for a given score.
    """
    if score < 0:
        return "Getting Started", "#94a3b8"
    if score > 100:
        return "D1 Ready", "#a855f7"
    for low, high, label, color in BENCHMARKS:
        if low <= score <= high:
            return label, color
    return "Getting Started", "#94a3b8"

def _calculate_streak(completions: list) -> int:
    """
    Calculate the consecutive days streak of completions allowing up to a 3-day gap.
    """
    unique_dates = sorted(list({c.get("date") for c in completions if c.get("date")}))
    if not unique_dates:
        return 0
    
    parsed_dates = []
    for d_str in unique_dates:
        try:
            parsed_dates.append(date.fromisoformat(d_str))
        except ValueError:
            continue
            
    if not parsed_dates:
        return 0
        
    # Ensure the streak is currently active (last session within past 3 days)
    if (date.today() - parsed_dates[-1]).days > 3:
        return 0
        
    streak = 1
    for i in range(len(parsed_dates) - 1, 0, -1):
        gap = (parsed_dates[i] - parsed_dates[i-1]).days
        if gap <= 3:
            streak += 1
        else:
            break
    return streak

def _calculate_consistency(completions: list, sessions_per_week: int) -> float:
    """
    Pillar 1 - Consistency (weight: 0.30)
    Measures training habit reliability over the last 4 weeks.
    """
    today = date.today()
    # Monday of current week
    monday = today - timedelta(days=today.weekday())
    
    # Define the start and end of the last 4 weeks (oldest to newest)
    weeks = []
    for i in reversed(range(4)):
        w_monday = monday - timedelta(weeks=i)
        w_sunday = w_monday + timedelta(days=6)
        weeks.append((w_monday, w_sunday))
        
    # Recency weights: oldest to newest
    weights = [0.15, 0.20, 0.30, 0.35]
    
    weighted_score = 0.0
    for idx, (start_date, end_date) in enumerate(weeks):
        sessions_that_week = 0
        for entry in completions:
            d_str = entry.get("date")
            if d_str:
                try:
                    c_date = date.fromisoformat(d_str)
                    if start_date <= c_date <= end_date:
                        sessions_that_week += 1
                except ValueError:
                    continue
        weekly_score = min(1.0, sessions_that_week / sessions_per_week)
        weighted_score += weekly_score * weights[idx]
        
    streak = _calculate_streak(completions)
    streak_bonus = 5 if streak >= 14 else (2 if streak >= 7 else 0)
    
    return min(100.0, float(round(weighted_score * 100 + streak_bonus)))

def _calculate_volume(completions: list, profile_created_date: str, sessions_per_week: int) -> float:
    """
    Pillar 2 - Volume (weight: 0.20)
    Measures total training investment since profile creation.
    """
    created_date = None
    if profile_created_date:
        try:
            created_date = date.fromisoformat(profile_created_date)
        except ValueError:
            pass
            
    if not created_date:
        created_date = date.today() - timedelta(weeks=4)
        
    days_since_creation = (date.today() - created_date).days
    weeks_active = max(1.0, days_since_creation / 7.0)
    expected_sessions = round(weeks_active * sessions_per_week)
    expected_sessions = max(1, expected_sessions)
    
    actual_sessions = len(completions)
    raw_score = min(1.0, actual_sessions / expected_sessions)
    
    return max(20.0, float(round(raw_score * 100)))

def _get_drill_info(drill_name: str, drills_df) -> Optional[dict]:
    """
    Helper to search for drill details by case-insensitive name match.
    """
    if drills_df is None:
        return None
    if isinstance(drills_df, pd.DataFrame):
        rows = drills_df[drills_df["drill_name"].str.lower() == drill_name.lower()]
        if not rows.empty:
            return rows.iloc[0].to_dict()
    elif isinstance(drills_df, list):
        for d in drills_df:
            if d.get("drill_name", "").lower() == drill_name.lower():
                return d
    return None

def _calculate_coverage(completions: list, focus_areas: list, drills_df, plan: dict,
                        primary_position: Optional[str] = None,
                        secondary_position: Optional[str] = None) -> float:
    """
    Pillar 3 - Coverage (weight: 0.25)
    Measures whether the player is training their stated focus areas and position relevance.
    """
    if not focus_areas:
        focus_ratio = 0.5
    else:
        focus_ratio = None
        
    fourteen_days_ago = date.today() - timedelta(days=14)
    recent_completions = []
    for c in completions:
        d_str = c.get("date")
        if d_str:
            try:
                c_date = date.fromisoformat(d_str)
                if c_date >= fourteen_days_ago:
                    recent_completions.append(c)
            except ValueError:
                continue
                
    drill_names = []
    for c in recent_completions:
        c_week = c.get("week")
        c_day = c.get("day")
        if plan and plan.get("weeks"):
            for w in plan.get("weeks", []):
                if w.get("week_number") == c_week:
                    for s in w.get("sessions", []):
                        if s.get("day_number") == c_day:
                            for d in s.get("drills", []):
                                name = d.get("drill_name")
                                if name:
                                    drill_names.append(name)
                                    
    if not drill_names:
        return 50.0
        
    # Calculate focus area ratio
    if focus_ratio is None:
        focus_areas_trained = 0
        for fa in focus_areas:
            fa_lower = fa.lower()
            trained = False
            for name in drill_names:
                d_info = _get_drill_info(name, drills_df)
                if d_info:
                    cat = str(d_info.get("skill_category", "")).lower()
                    tags = str(d_info.get("tags", "")).lower()
                    if fa_lower in cat or fa_lower in tags:
                        trained = True
                        break
            if trained:
                focus_areas_trained += 1
        focus_ratio = focus_areas_trained / len(focus_areas)
        
    # Calculate position alignment score
    primary_lower = primary_position.lower().strip() if primary_position else ""
    secondary_lower = secondary_position.lower().strip() if secondary_position else ""
    if secondary_lower == "none":
        secondary_lower = ""
        
    primary_matches = 0
    secondary_matches = 0
    
    for name in drill_names:
        d_info = _get_drill_info(name, drills_df)
        if d_info:
            pos_rel_raw = d_info.get("position_relevance", "")
            pos_rel_parts = []
            if isinstance(pos_rel_raw, list):
                pos_rel_parts = [p.lower().strip() for p in pos_rel_raw if p.strip()]
            elif pos_rel_raw:
                pos_rel_parts = [p.lower().strip() for p in str(pos_rel_raw).split("|") if p.strip()]
                
            # If no position relevance details, it's a universal drill
            if not pos_rel_parts:
                primary_matches += 1
                secondary_matches += 1
            else:
                if primary_lower and primary_lower in pos_rel_parts:
                    primary_matches += 1
                if secondary_lower and secondary_lower in pos_rel_parts:
                    secondary_matches += 1
                    
    primary_ratio = primary_matches / len(drill_names)
    secondary_ratio = secondary_matches / len(drill_names)
    
    if secondary_lower:
        position_alignment = 0.70 * primary_ratio + 0.30 * secondary_ratio
    else:
        position_alignment = primary_ratio
        
    score = round((0.70 * focus_ratio + 0.30 * position_alignment) * 100)
    
    # Weak Foot Development bonus
    has_weak_foot_bonus = False
    if focus_areas and "Weak Foot Development" in focus_areas:
        for name in drill_names:
            d_info = _get_drill_info(name, drills_df)
            if d_info:
                tags = str(d_info.get("tags", "")).lower()
                if "weak foot" in tags or "left foot" in tags or "right foot" in tags:
                    has_weak_foot_bonus = True
                    break
                    
    if has_weak_foot_bonus:
        score += 10
        
    return min(100.0, float(score))

REWARD_MATRIX = {
    "Recreational": {
        "beginner": 1.0,
        "intermediate": 1.0,
        "advanced": 1.2,
        "elite": 1.4
    },
    "Competitive Club": {
        "beginner": 0.5,
        "intermediate": 1.0,
        "advanced": 1.0,
        "elite": 1.2
    },
    "Academy/Select": {
        "beginner": 0.2,
        "intermediate": 0.6,
        "advanced": 1.0,
        "elite": 1.0
    }
}

def _calculate_progression(completions: list, current_level: str, plan: dict, drills_df) -> float:
    """
    Pillar 4 - Progression (weight: 0.25)
    Measures whether training difficulty matches the player's goals.
    """
    level_rewards = REWARD_MATRIX.get(current_level, REWARD_MATRIX["Recreational"])
    
    total_drills_checked = 0
    total_points = 0.0
    
    for c in completions:
        c_week = c.get("week")
        c_day = c.get("day")
        if plan and plan.get("weeks"):
            for w in plan.get("weeks", []):
                if w.get("week_number") == c_week:
                    for s in w.get("sessions", []):
                        if s.get("day_number") == c_day:
                            for d in s.get("drills", []):
                                name = d.get("drill_name")
                                if name:
                                    d_info = _get_drill_info(name, drills_df)
                                    if d_info:
                                        diff = str(d_info.get("difficulty", "intermediate")).lower().strip()
                                        if diff in level_rewards:
                                            total_points += level_rewards[diff]
                                            total_drills_checked += 1
                                            
    if total_drills_checked == 0:
        return 50.0
        
    prog_score = (total_points / total_drills_checked) * 100.0
    return min(100.0, float(round(prog_score)))

def calculate_rrs(athlete_profile: dict, completion_log: dict,
                  drills_df, plan: dict) -> dict:
    """
    Single entry point for all RRS calculations.
    """
    completions = []
    if completion_log and isinstance(completion_log, dict):
        completions = completion_log.get("completions", [])
        
    total_sessions = len(completions)
    unlocked = total_sessions >= 5
    sessions_until_unlock = max(0, 5 - total_sessions)
    
    # Safe defaults or actual calculations
    if not unlocked:
        consistency_score = 0
        volume_score = 0
        coverage_score = 0
        progression_score = 0
        overall = 0
    else:
        sessions_per_week = athlete_profile.get("sessions_per_week", 3)
        try:
            sessions_per_week = int(sessions_per_week)
        except Exception:
            sessions_per_week = 3
        if sessions_per_week <= 0:
            sessions_per_week = 3
            
        consistency_score = _calculate_consistency(completions, sessions_per_week)
        
        created_date_str = athlete_profile.get("created_date", None)
        volume_score = _calculate_volume(completions, created_date_str, sessions_per_week)
        
        focus_areas = athlete_profile.get("focus_areas", [])
        primary_pos = athlete_profile.get("position", "")
        secondary_pos = athlete_profile.get("secondary_position", "")
        coverage_score = _calculate_coverage(completions, focus_areas, drills_df, plan, primary_pos, secondary_pos)
        
        current_level = athlete_profile.get("level", "Recreational")
        progression_score = _calculate_progression(completions, current_level, plan, drills_df)
        
        overall = round(
            consistency_score * 0.30 +
            volume_score * 0.20 +
            coverage_score * 0.25 +
            progression_score * 0.25
        )
        
    current_label, current_color = get_benchmark_for_score(overall)
    
    # Next benchmark milestone
    next_label = None
    next_threshold = None
    points_needed = None
    for low, high, label, color in BENCHMARKS:
        if low > overall:
            next_label = label
            next_threshold = low
            points_needed = max(0, next_threshold - overall)
            break
            
    # Target level progress
    target_level = athlete_profile.get("level", "Recreational")
    target_threshold = TARGET_LEVEL_TO_THRESHOLD.get(target_level, 45)
    on_track = overall >= target_threshold
    
    target_benchmark = {
        "label": target_level,
        "threshold": target_threshold,
        "on_track": on_track
    }
    
    # Calculate weekly delta using loaded history
    weekly_delta = 0
    try:
        import config
        import data_loader
        d_path = None
        try:
            import streamlit as st
            if "data_path" in st.session_state:
                d_path = st.session_state.data_path
        except Exception:
            pass
        if not d_path:
            d_path = config.get_data_path()
            
        history = data_loader.load_rrs_history(d_path)
        snapshots = history.get("snapshots", [])
        if snapshots:
            if len(snapshots) >= 2 and snapshots[-1].get("overall") == overall:
                last_snapshot = snapshots[-2]
            else:
                last_snapshot = snapshots[-1]
            weekly_delta = overall - last_snapshot.get("overall", 0)
    except Exception:
        pass
        
    # Calculate completed_this_week for next actions
    completed_this_week = 0
    if plan:
        current_week_number = plan.get("current_week_number", 1)
        for week in plan.get("weeks", []):
            if week.get("week_number") == current_week_number:
                completed_this_week = sum(1 for s in week.get("sessions", []) if s.get("completed", False))
                break
                
    # Next Actions
    next_actions = []
    if unlocked:
        sessions_per_week = athlete_profile.get("sessions_per_week", 3)
        try:
            sessions_per_week = int(sessions_per_week)
        except Exception:
            sessions_per_week = 3
        if sessions_per_week <= 0:
            sessions_per_week = 3
            
        pillar_list = [
            ("Consistency", consistency_score),
            ("Volume", volume_score),
            ("Coverage", coverage_score),
            ("Progression", progression_score)
        ]
        pillar_list.sort(key=lambda x: x[1])
        
        focus_areas = athlete_profile.get("focus_areas", [])
        
        for p_name, p_score in pillar_list:
            if len(next_actions) >= 3:
                break
            if p_name == "Coverage" and p_score < 60:
                lowest_focus_area = focus_areas[0] if focus_areas else "Weak Foot Development"
                next_actions.append(f"Train drills in your focus areas — especially {lowest_focus_area}")
            elif p_name == "Consistency" and p_score < 60:
                needed = max(1, sessions_per_week - completed_this_week)
                next_actions.append(f"Complete {needed} more sessions this week to build your streak")
            elif p_name == "Progression" and p_score < 60:
                next_actions.append("Push to higher difficulty drills to accelerate your score")
                
        if not on_track and len(next_actions) < 3:
            weakest_pillar = pillar_list[0][0]
            next_actions.append(f"You're {points_needed} points from your target — focus on {weakest_pillar}")
            
        if len(next_actions) < 2:
            next_actions.append("Keep completing your scheduled sessions to maintain consistency")
            next_actions.append("Review your athlete profile to ensure focus areas are up to date")
    else:
        next_actions = ["Complete at least 5 sessions to unlock actions and see recommendations"]
        
    return {
        "unlocked": unlocked,
        "sessions_until_unlock": sessions_until_unlock,
        "overall": int(overall),
        "pillars": {
            "consistency": {"score": int(consistency_score), "weight": 0.30, "label": "Consistency"},
            "volume":      {"score": int(volume_score), "weight": 0.20, "label": "Volume"},
            "coverage":    {"score": int(coverage_score), "weight": 0.25, "label": "Coverage"},
            "progression": {"score": int(progression_score), "weight": 0.25, "label": "Progression"}
        },
        "benchmark": {
            "current_label":   current_label,
            "current_color":   current_color,
            "next_label":      next_label,
            "next_threshold":  next_threshold,
            "points_needed":   points_needed
        },
        "target_benchmark": target_benchmark,
        "next_actions": next_actions,
        "weekly_delta": int(weekly_delta),
        "snapshot_date": date.today().isoformat()
    }
