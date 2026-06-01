"""Player AI - Highlight Reel Guide"""
import streamlit as st
import sys
import pandas as pd
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import importlib
import config
import data_loader
import session_state
import ui_components

# Force reload of custom modules to clear Streamlit's running process cache
try:
    importlib.reload(config)
    importlib.reload(data_loader)
    importlib.reload(session_state)
    importlib.reload(ui_components)
except Exception:
    pass

from auth import require_auth

# Page configuration
st.set_page_config(
    page_title="Highlight Reel Guide | Player AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Enforce authentication
require_auth()

# Initialize session state
session_state.init_session_state()
if "data_path" not in st.session_state:
    st.session_state.data_path = config.get_data_path()

# Load current profile details
athlete_profile = data_loader.load_athlete_profile(st.session_state.data_path) or {}

# Check for redirect banner
if not athlete_profile or not athlete_profile.get("name"):
    st.session_state.redirect_banner = "Please set up your Player Profile first to access the Highlight Reel Guide!"
    st.switch_page("pages/5_Team_Hub.py")
    st.stop()

# Store in session state
st.session_state.athlete_profile = athlete_profile

# Render standard navigation
ui_components.render_nav(active_label="Highlight Reel")

st.divider()

# CSS
st.markdown("""
<style>
.reel-hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
    border-radius: 12px;
    padding: 32px;
    margin-bottom: 28px;
    box-shadow: 0 4px 15px rgba(15, 23, 42, 0.15);
}
.section-title {
    font-size: 22px;
    font-weight: 700;
    color: #0f172a;
    margin-top: 24px;
    margin-bottom: 16px;
    border-left: 5px solid #1e3a8a;
    padding-left: 12px;
}
.callout-box {
    background-color: #f8fafc;
    border-left: 4px solid #3b82f6;
    padding: 18px;
    border-radius: 8px;
    margin-bottom: 24px;
    color: #334155;
    font-size: 15px;
    line-height: 1.6;
}
.rule-card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    height: 100%;
}
.rule-number {
    font-size: 32px;
    font-weight: 800;
    color: #1e3a8a;
    margin-bottom: 10px;
    line-height: 1;
}
.rule-title {
    font-size: 17px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 8px;
}
.rule-text {
    font-size: 14px;
    color: #475569;
    line-height: 1.6;
}
.priority-box {
    background-color: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 10px;
    padding: 24px;
    margin-bottom: 20px;
}
.priority-box h4 {
    color: #166534;
    font-size: 18px;
    font-weight: 700;
    margin-top: 0;
    margin-bottom: 16px;
}
.priority-list {
    margin: 0;
    padding-left: 20px;
    color: #14532d;
    line-height: 1.7;
    font-size: 15px;
}
.priority-list li { margin-bottom: 12px; }
.priority-list li strong { color: #166534; }
.leave-out-box {
    background-color: #fef2f2;
    border: 1px solid #fca5a5;
    border-radius: 10px;
    padding: 24px;
    margin-bottom: 20px;
}
.leave-out-box h4 {
    color: #991b1b;
    font-size: 18px;
    font-weight: 700;
    margin-top: 0;
    margin-bottom: 14px;
}
.leave-out-text {
    margin: 0;
    color: #7f1d1d;
    line-height: 1.7;
    font-size: 15px;
}
.structure-box {
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 24px;
    margin-bottom: 20px;
}
.structure-box h4 {
    color: #0f172a;
    font-size: 18px;
    font-weight: 700;
    margin-top: 0;
    margin-bottom: 14px;
}
.structure-text {
    margin: 0;
    color: #334155;
    line-height: 1.7;
    font-size: 15px;
}
.timeline-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 16px;
    margin-bottom: 24px;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
}
.timeline-table th {
    background-color: #0f172a;
    color: white;
    text-align: left;
    padding: 14px 18px;
    font-weight: 600;
    font-size: 15px;
}
.timeline-table td {
    padding: 14px 18px;
    border-bottom: 1px solid #e2e8f0;
    color: #334155;
    font-size: 14px;
}
.timeline-table tr:last-child td { border-bottom: none; }
.timeline-table tr:nth-child(even) { background-color: #f8fafc; }
.timeline-table tr:hover { background-color: #f1f5f9; }
.coming-soon-card {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
    color: white;
    border-radius: 12px;
    padding: 28px;
    margin-top: 32px;
    box-shadow: 0 4px 15px rgba(15, 23, 42, 0.15);
}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────
st.markdown("""
<div class="reel-hero">
    <h1 style="color:white; margin:0 0 8px 0;">🎬 Highlight Reel Guide</h1>
    <p style="color:rgba(255,255,255,0.9); font-size:16px; margin:0;">
        What college coaches actually want to see — by position
    </p>
</div>
""", unsafe_allow_html=True)

# ── 4 Rules ───────────────────────────────────────────────────
st.markdown('<div class="section-title">4 Rules Every Reel Must Follow</div>', unsafe_allow_html=True)
st.markdown("""
<div class="callout-box">
    Before diving into position-specific details, every recruiting highlight reel must adhere to these
    foundational rules. Coaches watch hundreds of reels a week; standing out requires getting these right first.
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div class="rule-card">
        <div class="rule-number">1</div>
        <div class="rule-title">Keep it under 3 minutes</div>
        <div class="rule-text">
            College coaches watch dozens of reels per week. A 6-minute reel signals the player and family
            don't understand the recruiting process. 90 seconds to 3 minutes is the sweet spot.
        </div>
    </div>
    <div class="rule-card">
        <div class="rule-number">3</div>
        <div class="rule-title">Real game footage only</div>
        <div class="rule-text">
            Training clips can supplement but should never lead. College coaches want to see how you perform
            under real match pressure, with real opponents, at real pace.
        </div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="rule-card">
        <div class="rule-number">2</div>
        <div class="rule-title">Quality over quantity</div>
        <div class="rule-text">
            Eight clips of you doing something exceptional beat twenty clips of average plays. Every clip
            should make the coach think "I want to see more of this player."
        </div>
    </div>
    <div class="rule-card">
        <div class="rule-number">4</div>
        <div class="rule-title">Start strong</div>
        <div class="rule-text">
            The first 20 seconds determine whether a coach watches the rest. Lead with your single best
            moment — the goal, the tackle, the assist, the save. Do not build up to it.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Position Tabs ─────────────────────────────────────────────
st.markdown('<div class="section-title">Position-Specific Requirements</div>', unsafe_allow_html=True)

# Load athlete profile for smart pre-selection
athlete_profile = data_loader.load_athlete_profile(st.session_state.data_path) or {}
player_position = athlete_profile.get("position", "")

# Map the player's position to the correct tab index
position_to_index = {
    "Goalkeeper": 0,
    "Center Back": 1,
    "Full Back": 2,
    "Midfielder": 3,
    "Defensive Midfielder": 3,
    "Central Midfielder": 3,
    "Attacking Midfielder": 3,
    "Winger": 4,
    "Striker": 5,
    "Forward": 5,
}

tab_index = 0
if athlete_profile and player_position:
    tab_index = position_to_index.get(player_position, 0)
    st.info(f"Showing your position: {player_position}. Switch tabs to explore other positions.")

tabs_list = [
    "🧤 Goalkeeper",
    "🛡️ Center Back",
    "🏃‍♂️ Full Back",
    "🏃 Midfielder",
    "⚡ Winger",
    "🥅 Striker"
]
default_tab = tabs_list[tab_index]
pos_tabs = st.tabs(tabs_list, default=default_tab)

# Goalkeeper
with pos_tabs[0]:
    st.markdown("""
    <div class="priority-box">
        <h4>🎯 What GK Coaches Prioritize (in order):</h4>
        <ol class="priority-list">
            <li><strong>Distribution quality:</strong> Goal kicks, throws, played passes under pressure.
                Modern coaches care more about this than almost anything else. Show clips of you playing
                out under a press, not just saves.</li>
            <li><strong>Shot stopping:</strong> 2–3 clips of different save types — near post driven shot,
                diving save, reaction save. Do not show 8 saves. Show 3 exceptional ones.</li>
            <li><strong>Cross claiming:</strong> One or two clips of you commanding and catching a cross
                confidently, especially in traffic.</li>
            <li><strong>1v1 situations:</strong> One clip of you saving a 1v1 cleanly, staying big and
                forcing the shot into your body.</li>
        </ol>
    </div>
    <div class="leave-out-box">
        <h4>⚠️ What to leave out:</h4>
        <p class="leave-out-text">
            Punching crosses (shows uncertainty), routine catches, any save where the shot was weak,
            long goal kicks where you cannot see the outcome.
        </p>
    </div>
    <div class="structure-box">
        <h4>📋 Ideal reel structure for GKs:</h4>
        <p class="structure-text">
            Open with your best save (10s). Distribution sequence showing 2–3 clean plays out of the
            back (30s). Cross claiming clip (15s). Second strong save (10s). 1v1 clip (10s). Close with
            a confident distribution moment (10s). <strong>Total: ~85 seconds.</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

# Center Back
with pos_tabs[1]:
    st.markdown("""
    <div class="priority-box">
        <h4>🎯 What CB Coaches Prioritize:</h4>
        <ol class="priority-list">
            <li><strong>Composure on the ball:</strong> Clips of you receiving under pressure and playing
                out cleanly. This is what separates modern CBs. Show at least 2 clips.</li>
            <li><strong>Aerial duels:</strong> One or two clips of you winning a header decisively, both
                defensive and attacking set pieces if possible.</li>
            <li><strong>1v1 defending:</strong> One clip of you staying disciplined, showing a striker
                inside, and winning the ball cleanly.</li>
            <li><strong>Reading the game:</strong> A clip of you stepping to intercept a through ball or
                cutting off a passing lane. Hard to film but extremely valuable.</li>
        </ol>
    </div>
    <div class="leave-out-box">
        <h4>⚠️ What to leave out:</h4>
        <p class="leave-out-text">
            Slide tackles (show last resort, not first option), clearances that go nowhere,
            headers that lack conviction.
        </p>
    </div>
    <div class="structure-box">
        <h4>📋 Ideal reel structure for CBs:</h4>
        <p class="structure-text">
            Composure under press clip (15s). Aerial duel won (10s). 1v1 defense clip (15s).
            Distribution sequence showing range of passing (20s). Set piece defensive moment (10s).
            Best individual defending moment (15s). <strong>Total: ~85 seconds.</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

# Full Back
with pos_tabs[2]:
    st.markdown("""
    <div class="priority-box">
        <h4>🎯 What FB Coaches Prioritize:</h4>
        <ol class="priority-list">
            <li><strong>Defending wide:</strong> Your ability to handle a winger 1v1 without diving in.
                One clip of you staying disciplined and winning.</li>
            <li><strong>Attacking contribution:</strong> An overlap run that leads to a cross or
                combination. Shows coaches you understand the modern FB role.</li>
            <li><strong>Recovery pace:</strong> A clip of you tracking back after getting caught high.
                Shows work ethic and recovery speed.</li>
            <li><strong>Crossing quality:</strong> If you have a quality cross that leads to a chance
                or goal, include it. If not, do not force it.</li>
        </ol>
    </div>
    <div class="leave-out-box">
        <h4>⚠️ What to leave out:</h4>
        <p class="leave-out-text">
            Overlapping runs that end without a cross or combination, tracking back runs where you are
            clearly beaten, any defensive moment where you dive in and get turned.
        </p>
    </div>
    <div class="structure-box">
        <h4>📋 Ideal reel structure for FBs:</h4>
        <p class="structure-text">
            Best defending 1v1 clip (15s). Overlap into crossing position (15s). Recovery run clip (10s).
            Second defending clip (10s). Combination with winger (15s). <strong>Total: ~65 seconds.</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

# Midfielder
with pos_tabs[3]:
    st.markdown("""
    <div class="priority-box">
        <h4>🎯 What MID Coaches Prioritize:</h4>
        <ol class="priority-list">
            <li><strong>Receiving and turning under pressure:</strong> The single most important technical
                skill for midfielders in the college game. Show at least 2 clips of you receiving and
                playing forward quickly.</li>
            <li><strong>Progressive passing:</strong> A clip of a through ball or line-breaking pass that
                creates a chance. Shows vision.</li>
            <li><strong>Pressing and winning the ball:</strong> One clip of you winning the ball in the
                middle third and transitioning immediately.</li>
            <li><strong>Box arrivals:</strong> If you have a goal or assist from a run from deep, include
                it. This separates midfielders at the next level.</li>
        </ol>
    </div>
    <div class="leave-out-box">
        <h4>⚠️ What to leave out:</h4>
        <p class="leave-out-text">
            Sideways passes, square balls, any moment where you played safe when forward was available.
        </p>
    </div>
    <div class="structure-box">
        <h4>📋 Ideal reel structure for MIDs:</h4>
        <p class="structure-text">
            Best receiving-and-turning sequence (20s). Progressive pass leading to a chance (10s).
            Ball won and quick transition (15s). Box arrival or goal (15s). Second receiving sequence
            showing range (15s). <strong>Total: ~75 seconds.</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

# Winger
with pos_tabs[4]:
    st.markdown("""
    <div class="priority-box">
        <h4>🎯 What Winger Coaches Prioritize:</h4>
        <ol class="priority-list">
            <li><strong>1v1 in wide areas:</strong> The ability to beat a defender and create a crossing
                or shooting opportunity. Baseline expectation at college level. Show 2–3 clips.</li>
            <li><strong>Goals and assists:</strong> If you have them, they go first. College coaches
                recruit output.</li>
            <li><strong>Pressing from the front:</strong> One clip of you forcing a turnover or cutting
                off a goal kick with your pressing angle.</li>
            <li><strong>Weak foot involvement:</strong> If you can cut inside onto your weak foot and
                shoot, film it. Left-footed finishes by a right-footed winger are memorable.</li>
        </ol>
    </div>
    <div class="leave-out-box">
        <h4>⚠️ What to leave out:</h4>
        <p class="leave-out-text">
            Any cross that does not find a teammate, runs in behind that come to nothing, clips where
            you beat a defender but then lose the ball.
        </p>
    </div>
    <div class="structure-box">
        <h4>📋 Ideal reel structure for Wingers:</h4>
        <p class="structure-text">
            Best goal or assist (10s). First 1v1 won into cross or shot (15s). Second 1v1 sequence (15s).
            Pressing clip (10s). Weak foot moment if you have it (10s). Final highlight (15s).
            <strong>Total: ~75 seconds.</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

# Striker
with pos_tabs[5]:
    st.markdown("""
    <div class="priority-box">
        <h4>🎯 What Striker Coaches Prioritize:</h4>
        <ol class="priority-list">
            <li><strong>Finishing:</strong> Goals of different types — near post, far post, header, weak
                foot. Variety shows technical range.</li>
            <li><strong>Movement:</strong> A clip showing your off-ball movement creating space for a
                teammate even when you do not score. Demonstrates tactical intelligence.</li>
            <li><strong>Hold-up play:</strong> One clip of you receiving with your back to goal, holding
                a defender off, and playing a teammate in.</li>
            <li><strong>Pressing from the front:</strong> College coaches want strikers who work. Show
                one clip of your pressing effort leading to a turnover or forcing a mistake.</li>
        </ol>
    </div>
    <div class="leave-out-box">
        <h4>⚠️ What to leave out:</h4>
        <p class="leave-out-text">
            Missed chances (obviously), any clip where the goalkeeper saves a weak shot, goals where
            the goalkeeper is not between the posts.
        </p>
    </div>
    <div class="structure-box">
        <h4>📋 Ideal reel structure for Strikers:</h4>
        <p class="structure-text">
            Best goal (10s). Second goal showing different finish type (10s). Movement clip — space
            created (15s). Hold-up play and assist (15s). Pressing clip (10s). Third goal or best
            attacking moment (10s). <strong>Total: ~70 seconds.</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

# ── Recruiting Timeline ───────────────────────────────────────
st.markdown('<div class="section-title">Recruiting Timeline: When to Have Your Reel Ready</div>', unsafe_allow_html=True)
st.markdown("""
<div class="callout-box">
    Timing is everything in recruiting. Here is when you should have your highlight reel ready
    and updated throughout your high school career.
</div>
""", unsafe_allow_html=True)

timeline_df = pd.DataFrame({
    "Grade": [
        "8th grade",
        "9th grade",
        "10th grade",
        "11th grade",
        "12th grade"
    ],
    "Target Date": [
        "End of 8th grade year",
        "Start of sophomore year",
        "Summer before junior year",
        "Fall of junior year",
        "First month of school"
    ],
    "Reel Status": [
        "Training clips only OK",
        "First game reel ready",
        "Full polished reel",
        "Final reel locked",
        "Signing reel ready"
    ],
    "Priority Action": [
        "Attend showcases, get filmed",
        "Submit to ID camps, build list",
        "Email coaches, register NCSA",
        "Official visits, verbal commits",
        "NLI signing if committing"
    ]
})

st.dataframe(timeline_df, use_container_width=True, hide_index=True)

# ── Coming Soon ───────────────────────────────────────────────
st.markdown("""
<div class="coming-soon-card">
    <h3 style="margin:0 0 8px 0;">🚀 Highlight Reel Workshop — Coming Soon</h3>
    <p style="margin:0; opacity:0.9;">
        Player AI will soon offer personalized highlight reel feedback from our college and professional
        coaching staff — Mitch, Nick, and Liam will review your footage and tell you exactly
        what to keep, what to cut, and how to structure your reel for maximum impact with college coaches.
    </p>
</div>
""", unsafe_allow_html=True)
