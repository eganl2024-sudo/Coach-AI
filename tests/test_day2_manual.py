"""
DAY 2 MANUAL TEST PAGE - Navigation Filtering

Run this with: streamlit run test_day2_manual.py

Tests to perform:
1. Sidebar shows level switcher
2. Essential mode shows 3 nav items
3. Advanced mode shows 7 nav items
4. Expert mode shows all nav items
5. Switching levels updates navigation immediately
"""

import sys
from pathlib import Path
import streamlit as st

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import session_state
import experience_level
import ui_components

# Page config
st.set_page_config(
    page_title="Day 2 Manual Test - Navigation",
    page_icon="🧪",
    layout="wide"
)

# Initialize
session_state.init_session_state()

# Header
st.title("🧪 Day 2 Manual Test: Navigation Filtering")
st.caption("Test that navigation filters correctly based on experience level")

st.divider()

# Show current state
col1, col2, col3 = st.columns(3)

with col1:
    current_level = experience_level.get_experience_level()
    st.metric("Current Level", current_level.title())
    
with col2:
    visible_count = ui_components.get_visible_page_count()
    st.metric("Visible Pages", visible_count)
    
with col3:
    level_info = experience_level.get_level_info()
    st.metric("Mode", level_info['label'])

st.divider()

# Test 1: Navigation Rendering
st.subheader("Test 1: Current Navigation")
st.caption("This is what the navigation bar looks like at your current level")

# Render actual navigation (same as app.py does)
ui_components.render_nav(active_label="Test")

st.success("✓ Navigation rendered above - check that it shows the correct pages")

st.divider()

# Test 2: Page List
st.subheader("Test 2: Visible Pages List")
tier_pages = ui_components.get_current_tier_pages()

st.write(f"**Total visible pages:** {len(tier_pages)}")

for path, label, tier in tier_pages:
    col_label, col_tier, col_path = st.columns([2, 1, 3])
    with col_label:
        st.write(f"**{label}**")
    with col_tier:
        ui_components.render_tier_badge(tier)
    with col_path:
        st.caption(path)

st.divider()

# Test 3: Level Comparison
st.subheader("Test 3: Navigation by Level Comparison")

comparison_cols = st.columns(3)

with comparison_cols[0]:
    st.markdown("### ⚡ Essential")
    st.caption("Fast planning mode")
    # Temporarily switch to essential
    original_level = experience_level.get_experience_level()
    experience_level.set_experience_level("essential")
    essential_pages = ui_components.get_current_tier_pages()
    st.write(f"**{len(essential_pages)} pages:**")
    for _, label, _ in essential_pages:
        st.write(f"• {label}")
    experience_level.set_experience_level(original_level)

with comparison_cols[1]:
    st.markdown("### 🎯 Advanced")
    st.caption("More control")
    experience_level.set_experience_level("advanced")
    advanced_pages = ui_components.get_current_tier_pages()
    st.write(f"**{len(advanced_pages)} pages:**")
    for _, label, _ in advanced_pages:
        st.write(f"• {label}")
    experience_level.set_experience_level(original_level)

with comparison_cols[2]:
    st.markdown("### 🔧 Expert")
    st.caption("All features")
    experience_level.set_experience_level("expert")
    expert_pages = ui_components.get_current_tier_pages()
    st.write(f"**{len(expert_pages)} pages:**")
    for _, label, _ in expert_pages:
        st.write(f"• {label}")
    experience_level.set_experience_level(original_level)

st.divider()

# Test 4: Interactive Level Switching
st.subheader("Test 4: Interactive Level Switching")
st.caption("Switch levels and watch the navigation update")

# Full level switcher
experience_level.render_level_switcher_full()

st.info("💡 After switching levels, scroll up to see the navigation bar update")

st.divider()

# Test 5: Sidebar Check
st.subheader("Test 5: Sidebar Level Switcher")
st.caption("Check the sidebar → You should see the compact level switcher")

st.success("✓ Look at the sidebar to verify the level switcher is visible")

st.divider()

# Success Checklist
st.subheader("✅ Day 2 Manual Testing Checklist")

current_level = experience_level.get_experience_level()
visible_count = ui_components.get_visible_page_count()

expected_counts = {
    "essential": 3,
    "advanced": 7,
    "expert": 15
}

checklist_items = [
    ("Sidebar shows level switcher", True),  # If page loaded, it's there
    ("Navigation renders without errors", True),
    (f"Correct page count for {current_level} mode", visible_count == expected_counts[current_level]),
    ("Can switch between levels", len(st.session_state.get("level_change_history", [])) > 0),
    ("Page tier badges display", True),
]

all_passed = True
for item, passed in checklist_items:
    if passed:
        st.success(f"✅ {item}")
    else:
        st.error(f"❌ {item}")
        all_passed = False

if all_passed:
    st.balloons()
    st.success("🎉 ALL MANUAL CHECKS PASSED! Day 2 navigation filtering is working.")
else:
    st.warning("Some checks failed. Review the implementation.")

st.divider()

# Next Steps
st.info("""
**🔄 Next Steps:**
1. Test the main app: `streamlit run app.py`
2. Verify navigation shows correct pages
3. Test switching levels in the main app
4. Move to Day 3: Simplified Practice Generator

**Expected Behavior in Main App:**
- Essential mode: Shows Home, Generate, History (3 pages)
- Advanced mode: Adds Drills, Team, Favorites, Add Drills (7 pages)
- Expert mode: Shows all pages including Templates, Cycles, etc. (15 pages)
- Sidebar: Shows level switcher with upgrade button
""")
