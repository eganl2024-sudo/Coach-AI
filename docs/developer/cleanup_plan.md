# Coach AI - Directory Cleanup Plan

**Analysis Date:** January 25, 2026  
**Analyzed By:** Claude (Antigravity Kit)

---

## 📊 Current State Analysis

### Root Directory (36 items - TOO MANY!)

**✅ KEEP (Production Code & Config):**
- `app.py` - Main Streamlit entry point
- `requirements.txt` - Python dependencies
- `Procfile` - Heroku deployment config
- `.gitignore` - Git configuration
- `README.md` - Project overview (GOOD!)
- `PROJECT_HANDOFF.md` - Handoff doc (GOOD!)
- `ANTIGRAVITY_CLEANUP_GUIDE.md` - This guide

**⚠️ MOVE TO /archive/ (Development Artifacts):**
- `00_data_exploration.ipynb` → archive/notebooks/
- `coach_practice_planner.ipynb` → archive/notebooks/
- `drill_library_manager.ipynb` → archive/notebooks/
- `practice_plan_generator.ipynb` → archive/notebooks/
- `debug_schedule_page1.txt` → archive/debug/
- `debug_schedule_text.txt` → archive/debug/
- `temp_session_detail_bytes.tmp` → archive/temp/
- `practice_plan_20251117.html` → archive/exports/

**📁 MOVE TO /docs/** (Documentation)
- `DEPLOYMENT.md` → docs/developer/deployment.md
- `IMPLEMENTATION_LOG.md` → docs/developer/implementation_log.md
- `GIT_CLEANUP_NOTES.md` → docs/developer/git_cleanup.md
- `WEEK2_ROADMAP.md` → docs/developer/roadmap.md
- `PRACTICE_DETAILS_VERIFICATION.md` → docs/developer/testing/

**📂 KEEP BUT ORGANIZE (Data - Move to /data/):**
- `drill_library.csv` → data/ (ALREADY IN /data/, REMOVE DUPLICATE!)
- `practice_history.csv` → data/ (ALREADY IN /data/, REMOVE DUPLICATE!)
- `practice_history_u14_boys.csv` → data/test_data/
- `team_profiles.csv` → data/ (ALREADY IN /data!, REMOVE DUPLICATE!)
- `session_templates.json` → data/

**❌ DELETE (Unrelated Projects):**
- `Grow Irish/` - COMPLETELY UNRELATED PROJECT
- `Grow_Irish_App/` - COMPLETELY UNRELATED PROJECT
- `PDF Docs/` - Move contents to docs/pdf/ then delete
- `Indiana Soccer Preview for Practice Plan.pdf` → docs/pdf/ or archive/

**⚙️ KEEP (Auto-generated):**
- `.agent/` - Antigravity config
- `.claude/` - Claude project files
- `.git/` - Git repository
- `.pytest_cache/` - Test cache
- `.streamlit/` - Streamlit config
- `.venv/` - Python virtual environment
- `__pycache__/` - Can delete (regenerates)

**🔧 REVIEW (Generated Scripts):**
- `cleanup_directory.py` - Keep or delete after using

---

## 📁 Subdirectory Analysis

### /pages/ (20+ files)
**Status:** ✅ GOOD - Core Streamlit pages
**Action:** Keep as-is, but check for:
- Duplicate files (2_Practice_Generator_tmp.txt)
- Unused pages

### /src/ (22 modules)
**Status:** ✅ GOOD - Business logic
**Action:** Keep as-is, well organized

### /data/ (Check contents)
**Action:** Consolidate all CSVs here, remove root duplicates

### /docs/ (Check contents)
**Status:** Needs organization
**Action:** Create structure:
```
/docs/
  ├── user/          (USER_GUIDE.md, DEMO_SCRIPT.md, etc.)
  ├── developer/     (DEPLOYMENT.md, IMPLEMENTATION_LOG.md, etc.)
  ├── business/      (EXECUTIVE_PRESENTATION.md, etc.)
  ├── pdf/           (PDF resources)
  └── INDEX.md       (Master index of all docs)
```

### /tests/
**Status:** ✅ GOOD
**Action:** Keep as-is

### /assets/
**Status:** Unknown (need to check)
**Action:** Review contents

### /temp/
**Status:** Should be empty or archived
**Action:** Move to /archive/temp/ or delete

---

## 🎯 Proposed New Structure

### ROOT (Cleaned - ~12 files):
```
Coach AI/
├── README.md                    ← Clean project overview
├── PROJECT_HANDOFF.md           ← For your brother  
├── app.py                       ← Main entry point
├── requirements.txt
├── Procfile
├── .gitignore
│
├── /pages/                      ← Streamlit pages (20+ files)
├── /src/                        ← Python modules (22 files)
├── /data/                       ← ALL data files consolidated
├── /docs/                       ← ALL documentation organized
├── /tests/                      ← Unit tests
├── /assets/                     ← Images, diagrams
│
├── /archive/                    ← OLD STUFF (hidden from main view)
│   ├── /notebooks/              ← .ipynb files
│   ├── /debug/                  ← debug_*.txt files
│   ├── /temp/                   ← temp files
│   └── /exports/                ← old HTML/PDF exports
│
└── [config directories]         ← .git, .venv, .streamlit, etc.
```

---

## 🗂️ Documentation Organization Plan

### Current Docs (From Project Knowledge):
1. USER_GUIDE.md - User manual
2. DEMO_SCRIPT.md - Demo guide
3. NAVIGATION_WALKTHROUGH.md - UX flows
4. DOCUMENTATION_INDEX.md - Doc index
5. COACH_AI_THREE_TIER_VISUAL_REFERENCE.md - Architecture
6. COACH_AI_EXECUTIVE_PRESENTATION.md - Business pitch
7. COACH_AI_PROJECT_DESCRIPTION.md - Complete overview
8. Coach_AI_Quick_Start_Guide_DAY1_DRAFT.md - Quick start
9. Coach_AI_Documentation_DAY2_COMPLETE.md - FAQ/Onboarding
10. Coach_AI_Troubleshooting_DAY4_COMPLETE.md - Troubleshooting v1
11. Coach_AI_Troubleshooting_DAY4_FINAL.md - Troubleshooting v2

### Proposed Organization:

**/docs/user/**
- USER_GUIDE.md (keep)
- Quick_Start_Guide.md (rename from DAY1_DRAFT)
- DEMO_SCRIPT.md (keep)
- NAVIGATION_WALKTHROUGH.md (keep)
- FAQ.md (extract from DAY2_COMPLETE)
- Troubleshooting.md (use DAY4_FINAL, archive DAY4_COMPLETE)

**/docs/developer/**
- ARCHITECTURE.md (rename from THREE_TIER_VISUAL_REFERENCE)
- PROJECT_DESCRIPTION.md (rename from COACH_AI_PROJECT_DESCRIPTION)
- deployment.md (from root)
- implementation_log.md (from root)
- roadmap.md (from WEEK2_ROADMAP)

**/docs/business/**
- EXECUTIVE_PRESENTATION.md (keep)
- business_model.md (extract from PROJECT_DESCRIPTION if needed)

**/docs/**
- INDEX.md (create new - master document index)

---

## 🚀 Action Plan (Recommended Order)

### Phase 1: Safety First (5 min)
```bash
# Create git commit before any changes
git add -A
git commit -m "Backup before directory cleanup"

# Create manual backup
cp -r "Coach AI" "Coach AI BACKUP $(date +%Y%m%d)"
```

### Phase 2: Create New Structure (2 min)
Create these directories:
- archive/notebooks/
- archive/debug/
- archive/temp/
- archive/exports/
- docs/user/
- docs/developer/
- docs/business/
- docs/pdf/
- data/test_data/

### Phase 3: Move Files (10 min)
**Use cleanup script I provided or do manually:**

1. Move notebooks to archive/
2. Move debug files to archive/
3. Move docs to docs/*/
4. Move temp files to archive/
5. Consolidate CSVs in /data/
6. Delete __pycache__/ directories
7. Delete or move unrelated projects

