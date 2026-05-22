"""Player Development Platform - My Profile"""
import streamlit as st
import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import importlib
import config
import data_loader
import session_state
import ui_components
import training_plan_generator

# Force reload of custom modules to clear Streamlit's running process cache
try:
    importlib.reload(config)
    importlib.reload(data_loader)
    importlib.reload(session_state)
    importlib.reload(ui_components)
    importlib.reload(training_plan_generator)
except Exception:
    pass

from auth import require_auth

# Page configuration
st.set_page_config(
    page_title="My Profile - Player Development Platform",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Enforce authentication
require_auth()

# Initialize session state
session_state.init_session_state()
if "data_path" not in st.session_state:
    st.session_state.data_path = config.get_data_path()

# Render standard navigation
ui_components.render_nav(active_label="My Profile")

st.divider()

# Load current profile details
athlete_profile = data_loader.load_athlete_profile(st.session_state.data_path) or {}

is_first_visit = (
    not athlete_profile or
    not athlete_profile.get("name")
) and not st.session_state.get("onboarding_dismissed")

if is_first_visit:
    # Always reset step to 0 when entering onboarding fresh
    if "onboarding_step" not in st.session_state or not st.session_state.get("_onboarding_active"):
        st.session_state.onboarding_step = 0
        st.session_state["_onboarding_active"] = True
        
    step = st.session_state.onboarding_step
    
    # Custom styles
    st.markdown("""
    <style>
    .welcome-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 32px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        max-width: 700px;
        margin: 24px auto;
    }
    .welcome-step {
        font-size: 12px;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    .welcome-card h2 {
        font-size: 24px;
        font-weight: 800;
        color: #0f172a;
        margin-top: 0;
        margin-bottom: 12px;
    }
    .welcome-lead {
        font-size: 18px;
        color: #3b82f6;
        margin-bottom: 24px;
        font-weight: 600;
    }
    .credential-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 16px;
        margin-top: 24px;
    }
    .credential-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
    }
    .cred-name {
        font-weight: 700;
        color: #0f172a;
        font-size: 15px;
        margin-bottom: 4px;
    }
    .cred-role {
        font-size: 13px;
        color: #475569;
        margin-bottom: 4px;
    }
    .cred-level {
        display: inline-block;
        background: #eff6ff;
        color: #2563eb;
        font-size: 11px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 12px;
    }
    .rrs-explainer-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 8px;
        margin-top: 16px;
    }
    .rrs-explainer-item {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px 8px;
        text-align: center;
    }
    .rrs-explainer-item.highlight {
        background: #eff6ff;
        border-color: #bfdbfe;
    }
    .rrs-explainer-number {
        font-size: 16px;
        font-weight: 800;
        color: #1e3a8a;
        margin-bottom: 4px;
    }
    .rrs-explainer-label {
        font-size: 11px;
        font-weight: 600;
        color: #64748b;
    }
    .setup-tips {
        background: #f8fafc;
        border-radius: 8px;
        padding: 16px;
        margin-top: 16px;
    }
    .setup-tip {
        font-size: 14px;
        color: #334155;
        padding: 8px 0;
        border-bottom: 1px solid #e2e8f0;
    }
    .setup-tip:last-child {
        border-bottom: none;
    }
    </style>
    """, unsafe_allow_html=True)
    
    welcome_container = st.container()
    with welcome_container:
        if step == 0:
            st.markdown("""
            <div class="welcome-card">
                <div class="welcome-step">Step 1 of 3</div>
                <h2>Welcome to Player AI ⚽</h2>
                <p class="welcome-lead">
                    Train like a pro. Learn from ones.
                </p>
                <p>
                    Player AI gives you personalized training plans built around
                    the methods used at the professional and Division I level —
                    taught by athletes who play there right now.
                </p>
                <div class="credential-grid">
                    <div class="credential-card">
                        <div class="cred-name">Mitch Ferguson</div>
                        <div class="cred-role">Center Back · Sporting KC 2</div>
                        <div class="cred-level">MLS Next Pro</div>
                    </div>
                    <div class="credential-card">
                        <div class="cred-name">Nick Legendre</div>
                        <div class="cred-role">Winger/Forward · UNLV</div>
                        <div class="cred-level">Division I</div>
                    </div>
                    <div class="credential-card">
                        <div class="cred-name">Liam Egan</div>
                        <div class="cred-role">Goalkeeper · University of Notre Dame</div>
                        <div class="cred-level">Notre Dame</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif step == 1:
            st.markdown("""
            <div class="welcome-card">
                <div class="welcome-step">Step 2 of 3</div>
                <h2>Recruit Readiness Score (RRS) 📊</h2>
                <p class="welcome-lead">
                    Track your progress toward college and professional benchmarks.
                </p>
                <p>
                    Your Recruit Readiness Score (RRS) evaluates your training habits, volume, and focus alignment to place you in real-world collegiate recruiting tiers:
                </p>
                <div class="rrs-explainer-grid" style="grid-template-columns: repeat(3, 1fr);">
                    <div class="rrs-explainer-item">
                        <div class="rrs-explainer-number">0–24</div>
                        <div class="rrs-explainer-label">Getting Started</div>
                    </div>
                    <div class="rrs-explainer-item">
                        <div class="rrs-explainer-number">25–44</div>
                        <div class="rrs-explainer-label">Recreational</div>
                    </div>
                    <div class="rrs-explainer-item">
                        <div class="rrs-explainer-number">45–59</div>
                        <div class="rrs-explainer-label">Club Level</div>
                    </div>
                    <div class="rrs-explainer-item">
                        <div class="rrs-explainer-number">60–74</div>
                        <div class="rrs-explainer-label">Varsity Starter</div>
                    </div>
                    <div class="rrs-explainer-item highlight">
                        <div class="rrs-explainer-number">75–87</div>
                        <div class="rrs-explainer-label">College Prospect ⭐</div>
                    </div>
                    <div class="rrs-explainer-item">
                        <div class="rrs-explainer-number">88+</div>
                        <div class="rrs-explainer-label">D1 Ready</div>
                    </div>
                </div>
                <div style="margin-top: 20px; font-size: 14px; color: #475569;">
                    <p>Your RRS consists of four key pillars, each weighted to give a complete picture of your development:</p>
                    <ul style="margin-bottom: 0; padding-left: 20px;">
                        <li><strong>Consistency (30%):</strong> How reliably you train week-to-week.</li>
                        <li><strong>Volume (20%):</strong> Total sessions logged against expectations.</li>
                        <li><strong>Coverage (25%):</strong> How closely your training aligns with your focus areas.</li>
                        <li><strong>Progression (25%):</strong> Your drill difficulty compared to your playing level.</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif step == 2:
            st.markdown("""
            <div class="welcome-card">
                <div class="welcome-step">Step 3 of 3</div>
                <h2>Set Up Your Profile ⚙️</h2>
                <p class="welcome-lead">
                    Get the most out of Player AI.
                </p>
                <p>
                    Your weekly training plans and recommended drills are dynamically generated based on your profile details. Here are some quick tips:
                </p>
                <div class="setup-tips">
                    <div class="setup-tip">
                        <strong>🎯 Be Realistic with Target Level:</strong> Set your target playing level to what you aim to achieve in the next 6 months.
                    </div>
                    <div class="setup-tip">
                        <strong>👟 Choose Stated Focus Areas:</strong> Select 2-3 areas you want to improve to boost your RRS Coverage score.
                    </div>
                    <div class="setup-tip">
                        <strong>📦 Select Your Available Gear:</strong> We'll automatically filter recommendations so you only see drills you can perform.
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Navigation panel centered under 700px container
    col_btn_l, col_btn_c, col_btn_r = st.columns([1, 2, 1])
    with col_btn_c:
        col_back, col_next = st.columns([1, 2])
        with col_back:
            if step > 0:
                if st.button("← Back", use_container_width=True):
                    st.session_state.onboarding_step -= 1
                    st.rerun()
        with col_next:
            if step < 2:
                if st.button("Next →", type="primary", use_container_width=True):
                    st.session_state.onboarding_step += 1
                    st.rerun()
            else:
                if st.button("Set Up My Profile →", type="primary", use_container_width=True):
                    st.session_state.onboarding_dismissed = True
                    st.session_state["_onboarding_active"] = False
                    st.rerun()
                    
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if st.button("Skip Introduction", key="skip_intro", use_container_width=True):
            st.session_state.onboarding_dismissed = True
            st.session_state["_onboarding_active"] = False
            st.rerun()
            
    st.stop()

# Check for redirect banner
if st.session_state.get("redirect_banner"):
    st.warning(st.session_state.redirect_banner, icon="⚠️")

st.title("👤 My Profile Setup")
st.write("Customize your training parameters, position targets, and available gear to unlock personalized drills.")

# Beautiful CSS for Premium Styling
st.markdown("""
<style>
.profile-card {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 24px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    margin-bottom: 24px;
}
.profile-section-title {
    font-size: 18px;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 16px;
    border-left: 4px solid #3b82f6;
    padding-left: 10px;
}
.success-card {
    background-color: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 8px;
    padding: 16px;
    color: #166534;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# Form structure
with st.form("athlete_profile_form"):
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="profile-section-title">Personal Details</div>', unsafe_allow_html=True)
        name = st.text_input("Player Name", value=athlete_profile.get("name", ""), placeholder="e.g. Alex Morgan")
        age = st.number_input("Age", min_value=6, max_value=25, value=int(athlete_profile.get("age", 12)))
        preferred_foot = st.radio("Preferred Foot", ["Right", "Left", "Both"], index=["Right", "Left", "Both"].index(athlete_profile.get("preferred_foot", "Right")))
        
        st.markdown('<div class="profile-section-title">Position & Level</div>', unsafe_allow_html=True)
        POSITIONS = [
            "Goalkeeper",
            "Center Back",
            "Full Back",
            "Defensive Midfielder",
            "Central Midfielder",
            "Attacking Midfielder",
            "Winger",
            "Striker",
        ]

        # Safe index lookup — fallback to 0 if saved value not in list
        def _pos_index(val, options, default=0):
            try:
                return options.index(val)
            except ValueError:
                return default

        position = st.selectbox(
            "Primary Position",
            POSITIONS,
            index=_pos_index(athlete_profile.get("position", "Striker"), POSITIONS)
        )
        secondary_position = st.selectbox(
            "Secondary Position (optional)",
            ["None"] + POSITIONS,
            index=_pos_index(
                athlete_profile.get("secondary_position", "None"),
                ["None"] + POSITIONS
            )
        )
        level = st.selectbox("Experience / Playing Level", ["Recreational", "Competitive Club", "Academy/Select"], index=["Recreational", "Competitive Club", "Academy/Select"].index(athlete_profile.get("level", "Recreational")))
        
        target_level = st.selectbox(
            "Target Level (6-month goal)",
            ["Recreational", "Competitive Club", "Academy/Select"],
            index=["Recreational", "Competitive Club", "Academy/Select"].index(
                athlete_profile.get("target_level",
                    "Competitive Club" if level == "Recreational"
                    else "Academy/Select")
            ),
            help="Where do you want to be in 6 months? Sets your RRS target benchmark."
        )
        
    with col2:
        st.markdown('<div class="profile-section-title">Schedule & Targets</div>', unsafe_allow_html=True)
        sessions_per_week = st.slider("Sessions Per Week", min_value=1, max_value=5, value=int(athlete_profile.get("sessions_per_week", 3)))
        session_duration = st.selectbox("Session Duration (minutes)", [20, 30, 45, 60], index=[20, 30, 45, 60].index(athlete_profile.get("session_duration", 30)))
        
        FOCUS_AREAS = [
            "First Touch",
            "Weak Foot Development",
            "Dribbling & Ball Mastery",
            "Passing & Combination Play",
            "Finishing & Shooting",
            "1v1 Attacking",
            "1v1 Defending",
            "Positioning & Movement",
            "Heading",
            "Crossing & Service",
            "Speed & Agility",
            "Tactical Awareness",
        ]

        focus_areas = st.multiselect(
            "Training Focus Areas (choose 2–3)",
            FOCUS_AREAS,
            default=[f for f in athlete_profile.get("focus_areas", [])
                     if f in FOCUS_AREAS] or ["First Touch", "Dribbling & Ball Mastery"],
            help="These drive your drill recommendations and RRS Coverage score."
        )
        
        st.markdown('<div class="profile-section-title">Gear & Support</div>', unsafe_allow_html=True)
        equipment_available = st.multiselect(
            "Equipment & Setup Available",
            ["Ball only", "Cones", "Goal", "Rebounder/Wall", "Training partner available"],
            default=athlete_profile.get("equipment_available", ["Ball only", "Cones"])
        )

    submit_button = st.form_submit_button("💾 Save Profile", type="primary", use_container_width=True)

# Process form submission
if submit_button:
    if not name.strip():
        st.error("Please enter a valid player name.", icon="🛑")
    else:
        # Derive age_group from age
        age_val = int(age)
        if age_val <= 12:
            age_group = "U12"
        elif age_val <= 13:
            age_group = "U13"
        elif age_val <= 14:
            age_group = "U14"
        elif age_val <= 15:
            age_group = "U15"
        elif age_val <= 16:
            age_group = "U16"
        elif age_val <= 17:
            age_group = "U17"
        else:
            age_group = "U18"

        # Create profile dictionary
        updated_profile = {
            "name": name.strip(),
            "age": age,
            "preferred_foot": preferred_foot,
            "position": position,
            "secondary_position": secondary_position,
            "level": level,
            "target_level": target_level,
            "sessions_per_week": sessions_per_week,
            "session_duration": session_duration,
            "focus_areas": focus_areas,
            "equipment_available": equipment_available,
            "created_date": athlete_profile.get("created_date", None),
            "age_group": age_group
        }
        
        from datetime import date
        # Only stamp created_date if it doesn't already exist
        # (preserve original date on profile edits)
        if "created_date" not in updated_profile or not updated_profile["created_date"]:
            updated_profile["created_date"] = date.today().isoformat()
        
        # Save to JSON
        data_loader.save_athlete_profile(updated_profile, st.session_state.data_path)
        st.session_state.athlete_profile = updated_profile
        
        # Clear redirect banner flag
        if "redirect_banner" in st.session_state:
            del st.session_state.redirect_banner
            
        # Silently auto-generate a fresh training plan tailored to new profile
        drills = st.session_state.drills_df.to_dict('records')
        new_plan = training_plan_generator.generate_training_plan(updated_profile, drills)
        data_loader.save_weekly_training_plan(new_plan, st.session_state.data_path)
        st.session_state.weekly_training_plan = new_plan
        
        # Display Confirmation & Interactive Dashboard Link
        st.markdown("""
        <div class="success-card">
            <h4>🎉 Profile Saved Successfully!</h4>
            <p>Your weekly training plan has been updated and fully tailored to your age, focus areas, and gear subset.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_ok, _ = st.columns([1.5, 2])
        with col_ok:
            st.page_link("pages/0_Coach_Home.py", label="Go to My Dashboard →", icon="🏠", use_container_width=True)
