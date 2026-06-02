"""UI Components for Player AI - Navigation and common widgets"""

import streamlit as st
from typing import Optional, List, Tuple
import config
import session_state as ui_session

# Import experience level module (Day 2)
try:
    import experience_level
    EXPERIENCE_LEVEL_AVAILABLE = True
except ImportError:
    EXPERIENCE_LEVEL_AVAILABLE = False

# Import getting started checklist (Day 9)
try:
    import getting_started
    GETTING_STARTED_AVAILABLE = True
except ImportError:
    GETTING_STARTED_AVAILABLE = False

# Import help content (Day 10)
try:
    import help_content
    HELP_CONTENT_AVAILABLE = True
except ImportError:
    HELP_CONTENT_AVAILABLE = False

# Import user settings (Day 11)
try:
    import user_settings
    USER_SETTINGS_AVAILABLE = True
except ImportError:
    USER_SETTINGS_AVAILABLE = False


# Shared video renderer component for Player AI
def render_video(video_url: str):
    if not video_url:
        st.info("Video demo coming soon.")
    elif "youtube.com" in video_url or "youtu.be" in video_url:
        embed_url = video_url
        if "youtu.be/" in video_url:
            video_id = video_url.split("youtu.be/")[-1].split("?")[0]
            embed_url = f"https://www.youtube.com/embed/{video_id}"
        elif "watch?v=" in video_url:
            embed_url = video_url.replace("watch?v=", "embed/")
            if "&" in embed_url:
                embed_url = embed_url.split("&")[0]
        
        st.components.v1.html(
            f'<iframe width="100%" height="315" src="{embed_url}" frameborder="0" allowfullscreen></iframe>',
            height=315
        )
    else:
        st.video(video_url)

# Page tier definitions (Progressive Disclosure)
# Format: (path, label, tier, icon)
PAGE_TIER_MAP = [
    ("pages/0_Coach_Home.py", "My Dashboard", "essential", "🏠"),
    ("pages/2_Practice_Generator.py", "My Training Plan", "essential", "⚽"),
    ("pages/3_Practice_History.py", "My Progress", "essential", "📅"),
    ("pages/4_Highlight_Reel.py", "Highlight Reel", "essential", "🎬"),
    ("pages/6_Mentor_Feed.py", "Mentor Feed", "essential", "🎙️"),
    ("pages/1_Drill_Library.py", "Drill Library", "essential", "🔍"),
    ("pages/5_Team_Hub.py", "My Profile", "essential", "👤"),
]

PAGE_ACCESS_RULES = {
    "pages/0_Coach_Home.py": {"tier": "essential", "developer_only": False},
    "pages/2_Practice_Generator.py": {"tier": "essential", "developer_only": False},
    "pages/3_Practice_History.py": {"tier": "essential", "developer_only": False},
    "pages/4_Highlight_Reel.py": {"tier": "essential", "developer_only": False},
    "pages/6_Mentor_Feed.py": {"tier": "essential", "developer_only": False},
    "pages/1_Drill_Library.py": {"tier": "essential", "developer_only": False},
    "pages/5_Team_Hub.py": {"tier": "essential", "developer_only": False},
    "pages/9_Schema_Migration.py": {"tier": "expert", "developer_only": True},
    "pages/9_Developer_Tools.py": {"tier": "expert", "developer_only": True},
}


def _get_tier_index(tier: str) -> int:
    """Convert tier name to numeric index for comparison."""
    tier_order = ["essential", "advanced", "expert"]
    return tier_order.index(tier) if tier in tier_order else 0


def _page_links() -> List[Tuple[str, str]]:
    """
    Get navigation links filtered by current experience level.
    
    Returns:
        List of (path, label) tuples for navigation
    """
    # If experience level not available, use legacy behavior
    if not EXPERIENCE_LEVEL_AVAILABLE:
        return _page_links_legacy()
    
    # Get current experience level
    current_level = experience_level.get_experience_level()
    current_tier_index = _get_tier_index(current_level)
    
    # Filter pages by tier
    filtered_pages = []
    for path, label, tier, icon in PAGE_TIER_MAP:
        page_tier_index = _get_tier_index(tier)
        
        # Include page if user's tier is >= page's required tier
        if current_tier_index >= page_tier_index:
            filtered_pages.append((path, label))
    
    return filtered_pages


