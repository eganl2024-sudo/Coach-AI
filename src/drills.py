"""Add missing exports to drills.py"""
import pandas as pd
import streamlit as st
from config import (
    SCORE_DIFFICULTY_MATCH, SCORE_DIFFICULTY_MISMATCH,
    SCORE_RECENCY_LAST_SESSION, SCORE_RECENCY_TWO_SESSIONS,
    SCORE_INTENSITY_MATCH, SCORE_INTENSITY_ONE_OFF, SCORE_INTENSITY_TWO_OFF,
    DIFFICULTY_LEVELS, INTENSITY_LEVELS, CATEGORIES, EQUIPMENT_TYPES
)

# Export constants for use by other modules
DIFFICULTIES = DIFFICULTY_LEVELS
INTENSITIES = INTENSITY_LEVELS


def calculate_drill_score(drill, team_level, recent_usage, target_intensity, selected_categories):
    """
    Calculate score for a drill based on multiple factors.

    Args:
        drill: Drill dictionary with difficulty, intensity, category
        team_level: Team's skill level ('beginner', 'intermediate', 'advanced')
        recent_usage: Dict of {drill_id: sessions_ago}
        target_intensity: Target intensity for this drill position ('low', 'medium', 'high')
        selected_categories: List of categories to include

    Returns:
        tuple: (total_score, breakdown_dict)
    """
    score = 100  # Base score
    breakdown = {'base': 100}

    drill_id = drill.get('drill_id', '')
    drill_difficulty = drill.get('difficulty', 'intermediate')
    drill_intensity = drill.get('intensity', 'medium')
    drill_category = drill.get('category', '')

    # Difficulty match scoring
    if drill_difficulty == team_level:
        score += SCORE_DIFFICULTY_MATCH
        breakdown['difficulty'] = f"+{SCORE_DIFFICULTY_MATCH} (perfect match)"
    else:
        # Check if one level off
        try:
            team_idx = DIFFICULTY_LEVELS.index(team_level)
            drill_idx = DIFFICULTY_LEVELS.index(drill_difficulty)
            if abs(team_idx - drill_idx) == 1:
                score += SCORE_DIFFICULTY_MISMATCH
                breakdown['difficulty'] = f"{SCORE_DIFFICULTY_MISMATCH} (one level off)"
            else:
                score += SCORE_DIFFICULTY_MISMATCH * 2
                breakdown['difficulty'] = f"{SCORE_DIFFICULTY_MISMATCH * 2} (two levels off)"
        except ValueError:
            pass

    # Recency penalty
    if drill_id in recent_usage:
        sessions_ago = recent_usage[drill_id]
        if sessions_ago == 0:
            score += SCORE_RECENCY_LAST_SESSION
            breakdown['recency'] = f"{SCORE_RECENCY_LAST_SESSION} (used last session)"
        elif sessions_ago == 1:
            score += SCORE_RECENCY_TWO_SESSIONS
            breakdown['recency'] = f"{SCORE_RECENCY_TWO_SESSIONS} (used 2 sessions ago)"
        else:
            score += -10
            breakdown['recency'] = f"-10 (used {sessions_ago} sessions ago)"
    else:
        breakdown['recency'] = "+0 (new drill)"

    # Intensity match scoring
    if drill_intensity == target_intensity:
        score += SCORE_INTENSITY_MATCH
        breakdown['intensity'] = f"+{SCORE_INTENSITY_MATCH} (perfect match)"
    else:
        # Check if one level off
        try:
            target_idx = INTENSITY_LEVELS.index(target_intensity)
            drill_idx = INTENSITY_LEVELS.index(drill_intensity)
            if abs(target_idx - drill_idx) == 1:
                score += SCORE_INTENSITY_ONE_OFF
                breakdown['intensity'] = f"{SCORE_INTENSITY_ONE_OFF} (one level off)"
            else:
                score += SCORE_INTENSITY_TWO_OFF
                breakdown['intensity'] = f"{SCORE_INTENSITY_TWO_OFF} (two levels off)"
        except ValueError:
            pass

    # Category bonus (if in selected categories)
    if drill_category in selected_categories:
        breakdown['category'] = "+10 (selected category)"
    else:
        score -= 100  # Heavy penalty for wrong category
        breakdown['category'] = "-100 (excluded category)"

    # Coach rating bonus/penalty
        coach_rating = drill.get('coach_rating', 3)  # Default neutral rating
        if pd.notna(coach_rating):
            coach_rating = int(coach_rating)
            rating_adjustment = (coach_rating - 3) * 10  # 10 per star from neutral
            if rating_adjustment != 0:
                score += rating_adjustment
            stars = '*' * coach_rating
            breakdown['rating'] = f"{rating_adjustment:+d} ({stars})"
        else:
            breakdown['rating'] = "+0 (neutral)"

    breakdown['total'] = score
    return score, breakdown


def score_focus_tags(drill_tags, preferred_tags):
    if not preferred_tags:
        return 0, False
    match = bool(drill_tags.intersection(preferred_tags))
    return (20 if match else 0), match


