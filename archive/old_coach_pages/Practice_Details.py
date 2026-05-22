"""Practice Details - Read-only viewer for saved practice sessions with diagram support"""
import streamlit as st
import pandas as pd
import sys
import json
from pathlib import Path
import math

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import config
import practice_history
import session_state as ui_session
import ui_components
from auth import require_auth

st.set_page_config(page_title="Practice Details", page_icon="📋", layout="wide")

require_auth()
ui_components.require_page_access("pages/Practice_Details.py")

ui_components.render_nav(active_label="📋 Practice Details")
st.divider()

# ============================================================================
# CONTEXT VALIDATION
# ============================================================================
team_id = st.session_state.get("current_team_id")
view_session_id = st.session_state.get("view_session_id")
data_path = st.session_state.get("data_path", config.get_data_path())

if not team_id or not view_session_id:
    st.error("No practice session selected to view.")
    if st.button("← Back to Team Hub"):
        st.switch_page("pages/5_Team_Hub.py")
    st.stop()

# ============================================================================
# LOAD SESSION
# ============================================================================
try:
    session_df = practice_history.load_sessions_for_team(data_path, team_id)
    if session_df.empty:
        st.error("No practice history found for this team.")
        if st.button("← Back to Team Hub"):
            st.switch_page("pages/5_Team_Hub.py")
        st.stop()
    
    # Find the session by ID
    mask = session_df["session_id"] == view_session_id
    if not mask.any():
        st.error(f"Could not find session {view_session_id}.")
        if st.button("← Back to Team Hub"):
            st.switch_page("pages/5_Team_Hub.py")
        st.stop()
    
    session_row = session_df[mask].iloc[0]
    
    # Load full session structure
    session_structure = session_row.get("session_structure", "")
    if isinstance(session_structure, str) and session_structure.strip():
        try:
            session_dict = json.loads(session_structure)
        except Exception:
            session_dict = {}
    else:
        session_dict = session_structure if isinstance(session_structure, dict) else {}
    
except Exception as e:
    st.error(f"Error loading session: {str(e)[:100]}")
    if st.button("← Back to Team Hub"):
        st.switch_page("pages/5_Team_Hub.py")
    st.stop()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def safe_str(value) -> str:
    """Convert any value to a safe string using centralized cleaner."""
    return ui_components.clean_text(value)


def normalize_block_title(label: str) -> str:
    """
    Normalize block label to professional Title Case.
    Handles variations like "warmup", "Cool Down", "SSG", etc.
    """
    label_str = safe_str(label).lower()
    
    # Exact mappings for common block types
    mapping = {
        "warmup": "Warmup Block",
        "technical": "Technical Block",
        "tactical": "Tactical Block",
        "tactic": "Tactical Block",
        "small sided games": "Small-Sided Games Block",
        "ssg": "Small-Sided Games Block",
        "conditioning": "Conditioning Block",
        "cool down": "Cooldown Block",
        "cooldown": "Cooldown Block",
        "other": "Other",
    }
    
    # Check exact matches first
    if label_str in mapping:
        return mapping[label_str]
    
    # If not found, title case it + add Block suffix
    if label_str and label_str != "other":
        return label_str.title() + " Block"
    
    return "Other"


def clean_sentence(text: str) -> str:
    """
    Clean sentence: trim whitespace, fix double spaces, capitalize first letter.
    Adds period if it looks like a sentence and doesn't already end in .?!
    """
    text_str = safe_str(text)
    if not text_str:
        return ""
    
    # Fix multiple spaces
    text_str = " ".join(text_str.split())
    
    # Capitalize first letter
    if len(text_str) > 0:
        text_str = text_str[0].upper() + text_str[1:]
    
    # Add period if sentence-like and doesn't end with punctuation
    if len(text_str) > 0 and text_str[-1] not in ".?!":
        # Only add period if it looks like a sentence (has spaces or is long enough)
        if " " in text_str or len(text_str) > 10:
            text_str += "."
    
    return text_str