def _normalize_page_path(page_path: str) -> str:
    return str(page_path).replace("\\", "/")


def _developer_tools_available() -> bool:
    return config.is_dev() and ui_session.is_developer_mode()


def require_page_access(page_path: str):
    """
    Enforce page access based on experience level and developer visibility.
    """
    if not EXPERIENCE_LEVEL_AVAILABLE:
        return

    normalized = _normalize_page_path(page_path)
    rule = PAGE_ACCESS_RULES.get(normalized)
    if not rule:
        return

    required_tier = rule.get("tier", "essential")
    developer_only = bool(rule.get("developer_only", False))

    if developer_only and not _developer_tools_available():
        st.warning("This page is only available in developer mode.", icon="⚠️")
        if st.button("← Back to Home", key=f"back_from_{normalized}"):
            st.switch_page("pages/0_Coach_Home.py")
        st.stop()

    if not experience_level.can_access_page(required_tier):
        experience_level.render_locked_page_message(required_tier)


def _page_links_legacy() -> List[Tuple[str, str]]:
    """
    Legacy page links (pre-progressive disclosure).
    Used as fallback if experience_level module not available.
    """
    return [
        ("pages/0_Coach_Home.py", "My Dashboard"),
        ("pages/2_Practice_Generator.py", "My Training Plan"),
        ("pages/3_Practice_History.py", "My Progress"),
        ("pages/4_Highlight_Reel.py", "Highlight Reel"),
        ("pages/6_Mentor_Feed.py", "Mentor Feed"),
        ("pages/1_Drill_Library.py", "Drill Library"),
        ("pages/5_Team_Hub.py", "My Profile"),
    ]


def render_nav(active_label: Optional[str] = None, columns=None):
    """
    Render the application navigation sidebar for Player AI.
    All six pages are accessible at the Essential tier by default.

    Args:
        active_label: Optional label to emphasize the current page
        columns: Optional list of column widths
    """
    links = _page_links()
    
    # Dynamic column sizing based on number of links
    if columns is None:
        # Adjust columns based on number of visible pages
        if len(links) <= 3:
            # Essential mode: 3 pages
            columns = [1.5, 2.0, 1.8]
        elif len(links) <= 7:
            # Advanced mode: 7 pages
            columns = [1.2, 1.5, 1.3, 1.2, 1.2, 1.3, 1.5]
        else:
            # Expert mode: Many pages
            columns = [1.0] * len(links)
    
    # Ensure we have enough columns
    if len(columns) < len(links):
        columns = [1.5] * len(links)
    
    # Render navigation
    nav_cols = st.columns(columns[:len(links)])
    for col, (path, label) in zip(nav_cols, links):
        with col:
            # Highlight active page
            if active_label and active_label.lower() in label.lower():
                st.page_link(path, label=f"**{label}**")
            else:
                st.page_link(path, label=label)
    
    # Add level switcher to sidebar (Day 2)
    if EXPERIENCE_LEVEL_AVAILABLE:
        experience_level.render_level_switcher_compact()
    
    # Day 9: Getting Started Checklist (check settings)
    if GETTING_STARTED_AVAILABLE:
        # Check if checklist is enabled in settings
        show_checklist = True
        if USER_SETTINGS_AVAILABLE:
            show_checklist = user_settings.should_show_feature("checklist")
        
        if show_checklist:
            getting_started.render_getting_started_checklist()
    
    # Day 10: Help System (check settings)
    if HELP_CONTENT_AVAILABLE:
        # Check if help is enabled in settings
        show_help = True
        if USER_SETTINGS_AVAILABLE:
            show_help = user_settings.should_show_feature("help")
        
        if show_help:
            # Render help button
            help_content.render_help_button()
            
            # Render help panel if open
            # Extract page name from active_label for contextual help
            page_name = None
            if active_label:
                # Clean up active label to get page name
                page_name = active_label.replace("**", "").strip()
                # Remove emoji if present
                for emoji in ["🏠", "⚽", "📅", "🔍", "👥", "⭐", "➕", "📚", "🎨", "📝", "🔧", "📆", "🗓️", "🔬", "🗄️", "⚙️"]:
                    page_name = page_name.replace(emoji, "").strip()
            
            help_content.render_help_panel(current_page=page_name)


