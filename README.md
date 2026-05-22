# Coach AI - Soccer Practice Planner

**3-minute professional practice planning powered by AI** ⚽🎯

[![Status](https://img.shields.io/badge/status-beta-yellow)](https://github.com)
[![Python](https://img.shields.io/badge/python-3.8+-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/streamlit-1.32+-red)](https://streamlit.io)

---

## Quick Start

```bash
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1  # Windows PowerShell

# 2. Run app
streamlit run app.py --server.fileWatcherType none

# 3. Open browser
# http://localhost:8501
```

**First time?** See [PROJECT_HANDOFF.md](PROJECT_HANDOFF.md) for complete setup guide.

---

## What is Coach AI?

**Transform practice planning from 30+ minutes to under 3 minutes.**

Coach AI is an intelligent soccer practice planning application that:
- ✅ Generates professional practices in 3 minutes
- ✅ Learns your team's focus areas and playing style  
- ✅ Adapts to coach experience level (Essential → Advanced → Expert)
- ✅ Tracks practice history and avoids drill repetition
- ✅ Exports to HTML/PDF for field use

**Target Users:** 3.2M youth soccer coaches in the US

---

## Project Structure

```
Coach AI/
├── app.py                    # Main entry point
├── requirements.txt          # Dependencies
│
├── pages/                    # Streamlit pages (20+ files)
│   ├── 0_Coach_Home.py
│   ├── 2_Practice_Generator.py    ← CORE FEATURE
│   └── 3_Practice_History.py
│
├── src/                      # Business logic (22 modules)
│   ├── practice_generator.py     ← CORE LOGIC
│   └── data_loader.py
│
├── data/                     # CSV data files
│   ├── drill_library.csv         # 35 professional drills
│   └── team_profiles.csv
│
└── docs/                     # User documentation
    ├── USER_GUIDE.md             # 25-page manual
    └── DEMO_SCRIPT.md            # 3-min demo
```

---

## Key Features

### 🎯 Three-Tier Progressive Disclosure
- **Essential Mode:** 3 pages, 5 clicks, 3 minutes to practice
- **Advanced Mode:** 7 pages, drill library, team profiles
- **Expert Mode:** 13+ pages, templates, cycles, automation

### 🧠 Intelligent Drill Selection
- Matches team focus areas (e.g., "First touch", "Quick passing")
- Adapts to skill level and age group
- Avoids drills used in last 7 days
- Distributes intensity properly (warmup → peak → cool down)

### 📊 Complete Practice Plans
- 5-6 drills per 90-minute session
- Intensity curve visualization
- Full drill descriptions with coaching points
- Equipment lists and field diagrams
- Export to HTML/PDF

---

## Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| **[PROJECT_HANDOFF.md](PROJECT_HANDOFF.md)** | Complete handoff guide | New developers |
| **[docs/USER_GUIDE.md](docs/USER_GUIDE.md)** | User manual (25 pages) | Coaches |
| **[docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md)** | 3-minute demo script | Sales/demos |
| **[docs/NAVIGATION_WALKTHROUGH.md](docs/NAVIGATION_WALKTHROUGH.md)** | User journey flows | UX review |

---

## Tech Stack

- **Framework:** Streamlit (Python web framework)
- **Data:** CSV files (will migrate to PostgreSQL)
- **Deployment:** Streamlit Cloud / Heroku ready
- **Dependencies:** pandas, plotly, python-dotenv

---

## Development

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Tests
```bash
pytest tests/
```

### Common Issues

**Issue: App constantly refreshes**
```bash
# Fix: Disable file watcher
streamlit run app.py --server.fileWatcherType none
```

**Issue: PDF export not working**
```bash
# Workaround: Use HTML export instead
# Click "Download Practice (HTML)" button
```

---

## Current Status

**✅ Completed:**
- Core practice generation working
- 35 professional drills in library
- Progressive disclosure system functional
- User documentation complete (100+ pages)
- Authentication system implemented

**⚠️ In Progress:**
- CSV → PostgreSQL migration
- PDF export reliability
- Directory cleanup
- Mobile app (React Native)

**📋 Roadmap:**
- Template Studio (save session templates)
- Practice Cycles (multi-week programs)
- Weekly Planner (calendar view)
- Multi-sport expansion

---

## Metrics

- **Code:** 3,300+ lines of Python
- **Content:** 35 professional soccer drills
- **Documentation:** 100+ pages
- **Test Data:** 43 saved practices

---

## License

Private / Not yet open source

---

## Contact

**Developer:** Liam Jegatheeswaran  
**Email:** [your email]  
**Project Start:** November 2024  
**Current Version:** 2.1 (Beta)

---

**Need help?** See [PROJECT_HANDOFF.md](PROJECT_HANDOFF.md) for complete setup guide.
