"""Temporary Experience Level Switcher - Testing Tool"""
import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import experience_level

st.set_page_config(page_title="Experience Level Switcher", page_icon="🔧")

st.title("🔧 Experience Level Switcher")
st.caption("Temporary tool to switch between experience levels during testing")

# Show current level
current_level = experience_level.get_experience_level()
st.info(f"**Current Level:** {current_level}")

# Display level info
level_info = experience_level.get_level_info(current_level)
if level_info:
    st.markdown(f"**Icon:** {level_info['icon']}")
    st.markdown(f"**Tagline:** {level_info['tagline']}")

st.divider()

# Show buttons to switch
st.subheader("Switch to:")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⚡ Essential Mode", use_container_width=True, type="primary" if current_level == "essential" else "secondary"):
        experience_level.set_experience_level("essential")
        st.success("✅ Switched to Essential Mode!")
        st.balloons()
        st.rerun()

with col2:
    if st.button("🎯 Advanced Mode", use_container_width=True, type="primary" if current_level == "advanced" else "secondary"):
        experience_level.set_experience_level("advanced")
        st.success("✅ Switched to Advanced Mode!")
        st.balloons()
        st.rerun()

with col3:
    if st.button("🔧 Expert Mode", use_container_width=True, type="primary" if current_level == "expert" else "secondary"):
        experience_level.set_experience_level("expert")
        st.success("✅ Switched to Expert Mode!")
        st.balloons()
        st.rerun()

st.divider()

# Quick nav back to app
st.subheader("Return to App")

nav_col1, nav_col2, nav_col3 = st.columns(3)

with nav_col1:
    if st.button("🏠 Go to Home", use_container_width=True):
        st.switch_page("app.py")

with nav_col2:
    if st.button("⚽ Go to Generator", use_container_width=True):
        st.switch_page("pages/2_Practice_Generator.py")

with nav_col3:
    if st.button("📅 Go to History", use_container_width=True):
        st.switch_page("pages/3_Practice_History.py")

st.divider()

# Show debug info
with st.expander("🔍 Debug Info", expanded=False):
    st.write("**Session State:**")
    st.write(f"- experience_level: {st.session_state.get('experience_level', 'Not set')}")
    st.write(f"- experience_level_history: {st.session_state.get('experience_level_history', [])}")
    
    st.write("\n**Available Levels:**")
    for level in ["essential", "advanced", "expert"]:
        info = experience_level.get_level_info(level)
        if info:
            st.write(f"- {level}: {info['icon']} {info['tagline']}")
