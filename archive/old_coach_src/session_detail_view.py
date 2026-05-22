"""Session Detail View - Rich display of past practice sessions."""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

import practice_generator
import practice_history
import templates
import diagram_renderer
from models import PracticeSession, SessionDrill


BLOCK_LABELS = {
    "warmup": "Warmup",
    "technical": "Technical Block",
    "tactical": "Tactical Block",
    "ssg": "Small-Sided Games",
    "conditioning": "Conditioning",
    "cooldown": "Cool Down",
}


def _get_drill_maps():
    """Return mappings for drill_id -> name/category for display."""
    name_map, category_map = {}, {}
    drills_df = st.session_state.get("drills_df")
    if drills_df is not None and "drill_id" in drills_df.columns:
        name_col = "drill_name" if "drill_name" in drills_df.columns else (
            "name" if "name" in drills_df.columns else None
        )
        if name_col:
            try:
                name_map = drills_df.set_index("drill_id")[name_col].to_dict()
            except Exception:
                name_map = {}
        if "category" in drills_df.columns:
            try:
                category_map = drills_df.set_index("drill_id")["category"].to_dict()
            except Exception:
                category_map = {}
    return name_map, category_map


def _resolve_block(drill):
    """Resolve block type from drill data."""
    block = getattr(drill, "block_type", None)
    if block:
        return block
    category = getattr(drill, "category", None)
    return practice_generator.CATEGORY_TO_BLOCK.get(category, "technical")


def _refresh_block_indices(drills):
    """Ensure block_index values are sequential within each block."""
    counters = {}
    for drill in drills:
        block_key = _resolve_block(drill)
        counters.setdefault(block_key, 0)
        drill.block_index = counters[block_key]
        counters[block_key] += 1


def _split_tags(cell):
    return [tag.strip() for tag in str(cell).split("|") if tag and tag.strip()]


def render_session_detail(session_row, team_id, data_path):
    """
    Render rich session detail panel.

    Args:
        session_row: Dictionary/Series from practice history DataFrame
        team_id: Team identifier
        data_path: Path to data directory
    """
    st.page_link("pages/3_Practice_History.py", label="< Back to Past Sessions")

    session_structure = session_row.get("session_structure", "")

    if session_structure:
        try:
            session_data = json.loads(session_structure)
            session_obj = practice_history.load_practice_session_from_record(session_row)
            _render_rich_session(session_data, session_obj, session_row, team_id, data_path)
        except Exception as e:
            st.error(f"Error loading session structure: {e}")
            _render_simple_session(session_row, team_id, data_path)
    else:
        _render_simple_session(session_row, team_id, data_path)


def _render_summary_card(session_date, total_time, num_players, session_title, is_favorite, session_row, team_id, data_path):
    with st.container():
        st.markdown(
            "<div style='padding:16px;border:1px solid #e5e7eb;border-radius:10px;background-color:#f9fafb;'>",
            unsafe_allow_html=True,
        )
        header_cols = st.columns([3, 1])
        with header_cols[0]:
            st.markdown(f"**{session_title}**")
            st.caption("Session summary")
        with header_cols[1]:
            fav_label = "Remove from Library" if is_favorite else "Add to Library"
            if st.button(fav_label, use_container_width=True, key=f"fav_toggle_{session_title}"):
                success = practice_history.set_session_favorite(
                    team_id,
                    session_row.get("session_date"),
                    session_row.get("session_name"),
                    not is_favorite,
                    data_path,
                )
                if success:
                    st.success("Favorite status updated!")
                    st.rerun()

        metric_cols = st.columns(3)
        metric_cols[0].metric("Date", str(session_date))
        metric_cols[1].metric("Duration", f"{total_time} min")
        metric_cols[2].metric("Players", num_players)

        action_cols = st.columns(2)
        return action_cols


