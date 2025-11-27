"""Schema Migration Helper - fill new drill fields in bulk"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import config
import data_loader
import session_state
import ui_components
from drills import validate_drill_schema

st.set_page_config(page_title="Schema Migration", page_icon="🧹", layout="wide")

ui_components.render_nav(active_label="🧹 Schema Migration")
st.divider()
st.title("🧹 Drill Schema Migration")
st.caption("Identify and fill missing new fields (positions, age_groups, field size, coach cues, progression).")

session_state.init_session_state()

if 'data_path' not in st.session_state:
    st.session_state.data_path = config.get_data_path()

if st.session_state.drills_df is None:
    st.session_state.drills_df = data_loader.load_drills(st.session_state.data_path)

drills_df = st.session_state.drills_df.copy()

target_fields = ["positions", "age_groups", "recommended_field_size", "coach_cues", "progression"]
defaults = {
    "positions": "GK|DEF|MID|FWD",
    "age_groups": "U9|U11|U13|U15|U17",
    "recommended_field_size": "half",
    "coach_cues": "",
    "progression": "",
}

missing_counts = {}
for field in target_fields:
    missing_counts[field] = drills_df[field].isna().sum() + (drills_df[field] == "").sum()

summary_cols = st.columns(len(target_fields))
for idx, field in enumerate(target_fields):
    summary_cols[idx].metric(field.replace("_", " ").title(), missing_counts[field])

st.divider()
st.subheader("Apply defaults to missing")
if st.button("Apply defaults to missing fields"):
    for field, default_val in defaults.items():
        mask = drills_df[field].fillna("").eq("")
        drills_df.loc[mask, field] = default_val
    st.session_state.drills_df = drills_df
    drills_df.to_csv(Path(st.session_state.data_path) / "drill_library.csv", index=False)
    st.success("Defaults applied and saved.")

st.divider()
st.subheader("Edit missing values")
missing_mask = drills_df[target_fields].apply(lambda row: any(str(val).strip() == "" for val in row), axis=1)
missing_rows = drills_df[missing_mask].copy()

if missing_rows.empty:
    st.success("No drills are missing the new schema fields.")
    st.stop()

edited = st.data_editor(
    missing_rows[target_fields + ["drill_id", "drill_name"]],
    hide_index=True,
    num_rows="dynamic",
    use_container_width=True,
    key="schema_editor",
)

st.caption("Tip: use pipe separators (e.g., GK|DEF) for list fields.")

if st.button("Save updates", type="primary"):
    try:
        for _, row in edited.iterrows():
            drill_id = row["drill_id"]
            for field in target_fields:
                drills_df.loc[drills_df["drill_id"] == drill_id, field] = row[field]
            validate_drill_schema(drills_df.loc[drills_df["drill_id"] == drill_id].iloc[0].to_dict())
        drills_df.to_csv(Path(st.session_state.data_path) / "drill_library.csv", index=False)
        st.session_state.drills_df = drills_df
        st.success("Updated drills saved.")
    except Exception as exc:
        st.error(f"Failed to save updates: {exc}")
