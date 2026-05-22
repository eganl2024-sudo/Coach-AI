"""Team Hub - Deep dive into team profiles and context"""
import streamlit as st
import pandas as pd
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import config
import data_loader
import practice_history
import session_state
import session_state as ui_session
import ui_components
import schedule
import team_profile
import experience_level  # Day 7: Progressive disclosure
import pandas as pd
from auth import require_auth


CHECKLIST_LINK_CSS = """
<style>
.checklist-link {
    display: inline-block;
    padding: 6px 10px;
    border-radius: 6px;
    border: 1px solid #e5e7eb;
    background: #f9fafb;
    color: #111827;
    text-decoration: none;
    font-size: 13px;
}
.checklist-link:hover { background: #eef2ff; }
</style>
"""

CHECKLIST_SCROLL_JS = """
<script>
document.addEventListener('DOMContentLoaded', () => {
  const OFFSET = window.innerHeight * 0.3;  // scroll target ~30% down
  document.querySelectorAll('a.checklist-link').forEach(link => {
    link.addEventListener('click', (e) => {
      const targetId = link.getAttribute('href').replace('#','');
      const target = document.getElementById(targetId);
      if (!target) { return; }
      e.preventDefault();
      const rect = target.getBoundingClientRect();
      const scrollTop = window.pageYOffset + rect.top - OFFSET;
      window.scrollTo({ top: scrollTop, behavior: 'smooth' });
      setTimeout(() => {
        const focusable = Array.from(document.querySelectorAll('input, textarea, select'))
          .find(el => el.getBoundingClientRect().top > rect.top - 5);
        if (focusable) {
          focusable.focus({ preventScroll: true });
        }
      }, 400);
    });
  });
});
</script>
"""


def _persist_teams(df):
    data_path = st.session_state.get('data_path')
    if not data_path:
        return
    team_file = Path(data_path) / 'team_profiles.csv'
    df.to_csv(team_file, index=False)
    st.session_state.teams_df = df


def _explode(cell):
    return [item.strip() for item in str(cell).split("|") if item.strip()]

def _get_next_match_from_schedule(upcoming_df: pd.DataFrame | None):
    import pandas as pd
    if upcoming_df is None or upcoming_df.empty:
        return None
    df = upcoming_df.copy()
    if "event_date" not in df.columns:
        return None
    df["event_date"] = pd.to_datetime(df["event_date"]).dt.normalize()
    today = pd.Timestamp(datetime.today().date())
    df = df[df["event_date"] >= today]
    if df.empty:
        return None
    if "event_type" in df.columns:
        mask_game = df["event_type"].astype(str).str.lower().str.contains("game|match", na=False)
        games_df = df[mask_game]
        if not games_df.empty:
            df = games_df
    if "start_time" in df.columns:
        df["start_time"] = df["start_time"].astype(str)
        df = df.sort_values(["event_date", "start_time"])
    else:
        df = df.sort_values(["event_date"])
    return df.iloc[0]


# ============================================================================
# MATCH SNAPSHOT HELPER FUNCTIONS
# ============================================================================
def safe_text(value) -> str:
    """Convert value to safe display text, handling None/empty/whitespace."""
    if value is None:
        return "—"
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned if cleaned else "—"
    return str(value).strip() if str(value).strip() else "—"


def format_focus_tags(tags, max_show=3) -> str:
    """
    Format focus tags/list for display. Handles list or pipe-separated string.
    Shows up to max_show tags, then "+N more" if additional.
    """
    if not tags:
        return "—"
    
    # Convert to list if pipe-separated string
    if isinstance(tags, str):
        tag_list = [t.strip() for t in tags.split("|") if t.strip()]
    else:
        tag_list = tags if isinstance(tags, list) else []
    
    if not tag_list:
        return "—"
    
    tag_list = list(dict.fromkeys(tag_list))  # Remove duplicates, preserve order
    
    if len(tag_list) <= max_show:
        return ", ".join(tag_list)
    else:
        shown = ", ".join(tag_list[:max_show])
        remaining = len(tag_list) - max_show
        return f"{shown}, +{remaining} more"


def derive_play_style(play_style, custom_play_style) -> str:
    """Derive play style display: show custom if selected, otherwise show value."""
    if play_style == "Custom":
        return safe_text(custom_play_style)
    return safe_text(play_style)


def derive_objective(objective, custom_objective) -> str:
    """Derive season objective display: show custom if selected, otherwise show value."""
    if objective == "Custom":
        return safe_text(custom_objective)
    return safe_text(objective)


# ============================================================================
# PRACTICE CARD HELPER FUNCTIONS
# ============================================================================
def safe_str(value) -> str:
    """
    Convert any value to a safe string for HTML rendering.
    Handles None, NaN, floats, and all other types gracefully.
    
    Args:
        value: Any value (string, float, None, NaN, etc.)
    
    Returns:
        Safe string representation, empty string for None/NaN
    """
    import math
    
    if value is None:
        return ""
    try:
        if isinstance(value, float) and math.isnan(value):
            return ""
    except Exception:
        pass
    return str(value).strip()


def _get_stable_event_key(row) -> str:
    """Generate stable, unique key for an event based on event_id or (date + time + title)."""
    event_id = row.get("event_id")
    if event_id and str(event_id).strip():
        return str(event_id).strip()
    # Fallback: create hash from date + time + title for stability across reruns
    import hashlib
    date_str = str(row.get("event_date", "")).replace("-", "")
    time_str = str(row.get("start_time", "")).replace(":", "").replace(" ", "")
    title_str = str(row.get("event_type", "")).lower().replace(" ", "")
    combined = f"{date_str}_{time_str}_{title_str}"
    return hashlib.md5(combined.encode()).hexdigest()[:8]


def _find_saved_session_for_event(team_id: str, row, sessions_df: pd.DataFrame) -> Optional[dict]:
    """
    Search sessions_df for a saved practice session matching the event date/time.
    Returns the session row dict if found, None otherwise.
    """
    if sessions_df is None or sessions_df.empty:
        return None
    
    # Try to match by event date and approximate time
    try:
        event_date = pd.to_datetime(row.get("event_date"), errors="coerce")
        if pd.isna(event_date):
            return None
        
        # Normalize date
        event_date = event_date.normalize()
        
        # Look for sessions on the same date
        if "session_date" in sessions_df.columns:
            sessions_df_copy = sessions_df.copy()
            sessions_df_copy["session_date_norm"] = pd.to_datetime(
                sessions_df_copy["session_date"], errors="coerce"
            ).dt.normalize()
            matches = sessions_df_copy[sessions_df_copy["session_date_norm"] == event_date]
            
            if not matches.empty:
                # Return the first match (or best match if multiple exist)
                return matches.iloc[0].to_dict()
    except Exception:
        pass
    
    return None