def score_play_style(drill_details, play_style):
    if not play_style:
        return 0, False
    text = (drill_details.get('description', '') or '').lower()
    match = play_style in text or play_style in drill_details.get('tags', '')
    return (10 if match else 0), match


def score_objective(drill_details, objective_text):
    if not objective_text:
        return 0, False
    text = (drill_details.get('description', '') or '').lower()
    match = objective_text in text or objective_text in drill_details.get('tags', '')
    return (10 if match else 0), match


def score_injuries(drill_details, injuries):
    if not injuries:
        return 0, False
    penalty = -15 if str(drill_details.get('intensity', '')).lower() == 'high' else 0
    return penalty, penalty < 0


def select_best_drill(
    candidates,
    team_level,
    recent_usage,
    target_intensity,
    selected_categories,
    preferred_tags=None,
    play_style="",
    objective_text="",
    injuries=None
):
    """
    Select the best drill from candidates based on scoring.

    Args:
        candidates: List of drill dictionaries
        team_level: Team's skill level
        recent_usage: Dict of recent drill usage
        target_intensity: Target intensity for this position
        selected_categories: List of categories to include

    Returns:
        dict: Best scoring drill with _score and _score_breakdown added
    """
    if candidates.empty:
        return None

    best_drill = None
    best_score = -999999

    preferred_tags = {tag.lower() for tag in preferred_tags or set()}
    play_style = (play_style or "").lower()
    objective_text = (objective_text or "").lower()
    injuries = injuries or []

    for _, drill in candidates.iterrows():
        score, breakdown = calculate_drill_score(
            drill, team_level, recent_usage, target_intensity, selected_categories
        )

        drill_tags = {
            tag.strip().lower()
            for tag in str(drill.get('tags', '')).split("|")
            if tag.strip()
        }

        profile_focus_match = bool(preferred_tags and drill_tags.intersection(preferred_tags))
        profile_playstyle_match = bool(
            play_style and (
                play_style in drill_tags or play_style in str(drill.get('description', '')).lower()
            )
        )
        profile_objective_match = bool(
            objective_text and (
                objective_text in drill_tags or objective_text in str(drill.get('description', '')).lower()
            )
        )
        profile_injury_penalty = bool(
            injuries and str(drill.get('intensity', '')).lower() == 'high'
        )

        if profile_focus_match:
            score += 20
        if profile_playstyle_match:
            score += 10
        if profile_objective_match:
            score += 10
        if profile_injury_penalty:
            score -= 15

        focus_bonus, focus_match = score_focus_tags(drill_tags, preferred_tags)
        score += focus_bonus
        playstyle_bonus, play_match = score_play_style(drill, play_style)
        score += playstyle_bonus
        objective_bonus, obj_match = score_objective(drill, objective_text)
        score += objective_bonus
        injury_penalty, injury_match = score_injuries(drill, injuries)
        score += injury_penalty

        if score > best_score:
            best_score = score
            best_drill = drill.copy()
            best_drill['_score'] = score
            best_drill['_score_breakdown'] = breakdown
            best_drill['_profile_focus_match'] = focus_match
            best_drill['_profile_playstyle_match'] = play_match
            best_drill['_profile_objective_match'] = obj_match
            best_drill['_profile_injury_penalty'] = injury_match

    return best_drill


