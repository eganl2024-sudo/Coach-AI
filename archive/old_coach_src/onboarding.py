"""
Contextual Onboarding System for Progressive Disclosure.

This module provides reusable hint and tutorial components that can be added
to any page in the application. Hints are dismissible, tracked in session state,
and can be targeted to specific experience levels.

Author: Liam
Created: Day 8 of Progressive Disclosure Implementation
"""

import streamlit as st
from typing import Dict, List, Literal, Optional, Callable
from datetime import datetime

# Import user settings (Day 11)
try:
    import user_settings
    USER_SETTINGS_AVAILABLE = True
except ImportError:
    USER_SETTINGS_AVAILABLE = False

# Type aliases
HintType = Literal["spotlight", "tip", "walkthrough", "success"]
ExperienceLevel = Literal["essential", "advanced", "expert"]


# ============================================================================
# HINT CATALOG
# ============================================================================

HINTS: Dict[str, Dict] = {
    # Coach Home hints
    "home_first_practice": {
        "id": "home_first_practice",
        "type": "spotlight",
        "title": "🎉 Welcome to Coach AI!",
        "message": "Ready to plan your first practice? Click the big green button to get started. We'll guide you through creating a session your team will love!",
        "page": "Coach Home",
        "target_level": ["essential", "advanced", "expert"],
        "priority": 1,
    },
    "home_practice_history": {
        "id": "home_practice_history",
        "type": "tip",
        "title": "💡 Quick Tip: Reuse Past Practices",
        "message": "See those recent sessions below? Click 'Reuse' on any practice to quickly generate a similar one. It's a huge time-saver!",
        "page": "Coach Home",
        "target_level": ["essential", "advanced", "expert"],
        "priority": 3,
    },
    "home_upgrade_advanced": {
        "id": "home_upgrade_advanced",
        "type": "spotlight",
        "title": "🎯 Ready for More Control?",
        "message": "Upgrade to Advanced mode in the sidebar to access the Drill Library, Team Hub, and more customization options!",
        "page": "Coach Home",
        "target_level": ["essential"],
        "priority": 5,
    },
    
    # Practice Generator hints
    "generator_session_types": {
        "id": "generator_session_types",
        "type": "tip",
        "title": "⚡ Quick Tip: Session Types",
        "message": "Choose 'Balanced' for a well-rounded practice, 'Technical Focus' to work on skills, 'Game Prep' before matches, or 'Fitness' for conditioning days.",
        "page": "Practice Generator",
        "target_level": ["essential"],
        "priority": 2,
    },
    "generator_duration": {
        "id": "generator_duration",
        "type": "tip",
        "title": "⏱️ Adjust Practice Length",
        "message": "Use the duration slider to match your available time. We'll automatically adjust drill lengths to fit perfectly.",
        "page": "Practice Generator",
        "target_level": ["essential", "advanced"],
        "priority": 4,
    },
    "generator_categories": {
        "id": "generator_categories",
        "type": "tip",
        "title": "🎯 Customize Drill Categories",
        "message": "Select specific drill categories to focus on particular aspects of the game. The more specific you are, the better we can tailor your practice!",
        "page": "Practice Generator",
        "target_level": ["advanced", "expert"],
        "priority": 3,
    },
    "generator_templates": {
        "id": "generator_templates",
        "type": "spotlight",
        "title": "🔧 Power Feature: Practice Templates",
        "message": "Save time by creating practice templates! Define your preferred drill structure once, then reuse it whenever you need.",
        "page": "Practice Generator",
        "target_level": ["expert"],
        "priority": 2,
    },
    
    # Drill Library hints
    "drills_quick_filters": {
        "id": "drills_quick_filters",
        "type": "tip",
        "title": "⚡ Quick Tip: One-Click Filters",
        "message": "Use the Quick Filter buttons to instantly find drills for common scenarios. No need to fiddle with multiple filter options!",
        "page": "Drill Library",
        "target_level": ["advanced", "expert"],
        "priority": 2,
    },
    "drills_favorites": {
        "id": "drills_favorites",
        "type": "tip",
        "title": "⭐ Build Your Favorites Collection",
        "message": "Star your go-to drills as favorites! They'll be easier to find and can be filtered in the Practice Generator.",
        "page": "Drill Library",
        "target_level": ["advanced", "expert"],
        "priority": 3,
    },
    "drills_tags": {
        "id": "drills_tags",
        "type": "tip",
        "title": "🏷️ Organize with Tags",
        "message": "Add custom tags to drills (like 'Indoor', 'Small space', 'High energy') to make them easier to find later.",
        "page": "Drill Library",
        "target_level": ["advanced", "expert"],
        "priority": 4,
    },
    
    # Team Hub hints
    "team_first_setup": {
        "id": "team_first_setup",
        "type": "spotlight",
        "title": "👥 Set Up Your Team Profile",
        "message": "Adding team details like age group, play style, and focus areas helps us suggest better drills and practices tailored to your team!",
        "page": "Team Hub",
        "target_level": ["advanced", "expert"],
        "priority": 1,
    },
    "team_focus_areas": {
        "id": "team_focus_areas",
        "type": "tip",
        "title": "🎯 Define Focus Areas",
        "message": "Set focus areas (like 'Pressing', 'Build-up play') and we'll highlight drills that match your team's development goals.",
        "page": "Team Hub",
        "target_level": ["advanced", "expert"],
        "priority": 2,
    },
    "team_schedule": {
        "id": "team_schedule",
        "type": "tip",
        "title": "📅 Add Your Schedule",
        "message": "Connect your match schedule to get practice suggestions that prepare your team for upcoming opponents.",
        "page": "Team Hub",
        "target_level": ["expert"],
        "priority": 3,
    },
    
    # Practice History hints
    "history_reuse": {
        "id": "history_reuse",
        "type": "tip",
        "title": "🔄 Reuse Successful Practices",
        "message": "Click 'Reuse' on any past practice to quickly generate a similar session. Perfect when you're short on planning time!",
        "page": "Practice History",
        "target_level": ["essential", "advanced", "expert"],
        "priority": 2,
    },
    "history_export": {
        "id": "history_export",
        "type": "tip",
        "title": "📄 Export Practice Plans",
        "message": "Export practices as PDF or HTML to print for the field, or share with assistant coaches.",
        "page": "Practice History",
        "target_level": ["advanced", "expert"],
        "priority": 4,
    },
}