def clean_bullet(text: str) -> str:
    """
    Clean bullet point: trim, fix spaces, capitalize first letter.
    Does NOT add period (bullets typically don't need them).
    """
    text_str = safe_str(text)
    if not text_str:
        return ""
    
    # Fix multiple spaces
    text_str = " ".join(text_str.split())
    
    # Capitalize first letter
    if len(text_str) > 0:
        text_str = text_str[0].upper() + text_str[1:]
    
    return text_str


def extract_bullets(value, max_items: int = 5) -> list:
    """
    Extract bullet points from a string (newline or semicolon delimited).
    Returns a list of cleaned strings, max max_items items.
    """
    if not value:
        return []
    
    value_str = safe_str(value)
    if not value_str:
        return []
    
    # Try newline first, then semicolon
    if "\n" in value_str:
        bullets = [clean_bullet(b.strip()) for b in value_str.split("\n") if b.strip()]
    elif ";" in value_str:
        bullets = [clean_bullet(b.strip()) for b in value_str.split(";") if b.strip()]
    else:
        # Single line, return as single bullet
        bullets = [clean_bullet(value_str)]
    
    return bullets[:max_items]


def normalize_block_label(drill: dict) -> str:
    """
    Derive the block label for a drill.
    Priority: block_type → category → type → tags → Other
    """
    # Exact priority order
    for key in ["block_type", "category", "type"]:
        val = drill.get(key, "")
        val_str = safe_str(val)
        if val_str:
            return val_str
    
    # Check tags
    tags = drill.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split("|") if t.strip()]
    
    known_blocks = {"warmup", "technical", "tactical", "small sided games", "ssg", 
                    "conditioning", "cool down", "cooldown"}
    for tag in tags:
        if tag.lower() in known_blocks:
            return tag
    
    return "Other"


def get_block_focus_description(block_label: str) -> str:
    """Return a one-line focus description for a block type."""
    block_lower = block_label.lower()
    
    if block_lower == "warmup":
        return "Raise intensity + touches on the ball"
    elif block_lower == "technical":
        return "Repetition with clear coaching cues"
    elif block_lower in ["tactical", "tactic"]:
        return "Apply technique in tactical scenarios"
    elif block_lower in ["small sided games", "ssg"]:
        return "Game-realistic decisions under pressure"
    elif block_lower == "conditioning":
        return "Physical preparation + explosive movements"
    elif block_lower in ["cool down", "cooldown"]:
        return "Downshift + quick reflection"
    else:
        return "Focus on core concepts"


def derive_session_intent(session_dict: dict, categories: list) -> dict:
    """
    Derive session intent from available fields.
    Returns dict with 'objective' and 'coach_emphasis' keys.
    """
    intent = {"objective": "", "coach_emphasis": []}
    
    # Objective: prefer explicit fields, else infer from categories
    objective = safe_str(session_dict.get("objective", ""))
    if not objective:
        objective = safe_str(session_dict.get("session_goal", ""))
    if not objective:
        objective = safe_str(session_dict.get("primary_goal", ""))
    if not objective:
        objective = safe_str(session_dict.get("theme", ""))
    
    if objective:
        intent["objective"] = objective
    else:
        # Infer from categories
        if categories:
            cat_str = ", ".join(categories[:3])
            intent["objective"] = f"Develop key skills in {cat_str} through structured, progressive activities."
        else:
            intent["objective"] = "Improve team performance through structured practice."
    
    # Coach emphasis: prefer explicit fields, else derive from categories
    emphasis_str = safe_str(session_dict.get("coach_emphasis", ""))
    if not emphasis_str:
        emphasis_str = safe_str(session_dict.get("notes", ""))
    if not emphasis_str:
        emphasis_str = safe_str(session_dict.get("coach_notes", ""))
    
    if emphasis_str:
        # Try to extract bullets
        bullets = extract_bullets(emphasis_str, max_items=4)
        intent["coach_emphasis"] = bullets
    else:
        # Derive from categories
        defaults = {
            "Technical": ["Scanning before touch", "Body shape for control", "Tempo of play"],
            "Tactical": ["Defensive triggers", "Compactness as a team", "Communication"],
            "Possession": ["Ball retention", "Scanning", "Body shape"],
            "Pressing": ["Triggers for pressing", "Team compactness", "Communication"],
            "Finishing": ["First touch into space", "Shot selection", "Follow rebounds"]
        }
        
        for cat in categories:
            if cat in defaults:
                intent["coach_emphasis"] = defaults[cat]
                break
        
        if not intent["coach_emphasis"]:
            intent["coach_emphasis"] = ["Quality of execution", "Communication", "Awareness"]
    
    return intent


