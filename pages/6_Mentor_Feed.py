"""Player Development Platform - Mentor Feed"""
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import importlib
import config
import data_loader
import session_state
import ui_components

# Force reload of custom modules to clear Streamlit's running process cache
try:
    importlib.reload(config)
    importlib.reload(data_loader)
    importlib.reload(session_state)
    importlib.reload(ui_components)
except Exception:
    pass

from auth import require_auth

# Page configuration
st.set_page_config(
    page_title="Mentor Feed - Player AI",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Enforce authentication
require_auth()

# Initialize session state
session_state.init_session_state()
if "data_path" not in st.session_state:
    st.session_state.data_path = config.get_data_path()

# Render standard navigation
ui_components.render_nav(active_label="Mentor Feed")

st.divider()

# Load data at the top
athlete_profile = data_loader.load_athlete_profile(st.session_state.data_path) or {}
presenters_df = st.session_state.get("presenters_df") or \
    data_loader.load_presenters(st.session_state.data_path)
feed = data_loader.load_mentor_feed(st.session_state.data_path)
posts = feed.get("posts", [])

# Store athlete profile in session state if needed
st.session_state.athlete_profile = athlete_profile

# Inject CSS Block
st.markdown("""
<style>
.feed-hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
    border-radius: 12px;
    padding: 32px;
    margin-bottom: 28px;
    box-shadow: 0 4px 15px rgba(15, 23, 42, 0.15);
}
.presenter-filter-card {
    background: white;
    border: 2px solid #e2e8f0;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
    height: 100%;
}
.presenter-filter-card.active {
    border-color: #3b82f6;
    background: #eff6ff;
}
.presenter-filter-card:hover {
    border-color: #93c5fd;
    transform: translateY(-1px);
}
.presenter-name-card {
    font-size: 15px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 4px;
}
.presenter-team-card {
    font-size: 12px;
    color: #64748b;
    margin-bottom: 6px;
}
.presenter-level-card {
    display: inline-block;
    background: #dbeafe;
    color: #1e40af;
    font-size: 10px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 12px;
}
.post-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.04);
}
.post-presenter-badge {
    display: inline-flex;
    align-items: center;
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 12px;
}
.post-date {
    font-size: 12px;
    color: #94a3b8;
    margin-bottom: 8px;
}
.post-title {
    font-size: 20px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 10px;
    line-height: 1.3;
}
.post-description {
    font-size: 15px;
    color: #475569;
    line-height: 1.6;
    margin-bottom: 16px;
}
.post-position-tag {
    display: inline-block;
    background: #f1f5f9;
    color: #475569;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 12px;
    margin-right: 6px;
    margin-bottom: 8px;
}
.coming-soon-video {
    background: #f8fafc;
    border: 2px dashed #cbd5e1;
    border-radius: 8px;
    padding: 32px;
    text-align: center;
    color: #94a3b8;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 12px;
}
.a2a-banner {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
    color: white;
    border-radius: 12px;
    padding: 24px 28px;
    margin-top: 32px;
}
</style>
""", unsafe_allow_html=True)

# Section 1 — Hero Banner
st.markdown("""
<div class="feed-hero">
    <h1 style="color:white; margin:0 0 8px 0; font-size:28px;">
        🎙️ Mentor Feed
    </h1>
    <p style="color:rgba(255,255,255,0.9); font-size:16px; margin:0 0 6px 0;">
        Direct from Mitch, Bryce, Nick, and Liam — what they are 
        training, what they are learning, and what you need to hear.
    </p>
    <p style="color:rgba(255,255,255,0.65); font-size:13px; margin:0;">
        MLS Next Pro · Division I · Notre Dame
    </p>
</div>
""", unsafe_allow_html=True)

# Section 2 — Presenter Filter Row
if "feed_filter_presenter" not in st.session_state:
    st.session_state.feed_filter_presenter = "All"

filter_cols = st.columns([1, 1, 1, 1, 1])  # 5 columns: All + 4 presenters

with filter_cols[0]:
    is_active = st.session_state.feed_filter_presenter == "All"
    if st.button(
        "All Posts",
        key="filter_all",
        use_container_width=True,
        type="primary" if is_active else "secondary"
    ):
        st.session_state.feed_filter_presenter = "All"
        st.rerun()

ORDERED_PRESENTER_IDS = ["YOU-01", "KC-01", "UNLV-01", "TFC-01"]

for idx, pid in enumerate(ORDERED_PRESENTER_IDS):
    col_idx = idx + 1
    # Look up presenter details
    p_row = presenters_df[presenters_df["presenter_id"] == pid]
    if not p_row.empty:
        p_data = p_row.iloc[0]
        display_name = p_data.get("display_name", "")
        
        # Count posts
        count = sum(1 for p in posts if p.get("presenter_id") == pid)
        
        with filter_cols[col_idx]:
            is_active = st.session_state.feed_filter_presenter == pid
            if st.button(
                f"{display_name} ({count})",
                key=f"filter_{pid}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.feed_filter_presenter = pid
                st.rerun()

st.write("")

# Section 3 — Position Filter (secondary, compact)
position_options = [
    "All Positions",
    "Goalkeeper",
    "Center Back",
    "Full Back",
    "Defensive Midfielder",
    "Central Midfielder",
    "Attacking Midfielder",
    "Winger",
    "Striker",
]

filter_row_col1, filter_row_col2 = st.columns([1, 4])
with filter_row_col1:
    st.markdown("**Filter by position:**")
with filter_row_col2:
    selected_position = st.selectbox(
        "Filter by position relevance",
        options=position_options,
        index=0,
        key="feed_filter_position",
        label_visibility="collapsed",
    )

st.write("")

# Section 4 — Feed Cards
# Apply filters
visible_posts = posts
if st.session_state.feed_filter_presenter != "All":
    visible_posts = [
        p for p in visible_posts
        if p.get("presenter_id") == st.session_state.feed_filter_presenter
    ]
if selected_position != "All Positions":
    visible_posts = [
        p for p in visible_posts
        if selected_position.lower() in
           [t.lower().strip() for t in
            p.get("position_tags", "").split("|") if t.strip()]
        or not p.get("position_tags", "").strip()  # show universal posts
    ]

for post in visible_posts:
    # Look up presenter details
    presenter_row = None
    if presenters_df is not None and not presenters_df.empty:
        match = presenters_df[
            presenters_df["presenter_id"] == post.get("presenter_id", "")
        ]
        if not match.empty:
            presenter_row = match.iloc[0]

    display_name = presenter_row.get("display_name", "") if presenter_row is not None else ""
    team_level   = presenter_row.get("team_level", "")   if presenter_row is not None else ""

    # Format date
    date_str = post.get("date_posted", "")
    try:
        formatted_date = datetime.fromisoformat(date_str).strftime("%B %d, %Y")
    except Exception:
        formatted_date = date_str

    # Build position tag HTML
    pos_tags = [t.strip() for t in post.get("position_tags", "").split("|") if t.strip()]
    pos_tag_html = "".join(
        f'<span class="post-position-tag">{t}</span>' for t in pos_tags
    )

    # Render card
    st.markdown(f"""
    <div class="post-card">
        <div class="post-presenter-badge">
            🎙️ {display_name}{(" · " + team_level) if team_level else ""}
        </div>
        <div class="post-date">{formatted_date}</div>
        <div class="post-title">{post.get("title", "")}</div>
        <div class="post-description">{post.get("description", "")}</div>
        {pos_tag_html}
    </div>
    """, unsafe_allow_html=True)

    # Video: render below the card HTML
    video_url = post.get("video_url", "")
    if post.get("coming_soon", False) or not video_url:
        st.markdown("""
        <div class="coming-soon-video">
            🎬 Video dropping soon — check back shortly.
        </div>
        """, unsafe_allow_html=True)
    else:
        ui_components.render_video(video_url)

    st.write("")  # breathing room between cards

# Empty State
if not visible_posts:
    st.info(
        "No posts match your current filters. "
        "Try selecting 'All Posts' or a different position.",
        icon="🔍"
    )

# Section 5 — Athlete2Athlete Teaser Banner
st.markdown("""
<div class="a2a-banner">
    <h3 style="margin:0 0 8px 0; color:white; font-size:20px;">
        🚀 Athlete2Athlete — Coming Soon
    </h3>
    <p style="margin:0 0 12px 0; color:rgba(255,255,255,0.85);
              font-size:15px; line-height:1.6;">
        Soon you will be able to submit your game footage directly to Mitch,
        Bryce, Nick, or Liam for a personal video review — and book a live
        30-minute Q&A session with a current college or professional player
        who plays your position.
    </p>
    <p style="margin:0; color:rgba(255,255,255,0.55); font-size:13px;">
        Reel Reviews · Live Q&A · Position-Specific Mentorship
    </p>
</div>
""", unsafe_allow_html=True)