def _render_selected_drills_read_only(drills):
    """Render a read-only view of drills mirroring the generator layout."""
    if not drills:
        st.info("No drills found in this session.")
        return

    _refresh_block_indices(drills)
    display_counter = 1
    for block_key in practice_generator.BLOCK_ORDER:
        block_drills = [
            (idx, drill) for idx, drill in enumerate(drills)
            if _resolve_block(drill) == block_key
        ]
        block_drills.sort(key=lambda item: item[0])
        if not block_drills:
            continue

        st.markdown(f"#### {BLOCK_LABELS.get(block_key, block_key.title())}")
        for _, drill in block_drills:
            st.divider()
            col_desc, col_details, col_diagram = st.columns([2, 1.2, 1.2])

            with col_desc:
                st.markdown(f"**{display_counter}. {drill.drill_name} ({drill.allocated_time} min)**")
                display_counter += 1
                if getattr(drill, "fallback", False):
                    st.warning("Fallback drill added due to limited options.", icon="⚠️")

                st.markdown("**Overview**")
                st.write(getattr(drill, "description", "") or "No description")
                st.markdown("**Coaching Points**")
                st.write(getattr(drill, "coaching_points", "") or "None")
                st.markdown("**Equipment**")
                st.write(getattr(drill, "equipment", "") or "None")

            with col_details:
                st.markdown("**Drill Details**")
                st.write(f"Category: {getattr(drill, 'category', '')}")
                intensity = getattr(drill, "intensity", "")
                intensity_text = intensity.title() if hasattr(intensity, "title") else intensity
                target = getattr(drill, "target_intensity", "")
                st.write(f"Intensity: {intensity_text}{f' (target {target})' if target else ''}")
                st.write(f"Players: {getattr(drill, 'players_min', 0)}-{getattr(drill, 'players_max', 0)}")
                st.write(f"Field: {getattr(drill, 'field_type', '') or 'N/A'}")
                st.write(f"Recency: {getattr(drill, 'recency_label', '') or 'New'}")
                tags_val = getattr(drill, "tags", "") or getattr(drill, "extras", {}).get("tags", "")
                if tags_val:
                    st.write(f"Tags: {', '.join(_split_tags(tags_val))}")
                positions_val = getattr(drill, "positions", "") or getattr(drill, "extras", {}).get("positions", "")
                if positions_val:
                    st.write(f"Positions: {positions_val}")
                age_groups_val = getattr(drill, "age_groups", "") or getattr(drill, "extras", {}).get("age_groups", "")
                if age_groups_val:
                    st.write(f"Age Groups: {age_groups_val}")

            with col_diagram:
                st.markdown("**Diagram**")
                rendered = diagram_renderer.render_diagram(getattr(drill, "drill_id", ""), getattr(drill, "diagram_path", ""))
                if not rendered:
                    st.caption("No diagram available yet.")


