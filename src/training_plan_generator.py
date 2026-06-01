"""
Training Plan Generator for Player AI.

Selects, filters, and structures personalized weekly training plans for players.
"""
from datetime import datetime, date, timezone
import random
from typing import List, Dict, Any, Optional
from models import SessionDrill

def generate_training_plan(
    athlete_profile: dict,
    drills: List[dict],
    week_number: int = 1,
    existing_plan: Optional[dict] = None,
) -> dict:
    """
    Generate a personalized weekly training plan for a player.

    Args:
        athlete_profile:  Dict containing player profiles and settings.
        drills:           List of raw drill dictionaries loaded from CSV.
        week_number:      Ignored when existing_plan is provided; used only
                          when bootstrapping the very first plan.
        existing_plan:    Full multi-week plan dict. When supplied the
                          current week is archived and a new week is appended.

    Returns:
        Dict representing the full multi-week training plan.
    """
    # Derive week_number from existing plan when provided
    if existing_plan and existing_plan.get("weeks"):
        week_number = max(w.get("week_number", 1) for w in existing_plan["weeks"]) + 1
    # Filter out unpublished drills
    drills = [d for d in drills if str(d.get("status", "Published")).lower().strip() == "published"]

    # 1. Read parameters from athlete profile
    sessions_per_week = int(athlete_profile.get("sessions_per_week", 3))
    session_duration = int(athlete_profile.get("session_duration", 30))
    position = athlete_profile.get("position", "")
    secondary_position = athlete_profile.get("secondary_position", "")
    level = athlete_profile.get("level", "Recreational")
    equipment_available = [e.lower() for e in athlete_profile.get("equipment_available", [])]
    focus_areas = [f.lower() for f in athlete_profile.get("focus_areas", [])]
    
    # 2. Level difficulty mapping
    # Recreational -> beginner, intermediate
    # Competitive Club -> intermediate, advanced
    # Academy/Select -> advanced, elite
    allowed_difficulties = set()
    if level == "Recreational":
        allowed_difficulties = {"beginner", "intermediate"}
    elif level == "Competitive Club":
        allowed_difficulties = {"intermediate", "advanced"}
    elif level == "Academy/Select":
        allowed_difficulties = {"advanced", "elite"}
    else:
        allowed_difficulties = {"beginner", "intermediate", "advanced", "elite"}
        
    # Check if a training partner is available
    has_partner = any("partner" in e for e in equipment_available)
    
    # 3. Filter drills step-by-step
    filtered_drills = []
    for drill in drills:
        # Determine drill properties
        drill_difficulty = str(drill.get("difficulty", "intermediate")).lower().strip()
        drill_solo = bool(drill.get("solo_possible") if drill.get("solo_possible") is not None else True)
        if isinstance(drill.get("solo_possible"), str):
            drill_solo = drill.get("solo_possible").strip().lower() not in {"0", "false", "no", "n"}
            
        drill_equipment = str(drill.get("min_equipment", "Ball only")).lower().strip()
        
        # A. Warmup and Cool Down drills bypass the difficulty filter
        # — a beginner-tagged warmup is appropriate for any level player.
        # Difficulty filtering only applies to main technical content.
        drill_cat = str(drill.get("category", "")).lower().strip()
        is_warmup_or_cooldown = drill_cat in ("warmup", "cool down", "cooldown")

        if not is_warmup_or_cooldown and drill_difficulty not in allowed_difficulties:
            continue
            
        # B. Enforce solo check if no partner available
        if not has_partner and not drill_solo:
            continue
            
        # C. Filter by equipment availability subset
        equipment_ok = True
        if "cones" in drill_equipment:
            if not any("cone" in e for e in equipment_available):
                equipment_ok = False
        if "goal" in drill_equipment:
            if not any("goal" in e for e in equipment_available):
                equipment_ok = False
        if "rebounder" in drill_equipment or "wall" in drill_equipment:
            if not any("rebounder" in e or "wall" in e for e in equipment_available):
                equipment_ok = False
        if "partner" in drill_equipment:
            if not has_partner:
                equipment_ok = False
                
        if not equipment_ok:
            continue
            
        filtered_drills.append(drill)
        
    # Fallback to all drills if our filtering is too restrictive
    if not filtered_drills:
        filtered_drills = list(drills)
        
    # 4. Group drills into buckets
    # Separate cool down drills first — they are only used as session closers
    # when no game application drill is available.
    warmups = []
    cooldowns_pool = []
    main_drills = []
    game_apps = []

    for drill in filtered_drills:
        cat = str(drill.get("category", "")).lower().strip()
        drill_type_val = str(drill.get("drill_type", "")).lower().strip()
        intensity = str(drill.get("intensity", "")).lower().strip()

        # Category field is the primary signal — it was set intentionally
        if cat == "warmup":
            warmups.append(drill)
        elif cat == "cool down" or cat == "cooldown":
            cooldowns_pool.append(drill)
        elif cat == "game application":
            game_apps.append(drill)
        elif drill_type_val == "game application":
            game_apps.append(drill)
        elif drill_type_val == "pressure":
            main_drills.append(drill)
        elif drill_type_val == "isolation":
            # Only isolation drills with intensity medium/high go to main
            # Low-intensity isolations that are NOT warmup category go to main too
            # (e.g. ball mastery technical drills)
            main_drills.append(drill)
        else:
            main_drills.append(drill)

    # Ensure buckets are never empty — fallback gracefully
    if not warmups:
        # Fall back to any low-intensity drill
        warmups = [d for d in filtered_drills
                   if str(d.get("intensity", "")).lower() == "low"] or filtered_drills
    if not main_drills:
        main_drills = [d for d in filtered_drills
                       if str(d.get("category", "")).lower() not in
                       ("warmup", "cool down", "cooldown", "game application")] or filtered_drills
    if not game_apps:
        # Fall back to cooldowns, then high-intensity mains
        game_apps = cooldowns_pool or [
            d for d in filtered_drills
            if str(d.get("intensity", "")).lower() == "high"
        ] or filtered_drills
        
    # 5. Helper function to score and select a drill
    def select_best_drills(candidates: List[dict], count: int, exclude_names: set, preferred_type: Optional[str] = None, preferred_intensity: Optional[str] = None) -> List[dict]:
        scored_candidates = []
        for c in candidates:
            if c.get("drill_name", "") in exclude_names:
                continue
            # Base score
            score = 0.0
            
            # Position scoring — three tiers
            pos_rel_raw = c.get("position_relevance", "")
            pos_rel_parts = []
            if isinstance(pos_rel_raw, list):
                pos_rel_parts = [p.lower().strip() for p in pos_rel_raw if p.strip()]
            elif pos_rel_raw:
                pos_rel_parts = [p.lower().strip() for p in str(pos_rel_raw).split("|") if p.strip()]

            player_pos_lower = [p.lower().strip() for p in [position, secondary_position] if p and p.lower() != "none"]

            if not pos_rel_parts:
                # Universal drill — neutral, slight positive
                score += 1.0
            elif any(p in pos_rel_parts for p in player_pos_lower):
                # Drill explicitly for this player's position — strong boost
                score += 6.0
            else:
                # Drill is for a different specific position — penalty
                score -= 4.0
                
            # Focus area match boost
            c_cat = str(c.get("category", "")).lower()
            c_skill = str(c.get("skill_category", "")).lower()
            c_tags = [t.lower() for t in (c.get("tags") or [])]
            if isinstance(c.get("tags"), str):
                c_tags = [t.lower().strip() for t in c.get("tags").split("|") if t.strip()]
                
            for fa in focus_areas:
                if fa in c_cat or fa in c_skill or any(fa in t for t in c_tags):
                    score += 5.0
                    
            # Preferred type boost
            if preferred_type:
                c_type = str(c.get("drill_type", "")).strip().lower()
                if c_type == preferred_type.strip().lower():
                    score += 10.0
                    
            # Preferred intensity boost
            if preferred_intensity:
                c_intensity = str(c.get("intensity", "")).strip().lower()
                if c_intensity == preferred_intensity.strip().lower():
                    score += 8.0

            # Random slight variance to avoid duplicate plans
            score += random.uniform(0.0, 1.0)
            scored_candidates.append((score, c))
            
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        selected = []
        for _, c in scored_candidates[:count]:
            selected.append(c)
            exclude_names.add(c.get("drill_name", ""))
        return selected

    # 6. Generate the sessions
    sessions = []
    used_drill_names = set()
    
    for day in range(1, sessions_per_week + 1):
        day_warmups = select_best_drills(warmups, 1, used_drill_names, preferred_intensity="low")
        if not day_warmups:
            # Re-allow already used drills if needed
            day_warmups = select_best_drills(warmups, 1, set(), preferred_intensity="low")
            
        # Determine drill count and duration allocations
        # Let's support 20, 30, 45, 60 minutes
        # Round allocations to clean 5-minute increments
        if session_duration <= 20:
            warmup_dur = 5
            main_count = 2
            main_dur = 5
            cool_dur = 5
            include_game_app = False
        elif session_duration <= 30:
            warmup_dur = 5
            main_count = 2
            main_dur = 10
            cool_dur = 5
            include_game_app = False
        elif session_duration <= 45:
            warmup_dur = 5
            main_count = 3
            main_dur = 10
            cool_dur = 10
            include_game_app = True
        elif session_duration <= 60:
            warmup_dur = 10
            main_count = 3
            main_dur = 15
            cool_dur = 5
            include_game_app = True
        elif session_duration <= 75:
            warmup_dur = 10
            main_count = 3
            main_dur = 18
            cool_dur = 11
            include_game_app = True
        elif session_duration <= 90:
            warmup_dur = 15
            main_count = 3
            main_dur = 20
            cool_dur = 15
            include_game_app = True
        else: # 120+ minutes
            warmup_dur = 15
            main_count = 4
            main_dur = 22
            cool_dur = 17
            include_game_app = True
            
        pref_intensity = "medium" if level == "Recreational" else "high"
        pref_type = "Isolation" if day <= 2 else "Pressure"
        day_mains = select_best_drills(main_drills, main_count, used_drill_names, preferred_type=pref_type, preferred_intensity=pref_intensity)
        if len(day_mains) < main_count:
            # Re-allow already used drills
            day_mains += select_best_drills(main_drills, main_count - len(day_mains), set(), preferred_type=pref_type, preferred_intensity=pref_intensity)
            
        day_cools = []
        if include_game_app:
            day_cools = select_best_drills(game_apps, 1, used_drill_names, preferred_intensity="low")
            if not day_cools:
                day_cools = select_best_drills(game_apps, 1, set(), preferred_intensity="low")
        if not day_cools:
            # Fall back to cooldown drills first, then warmup drills
            day_cools = select_best_drills(cooldowns_pool, 1, used_drill_names, preferred_intensity="low")
            if not day_cools:
                day_cools = select_best_drills(cooldowns_pool, 1, set(), preferred_intensity="low")
        if not day_cools:
            day_cools = select_best_drills(warmups, 1, used_drill_names, preferred_intensity="low")
            if not day_cools:
                day_cools = select_best_drills(warmups, 1, set(), preferred_intensity="low")
                
        # Build SessionDrills with allocated times
        session_drills = []
        
        # A. Add Warmup
        if day_warmups:
            wd = day_warmups[0]
            sd = SessionDrill.from_dict({**wd, "allocated_time": warmup_dur, "block_type": "warmup", "block_index": 0})
            session_drills.append(sd.to_dict())
            
        # B. Add Mains
        for idx, md in enumerate(day_mains):
            sd = SessionDrill.from_dict({**md, "allocated_time": main_dur, "block_type": "technical", "block_index": idx + 1})
            session_drills.append(sd.to_dict())
            
        # C. Add Cool Down
        if day_cools:
            cd = day_cools[0]
            sd = SessionDrill.from_dict({**cd, "allocated_time": cool_dur, "block_type": "cooldown", "block_index": len(day_mains) + 1})
            session_drills.append(sd.to_dict())
            
        # Ensure total allocated time equals duration (adjust slightly if needed)
        allocated_total = sum(d["allocated_time"] for d in session_drills)
        diff = session_duration - allocated_total
        if diff != 0 and session_drills:
            # Distribute the difference evenly across technical drills
            technical_drills = [d for d in session_drills if d.get("block_type") == "technical"]
            if technical_drills:
                base_diff = diff // len(technical_drills)
                rem = diff % len(technical_drills)
                for idx, sd in enumerate(technical_drills):
                    sd["allocated_time"] += base_diff
                    if idx < rem:
                        sd["allocated_time"] += 1
            else:
                session_drills[0]["allocated_time"] += diff
                
        sessions.append({
            "day_number": day,
            "name": f"Session {day}: {athlete_profile.get('name', 'Player')}'s Development Plan",
            "duration_minutes": session_duration,
            "drills": session_drills,
            "completed": False,
            "completed_date": None
        })
        
    now_iso = datetime.now().isoformat()
    new_week = {
        "week_number": week_number,
        "generated_date": now_iso,
        "archived_date": None,
        "sessions": sessions,
    }

    if existing_plan and existing_plan.get("weeks"):
        # Archive the outgoing current week
        current_num = existing_plan.get("current_week_number", 1)
        updated_weeks = []
        for w in existing_plan["weeks"]:
            if w.get("week_number") == current_num and w.get("archived_date") is None:
                w = dict(w)  # shallow copy to avoid mutating the original
                w["archived_date"] = now_iso
            updated_weeks.append(w)
        updated_weeks.append(new_week)
        return {
            "current_week_number": week_number,
            "generated_date": now_iso,
            "weeks": updated_weeks,
        }

    # First-ever plan
    return {
        "current_week_number": week_number,
        "generated_date": now_iso,
        "weeks": [new_week],
    }
