import streamlit as st
from typing import Mapping, Any, Optional

import config

FIELD_TYPES = ["Full Field", "Half Field", "Grid", "Penalty Area", "Other"]
DEFAULT_EQUIPMENT = ["Cones", "Balls"]
DEFAULT_POSITIONS = ["GK", "CB", "FB", "WB", "CM", "WM", "AM", "ST", "Winger", "Forward"]
DEFAULT_AGE_GROUPS = ["U8", "U10", "U12", "U14", "U16", "U18", "Adult"]


def _value(source: Optional[Mapping[str, Any]], key: str, default: Any = "") -> Any:
    if source is None:
        return default
    try:
        return source.get(key, default)
    except AttributeError:
        return getattr(source, key, default)


def render_drill_form(
    drill: Optional[Mapping[str, Any]] = None,
    *,
    allow_id_edit: bool = True,
    key_prefix: str = "",
    drill_id_placeholder: str = ""
) -> dict:
    """
    Render the shared drill form and return the collected values.

    Args:
        drill: Existing drill mapping for defaults (dict/pandas Series)
        allow_id_edit: Whether the Drill ID field is editable
        key_prefix: Unique prefix for Streamlit widget keys
        drill_id_placeholder: Placeholder text for the Drill ID input

    Returns:
        dict of field values
    """
    # Row 1: ID, Name
    col1, col2 = st.columns([1, 3])
    drill_id = col1.text_input(
        "Drill ID",
        value=_value(drill, "drill_id", ""),
        placeholder=drill_id_placeholder if allow_id_edit else None,
        disabled=not allow_id_edit,
        key=f"{key_prefix}_drill_id",
    )
    drill_name = col2.text_input(
        "Drill Name",
        value=_value(drill, "drill_name", ""),
        key=f"{key_prefix}_drill_name",
    )

    # Row 2: Category, Duration, Field Type
    category_default = _value(drill, "category", config.CATEGORIES[0])
    if category_default not in config.CATEGORIES:
        category_default = config.CATEGORIES[0]
        
    c1, c2, c3 = st.columns(3)
    category = c1.selectbox(
        "Category",
        options=config.CATEGORIES,
        index=config.CATEGORIES.index(category_default),
        key=f"{key_prefix}_category",
    )
    
    duration = c2.number_input(
        "Duration (min)",
        min_value=1, max_value=90,
        value=int(_value(drill, "duration_minutes", 15) or 15),
        key=f"{key_prefix}_duration",
    )
    
    field_type_value = _value(drill, "field_type", FIELD_TYPES[-1]) or FIELD_TYPES[-1]
    if field_type_value not in FIELD_TYPES:
        field_type_value = FIELD_TYPES[-1]
    field_type = c3.selectbox(
        "Field type",
        options=FIELD_TYPES,
        index=FIELD_TYPES.index(field_type_value),
        key=f"{key_prefix}_field_type",
    )

    # Row 3: Metrics (Players, Difficulty, Intensity)
    m1, m2, m3, m4 = st.columns(4)
    players_min = m1.number_input("Min Players", 1, 30, int(_value(drill, "players_min", 6) or 6), key=f"{key_prefix}_pmin")
    players_max = m2.number_input("Max Players", 1, 30, int(_value(drill, "players_max", 12) or 12), key=f"{key_prefix}_pmax")

    difficulty_default = _value(drill, "difficulty", config.DIFFICULTY_LEVELS[1])
    intensity_default = _value(drill, "intensity", config.INTENSITY_LEVELS[1])
    
    difficulty = m3.selectbox("Difficulty", config.DIFFICULTY_LEVELS, 
                             index=config.DIFFICULTY_LEVELS.index(difficulty_default if difficulty_default in config.DIFFICULTY_LEVELS else config.DIFFICULTY_LEVELS[1]),
                             key=f"{key_prefix}_diff")
    intensity = m4.selectbox("Intensity", config.INTENSITY_LEVELS, 
                            index=config.INTENSITY_LEVELS.index(intensity_default if intensity_default in config.INTENSITY_LEVELS else config.INTENSITY_LEVELS[1]),
                            key=f"{key_prefix}_int")

    # Core Text Areas
    description = st.text_area("Description", value=_value(drill, "description", ""), height=100, key=f"{key_prefix}_desc")
    
    t1, t2 = st.columns(2)
    setup_data = t1.text_area("Setup / Grid", value=_value(drill, "setup_data", ""), height=100, key=f"{key_prefix}_setup")
    coaching_points = t2.text_area("Coaching Points", value=_value(drill, "coaching_points", ""), height=100, key=f"{key_prefix}_cp")

    # Advanced / Details Expander
    with st.expander("Detailed Attributes (Tags, Equipment, Progression, etc.)", expanded=False):
        d1, d2 = st.columns(2)
        
        equipment_defaults = [item.strip() for item in str(_value(drill, "equipment", "") or "").split(",") if item.strip() in config.EQUIPMENT_TYPES]
        equipment = d1.multiselect("Equipment", config.EQUIPMENT_TYPES, default=equipment_defaults or DEFAULT_EQUIPMENT, key=f"{key_prefix}_equip")
        
        tag_defaults = [tag.strip() for tag in str(_value(drill, "tags", "") or "").split("|") if tag.strip()]
        tags = d2.multiselect("Tags", sorted(set(config.DRILL_TAGS).union(tag_defaults)), default=tag_defaults, key=f"{key_prefix}_tags")

        coach_cues = st.text_area("Coach Cues", value=_value(drill, "coach_cues", ""), height=60, key=f"{key_prefix}_cues")
        progression = st.text_area("Progression / Regressions", value=_value(drill, "progression", ""), height=60, key=f"{key_prefix}_prog")

        d3, d4 = st.columns(2)
        pos_defaults = [p.strip() for p in str(_value(drill, "positions", "") or "").split("|") if p.strip()]
        positions = d3.multiselect("Positions", sorted(set(DEFAULT_POSITIONS).union(pos_defaults)), default=pos_defaults, key=f"{key_prefix}_pos")
        
        age_defaults = [a.strip() for a in str(_value(drill, "age_groups", "") or "").split("|") if a.strip()]
        age_groups = d4.multiselect("Age Groups", sorted(set(DEFAULT_AGE_GROUPS).union(age_defaults)), default=age_defaults, key=f"{key_prefix}_ages")

        d5, d6 = st.columns(2)
        recommended_field_size = d5.text_input("Rec. Field Size", value=_value(drill, "recommended_field_size", ""), key=f"{key_prefix}_fsize")
        coach_rating = d6.slider("Personal Rating", 1, 5, int(_value(drill, "coach_rating", 3) or 3), key=f"{key_prefix}_rating")
        
        personal_notes = st.text_area("Personal Notes", value=_value(drill, "personal_notes", ""), height=60, key=f"{key_prefix}_notes")
        
        favorite = st.checkbox(
            "Mark as favorite",
            value=bool(_value(drill, "is_favorite", False)),
            key=f"{key_prefix}_favorite",
        )

    return {
        "drill_id": drill_id.strip(),
        "drill_name": drill_name.strip(),
        "description": description.strip(),
        "setup_data": setup_data.strip(),
        "coaching_points": coaching_points.strip(),
        "duration_minutes": int(duration),
        "field_type": field_type,
        "players_min": int(players_min),
        "players_max": int(players_max),
        "category": category,
        "difficulty": difficulty,
        "intensity": intensity,
        "equipment": equipment,
        "tags": tags,
        "positions": positions,
        "age_groups": age_groups,
        "coach_cues": coach_cues.strip(),
        "progression": progression.strip(),
        "recommended_field_size": recommended_field_size.strip(),
        "coach_rating": int(coach_rating),
        "personal_notes": personal_notes.strip(),
        "is_favorite": favorite,
    }