def _render_week_view(upcoming_df: pd.DataFrame | None) -> None:
    import pandas as pd
    import datetime as dt

    has_schedule = True
    if upcoming_df is None or upcoming_df.empty or "event_date" not in upcoming_df.columns:
        has_schedule = False
        upcoming_df = pd.DataFrame(columns=["event_date", "start_time", "event_type", "opponent"])
    else:
        upcoming_df = upcoming_df.copy()
        upcoming_df["event_date"] = pd.to_datetime(upcoming_df["event_date"]).dt.date

        today_date = dt.date.today()
        upcoming_df = upcoming_df[upcoming_df["event_date"] >= today_date].copy()

        if upcoming_df.empty:
            has_schedule = False

    # Ensure session state keys exist
    if "current_week_start" not in st.session_state:
        today = dt.date.today()
        week_start = today - dt.timedelta(days=today.weekday())
        st.session_state["current_week_start"] = week_start
        st.session_state["week_offset"] = 0

    current_week_start = st.session_state.get("current_week_start", dt.date.today())
    week_offset = st.session_state.get("week_offset", 0)
    display_week_start = current_week_start + dt.timedelta(weeks=week_offset)
    display_week_end = display_week_start + dt.timedelta(days=6)

    # Navigation
    nav_cols = st.columns([1, 2, 1])
    with nav_cols[0]:
        if st.button("← Prev week", key="prev_week"):
            st.session_state["week_offset"] -= 1
            st.rerun()
    with nav_cols[1]:
        week_str = f"{display_week_start.strftime('%b %d')} – {display_week_end.strftime('%b %d, %Y')}"
        st.markdown(f"<div style='text-align:center; font-weight:600;'>{week_str}</div>", unsafe_allow_html=True)
    with nav_cols[2]:
        if st.button("Next week →", key="next_week"):
            st.session_state["week_offset"] += 1
            st.rerun()

    # Filter to current week
    if has_schedule:
        week_df = upcoming_df[
            (upcoming_df["event_date"] >= display_week_start) &
            (upcoming_df["event_date"] <= display_week_end)
        ].copy()
    else:
        week_df = pd.DataFrame()

    # Render 7-day strip
    day_cols = st.columns(7)
    for i, col_idx in enumerate(range(7)):
        day = display_week_start + dt.timedelta(days=col_idx)
        day_name = day.strftime("%a").upper()
        day_num = day.strftime("%d")
        is_today = day == dt.date.today()
        bg_color = "#e3f2fd" if is_today else "#f5f5f5"

        with day_cols[col_idx]:
            st.markdown(
                f"""
                <div style="
                    background-color:{bg_color};
                    border:{'2px solid #1976d2' if is_today else '1px solid #ddd'};
                    border-radius:6px;
                    padding:0.5rem;
                    text-align:center;
                    min-height:100px;
                ">
                    <div style="font-weight:700; font-size:0.75rem; color:#666;">{day_name}</div>
                    <div style="font-weight:700; font-size:1.25rem; color:#1a1a1a;">{day_num}</div>
                """,
                unsafe_allow_html=True,
            )

            if not week_df.empty:
                day_events = week_df[week_df["event_date"] == day]
                if not day_events.empty:
                    for _, evt in day_events.iterrows():
                        event_type = str(evt.get("event_type", "")).lower().strip()
                        opponent = str(evt.get("opponent", "") or "").strip()
                        start_time = str(evt.get("start_time", "") or "").strip()

                        if event_type in ("game", "match"):
                            icon = "⚽"
                        elif event_type in ("film", "review"):
                            icon = "🎬"
                        elif event_type in ("lift", "strength", "conditioning"):
                            icon = "💪"
                        elif event_type in ("recovery", "cool", "cooldown"):
                            icon = "❄️"
                        elif event_type in ("walkthrough", "talk"):
                            icon = "👥"
                        else:
                            icon = "🟢"

                        opp_label = opponent
                        if len(opp_label) > 18:
                            opp_label = opp_label[:15].rstrip() + "…"

                        parts = [icon]
                        if start_time:
                            parts.append(start_time)
                        if event_type:
                            parts.append(event_type)
                        if opp_label:
                            parts.append(f"vs {opp_label}")
                        label = " ".join(parts)
                        st.markdown(
                            f"<div style='font-size:0.75rem; margin-bottom:0.25rem; line-height:1.25;'>{label}</div>",
                            unsafe_allow_html=True,
                        )

            st.markdown("</div>", unsafe_allow_html=True)