### Phase 4: Documentation (15 min)
1. Organize docs per plan above
2. Create docs/INDEX.md
3. Update README.md if needed
4. Keep PROJECT_HANDOFF.md in root

### Phase 5: Verification (5 min)
```bash
# Test app still works
streamlit run app.py --server.fileWatcherType none

# Check structure looks clean
dir  # (or ls -la on Mac/Linux)
```

### Phase 6: Cleanup (2 min)
- Delete Grow Irish folders
- Delete duplicate CSV files from root
- Empty temp/ directory

---

## ⚠️ Files Requiring Decisions

**Duplicates Found:**
- `drill_library.csv` in root AND /data/ - DELETE root copy
- `practice_history.csv` in root AND /data/ - DELETE root copy
- `team_profiles.csv` in root AND /data/ - DELETE root copy
- `Coach_AI_Troubleshooting_DAY4_COMPLETE.md` vs `DAY4_FINAL.md` - Keep FINAL

**Unrelated Content:**
- `Grow Irish/` - DELETE or move outside Coach AI
- `Grow_Irish_App/` - DELETE or move outside Coach AI

**Review Before Deleting:**
- `cleanup_directory.py` - Delete after using, or keep for future cleanups
- `Indiana Soccer Preview for Practice Plan.pdf` - Archive or delete?

---

## ✅ Success Criteria

After cleanup, root directory should have:
- ≤15 visible files/folders
- Clear purpose for each file
- All docs in /docs/
- All data in /data/
- All old stuff in /archive/

Your brother should be able to:
- Understand project in 30 min by reading README + PROJECT_HANDOFF
- Find any doc quickly via docs/INDEX.md
- Run app in <10 min following README
- Know where to make first contribution

---

## 💡 Next Steps

1. **Review this plan** - Any questions or concerns?
2. **Make backup** - Git commit + folder copy
3. **Run cleanup** - Use script or manual moves
4. **Test app** - Verify still works
5. **Create docs/INDEX.md** - Central navigation
6. **Update README** - Point to cleaned structure
7. **Review with brother** - Get feedback

---

**Want me to generate the cleanup script or any specific files?** Just ask!