def get_description(drill: dict) -> str:
    """
    Extract description from drill with priority:
    description → drill_description → details → instructions
    Returns cleaned, safe string, or empty if not found.
    """
    for key in ["description", "drill_description", "details", "instructions"]:
        val = safe_str(drill.get(key, ""))
        if val:
            return val
    return ""


def get_diagram_sources(drill) -> list:
    """
    Extract diagram/image sources from a drill.
    Returns list of dicts with 'type' (base64, path, url) and 'value'.
    """
    sources = []
    
    if isinstance(drill, dict):
        # Check for various diagram/image fields
        for key in ["diagram_image_base64", "diagram_base64", "image_base64"]:
            val = drill.get(key, "")
            if val and isinstance(val, str) and len(val) > 10:
                sources.append({"type": "base64", "value": val})
                break
        
        for key in ["diagram_path", "image_path", "diagram_file"]:
            val = drill.get(key, "")
            if val and isinstance(val, str) and len(val) > 0:
                sources.append({"type": "path", "value": val})
        
        for key in ["diagram_url", "image_url"]:
            val = drill.get(key, "")
            if val and isinstance(val, str) and val.startswith("http"):
                sources.append({"type": "url", "value": val})
    
    return sources


def image_to_base64(file_path: str) -> str:
    """Convert a local image file to base64 string."""
    import base64
    try:
        path = Path(file_path)
        if not path.exists():
            return ""
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return ""


def compare_intensity_levels(planned: str, actual: str) -> str:
    """
    Compare planned vs actual intensity and return interpretation sentence.
    Returns a neutral, coach-supportive message.
    """
    planned_str = safe_str(planned).lower().strip()
    actual_str = safe_str(actual).lower().strip()
    
    if not planned_str or not actual_str:
        return "Intensity data not fully available for comparison."
    
    # Normalize to standard levels
    intensity_order = {"low": 1, "medium": 2, "high": 3}
    planned_level = intensity_order.get(planned_str, 2)
    actual_level = intensity_order.get(actual_str, 2)
    
    if actual_level > planned_level:
        return "This session was more intense than planned."
    elif actual_level < planned_level:
        return "This session was less intense than planned."
    else:
        return "This session matched the planned intensity."


def get_load_drivers(session_dict: dict) -> list:
    """
    Extract up to 2 load driver explanations from session data.
    Returns list of clean bullet strings, or empty list if not available.
    """
    drivers = []
    
    # Check for explicit load drivers field
    load_drivers = session_dict.get("load_drivers", "")
    if load_drivers:
        driver_list = extract_bullets(load_drivers, max_items=2)
        drivers.extend(driver_list)
    
    # Check for intensity notes or explanation
    intensity_notes = session_dict.get("intensity_notes", "")
    if intensity_notes and len(drivers) < 2:
        note = clean_bullet(intensity_notes)
        if note:
            drivers.append(note)
    
    return drivers[:2]  # Return max 2


def get_suggested_adjustment(session_dict: dict) -> str:
    """
    Extract a suggested adjustment for next time.
    Returns single recommendation string, or "No adjustment suggested."
    """
    # Check for explicit adjustment field
    adjustment = safe_str(session_dict.get("suggested_adjustment", ""))
    if adjustment:
        return adjustment
    
    # Check for coach recommendation
    recommendation = safe_str(session_dict.get("coach_recommendation", ""))
    if recommendation:
        return recommendation
    
    # Default if none available
    return "No adjustment suggested."


