"""Admin Media Manager - Upload and manage drill diagrams"""
import streamlit as st
import pandas as pd
import sys
import os
import shutil
from pathlib import Path
from PIL import Image
import io

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import config
import data_loader

st.set_page_config(page_title="Admin Media Manager", page_icon="🔐", layout="wide")

# ==========================================
# AUTHENTICATION
# ==========================================
def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        if st.session_state["password"] == st.secrets["admin_password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

if not check_password():
    st.stop()

# ==========================================
# CONSTANTS & SETUP
# ==========================================
DATA_PATH = config.get_data_path()
STATIC_ROOT = Path("static")
DIAGRAMS_ROOT = STATIC_ROOT / "diagrams"
VIDEOS_ROOT = STATIC_ROOT / "videos"
BACKUPS_ROOT = Path("backups") / "media"

# Ensure directories exist
for folder in [DIAGRAMS_ROOT, VIDEOS_ROOT, BACKUPS_ROOT]:
    folder.mkdir(parents=True, exist_ok=True)

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def optimize_image(uploaded_file, max_width=800, quality=85):
    """
    Resize and optimize image.
    Returns: (bytes_io_object, details_dict)
    """
    image = Image.open(uploaded_file)
    
    # Convert RGBA to RGB if needed
    if image.mode in ('RGBA', 'P'):
        image = image.convert('RGB')
    
    # Calculate new dimensions
    width, height = image.size
    if width > max_width:
        ratio = max_width / width
        new_width = max_width
        new_height = int(height * ratio)
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Save to buffer
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=True) # Saving as PNG for diagrams usually better, or JPEG for photos? 
    # Prompt asked for PNG/JPG. Let's infer or default to PNG for diagrams (crisper lines). 
    # Actually, for optimization, JPEG is smaller for photos, PNG for graphics. 
    # Let's check original format.
    
    output_format = "PNG"
    if uploaded_file.type == "image/jpeg":
        output_format = "JPEG"
        image.save(buffer, format=output_format, quality=quality, optimize=True)
    else:
        # Default to PNG for diagrams
        image.save(buffer, format="PNG", optimize=True)
        
    buffer.seek(0)
    
    details = {
        "original_size": uploaded_file.size,
        "new_size": buffer.getbuffer().nbytes,
        "format": output_format,
        "width": image.width,
        "height": image.height
    }
    return buffer, details

def save_drill_data(df):
    """Persist drill dataframe to CSV."""
    drill_file = Path(DATA_PATH) / 'drill_library.csv'
    df.to_csv(drill_file, index=False)
    # Update cache
    st.session_state.drills_df = df
    st.toast("✅ Database updated successfully!")

# ==========================================
# MAIN UI
# ==========================================
st.title("🔐 Admin Media Manager")
st.markdown("Upload and manage drill diagrams and videos.")

# Load Data
if 'drills_df' not in st.session_state:
    st.session_state.drills_df = data_loader.load_drills(DATA_PATH)
drills_df = st.session_state.drills_df

tab1, tab2 = st.tabs(["Single Upload", "Batch Upload"])

# ==========================================
# TAB 1: SINGLE UPLOAD
# ==========================================
with tab1:
    # 1. Select Drill
    col1, col2 = st.columns([1, 2])
    with col1:
        categories = ["All"] + sorted(drills_df['category'].dropna().unique().tolist())
        selected_category = st.selectbox("Filter Category", categories)

    with col2:
        if selected_category != "All":
            filtered_drills = drills_df[drills_df['category'] == selected_category]
        else:
            filtered_drills = drills_df
        
        drill_map = dict(zip(filtered_drills['drill_id'], filtered_drills['drill_name']))
        selected_drill_id = st.selectbox(
            "Select Drill", 
            options=drill_map.keys(), 
            format_func=lambda x: drill_map[x]
        )

    if selected_drill_id:
        drill_row = drills_df[drills_df['drill_id'] == selected_drill_id].iloc[0]
        category_slug = str(drill_row['category']).lower().strip().replace(" ", "_")
        drill_slug = str(drill_row['drill_name']).lower().strip().replace(" ", "-")[:50] # Limit length
        
        st.divider()
        st.subheader(f"Editing: {drill_row['drill_name']}")
        
        # 2. Upload Interface
        st.markdown("### 🖼️ Diagram Upload")
        
        current_url = drill_row.get('diagram_url', '')
        if pd.notna(current_url) and current_url:
            st.info(f"Current Diagram: `{current_url}`")
            if str(current_url).startswith("static/") and os.path.exists(current_url):
                 st.image(current_url, caption="Current Diagram", width=300)
        else:
            st.warning("No diagram set.")

        uploaded_file = st.file_uploader("Choose an image (PNG/JPG)", type=['png', 'jpg', 'jpeg'])

        if uploaded_file:
            with st.status("Processing image...") as status:
                optimized_buffer, details = optimize_image(uploaded_file)
                status.write("✅ Image optimized")
                
                savings = (1 - details['new_size'] / details['original_size']) * 100
                st.success(f"Compressed by {savings:.1f}% ({details['original_size']/1024:.1f}KB → {details['new_size']/1024:.1f}KB)")
                st.image(optimized_buffer, caption=f"Preview ({details['width']}x{details['height']})", width=400)
                
                if st.button("💾 Save to Library", type="primary"):
                    try:
                        save_dir = DIAGRAMS_ROOT / category_slug
                        save_dir.mkdir(parents=True, exist_ok=True)
                        
                        ext = details['format'].lower()
                        filename = f"{category_slug}-{drill_slug}.{ext}"
                        save_path = save_dir / filename
                        
                        with open(save_path, "wb") as f:
                            f.write(optimized_buffer.getbuffer())
                        
                        status.write(f"✅ Saved to {save_path}")
                        
                        relative_path = f"static/diagrams/{category_slug}/{filename}"
                        drills_df.loc[drills_df['drill_id'] == selected_drill_id, 'diagram_url'] = relative_path
                        
                        save_drill_data(drills_df)
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"Error saving file: {e}")
        st.caption(f"Drill ID: {selected_drill_id}")

