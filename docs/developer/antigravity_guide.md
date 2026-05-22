# Coach AI - Antigravity Cleanup Guide

**Purpose:** Use this guide to prompt Antigravity (Claude) to help organize and improve this project before sharing with your brother.

---

## 🎯 Current Situation

Your Coach AI project is **functionally complete** but the directory structure is messy:
- Documentation scattered across multiple locations  
- Old development files mixed with production code
- Unclear what's important vs. what's archive material
- Hard for someone new (your brother) to understand project structure

**Goal:** Clean, professional project structure that's easy to navigate and collaborate on.

---

## 📋 How to Use Antigravity for Cleanup

### Session 1: Directory Analysis & Planning (30 min)

**Prompt Antigravity:**

```
I need you to analyze my Coach AI project directory structure and create a cleanup plan.

Current directory: C:\Users\ljega\Downloads\Coach AI

Please:
1. List ALL files in the root directory (with brief descriptions)
2. List ALL subdirectories and their key contents
3. Identify which files are:
   - Core production code (keep in root/src/pages)
   - Development/testing artifacts (move to /archive)
   - Documentation (organize in /docs)
   - Data files (keep in /data)
   - Configuration (keep in root)
4. Create a "before/after" directory structure proposal
5. Suggest which files can be safely deleted

Show me the plan before making any changes.
```

---

### Session 2: Documentation Consolidation (30 min)

**Prompt Antigravity:**

```
I have many documentation files in my project knowledge. Help me consolidate:

Files I see in project knowledge:
- USER_GUIDE.md
- DEMO_SCRIPT.md  
- NAVIGATION_WALKTHROUGH.md
- DOCUMENTATION_INDEX.md
- COACH_AI_THREE_TIER_VISUAL_REFERENCE.md
- COACH_AI_EXECUTIVE_PRESENTATION.md
- COACH_AI_PROJECT_DESCRIPTION.md
- Coach_AI_Quick_Start_Guide_DAY1_DRAFT.md
- Coach_AI_Documentation_DAY2_COMPLETE.md
- Coach_AI_Troubleshooting_DAY4_COMPLETE.md
- Coach_AI_Troubleshooting_DAY4_FINAL.md

Please:
1. Categorize these into: User Docs, Developer Docs, Business Docs
2. Identify any duplicates or overlapping content
3. Tell me which are most important to keep
4. Suggest a simple docs/ structure

Then create a single README.md for root that:
- Explains what Coach AI is (2 paragraphs)
- Shows quick start commands (3-4 lines)
- Points to key documentation
- Has a "For New Contributors" section

Write the README.md for me.
```

---

### Session 3: Create Handoff Document (30 min)

**Prompt Antigravity:**

```
I need to hand this project off to my brother. Create PROJECT_HANDOFF.md that includes:

1. What is Coach AI (one paragraph)
2. Quick start (exact commands to run it)
3. Directory structure explanation
4. Key files to understand first (top 5)
5. How the app works (high level architecture)
6. Common tasks:
   - How to add a new drill
   - How to modify a page
   - How to test changes
7. Known issues and workarounds
8. Next steps / priorities

Make it practical and concise - assume my brother is technical but new to this specific project.
```

---

## 🚀 Start Here: Session 1

**Copy-paste this to start your cleanup:**

```
I need help organizing my Coach AI project before my brother reviews it.

It's a soccer practice planning app built with Python/Streamlit. The code works great but the directory feels jumbled.

Location: C:\Users\ljega\Downloads\Coach AI

Please:
1. Analyze the current directory structure
2. Identify what's production code vs development artifacts
3. Suggest how to organize documentation
4. Create a cleanup plan

Use the Filesystem tools to explore the directory. Show me the analysis before making changes.
```

---

## 💡 Quick Wins You Can Prompt For

**Clean README:**
```
Create a clean README.md for the root directory. Include: project description, quick start commands, link to docs, and status badges.
```

**Directory Map:**
```
Create a DIRECTORY_MAP.md that explains what's in each folder and what each key file does. Target audience: new developer.
```

**Code Map:**
```
Analyze /pages/ and /src/ and create CODEBASE_MAP.md explaining the architecture and where to find specific features.
```

**Handoff Checklist:**
```
Create HANDOFF_CHECKLIST.md with tasks for me to complete before sharing with my brother (test these still work, document these decisions, etc.)
```

---

## ✅ Success Criteria

You'll know cleanup worked when:

1. ✅ Brother can understand project in <30 min
2. ✅ Brother can run app in <10 min  
3. ✅ All important docs easy to find
4. ✅ Clear what's old vs current
5. ✅ Know where to start contributing

---

**Start with Session 1 and see what Antigravity finds!**
