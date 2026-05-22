"""Developer Tools (Danger Zone) - clean up test data."""
from pathlib import Path
import pandas as pd
import streamlit as st

# Add src to path
import sys
from pathlib import Path as P
sys.path.insert(0, str(P(__file__).parent.parent / "src"))

import config
import practice_history
from auth import require_auth


st.set_page_config(page_title="Developer Tools", page_icon="🛠️", layout="wide")

require_auth()
from src import ui_components
ui_components.require_page_access("pages/9_Developer_Tools.py")

# Dev-only guard
if not getattr(config, "DEV_MODE", False) and not st.session_state.get("debug_mode", False):
    st.title("Developer Tools")
    st.info("Developer tools are disabled. Enable DEV_MODE or debug_mode to access this page.")
    st.stop()

st.title("Developer Tools (Danger Zone)")
st.caption("Clean up test sessions. Actions are irreversible—use with caution.")

with st.expander("Session Management", expanded=True):
    teams_df = st.session_state.get("teams_df")
    if teams_df is None or teams_df.empty:
        st.warning("No teams loaded. Go to My Team to add a team first.")
        st.stop()

    team_options = teams_df["team_name"].astype(str).tolist()
    selected_label = st.selectbox("Select team", team_options)
    selected_team = teams_df.loc[teams_df["team_name"] == selected_label].iloc[0]
    team_id = selected_team["team_id"]

    data_path = config.get_data_path()
    sessions_df = practice_history.load_sessions_for_team(data_path, team_id)

    if sessions_df is None or sessions_df.empty:
        st.info("No sessions saved for this team.")
        st.stop()

    # Sort newest first if possible
    if "session_date" in sessions_df.columns:
        try:
            sessions_df["_sort_date"] = pd.to_datetime(sessions_df["session_date"])
            sessions_df = sessions_df.sort_values("_sort_date", ascending=False)
        except Exception:
            pass

    danger_ack = st.checkbox(
        "I understand that deleting sessions here is permanent and cannot be undone.",
        value=False,
    )

    st.markdown("#### Sessions")
    for _, row in sessions_df.iterrows():
        session_id = str(row.get("session_id", ""))
        col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
        with col1:
            st.write(row.get("session_date", ""))
        with col2:
            title = row.get("session_name") or row.get("session_title") or "Untitled session"
            st.write(title)
            st.caption(f"Session ID: {session_id}")
        with col3:
            dur = row.get("total_time", row.get("duration_minutes", 0))
            players = row.get("num_players", "")
            st.write(f"{int(dur) if pd.notna(dur) else 0} min | {players} players")
        with col4:
            if danger_ack and st.button("Delete", key=f"delete_{session_id}"):
                success = practice_history.delete_session_for_team(data_path, team_id, session_id)
                if success:
                    st.success(f"Deleted session {session_id}.")
                    st.experimental_rerun()
                else:
                    st.warning("Session not found or already deleted.")

    st.markdown("---")
    col_backup, col_delete_all = st.columns([1, 1])
    with col_backup:
        st.download_button(
            "Download sessions CSV",
            data=sessions_df.to_csv(index=False),
            file_name=f"sessions_{team_id}.csv",
            mime="text/csv",
        )
    with col_delete_all:
        if danger_ack and st.button("Delete ALL sessions for this team", type="secondary"):
            deleted_any = False
            for sid in sessions_df["session_id"].astype(str).tolist():
                if practice_history.delete_session_for_team(data_path, team_id, sid):
                    deleted_any = True
            if deleted_any:
                st.success("All sessions deleted.")
                st.experimental_rerun()
            else:
                st.info("No sessions were deleted.")

with st.expander("Templates (coming soon)"):
    st.text("Here you will be able to list and delete test templates.")

with st.expander("Drills (coming soon)"):
    st.text("Here you will be able to list and delete test drills.")