def _render_rich_session(session_data, session_obj, session_row, team_id, data_path):
    """
    Full session detail with blocks.

    Args:
        session_data: Deserialized PracticeSession.to_dict()
        session_obj: PracticeSession object rebuilt from history
        session_row: Row from history DataFrame
        team_id: Team identifier
        data_path: Path to data directory
    """
    st.markdown("### Session Details")

    session_date = session_row.get("session_date", "Unknown")
    total_time = session_obj.duration_minutes if session_obj else session_data.get("duration_minutes", 0)
    num_players = session_obj.num_players if session_obj else session_data.get("num_players", 0)
    session_title = (
        str(session_row.get("session_title", ""))
        or str(session_row.get("session_name", ""))
        or f"Session on {session_date}"
    ).strip()
    is_favorite = bool(session_row.get("is_favorite", False))

    action_cols = _render_summary_card(session_date, total_time, num_players, session_title, is_favorite, session_row, team_id, data_path)
    drills_list = session_obj.drills if session_obj else [SessionDrill.from_dict(d) for d in session_data.get("drills", [])]

    with action_cols[0]:
        if st.button("Reuse session", type="primary", use_container_width=True, key="summary_reuse"):
            import session_state as ui_session

            config = session_obj.config.to_dict() if session_obj else session_data.get("config", {})
            ui_session.set_practice_config(
                duration_minutes=config.get("duration_minutes", session_data.get("duration_minutes", 90)),
                num_players=config.get("num_players", session_data.get("num_players", 16)),
                num_drills=len(drills_list),
                selected_categories=config.get("selected_categories", session_data.get("selected_categories", [])),
                session_notes=config.get("session_notes", ""),
            )

            st.switch_page("pages/2_Practice_Generator.py")
    with action_cols[1]:
        st.page_link("pages/3_Practice_History.py", label="Back to Past Sessions", use_container_width=True)

    st.divider()

    # Edit title and tags
    with st.expander("Edit Title & Tags", expanded=False):
        current_title = str(session_row.get("session_title", "")).strip()
        current_tags = practice_history.parse_session_tags(session_row.get("session_tags", ""))

        new_title = st.text_input(
            "Session Title",
            value=current_title or session_row.get("session_name", ""),
            help="Give this session a memorable name",
        )

        tags_input = st.text_input(
            "Tags (comma-separated)",
            value=", ".join(current_tags),
            help="Add tags like: passing, defensive, high-intensity",
        )

        col_save, _ = st.columns([1, 3])
        with col_save:
            if st.button("Save Title & Tags", type="primary"):
                new_tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]

                title_success = practice_history.update_session_title(
                    team_id,
                    session_row.get("session_date"),
                    session_row.get("session_name"),
                    new_title,
                    data_path,
                )

                tags_success = practice_history.update_session_tags(
                    team_id,
                    session_row.get("session_date"),
                    session_row.get("session_name"),
                    new_tags,
                    data_path,
                )

                if title_success and tags_success:
                    st.success("Title and tags updated!")
                    st.rerun()
                else:
                    st.error("Failed to update title or tags")

    # Coach notes card
    coach_notes = str(session_row.get("coach_notes", "")).strip()
    with st.expander("Coach Notes", expanded=False):
        st.caption("What did you notice in this session?")
        notes_value = st.text_area(
            "Notes",
            value=coach_notes,
            height=120,
            help="Add observations, what worked well, areas for improvement, etc.",
        )
        right_align = st.columns([3, 1])
        with right_align[1]:
            if st.button("Save Notes", key="save_notes_detail"):
                success = practice_history.update_session_notes(
                    team_id,
                    session_row.get("session_date"),
                    session_row.get("session_name"),
                    notes_value,
                    data_path,
                )
                if success:
                    st.success("Notes saved!")
                    st.rerun()
                else:
                    st.error("Failed to save notes")

    if coach_notes:
        st.info(coach_notes)

    st.divider()

    # Drills used overview
    name_map, category_map = _get_drill_maps()
    if drills_list:
        st.markdown("#### Drills Used")
        for drill in drills_list:
            drill_id = getattr(drill, "drill_id", "")
            drill_name = getattr(drill, "drill_name", "") or name_map.get(drill_id, drill_id or "Unknown Drill")
            minutes = getattr(drill, "allocated_time", 0)
            category = getattr(drill, "category", "") or category_map.get(drill_id, "")
            meta_bits = []
            if category:
                meta_bits.append(category.title())
            if minutes:
                meta_bits.append(f"{minutes} min")
            meta_text = " | ".join(meta_bits)
            line = f"- **{drill_name}**"
            if meta_text:
                line += f"  _{meta_text}_"
            st.markdown(line)

        st.divider()

    # Practice structure (read-only mirror of generator layout)
    st.markdown("### Practice Structure")
    _render_selected_drills_read_only(drills_list)

    st.divider()

    # Action buttons
    st.markdown("### Actions")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Reuse this session", use_container_width=True, key="reuse_bottom"):
            import session_state as ui_session

            config = session_obj.config.to_dict() if session_obj else session_data.get("config", {})
            ui_session.set_practice_config(
                duration_minutes=config.get("duration_minutes", session_data.get("duration_minutes", 90)),
                num_players=config.get("num_players", session_data.get("num_players", 16)),
                num_drills=len(drills_list),
                selected_categories=config.get("selected_categories", session_data.get("selected_categories", [])),
                session_notes=config.get("session_notes", ""),
            )

            st.switch_page("pages/2_Practice_Generator.py")

    with col2:
        if st.button("Convert to Template", use_container_width=True, key="convert_template"):
            template_blocks = {}
            block_durations = {}

            for block_type in practice_generator.BLOCK_ORDER:
                block_drills = [d for d in drills_list if _resolve_block(d) == block_type]
                if not block_drills:
                    continue
                template_blocks[block_type] = [getattr(d, "drill_id", "") for d in block_drills]
                block_durations[block_type] = sum(getattr(d, "allocated_time", 0) for d in block_drills)

            template_name = st.text_input(
                "Template Name",
                value=session_row.get("session_title", "")
                or f"Template from {session_row.get('session_date', '')}",
                key="template_name_input",
            )

            if st.button("Create Template", type="primary", key="create_template_btn"):
                from models import BlockTemplate

                new_template = templates.BlockTemplate(
                    name=template_name,
                    description=f"Converted from session on {session_row.get('session_date', '')}",
                    blocks=template_blocks,
                    block_durations=block_durations,
                    repair_notes=[f"Auto-converted from session {session_row.get('session_date', '')}"],
                )

                existing_templates = templates.load_block_templates()
                existing_templates.append(new_template)
                templates.save_block_templates(existing_templates)

                st.success(f"Template '{template_name}' created!")


