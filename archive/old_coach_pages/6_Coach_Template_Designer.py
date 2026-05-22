"""Coach Template Designer - Simplified template builder for coaches"""
import streamlit as st
import pandas as pd
import sys
import json
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

import config
import data_loader
import templates
import practice_history
import session_state
import session_state as ui_session
import ui_components
from templates import BlockTemplate
from auth import require_auth

st.set_page_config(page_title="Template Designer", page_icon="🧩", layout="wide")

require_auth()
ui_components.require_page_access("pages/6_Coach_Template_Designer.py")

ui_components.render_nav(active_label="Template Designer")
st.divider()

st.title("Coach Template Designer")
st.caption("Create reusable practice templates from scratch or from past sessions")

session_state.init_session_state()

# Initialize data
if 'data_path' not in st.session_state:
    st.session_state.data_path = config.get_data_path()

if st.session_state.drills_df is None:
    st.session_state.drills_df = data_loader.load_drills(st.session_state.data_path)

if st.session_state.teams_df is None:
    st.session_state.teams_df = data_loader.load_teams(st.session_state.data_path)

if st.session_state.selected_team is None and len(st.session_state.teams_df) > 0:
    st.session_state.selected_team = st.session_state.teams_df.iloc[0].to_dict()

# Load existing templates
existing_templates = templates.load_block_templates()

# Two modes: Create New or Convert from Session
st.subheader("Choose Mode")
mode = st.radio(
    "How would you like to create your template?",
    options=["Create New Template", "Convert from Past Session"],
    help="Create from scratch or convert an existing session into a reusable template"
)

st.markdown("---")

# Block categories for drill selection
BLOCK_TYPES = {
    "warmup": "Warmup",
    "technical": "Technical",
    "tactical": "Tactical",
    "ssg": "Small-Sided Games",
    "conditioning": "Conditioning",
    "cooldown": "Cool Down"
}

CATEGORY_TO_BLOCK = {
    "Warmup": "warmup",
    "Technical": "technical",
    "Tactical": "tactical",
    "Small Sided Games": "ssg",
    "Conditioning": "conditioning",
    "Cool Down": "cooldown"
}


