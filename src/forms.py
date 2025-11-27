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
    col1, col2 = st.columns(2)
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

    description = st.text_area(
        "Description",
        value=_value(drill, "description", ""),
        height=100,
        key=f"{key_prefix}_description",
    )
    setup_data = st.text_area(
        "Setup / grid info",
        value=_value(drill, "setup_data", ""),
        height=100,
        key=f"{key_prefix}_setup",
    )
    coaching_points = st.text_area(
        "Coaching points",
        value=_value(drill, "coaching_points", ""),
        height=80,
        key=f"{key_prefix}_coaching",
    )
    coach_cues = st.text_area(
        "Coach cues (quick reminders)",
        value=_value(drill, "coach_cues", ""),
        height=60,
        key=f"{key_prefix}_coach_cues",
    )
    progression = st.text_area(
        "Progression / regressions",
        value=_value(drill, "progression", ""),
        height=60,
        key=f"{key_prefix}_progression",
    )

    col3, col4 = st.columns(2)
    duration = col3.number_input(
        "Duration (minutes)",
        min_value=1,
        max_value=90,
        value=int(_value(drill, "duration_minutes", 15) or 15),
        key=f"{key_prefix}_duration",
    )
    field_type_value = _value(drill, "field_type", FIELD_TYPES[-1]) or FIELD_TYPES[-1]
    if field_type_value not in FIELD_TYPES:
        field_type_value = FIELD_TYPES[-1]
    field_type = col4.selectbox(
        "Field type",
        options=FIELD_TYPES,
        index=FIELD_TYPES.index(field_type_value),
        key=f"{key_prefix}_field_type",
    )

    col5, col6 = st.columns(2)
    players_min = col5.number_input(
        "Min players",
        min_value=1,
        max_value=30,
        value=int(_value(drill, "players_min", 6) or 6),
        key=f"{key_prefix}_players_min",
    )
    players_max = col6.number_input(
        "Max players",
        min_value=1,
        max_value=30,
        value=int(_value(drill, "players_max", 12) or 12),
        key=f"{key_prefix}_players_max",
    )

    category_default = _value(drill, "category", config.CATEGORIES[0])
    if category_default not in config.CATEGORIES:
        category_default = config.CATEGORIES[0]
    category = st.selectbox(
        "Category",
        options=config.CATEGORIES,
        index=config.CATEGORIES.index(category_default),
        key=f"{key_prefix}_category",
    )

    col7, col8 = st.columns(2)
    difficulty_default = _value(drill, "difficulty", config.DIFFICULTY_LEVELS[1])
    if difficulty_default not in config.DIFFICULTY_LEVELS:
        difficulty_default = config.DIFFICULTY_LEVELS[1]
    intensity_default = _value(drill, "intensity", config.INTENSITY_LEVELS[1])
    if intensity_default not in config.INTENSITY_LEVELS:
        intensity_default = config.INTENSITY_LEVELS[1]
    difficulty = col7.selectbox(
        "Difficulty",
        options=config.DIFFICULTY_LEVELS,
        index=config.DIFFICULTY_LEVELS.index(difficulty_default),
        key=f"{key_prefix}_difficulty",
    )
    intensity = col8.selectbox(
        "Intensity",
        options=config.INTENSITY_LEVELS,
        index=config.INTENSITY_LEVELS.index(intensity_default),
        key=f"{key_prefix}_intensity",
    )

    equipment_defaults = [
        item.strip()
        for item in str(_value(drill, "equipment", "") or "").split(",")
        if item.strip() and item.strip() in config.EQUIPMENT_TYPES
    ]
    if not equipment_defaults:
        equipment_defaults = DEFAULT_EQUIPMENT
    equipment = st.multiselect(
        "Equipment",
        options=config.EQUIPMENT_TYPES,
        default=equipment_defaults,
        key=f"{key_prefix}_equipment",
    )

    tag_defaults = [
        tag.strip() for tag in str(_value(drill, "tags", "") or "").split("|") if tag.strip()
    ]
    tags = st.multiselect(
        "Tags",
        options=sorted(set(config.DRILL_TAGS).union(tag_defaults)),
        default=tag_defaults,
        key=f"{key_prefix}_tags",
    )

    position_defaults = [
        pos.strip() for pos in str(_value(drill, "positions", "") or "").split("|") if pos.strip()
    ]
    positions = st.multiselect(
        "Positions/lines emphasized",
        options=sorted(set(DEFAULT_POSITIONS).union(position_defaults)),
        default=position_defaults,
        key=f"{key_prefix}_positions",
    )

    age_group_defaults = [
        age.strip() for age in str(_value(drill, "age_groups", "") or "").split("|") if age.strip()
    ]
    age_groups = st.multiselect(
        "Recommended age groups",
        options=sorted(set(DEFAULT_AGE_GROUPS).union(age_group_defaults)),
        default=age_group_defaults,
        key=f"{key_prefix}_age_groups",
    )

    recommended_field_size = st.text_input(
        "Recommended field size",
        value=_value(drill, "recommended_field_size", ""),
        placeholder="e.g., 30x20 yards grid",
        key=f"{key_prefix}_field_size",
    )

    coach_rating = st.slider(
        "Coach rating",
        min_value=1,
        max_value=5,
        value=int(_value(drill, "coach_rating", 3) or 3),
        key=f"{key_prefix}_rating",
    )
    personal_notes = st.text_area(
        "Personal notes",
        value=_value(drill, "personal_notes", ""),
        height=60,
        key=f"{key_prefix}_notes",
    )
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
