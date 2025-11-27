"""Template Studio - create and edit session templates."""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import config
import data_loader
import templates
import practice_generator
import ui_components
import session_state
from difflib import unified_diff

st.set_page_config(page_title="Template Studio", page_icon="🧩", layout="wide")

ui_components.render_nav(active_label="🧩 Practice Templates (Advanced)")
st.divider()
st.title("🧩 Template Studio")
st.caption("Create and edit session templates used by the Practice Generator and Cycle Planner.")

session_state.init_session_state()

if "data_path" not in st.session_state:
    st.session_state.data_path = config.get_data_path()

template_list = data_loader.load_session_templates(st.session_state.data_path)
if st.session_state.get("drills_df") is None:
    st.session_state.drills_df = data_loader.load_drills(st.session_state.data_path)
template_issues = templates.validate_templates(template_list, st.session_state.drills_df)
template_names = ["New template"] + [tpl.name for tpl in template_list]

# Toggle to filter broken templates
show_broken_only = st.checkbox("Show only templates that need repair", value=False)
visible_templates = [
    tpl for tpl in template_list
    if not show_broken_only or (template_issues.get(tpl.name, {}).get("missing_drill_ids") or template_issues.get(tpl.name, {}).get("bad_durations"))
]
visible_names = ["New template"] + [tpl.name for tpl in visible_templates]

selected_name = st.selectbox("Select template", options=visible_names)

if selected_name == "New template":
    current_template = None
    default_blocks = pd.DataFrame([{"block_type": "warmup", "drill_ids": "", "duration_minutes": 10}])
    template_name = ""
    template_description = ""
    existing_template_blocks = {}
    existing_template_durations = {}
else:
    current_template = next((tpl for tpl in visible_templates if tpl.name == selected_name), None)
    template_name = current_template.name if current_template else ""
    template_description = current_template.description if current_template else ""
    existing_template_blocks = current_template.blocks if current_template else {}
    existing_template_durations = current_template.block_durations if current_template else {}
    rows = []
    blocks = current_template.blocks if current_template else {}
    durations = current_template.block_durations if current_template else {}
    for block_type, drill_ids in blocks.items():
        rows.append({
            "block_type": block_type,
            "drill_ids": "|".join(drill_ids) if isinstance(drill_ids, (list, tuple)) else str(drill_ids),
            "duration_minutes": durations.get(block_type, 0),
        })
    default_blocks = pd.DataFrame(rows) if rows else pd.DataFrame(
        [{"block_type": "warmup", "drill_ids": "", "duration_minutes": 10}]
    )

template_name = st.text_input("Template name", value=template_name, placeholder="e.g., High Press Session")
template_description = st.text_area("Description", value=template_description, height=80)
target_duration = st.number_input(
    "Target session duration (minutes, optional)",
    min_value=0,
    max_value=180,
    value=60,
    step=5,
    help="Used for validation. Leave as-is if you want soft warnings only."
)

st.markdown("### Blocks")
st.caption("Use pipe separators for multiple drills in a block. Warmup should be first; Cool Down last.")
                       
edited_blocks = st.data_editor(
    default_blocks,
    hide_index=True,
    use_container_width=True,
    num_rows="dynamic",
    column_config={
        "block_type": st.column_config.SelectboxColumn(
            "Block type",
            options=practice_generator.BLOCK_ORDER,
            help="Select the type of this block.",
        ),
        "drill_ids": st.column_config.TextColumn(
            "Default drill IDs (pipe-separated)",
            help="Optional: prefill specific drills, separated by '|'.",
        ),
        "duration_minutes": st.column_config.NumberColumn(
            "Default duration (min)",
            min_value=0,
            max_value=120,
            step=1,
        ),
    },
    key="template_blocks_editor",
)

