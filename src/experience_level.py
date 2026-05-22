"""
User Experience Level Management for Progressive Disclosure.

This module manages the three-tier experience system:
- Essential: Core training plan and progress tracking (3 pages)
- Advanced: More control over drills and player profile (5+ pages)
- Expert: Full customization and developer tools (all pages)
"""

import streamlit as st
from typing import Dict, List, Literal

# Type alias for experience levels
ExperienceLevel = Literal["essential", "advanced", "expert"]

# Experience level definitions with metadata
LEVELS: Dict[str, Dict[str, any]] = {
    "essential": {
        "label": "Essential Mode",
        "description": "Fast individual training with smart defaults",
        "icon": "⚡",
        "color": "#10b981",  # Green
        "tagline": "Get training plans done in under 5 clicks",
        "visible_pages": [
            "My Dashboard",
            "⚽ My Training Plan", 
            "📅 My Progress"
        ],
    },
    "advanced": {
        "label": "Advanced Mode",
        "description": "More control over drills and player profile",
        "icon": "🎯",
        "color": "#3b82f6",  # Blue
        "tagline": "Customize your training workflow",
        "visible_pages": [
            "My Dashboard",
            "⚽ My Training Plan",
            "📅 My Progress",
            "👥 My Profile",
        ],
    },
    "expert": {
        "label": "Expert Mode",
        "description": "Full customization and power user tools",
        "icon": "🔧",
        "color": "#8b5cf6",  # Purple
        "tagline": "Unlock all features and automation",
        "visible_pages": "*",  # Special marker for "all pages"
    }
}

# Tier hierarchy (for comparisons)
TIER_ORDER: List[str] = ["essential", "advanced", "expert"]


def get_experience_level() -> ExperienceLevel:
    """
    Get the current user's experience level.
    
    Returns:
        Current experience level (essential/advanced/expert)
    """
    # Initialize if not set
    if "user_experience_level" not in st.session_state:
        st.session_state.user_experience_level = "essential"
    
    return st.session_state.user_experience_level


def set_experience_level(level: ExperienceLevel) -> bool:
    """
    Set the user's experience level.
    
    Args:
        level: Experience level to set (essential/advanced/expert)
        
    Returns:
        True if level was changed, False if already at that level
    """
    if level not in LEVELS:
        raise ValueError(f"Invalid experience level: {level}. Must be one of {list(LEVELS.keys())}")
    
    current_level = get_experience_level()
    
    if current_level == level:
        return False  # No change needed
    
    # Track level changes for analytics
    if "level_change_history" not in st.session_state:
        st.session_state.level_change_history = []
    
    st.session_state.level_change_history.append({
        "from": current_level,
        "to": level,
        "timestamp": st.session_state.get("session_start_time", "unknown")
    })
    
    st.session_state.user_experience_level = level
    return True


def is_essential_mode() -> bool:
    """Check if user is in Essential mode."""
    return get_experience_level() == "essential"


def is_advanced_mode() -> bool:
    """Check if user is in Advanced mode."""
    return get_experience_level() == "advanced"


def is_expert_mode() -> bool:
    """Check if user is in Expert mode."""
    return get_experience_level() == "expert"


def is_at_least_advanced() -> bool:
    """Check if user is in Advanced or Expert mode."""
    return get_experience_level() in ["advanced", "expert"]


def is_at_least_expert() -> bool:
    """Check if user is in Expert mode (explicit check for clarity)."""
    return get_experience_level() == "expert"


def can_access_page(required_tier: ExperienceLevel) -> bool:
    """
    Check if current user can access a page requiring a specific tier.
    
    Args:
        required_tier: Minimum experience level required
        
    Returns:
        True if user's level is equal or higher than required
    """
    current_level = get_experience_level()
    current_index = TIER_ORDER.index(current_level)
    required_index = TIER_ORDER.index(required_tier)
    
    return current_index >= required_index


def get_level_info(level: ExperienceLevel = None) -> Dict:
    """
    Get metadata for an experience level.
    
    Args:
        level: Experience level (defaults to current level)
        
    Returns:
        Dictionary with level metadata
    """
    if level is None:
        level = get_experience_level()
    
    return LEVELS.get(level, {})


def get_upgrade_benefits(from_level: ExperienceLevel = None) -> List[str]:
    """
    Get list of features unlocked by upgrading from current level.
    
    Args:
        from_level: Starting level (defaults to current level)
        
    Returns:
        List of feature descriptions
    """
    if from_level is None:
        from_level = get_experience_level()
    
    benefits = {
        "essential": [
            "Browse full drill library by position and skill",
            "Save favorite training plans for quick reuse",
            "Add custom notes to your training sessions",
            "Track personal focus areas and skill progress",
            "Customize drill selections and position filters",
            "Edit player profile and position targets",
        ],
        "advanced": [
            "Create customized solo training templates",
            "Generate multi-week training cycles",
            "Bulk import custom training drills",
            "Advanced recommendation scoring settings",
            "Weekly calendar training view",
            "Developer diagnostics and player data tools",
        ],
    }
    
    return benefits.get(from_level, [])