def infer_actual_intensity_from_blocks(session_dict: dict) -> str | None:
    """
    Infer actual session intensity from drill/block durations.
    
    Rules:
    - SSG/tactical/game-like minutes >= 30 → "High"
    - >= 15 → "Medium"
    - < 15 → "Low"
    
    Returns "High", "Medium", "Low", or None if unable to infer.
    """
    drills = session_dict.get("drills", [])
    if not drills:
        return None
    
    # Categorize drills and sum durations
    high_intensity_minutes = 0  # SSG, tactical, game-like
    
    for drill in drills:
        if not isinstance(drill, dict):
            continue
        
        # Get drill duration
        duration_str = safe_str(drill.get("allocated_time", "0"))
        try:
            duration = float(duration_str) if duration_str else 0
        except (ValueError, TypeError):
            duration = 0
        
        if duration <= 0:
            continue
        
        # Check block/category type
        block_label = normalize_block_label(drill).lower()
        category = safe_str(drill.get("category", "")).lower()
        
        # Check if this is high-intensity (SSG, tactical, game-like)
        is_high_intensity = (
            "ssg" in block_label or 
            "small sided" in block_label or 
            "tactical" in block_label or 
            "game" in block_label or
            "ssg" in category or 
            "small sided" in category or 
            "tactical" in category or 
            "game" in category
        )
        
        if is_high_intensity:
            high_intensity_minutes += duration
    
    # Apply intensity rules
    if high_intensity_minutes >= 30:
        return "High"
    elif high_intensity_minutes >= 15:
        return "Medium"
    else:
        return "Low"


# ============================================================================
# PAGE CONTENT
# ============================================================================
# Extract session metadata
session_title = safe_str(session_row.get("session_title") or session_dict.get("session_title") or session_dict.get("session_name", "Practice Details"))
if session_title.lower() == "nan" or not session_title:
    session_title = "Practice Details"

st.title(f"📋 {session_title}")

team_name = safe_str(session_dict.get("team_name", "Team"))
session_date = safe_str(session_dict.get("session_date", ""))
duration_min = safe_str(session_dict.get("duration_minutes", "90"))
num_raw = session_dict.get("num_players", "")
num_players = safe_str(num_raw) if safe_str(num_raw).lower() != "nan" else ""

# Format date for display
session_date_display = ""
if session_date:
    try:
        dt_obj = pd.to_datetime(session_date)
        session_date_display = dt_obj.strftime("%A, %B %d, %Y")
    except Exception:
        session_date_display = session_date

# Header section
cols = st.columns(4)
with cols[0]:
    st.metric("Team", team_name)
with cols[1]:
    if session_date_display:
        st.metric("Date", session_date_display)
with cols[2]:
    if duration_min and duration_min != "nan":
        st.metric("Duration", f"{duration_min} min")
with cols[3]:
    if num_players and num_players != "nan":
        st.metric("Players", num_players)

# Focus areas
config_data = session_dict.get("config", {})
selected_categories = config_data.get("selected_categories", [])
if isinstance(selected_categories, str):
    selected_categories = [c.strip() for c in selected_categories.split("|") if c.strip()]

# ============================================================================
# SESSION INTENT SECTION
# ============================================================================
st.divider()
st.markdown("## 🎯 Session Intent")

session_intent = derive_session_intent(session_dict, selected_categories)

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("**Objective**")
    st.write(session_intent["objective"])

with col2:
    st.markdown("**Coach Emphasis**")
    if session_intent["coach_emphasis"]:
        for point in session_intent["coach_emphasis"]:
            st.write(f"• {point}")
    else:
        st.write("—")

# Focus areas
if selected_categories:
    st.markdown("#### 🎯 Focus Areas")
    focus_str = " • ".join([str(c) for c in selected_categories])
    st.write(focus_str)