def get_visible_page_count() -> int:
    """
    Get the number of pages visible to the current user.
    Useful for analytics and testing.
    
    Returns:
        Number of navigation links visible
    """
    return len(_page_links())


def get_current_tier_pages() -> List[Tuple[str, str, str]]:
    """
    Get all pages available at current tier with their metadata.
    
    Returns:
        List of (path, label, tier) tuples
    """
    if not EXPERIENCE_LEVEL_AVAILABLE:
        return [(path, label, "unknown") for path, label in _page_links_legacy()]
    
    current_level = experience_level.get_experience_level()
    current_tier_index = _get_tier_index(current_level)
    
    pages = []
    for path, label, tier, icon in PAGE_TIER_MAP:
        page_tier_index = _get_tier_index(tier)
        if current_tier_index >= page_tier_index:
            pages.append((path, label, tier))
    
    return pages


def render_tier_badge(tier: str) -> None:
    """
    Render a small badge showing the tier requirement for a page.
    Useful for settings or debug pages.
    
    Args:
        tier: Experience level tier (essential/advanced/expert)
    """
    colors = {
        "essential": "#10b981",
        "advanced": "#3b82f6", 
        "expert": "#8b5cf6"
    }
    
    icons = {
        "essential": "⚡",
        "advanced": "🎯",
        "expert": "🔧"
    }
    
    color = colors.get(tier, "#666")
    icon = icons.get(tier, "")
    
    st.markdown(
        f"""
        <span style="
            background-color: {color}15;
            color: {color};
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            border: 1px solid {color}40;
        ">
            {icon} {tier.upper()}
        </span>
        """,
        unsafe_allow_html=True
    )


# ============================================================================
# ENHANCED NAVIGATION (Day 13) - CLEANED UP VERSION
# ============================================================================

def clean_text(text: Optional[str], default: str = "") -> str:
    """Safe text cleaner that removes 'nan', 'None', etc."""
    if text is None:
        return default
    s = str(text).strip()
    if s.lower() in ("nan", "none", "", "null"):
        return default
    return s


def render_nav_enhanced(active_label: Optional[str] = None):
    """
    Enhanced navigation delegate for Player AI.
    Delegates directly to render_nav for clean, simplified player navigation.
    """
    render_nav(active_label)


def render_skills_radar(skill_radar: dict, target_rrs_score: int = 88):
    """
    Render a Plotly radar chart displaying skill categories.
    If has_data is False, renders an info box instead.
    """
    if not skill_radar or not skill_radar.get("has_data", False):
        st.info("Complete 2+ sessions to see your Skills Radar populate with your personal training data.")
        return

    import plotly.graph_objects as go

    axes = skill_radar["axes"]
    scores = skill_radar["scores"]

    # Wrap the data so the radar polygon is closed
    axes_closed = list(axes) + [axes[0]]
    scores_closed = list(scores) + [scores[0]]

    # Target level values (drawn as a dotted reference line)
    # Target level values match the size of axes_closed
    target_val = target_rrs_score if target_rrs_score is not None else 88
    r_target = [target_val] * len(axes_closed)

    fig = go.Figure()

    # Trace 1: Current Score
    fig.add_trace(go.Scatterpolar(
        r=scores_closed,
        theta=axes_closed,
        fill="toself",
        fillcolor="rgba(59, 130, 246, 0.2)",
        line=dict(color="#3b82f6"),
        name="Your Score"
    ))

    # Trace 2: Target Level
    fig.add_trace(go.Scatterpolar(
        r=r_target,
        theta=axes_closed,
        fill=None,
        mode="lines",
        line=dict(color="#cbd5e1", dash="dot", width=2),
        name="Target Level"
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor="#e2e8f0"
            ),
            angularaxis=dict(
                gridcolor="#e2e8f0"
            ),
            bgcolor="rgba(0,0,0,0)"
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=40, r=40, t=20, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=320,
    )
    
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"responsive": True}
    )