# ============================================================================
# SESSION STATE MANAGEMENT
# ============================================================================

def init_onboarding_state():
    """Initialize onboarding state in Streamlit session state."""
    if "dismissed_hints" not in st.session_state:
        st.session_state.dismissed_hints = set()
    
    if "shown_hints_this_session" not in st.session_state:
        st.session_state.shown_hints_this_session = set()
    
    if "hint_interactions" not in st.session_state:
        st.session_state.hint_interactions = []


def is_hint_dismissed(hint_id: str) -> bool:
    """Check if a hint has been permanently dismissed."""
    init_onboarding_state()
    return hint_id in st.session_state.dismissed_hints


def dismiss_hint(hint_id: str):
    """Permanently dismiss a hint."""
    init_onboarding_state()
    st.session_state.dismissed_hints.add(hint_id)
    
    # Track interaction
    st.session_state.hint_interactions.append({
        "hint_id": hint_id,
        "action": "dismissed",
        "timestamp": datetime.now().isoformat(),
    })


def is_hint_shown_this_session(hint_id: str) -> bool:
    """Check if hint was already shown in current session."""
    init_onboarding_state()
    return hint_id in st.session_state.shown_hints_this_session


def mark_hint_shown(hint_id: str):
    """Mark hint as shown in current session."""
    init_onboarding_state()
    st.session_state.shown_hints_this_session.add(hint_id)