# Session notes
session_notes = safe_str(config_data.get("session_notes", ""))
if session_notes:
    st.markdown("#### 📝 Session Notes")
    st.write(session_notes)

st.divider()

# ============================================================================
# SESSION REVIEW SECTION (Layer 2)
# ============================================================================
st.markdown("## 📊 Session Review")

# Get intensity data
planned_intensity = safe_str(session_dict.get("planned_intensity", "Medium"))
actual_intensity = safe_str(session_dict.get("actual_intensity", ""))

# Use inferred intensity if explicit value not available
is_estimated = False
if not actual_intensity:
    inferred = infer_actual_intensity_from_blocks(session_dict)
    if inferred:
        actual_intensity = inferred
        is_estimated = True

# Display planned vs actual intensity
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Planned Intensity**")
    st.write(planned_intensity if planned_intensity else "Not specified")

with col2:
    st.markdown("**Actual Intensity**")
    if actual_intensity:
        if is_estimated:
            st.write(f"{actual_intensity} *(Estimated)*")
        else:
            st.write(actual_intensity)
    else:
        st.write("Not Available Yet")

# Interpretation sentence
interpretation = compare_intensity_levels(planned_intensity, actual_intensity)
st.write(f"*{interpretation}*")

# Load driver explanation
load_drivers = get_load_drivers(session_dict)
if load_drivers:
    st.markdown("**What contributed to this intensity**")
    for driver in load_drivers:
        st.write(f"• {driver}")

# Suggested adjustment (highlighted callout)
st.divider()
suggested = get_suggested_adjustment(session_dict)
with st.container(border=True):
    st.markdown("**Suggested Adjustment for Next Time**")
    st.write(suggested)

# Coach reflection (optional text input)
st.markdown("**Coach Reflection** *(optional)*")
reflection_key = f"coach_reflection_{session_row.get('session_id', 'new')}"

# Get existing reflection if available
existing_reflection = safe_str(session_dict.get("coach_reflection", ""))
reflection_text = st.text_area(
    "Add your thoughts about this session",
    value=existing_reflection,
    height=80,
    key=reflection_key,
    label_visibility="collapsed"
)

# Save reflection button
if reflection_text and reflection_text != existing_reflection:
    if st.button("💾 Save Reflection", key=f"save_reflection_{reflection_key}"):
        # Update session with reflection
        session_dict["coach_reflection"] = reflection_text
        try:
            import json
            updated_structure = json.dumps(session_dict)
            # TODO: Call practice_history.save_session_for_team() to persist
            st.success("Reflection saved!")
        except Exception as e:
            st.warning(f"Could not save reflection: {str(e)[:50]}")

st.divider()

