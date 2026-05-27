# Player Development Platform (PDP) ⚽🚀

**An AI-powered, data-driven training ecosystem that structures personalized development, visualizes athletic metrics, and calculates Recruit Readiness.**

[![Status](https://img.shields.io/badge/status-production--ready-success.svg?style=flat-square)](https://github.com/eganl2024-sudo/MDP_APP)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg?style=flat-square)](https://python.org)
[![Streamlit](https://img.shields.io/badge/streamlit-1.51%2B-red.svg?style=flat-square)](https://streamlit.io)
[![Tests](https://img.shields.io/badge/tests-42%2F42%20passed-brightgreen.svg?style=flat-square)](https://github.com/eganl2024-sudo/MDP_APP)

---

## 🎯 What is the Player Development Platform?

The **Player Development Platform** (formerly Coach AI) transforms individual soccer development by acting as an automated personal trainer and athletic advisor. It helps competitive soccer athletes optimize their training efficiency, log completions, build streaks, upload highlights, and measure progress through a proprietary quantitative engine.

Through a **progressive disclosure model**, the platform caters to three distinct tiers:
* ⚡ **Essential Mode:** Simple dashboard, 3-click weekly training plan generation, and basic log completions.
* 🎯 **Advanced Mode:** Unlocks interactive player profile settings, advanced drill browsing, and detailed focus tagging.
* 🔧 **Expert Mode:** Opens developer analytics, template building, and custom database diagnostic tools.

---

## 🧠 Scientific Core: The Recruit Readiness Score (RRS) Engine

At the heart of the platform is the **RRS Engine** (`src/rrs_calculator.py`), which calculates a unified score from **0 to 100** that gauges an athlete's preparedness for high-level competitive environments:

### The 4 Pillars of RRS
1. **Consistency (30% weight):** Measures training habit reliability over the last 4 weeks. Includes consecutive days streak bonuses (+5 points for 14-day streaks).
2. **Volume (20% weight):** Measures cumulative training hours and completed sessions against expectations since account creation.
3. **Coverage (25% weight):** Audits recent sessions against stated weak spots (e.g., *Weak Foot Development*, *Passing Speed*). Gives a +10 point bonus for targeted technical drills.
4. **Progression (25% weight):** Evaluates if the average drill difficulty aligns with the athlete's collegiate or professional goals.

### Milestones & Benchmarks
* 🥈 **0–24:** *Getting Started* (Recreational/Youth)
* 🥉 **25–44:** *Recreational Player*
* 🥇 **45–59:** *Club Level* (Competitive Club threshold)
* 🏆 **60–74:** *Varsity Starter* (Academy/Select threshold)
* 🔥 **75–87:** *College Prospect*
* 👑 **88–100:** *D1 Ready* (Elite college goalkeeper/field player readiness)

---

## 📁 Project Architecture & Tour

The codebase is organized as a co-existing system with two core applications: a **Python Streamlit dashboard application** for rapid prototyping and coach tools, and a new **Next.js & TypeScript React application** representing our pivoted web application frontend.

```
Coach AI/ (Root Directory)
├── app.py                      # Main Python Streamlit Bootstrapper
├── requirements.txt            # Python Dependencies
├── pytest.ini                  # Pytest Configuration
│
├── pages/                      # The 7 Consolidated Streamlit Pages
│   ├── 0_Coach_Home.py         # Dashboard (RRS Analytics, Milestones, Active Streak)
│   ├── 1_Drill_Library.py      # Drill browser (Filtered by Skills, Category, Difficulty)
│   ├── 2_Practice_Generator.py # AI-Powered Training Plan Generator (Intensity Curve charts)
│   ├── 3_Practice_History.py   # Training Plan Log (Save/Restore historic sessions)
│   ├── 4_Highlight_Reel.py     # Media hub (Video clips, progress uploads)
│   ├── 5_Team_Hub.py           # Athlete Profile Setup (Skill target, Focus area selector)
│   └── 6_Mentor_Feed.py        # Curator feedback stream matching the athlete's profile
│
├── src/                        # Platform Business Logic Modules (Python)
│   ├── rrs_calculator.py       # Proprietary RRS Score engine
│   ├── data_loader.py          # State persistence, CSV auto-repair, and fallback data
│   ├── db.py                   # Supabase database client interface
│   ├── training_plan_generator.py # Smart weekly planner and duration distributor
│   ├── experience_level.py     # Sidebar tier switcher & progressive disclosure manager
│   ├── auth.py                 # Multi-user login & password encryption modules
│   └── ui_components.py        # Curated charts, widgets, and modern CSS styling
│
├── web/                        # [NEW] Next.js Web Application Frontend
│   ├── package.json            # Node.js project configuration and dependencies
│   ├── tsconfig.json           # TypeScript configuration
│   ├── app/                    # Next.js App Router
│   │   ├── page.tsx            # Home page with Glassmorphic design querying Supabase
│   │   ├── layout.tsx          # Global HTML/meta template layout
│   │   └── globals.css         # Tailwind & custom CSS resets
│   ├── utils/supabase/         # Supabase Client & Cookie Sync Helpers
│   │   ├── client.ts           # Browser component Supabase client
│   │   ├── server.ts           # Server component Supabase client
│   │   └── middleware.ts       # Router middleware session keeping helper
│   └── .env.local              # Local environment secrets (ignored from git)
│
└── archive/                    # Archived legacy scripts and 20+ old sub-pages
```

---

## ⚡ Quick Start

Get both applications running locally in less than 3 minutes.

### 🐍 1. Running the Streamlit App (Python)

Cloning the repository and initializing the Python virtual environment:

```powershell
# Navigate to the project folder
cd "Coach AI"

# Initialize or activate the virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

# Run the Streamlit application
streamlit run app.py --server.fileWatcherType none
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser!

### ⚛️ 2. Running the Next.js App (TypeScript / React)

Bootstrapping and launching the web application:

```bash
# Navigate to the web folder
cd web

# Install Node dependencies
npm install

# Start the Next.js local development server
npm run dev
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser!

---

## 🧪 Testing Suite

We maintain a rigorous standard of code reliability. The codebase includes 45 end-to-end and unit tests verifying:
* Drill loading resilience & schema auto-repair.
* Experience level switcher and locked page navigations.
* RRS calculation pillars, bonuses, and milestone thresholds.
* Plan Rollover (automatic weekly rollover intervals).
* Multi-user registration & secure credential verification.

Run all tests via:
```powershell
pytest
```

---

## 🚀 Streamlit Cloud Deployment

This repository is optimized for one-click deployment on **Streamlit Community Cloud**:
1. Connect your GitHub account at **[share.streamlit.io](https://share.streamlit.io/)**.
2. Click **"New App"** and select this repository: `eganl2024-sudo/MDP_APP`.
3. Set the **Main file path** to `app.py`.
4. Add your database environment variables under **App Settings -> Secrets**:
   ```toml
   SUPABASE_URL = "https://ejfuesjtzsxxjdzaywjb.supabase.co"
   SUPABASE_KEY = "sb_publishable_Uvv5du2PbYcI2IEGp6b4kA_hAMhV-oL"
   ```
5. Click **"Deploy!"**

---

## 📈 Tech Stack

* **Front-End & Dashboards:** [Streamlit](https://streamlit.io/) (Rapid Python prototyping) & [Next.js 15 App Router](https://nextjs.org/) (Production-ready React UI)
* **Data Visualization:** [Plotly](https://plotly.com/) (D1 intensity curves & dynamic radar charts)
* **Database & Auth:** [Supabase](https://supabase.com/) (PostgreSQL cloud database, Auth engine, User isolation)
* **Data Management:** Pandas, CSV Data Layer, Schema auto-repair engines
* **Unit Testing:** Pytest

---

## 🌟 Future Roadmap

* **CSV to Supabase Migration:** Fully complete the data migration for drilling datasets to cloud PostgreSQL tables.
* **Full Next.js Feature Parity:** Rebuild the full Streamlit dashboard experience (RRS calculations, intensity maps, history tracking) as a native React Next.js application.
* **Mobile App (React Native):** Solo training tracker optimized for outdoor field use.
* **Advanced Video Analytics:** Integrate computer-vision-based footwork analysis into the Highlight Reel.

---

**Developed by:** Liam Jegatheeswaran  
**Notre Dame MSBA '26 / D1 NCAA Goalkeeper**  
*Project Version: 2.2 (Database-Ready)*