def define_balanced_intensity_curve(num_drills):
    """
    Define balanced intensity progression for practice drills.

    Pattern: low  medium  high  medium  low

    Args:
        num_drills: Number of drills in the practice

    Returns:
        list: Intensity targets for each drill position
    """
    if num_drills <= 1:
        return ['medium']
    elif num_drills == 2:
        return ['low', 'low']
    elif num_drills == 3:
        return ['low', 'medium', 'low']
    elif num_drills == 4:
        return ['low', 'medium', 'medium', 'low']
    elif num_drills == 5:
        return ['low', 'medium', 'high', 'medium', 'low']
    else:
        # For longer practices, expand the pattern
        curve = ['low']
        remaining = num_drills - 2  # Start and end are 'low'

        # Build up phase
        for i in range(remaining // 2):
            if i % 2 == 0:
                curve.append('medium')
            else:
                curve.append('high')

        # Add peak
        if remaining % 2 == 1:
            curve.append('high')

        # Wind down phase (mirror of build up)
        wind_down = curve[1:-1][::-1]
        curve.extend(wind_down)
        curve.append('low')

        # Ensure the curve matches requested length
        while len(curve) < num_drills:
            curve.append('low')
        return curve[:num_drills]


def validate_drill_on_submit(drill_data):
    """
    Validate drill data before saving.

    Args:
        drill_data: Dict with drill fields

    Returns:
        dict: {field_name: error_message} or empty dict if valid
    """
    errors = {}

    # Required fields
    if not drill_data.get('drill_id', '').strip():
        errors['drill_id'] = "Drill ID is required"

    if not drill_data.get('drill_name', '').strip():
        errors['drill_name'] = "Drill name is required"

    if not drill_data.get('category'):
        errors['category'] = "Category is required"
    elif drill_data['category'] not in CATEGORIES:
        errors['category'] = f"Must be one of: {', '.join(CATEGORIES)}"

    # Numeric validations
    try:
        players_min = int(drill_data.get('players_min', 0))
        if players_min < 1:
            errors['players_min'] = "Must be at least 1"
    except (ValueError, TypeError):
        errors['players_min'] = "Must be a number"

    try:
        players_max = int(drill_data.get('players_max', 0))
        if players_max < 1:
            errors['players_max'] = "Must be at least 1"
        elif 'players_min' not in errors:
            if players_max < players_min:
                errors['players_max'] = "Must be >= players_min"
    except (ValueError, TypeError):
        errors['players_max'] = "Must be a number"

    try:
        duration = int(drill_data.get('duration_minutes', 0))
        if duration < 1:
            errors['duration_minutes'] = "Must be at least 1 minute"
    except (ValueError, TypeError):
        errors['duration_minutes'] = "Must be a number"

    # Difficulty validation
    if drill_data.get('difficulty') not in DIFFICULTY_LEVELS:
        errors['difficulty'] = f"Must be one of: {', '.join(DIFFICULTY_LEVELS)}"

    # Intensity validation
    if drill_data.get('intensity') not in INTENSITY_LEVELS:
        errors['intensity'] = f"Must be one of: {', '.join(INTENSITY_LEVELS)}"

    # Coach rating validation (if provided)
    if drill_data.get('coach_rating'):
        try:
            rating = int(drill_data['coach_rating'])
            if rating < 1 or rating > 5:
                errors['coach_rating'] = "Must be 1-5 stars"
        except (ValueError, TypeError):
            errors['coach_rating'] = "Must be a number (1-5)"

    return errors


def check_duplicate_id(drill_id, existing_drills_df):
    """
    Check if drill ID already exists.

    Args:
        drill_id: Drill ID to check
        existing_drills_df: DataFrame of existing drills

    Returns:
        bool: True if duplicate exists
    """
    if existing_drills_df is None or len(existing_drills_df) == 0:
        return False

    return drill_id in existing_drills_df['drill_id'].values


def suggest_next_drill_id(existing_drills_df, category='Technical'):
    """
    Suggest next drill ID for a category.

    Format: {CATEGORY_PREFIX}_{NUMBER}
    Example: TECH_032, WARM_015

    Args:
        existing_drills_df: DataFrame of existing drills
        category: Drill category (optional, defaults to Technical)

    Returns:
        str: Suggested drill ID
    """
    # Category prefixes
    category_prefixes = {
        'Warmup': 'WARM',
        'Technical': 'TECH',
        'Tactical': 'TACT',
        'Small Sided Games': 'SSG',
        'Conditioning': 'COND',
        'Cool Down': 'COOL'
    }

    prefix = category_prefixes.get(category, 'DRILL')

    # Find highest number for this prefix
    max_num = 0
    if existing_drills_df is not None and len(existing_drills_df) > 0:
        category_drills = existing_drills_df[
            existing_drills_df['drill_id'].str.startswith(prefix, na=False)
        ]

        for drill_id in category_drills['drill_id']:
            try:
                # Extract number from ID (e.g., TECH_032 -> 32)
                num_str = drill_id.split('_')[-1]
                num = int(num_str)
                max_num = max(max_num, num)
            except (ValueError, IndexError):
                pass

    # Suggest next number
    next_num = max_num + 1
    return f"{prefix}_{next_num:03d}"


print("Drill management module created")


def validate_drill_schema(drill: dict):
    """
    Validate richer drill metadata before persisting or using in generators.

    Checks required fields, duration integrity, and list-typed attributes.
    Raises a friendly Streamlit error and ValueError when invalid.
    """
    errors = []
    required_fields = {
        "drill_id": "Drill ID",
        "drill_name": "Drill name",
        "category": "Category",
        "duration_minutes": "Duration (minutes)",
    }
    for key, label in required_fields.items():
        value = drill.get(key)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append(f"{label} is required.")

    # Duration must be an integer >= 1
    duration = drill.get("duration_minutes")
    try:
        duration_int = int(duration)
        if duration_int < 1:
            errors.append("Duration must be at least 1 minute.")
    except (TypeError, ValueError):
        errors.append("Duration must be a whole number.")

    # Optional list fields
    if "positions" in drill and drill.get("positions") not in (None, "", []):
        if not isinstance(drill.get("positions"), (list, tuple)):
            errors.append("Positions must be a list.")
    if "age_groups" in drill and drill.get("age_groups") not in (None, "", []):
        if not isinstance(drill.get("age_groups"), (list, tuple)):
            errors.append("Age groups must be a list.")
    if "focus_attributes" in drill and drill.get("focus_attributes") not in (None, "", []):
        if not isinstance(drill.get("focus_attributes"), list):
            errors.append("Focus attributes must be provided as a list.")

    # Optional text fields sanity
    for key, label in {"coach_cues": "Coach cues", "progression": "Progression"}.items():
        value = drill.get(key)
        if value is not None and not isinstance(value, (str, float, int)):
            errors.append(f"{label} must be text.")

    if errors:
        message = " ".join(errors)
        try:
            st.error(message)
        except Exception:
            pass
        raise ValueError(message)

    return True