def _session_to_html(session_dict: dict, team_name: str = "", opponent: str = "", location: str = "") -> str:
    """
    Convert a saved PracticeSession dict to a readable HTML document.
    Safe against None, NaN, floats, and missing fields.
    
    Args:
        session_dict: Dictionary from session_structure JSON or saved session
        team_name: Team name (optional override)
        opponent: Opponent/event info (optional)
        location: Location info (optional)
    
    Returns:
        Complete HTML document string
    """
    import html as html_module
    
    # Safe extraction helper
    def safe_get(obj, key, default=""):
        if isinstance(obj, dict):
            val = obj.get(key, default)
        else:
            val = getattr(obj, key, default)
        return val if val not in (None, "") else default
    
    # Extract key fields - use safe_str() before any operations
    session_date = safe_str(safe_get(session_dict, "session_date", ""))
    session_date_display = ""
    if session_date:
        try:
            dt_obj = pd.to_datetime(session_date)
            session_date_display = dt_obj.strftime("%A, %B %d, %Y")
        except Exception:
            session_date_display = session_date
    
    team_name_final = safe_str(team_name) or safe_str(safe_get(session_dict, "team_name", "Team")) or "Team"
    session_name = safe_str(safe_get(session_dict, "session_name", "")) or safe_str(safe_get(session_dict, "team_name", "")) or "Practice"
    duration = safe_str(safe_get(session_dict, "duration_minutes", 90))
    num_players = safe_str(safe_get(session_dict, "num_players", "")) or "—"
    
    opponent = safe_str(opponent) or "—"
    location = safe_str(location) or "—"
    
    # Session config
    config_data = safe_get(session_dict, "config", {})
    session_notes = safe_str(safe_get(config_data, "session_notes", ""))
    selected_categories = safe_get(config_data, "selected_categories", [])
    if isinstance(selected_categories, str):
        selected_categories = [c.strip() for c in selected_categories.split("|") if c.strip()]
    
    # Drills
    drills = safe_get(session_dict, "drills", [])
    
    # HTML template
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Practice Plan - {html_module.escape(team_name_final)}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
            color: #333;
            line-height: 1.6;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            font-size: 28px;
            margin-bottom: 10px;
            color: #1a1a1a;
        }}
        h2 {{
            font-size: 20px;
            margin-top: 30px;
            margin-bottom: 15px;
            border-bottom: 2px solid #007bff;
            padding-bottom: 8px;
            color: #0056b3;
        }}
        h3 {{
            font-size: 16px;
            margin-top: 20px;
            margin-bottom: 10px;
            color: #333;
        }}
        .header {{
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #e0e0e0;
        }}
        .header-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 15px;
        }}
        .header-item {{
            background: #f9f9f9;
            padding: 12px;
            border-radius: 4px;
        }}
        .header-item .label {{
            font-weight: 600;
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            margin-bottom: 4px;
        }}
        .header-item .value {{
            font-size: 14px;
            color: #1a1a1a;
        }}
        .summary {{
            background: #f0f8ff;
            padding: 15px;
            border-left: 4px solid #007bff;
            border-radius: 4px;
            margin-bottom: 20px;
        }}
        .summary-item {{
            display: inline-block;
            margin-right: 20px;
            margin-bottom: 8px;
        }}
        .summary-label {{
            font-weight: 600;
            color: #0056b3;
        }}
        .tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }}
        .tag {{
            display: inline-block;
            background: #e7f3ff;
            color: #0056b3;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }}
        .drill {{
            border: 1px solid #ddd;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 6px;
            background: #fafafa;
        }}
        .drill-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 10px;
        }}
        .drill-name {{
            font-weight: 600;
            font-size: 15px;
            color: #1a1a1a;
        }}
        .drill-meta {{
            display: flex;
            gap: 15px;
            font-size: 12px;
            color: #666;
            margin-bottom: 10px;
        }}
        .drill-meta-item {{
            display: flex;
            align-items: center;
        }}
        .drill-meta-label {{
            font-weight: 600;
            margin-right: 4px;
        }}
        .drill-section {{
            margin-top: 10px;
        }}
        .drill-section-label {{
            font-weight: 600;
            color: #0056b3;
            font-size: 12px;
            margin-bottom: 6px;
        }}
        .drill-section-content {{
            font-size: 13px;
            color: #333;
            line-height: 1.5;
        }}
        .notes {{
            background: #fff8f0;
            border-left: 4px solid #ff9800;
            padding: 12px;
            border-radius: 4px;
            margin-top: 20px;
        }}
        .notes-label {{
            font-weight: 600;
            color: #e65100;
            margin-bottom: 6px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            font-size: 11px;
            color: #999;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{html_module.escape(session_name)}</h1>
            
            <div class="header-row">
                <div class="header-item">
                    <div class="label">Team</div>
                    <div class="value">{html_module.escape(team_name_final)}</div>
                </div>
                <div class="header-item">
                    <div class="label">Date</div>
                    <div class="value">{html_module.escape(session_date_display) if session_date_display else "—"}</div>
                </div>
            </div>
            
            <div class="header-row">
                <div class="header-item">
                    <div class="label">Duration</div>
                    <div class="value">{html_module.escape(duration)} minutes</div>
                </div>
                <div class="header-item">
                    <div class="label">Players</div>
                    <div class="value">{html_module.escape(num_players)}</div>
                </div>
            </div>
"""
    
    if opponent and opponent != "—":
        html_content += f"""            <div class="header-row">
                <div class="header-item">
                    <div class="label">Opponent / Event</div>
                    <div class="value">{html_module.escape(opponent)}</div>
                </div>
                <div class="header-item">
                    <div class="label">Location</div>
                    <div class="value">{html_module.escape(location)}</div>
                </div>
            </div>
"""
    
    if selected_categories:
        html_content += f"""            <div class="summary">
                <div class="summary-item">
                    <span class="summary-label">Focus Areas:</span>
                </div>
                <div class="tags">
"""
        for cat in selected_categories:
            safe_cat = html_module.escape(safe_str(cat))
            html_content += f'                    <span class="tag">{safe_cat}</span>\n'
        html_content += """                </div>
            </div>
"""
    
    html_content += "        </div>\n"  # Close header
    
    # Session notes
    if session_notes:
        safe_notes = html_module.escape(session_notes)
        html_content += f"""        <div class="notes">
            <div class="notes-label">Session Notes</div>
            <div>{safe_notes}</div>
        </div>
"""
    
    # Drills section
    if drills:
        html_content += "        <h2>Drills & Activities</h2>\n"
        for i, drill in enumerate(drills, 1):
            drill_name = safe_str(safe_get(drill, "drill_name", f"Drill {i}"))
            drill_time = safe_str(safe_get(drill, "allocated_time", ""))
            drill_intensity = safe_str(safe_get(drill, "intensity", ""))
            drill_category = safe_str(safe_get(drill, "category", ""))
            drill_description = safe_str(safe_get(drill, "description", ""))
            coaching_points = safe_str(safe_get(drill, "coaching_points", ""))
            
            html_content += f"""        <div class="drill">
            <div class="drill-header">
                <div class="drill-name">{html_module.escape(drill_name)}</div>
            </div>
            <div class="drill-meta">
"""
            if drill_time:
                safe_time = html_module.escape(drill_time)
                html_content += f'                <div class="drill-meta-item"><span class="drill-meta-label">Time:</span> {safe_time} min</div>\n'
            if drill_intensity:
                safe_intensity = html_module.escape(drill_intensity)
                html_content += f'                <div class="drill-meta-item"><span class="drill-meta-label">Intensity:</span> {safe_intensity}</div>\n'
            if drill_category:
                safe_category = html_module.escape(drill_category)
                html_content += f'                <div class="drill-meta-item"><span class="drill-meta-label">Category:</span> {safe_category}</div>\n'
            
            html_content += "            </div>\n"
            
            if drill_description:
                safe_description = html_module.escape(drill_description)
                html_content += f"""            <div class="drill-section">
                <div class="drill-section-label">Description</div>
                <div class="drill-section-content">{safe_description}</div>
            </div>
"""
            
            if coaching_points:
                safe_coaching = html_module.escape(coaching_points)
                html_content += f"""            <div class="drill-section">
                <div class="drill-section-label">Coaching Points</div>
                <div class="drill-section-content">{safe_coaching}</div>
            </div>
"""
            
            html_content += "        </div>\n"
    
    html_content += """        <div class="footer">
            <p>Generated by Coach AI Practice Planner</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html_content


    has_schedule = True
    if upcoming_df is None or upcoming_df.empty or "event_date" not in upcoming_df.columns:
        has_schedule = False
        upcoming_df = pd.DataFrame(columns=["event_date", "start_time", "event_type", "opponent"])
    else:
        upcoming_df = upcoming_df.copy()
        upcoming_df["event_date"] = pd.to_datetime(upcoming_df["event_date"]).dt.date

        today_date = dt.date.today()
        upcoming_df = upcoming_df[upcoming_df["event_date"] >= today_date].copy()

        if upcoming_df.empty:
            has_schedule = False

    # Ensure session state keys exist
    if "current_week_start" not in st.session_state:
        today = dt.date.today()
        st.session_state.current_week_start = today - dt.timedelta(days=today.weekday())

    if not isinstance(st.session_state.current_week_start, dt.date):
        st.session_state.current_week_start = dt.date.today()

    def shift_week(days):
        st.session_state.current_week_start += dt.timedelta(days=days)

    # Always draw both buttons, never conditional
    nav_prev, nav_next = st.columns([1, 1])

    with nav_prev:
        if st.button("← Previous week", key="nav_prev_week"):
            shift_week(-7)

    with nav_next:
        if st.button("Next week →", key="nav_next_week"):
            shift_week(+7)

    # Compute the visible week range safely
    week_start = st.session_state.current_week_start
    week_end = week_start + dt.timedelta(days=6)

    st.write("")  # spacing
    st.divider()

    st.markdown(
        f"### Week of {week_start.strftime('%b %d')} – {week_end.strftime('%b %d')}"
    )

    week_days = [week_start + dt.timedelta(days=i) for i in range(7)]

    if not has_schedule:
        st.info("No upcoming schedule found for this team. Upload and save a PDF schedule above to get started.")


    if "start_time" in upcoming_df.columns:
        upcoming_df["start_time"] = upcoming_df["start_time"].astype(str).fillna("")
    else:
        upcoming_df["start_time"] = ""

    week_df = upcoming_df[
        (upcoming_df["event_date"] >= week_start) & (upcoming_df["event_date"] <= week_end)
    ].copy()

    events_by_day = {
        day: week_df[week_df["event_date"] == day].sort_values(["event_date", "start_time"])
        for day in week_days
    }

    day_cols = st.columns(7)
    day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    today = dt.date.today()

    for idx, day in enumerate(week_days):
        day_events = events_by_day[day]
        with day_cols[idx]:
            st.markdown(
                f"<div style='text-align:center; font-size:0.75rem; color:#888;'>{day_names[idx]}</div>",
                unsafe_allow_html=True,
            )
            is_today = day == today
            border_color = "#4F8BF9" if is_today else "#e0e0e0"
            font_weight = "600" if is_today else "400"
            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    margin-top:0.25rem;
                    padding:0.15rem 0.4rem;
                    border-radius:999px;
                    border:1px solid {border_color};
                    font-size:0.85rem;
                    font-weight:{font_weight};
                ">{day.strftime('%d')}</div>
                """,
                unsafe_allow_html=True,
            )

            if day_events.empty:
                st.markdown(
                    "<div style='height:2.5rem; text-align:center; font-size:0.75rem; color:#bbb; margin-top:0.25rem;'>—</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown("<div style='height:0.25rem;'></div>", unsafe_allow_html=True)
                for _, row in day_events.iterrows():
                    event_type = str(row.get("event_type", "") or "").strip()
                    start_time = str(row.get("start_time", "") or "").strip()
                    opponent = str(row.get("opponent", "") or "").strip()
                    lower_type = event_type.lower()
                    if "game" in lower_type or "match" in lower_type:
                        icon = "⚽"
                    elif "lift" in lower_type or "strength" in lower_type:
                        icon = "💪"
                    elif "film" in lower_type or "video" in lower_type:
                        icon = "🎥"
                    else:
                        icon = "🟢"

                    opp_label = opponent
                    if len(opp_label) > 18:
                        opp_label = opp_label[:15].rstrip() + "…"

                    parts = [icon]
                    if start_time:
                        parts.append(start_time)
                    if event_type:
                        parts.append(event_type)
                    if opp_label:
                        parts.append(f"vs {opp_label}")
                    label = " ".join(parts)
                    st.markdown(
                        f"<div style='font-size:0.75rem; margin-bottom:0.25rem; line-height:1.25;'>{label}</div>",
                        unsafe_allow_html=True,
                    )


st.set_page_config(page_title="Team Hub", page_icon="👥", layout="wide")

require_auth()
ui_components.require_page_access("pages/5_Team_Hub.py")

ui_components.render_nav(active_label="👥 My Team")
st.divider()

st.title("👥 Team Hub")
st.caption("Capture formation, match notes, focus areas, and practice context for every squad.")
st.markdown(CHECKLIST_LINK_CSS + CHECKLIST_SCROLL_JS, unsafe_allow_html=True)

session_state.init_session_state()
is_coach = ui_session.is_coach_mode()
is_dev = ui_session.is_developer_mode()

if 'data_path' not in st.session_state:
    st.session_state.data_path = config.get_data_path()

if st.session_state.teams_df is None:
    st.session_state.teams_df = data_loader.load_teams(st.session_state.data_path)

if st.session_state.teams_df.attrs.get('load_error'):
    st.error(st.session_state.teams_df.attrs['load_error'])

session_state.render_team_selector(
    label="Active team",
    widget_key="team_selector_hub",
    help_text="Switch teams to edit a different profile."
)

teams_df = st.session_state.teams_df
team_repair = teams_df.attrs.get('repair_info')
if team_repair and team_repair.get("was_repaired"):
    added = ", ".join(team_repair.get("added_columns", [])) or "columns"
    added = ", ".join(team_repair.get("added_columns", [])) or "columns"
    # Suppress default repair warning to reduce clutter
    # st.warning(f"Team profiles CSV was missing {added}; defaults were applied.")

if st.session_state.selected_team is None or teams_df is None or len(teams_df) == 0:
    st.warning("Add a team to start using the Team Hub.")
    st.stop()

team = st.session_state.selected_team
team_id = team['team_id']
team_row = teams_df[teams_df['team_id'] == team_id].iloc[0]
profile_status = session_state.get_team_profile_status(team_id)
completion_percent, missing_fields = session_state.get_team_profile_completeness(team_row)
profile_data_path = Path(st.session_state.data_path)
stored_profile = team_profile.load_team_profile(profile_data_path, team_id)
next_match_row = _get_next_match_from_schedule(schedule.load_team_schedule(team_id, st.session_state.data_path))

profile_col, meta_col = st.columns([2, 1])
with profile_col:
    st.subheader(team['team_name'])
    st.markdown(f"**Age Group:** {team.get('age_group', '—')}")
    st.markdown(f"**Skill Level:** {team.get('skill_level', '—').title() if team.get('skill_level') else '—'}")
    st.markdown(f"**Formation:** {ui_components.clean_text(team_row.get('formation', ''), 'Set in profile below')}")
    st.markdown(f"**Play Style:** {ui_components.clean_text(team_row.get('play_style', ''), 'Set in profile below')}")
    
    notes_val = ui_components.clean_text(team_row.get('notes', ''), '—')
    if notes_val != '—':
        st.markdown(f"**Notes:** {notes_val}")
    if team_row.get('upcoming_match_date') or team_row.get('upcoming_match_opponent'):
        match_bits = []
        if team_row.get('upcoming_match_opponent'):
            match_bits.append(str(team_row['upcoming_match_opponent']))
        if team_row.get('upcoming_match_date'):
            match_bits.append(str(team_row['upcoming_match_date']))
        if team_row.get('upcoming_match_time'):
            match_bits.append(str(team_row['upcoming_match_time']))
        if match_bits:
            st.markdown(f"**Upcoming Match:** {' | '.join(filter(None, match_bits))}")
    if team_row.get('season_objectives'):
        st.markdown(f"**Season Objective:** {team_row.get('season_objectives')}")

with meta_col:
    st.metric("Roster Size", team.get('typical_roster_size', 0))
    st.metric("Focus Areas", len(_explode(team_row.get('focus_areas', ''))))
    st.metric("Key Players Logged", len(_explode(team_row.get('key_players', ''))))


st.subheader("Quick Edit")
edit_sections = st.columns(3)
if edit_sections[0].button("Update team basics"):
    st.session_state["quick_setup_mode"] = "edit_defaults"
    st.session_state["quick_setup_team_id"] = team_id
    st.switch_page("pages/0_Coach_Onboarding.py")
if edit_sections[1].button("Update practice schedule"):
    st.session_state["quick_setup_mode"] = "edit_defaults"
    st.session_state["quick_setup_team_id"] = team_id
    st.switch_page("pages/0_Coach_Onboarding.py")
if edit_sections[2].button("Edit focus/style"):
    st.session_state["quick_setup_mode"] = "edit_defaults"
    st.session_state["quick_setup_team_id"] = team_id
    st.switch_page("pages/0_Coach_Onboarding.py")


st.subheader("Profile Details")

with st.expander("Setup Checklist", expanded=completion_percent < 80):
    st.markdown(f"Completion: **{completion_percent}%**")
    checklist_items = [
        ("age_group", "Select age group", "anchor_age_group"),
        ("formation", "Select formation", "anchor_formation"),
        ("play_style", "Select play style", "anchor_play_style"),
        ("focus_tags", "Add focus tags", "anchor_focus_tags"),
        ("key_players", "Add key players", "anchor_key_players"),
        ("injuries", "Add injuries or availability notes", "anchor_injuries"),
        ("practice_schedule", "Add practice schedule", "anchor_practice_schedule"),
    ]
    for key, label, link in checklist_items:
        status_icon = "✅" if key not in missing_fields else "⬜"
        cols = st.columns([3, 1])
        cols[0].markdown(f"{status_icon} {label}")
        cols[1].markdown(
            f"<a class='checklist-link' href='#{link}'>Go there</a>",
            unsafe_allow_html=True,
        )
    if completion_percent >= 80:
        st.success("Team profile complete — ready for multi-week cycle generation.")
    else:
        st.info("Fill the unchecked items above to unlock better recommendations.")

existing_focus_tags = _explode(team_row.get('focus_areas', ''))
key_players_default = "\n".join(_explode(team_row.get('key_players', '')))
injuries_default = "\n".join(_explode(team_row.get('injuries', '')))

if not profile_status["is_complete"]:
    missing = ", ".join(profile_status["missing_fields"])
    st.warning(
        f"Team profile is missing {missing}. Fill these in so the Practice Generator "
        "can tailor drill suggestions."
    )

st.markdown("---")
st.markdown("<a name='schedule-section'></a>", unsafe_allow_html=True)
st.header("Schedule (Upload & Calendar)")
st.caption("Upload a game/practice PDF, review parsed events, then save & view on the calendar.")


st.subheader("Upload Schedule (PDF)")
uploaded_schedule = st.file_uploader(
    "Upload a game or practice schedule (PDF)",
    type=["pdf"],
    key="schedule_pdf",
)

if st.button("Parse PDF schedule"):
    if uploaded_schedule is None:
        st.warning("Please upload a PDF schedule first.")
    else:
        try:
            parsed_df = schedule.parse_pdf_schedule(uploaded_schedule.getvalue())
            st.session_state["draft_schedule_df"] = parsed_df
            st.success("Schedule parsed. Review and edit below before saving.")
        except Exception as exc:
            print("Error parsing PDF schedule:", exc)
            st.error(
                "We couldn't read this PDF. "
                f"Details: {exc}"
            )

# Editable draft table
if "draft_schedule_df" in st.session_state:
    st.subheader("Review & Edit Schedule")
    draft_df = st.session_state["draft_schedule_df"]
    edited_df = st.data_editor(
        draft_df,
        num_rows="dynamic",
        hide_index=True,
        use_container_width=True,
        key="schedule_editor",
    )
    st.session_state["draft_schedule_df"] = edited_df

    if st.button("Save schedule to team"):
        df_to_save = st.session_state.get("draft_schedule_df")
        if df_to_save is None:
            st.warning("Nothing to save yet. Parse a PDF schedule first.")
        else:
            try:
                schedule.save_team_schedule(st.session_state.data_path, team_id, df_to_save)
                st.success("Schedule saved for this team.")
            except Exception as e:
                print("Error saving team schedule:", e)
                st.error(f"We couldn't save this schedule. {e}")

st.markdown("---")
st.markdown("## Upcoming Schedule")
st.caption("Week-by-week view of games, training, and events for this team.")
upcoming_df = schedule.load_team_schedule(team_id, st.session_state.data_path)
_render_week_view(upcoming_df)

st.markdown("## This Week's Practices")
practice_types = {"practice", "film", "lift", "recovery", "walkthrough"}
today_norm = pd.Timestamp.today().normalize()
week_cutoff = today_norm + pd.Timedelta(days=7)
pr_df = None
if upcoming_df is not None and not upcoming_df.empty and "event_date" in upcoming_df.columns:
    pr_df = upcoming_df.copy()
    pr_df["event_date"] = pd.to_datetime(pr_df["event_date"], errors="coerce").dt.normalize()
    pr_df = pr_df[(pr_df["event_date"] >= today_norm) & (pr_df["event_date"] <= week_cutoff)]
    if "event_type" in pr_df.columns:
        pr_df = pr_df[pr_df["event_type"].astype(str).str.lower().isin(practice_types)]
    pr_df = pr_df.dropna(subset=["event_date"])
    pr_df = pr_df.sort_values(["event_date", "start_time"]) if not pr_df.empty else pr_df

# Load saved sessions for this team to check which events have plans
try:
    sessions_df = practice_history.load_sessions_for_team(st.session_state.data_path, team_id)
except Exception:
    sessions_df = None

if pr_df is None or pr_df.empty:
    st.info("No practices scheduled for the next 7 days.")
else:
    for _, row in pr_df.iterrows():
        date_val = row.get("event_date")
        date_disp = ""
        if pd.notna(date_val):
            try:
                date_disp = pd.to_datetime(date_val).strftime("%a %b %d")
            except Exception:
                date_disp = str(date_val)
        time_raw = str(row.get("start_time", "") or "").strip()
        time_disp = time_raw
        if time_raw:
            try:
                parsed_time = pd.to_datetime(time_raw).time()
                time_disp = parsed_time.strftime("%I:%M %p").lstrip("0")
            except Exception:
                time_disp = time_raw
        type_disp = str(row.get("event_type", "") or "Practice").strip()
        loc_disp = str(row.get("location", "") or "").strip()
        notes_disp = str(row.get("notes", "") or "").strip()
        meta_parts = [p for p in [loc_disp, notes_disp] if p]
        meta_line = " | ".join(meta_parts)
        st.markdown(
            f"""
            <div style="border:1px solid #e5e5e5; border-radius:8px; padding:0.6rem 0.75rem; margin-bottom:0.5rem;">
                <div style="font-weight:700;">{date_disp} {time_disp}</div>
                <div style="font-size:0.9rem; margin-top:0.15rem;">{type_disp}</div>
                <div style="font-size:0.85rem; color:#666; margin-top:0.15rem;">{meta_line}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        # ACTION BUTTONS ROW
        event_key = _get_stable_event_key(row)
        saved_session = _find_saved_session_for_event(team_id, row, sessions_df)
        
        btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
        
        with btn_col1:
            if saved_session:
                # If session exists, show "Edit" button as primary
                if st.button(
                    "✏️ Edit",
                    key=f"edit_{event_key}",
                    use_container_width=True,
                    type="primary"
                ):
                    session_id = saved_session.get("session_id")
                    if session_id:
                        st.session_state.current_team_id = team_id
                        st.session_state.current_event_id = row.get("event_id", "")
                        st.session_state.edit_session_id = session_id
                    st.switch_page("pages/2_Practice_Generator.py")
            else:
                # If no session, show "Plan Practice" as primary
                if st.button(
                    "📝 Plan Practice",
                    key=f"plan_{event_key}",
                    use_container_width=True,
                    type="primary"
                ):
                    # Set context for Practice Generator
                    st.session_state.current_team_id = team_id
                    st.session_state.current_event_id = row.get("event_id", "")
                    st.session_state.current_practice_date = pd.to_datetime(row.get("event_date")).date()
                    if time_raw:
                        st.session_state.practice_start_time = time_raw
                    if type_disp:
                        st.session_state.practice_title = type_disp
                    st.switch_page("pages/2_Practice_Generator.py")
        
        with btn_col2:
            if saved_session:
                # Show "View Details" button for read-only viewer
                if st.button(
                    "📄 View Details",
                    key=f"view_{event_key}",
                    use_container_width=True
                ):
                    # Set state for Practice Details page
                    st.session_state.current_team_id = team_id
                    st.session_state.current_event_id = row.get("event_id", "")
                    st.session_state.view_session_id = saved_session.get("session_id", "")
                    st.session_state.view_mode = "read_only"
                    st.switch_page("pages/Practice_Details.py")
            else:
                # Show disabled View Details button if no session
                st.button(
                    "📄 View Details",
                    key=f"view_disabled_{event_key}",
                    use_container_width=True,
                    disabled=True,
                    help="Create a plan first to view details"
                )
        
        with btn_col3:
            # Spacer column
            st.caption("")


formation_options = ["4-3-3", "4-4-2", "3-5-2", "4-2-3-1", "4-1-4-1", "Custom"]
raw_formation = team_row.get('formation', '')
current_formation = str(raw_formation) if raw_formation is not None else ''
current_formation = current_formation.strip()
if current_formation and current_formation not in formation_options:
    formation_options.append(current_formation)
formation_index = formation_options.index(current_formation) if current_formation in formation_options else 0

st.divider()
st.markdown("## Match Plan & Coach Notes")
st.caption("Capture how you want this team to set up for the next match.")

# ============================================================================
# CALCULATE MATCH DATA FOR BANNER AND FORM
# ============================================================================
current_match_date = team_row.get('upcoming_match_date')
upcoming_match_date_default = stored_profile.get("upcoming_match_date") or current_match_date
kickoff_time_default = stored_profile.get("kickoff_time") or team_row.get('upcoming_match_time')
upcoming_opponent_default = stored_profile.get("upcoming_opponent") or team_row.get('upcoming_match_opponent', '')

kickoff_time_readonly = ""
upcoming_opponent_readonly = ""
location_readonly = ""
upcoming_match_date_display = ""

if next_match_row is not None:
    upcoming_match_date_default = next_match_row.get("event_date", upcoming_match_date_default)
    upcoming_opponent_readonly = str(next_match_row.get("opponent", "") or "").strip()
    location_readonly = str(next_match_row.get("location", "") or "").strip()
    raw_time = next_match_row.get("start_time", "")
    if pd.notna(raw_time) and str(raw_time).strip():
        try:
            if isinstance(raw_time, str):
                parsed = pd.to_datetime(raw_time).time()
            else:
                parsed = getattr(raw_time, "time", lambda: raw_time)()
            kickoff_time_readonly = parsed.strftime("%I:%M %p").lstrip("0")
        except Exception:
            kickoff_time_readonly = str(raw_time)

# Parse upcoming_match_date for banner display
match_date_value = None
if upcoming_match_date_default is not None and upcoming_match_date_default != "":
    try:
        parsed_date = pd.to_datetime(upcoming_match_date_default, errors='coerce')
        if pd.notna(parsed_date):
            match_date_value = parsed_date.date()
            upcoming_match_date_display = parsed_date.strftime("%a, %b %d")
    except Exception:
        match_date_value = None

# ============================================================================
# MATCH BANNER: OPPONENT | DATE | TIME | LOCATION
# ============================================================================
if upcoming_opponent_readonly or kickoff_time_readonly or location_readonly:
    opp_text = upcoming_opponent_readonly or "TBD"
    date_text = upcoming_match_date_display or "TBD"
    time_text = kickoff_time_readonly or "TBD"
    loc_text = location_readonly or "TBD"

    st.markdown(
        f"""
        <div style="
            background-color:#f7f7f9;
            padding:0.75rem 1rem;
            border-radius:8px;
            display:flex;
            justify-content:space-between;
            align-items:center;
            font-weight:600;
            font-size:15px;
            margin-bottom:1.5rem;
            gap:1rem;
        ">
            <div style="flex:1.2;">{opp_text}</div>
            <div style="flex:1;">{date_text}</div>
            <div style="flex:0.9;">{time_text}</div>
            <div style="flex:1.2;">{loc_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================================
# MAIN FORM CONTAINER
# ============================================================================
st.markdown("<a id='anchor_formation'></a>", unsafe_allow_html=True)
st.markdown("<a id='anchor_play_style'></a>", unsafe_allow_html=True)

# Row 1: Preferred formation & Play style / identity
col_form, col_style = st.columns(2)

with col_form:
    preferred_formation_value = st.selectbox(
        "Preferred formation",
        options=formation_options,
        index=formation_index,
        key="preferred_formation",
        help="Default shape for this team's next match.",
    )

with col_style:
    play_style_options = config.TEAM_PLAY_STYLES + ["Custom"]
    raw_play_style = team_row.get('play_style', '')
    current_play_style = str(raw_play_style) if raw_play_style is not None else ''
    current_play_style = current_play_style.strip()
    default_play_style = stored_profile.get("default_play_style", "Custom")
    match_play_style = stored_profile.get("play_style_identity", "") or current_play_style
    current_play_style_value = match_play_style or default_play_style
    if current_play_style_value in play_style_options:
        play_style_index = play_style_options.index(current_play_style_value)
        play_style_custom_value = ""
    elif current_play_style_value:
        play_style_index = len(play_style_options) - 1
        play_style_custom_value = current_play_style_value
    else:
        play_style_index = 0
        play_style_custom_value = ""

    def _on_play_style_change():
        value = st.session_state.get("play_style_identity")
        if value is not None:
            updated = stored_profile.copy()
            updated["play_style_identity"] = value
            team_profile.save_team_profile(profile_data_path, team_id, updated)

    play_style_choice = st.selectbox(
        "Play style / identity",
        options=play_style_options,
        index=play_style_index,
        key="play_style_identity",
        on_change=_on_play_style_change,
        help="How you want this team to behave with and without the ball.",
    )
    play_style_value = play_style_choice
    if play_style_choice == "Custom":
        play_style_custom_value = st.text_input(
            "Custom play style",
            value=play_style_custom_value,
            key="custom_play_style",
            placeholder="e.g. High press, possession-focused, counter-attacking",
        )
        play_style_value = play_style_custom_value.strip()

# Row 2: Season objective
st.markdown("<a id='anchor_season_objective'></a>", unsafe_allow_html=True)
season_objective_options = config.TEAM_SEASON_OBJECTIVES + ["Custom"]
raw_objective = team_row.get('season_objectives', '')
default_season_objective = stored_profile.get("default_season_objective", "Custom")
current_objective_val = stored_profile.get("season_objectives", "").strip() or str(raw_objective).strip() or default_season_objective
if current_objective_val in season_objective_options:
    season_index = season_objective_options.index(current_objective_val)
    season_custom_value = ""
elif current_objective_val:
    season_index = len(season_objective_options) - 1
    season_custom_value = current_objective_val
else:
    season_index = 0
    season_custom_value = ""

def _on_season_objective_change():
    value = st.session_state.get("season_objective")
    if value is not None:
        updated = stored_profile.copy()
        updated["season_objectives"] = value
        team_profile.save_team_profile(profile_data_path, team_id, updated)

season_choice = st.selectbox(
    "Season objective",
    options=season_objective_options,
    index=season_index,
    on_change=_on_season_objective_change,
    key="season_objective",
    help="Align everyone on the primary mission for this season.",
)
season_objectives_value = season_choice
if season_choice == "Custom":
    season_custom_value = st.text_area(
        "Custom objective",
        value=season_custom_value,
        key="custom_objective",
        placeholder="e.g. Develop young players, improve defensive shape, build possession habits",
        height=80,
    )
    season_objectives_value = season_custom_value.strip()

# Row 3: Practice schedule
st.markdown("<a id='anchor_practice_schedule'></a>", unsafe_allow_html=True)
practice_schedule = st.text_input(
    "Typical practice pattern (e.g., Mon/Wed 6–7:30p)",
    value=str(team_row.get('practice_schedule', '') or '').strip(),
    placeholder="Days and times",
    help="The regular weekly schedule pattern (separate from the calendar view above)."
)

# Row 4: Edit match details expander
with st.expander("Edit match details"):
    edit_col1, edit_col2 = st.columns(2)

    with edit_col1:
        opponent_edit = st.text_input(
            "Opponent",
            value=upcoming_opponent_readonly or upcoming_opponent_default,
            key="opponent_edit",
            placeholder="Team name",
        )
        match_date_edit = st.date_input(
            "Match date",
            value=match_date_value or pd.Timestamp.today().date(),
            key="match_date_edit",
        )

    with edit_col2:
        time_edit = st.text_input(
            "Kickoff time",
            value=kickoff_time_readonly or "",
            key="time_edit",
            placeholder="e.g., 7:00 PM",
        )
        location_edit = st.text_input(
            "Location",
            value=location_readonly or "",
            key="location_edit",
            placeholder="Stadium or field name",
        )

# Row 5: Focus areas
st.markdown("<a id='anchor_focus_tags'></a>", unsafe_allow_html=True)
focus_options = sorted(set(config.DRILL_TAGS).union(existing_focus_tags))
focus_selection = st.multiselect(
    "Focus areas (tagged)",
    options=focus_options,
    default=stored_profile.get("focus_tags", existing_focus_tags),
    help="These tags describe team priorities. Matching drill tags boosts recommendations."
)
extra_focus_input = st.text_input(
    "Additional focus tags (comma separated)",
    value=stored_profile.get("extra_focus_tags", ""),
    placeholder="Leadership, Mental Toughness, etc.",
    help="Add quick one-off tags separated by commas."
)

# Row 6: Expandable text areas for detailed notes
st.markdown("<a id='anchor_key_players'></a>", unsafe_allow_html=True)
with st.expander("Key players / notes"):
    key_players_input = st.text_area(
        "",
        value=stored_profile.get("key_players_notes", key_players_default),
        height=120,
        placeholder="One entry per line",
        key="key_players_area",
    )

st.markdown("<a id='anchor_injuries'></a>", unsafe_allow_html=True)
with st.expander("Injuries / availability"):
    injuries_input = st.text_area(
        "",
        value=stored_profile.get("injury_notes", injuries_default),
        height=120,
        placeholder="One entry per line",
        key="injuries_area",
    )

with st.expander("General notes"):
    notes_input = st.text_area(
        "",
        value=stored_profile.get("general_notes", team_row.get('notes', '')),
        height=120,
        placeholder="Scouting intel, training reminders, parent communication, etc.",
        key="general_notes_area",
    )

# ============================================================================
# MATCH SNAPSHOT - READ-ONLY COACH SUMMARY
# ============================================================================
st.markdown("### Match Snapshot")
with st.container(border=True):
    snapshot_col1, snapshot_col2, snapshot_col3 = st.columns(3)
    
    with snapshot_col1:
        st.caption("📋 Formation")
        # Read from the form widget key set earlier
        formation_display = safe_text(st.session_state.get("preferred_formation", current_formation))
        st.write(formation_display)
    
    with snapshot_col2:
        st.caption("🎯 Identity")
        current_play_style_val = st.session_state.get("play_style_identity", current_play_style_value)
        current_custom_play = st.session_state.get("custom_play_style", play_style_custom_value)
        identity_display = derive_play_style(current_play_style_val, current_custom_play)
        st.write(identity_display)
    
    with snapshot_col3:
        st.caption("🏆 Objective")
        current_objective_val = st.session_state.get("season_objective", current_objective_val)
        current_custom_obj = st.session_state.get("custom_objective", season_custom_value)
        objective_display = derive_objective(current_objective_val, current_custom_obj)
        st.write(objective_display)
    
    st.markdown("")  # Spacer
    
    # Second row: Focus areas and optional key note preview
    snapshot_col_focus, snapshot_col_notes = st.columns([2, 1])
    
    with snapshot_col_focus:
        st.caption("🎪 Focus Areas")
        current_focus_tags = st.session_state.get("focus_selection", stored_profile.get("focus_tags", existing_focus_tags))
        extra_focus_tags_str = st.session_state.get("extra_focus_tags", stored_profile.get("extra_focus_tags", ""))
        combined_tags = current_focus_tags if isinstance(current_focus_tags, list) else []
        if extra_focus_tags_str:
            extra_list = [t.strip() for t in str(extra_focus_tags_str).split(",") if t.strip()]
            combined_tags = list(dict.fromkeys([*combined_tags, *extra_list]))
        focus_display = format_focus_tags(combined_tags, max_show=3)
        st.write(focus_display)
    
    with snapshot_col_notes:
        st.caption("📝 Notes")
        key_notes = st.session_state.get("key_players_area", stored_profile.get("key_players_notes", key_players_default))
        if key_notes and str(key_notes).strip():
            preview = safe_text(str(key_notes)[:80])
            if len(str(key_notes)) > 80:
                preview += "…"
            st.write(preview)
        else:
            st.write("—")

st.divider()

# ============================================================================
# SAVE BUTTON AND HANDLER
# ============================================================================
submitted = st.button("Save team profile", type="primary")

if submitted:
    extra_focus = [item.strip() for item in extra_focus_input.split(",") if item.strip()]
    focus_value = "|".join(dict.fromkeys([*focus_selection, *extra_focus]))
    key_players_value = "|".join([item.strip() for item in key_players_input.splitlines() if item.strip()])
    injuries_value = "|".join([item.strip() for item in injuries_input.splitlines() if item.strip()])

    # Use edited values if available, otherwise use readonly/default values
    final_opponent = opponent_edit.strip() if opponent_edit.strip() else upcoming_opponent_readonly
    final_date = match_date_edit.isoformat() if match_date_edit else ""
    final_time = time_edit.strip() if time_edit.strip() else kickoff_time_readonly
    final_location = location_edit.strip() if location_edit.strip() else location_readonly

    profile_payload = {
        "preferred_formation": preferred_formation_value,
        "play_style_identity": play_style_value,
        "custom_play_style": play_style_custom_value,
        "season_objective": season_objectives_value,
        "custom_objective": season_custom_value,
        "practice_schedule": practice_schedule.strip(),
        "focus_tags": focus_selection,
        "extra_focus_tags": extra_focus_input.strip(),
        "key_players_notes": key_players_input,
        "injury_notes": injuries_input,
        "general_notes": notes_input.strip(),
        "upcoming_match_date": final_date,
        "kickoff_time": final_time,
        "upcoming_opponent": final_opponent,
        "location": final_location,
    }
    try:
        team_profile.save_team_profile(profile_data_path, team_id, profile_payload)
        st.success("Team profile saved.")
    except Exception as exc:
        st.error(f"Couldn't save team profile: {exc}")

st.divider()
st.subheader("Focus & Key Players")

focus_pills = _explode(teams_df.loc[teams_df['team_id'] == team_id, 'focus_areas'].iloc[0])
if focus_pills:
    st.markdown("**Focus Areas:** " + ", ".join(f"`{pill}`" for pill in focus_pills))
else:
    st.markdown("**Focus Areas:** Add focus areas above to drive planning suggestions.")

key_player_list = _explode(teams_df.loc[teams_df['team_id'] == team_id, 'key_players'].iloc[0])
injury_list = _explode(teams_df.loc[teams_df['team_id'] == team_id, 'injuries'].iloc[0])

cols_focus = st.columns(2)
with cols_focus[0]:
    st.markdown("**Key Players / Notes**")
    if key_player_list:
        for player in key_player_list:
            st.markdown(f"- {player}")
    else:
        st.caption("No key players logged yet.")

with cols_focus[1]:
    st.markdown("**Injuries / Availability**")
    if injury_list:
        for injury in injury_list:
            st.markdown(f"- {injury}")
    else:
        st.caption("Healthy squad! Keep it going.")

st.divider()
st.subheader("Recent Practice Snapshot")

history_mtime = practice_history.get_history_mtime(team_id, st.session_state.data_path)
history_df = practice_history.load_practice_history(team_id, st.session_state.data_path, history_mtime)
if len(history_df) == 0:
    st.info("No sessions saved yet for this team. Generate one from the Practice Generator.")
else:
    history_df['session_date'] = pd.to_datetime(history_df['session_date']).dt.date
    sessions_metric_col, total_time_col, last_session_col = st.columns(3)
    sessions_metric_col.metric("Sessions Logged", len(history_df))
    total_time_col.metric("Total Minutes", int(history_df['total_time'].sum()))
    last_session_col.metric("Last Session", str(history_df['session_date'].max()))

    all_categories = []
    for entry in history_df['categories'].fillna(""):
        all_categories.extend(_explode(entry))
    cat_series = pd.Series(all_categories)
    if not cat_series.empty:
        st.bar_chart(cat_series.value_counts(), use_container_width=True)

    st.markdown("**Last 5 Sessions**")
    st.dataframe(
        history_df[['session_date', 'session_name', 'num_players', 'total_time']].tail(5),
        hide_index=True,
        use_container_width=True
    )
