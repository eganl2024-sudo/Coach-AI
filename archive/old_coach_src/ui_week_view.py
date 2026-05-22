"""Reusable weekly planner strip for schedule + practice linking."""
from __future__ import annotations

import datetime as dt
from typing import Callable, Dict, Optional

import pandas as pd
import streamlit as st


def _normalize_date(series, column_name: str):
    if series is None:
        return pd.Series(dtype="datetime64[ns]")
    try:
        return pd.to_datetime(series, errors="coerce").dt.date
    except Exception:
        st.debug(f"Could not parse dates for {column_name}") if hasattr(st, "debug") else None
        return pd.Series([None for _ in range(len(series))])


def render_week_planner(
    team_id: str,
    schedule_df: pd.DataFrame,
    sessions_df: pd.DataFrame,
    current_date: dt.date,
    on_plan_click: Optional[Callable[[dt.date, Dict | None], None]] = None,
    on_view_click: Optional[Callable[[str], None]] = None,
) -> None:
    """
    Render a horizontal week strip (Mon–Sun) for the given team.

    schedule_df: events with at least event_date/date, event_type, maybe time.
    sessions_df: saved practice sessions for this team with session_date and session_id.
    """
    if current_date is None:
        current_date = dt.date.today()

    # Normalize dates
    sched = schedule_df.copy() if schedule_df is not None else pd.DataFrame()
    sessions = sessions_df.copy() if sessions_df is not None else pd.DataFrame()
    if not sched.empty:
        date_col = "event_date" if "event_date" in sched.columns else "date"
        sched["_date"] = _normalize_date(sched[date_col], "event_date")
    else:
        sched["_date"] = []
    if not sessions.empty:
        sessions["_date"] = _normalize_date(sessions["session_date"], "session_date")
    else:
        sessions["_date"] = []

    start_of_week = current_date - dt.timedelta(days=current_date.weekday())  # Monday start
    week_days = [start_of_week + dt.timedelta(days=i) for i in range(7)]

    cols = st.columns(7)
    for col, day in zip(cols, week_days):
        with col:
            is_today = day == dt.date.today()
            header = day.strftime("%a\n%b %d")
            color = "#4F8BF9" if is_today else "#111827"
            st.markdown(
                f"<div style='font-weight:600;color:{color};text-align:center'>{header}</div>",
                unsafe_allow_html=True,
            )

            day_events = sched[sched["_date"] == day] if not sched.empty else pd.DataFrame()
            practice_events = pd.DataFrame()
            if not day_events.empty:
                type_col = "event_type" if "event_type" in day_events.columns else "type" if "type" in day_events.columns else None
                if type_col:
                    practice_events = day_events[
                        day_events[type_col].astype(str).str.lower() == "practice"
                    ]
            event_info = practice_events.iloc[0].to_dict() if not practice_events.empty else None

            day_session = None
            if not sessions.empty:
                match = sessions[sessions["_date"] == day]
                if not match.empty:
                    day_session = match.iloc[0].to_dict()

            if event_info is None and day_session is None:
                st.caption("No practice")
                continue

            status = "Not planned"
            if day_session is not None:
                status = str(day_session.get("status", "") or "Planned").title()
            st.caption(status)

            if event_info is not None and day_session is None and on_plan_click:
                if st.button("Plan practice", key=f"plan_{team_id}_{day.isoformat()}"):
                    on_plan_click(day, event_info)
            if day_session is not None and on_view_click:
                sess_id = str(day_session.get("session_id") or "")
                if sess_id and st.button("View session", key=f"view_{team_id}_{sess_id}"):
                    on_view_click(sess_id)
