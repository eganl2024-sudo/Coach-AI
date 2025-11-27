import streamlit as st
from typing import Optional
import config
import session_state as ui_session


def _page_links():
    is_coach = ui_session.is_coach_mode()
    links = [
        ("pages/0_Coach_Home.py", "Home"),
        ("pages/2_Practice_Generator.py", "Generate Practice"),
        ("pages/6_Coach_Template_Designer.py", "Template Designer"),
        ("pages/5_Team_Hub.py", "My Team"),
        ("pages/3_Practice_History.py", "Past Sessions"),
        ("pages/10_Practice_Library.py", "Practice Library"),
    ]
    if config.is_dev() and not is_coach:
        links.append(("pages/11_Template_Studio.py", "Template Studio (Advanced)"))
        links.append(("pages/4_Add_Drills.py", "Add Drills"))
        links.append(("pages/1_Drill_Library.py", "Drill Library"))
        links.append(("pages/9_Schema_Migration.py", "Schema Migration"))
        links.append(("pages/13_Dev_Diagnostics.py", "Dev Diagnostics"))
    return links


def render_nav(active_label: Optional[str] = None, columns=None):
    """
    Render the application navigation links with consistent layout.

    Args:
        active_label: Optional label to emphasize the current page.
        columns: Optional list of column widths.
    """
    if columns is None:
        # Updated for 6 coach links: Home, Generator, Templates, Team, History, Library
        columns = [1.5, 2.0, 1.8, 1.5, 1.8, 2.0, 2.5, 1.7, 1.7]
    links = _page_links()
    # widen columns list if more links appear (dev mode)
    if len(columns) < len(links):
        columns = [2.0] * len(links)
    nav_cols = st.columns(columns[: len(links)])
    for col, (path, label) in zip(nav_cols, links):
        with col:
            st.page_link(path, label=label)