def reset_all_hints():
    """Reset all dismissed hints (for testing/debugging)."""
    st.session_state.dismissed_hints = set()
    st.session_state.shown_hints_this_session = set()


# ============================================================================
# HINT FILTERING
# ============================================================================

def get_hints_for_page(
    page: str,
    experience_level: Optional[ExperienceLevel] = None,
    max_hints: int = 3
) -> List[Dict]:
    """
    Get relevant hints for a specific page and experience level.
    
    Args:
        page: Page name (e.g., "Coach Home", "Practice Generator")
        experience_level: Current user experience level
        max_hints: Maximum number of hints to return
        
    Returns:
        List of hint dictionaries, sorted by priority
    """
    init_onboarding_state()
    
    # Filter hints for this page
    page_hints = [
        hint for hint in HINTS.values()
        if hint["page"] == page
    ]
    
    # Filter by experience level if provided
    if experience_level:
        page_hints = [
            hint for hint in page_hints
            if experience_level in hint["target_level"]
        ]
    
    # Filter out dismissed hints
    page_hints = [
        hint for hint in page_hints
        if not is_hint_dismissed(hint["id"])
    ]
    
    # Sort by priority (lower number = higher priority)
    page_hints.sort(key=lambda h: h["priority"])
    
    # Limit to max_hints
    return page_hints[:max_hints]


# ============================================================================
# HINT RENDERING COMPONENTS
# ============================================================================

def render_feature_spotlight(
    hint_id: str,
    title: str,
    message: str,
    icon: str = "💡",
    dismissible: bool = True,
) -> bool:
    """
    Render a feature spotlight hint (prominent, attention-grabbing).
    
    Args:
        hint_id: Unique hint identifier
        title: Spotlight title
        message: Spotlight message
        icon: Emoji or icon for the spotlight
        dismissible: Whether user can dismiss the hint
        
    Returns:
        True if hint was dismissed, False otherwise
    """
    init_onboarding_state()
    
    # Don't show if already dismissed
    if is_hint_dismissed(hint_id):
        return False
    
    # Mark as shown
    mark_hint_shown(hint_id)
    
    # Render spotlight
    with st.container():
        col1, col2 = st.columns([10, 1]) if dismissible else (st, None)
        
        with col1:
            st.info(f"### {icon} {title}\n\n{message}")
        
        if dismissible and col2:
            with col2:
                if st.button("✕", key=f"dismiss_{hint_id}", help="Dismiss this hint"):
                    dismiss_hint(hint_id)
                    return True
    
    return False


def render_quick_tip(
    hint_id: str,
    title: str,
    message: str,
    icon: str = "💡",
    dismissible: bool = True,
) -> bool:
    """
    Render a quick tip hint (subtle, informative).
    
    Args:
        hint_id: Unique hint identifier
        title: Tip title
        message: Tip message
        icon: Emoji or icon for the tip
        dismissible: Whether user can dismiss the hint
        
    Returns:
        True if hint was dismissed, False otherwise
    """
    init_onboarding_state()
    
    # Don't show if already dismissed
    if is_hint_dismissed(hint_id):
        return False
    
    # Mark as shown
    mark_hint_shown(hint_id)
    
    # Render tip in expander (collapsed by default)
    with st.expander(f"{icon} {title}", expanded=False):
        st.markdown(message)
        
        if dismissible:
            if st.button("Got it! Don't show again", key=f"dismiss_{hint_id}"):
                dismiss_hint(hint_id)
                return True
    
    return False


