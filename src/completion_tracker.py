"""
Completion Tracker for Player Development Platform.

Tracks player session completions, logs events to completion_log.json,
and computes total sessions and streaks.
"""
from datetime import datetime, date, timedelta
from typing import Dict, Any, List
from pathlib import Path
import data_loader

def mark_session_complete(week_number: int, day_number: int, data_path: str) -> None:
    """
    Mark a specific session as complete in weekly_training_plan.json and log in completion_log.json.
    """
    # 1. Update weekly training plan
    plan = data_loader.load_weekly_training_plan(data_path)
    if plan:
        for week in plan.get("weeks", []):
            if week.get("week_number") == week_number:
                for session in week.get("sessions", []):
                    if session.get("day_number") == day_number:
                        session["completed"] = True
                        session["completed_date"] = datetime.now().isoformat()
        data_loader.save_weekly_training_plan(plan, data_path)
        
    # 2. Add log entry to completion_log.json
    log = data_loader.load_completion_log(data_path)
    if not log or "completions" not in log:
        log = {"completions": []}
        
    # Prevent duplicate logging of the same session on the same day if clicked twice
    already_logged = False
    for entry in log.get("completions", []):
        if entry.get("week") == week_number and entry.get("day") == day_number:
            already_logged = True
            break
            
    if not already_logged:
        log["completions"].append({
            "timestamp": datetime.now().isoformat(),
            "date": date.today().isoformat(),
            "week": week_number,
            "day": day_number
        })
        data_loader.save_completion_log(log, data_path)

    # Trigger RRS snapshot after session completion
    try:
        import rrs_calculator
        import pandas as pd

        athlete_profile = data_loader.load_athlete_profile(data_path)
        completion_log = data_loader.load_completion_log(data_path)
        plan = data_loader.load_weekly_training_plan(data_path)

        # Load drills — try session state first, fall back to CSV
        try:
            import streamlit as st
            drills_df = st.session_state.get("drills_df")
        except Exception:
            drills_df = None

        if drills_df is None:
            drills_path = Path(data_path) / "drill_library.csv"
            if drills_path.exists():
                drills_df = pd.read_csv(drills_path)

        if athlete_profile:
            rrs = rrs_calculator.calculate_rrs(
                athlete_profile, completion_log, drills_df, plan
            )
            if rrs.get("unlocked"):
                history = data_loader.load_rrs_history(data_path)
                snapshots = history.get("snapshots", [])
                today_str = rrs["snapshot_date"]
                # Only write one snapshot per day
                if not snapshots or snapshots[-1].get("date") != today_str:
                    snapshots.append({
                        "date": today_str,
                        "overall": rrs["overall"],
                        "pillars": {
                            k: v["score"]
                            for k, v in rrs["pillars"].items()
                        }
                    })
                    history["snapshots"] = snapshots
                    data_loader.save_rrs_history(history, data_path)
    except Exception:
        pass  # Never let RRS errors block session completion

def get_week_completion_status(week_number: int, data_path: str) -> dict:
    """
    Get the completion count and total sessions for a given week.
    """
    plan = data_loader.load_weekly_training_plan(data_path)
    completed = 0
    total = 0
    if plan:
        for week in plan.get("weeks", []):
            if week.get("week_number") == week_number:
                sessions = week.get("sessions", [])
                total = len(sessions)
                completed = sum(1 for s in sessions if s.get("completed", False))
    return {
        "completed": completed,
        "total": total
    }

def get_total_sessions_completed(data_path: str) -> int:
    """
    Get total sessions completed.
    """
    log = data_loader.load_completion_log(data_path)
    return len(log.get("completions", []))

def get_current_streak(data_path: str) -> int:
    """
    Calculate current consecutive days streak of session completions.
    The streak continues if a session was completed today or yesterday.
    """
    log = data_loader.load_completion_log(data_path)
    if not log or "completions" not in log:
        return 0
        
    unique_dates = set()
    for entry in log.get("completions", []):
        d_str = entry.get("date")
        if d_str:
            unique_dates.add(d_str)
            
    if not unique_dates:
        return 0
        
    current_date = date.today()
    yesterday = current_date - timedelta(days=1)
    
    if current_date.isoformat() in unique_dates:
        check_date = current_date
    elif yesterday.isoformat() in unique_dates:
        check_date = yesterday
    else:
        return 0
        
    streak = 0
    while check_date.isoformat() in unique_dates:
        streak += 1
        check_date -= timedelta(days=1)
        
    return streak