def _render_new_template_builder():
    """Build template from scratch"""
    st.markdown("### Create New Template")

    # Template metadata
    col1, col2 = st.columns(2)

    with col1:
        template_name = st.text_input(
            "Template Name *",
            placeholder="e.g., High Intensity Attack Practice",
            help="Give your template a descriptive name"
        )

    with col2:
        template_desc = st.text_input(
            "Description",
            placeholder="e.g., Focus on quick transitions and finishing",
            help="Brief description of what this template is for"
        )

    # Block configuration
    st.markdown("### Configure Blocks")
    st.caption("Select which blocks to include and set their durations")

    # Let user select which blocks to include
    included_blocks = st.multiselect(
        "Include Blocks",
        options=list(BLOCK_TYPES.keys()),
        default=["warmup", "technical", "ssg", "cooldown"],
        format_func=lambda x: BLOCK_TYPES[x],
        help="Select which blocks to include in your template. Warmup should be first, cooldown last."
    )

    # Block durations
    st.markdown("#### Block Durations")
    block_durations = {}

    cols = st.columns(3)
    for idx, block_type in enumerate(included_blocks):
        with cols[idx % 3]:
            default_duration = {
                "warmup": 10,
                "technical": 20,
                "tactical": 20,
                "ssg": 20,
                "conditioning": 10,
                "cooldown": 10
            }.get(block_type, 15)

            duration = st.number_input(
                f"{BLOCK_TYPES[block_type]} (minutes)",
                min_value=5,
                max_value=45,
                value=default_duration,
                step=5,
                key=f"dur_{block_type}"
            )
            block_durations[block_type] = duration

    # Drill selection per block
    st.markdown("### Select Drills for Each Block")

    drills_df = st.session_state.drills_df
    template_blocks = {}

    for block_type in included_blocks:
        with st.expander(f"**{BLOCK_TYPES[block_type]}** ({block_durations[block_type]} min)", expanded=False):
            # Filter drills by category
            # Map block type to category
            category_mapping = {
                "warmup": "Warmup",
                "technical": "Technical",
                "tactical": "Tactical",
                "ssg": "Small Sided Games",
                "conditioning": "Conditioning",
                "cooldown": "Cool Down"
            }

            category = category_mapping.get(block_type, block_type.title())

            # Filter drills
            block_drills = drills_df[drills_df['category'] == category].copy()

            if len(block_drills) == 0:
                st.warning(f"No drills found for {category} category")
                template_blocks[block_type] = []
                continue

            # Show drill selector
            st.caption(f"{len(block_drills)} available drills in {category}")

            selected_drill_ids = st.multiselect(
                f"Select drills for {BLOCK_TYPES[block_type]}",
                options=block_drills['drill_id'].tolist(),
                format_func=lambda x: f"{block_drills[block_drills['drill_id']==x]['drill_name'].iloc[0]} (ID: {x})",
                key=f"drills_{block_type}",
                help=f"Choose which drills to include in the {BLOCK_TYPES[block_type]} block"
            )

            template_blocks[block_type] = selected_drill_ids

            # Show selected count
            if selected_drill_ids:
                st.success(f"✓ {len(selected_drill_ids)} drill(s) selected")

    # Validation and save
    st.markdown("### Save Template")

    # Validation messages
    validation_errors = []

    if not template_name or template_name.strip() == "":
        validation_errors.append("Template name is required")

    if not included_blocks:
        validation_errors.append("At least one block must be included")

    # Check for warmup first / cooldown last
    if included_blocks:
        if "warmup" in included_blocks and included_blocks[0] != "warmup":
            validation_errors.append("⚠️ Warning: Warmup should be first")

        if "cooldown" in included_blocks and included_blocks[-1] != "cooldown":
            validation_errors.append("⚠️ Warning: Cooldown should be last")

    # Check if any blocks have no drills
    empty_blocks = [b for b in included_blocks if not template_blocks.get(b)]
    if empty_blocks:
        empty_names = [BLOCK_TYPES[b] for b in empty_blocks]
        validation_errors.append(f"⚠️ Warning: These blocks have no drills: {', '.join(empty_names)}")

    # Check for duplicate template name
    if template_name and any(t.name == template_name for t in existing_templates):
        validation_errors.append(f"⚠️ Warning: A template named '{template_name}' already exists and will be overwritten")

    # Show validation messages
    if validation_errors:
        for error in validation_errors:
            if error.startswith("⚠️"):
                st.warning(error)
            else:
                st.error(error)

    # Save button
    col_save, col_cancel = st.columns([1, 3])

    with col_save:
        can_save = template_name and template_name.strip() != "" and included_blocks

        if st.button("💾 Save Template", type="primary", disabled=not can_save, use_container_width=True):
            # Create template
            new_template = templates.BlockTemplate(
                name=template_name.strip(),
                description=template_desc.strip() if template_desc else "",
                blocks=template_blocks,
                block_durations=block_durations,
                repair_notes=[]
            )

            # Check if replacing existing
            existing_idx = None
            for idx, t in enumerate(existing_templates):
                if t.name == new_template.name:
                    existing_idx = idx
                    break

            if existing_idx is not None:
                # Replace existing
                existing_templates[existing_idx] = new_template
            else:
                # Add new
                existing_templates.append(new_template)

            # Save
            templates.save_block_templates(existing_templates)

            st.success(f"✓ Template '{template_name}' saved successfully!")
            st.balloons()

            # Clear form (optional - could navigate away instead)
            st.info("Template saved! You can now use it in the Practice Generator.")

    with col_cancel:
        if st.button("Clear Form"):
            st.rerun()