def _render_simple_session(session_row, team_id, data_path):
    """
    Fallback view for old sessions without structure.

    Args:
        session_row: Row from history DataFrame
        team_id: Team identifier
        data_path: Path to data directory
    """
    st.markdown("### Session Details")
    st.info("Limited details - this session was created before detailed structure tracking. Showing basic information only.")

    session_date = session_row.get("session_date", "Unknown")
    total_time = session_row.get("total_time", 0)
    num_players = session_row.get("num_players", 0)
    is_favorite = bool(session_row.get("is_favorite", False))
    session_title = (
        str(session_row.get("session_title", ""))
        or str(session_row.get("session_name", ""))
        or f"Session on {session_date}"
    ).strip()

    action_cols = _render_summary_card(
        session_date, total_time, num_players, session_title, is_favorite, session_row, team_id, data_path
    )

    with action_cols[0]:
        if st.button("Reuse config", type="primary", use_container_width=True, key="legacy_reuse"):
            import session_state as ui_session

            categories = session_row.get("categories", "")
            cat_list = [c.strip() for c in str(categories).split("|") if c.strip()]

            ui_session.set_practice_config(
                duration_minutes=int(session_row.get("total_time", 90)),
                num_players=int(session_row.get("num_players", 16)),
                num_drills=5,
                selected_categories=cat_list,
                session_notes="",
            )

            st.switch_page("pages/2_Practice_Generator.py")
    with action_cols[1]:
        st.page_link("pages/3_Practice_History.py", label="Back to Past Sessions", use_container_width=True)

    st.divider()

    drills_used = session_row.get("drills_used", "")
    if drills_used:
        drill_ids = [d.strip() for d in str(drills_used).split("|") if d.strip()]
        st.markdown(f"**Drills Used:** {len(drill_ids)}")

        name_map, category_map = _get_drill_maps()

        for drill_id in drill_ids:
            label = name_map.get(drill_id, drill_id)
            category = category_map.get(drill_id, "")
            meta_bits = []
            if category:
                meta_bits.append(category.title())
            meta_text = f" _{' | '.join(meta_bits)}_" if meta_bits else ""
            st.markdown(f"- **{label}**{meta_text}")

    categories = session_row.get("categories", "")
    if categories:
        cat_list = [c.strip() for c in str(categories).split("|") if c.strip()]
        st.markdown("**Categories:**")
        st.caption(" | ".join(cat_list))

    st.divider()

    coach_notes = str(session_row.get("coach_notes", "")).strip()
    with st.expander("Coach Notes", expanded=False):
        st.caption("What did you notice in this session?")
        notes_value = st.text_area(
            "Notes",
            value=coach_notes,
            height=120,
        )

        right_align = st.columns([3, 1])
        with right_align[1]:
            if st.button("Save Notes", key="save_notes_legacy"):
                success = practice_history.update_session_notes(
                    team_id,
                    session_row.get("session_date"),
                    session_row.get("session_name"),
                    notes_value,
                    data_path,
                )
                if success:
                    st.success("Notes saved!")
                    st.rerun()
                else:
                    st.error("Failed to save notes")

    if coach_notes:
        st.info(coach_notes)