# ==========================================
# TAB 2: BATCH UPLOAD
# ==========================================
with tab2:
    st.markdown("### 📦 Batch Diagram Upload")
    st.markdown("Upload multiple images and assign them to drills automatically or manually.")
    
    uploaded_files = st.file_uploader(
        "Choose diagrams", 
        accept_multiple_files=True,
        type=['png', 'jpg', 'jpeg']
    )
    
    if uploaded_files:
        st.divider()
        st.subheader("Assign Images")
        
        # Prepare drill lookup
        all_drills_map = dict(zip(drills_df['drill_id'], drills_df['drill_name']))
        drill_choices = {"SKIP": "-- Skip this image --"}
        drill_choices.update(all_drills_map)
        
        # State to track assignments usually needs keys, but here we can just read widgets
        assignments = {}
        
        for f in uploaded_files:
            col_img, col_match = st.columns([1, 3])
            
            # Clean filename for matching
            raw_name = Path(f.name).stem.lower().replace("_", " ").replace("-", " ")
            
            # Auto-Match Logic
            best_match_id = "SKIP"
            for did, dname in all_drills_map.items():
                dname_clean = dname.lower()
                # Check for containment either way
                if raw_name in dname_clean or dname_clean in raw_name:
                    best_match_id = did
                    break
            
            with col_img:
                st.image(f, width=150)
                st.caption(f.name)
            
            with col_match:
                selected = st.selectbox(
                    f"Assign '{f.name}' to:",
                    options=drill_choices.keys(),
                    format_func=lambda x: drill_choices[x],
                    index=list(drill_choices.keys()).index(best_match_id) if best_match_id in drill_choices else 0,
                    key=f"batch_{f.name}"
                )
                assignments[f] = selected
                if selected != "SKIP":
                    st.success(f"Matched: {drill_choices[selected]}")
                else:
                    st.warning("Not assigned")
            st.divider()
        
        # Batch Save Button
        to_process = {f: did for f, did in assignments.items() if did != "SKIP"}
        count = len(to_process)
        
        if count > 0:
            if st.button(f"💾 Save {count} Assigned Images", type="primary"):
                progress_bar = st.progress(0)
                success_count = 0
                
                for idx, (file_obj, drill_id) in enumerate(to_process.items()):
                    try:
                        # Process
                        optimized_buffer, details = optimize_image(file_obj)
                        
                        # Get Drill Info
                        d_row = drills_df[drills_df['drill_id'] == drill_id].iloc[0]
                        cat_slug = str(d_row['category']).lower().strip().replace(" ", "_")
                        d_slug = str(d_row['drill_name']).lower().strip().replace(" ", "-")[:50]
                        
                        # Save
                        save_dir = DIAGRAMS_ROOT / cat_slug
                        save_dir.mkdir(parents=True, exist_ok=True)
                        
                        ext = details['format'].lower()
                        fname = f"{cat_slug}-{d_slug}.{ext}"
                        save_path = save_dir / fname
                        
                        with open(save_path, "wb") as out:
                            out.write(optimized_buffer.getbuffer())
                        
                        # Update DF
                        rel_path = f"static/diagrams/{cat_slug}/{fname}"
                        drills_df.loc[drills_df['drill_id'] == drill_id, 'diagram_url'] = rel_path
                        
                        success_count += 1
                    except Exception as ex:
                        st.error(f"Failed to save {file_obj.name}: {ex}")
                    
                    progress_bar.progress((idx + 1) / count)
                
                # Single CSV Save at the end
                save_drill_data(drills_df)
                st.success(f"✅ Batch complete! {success_count} of {count} images saved.")
                st.balloons()
        else:
            st.info("Assign at least one image to a drill to save.")
