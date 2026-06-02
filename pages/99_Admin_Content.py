import streamlit as st
import sys
import os
import datetime
import pandas as pd
from pathlib import Path
from PIL import Image, ImageDraw

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


def generate_field_backdrop(layout_type: str, width: int = 600, height: int = 400) -> Image.Image:
    # Colors
    green = (20, 60, 32)       # premium dark green
    white = (255, 255, 255)
    
    if layout_type == "None":
        return Image.new("RGBA", (width, height), (255, 255, 255, 255))
        
    # Green background for field types
    img = Image.new("RGBA", (width, height), green + (255,))
    draw = ImageDraw.Draw(img)
    
    margin = 20
    if layout_type == "Full Field":
        # Draw outer boundary
        draw.rectangle([margin, margin, width - margin, height - margin], outline=white, width=2)
        
        # Center line
        center_x = width // 2
        draw.line([center_x, margin, center_x, height - margin], fill=white, width=2)
        
        # Center circle
        circle_r = 50
        draw.ellipse([center_x - circle_r, height // 2 - circle_r, center_x + circle_r, height // 2 + circle_r], outline=white, width=2)
        
        # Penalty areas (left and right)
        box_w = 70
        box_h = 160
        draw.rectangle([margin, height // 2 - box_h // 2, margin + box_w, height // 2 + box_h // 2], outline=white, width=2)
        draw.rectangle([width - margin - box_w, height // 2 - box_h // 2, width - margin, height // 2 + box_h // 2], outline=white, width=2)
        
        # Goal areas (six-yard box)
        goal_w = 25
        goal_h = 80
        draw.rectangle([margin, height // 2 - goal_h // 2, margin + goal_w, height // 2 + goal_h // 2], outline=white, width=2)
        draw.rectangle([width - margin - goal_w, height // 2 - goal_h // 2, width - margin, height // 2 + goal_h // 2], outline=white, width=2)
        
        # Penalty spots
        draw.ellipse([margin + 55 - 2, height // 2 - 2, margin + 55 + 2, height // 2 + 2], fill=white)
        draw.ellipse([width - margin - 55 - 2, height // 2 - 2, width - margin - 55 + 2, height // 2 + 2], fill=white)
        
    elif layout_type == "Half Field":
        center_x = width - margin
        # Draw boundary
        draw.rectangle([margin, margin, center_x, height - margin], outline=white, width=2)
        
        # Center circle line (arc on center line)
        circle_r = 60
        draw.arc([center_x - circle_r, height // 2 - circle_r, center_x + circle_r, height // 2 + circle_r], 90, 270, fill=white, width=2)
        
        # Penalty box
        box_w = 110
        box_h = 200
        draw.rectangle([margin, height // 2 - box_h // 2, margin + box_w, height // 2 + box_h // 2], outline=white, width=2)
        
        # Goal area
        goal_w = 40
        goal_h = 100
        draw.rectangle([margin, height // 2 - goal_h // 2, margin + goal_w, height // 2 + goal_h // 2], outline=white, width=2)
        
        # Penalty spot
        draw.ellipse([margin + 80 - 2, height // 2 - 2, margin + 80 + 2, height // 2 + 2], fill=white)
        
    elif layout_type == "Grid":
        draw.rectangle([margin, margin, width - margin, height - margin], outline=white, width=2)
        grid_size = 40
        for x in range(margin + grid_size, width - margin, grid_size):
            draw.line([x, margin, x, height - margin], fill=(255, 255, 255, 80), width=1)
        for y in range(margin + grid_size, height - margin, grid_size):
            draw.line([margin, y, width - margin, y], fill=(255, 255, 255, 80), width=1)
            
    return img


# Create tabs for cleaner layout
tab1, tab2 = st.tabs(["📋 Edit Drill Metadata", "🎨 Schematic Painter"])

with tab1:
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
            "Filter by presenter", presenter_options, key="metadata_presenter_filter"
        )

    with filter_col2:
        status_options = ["All", "Not Filmed", "Filmed", "Published"]
        selected_status = st.selectbox(
            "Filter by video status", status_options, key="metadata_status_filter"
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

                    # Also update demo user sandbox if it exists
                    demo_csv = Path(
                        "data/production/users/demo/drill_library.csv"
                    )
                    if demo_csv.exists():
                        df.to_csv(demo_csv, index=False)
                    
                    st.session_state.admin_success_msg = f"✅ {drill_id} saved."
                    st.rerun()

with tab2:
    st.header("🎨 Schematic Painter")
    st.write("Draw soccer drill setups on top of tactical field backdrops and link them to the drill.")
    
    # 1. Select drill
    selected_drill_id = st.selectbox(
        "Select Drill for Schematic",
        df["drill_id"].tolist(),
        key="canvas_drill_select"
    )
    
    # Get selected drill row
    drill_row = df[df["drill_id"] == selected_drill_id].iloc[0]
    
    # Check if there is an existing diagram file
    existing_path = drill_row.get("diagram_path", "")
    existing_diagram = None
    if existing_path:
        diag_file = Path(existing_path)
        if not diag_file.is_absolute():
            diag_file = Path.cwd() / diag_file
        if diag_file.exists():
            existing_diagram = diag_file
            
    use_existing = False
    if existing_diagram:
        use_existing = st.checkbox("Use existing diagram as backdrop", value=True, key="use_existing_checkbox")
        
    if use_existing and existing_diagram:
        bg_image = Image.open(existing_diagram)
        # Ensure it has correct size 600x400 for drawing
        if bg_image.size != (600, 400):
            bg_image = bg_image.resize((600, 400), Image.Resampling.LANCZOS)
    else:
        template_type = st.selectbox(
            "Select field backdrop template",
            ["Full Field", "Half Field", "Grid", "None"],
            key="backdrop_template_select"
        )
        bg_image = generate_field_backdrop(template_type)
        
    st.divider()
    
    col_c1, col_c2 = st.columns([1, 3])
    
    with col_c1:
        st.subheader("🎨 Drawing Tools")
        drawing_mode = st.selectbox(
            "Drawing Tool",
            ("freedraw", "line", "rect", "circle", "transform"),
            key="drawing_mode_select"
        )
        stroke_width = st.slider("Stroke Width", 1, 20, 3, key="stroke_width_slider")
        stroke_color = st.color_picker("Stroke Color", "#FF0000", key="stroke_color_picker")
        
    with col_c2:
        st.subheader("📝 Canvas")
        from streamlit_drawable_canvas import st_canvas
        
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",  # semi-transparent fill for shapes
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            background_image=bg_image,
            update_streamlit=True,
            height=400,
            width=600,
            drawing_mode=drawing_mode,
            key="schematic_painter_canvas"
        )
        
    st.write("")
    
    if st.button("💾 Save Schematic", type="primary", use_container_width=True, key="save_schematic_btn"):
        if canvas_result is not None and canvas_result.image_data is not None:
            # Create diagrams folder if not exists
            diagrams_dir = Path("assets/diagrams")
            diagrams_dir.mkdir(parents=True, exist_ok=True)
            
            output_file_name = f"{selected_drill_id.lower().replace('_', '-')}.png"
            output_path = diagrams_dir / output_file_name
            
            # Combine backdrop and drawing
            overlay = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
            composite = Image.alpha_composite(bg_image.convert("RGBA"), overlay)
            composite.save(output_path, "PNG")
            
            # Update the CSV
            idx = df.index[df["drill_id"] == selected_drill_id][0]
            relative_path = f"assets/diagrams/{output_file_name}"
            df.at[idx, "diagram_path"] = relative_path
            df.at[idx, "diagram_url"] = f"https://raw.githubusercontent.com/eganl2024-sudo/MDP_APP/main/{relative_path}"
            
            # Save the main CSV
            df.to_csv(CSV_PATH, index=False)
            
            # Mirror to demo user sandbox if it exists
            demo_csv = Path("data/production/users/demo/drill_library.csv")
            if demo_csv.exists():
                df.to_csv(demo_csv, index=False)
                
            st.session_state.admin_success_msg = f"✅ Schematic saved successfully for {selected_drill_id}!"
            st.rerun()

# Git push section
st.divider()
st.subheader("🚀 Publish to GitHub")
st.caption(
    "Pushes updated drill_library.csv and generated schematics to GitHub. "
    "Streamlit Cloud redeploys in ~60 seconds."
)

if st.button("Push to GitHub", type="primary", key="git_push_btn"):
    import subprocess
    # Stage CSV and any generated diagrams
    result = subprocess.run(
        ["git", "add", "data/production/drill_library.csv", "assets/diagrams/"],
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