if st.button("Save Template", type="primary"):
    if not template_name.strip():
        st.error("Template name is required.")
        st.stop()

    blocks_payload = {}
    durations_payload = {}
    validation_errors = []
    allowed_blocks = set(practice_generator.BLOCK_ORDER)

    for idx, row in edited_blocks.iterrows():
        block_type = str(row.get("block_type") or "").strip()
        if not block_type:
            validation_errors.append(f"Row {idx + 1}: Block type is required.")
            continue
        if block_type not in allowed_blocks:
            validation_errors.append(f"Row {idx + 1}: Invalid block type '{block_type}'.")
        drill_ids = [
            item.strip() for item in str(row.get("drill_ids", "") or "").split("|") if item.strip()
        ]
        try:
            duration_val = int(row.get("duration_minutes") or 0)
        except Exception:
            duration_val = 0
        if duration_val < 1:
            validation_errors.append(f"Row {idx + 1}: Duration must be at least 1 minute.")
        blocks_payload[block_type] = drill_ids
        durations_payload[block_type] = duration_val

    # Order validation
    block_sequence = list(blocks_payload.keys())
    if "warmup" in block_sequence and block_sequence[0] != "warmup":
        validation_errors.append("Warmup must be the first block.")
    if "cooldown" in block_sequence and block_sequence[-1] != "cooldown":
        validation_errors.append("Cooldown must be the last block.")

    total_duration = sum(durations_payload.values())
    if target_duration:
        if total_duration != target_duration:
            validation_errors.append(f"Template duration must sum to {target_duration} minutes. Currently: {total_duration} minutes.")
    else:
        if total_duration < 30:
            validation_errors.append(f"Warning: Total duration {total_duration} minutes seems low.")

    if validation_errors:
        st.error("Please fix the following issues before saving:\n- " + "\n- ".join(validation_errors))
        st.stop()

    # Diff preview for existing template
    if replaced and existing_template_blocks:
        diff_messages = []
        # block type differences
        old_blocks = set(existing_template_blocks.keys())
        new_blocks = set(blocks_payload.keys())
        added = new_blocks - old_blocks
        removed = old_blocks - new_blocks
        if added:
            diff_messages.append(f"Added blocks: {', '.join(sorted(added))}")
        if removed:
            diff_messages.append(f"Removed blocks: {', '.join(sorted(removed))}")
        # duration differences
        duration_changes = []
        for blk, dur in durations_payload.items():
            old_dur = existing_template_durations.get(blk)
            if old_dur is not None and dur != old_dur:
                duration_changes.append(f"{blk}: {old_dur} → {dur}")
        if duration_changes:
            diff_messages.append("Duration changes: " + "; ".join(duration_changes))
        if diff_messages:
            st.info("Template changes:\n- " + "\n- ".join(diff_messages))

    new_template = templates.BlockTemplate(
        name=template_name.strip(),
        description=template_description.strip(),
        blocks=blocks_payload,
        block_durations=durations_payload,
    )

    # Replace or add
    updated_templates = []
    replaced = False
    for tpl in template_list:
        if tpl.name == new_template.name:
            updated_templates.append(new_template)
            replaced = True
        else:
            updated_templates.append(tpl)
    if not replaced:
        updated_templates.append(new_template)

    # Save per-template backup of the previous version if it existed
    if replaced and selected_name != "New template":
        try:
            prev_version = next((tpl for tpl in template_list if tpl.name == new_template.name), None)
            if prev_version:
                templates.save_template_backup(prev_version)
        except Exception:
            pass

    templates.save_block_templates(updated_templates)
    st.success("Template saved.")
    st.experimental_rerun()
st.markdown("### Backups")
backup_dir = None
try:
    backup_dir = templates._backup_dir()
except Exception:
    backup_dir = None

if backup_dir and backup_dir.exists():
    per_template_backup_dir = backup_dir / (selected_name if selected_name != "New template" else "")
    if per_template_backup_dir.exists():
        backup_files = sorted(per_template_backup_dir.glob(f"{selected_name}_*.json"), reverse=True)
        if backup_files:
            selected_backup = st.selectbox(
                "Available backups for this template",
                options=backup_files,
                format_func=lambda p: p.name
            )
            if st.button("Restore selected backup"):
                try:
                    data = json.loads(selected_backup.read_text(encoding="utf-8"))
                    restored_template = templates.BlockTemplate(
                        name=data.get("name", "Untitled"),
                        description=data.get("description", ""),
                        blocks=data.get("blocks", {}),
                        block_durations=data.get("block_durations", {}) or {},
                    )
                    updated_templates = []
                    for tpl in template_list:
                        if tpl.name == restored_template.name:
                            updated_templates.append(restored_template)
                        else:
                            updated_templates.append(tpl)
                    templates.save_block_templates(updated_templates)
                    st.success(f"Restored {restored_template.name} from {selected_backup.name}")
                    st.experimental_rerun()
                except Exception as exc:
                    st.error(f"Failed to restore backup: {exc}")

st.divider()
st.markdown("### Your Templates")
if not template_list:
    st.caption("No templates created yet.")
else:
    for tpl in template_list:
        issue = template_issues.get(tpl.name, {}) if template_issues else {}
        status = "OK"
        if issue.get("missing_drill_ids") or issue.get("bad_durations"):
            status = "Needs repair"
        with st.expander(f"{tpl.name} ({status})"):
            st.caption(tpl.description or "No description")
            for block_type, drill_ids in tpl.blocks.items():
                duration = tpl.block_durations.get(block_type, 0)
                st.caption(f"• {block_type}: {len(drill_ids)} drills, {duration} min")
            if issue.get("missing_drill_ids"):
                st.warning("Missing drills: " + ", ".join(issue["missing_drill_ids"]))
            if issue.get("bad_durations"):
                st.warning("Bad durations in: " + ", ".join(issue["bad_durations"]))
