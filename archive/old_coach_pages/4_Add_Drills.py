"""Add Drills - Single drill form and bulk CSV import"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

import config
import drill_adder
import drills
import data_loader
import session_state
import forms
import ui_components
from auth import require_auth

st.set_page_config(page_title="Add Drills", page_icon="➕", layout="wide")

require_auth()
ui_components.require_page_access("pages/4_Add_Drills.py")

ui_components.render_nav(active_label="➕ Add Drills")
st.divider()

st.title("➕ Add Drills")
st.caption("Grow your demo library by adding an individual drill or importing many from CSV.")


session_state.init_session_state()

if 'data_path' not in st.session_state:
    st.session_state.data_path = config.get_data_path()

if st.session_state.drills_df is None:
    st.session_state.drills_df = data_loader.load_drills(st.session_state.data_path)

if st.session_state.teams_df is None:
    st.session_state.teams_df = data_loader.load_teams(st.session_state.data_path)

session_state.render_team_selector(
    label="Active team",
    widget_key="team_selector_add_drills",
    help_text="Switch teams to contextualize additions."
)

drills_df = st.session_state.drills_df

col_a, col_b, col_c = st.columns(3)
col_a.metric("Total drills", len(drills_df))
col_b.metric("Categories", drills_df['category'].nunique() if len(drills_df) else 0)

last_used = "—"
if "last_used_date" in drills_df.columns and len(drills_df):
    parsed_dates = pd.to_datetime(drills_df["last_used_date"], errors="coerce")
    if parsed_dates.notna().any():
        last_used = parsed_dates.max().strftime("%Y-%m-%d")

col_c.metric("Last updated", last_used)


st.divider()
st.subheader("Add a single drill")

default_suggested_id = drills.suggest_next_drill_id(drills_df)

with st.form("single_drill_form"):
    form_values = forms.render_drill_form(
        drill=None,
        allow_id_edit=True,
        key_prefix="add_drill",
        drill_id_placeholder=default_suggested_id
    )
    submitted = st.form_submit_button("Add drill")

if submitted:
    suggested_id = drills.suggest_next_drill_id(
        drills_df,
        category=form_values["category"]
    )
    payload = {
        "drill_id": form_values["drill_id"] or suggested_id,
        "drill_name": form_values["drill_name"],
        "category": form_values["category"],
        "description": form_values["description"],
        "players_min": form_values["players_min"],
        "players_max": form_values["players_max"],
        "duration_minutes": form_values["duration_minutes"],
        "field_type": form_values["field_type"],
        "setup_data": form_values["setup_data"],
        "equipment": ", ".join(form_values["equipment"]),
        "coaching_points": form_values["coaching_points"],
        "difficulty": form_values["difficulty"],
        "intensity": form_values["intensity"],
        "coach_rating": form_values["coach_rating"],
        "personal_notes": form_values["personal_notes"],
        "positions": "|".join(form_values["positions"]),
        "age_groups": "|".join(form_values["age_groups"]),
        "coach_cues": form_values["coach_cues"],
        "progression": form_values["progression"],
        "recommended_field_size": form_values["recommended_field_size"],
        "times_used": 0,
        "last_used_date": "",
        "tags": "|".join(form_values["tags"]),
        "is_favorite": bool(form_values["is_favorite"]),
    }

    success, message, updated_df = drill_adder.add_single_drill(
        payload,
        drills_df,
        st.session_state.data_path
    )

    if success and updated_df is not None:
        st.session_state.drills_df = updated_df
        drills_df = updated_df
        st.success(message)
    else:
        st.warning(message)

st.divider()
st.subheader("Bulk upload")

uploaded_file = st.file_uploader("Upload CSV", type="csv")

expected_columns = [
    "drill_id",
    "drill_name",
    "category",
    "description",
    "players_min",
    "players_max",
    "duration_minutes",
    "field_type",
    "setup_data",
    "equipment",
    "coaching_points",
    "difficulty",
    "intensity",
    "coach_rating",
    "personal_notes",
    "times_used",
    "last_used_date",
    "tags",
    "is_favorite",
]

if uploaded_file is not None:
    bulk_df = pd.read_csv(uploaded_file)
    missing_cols = [col for col in expected_columns if col not in bulk_df.columns]
    if missing_cols:
        st.error(f"Missing required columns: {', '.join(missing_cols)}")
    else:
        added = 0
        errors = []
        working_df = drills_df.copy()

        for idx, row in bulk_df.iterrows():
            drill_data = {col: row.get(col, "") for col in expected_columns}
            for key, value in drill_data.items():
                if pd.isna(value):
                    drill_data[key] = ""

            try:
                drill_data["players_min"] = int(drill_data["players_min"])
                drill_data["players_max"] = int(drill_data["players_max"])
                drill_data["duration_minutes"] = int(drill_data["duration_minutes"])
                drill_data["coach_rating"] = int(drill_data["coach_rating"])
                drill_data["times_used"] = int(drill_data.get("times_used", 0) or 0)
                drill_data["is_favorite"] = str(drill_data.get("is_favorite", "")).strip().lower() in {"1", "true", "yes"}
            except ValueError:
                errors.append(f"Row {idx + 1}: invalid numeric value")
                continue

            drill_data["tags"] = str(drill_data.get("tags", "") or "")

            success, message, updated_df = drill_adder.add_single_drill(
                drill_data,
                working_df,
                st.session_state.data_path
            )

            if success and updated_df is not None:
                working_df = updated_df
                added += 1
            else:
                errors.append(f"Row {idx + 1}: {message}")

        st.session_state.drills_df = working_df
        drills_df = working_df

        if added:
            st.success(f"Added {added} drills from CSV.")
        if errors:
            st.warning("Some rows could not be imported:\n- " + "\n- ".join(errors))

st.divider()
st.subheader("Library preview")
st.dataframe(
    drills_df.head(10)[
        [
            "drill_id",
            "drill_name",
            "category",
            "players_min",
            "players_max",
            "duration_minutes",
            "difficulty",
            "intensity",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)

with st.expander("Demo tips"):
    st.caption(
        "Use this page to quickly seed additional drills while demoing. "
        "Reset the data directory manually if you need a fresh start."
    )
