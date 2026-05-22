"""Edit Practice - dedicated editor for a single schedule event"""
import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from src import schedule as schedule_utils
from src.auth import require_auth
from src import ui_components

st.set_page_config(page_title="Edit Practice", page_icon="✏️", layout="wide")

require_auth()
ui_components.require_page_access("pages/6_Edit_Practice.py")

data_path = st.session_state.get("data_path")
edit_event_id = st.session_state.get("edit_event_id")
edit_team_id = st.session_state.get("edit_event_team_id")
return_page = st.session_state.get("edit_return_page", "5_Team_Hub.py")

st.title("Edit Practice")

# --- Validate context ---
if not data_path or not edit_team_id or not edit_event_id:
    st.error("No practice selected to edit.")
    if st.button("Back"):
        st.switch_page(f"pages/{return_page}")
    st.stop()

schedule_df = schedule_utils.load_team_schedule(edit_team_id, data_path)

if "event_id" not in schedule_df.columns:
    st.error("Schedule is missing event IDs.")
    st.stop()

mask = schedule_df["event_id"].astype(str) == str(edit_event_id)
if not mask.any():
    st.error("Could not find this event in the schedule.")
    st.stop()

event = schedule_df.loc[mask].iloc[0]

# --- Prefill fields ---
date_field = event.get("event_date") or event.get("date")
current_date = (
    pd.to_datetime(date_field).date() if date_field is not None and pd.notna(date_field) else datetime.date.today()
)
current_time_raw = event.get("start_time")
try:
    current_time = pd.to_datetime(current_time_raw).time() if current_time_raw is not None and pd.notna(current_time_raw) else datetime.time(17, 0)
except Exception:
    current_time = datetime.time(17, 0)
try:
    current_duration = int(event.get("duration_minutes", 90) or 90)
except Exception:
    current_duration = 90
current_type = event.get("event_type", "Practice")
current_location = event.get("location", "")
current_notes = event.get("notes", "")

with st.form(f"edit_practice_{edit_event_id}"):
    col1, col2, col3 = st.columns(3)
    with col1:
        new_date = st.date_input("Date", value=current_date)
    with col2:
        new_time = st.time_input("Start time", value=current_time)
    with col3:
        new_duration = st.number_input("Duration (min)", 15, 180, current_duration, 5)

    type_options = ["Practice", "Game", "Event", "Film", "Lift", "Recovery", "Walkthrough"]
    if current_type not in type_options:
        type_options.insert(0, current_type)
    new_type = st.selectbox(
        "Type",
        options=type_options,
        index=type_options.index(current_type) if current_type in type_options else 0,
    )

    new_location = st.text_input("Location", value=current_location)
    new_notes = st.text_area("Notes", value=current_notes)

    save = st.form_submit_button("Save")
    cancel = st.form_submit_button("Cancel")

if save:
    updates = {
        "event_date": new_date.isoformat(),
        "start_time": new_time.strftime("%H:%M"),
        "duration_minutes": new_duration,
        "event_type": new_type,
        "location": new_location,
        "notes": new_notes,
    }

    schedule_utils.update_schedule_event(
        team_id=edit_team_id,
        event_id=edit_event_id,
        updates=updates,
        data_path=data_path,
    )

    st.session_state.edit_event_id = None
    st.session_state.edit_event_team_id = None
    st.success("Practice updated.")
    st.switch_page(f"pages/{return_page}")

if cancel:
    st.session_state.edit_event_id = None
    st.session_state.edit_event_team_id = None
    st.switch_page(f"pages/{return_page}")
