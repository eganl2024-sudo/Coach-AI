"""Practice Library - Favorite sessions for quick reuse"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import date

src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

import config
import practice_history
import data_loader
import session_state
import session_state as ui_session
import ui_components
import session_detail_view
from auth import require_auth

st.set_page_config(page_title="Practice Library", page_icon="⭐", layout="wide")

require_auth()
ui_components.require_page_access("pages/10_Practice_Library.py")

ui_components.render_nav(active_label="⭐ Practice Library")
st.divider()

st.title("⭐ Practice Library")
st.caption("Your saved favorite sessions for quick reuse and reference.")

session_state.init_session_state()
is_coach = ui_session.is_coach_mode()
is_dev = ui_session.is_developer_mode()

if 'data_path' not in st.session_state:
    st.session_state.data_path = config.get_data_path()

if st.session_state.drills_df is None:
    st.session_state.drills_df = data_loader.load_drills(st.session_state.data_path)

if st.session_state.teams_df is None:
    st.session_state.teams_df = data_loader.load_teams(st.session_state.data_path)

if st.session_state.selected_team is None and len(st.session_state.teams_df) > 0:
    st.session_state.selected_team = st.session_state.teams_df.iloc[0].to_dict()

if st.session_state.selected_team is None:
    st.warning("Please add a team to start using the Practice Library.")
    st.stop()

team = st.session_state.selected_team
team_id = team['team_id']
history_mtime = practice_history.get_history_mtime(team_id, st.session_state.data_path)
history_df = practice_history.load_practice_history(team_id, st.session_state.data_path, history_mtime).copy()

# Filter to favorites only
if 'is_favorite' not in history_df.columns:
    history_df['is_favorite'] = False

favorites_df = history_df[history_df['is_favorite'] == True].copy()

if len(favorites_df) == 0:
    st.info("You haven't saved any sessions yet. Go to Past Sessions and star your favorites!")
    st.page_link("pages/3_Practice_History.py", label="📅 Go to Past Sessions")
    st.stop()

# Convert dates for display
favorites_df['session_date'] = pd.to_datetime(favorites_df['session_date']).dt.date
today = pd.to_datetime('today').date()

# Check if viewing a session detail modal
if 'viewing_session' in st.session_state:
    session_to_view = st.session_state['viewing_session']

    st.markdown("---")
    st.markdown("## Session Details")

    # Render detail view
    session_detail_view.render_session_detail(
        session_to_view,
        team_id,
        st.session_state.data_path
    )

    st.markdown("---")

    # Close button
    if st.button("← Back to Practice Library", type="primary"):
        del st.session_state['viewing_session']
        st.rerun()

    st.stop()

# Collect all unique tags
all_tags = set()
for _, row in favorites_df.iterrows():
    tags = practice_history.parse_session_tags(row.get('session_tags', ''))
    all_tags.update(tags)

# Search and filter UI
st.subheader("Filter & Search")
col_search, col_tags = st.columns([2, 3])

with col_search:
    search_query = st.text_input(
        "Search by title",
        placeholder="Enter session title...",
        help="Search for sessions by their custom title"
    )

with col_tags:
    if all_tags:
        selected_tags = st.multiselect(
            "Filter by tags",
            options=sorted(all_tags),
            help="Filter sessions by tags"
        )
    else:
        selected_tags = []
        st.caption("💡 Add tags to your sessions to enable tag filtering")

# Apply filters
filtered_df = favorites_df.copy()

# Search filter
if search_query:
    # Search in both session_title and session_name
    filtered_df = filtered_df[
        filtered_df.apply(
            lambda row: (
                search_query.lower() in str(row.get('session_title', '')).lower() or
                search_query.lower() in str(row.get('session_name', '')).lower()
            ),
            axis=1
        )
    ]

# Tag filter
if selected_tags:
    filtered_df = filtered_df[
        filtered_df['session_tags'].apply(
            lambda tags_str: any(
                tag in practice_history.parse_session_tags(tags_str)
                for tag in selected_tags
            )
        )
    ]

# Sort by date (most recent first)
filtered_df = filtered_df.sort_values('session_date', ascending=False)

st.divider()

# Show count
st.subheader(f"Saved Sessions ({len(filtered_df)})")

if len(filtered_df) == 0:
    st.info("No sessions match your filters. Try adjusting your search or tag selection.")
    st.stop()

# Display each favorite session
for display_idx, (idx, row) in enumerate(filtered_df.iterrows()):
    session_date = row['session_date']
    session_name = row.get('session_name') or "Practice"
    session_title = str(row.get('session_title', '')).strip()
    total_time = row.get('total_time', 0)
    categories = row.get('categories', '')
    num_players = row.get('num_players', 0)
    coach_notes = str(row.get('coach_notes', '')).strip()
    session_tags = practice_history.parse_session_tags(row.get('session_tags', ''))

    # Display title if available, otherwise session_name
    display_name = session_title if session_title else session_name

    with st.container():
        # Main row
        main_cols = st.columns([0.5, 5, 1.5, 1.5])

        with main_cols[0]:
            # Star (filled since it's in library)
            if st.button("★", key=f"unfav_{display_idx}", help="Remove from Practice Library"):
                success = practice_history.set_session_favorite(
                    team_id,
                    session_date,
                    session_name,
                    False,
                    st.session_state.data_path
                )
                if success:
                    st.rerun()

        with main_cols[1]:
            st.markdown(f"**{session_date} — {display_name} ({total_time} min)**")
            st.caption(f"Categories: {categories or '—'} | Players: {num_players}")

            # Show tags if exists
            if session_tags:
                tags_str = " | ".join(session_tags)
                st.caption(f"🏷️ {tags_str}")

            # Show notes preview if exists
            if coach_notes:
                preview = coach_notes[:80] + ('...' if len(coach_notes) > 80 else '')
                st.caption(f"📝 {preview}")

        with main_cols[2]:
            if st.button("View Details", key=f"view_{display_idx}"):
                # Store session row in session state to trigger detail view
                st.session_state['viewing_session'] = row.to_dict()
                st.rerun()

        with main_cols[3]:
            if st.button("Remove", key=f"remove_{display_idx}", type="secondary"):
                success = practice_history.set_session_favorite(
                    team_id,
                    session_date,
                    session_name,
                    False,
                    st.session_state.data_path
                )
                if success:
                    st.rerun()

        # Notes viewing/editing section (expandable)
        with st.expander(f"📝 Session Notes", expanded=False):
            notes_value = st.text_area(
                "Session observations and notes",
                value=coach_notes,
                key=f"notes_{display_idx}",
                height=100,
                help="What worked well, areas for improvement, player feedback, etc."
            )

            col_save, col_info = st.columns([1, 3])
            with col_save:
                if st.button("Save Notes", key=f"save_notes_{display_idx}"):
                    success = practice_history.update_session_notes(
                        team_id,
                        session_date,
                        session_name,
                        notes_value,
                        st.session_state.data_path
                    )
                    if success:
                        st.success("Notes saved!")
                        st.rerun()
                    else:
                        st.error("Failed to save notes")

        st.divider()

st.divider()
st.caption(f"💡 Tip: Star sessions from Past Sessions to add them to your Practice Library")
