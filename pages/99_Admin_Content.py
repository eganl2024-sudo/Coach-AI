import streamlit as st
import sys
import os
import datetime
import pandas as pd
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

st.set_page_config(
    page_title="Admin Content | Player AI",
    page_icon="🔐",
    layout="wide",
)

ADMIN_PASSWORD = os.environ.get(
    "PLAYER_AI_ADMIN_PASSWORD", "AdminPlayerAI2026"
)

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if not st.session_state.admin_authenticated:
    st.title("🔐 Admin Access")
    pwd = st.text_input("Admin password", type="password")
    if st.button("Login"):
        if pwd == ADMIN_PASSWORD:
            st.session_state.admin_authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()

# authenticated
st.title("🛡️ Admin Content Editor")
st.write("Manage drill library video links, schematic diagrams, beta status, and sync changes with GitHub.")

# Display persistent success message if it exists
if "admin_success_msg" in st.session_state:
    st.success(st.session_state.admin_success_msg)
    del st.session_state.admin_success_msg

# Load drill library CSV
CSV_PATH = Path("data/production/drill_library.csv")
df = pd.read_csv(CSV_PATH, dtype=str).fillna("")

# Metrics Dashboard
total = len(df)
filmed = len(df[df["video_status"].str.lower() == "filmed"])
published = len(df[df["video_status"].str.lower() == "published"])
not_filmed = total - filmed - published
beta_ready_count = len(df[df["beta_ready"].str.lower() == "true"])

# Display as 4 metric columns
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric("Total Drills", total)
with col_m2:
    st.metric("Filmed", filmed)
with col_m3:
    st.metric("Beta Ready", beta_ready_count)
with col_m4:
    st.metric("Not Filmed", not_filmed, delta=f"-{not_filmed} to go")

# Progress bar
if total > 0:
    pct = round((filmed + published) / total * 100)
else:
    pct = 0
st.progress(pct / 100, text=f"{pct}% of library has video")

st.divider()

# Filters
st.subheader("🔍 Filters")
filter_col1, filter_col2 = st.columns(2)

with filter_col1:
    presenter_options = ["All"] + sorted(
        df["presenter_id"].unique().tolist()
    )
    selected_presenter = st.selectbox(
        "Filter by presenter", presenter_options
    )

with filter_col2:
    status_options = ["All", "Not Filmed", "Filmed", "Published"]
    selected_status = st.selectbox(
        "Filter by video status", status_options
    )

# Apply filters
filtered_df = df.copy()
if selected_presenter != "All":
    filtered_df = filtered_df[
        filtered_df["presenter_id"] == selected_presenter
    ]
if selected_status != "All":
    filtered_df = filtered_df[
        filtered_df["video_status"].str.lower() ==
        selected_status.lower()
    ]

# Drill Editor Cards
st.subheader(f"📋 Drills ({len(filtered_df)})")

for _, row in filtered_df.iterrows():
    drill_id = row["drill_id"]
    is_filmed = row.get("video_status", "").lower() in ["filmed", "published"]
    label = (
        f"{'✅' if is_filmed else '📹'} "
        f"{drill_id} — {row['drill_name']} "
        f"[{row.get('video_status', 'Not Filmed')}]"
    )
    with st.expander(label, expanded=not is_filmed):
        with st.form(key=f"form_{drill_id}"):
            # Current video preview
            current_url = row.get("video_url", "").strip()
            if current_url:
                st.video(current_url)
            else:
                st.info("No video linked yet.")

            col1, col2 = st.columns(2)

            with col1:
                new_url = st.text_input(
                    "YouTube URL",
                    value=current_url,
                    key=f"url_{drill_id}"
                )
                
                # Make sure the current status is mapped to valid option index
                status_val = row.get("video_status", "not filmed").lower().strip()
                status_list = ["not filmed", "filmed", "published"]
                if status_val in status_list:
                    status_idx = status_list.index(status_val)
                else:
                    status_idx = 0
                    
                new_status = st.selectbox(
                    "Video status",
                    ["Not Filmed", "Filmed", "Published"],
                    index=status_idx,
                    key=f"status_{drill_id}"
                )
                new_beta = st.checkbox(
                    "Beta Ready",
                    value=row.get("beta_ready", "").lower() == "true",
                    key=f"beta_{drill_id}"
                )

            with col2:
                new_notes = st.text_area(
                    "Filming notes",
                    value=row.get("filming_notes", ""),
                    height=80,
                    key=f"notes_{drill_id}"
                )
                new_diagram = st.text_input(
                    "Schematic URL (diagram_url)",
                    value=row.get("diagram_url", ""),
                    key=f"diag_{drill_id}"
                )
                st.markdown(
                    "[🎨 Open Excalidraw →]"
                    "(https://excalidraw.com) "
                    "Draw schematic, export PNG, host on "
                    "Imgur or GitHub raw, paste URL above."
                )

            submitted = st.form_submit_button(
                "💾 Save Changes", type="primary",
                use_container_width=True
            )

            if submitted:
                # Update the main df in place
                idx = df.index[df["drill_id"] == drill_id][0]
                df.at[idx, "video_url"]     = new_url
                df.at[idx, "video_status"]  = new_status
                df.at[idx, "beta_ready"]    = str(new_beta)
                df.at[idx, "filming_notes"] = new_notes
                df.at[idx, "diagram_url"]   = new_diagram
                df.at[idx, "filming_date"]  = (
                    datetime.date.today().isoformat()
                    if new_status == "Filmed" else
                    row.get("filming_date", "")
                )

                # Write CSV
                df.to_csv(CSV_PATH, index=False)

                # Also update demo drill_library.csv if it exists
                demo_csv = Path(
                    "data/production/users/demo/drill_library.csv"
                )
                if demo_csv.exists():
                    df.to_csv(demo_csv, index=False)
                
                st.session_state.admin_success_msg = f"✅ {drill_id} saved."
                st.rerun()

# Git push section
st.divider()
st.subheader("🚀 Publish to GitHub")
st.caption(
    "Pushes updated drill_library.csv to GitHub. "
    "Streamlit Cloud redeploys in ~60 seconds."
)

if st.button("Push to GitHub", type="primary"):
    import subprocess
    result = subprocess.run(
        ["git", "add", "data/production/drill_library.csv"],
        capture_output=True, text=True,
        cwd=str(Path.cwd())
    )
    if result.returncode != 0:
        st.error(f"git add failed: {result.stderr}")
    else:
        commit = subprocess.run(
            ["git", "commit", "-m", "Player AI — drill library content update"],
            capture_output=True, text=True,
            cwd=str(Path.cwd())
        )
        push = subprocess.run(
            ["git", "push", "origin", "main"],
            capture_output=True, text=True,
            cwd=str(Path.cwd())
        )
        if push.returncode == 0:
            st.success("✅ Pushed to GitHub!")
            st.caption(
                "Streamlit Cloud will redeploy in ~60s."
            )
        else:
            st.error(f"Push failed: {push.stderr}")
            st.caption(
                "Push may fail on Streamlit Cloud "
                "(read-only fs). Use locally or via "
                "GitHub web editor for cloud deploys."
            )