def render_level_switcher_compact() -> None:
    """
    Render a compact experience level switcher in the sidebar.
    Shows current level and upgrade button if not at max.
    """
    current_level = get_experience_level()
    current_info = get_level_info(current_level)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Experience Level")
    
    # Show current level with icon
    st.sidebar.markdown(
        f"**{current_info['icon']} {current_info['label']}**"
    )
    st.sidebar.caption(current_info['tagline'])
    
    # Show upgrade button if not at max level
    if current_level == "essential":
        if st.sidebar.button("⬆️ Unlock Advanced Mode", use_container_width=True):
            set_experience_level("advanced")
            st.rerun()
        st.sidebar.caption("Get more control and features")
    elif current_level == "advanced":
        if st.sidebar.button("⬆️ Unlock Expert Mode", use_container_width=True):
            set_experience_level("expert")
            st.rerun()
        st.sidebar.caption("Access all power user tools")
    else:
        st.sidebar.success("All features unlocked!")


def render_level_switcher_full() -> None:
    """
    Render a full experience level switcher showing all three options.
    Useful for settings pages or initial setup.
    """
    current_level = get_experience_level()
    
    st.markdown("### Choose Your Experience Level")
    st.caption("You can change this anytime in the sidebar")
    
    cols = st.columns(3)
    
    for idx, (level_key, level_info) in enumerate(LEVELS.items()):
        with cols[idx]:
            is_current = level_key == current_level
            
            # Card styling
            border_color = level_info['color'] if is_current else "#e5e7eb"
            bg_color = f"{level_info['color']}15" if is_current else "#ffffff"
            
            st.markdown(
                f"""
                <div style="
                    border: 2px solid {border_color};
                    border-radius: 8px;
                    padding: 16px;
                    background-color: {bg_color};
                    height: 100%;
                ">
                    <div style="font-size: 32px; margin-bottom: 8px;">
                        {level_info['icon']}
                    </div>
                    <div style="font-weight: 600; font-size: 16px; margin-bottom: 4px;">
                        {level_info['label']}
                    </div>
                    <div style="font-size: 13px; color: #666; margin-bottom: 12px;">
                        {level_info['description']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            if is_current:
                st.button(
                    "✓ Current",
                    disabled=True,
                    use_container_width=True,
                    key=f"current_{level_key}"
                )
            else:
                if st.button(
                    "Switch",
                    use_container_width=True,
                    key=f"switch_{level_key}",
                    type="primary" if level_key == "advanced" else "secondary"
                ):
                    set_experience_level(level_key)
                    st.rerun()


def render_upgrade_prompt(
    message: str,
    target_level: ExperienceLevel = "advanced",
    benefits: List[str] = None
) -> None:
    """
    Render a contextual upgrade prompt encouraging users to unlock features.
    
    Args:
        message: Main message to display
        target_level: Level to upgrade to
        benefits: Optional list of specific benefits to highlight
    """
    current_level = get_experience_level()
    
    # Don't show if already at or above target level
    if can_access_page(target_level):
        return
    
    target_info = get_level_info(target_level)
    
    if benefits is None:
        benefits = get_upgrade_benefits(current_level)[:3]  # Show top 3
    
    with st.expander(f"💡 {message}", expanded=False):
        st.markdown(f"**Unlock {target_info['label']}** to access:")
        for benefit in benefits:
            st.markdown(f"- {benefit}")
        
        if st.button(
            f"{target_info['icon']} Upgrade to {target_info['label']}",
            key=f"upgrade_prompt_{target_level}",
            type="primary"
        ):
            set_experience_level(target_level)
            st.success(f"Upgraded to {target_info['label']}!")
            st.rerun()


def render_locked_page_message(required_level: ExperienceLevel) -> None:
    """
    Render a message for pages that require a higher experience level.
    Shows upgrade CTA and stops page execution.
    
    Args:
        required_level: Experience level required to access this page
    """
    required_info = get_level_info(required_level)
    
    st.warning(
        f"🔒 This feature requires **{required_info['label']}**",
        icon="⚠️"
    )
    
    st.markdown(
        f"""
        You're currently in **{get_level_info()['label']}**. 
        Upgrade to unlock this feature and more!
        """
    )
    
    # Show benefits
    benefits = get_upgrade_benefits()
    if benefits:
        st.markdown("**What you'll unlock:**")
        for benefit in benefits[:5]:
            st.markdown(f"- {benefit}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(
            f"⬆️ Upgrade to {required_info['label']}",
            type="primary",
            use_container_width=True
        ):
            set_experience_level(required_level)
            st.rerun()
    
    with col2:
        if st.button("← Go Back", use_container_width=True):
            st.switch_page("pages/0_Coach_Home.py")
    
    st.stop()


def get_level_analytics() -> Dict:
    """
    Get analytics about experience level usage (for portfolio/metrics).
    
    Returns:
        Dictionary with level change history and current level
    """
    return {
        "current_level": get_experience_level(),
        "change_history": st.session_state.get("level_change_history", []),
        "total_changes": len(st.session_state.get("level_change_history", [])),
    }


# Debug helper
def _debug_print_level_info():
    """Print current level info to console (for testing)."""
    print(f"\n=== Experience Level Debug ===")
    print(f"Current Level: {get_experience_level()}")
    print(f"Is Essential: {is_essential_mode()}")
    print(f"Is Advanced: {is_advanced_mode()}")
    print(f"Is Expert: {is_expert_mode()}")
    print(f"Can Access Advanced: {can_access_page('advanced')}")
    print(f"Can Access Expert: {can_access_page('expert')}")
    print(f"===========================\n")
