# Player AI ⚽🚀

**An AI-powered, data-driven training ecosystem that structures personalized development, visualizes athletic metrics, and calculates Recruit Readiness — built for competitive soccer athletes.**

[![Status](https://img.shields.io/badge/status-live%20on%20Streamlit%20Cloud-success.svg?style=flat-square)](https://soccermentor.streamlit.app)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg?style=flat-square)](https://python.org)
[![Streamlit](https://img.shields.io/badge/streamlit-1.51%2B-red.svg?style=flat-square)](https://streamlit.io)
[![Tests](https://img.shields.io/badge/tests-53%2F53%20passed-brightgreen.svg?style=flat-square)](https://github.com/eganl2024-sudo/MDP_APP)

---

## 🔗 Try It Now

**Live app:** [https://soccermentor.streamlit.app](https://soccermentor.streamlit.app)

**Demo login — no sign-up required:**

| Field | Value |
|---|---|
| Username | `demo` |
| Password | `PlayerAI2026` |

The demo account loads **Alex's pre-seeded dashboard** — RRS 62, 3 weeks of training history, current week in progress. It resets to this clean state automatically on every login, so it's always ready to show.

---

## 🎯 What is Player AI?

**Player AI** transforms individual soccer development by acting as an automated personal trainer and athletic advisor. It helps competitive soccer athletes structure their weekly training, log completions, build streaks, and measure readiness through a proprietary quantitative scoring engine.

Core capabilities:
- 🗓️ **Multi-week training plan persistence** — plans roll over automatically after 7 days; all history is preserved across weeks
- 📊 **Recruit Readiness Score (RRS)** — proprietary 0–100 score across 4 measurable pillars
- 🔐 **Per-user sandboxed accounts** — every player's data is fully isolated
- 🎥 **Highlight Reel** — video feed curated to the player's position and focus areas
- 💬 **Mentor Feed** — coach commentary matched to the athlete's development profile

---

## 🧠 The Recruit Readiness Score (RRS) Engine

The RRS (`src/rrs_calculator.py`) produces a unified **0–100** score across 4 weighted pillars:

| Pillar | Weight | What It Measures |
|---|---|---|
| **Consistency** | 30% | Training habit reliability — weighted 4-week window + streak bonuses |
| **Volume** | 20% | Total sessions completed vs. expectation since account creation |
| **Coverage** | 25% | Whether recent sessions trained the player's stated focus areas |
| **Progression** | 25% | Whether drill difficulty aligns with the athlete's stated level |

### Benchmark Thresholds

| Score | Label |
|---|---|
| 0–24 | Getting Started |
| 25–44 | Recreational Player |
| 45–59 | Club Level |
| 60–74 | Varsity Starter |
| 75–87 | College Prospect |
| 88–100 | D1 Ready |

---

## 📁 Project Architecture

```
Coach AI/
├── app.py                          # Streamlit entry point
├── requirements.txt
├── pytest.ini
│
├── pages/                          # 7 Streamlit pages
│   ├── 0_Coach_Home.py             # Dashboard — RRS, active streak, weekly progress
│   ├── 1_Drill_Library.py          # Drill browser — filter by skill, category, difficulty
│   ├── 2_Practice_Generator.py     # Training plan generator + 7-day auto-rollover
│   ├── 3_Practice_History.py       # Multi-week history — week selector, archived view
│   ├── 4_Highlight_Reel.py         # Video & media hub
│   ├── 5_Team_Hub.py               # Athlete profile setup
│   └── 6_Mentor_Feed.py            # Position-matched coach commentary feed
│
├── src/                            # Business logic
│   ├── rrs_calculator.py           # RRS engine (4 pillars, benchmarks, next actions)
│   ├── training_plan_generator.py  # Multi-week plan builder + archival logic
│   ├── data_loader.py              # Persistence layer + format migration helpers
│   ├── completion_tracker.py       # Session completion + streak tracking
│   ├── auth.py                     # Login, signup, per-user sandbox, demo account reset
│   ├── db.py                       # Supabase client (users, user_data tables)
│   ├── config.py                   # Paths, constants, mode flags
│   └── ui_components.py            # Shared nav, CSS, chart widgets
│
├── data/
│   ├── demo/                       # Pre-seeded demo data (Alex, RRS 62, 3 weeks)
│   │   ├── athlete_profile.json
│   │   ├── weekly_training_plan.json   # 3-week multi-week format
│   │   ├── completion_log.json         # 10 sessions across weeks 1, 2, 3
│   │   ├── rrs_history.json
│   │   └── mentor_feed.json
│   └── production/
│       ├── drill_library.csv           # Master drill database
│       ├── mentor_feed.json
│       └── users/                      # Per-user sandboxes (auto-created on signup)
│           └── demo/                   # Demo account sandbox (resets on every login)
│
├── scripts/
│   ├── seed_demo.py                # Reset demo data to known state + refresh sandbox
│   └── create_demo_account.py      # One-time: register demo user in Supabase
│
└── tests/                          # 53 unit + end-to-end tests
```

---

## ⚡ Quick Start (Local)

```powershell
# Activate venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py --server.fileWatcherType none
```

Open **[http://localhost:8501](http://localhost:8501)**. Log in with any account or use the demo credentials above.

---

## 🗓️ Multi-Week Training Plan Persistence

As of June 2026, training plans are fully **multi-week persistent**:

- **No data loss between weeks** — when a week rolls over, the old plan is archived and the new week is appended. Completion history is never cleared.
- **7-day auto-rollover** — `pages/2_Practice_Generator.py` detects when the current week's `generated_date` is > 7 days old and automatically archives it and generates week N+1
- **Week selector in History** — `pages/3_Practice_History.py` shows all archived weeks via dropdown; archived weeks are read-only, current week has Mark Complete buttons
- **RRS uses all weeks** — Consistency and Volume use all-time completions; Coverage and Progression look up drills across all plan weeks
- **Backward compatible** — old single-week plans are silently migrated to the new multi-week format on first load (no manual action needed)

The demo account demonstrates this across 3 full weeks (weeks 1+2 archived at 4/4, week 3 in progress at 2/4).

---

## 🔐 Demo Account

The `demo` user is a **permanent account in Supabase** with automatic reset behavior:

- **Sandbox resets on every login** — `auth.py` overwrites the demo sandbox with fresh files from `data/demo/` immediately after `verify_password()` succeeds
- **No drift** — regardless of what a previous visitor completed, the next login always sees Alex's clean baseline (RRS 62, 10 sessions, week 3 in progress)
- **Credentials:** `demo` / `PlayerAI2026`

### Maintenance Commands

```powershell
# Reset demo seed data and refresh sandbox (if it exists)
python scripts/seed_demo.py

# Re-register demo account in Supabase (safe to re-run; skips if exists)
$env:SUPABASE_URL="https://ejfuesjtzsxxjdzaywjb.supabase.co"
$env:SUPABASE_KEY="your-key"
python scripts/create_demo_account.py
```

---

## 🧪 Testing Suite

53 unit and end-to-end tests covering:

- Drill loading resilience & schema auto-repair
- RRS calculation: all 4 pillars, bonuses, milestone thresholds
- Multi-week plan generation, rollover, and week number incrementing
- `get_current_week()` / `get_all_weeks()` data_loader helper correctness
- Multi-user registration & secure PBKDF2 credential verification
- Completion tracker streak logic

```powershell
pytest
# 53 passed in ~5s
```

---

## 🚀 Streamlit Cloud Deployment

**Live:** [https://soccermentor.streamlit.app](https://soccermentor.streamlit.app)

To deploy your own instance:
1. Fork `eganl2024-sudo/MDP_APP` and connect at [share.streamlit.io](https://share.streamlit.io/)
2. Set **Main file path** to `app.py`
3. Add secrets under **App Settings → Secrets**:
   ```toml
   SUPABASE_URL = "https://ejfuesjtzsxxjdzaywjb.supabase.co"
   SUPABASE_KEY = "your-service-role-key"
   ```
4. Click **Deploy!**
5. Run `python scripts/create_demo_account.py` once from the Cloud shell to register the demo user

---

## 📈 Tech Stack

| Layer | Technology |
|---|---|
| App framework | Streamlit 1.51+ |
| Language | Python 3.12 |
| Database & auth | Supabase (PostgreSQL) |
| Visualization | Plotly (radar charts, line charts) |
| Data layer | Pandas, JSON, CSV |
| Testing | Pytest (53 tests) |
| Hosting | Streamlit Community Cloud |

---

## 🌟 Roadmap

- **Native mobile app** — React Native solo training tracker optimized for field use
- **Video analytics** — Computer-vision footwork analysis in the Highlight Reel
- **Full Next.js frontend** — Rebuild the full dashboard as a production React application
- **Supabase drill table** — Migrate `drill_library.csv` to cloud PostgreSQL for real-time coach edits

---

**Developed by:** Liam Jegatheeswaran  
**Notre Dame MSBA '26 / D1 NCAA Goalkeeper**  
*Project Version: 3.0 — Multi-Week Persistence + Live Demo Account*
