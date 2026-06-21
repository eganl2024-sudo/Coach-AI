"""Player AI - Drill Library"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import importlib
import config
import data_loader
import session_state
import ui_components
import experience_level

# Force reload of custom modules to clear Streamlit's running process cache
try:
    importlib.reload(config)
    importlib.reload(data_loader)
    importlib.reload(session_state)
    importlib.reload(ui_components)
    importlib.reload(experience_level)
except Exception:
    pass

from auth import require_auth


def _split_tags(cell):
    return [tag.strip() for tag in str(cell).split("|") if tag and tag.strip()]


# Enforce player-focused defaults
FILTER_DEFAULTS = {
    "categories": ["All"],
    "difficulty": ["All"],
    "intensity": ["All"],
    "tags": ["All"],
    "position_relevance": ["All"],
    "skill_category": ["All"],
    "solo_only": False,
    "search": "",
    "favorites_only": False,
    "hide_recent": False,
    "sort": "Most Recent",
}

FILTER_WIDGET_KEYS = {
    "categories": "library_filter_categories",
    "difficulty": "library_filter_difficulty",
    "intensity": "library_filter_intensity",
    "tags": "library_filter_tags",
    "position_relevance": "library_filter_position_relevance",
    "skill_category": "library_filter_skill_category",
    "solo_only": "library_filter_solo_only",
    "search": "library_filter_search",
    "favorites_only": "library_filter_favorites",
    "hide_recent": "library_filter_hide_recent",
    "sort": "library_filter_sort",
}


def _persist_drills(df):
    data_path = st.session_state.get('data_path')
    if not data_path:
        return
    drill_file = Path(data_path) / 'drill_library.csv'
    df.to_csv(drill_file, index=False)
    st.session_state.drills_df = df


# Page setup
st.set_page_config(page_title="Drill Library | Player AI", page_icon="🔍", layout="wide")

require_auth()

st.session_state.drills_browsed = True

# Navigation
ui_components.render_nav(active_label="Drill Library")
st.divider()

st.title("🔍 Drill Library")
st.write("Browse and filter our comprehensive collection of training drills to practice your skills.")

# Inject premium styles for presenter badges, contexts, and mistake cues
st.markdown(
    """
    <style>
    .presenter-badge {
        display: inline-flex;
        align-items: center;
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .context-card {
        background-color: #F8FAFC;
        border-left: 4px solid #3B82F6;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin: 12px 0;
    }
    .context-pro {
        border-left-color: #10B981;
        background-color: #F0FDF4;
    }
    .context-college {
        border-left-color: #3B82F6;
        background-color: #EFF6FF;
    }
    .context-title {
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 4px;
        color: #1E293B;
    }
    .context-text {
        font-size: 0.85rem;
        color: #475569;
        line-height: 1.4;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Contextual Hints - Gated by player experience level
current_level = experience_level.get_experience_level()
is_advanced = current_level == "advanced"
is_expert = current_level == "expert"

session_state.init_session_state()

if 'data_path' not in st.session_state:
    st.session_state.data_path = config.get_data_path()

session_state.init_drills_in_session_state(st.session_state.data_path)

drills_df = st.session_state.drills_df
if drills_df is None or len(drills_df) == 0:
    st.info("Starter drills are being loaded. Add custom drills to tailor your library!")
    st.stop()

# Load Athlete Profile for personal recommendations
athlete_profile = st.session_state.get("athlete_profile") or \
    data_loader.load_athlete_profile(st.session_state.data_path)

if athlete_profile and athlete_profile.get("focus_areas"):
    focus_areas = athlete_profile.get("focus_areas", [])
    with st.expander("🎯 Personal Recommendations", expanded=True):
        st.write(f"Drills matching your focus areas: **{', '.join(focus_areas)}**")
        tag_set = {t.lower() for t in focus_areas}
        recommended_drills = []
        for _, drill in drills_df.iterrows():
            drill_tags = {tag.strip().lower() for tag in str(drill.get('tags', '')).split("|") if tag.strip()}
            if drill_tags.intersection(tag_set):
                recommended_drills.append(drill)
            if len(recommended_drills) >= 5:
                break
        
        if recommended_drills:
            rec_cols = st.columns(len(recommended_drills))
            for idx, r_drill in enumerate(recommended_drills):
                with rec_cols[idx]:
                    st.markdown(f"**{r_drill['drill_name']}**")
                    st.caption(f"{r_drill['category']} • {r_drill['duration_minutes']} min")
                    st.caption(f"Solo: {'Yes' if r_drill.get('solo_possible') else 'No'}")
        else:
            st.info("No matching drills found. Add matching tags to your profile focus areas to unlock custom suggestions!")
else:
    st.info("Set up your player profile to get personalized drill recommendations.")

# Library Overview metrics
st.subheader("Library Overview")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Drills Available", len(drills_df))
with col2:
    avg_duration = int(drills_df['duration_minutes'].mean()) if len(drills_df) > 0 else 0
    st.metric("Average Duration", f"{avg_duration} min")
with col3:
    avg_rating = round(drills_df['coach_rating'].mean(), 1) if len(drills_df) > 0 else 0.0
    st.metric("Average Rating", f"{'⭐' * int(avg_rating)} ({avg_rating})")
with col4:
    unique_categories = drills_df['category'].nunique() if len(drills_df) > 0 else 0
    st.metric("Categories", unique_categories)

st.divider()

# Initialize filter state
if 'library_filters' not in st.session_state:
    st.session_state.library_filters = FILTER_DEFAULTS.copy()

for field, key in FILTER_WIDGET_KEYS.items():
    if key not in st.session_state:
        st.session_state[key] = st.session_state.library_filters.get(field, FILTER_DEFAULTS.get(field))

filter_state = st.session_state.library_filters
sort_options = ["Most Recent", "Highest Rated", "Alphabetical"]

# Filter widget layouts
with st.expander("🔍 Advanced Filters & Sorting", expanded=True):
    col_cat, col_diff, col_int, col_tag = st.columns(4)
    category_filter = col_cat.multiselect("Category", options=['All'] + config.CATEGORIES, default=filter_state.get("categories", ["All"]), key=FILTER_WIDGET_KEYS["categories"])
    difficulty_filter = col_diff.multiselect("Difficulty", options=['All'] + config.DIFFICULTY_LEVELS, default=filter_state.get("difficulty", ["All"]), key=FILTER_WIDGET_KEYS["difficulty"])
    intensity_filter = col_int.multiselect("Intensity", options=['All'] + config.INTENSITY_LEVELS, default=filter_state.get("intensity", ["All"]), key=FILTER_WIDGET_KEYS["intensity"])
    
    all_tags = set()
    for tags_str in drills_df.get('tags', pd.Series([], dtype=str)).fillna(''):
        all_tags.update(_split_tags(tags_str))
    tag_filter_options = sorted(all_tags.union(set(config.DRILL_TAGS)))
    tag_filter_choices = ['All'] + tag_filter_options if tag_filter_options else ['All']
    tag_filter = col_tag.multiselect("Tags", options=tag_filter_choices, default=filter_state.get("tags", ["All"]), key=FILTER_WIDGET_KEYS["tags"])
    
    # 3 Pivot Filters (Position, Skill Category, Solo Possible)
    col_pos, col_skill, col_solo, col_sort = st.columns(4)
    position_filter = col_pos.multiselect(
        "Position Relevance",
        options=[
            'All', 'Goalkeeper', 'Center Back', 'Full Back',
            'Defensive Midfielder', 'Central Midfielder',
            'Attacking Midfielder', 'Winger', 'Striker'
        ],
        default=filter_state.get("position_relevance", ["All"]),
        key=FILTER_WIDGET_KEYS["position_relevance"]
    )
    skill_category_filter = col_skill.multiselect("Skill Category", options=['All', 'Technical', 'Tactical', 'Physical', 'Mental'], default=filter_state.get("skill_category", ["All"]), key=FILTER_WIDGET_KEYS["skill_category"])
    solo_only = col_solo.toggle("Solo Possible Only", value=filter_state.get("solo_only", False), key=FILTER_WIDGET_KEYS["solo_only"])
    sort_choice = col_sort.selectbox("Sort by", options=sort_options, index=sort_options.index(filter_state.get("sort", "Most Recent")) if filter_state.get("sort") in sort_options else 0, key=FILTER_WIDGET_KEYS["sort"])
    
    col_search, col_fav, col_rec = st.columns([2, 1, 1])
    search_query = col_search.text_input("Search Drill Name", placeholder="e.g. Cone Weave", value=filter_state.get("search", ""), key=FILTER_WIDGET_KEYS["search"])
    favorites_only = col_fav.toggle("⭐ Favorites Only", value=filter_state.get("favorites_only", False), key=FILTER_WIDGET_KEYS["favorites_only"])
    hide_recent = col_rec.toggle("🔄 Hide Recently Practiced", value=filter_state.get("hide_recent", False), key=FILTER_WIDGET_KEYS["hide_recent"])

    # Clear filters button
    if st.button("Clear Filters", use_container_width=True):
        st.session_state.library_filters = FILTER_DEFAULTS.copy()
        for field, key in FILTER_WIDGET_KEYS.items():
            if key in st.session_state:
                st.session_state[key] = FILTER_DEFAULTS[field]
        st.rerun()

# Apply Filters to dataframe
filtered_df = drills_df.copy()

if 'All' not in category_filter and len(category_filter) > 0:
    filtered_df = filtered_df[filtered_df['category'].isin(category_filter)]

if 'All' not in difficulty_filter and len(difficulty_filter) > 0:
    filtered_df = filtered_df[filtered_df['difficulty'].isin(difficulty_filter)]

if 'All' not in intensity_filter and len(intensity_filter) > 0:
    filtered_df = filtered_df[filtered_df['intensity'].isin(intensity_filter)]

if search_query:
    filtered_df = filtered_df[filtered_df['drill_name'].str.contains(search_query, case=False, na=False, regex=False)]

if 'All' not in tag_filter and len(tag_filter) > 0:
    tag_set = set(tag_filter)
    filtered_df = filtered_df[filtered_df['tags'].apply(lambda cell: bool(set(_split_tags(cell)).intersection(tag_set)))]

# Position relevance filter
if 'All' not in position_filter and len(position_filter) > 0:
    def matches_position(cell):
        if not cell or pd.isna(cell):
            return False
        parts = [p.strip().lower() for p in str(cell).split("|") if p.strip()]
        if 'universal' in parts or 'all' in parts:
            return True
        return any(pos.lower() in parts for pos in position_filter)
    filtered_df = filtered_df[filtered_df['position_relevance'].apply(matches_position)]

# Skill Category filter
if 'All' not in skill_category_filter and len(skill_category_filter) > 0:
    filtered_df = filtered_df[filtered_df['skill_category'].isin(skill_category_filter)]

# Solo filter
if solo_only:
    filtered_df = filtered_df[filtered_df['solo_possible'] == True]

if favorites_only:
    filtered_df = filtered_df[filtered_df['is_favorite'] == True]

# Sort results
if len(filtered_df) > 0:
    if sort_choice == "Most Recent":
        filtered_df['__last_used'] = pd.to_datetime(filtered_df.get('last_used_date'), errors='coerce')
        filtered_df = filtered_df.sort_values('__last_used', ascending=False, na_position='last')
        filtered_df = filtered_df.drop(columns=['__last_used'])
    elif sort_choice == "Highest Rated":
        filtered_df = filtered_df.sort_values('coach_rating', ascending=False)
    elif sort_choice == "Alphabetical":
        filtered_df = filtered_df.sort_values('drill_name', ascending=True)

# Render Drill Lists
st.subheader(f"Drills ({len(filtered_df)} found)")

def render_drill_card(drill, drills_df):
    favorite_icon = "⭐ " if drill.get('is_favorite') else ""
    with st.expander(f"{favorite_icon}{drill['drill_name']} ({drill['duration_minutes']} min)"):
        col_main, col_meta = st.columns([2, 1])

        # Presenter Badge lookup
        presenter_id = drill.get("presenter_id", "")
        presenter_badge_html = ""
        if presenter_id and "presenters_df" in st.session_state:
            df_p = st.session_state.presenters_df
            match = df_p[df_p["presenter_id"] == presenter_id]
            if not match.empty:
                p_row = match.iloc[0]
                d_name = p_row.get("display_name", "")
                t_level = p_row.get("team_level", "")
                badge_text = f"🎥 Lead Presenter: {d_name} ({t_level})" if t_level else f"🎥 Lead Presenter: {d_name}"
                presenter_badge_html = f'<div class="presenter-badge">{badge_text}</div>'

        with col_main:
            if presenter_badge_html:
                st.markdown(presenter_badge_html, unsafe_allow_html=True)

            st.markdown(f"**Description:** {drill['description']}")
            st.markdown(f"**Training Tips:** {drill['coaching_points']}")
            
            # Coaching cues
            cues_str = drill.get('coaching_cues') or drill.get('coach_cues') or ''
            cues_list = [c.strip() for c in str(cues_str).split('|') if c.strip()]
            if cues_list:
                st.markdown("**Key Focus Cues:**")
                for cue in cues_list:
                    st.markdown(f"- {cue}")
            
            # Common Mistakes (Clarification 2)
            common_mistakes = drill.get("common_mistakes", "")
            if common_mistakes:
                st.markdown("**Common Mistakes:**")
                for mistake in [m.strip() for m in common_mistakes.split("|") if m.strip()]:
                    st.markdown(f"⚠️ {mistake}")

            # Game Application Callout
            if drill.get('game_application'):
                st.info(f"⚽ **Game Application:** {drill['game_application']}")

            # College/Pro Context Cards
            if drill.get("college_context"):
                st.markdown(
                    f'<div class="context-card context-college">'
                    f'<div class="context-title">🎓 College Playing Context</div>'
                    f'<div class="context-text">{drill["college_context"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            if drill.get("pro_context"):
                st.markdown(
                    f'<div class="context-card context-pro">'
                    f'<div class="context-title">⚽ Pro Playing Context</div>'
                    f'<div class="context-text">{drill["pro_context"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            if drill['equipment']:
                st.markdown(f"**Equipment:** {drill['equipment']}")
            if drill.get('min_equipment'):
                st.markdown(f"**Minimum Gear:** {drill['min_equipment']}")
                
            st.markdown(f"**Setup Instructions:** {drill['setup_data']}")
            
            # Video player integration
            st.markdown("**Video Demonstration:**")
            ui_components.render_video(drill.get('video_url') or drill.get('video_youtube_url'))

            # Setup Diagram
            diagram_path = str(drill.get('diagram_path', '') or '').strip()
            if diagram_path:
                diagram_file = config.get_diagram_file(diagram_path)
                st.markdown("**Setup Diagram:**")
                if diagram_file and diagram_file.exists():
                    st.image(str(diagram_file), use_column_width=True)
                else:
                    st.caption("Diagram coming soon.")

        with col_meta:
            # Position Relevance
            pos_rel = drill.get('position_relevance') or ''
            pos_list = [p.strip() for p in str(pos_rel).split('|') if p.strip()]
            st.markdown(f"**Positions:** {', '.join(pos_list) if pos_list else 'Universal'}")
            
            st.markdown(f"**Skill Category:** {drill.get('skill_category', 'Technical')}")
            st.markdown(f"**Solo Friendly:** {'Yes ✅' if drill.get('solo_possible') else 'Requires Partner'}")
            st.markdown(f"**Duration:** {drill['duration_minutes']} min")
            st.markdown(f"**Difficulty:** {drill['difficulty'].title()}")
            st.markdown(f"**Intensity:** {drill['intensity'].title()}")
            
            if drill.get("position_track"):
                st.markdown(f"**Track:** {drill['position_track']}")
            if drill.get("series_name"):
                order_suffix = f" (#{drill['series_order']})" if drill.get("series_order") else ""
                st.markdown(f"**Series:** {drill['series_name']}{order_suffix}")
            if drill.get("rrs_benchmark"):
                st.markdown(f"**Level:** {drill['rrs_benchmark']}")

            favorite_state = bool(drill.get('is_favorite', False))
            new_favorite = st.checkbox("⭐ Save to Favorites", value=favorite_state, key=f"favorite_{drill['drill_id']}")
            if new_favorite != favorite_state:
                drills_df.loc[drills_df['drill_id'] == drill['drill_id'], 'is_favorite'] = new_favorite
                _persist_drills(drills_df)
                st.rerun()

            rating = drill.get('coach_rating')
            if pd.notna(rating):
                st.markdown(f"**Drill Rating:** {'⭐' * int(rating)}")


if len(filtered_df) > 0:
    categories = sorted(filtered_df['category'].unique())
    if len(categories) > 1:
        tabs = st.tabs(categories)
        for idx, category in enumerate(categories):
            with tabs[idx]:
                category_drills = filtered_df[filtered_df['category'] == category]
                st.markdown(f"**{len(category_drills)} {category} drills**")
                for _, drill in category_drills.iterrows():
                    render_drill_card(drill, drills_df)
    else:
        for _, drill in filtered_df.iterrows():
            render_drill_card(drill, drills_df)
else:
    st.warning("No drills found matching your filters. Try adjusting the filters above.")

st.divider()
st.caption(f"Showing {len(filtered_df)} of {len(drills_df)} total drills")
