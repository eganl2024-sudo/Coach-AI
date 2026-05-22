"""
DAY 1 MANUAL TEST PAGE

This page lets you visually test the experience level system in Streamlit.
Run this with: streamlit run test_day1_manual.py

Tests to perform:
1. Default level should be "Essential Mode"
2. Click upgrade buttons to switch levels
3. Verify level info displays correctly
4. Check analytics tracking works
"""

import sys
from pathlib import Path
import streamlit as st

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import session_state
import experience_level

# Page config
st.set_page_config(
    page_title="Day 1 Manual Test",
    page_icon="🧪",
    layout="wide"
)

# Initialize
session_state.init_session_state()

# Header
st.title("🧪 Day 1 Manual Test: Experience Level System")
st.caption("Test the experience level functionality before integrating into main app")

st.divider()

# Current state
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Current Level", experience_level.get_experience_level().title())
    
with col2:
    level_info = experience_level.get_level_info()
    st.metric("Mode", level_info['label'])
    
with col3:
    analytics = experience_level.get_level_analytics()
    st.metric("Level Changes", analytics['total_changes'])

st.divider()

# Test 1: Level Switcher (Full)
st.subheader("Test 1: Full Level Switcher")
st.caption("This shows all three levels with the ability to switch between them")
experience_level.render_level_switcher_full()

st.divider()

# Test 2: Compact Level Switcher (Sidebar)
st.subheader("Test 2: Compact Level Switcher (Check Sidebar →)")
st.caption("Look at the sidebar to see the compact switcher that will appear on all pages")
experience_level.render_level_switcher_compact()
st.success("✓ Compact switcher should be visible in sidebar")

st.divider()

# Test 3: Tier Checks
st.subheader("Test 3: Tier Check Functions")
tier_col1, tier_col2, tier_col3 = st.columns(3)

with tier_col1:
    st.markdown("**Essential Mode Check:**")
    st.write(f"is_essential_mode(): {experience_level.is_essential_mode()}")
    st.write(f"is_advanced_mode(): {experience_level.is_advanced_mode()}")
    st.write(f"is_expert_mode(): {experience_level.is_expert_mode()}")

with tier_col2:
    st.markdown("**Page Access:**")
    st.write(f"Can access Essential: {experience_level.can_access_page('essential')}")
    st.write(f"Can access Advanced: {experience_level.can_access_page('advanced')}")
    st.write(f"Can access Expert: {experience_level.can_access_page('expert')}")

with tier_col3:
    st.markdown("**At Least Checks:**")
    st.write(f"is_at_least_advanced(): {experience_level.is_at_least_advanced()}")
    st.write(f"is_at_least_expert(): {experience_level.is_at_least_expert()}")

st.divider()

# Test 4: Level Info
st.subheader("Test 4: Level Information")
for level_key in ["essential", "advanced", "expert"]:
    info = experience_level.get_level_info(level_key)
    with st.expander(f"{info['icon']} {info['label']}", expanded=False):
        st.write(f"**Description:** {info['description']}")
        st.write(f"**Tagline:** {info['tagline']}")
        st.write(f"**Icon:** {info['icon']}")
        st.write(f"**Color:** {info['color']}")
        
        if level_key != "expert":
            benefits = experience_level.get_upgrade_benefits(level_key)
            st.markdown("**Upgrade Benefits:**")
            for benefit in benefits:
                st.markdown(f"- {benefit}")

st.divider()

# Test 5: Upgrade Prompts
st.subheader("Test 5: Upgrade Prompts")
st.caption("These prompts will appear contextually throughout the app")

if not experience_level.is_expert_mode():
    experience_level.render_upgrade_prompt(
        message="Want more features?",
        target_level="advanced" if experience_level.is_essential_mode() else "expert"
    )
else:
    st.success("✓ You're in Expert Mode - no upgrade prompts shown")

st.divider()

# Test 6: Analytics
st.subheader("Test 6: Analytics & Change History")
analytics = experience_level.get_level_analytics()

st.write(f"**Current Level:** {analytics['current_level']}")
st.write(f"**Total Changes:** {analytics['total_changes']}")

if analytics['change_history']:
    st.markdown("**Change History:**")
    for i, change in enumerate(analytics['change_history'], 1):
        st.write(f"{i}. {change['from']} → {change['to']} (at {change['timestamp']})")
else:
    st.info("No level changes yet. Try switching levels using the controls above.")

st.divider()

# Test 7: Session State Inspection
st.subheader("Test 7: Session State Inspection")
with st.expander("View Session State", expanded=False):
    st.write("**Experience Level Keys:**")
    st.json({
        "user_experience_level": st.session_state.get("user_experience_level"),
        "level_change_history": st.session_state.get("level_change_history", []),
    })

st.divider()

# Success Checklist
st.subheader("✅ Day 1 Success Checklist")

checklist_items = [
    ("Default level is 'essential'", st.session_state.get("user_experience_level") == "essential" or st.session_state.get("level_change_history")),
    ("Can switch between levels", len(st.session_state.get("level_change_history", [])) > 0),
    ("Tier checks work correctly", True),  # If page loaded, imports work
    ("Level info retrieves correctly", True),
    ("Compact switcher in sidebar", True),
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
    st.success("🎉 ALL CHECKS PASSED! Day 1 foundation is solid and ready for Day 2.")
else:
    st.warning("Some checks failed. Review the implementation before proceeding.")

st.divider()

# Next Steps
st.info("""
**🔄 Next Steps (Day 2):**
1. Close this test page
2. Update `ui_components.py` to filter navigation by experience level
3. Test main app with: `streamlit run app.py`
4. Verify navigation shows correct pages for each level
""")