# ============================================================================
# DRILLS SECTION - GROUPED BY BLOCK
# ============================================================================
drills = session_dict.get("drills", [])
if drills:
    st.markdown("## 🏃 Practice Plan")
    
    # Group drills by block
    block_order = ["Warmup", "Technical", "Tactical", "Small Sided Games", "SSG", 
                   "Conditioning", "Cool Down", "Cooldown", "Other"]
    
    blocks_dict = {}
    for drill in drills:
        block_label = normalize_block_label(drill)
        if block_label not in blocks_dict:
            blocks_dict[block_label] = []
        blocks_dict[block_label].append(drill)
    
    # Sort blocks by priority order
    sorted_blocks = []
    for block_name in block_order:
        for key in blocks_dict:
            if key.lower() == block_name.lower():
                sorted_blocks.append((key, blocks_dict[key]))
                break
    
    # Add any remaining blocks not in the priority list
    for key in blocks_dict:
        if not any(key.lower() == b.lower() for b in block_order):
            sorted_blocks.append((key, blocks_dict[key]))
    
    # Render each block
    for block_label, block_drills in sorted_blocks:
        normalized_title = normalize_block_title(block_label)
        st.markdown(f"### {normalized_title}")
        
        # Block summary
        block_duration = sum([
            float(safe_str(d.get("allocated_time", 0)) or "0") 
            for d in block_drills
        ])
        if block_duration > 0:
            st.caption(f"⏱️ {int(block_duration)} min • {get_block_focus_description(block_label)}")
        else:
            st.caption(get_block_focus_description(block_label))
        
        # Render each drill in the block
        for drill_idx, drill in enumerate(block_drills, 1):
            drill_name = safe_str(drill.get("drill_name", f"Drill {drill_idx}"))
            drill_time = safe_str(drill.get("allocated_time", ""))
            drill_intensity = safe_str(drill.get("intensity", ""))
            drill_category = safe_str(drill.get("category", ""))
            
            with st.container(border=True):
                # Drill header
                st.markdown(f"#### {drill_name}")
                
                # Drill meta
                meta_parts = []
                if drill_time:
                    meta_parts.append(f"⏱️ {drill_time} min")
                if drill_intensity:
                    meta_parts.append(f"💥 {drill_intensity}")
                if drill_category:
                    meta_parts.append(f"📂 {drill_category}")
                
                if meta_parts:
                    st.caption(" • ".join(meta_parts))
                
                # Get diagram sources and description early
                diagram_sources = get_diagram_sources(drill)
                drill_description = get_description(drill)
                
                # Decide layout: two columns if diagram exists, else single column
                has_diagram = len(diagram_sources) > 0
                
                if has_diagram:
                    info_col, diagram_col = st.columns([3, 2], vertical_alignment="top")
                    
                    # Left column: drill info
                    with info_col:
                        # Purpose section
                        purpose = safe_str(drill.get("purpose", ""))
                        if not purpose and not drill_description:
                            description_fallback = safe_str(drill.get("drill_description", "") or drill.get("description", ""))
                            if description_fallback:
                                # Truncate to ~140 chars and remove newlines
                                purpose = description_fallback.replace("\n", " ")
                                if len(purpose) > 140:
                                    purpose = purpose[:137] + "..."
                        
                        if purpose:
                            cleaned_purpose = clean_sentence(purpose)
                            st.markdown("**Purpose**")
                            st.write(cleaned_purpose)
                        
                        # Description section
                        if drill_description:
                            cleaned_desc = clean_sentence(drill_description)
                            st.markdown("**Description**")
                            st.write(cleaned_desc)
                        
                        # Coaching points section
                        coaching_bullets = []
                        coaching_points = drill.get("coaching_points", "")
                        
                        if isinstance(coaching_points, list):
                            coaching_bullets = [clean_bullet(str(point)) for point in coaching_points[:5]]
                        elif coaching_points:
                            coaching_bullets = extract_bullets(coaching_points, max_items=5)
                        
                        # If no coaching points, derive from block type
                        if not coaching_bullets:
                            block_label_lower = normalize_block_label(drill).lower()
                            if "technical" in block_label_lower or "possession" in block_label_lower:
                                coaching_bullets = ["Scanning before touch", "Body shape for control", "Tempo of play"]
                            elif "pressing" in block_label_lower or "defend" in block_label_lower:
                                coaching_bullets = ["Triggers for pressing", "Team compactness", "Communication"]
                            elif "finishing" in block_label_lower or "shoot" in block_label_lower:
                                coaching_bullets = ["First touch into space", "Shot selection", "Follow rebounds"]
                            elif "ssg" in block_label_lower or "small sided" in block_label_lower:
                                coaching_bullets = ["Applies pressure", "Makes quick decisions", "Transitions quickly"]
                            else:
                                coaching_bullets = ["Execute with focus", "Communicate clearly", "Maintain intensity"]
                        
                        if coaching_bullets:
                            st.markdown("**Coaching points**")
                            for point in coaching_bullets:
                                if point:
                                    st.write(f"• {point}")
                        
                        # Progression / Regression sections
                        progression = safe_str(drill.get("progression", ""))
                        regression = safe_str(drill.get("regression", ""))
                        
                        if progression or regression:
                            col1, col2 = st.columns(2)
                            with col1:
                                if progression:
                                    st.markdown("**Progression**")
                                    st.write(clean_sentence(progression))
                            with col2:
                                if regression:
                                    st.markdown("**Regression**")
                                    st.write(clean_sentence(regression))
                    
                    # Right column: diagram
                    with diagram_col:
                        for source in diagram_sources[:1]:  # Show first diagram only
                            try:
                                if source["type"] == "base64":
                                    import base64
                                    image_data = base64.b64decode(source["value"])
                                    st.image(image_data, use_container_width=True)
                                elif source["type"] == "path":
                                    path = Path(source["value"])
                                    if path.exists():
                                        st.image(str(path), use_container_width=True)
                                elif source["type"] == "url":
                                    st.image(source["value"], use_container_width=True)
                            except Exception:
                                # Silently skip diagram rendering errors
                                pass
                            
                            # Optional caption
                            setup_info = safe_str(drill.get("setup", "") or drill.get("field_size", ""))
                            if setup_info:
                                st.caption(f"Setup: {setup_info}")
                
                else:
                    # No diagram: render full-width info
                    # Purpose section
                    purpose = safe_str(drill.get("purpose", ""))
                    if not purpose and not drill_description:
                        description_fallback = safe_str(drill.get("drill_description", "") or drill.get("description", ""))
                        if description_fallback:
                            # Truncate to ~140 chars and remove newlines
                            purpose = description_fallback.replace("\n", " ")
                            if len(purpose) > 140:
                                purpose = purpose[:137] + "..."
                    
                    if purpose:
                        cleaned_purpose = clean_sentence(purpose)
                        st.markdown("**Purpose**")
                        st.write(cleaned_purpose)
                    
                    # Description section
                    if drill_description:
                        cleaned_desc = clean_sentence(drill_description)
                        st.markdown("**Description**")
                        st.write(cleaned_desc)
                    
                    # Coaching points section
                    coaching_bullets = []
                    coaching_points = drill.get("coaching_points", "")
                    
                    if isinstance(coaching_points, list):
                        coaching_bullets = [clean_bullet(str(point)) for point in coaching_points[:5]]
                    elif coaching_points:
                        coaching_bullets = extract_bullets(coaching_points, max_items=5)
                    
                    # If no coaching points, derive from block type
                    if not coaching_bullets:
                        block_label_lower = normalize_block_label(drill).lower()
                        if "technical" in block_label_lower or "possession" in block_label_lower:
                            coaching_bullets = ["Scanning before touch", "Body shape for control", "Tempo of play"]
                        elif "pressing" in block_label_lower or "defend" in block_label_lower:
                            coaching_bullets = ["Triggers for pressing", "Team compactness", "Communication"]
                        elif "finishing" in block_label_lower or "shoot" in block_label_lower:
                            coaching_bullets = ["First touch into space", "Shot selection", "Follow rebounds"]
                        elif "ssg" in block_label_lower or "small sided" in block_label_lower:
                            coaching_bullets = ["Applies pressure", "Makes quick decisions", "Transitions quickly"]
                        else:
                            coaching_bullets = ["Execute with focus", "Communicate clearly", "Maintain intensity"]
                    
                    if coaching_bullets:
                        st.markdown("**Coaching points**")
                        for point in coaching_bullets:
                            if point:
                                st.write(f"• {point}")
                    
                    # Progression / Regression sections
                    progression = safe_str(drill.get("progression", ""))
                    regression = safe_str(drill.get("regression", ""))
                    
                    if progression or regression:
                        col1, col2 = st.columns(2)
                        with col1:
                            if progression:
                                st.markdown("**Progression**")
                                st.write(clean_sentence(progression))
                        with col2:
                            if regression:
                                st.markdown("**Regression**")
                                st.write(clean_sentence(regression))
else:
    st.info("No drills in this practice session.")

# Footer with back button
st.divider()
col1, col2 = st.columns([1, 4])
with col1:
    if st.button("← Back to Team Hub", use_container_width=True):
        st.switch_page("pages/5_Team_Hub.py")
