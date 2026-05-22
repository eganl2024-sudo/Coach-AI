"""Developer tools for generating drill diagrams from metadata."""
import json
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import config
import data_loader
import session_state
import diagram_renderer
from auth import require_auth

st.set_page_config(page_title="Diagram Tools", page_icon="🛠️", layout="wide")

require_auth()
ui_components.require_page_access("pages/7_Diagram_Tools.py")

ui_title = "🛠️ Diagram Tools"

if not getattr(config, "DEV_TOOLS", False):
    st.title(ui_title)
    st.warning("Developer tools are disabled. Set DEV_MODE/DEV_TOOLS=True in config.py to use this page.")
    st.stop()

st.title(ui_title)
st.caption("Generate static diagram assets from drill metadata.")

session_state.init_session_state()

if 'data_path' not in st.session_state:
    st.session_state.data_path = config.get_data_path()

if st.session_state.drills_df is None:
    st.session_state.drills_df = data_loader.load_drills(st.session_state.data_path)

drills_df = st.session_state.drills_df.copy()
drills_df['diagram_metadata'] = drills_df.get('diagram_metadata', '').fillna('')
metadata_rows = drills_df[drills_df['diagram_metadata'].str.strip() != '']

if metadata_rows.empty:
    st.info("No drills contain diagram metadata yet. Add JSON to the `diagram_metadata` column to begin.")
    st.stop()

options = [
    (row['drill_id'], row['drill_name'])
    for _, row in metadata_rows.iterrows()
]

def format_option(option):
    drill_id, name = option
    return f"{drill_id} — {name}" if name else drill_id

selected = st.selectbox(
    "Select drill",
    options=options,
    format_func=format_option
)
selected_row = metadata_rows[metadata_rows['drill_id'] == selected[0]].iloc[0]

metadata_str = selected_row.get('diagram_metadata', '')
try:
    metadata = json.loads(metadata_str)
except json.JSONDecodeError:
    st.error("Diagram metadata is not valid JSON. Please fix the value in drill_library.csv.")
    st.json(metadata_str)
    st.stop()

st.subheader("Metadata Preview")
st.json(metadata)

diagram_path = (selected_row.get('diagram_path') or '').strip()
if not diagram_path:
    diagram_path = f"assets/diagrams/{selected_row['drill_id']}.svg"

output_path = config.get_diagram_file(diagram_path)
st.write(f"Output: `{diagram_path}`")

col_a, col_b = st.columns(2)
with col_a:
    if st.button("Generate Diagram", type="primary"):
        # Enforce allowed image extensions and naming convention
        allowed_exts = {".png", ".jpg", ".jpeg", ".svg"}
        if output_path.suffix.lower() not in allowed_exts:
            st.error(f"Unsupported file type {output_path.suffix}. Use one of: {', '.join(allowed_exts)}")
        elif output_path.stem != selected_row['drill_id']:
            st.error(f"Filename should match drill_id ({selected_row['drill_id']}). Rename or adjust path.")
        else:
            try:
                diagram_renderer.save_diagram(metadata, output_path)
                st.success(f"Diagram saved to {output_path}")
            except RuntimeError as exc:
                st.error(str(exc))

with col_b:
    if output_path and output_path.exists():
        st.image(str(output_path), caption="Current diagram", use_column_width=True)
    else:
        st.info("No diagram file found yet. Generate one to preview it.")