def render_walkthrough_step(
    hint_id: str,
    step_number: int,
    total_steps: int,
    title: str,
    message: str,
    action_text: str = "Next",
    on_action: Optional[Callable] = None,
) -> bool:
    """
    Render a walkthrough step (multi-step tutorial).
    
    Args:
        hint_id: Unique hint identifier
        step_number: Current step number (1-indexed)
        total_steps: Total number of steps
        title: Step title
        message: Step message
        action_text: Text for action button
        on_action: Callback when action button is clicked
        
    Returns:
        True if action was taken, False otherwise
    """
    init_onboarding_state()
    
    # Don't show if already dismissed
    if is_hint_dismissed(hint_id):
        return False
    
    # Mark as shown
    mark_hint_shown(hint_id)
    
    # Render walkthrough
    st.markdown(f"**Step {step_number} of {total_steps}**")
    st.info(f"### {title}\n\n{message}")
    
    col1, col2 = st.columns([1, 5])
    
    action_taken = False
    with col1:
        if st.button(action_text, key=f"action_{hint_id}"):
            if on_action:
                on_action()
            action_taken = True
    
    with col2:
        if st.button("Skip tutorial", key=f"skip_{hint_id}"):
            dismiss_hint(hint_id)
            return True
    
    return action_taken


def render_success_message(
    hint_id: str,
    title: str,
    message: str,
    icon: str = "🎉",
    auto_dismiss_seconds: int = 5,
) -> None:
    """
    Render a success message (positive reinforcement).
    
    Args:
        hint_id: Unique hint identifier
        title: Success title
        message: Success message
        icon: Emoji or icon
        auto_dismiss_seconds: Seconds before auto-dismiss (0 = no auto-dismiss)
    """
    init_onboarding_state()
    
    # Mark as shown
    mark_hint_shown(hint_id)
    
    # Render success message
    st.success(f"### {icon} {title}\n\n{message}")
    
    # Track interaction
    st.session_state.hint_interactions.append({
        "hint_id": hint_id,
        "action": "shown",
        "timestamp": datetime.now().isoformat(),
    })


# ============================================================================
# HIGH-LEVEL HINT DISPLAY
# ============================================================================

def show_contextual_hints(
    page: str,
    experience_level: Optional[ExperienceLevel] = None,
    max_hints: int = 1,
    hint_type: Optional[HintType] = None,
) -> None:
    """
    Show contextual hints for a page (high-level convenience function).
    
    Args:
        page: Page name
        experience_level: Current user experience level  
        max_hints: Maximum number of hints to show
        hint_type: Optional filter by hint type
    """
    # Check if hints are enabled in settings (Day 11 integration)
    if USER_SETTINGS_AVAILABLE:
        if not user_settings.should_show_feature("hints"):
            return  # Hints disabled in settings
    
    # Get relevant hints
    hints = get_hints_for_page(page, experience_level, max_hints)
    
    # Filter by type if specified
    if hint_type:
        hints = [h for h in hints if h["type"] == hint_type]
    
    # Render hints
    for hint in hints:
        if hint["type"] == "spotlight":
            render_feature_spotlight(
                hint["id"],
                hint["title"],
                hint["message"],
            )
        elif hint["type"] == "tip":
            render_quick_tip(
                hint["id"],
                hint["title"],
                hint["message"],
            )
        elif hint["type"] == "success":
            render_success_message(
                hint["id"],
                hint["title"],
                hint["message"],
            )
        # walkthrough requires manual handling


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_hint_statistics() -> Dict:
    """Get statistics about hint usage."""
    init_onboarding_state()
    
    total_hints = len(HINTS)
    dismissed_count = len(st.session_state.dismissed_hints)
    shown_this_session = len(st.session_state.shown_hints_this_session)
    interaction_count = len(st.session_state.hint_interactions)
    
    return {
        "total_hints": total_hints,
        "dismissed_count": dismissed_count,
        "remaining_hints": total_hints - dismissed_count,
        "shown_this_session": shown_this_session,
        "interactions": interaction_count,
    }


def export_hint_interactions() -> List[Dict]:
    """Export hint interaction history for analytics."""
    init_onboarding_state()
    return st.session_state.hint_interactions.copy()
