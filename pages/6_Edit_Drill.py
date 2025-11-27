"""Drill Editor - Edit or duplicate existing drills"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import config
import data_loader
import session_state
import forms
import ui_components
from drills import validate_drill_schema

st.set_page_config(page_title="Edit Drill", page_icon="✏️", layout="wide")

ui_components.render_nav(active_label="✏️ Edit Drill")

st.divider()

st.title("✏️ Drill Editor")
st.caption("Edit existing drills or duplicate templates for quick customization.")

session_state.init_session_state()

if 'data_path' not in st.session_state:
    st.session_state.data_path = config.get_data_path()

if st.session_state.drills_df is None:
    st.session_state.drills_df = data_loader.load_drills(st.session_state.data_path)

drill_df = st.session_state.drills_df

query_params = st.query_params
selected_id = query_params.get("drill_id")

if selected_id is None:
    selected_id = st.session_state.get("selected_drill_id")
else:
    selected_id = selected_id[0] if isinstance(selected_id, list) else selected_id
    st.session_state.selected_drill_id = selected_id

prefill_drill = st.session_state.get("prefill_drill")

if not selected_id and not prefill_drill:
    st.info("Select a drill to edit or duplicate.")
    drill_choices = [""] + drill_df['drill_id'].tolist()
    drill_labels = ["-- Choose a drill --"] + [
        f"{row.drill_name} ({row.drill_id})" for row in drill_df.itertuples()
    ]
    selection_index = st.selectbox(
        "Choose a drill",
        options=range(len(drill_choices)),
        format_func=lambda idx: drill_labels[idx]
    )
    if selection_index == 0:
        st.stop()
    selected_id = drill_choices[selection_index]
    st.session_state.selected_drill_id = selected_id

matching_drill = drill_df[drill_df['drill_id'] == selected_id] if selected_id else pd.DataFrame()

is_new_drill = False
if matching_drill.empty:
    if prefill_drill and (not selected_id or prefill_drill.get('drill_id') == selected_id):
        drill = pd.Series(prefill_drill)
        is_new_drill = True
    else:
        st.error(f"No drill found for ID `{selected_id}`. Return to the Drill Library and choose another drill.")
        st.page_link("pages/1_📚_Drill_Library.py", label="← Back to Drill Library")
        st.stop()
else:
    drill = matching_drill.iloc[0]

st.subheader(f"Editing: {drill['drill_name']} ({drill['drill_id']})")
st.caption("Adjust details below and save to update your library.")

meta_col1, meta_col2, meta_col3, meta_col4 = st.columns(4)
meta_col1.markdown("**Created Drill ID**")
meta_col1.markdown(drill['drill_id'])
meta_col2.markdown("**Category**")
meta_col2.markdown(drill['category'])
meta_col3.markdown("**Times Used**")
meta_col3.markdown(str(drill.get('times_used', 0)))
meta_col4.markdown("**Last Used**")
meta_col4.markdown(drill.get('last_used_date') or "—")

st.divider()
st.subheader("Drill Details")

with st.form("edit_drill_form"):
    form_values = forms.render_drill_form(
        drill=drill.to_dict(),
        allow_id_edit=is_new_drill,
        key_prefix="edit_drill"
    )
    submitted = st.form_submit_button("Save Changes", type="primary")

if submitted:
    errors = []
    if not form_values["drill_name"]:
        errors.append("Drill name is required.")
    if not form_values["description"]:
        errors.append("Description is required.")
    if form_values["players_min"] > form_values["players_max"]:
        errors.append("Min players cannot exceed max players.")

    if errors:
        for err in errors:
            st.error(err)
    else:
        drill_id_value = (
            form_values["drill_id"] if form_values["drill_id"] else drill['drill_id']
        )
        updated_values = {
            'drill_id': drill_id_value,
            'drill_name': form_values["drill_name"],
            'description': form_values["description"],
            'setup_data': form_values["setup_data"],
            'coaching_points': form_values["coaching_points"],
            'duration_minutes': form_values["duration_minutes"],
            'field_type': form_values["field_type"],
            'players_min': form_values["players_min"],
            'players_max': form_values["players_max"],
            'category': form_values["category"],
            'difficulty': form_values["difficulty"],
            'intensity': form_values["intensity"],
            'equipment': ", ".join(form_values["equipment"]),
            'tags': "|".join(form_values["tags"]),
            'positions': "|".join(form_values["positions"]),
            'age_groups': "|".join(form_values["age_groups"]),
            'coach_cues': form_values["coach_cues"],
            'progression': form_values["progression"],
            'recommended_field_size': form_values["recommended_field_size"],
            'coach_rating': form_values["coach_rating"],
            'personal_notes': form_values["personal_notes"],
            'is_favorite': form_values["is_favorite"],
            'times_used': drill.get('times_used', 0),
            'last_used_date': drill.get('last_used_date', '')
        }

        try:
            validate_drill_schema(updated_values)
        except Exception as exc:
            st.error(f"Validation failed: {exc}")
            st.stop()

        if is_new_drill or drill_id_value not in drill_df['drill_id'].values:
            drill_df = pd.concat([drill_df, pd.DataFrame([updated_values])], ignore_index=True)
            st.session_state.prefill_drill = None
            success_text = "Drill duplicated successfully."
        else:
            for key, value in updated_values.items():
                drill_df.loc[drill_df['drill_id'] == drill_id_value, key] = value
            success_text = "Drill updated successfully."

        drill_file = Path(st.session_state.data_path) / 'drill_library.csv'
        drill_df.to_csv(drill_file, index=False)
        st.session_state.drills_df = drill_df
        st.success(success_text)
st.page_link("pages/1_Drill_Library.py", label="← Back to Drill Library")