def _render_convert_from_session():
    """Convert past session to template"""
    st.markdown("### Convert from Past Session")

    if st.session_state.selected_team is None:
        st.warning("Please select a team first")
        return

    team_id = st.session_state.selected_team['team_id']

    # Load history
    history_mtime = practice_history.get_history_mtime(team_id, st.session_state.data_path)
    history_df = practice_history.load_practice_history(team_id, st.session_state.data_path, history_mtime)

    # Filter to sessions with structure
    if 'session_structure' not in history_df.columns:
        history_df['session_structure'] = ''

    structured_sessions = history_df[history_df['session_structure'] != ''].copy()

    if len(structured_sessions) == 0:
        st.info("📌 No sessions with detailed structure found. Generate new practices from the Practice Generator to create templates from them.")
        st.caption("Note: Only sessions created after Phase 2 update contain the structure needed for template conversion.")
        return

    # Select session
    st.markdown("#### Select Session")

    structured_sessions['session_date'] = pd.to_datetime(structured_sessions['session_date']).dt.date

    session_options = {}
    for _, row in structured_sessions.iterrows():
        session_title = str(row.get('session_title', '')).strip()
        session_name = row.get('session_name', '')
        display_name = session_title if session_title else session_name

        key = f"{row['session_date']} - {display_name} ({row.get('total_time', 0)} min)"
        session_options[key] = row

    selected_key = st.selectbox(
        "Choose a session to convert:",
        options=list(session_options.keys()),
        help="Select a past practice session to turn into a reusable template"
    )

    selected_row = session_options[selected_key]

    # Load session structure
    try:
        session_data = json.loads(selected_row['session_structure'])
    except (json.JSONDecodeError, Exception) as e:
        st.error(f"Failed to load session structure: {e}")
        return

    # Extract blocks and durations
    drills = session_data.get('drills', [])

    if not drills:
        st.warning("This session has no drills to convert")
        return

    # Group by block
    template_blocks = {}
    block_durations = {}

    for drill in drills:
        block = drill.get('block_type', 'technical')

        if block not in template_blocks:
            template_blocks[block] = []
            block_durations[block] = 0

        template_blocks[block].append(drill['drill_id'])
        block_durations[block] += drill.get('allocated_time', 0)

    # Show preview
    st.markdown("#### Template Preview")

    st.caption(f"Extracted {len(template_blocks)} block(s) from session")

    # Display blocks
    for block_type, drill_ids in template_blocks.items():
        with st.expander(f"**{BLOCK_TYPES.get(block_type, block_type.title())}** - {len(drill_ids)} drill(s), {block_durations[block_type]} min"):
            for drill_id in drill_ids:
                st.caption(f"• {drill_id}")

    # Editable metadata
    st.markdown("#### Template Details")

    col1, col2 = st.columns(2)

    with col1:
        session_title = str(selected_row.get('session_title', '')).strip()
        default_name = session_title if session_title else f"Template from {selected_row['session_date']}"

        template_name = st.text_input(
            "Template Name *",
            value=default_name,
            help="Give your template a descriptive name"
        )

    with col2:
        default_desc = f"Converted from session on {selected_row['session_date']}"
        if selected_row.get('coach_notes'):
            default_desc = str(selected_row['coach_notes'])[:100]

        template_desc = st.text_input(
            "Description",
            value=default_desc,
            help="Brief description of this template"
        )

    # Save
    st.markdown("#### Save Template")

    # Check for duplicate
    if template_name and any(t.name == template_name for t in existing_templates):
        st.warning(f"⚠️ A template named '{template_name}' already exists and will be overwritten")

    col_save, col_info = st.columns([1, 3])

    with col_save:
        if st.button("💾 Save as Template", type="primary", disabled=not template_name, use_container_width=True):
            # Create template
            new_template = templates.BlockTemplate(
                name=template_name.strip(),
                description=template_desc.strip(),
                blocks=template_blocks,
                block_durations=block_durations,
                repair_notes=[f"Converted from session {selected_row['session_date']}"]
            )

            # Check if replacing existing
            existing_idx = None
            for idx, t in enumerate(existing_templates):
                if t.name == new_template.name:
                    existing_idx = idx
                    break

            if existing_idx is not None:
                # Replace existing
                existing_templates[existing_idx] = new_template
            else:
                # Add new
                existing_templates.append(new_template)

            # Save
            templates.save_block_templates(existing_templates)

            st.success(f"✓ Template '{template_name}' created from session!")
            st.balloons()
            st.info("Template saved! You can now use it in the Practice Generator.")


# Render appropriate mode
if mode == "Create New Template":
    _render_new_template_builder()
else:
    _render_convert_from_session()

# Show existing templates
st.divider()

st.markdown("### Your Templates")

if not existing_templates:
    st.info("No templates created yet. Create your first template above!")
else:
    st.caption(f"{len(existing_templates)} template(s) available")

    for idx, template in enumerate(existing_templates):
        with st.expander(f"**{template.name}** - {len(template.blocks)} block(s)"):
            st.write(template.description or "No description")

            # Show blocks
            for block_type, drill_ids in template.blocks.items():
                duration = template.block_durations.get(block_type, 0)
                st.caption(f"• **{BLOCK_TYPES.get(block_type, block_type.title())}** ({duration} min): {len(drill_ids)} drill(s)")

            # Repair notes
            if template.repair_notes:
                st.warning("⚠️ " + " | ".join(template.repair_notes))

            # Delete button
            if st.button(f"🗑️ Delete Template", key=f"delete_{idx}", type="secondary"):
                existing_templates.pop(idx)
                templates.save_block_templates(existing_templates)
                st.success(f"Template '{template.name}' deleted")
                st.rerun()
