# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Dual-stack soccer training application. The **Streamlit app** (Python) is the live production app. The **Next.js app** (`player-ai/`) is a modern frontend in active development. Both share the same Supabase backend.

## Running the Apps

### Streamlit (main production app)
```powershell
.\.venv\Scripts\Activate.ps1
streamlit run app.py --server.fileWatcherType none
# Opens at http://localhost:8501
# Demo login: demo / PlayerAI2026
```

### Next.js frontend (`player-ai/`)
```bash
cd player-ai
npm run dev    # http://localhost:3000
npm run build
```

### Tests
```powershell
pytest                          # Run all 53 tests
pytest tests/test_rrs_calculator.py  # Single file
```

### Reset demo data
```powershell
python scripts/seed_demo.py
```

## Environment Variables

**Streamlit** — `.env` (or Streamlit Cloud secrets):
```
SUPABASE_URL=...
SUPABASE_KEY=...
```

**Next.js** — `player-ai/.env.local` (git-ignored, create manually):
```
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
ANTHROPIC_API_KEY=...
```

**Local dev override:**
```
COACH_AI_DISABLE_AUTH=1   # bypass auth for local testing
```

## Architecture

### Streamlit App
- `app.py` — bootstrap: auth check → load user sandbox → route to pages
- `pages/` — 8 Streamlit pages (numbered for sidebar order). Each page imports from `src/`
- `src/` — all business logic; pages are thin UI shells over these modules

**Key `src/` modules:**
| Module | Purpose |
|--------|---------|
| `rrs_calculator.py` | RRS 4-pillar scoring engine (Consistency 30%, Volume 20%, Coverage 25%, Progression 25%) |
| `training_plan_generator.py` | Builds 7-day plans, handles multi-week rollover |
| `data_loader.py` | Persistence layer — reads/writes JSON/CSV, wraps Supabase calls |
| `db.py` | Supabase client (users, user_data, drills tables) |
| `auth.py` | Login/signup with PBKDF2 hashing |
| `session_state.py` | Streamlit `st.session_state` initialization and helpers |
| `config.py` | Constants, scoring weights, file paths |

### Data Storage
- **Supabase:** `users` table (auth), `user_data` table (per-user JSON blobs keyed by `data_key`), `drills` table (cloud drill library)
- **Local filesystem:** `data/production/users/{username}/` — per-user sandboxes auto-created on signup; each contains `athlete_profile.json`, `weekly_training_plan.json`, `completion_log.json`, `drill_library.csv`
- **Demo data:** `data/demo/` — pre-seeded fixtures; reset via `seed_demo.py`

Multi-week plan format: `weekly_training_plan.json` stores an array of week objects. On load, `data_loader.py` auto-migrates single-week (legacy) → multi-week format. 7-day auto-rollover fires in `app.py` at session start.

### Next.js App (`player-ai/`)
- App Router under `src/app/`
- `(auth)/` — login/signup pages
- `(dashboard)/` — 7 player pages mirroring Streamlit features, plus `/recruiting` (Coach Finder + AI email drafter)
- `admin/` — drill content editor
- `api/` — server actions and API routes (email drafting calls Anthropic)
- Same Supabase tables as Streamlit; UI lib is shadcn/Radix + Tailwind CSS 4

### Scraper (`scraper/`)
Two-pass pipeline for NCAA D1 coach data:
1. `scrape_coaches.py` — seeds 686 coaches across 212 programs
2. `scrape_enrich.py` — second pass to fill missing emails/phones
Output: `scraper/output/coaches_enriched.csv` — feeds the `/recruiting` Coach Finder UI

## Deployment

**Streamlit (live):** https://soccermentor.streamlit.app — deployed on Streamlit Cloud from `eganl2024-sudo/MDP_APP`. Set `SUPABASE_URL` and `SUPABASE_KEY` as cloud secrets. Run `python scripts/create_demo_account.py` once after first deploy.

**Procfile** is present for Heroku as an alternative host.

**Next.js:** Vercel-ready (`player-ai/` as root).
