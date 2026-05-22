# Week 2 Roadmap: Progressive Disclosure Enhancement
## Expanding the Experience Level System

**Goal:** Extend progressive disclosure to remaining pages and add onboarding features
**Timeline:** 5-7 days
**Estimated Total Time:** 18-24 hours

---

## 📋 Week 2 Overview

Building on Week 1's foundation, we'll:
1. Extend conditional rendering to more pages (Days 6-7)
2. Add contextual onboarding system (Day 8)
3. Create interactive getting started checklist (Day 9)
4. Build in-app help and tooltips (Day 10)
5. Add user analytics and usage tracking (Days 11-12)

---

## Day 6: Simplified Drill Library (Essential Mode)
**Estimated Time:** 2.5-3 hours
**Status:** 🔄 Ready to Start

### Goal
Transform Drill Library page to show simplified view for Essential users while maintaining full functionality for Advanced/Expert users.

### Current State Analysis
- Drill Library is Advanced-tier page (only visible to Advanced/Expert)
- Currently shows: full drill list, filters, search, categories
- Essential users: don't see this page at all
- Decision: Keep it Advanced-tier but add welcome/orientation for new Advanced users

### What We'll Build

**Essential Users (N/A - page not visible):**
- No changes needed - page correctly hidden

**Advanced Users (First-time orientation):**
- Welcome banner: "You unlocked the Drill Library! 🎉"
- Quick tour of key features (3-4 highlight boxes)
- "Getting Started" tips (expandable)
- Simple filter presets (Beginner Friendly, Quick Setup, Popular)

**Expert Users (Full Access):**
- All current functionality unchanged
- Optional: hide welcome banner after first visit
- Add "Drill Library Pro Tips" expander

### Implementation Steps

1. **Add first-visit detection** (10 min)
   - Add `drill_library_visited` to session state
   - Track visit in `src/session_state.py`

2. **Create welcome banner component** (30 min)
   - Import experience_level module
   - Add conditional welcome for Advanced users
   - Include feature highlights
   - Add dismiss/continue button

3. **Add filter presets for Advanced users** (45 min)
   - Create `DRILL_FILTER_PRESETS` constant
   - Map to existing filter combinations
   - Add radio buttons for quick selection
   - "Show All Filters" expander for customization

4. **Add Pro Tips expander for Expert users** (30 min)
   - Advanced filtering techniques
   - Bulk operations
   - Custom drill creation tips
   - Link to Template Studio

5. **Testing** (45 min)
   - Test as Advanced user (first visit)
   - Test as Advanced user (return visit)
   - Test as Expert user
   - Verify filters work correctly
   - Test preset filter combinations

### Files to Modify
- `pages/1_Drill_Library.py` (~100 lines added)
- `src/session_state.py` (add drill_library_visited tracking)

### Success Criteria
- ✅ Welcome banner shows for Advanced users on first visit
- ✅ Filter presets work correctly
- ✅ Pro tips expander shows for Expert users
- ✅ No breaking changes to existing functionality
- ✅ Manual browser testing passes

### Commit Message
```bash
git add pages/1_Drill_Library.py src/session_state.py
git commit -m "Day 6: Add onboarding and presets to Drill Library

- Add welcome banner for new Advanced users
- Implement filter presets for quick drill selection
- Add Pro Tips expander for Expert users
- Track first-visit state in session
- Zero breaking changes to existing features"
```

---

## Day 7: Simplified Team Hub (Essential Mode)
**Estimated Time:** 2.5-3 hours
**Status:** ⏳ Pending Day 6

### Goal
Add team management orientation and simplified interface for new Advanced users.

### Current State Analysis
- Team Hub is Advanced-tier page
- Currently shows: team list, player management, profile editor
- Complex for new users who just unlocked it
- Decision: Add progressive disclosure within the page

### What We'll Build

**Advanced Users (Simplified View):**
- Welcome banner: "Meet Your Team Hub! 👥"
- Quick setup wizard (3 steps)
  - Step 1: Create your first team
  - Step 2: Add basic info (age group, size)
  - Step 3: Optional player roster
- Simplified team card view
- "Show Advanced Options" expander

**Expert Users (Full View):**
- All current functionality
- Advanced team analytics
- Player tracking features
- Integration with practice history

### Implementation Steps

1. **Add Team Hub tracking** (10 min)
   - Add `team_hub_setup_complete` to session state
   - Track whether user has created first team

2. **Create setup wizard component** (60 min)
   - Step-by-step team creation
   - Progress indicator (1/3, 2/3, 3/3)
   - Skip option for experienced users
   - Auto-advance on completion

3. **Add simplified team view for Advanced** (45 min)
   - Card-based team display
   - Essential info only: name, age group, size
   - Quick action buttons: Edit, View Practice History
   - "Advanced Options" expander

4. **Preserve Expert functionality** (30 min)
   - All advanced features in main view
   - Player tracking
   - Team analytics
   - Historical data

5. **Testing** (45 min)
   - Test setup wizard flow
   - Test as Advanced user (simplified view)
   - Test as Expert user (full view)
   - Verify team creation works
   - Test navigation between teams

### Files to Modify
- `pages/5_Team_Hub.py` (~150 lines added)
- `src/session_state.py` (add team hub tracking)
- `src/team_profile.py` (possible helper functions)

### Success Criteria
- ✅ Setup wizard works for new Advanced users
- ✅ Simplified view shows for Advanced users
- ✅ Full view shows for Expert users
- ✅ Team creation works in both modes
- ✅ Zero breaking changes

### Commit Message
```bash
git add pages/5_Team_Hub.py src/session_state.py
git commit -m "Day 7: Add Team Hub onboarding and progressive disclosure

- Add 3-step setup wizard for new Advanced users
- Implement simplified team card view
- Preserve full functionality for Expert users
- Track team hub setup completion
- Improve first-time user experience"
```

---

## Day 8: Contextual Onboarding System
**Estimated Time:** 3-4 hours
**Status:** ⏳ Pending Days 6-7

### Goal
Build a reusable onboarding hint system that provides contextual help throughout the app.

### What We'll Build

**Core Onboarding Module** (`src/onboarding.py`):
- Hint/tooltip component library
- Context-aware help bubbles
- Dismissible tutorials
- Progress tracking

**Hint Types:**
1. **Feature Spotlights** - Highlight new features
2. **Quick Tips** - Contextual suggestions
3. **Walkthroughs** - Multi-step guides
4. **Success Messages** - Positive reinforcement

### Implementation Steps

1. **Create onboarding module** (90 min)
   - `src/onboarding.py` (new file ~300 lines)
   - Hint rendering functions
   - State management for dismissed hints
   - Progress tracking utilities

2. **Add hint components** (60 min)
   - `render_feature_spotlight()`
   - `render_quick_tip()`
   - `render_walkthrough_step()`
   - `render_success_message()`

3. **Define hint catalog** (45 min)
   - Create `HINTS` constant with all hints
   - Map hints to pages and contexts
   - Define trigger conditions
   - Set experience level visibility

4. **Integrate into key pages** (45 min)
   - Coach Home: "First practice" hint
   - Practice Generator: "Session types" hint
   - Drill Library: "Filter" hint
   - Team Hub: "Team setup" hint

5. **Testing** (30 min)
   - Test hint display at each level
   - Test dismiss functionality
   - Verify hints don't show after dismiss
   - Test hint persistence across sessions

### Files to Create/Modify
- `src/onboarding.py` (NEW - ~300 lines)
- `src/session_state.py` (add hint tracking)
- `pages/0_Coach_Home.py` (add hints)
- `pages/2_Practice_Generator.py` (add hints)
- `pages/1_Drill_Library.py` (add hints)
- `pages/5_Team_Hub.py` (add hints)

### Success Criteria
- ✅ Onboarding module fully functional
- ✅ Hints render correctly on all pages
- ✅ Dismiss functionality works
- ✅ Hints persist appropriately
- ✅ No performance impact

### Commit Message
```bash
git add src/onboarding.py src/session_state.py pages/*.py
git commit -m "Day 8: Add contextual onboarding hint system

- Create reusable onboarding module
- Implement 4 hint component types
- Add hint catalog with 15+ contextual hints
- Integrate hints into key pages
- Track hint dismissal state
- Improve first-time user experience"
```

---

## Day 9: Getting Started Checklist
**Estimated Time:** 2.5-3 hours
**Status:** ⏳ Pending Day 8

### Goal
Create an interactive checklist that guides new users through their first practice planning session.

### What We'll Build

**Getting Started Checklist Component:**
- Checklist widget in sidebar or expandable section
- 5-7 key milestones for new users
- Progress bar and completion percentage
- Celebration on completion
- Option to hide after completion

**Checklist Items (Essential Users):**
1. ✅ Welcome to Coach AI
2. ⬜ Generate your first practice
3. ⬜ Review the generated drills
4. ⬜ View your practice history
5. ⬜ Reuse a previous practice
6. ⬜ Explore Advanced mode features
7. 🎉 You're all set up!

**Checklist Items (Advanced Users):**
1. ✅ Create a team profile
2. ⬜ Customize drill categories
3. ⬜ Add a custom drill
4. ⬜ Generate with specific focus
5. ⬜ Save practice as favorite
6. ⬜ Explore Expert mode
7. 🎉 Team hub mastered!

### Implementation Steps

1. **Create checklist module** (60 min)
   - `src/checklist.py` (new file ~250 lines)
   - Checklist rendering component
   - Progress calculation
   - Item completion tracking
   - Celebration trigger

2. **Define checklists by level** (30 min)
   - Essential checklist (7 items)
   - Advanced checklist (7 items)
   - Expert checklist (optional - advanced features)
   - Map items to completion conditions

3. **Add completion detection** (60 min)
   - Hook into existing session state
   - Detect when actions complete items
   - Auto-check items on completion
   - Persist checklist state

4. **Integrate into UI** (30 min)
   - Add to sidebar with render_checklist()
   - Add celebration modal on completion
   - "Hide checklist" option
   - "Reset checklist" option (for testing)

5. **Testing** (30 min)
   - Test Essential checklist flow
   - Test Advanced checklist flow
   - Verify auto-completion works
   - Test persistence across sessions
   - Test hide/reset functionality

### Files to Create/Modify
- `src/checklist.py` (NEW - ~250 lines)
- `src/session_state.py` (add checklist state)
- `src/ui_components.py` (add render_checklist())
- Multiple pages (add completion hooks)

### Success Criteria
- ✅ Checklist renders in sidebar
- ✅ Items auto-complete on action
- ✅ Progress bar updates correctly
- ✅ Celebration shows on completion
- ✅ State persists across sessions

### Commit Message
```bash
git add src/checklist.py src/session_state.py src/ui_components.py pages/*.py
git commit -m "Day 9: Add interactive Getting Started checklist

- Create checklist module with progress tracking
- Define checklist for each experience level
- Implement auto-completion detection
- Add celebration on checklist completion
- Integrate into sidebar UI
- Guide new users through first session"
```

---

## Day 10: In-App Help System
**Estimated Time:** 3-4 hours
**Status:** ⏳ Pending Days 8-9

### Goal
Build a comprehensive help system with contextual documentation and quick reference guides.

### What We'll Build

**Help Module Components:**
1. **Help Button** - "?" icon in top nav
2. **Help Panel** - Slide-out help sidebar
3. **Quick Reference** - Page-specific guides
4. **Keyboard Shortcuts** - Hotkey reference
5. **FAQ Section** - Common questions
6. **Video Tutorials** - Links to demos

**Help Panel Structure:**
- Search box for help topics
- Categorized help articles
- Page-specific context help
- Links to external resources
- Feedback/contact option

### Implementation Steps

1. **Create help module** (90 min)
   - `src/help_system.py` (new file ~400 lines)
   - Help panel rendering
   - Article catalog structure
   - Search functionality
   - Context detection

2. **Write help articles** (90 min)
   - Practice Generator guide
   - Drill Library guide
   - Team Hub guide
   - Experience levels explained
   - Keyboard shortcuts
   - FAQ (10-15 common questions)

3. **Add help button to nav** (30 min)
   - Update `src/ui_components.py`
   - Add "?" button to top nav
   - Toggle help panel on click
   - Position help panel (sidebar)

4. **Implement contextual help** (45 min)
   - Detect current page
   - Show relevant help first
   - Add "Help on this page" section
   - Quick tips for current context

5. **Testing** (30 min)
   - Test help panel on all pages
   - Verify search works
   - Test contextual help detection
   - Check article formatting
   - Verify external links

### Files to Create/Modify
- `src/help_system.py` (NEW - ~400 lines)
- `src/ui_components.py` (add help button)
- `docs/help_articles.md` (NEW - documentation)
- All major pages (add help context)

### Success Criteria
- ✅ Help button visible in nav
- ✅ Help panel opens/closes smoothly
- ✅ Search finds relevant articles
- ✅ Contextual help works on each page
- ✅ All articles formatted correctly

### Commit Message
```bash
git add src/help_system.py src/ui_components.py docs/help_articles.md pages/*.py
git commit -m "Day 10: Add comprehensive in-app help system

- Create help module with search functionality
- Write 15+ help articles and guides
- Add help button to navigation
- Implement contextual page-specific help
- Include FAQ and keyboard shortcuts
- Improve user self-service support"
```

---

## Days 11-12: User Analytics & Usage Tracking
**Estimated Time:** 4-6 hours (split over 2 days)
**Status:** ⏳ Pending Days 6-10

### Goal
Implement privacy-respecting analytics to understand user behavior and improve the experience.

### What We'll Build

**Analytics System:**
- Event tracking (page views, actions, errors)
- Usage patterns analysis
- Feature adoption metrics
- Session duration tracking
- Experience level transitions
- A/B test framework (future)

**Privacy-First Approach:**
- No PII collection
- Local storage only (no external services)
- Anonymized user IDs
- Clear opt-out mechanism
- Data export functionality

### Day 11: Core Analytics Module (3 hours)

#### Implementation Steps

1. **Create analytics module** (90 min)
   - `src/analytics.py` (new file ~350 lines)
   - Event logging functions
   - Session tracking
   - Data storage (CSV/JSON)
   - Privacy controls

2. **Define event catalog** (30 min)
   - Page view events
   - User action events
   - Feature usage events
   - Error events
   - Level change events

3. **Add tracking hooks** (60 min)
   - Practice generation tracking
   - Drill interaction tracking
   - Level switch tracking
   - Feature usage tracking
   - Error tracking

4. **Testing** (30 min)
   - Verify events log correctly
   - Check data storage
   - Test privacy controls
   - Verify no PII collected

#### Files to Create/Modify
- `src/analytics.py` (NEW - ~350 lines)
- `src/session_state.py` (add analytics state)
- Major pages (add tracking calls)

#### Success Criteria
- ✅ Analytics module fully functional
- ✅ Events log correctly
- ✅ Data stored properly
- ✅ Privacy controls work
- ✅ No PII collected

---

### Day 12: Analytics Dashboard (2-3 hours)

#### Implementation Steps

1. **Create analytics dashboard** (90 min)
   - `pages/14_Analytics.py` (new page ~300 lines)
   - Expert-tier only page
   - Usage overview charts
   - Feature adoption metrics
   - Level transition analysis

2. **Add visualization components** (45 min)
   - Page view charts (line/bar)
   - Feature usage heatmap
   - Level distribution pie chart
   - Session duration histogram
   - Top features list

3. **Add export functionality** (30 min)
   - Export to CSV button
   - Date range filtering
   - Anonymized data export
   - Clear data option

4. **Testing** (30 min)
   - Test dashboard rendering
   - Verify charts display correctly
   - Test export functionality
   - Check data aggregation

#### Files to Create/Modify
- `pages/14_Analytics.py` (NEW - ~300 lines)
- `src/ui_components.py` (add to nav for Expert)
- `src/analytics.py` (add dashboard queries)

#### Success Criteria
- ✅ Dashboard accessible to Expert users
- ✅ Charts render correctly
- ✅ Export works properly
- ✅ Insights are actionable
- ✅ Privacy maintained

#### Combined Commit Message (Days 11-12)
```bash
git add src/analytics.py pages/14_Analytics.py src/session_state.py pages/*.py
git commit -m "Days 11-12: Add privacy-first analytics system

- Create analytics module with event tracking
- Implement privacy-respecting data collection
- Track page views, actions, and feature usage
- Add analytics dashboard for Expert users
- Include usage charts and feature adoption metrics
- Add data export and clear functionality
- Zero PII collection, local storage only"
```

---

## Week 2 Summary Dashboard

### Time Investment Breakdown
- Day 6: 2.5-3 hours (Drill Library)
- Day 7: 2.5-3 hours (Team Hub)
- Day 8: 3-4 hours (Onboarding)
- Day 9: 2.5-3 hours (Checklist)
- Day 10: 3-4 hours (Help System)
- Day 11: 3 hours (Analytics Core)
- Day 12: 2-3 hours (Analytics Dashboard)
- **Total: 19-23 hours**

### Files to Create (New)
1. `src/onboarding.py` (~300 lines)
2. `src/checklist.py` (~250 lines)
3. `src/help_system.py` (~400 lines)
4. `src/analytics.py` (~350 lines)
5. `pages/14_Analytics.py` (~300 lines)
6. `docs/help_articles.md` (documentation)
7. Test files for each module

### Files to Modify (Existing)
1. `pages/1_Drill_Library.py`
2. `pages/5_Team_Hub.py`
3. `src/ui_components.py`
4. `src/session_state.py`
5. Multiple pages (tracking hooks)

### Expected Code Output
- **New Code:** ~2,200 lines
- **Modified Code:** ~400 lines
- **Tests:** 30+ new tests
- **Documentation:** 20+ help articles
- **Total:** ~2,600 lines

### Portfolio Metrics (Week 2 Projected)

**Code Statistics:**
- Lines written: ~2,200
- Lines modified: ~400
- Tests created: 30+
- Files created: 7+
- Files modified: 10+
- Breaking changes: 0

**Feature Statistics:**
- Pages with conditional rendering: 5 (+2 from Week 1)
- Onboarding hints: 15+
- Help articles: 20+
- Analytics events: 25+
- Checklist items: 14 (7 per level)

### Key Achievements (Projected)

1. **Complete Progressive Disclosure**
   - All Advanced-tier pages enhanced
   - Contextual onboarding throughout
   - Self-service help system

2. **User Guidance**
   - Interactive checklist
   - 15+ contextual hints
   - 20+ help articles
   - Keyboard shortcuts

3. **Data-Driven Improvements**
   - Privacy-first analytics
   - Feature adoption tracking
   - User behavior insights
   - Usage patterns analysis

### Success Metrics

**User Experience:**
- Reduced time to first practice (< 2 min)
- Higher completion rates for new users
- Fewer support questions
- Improved feature discovery

**Technical:**
- Zero breaking changes
- < 100ms impact on load time
- 100% test coverage for new modules
- No PII collection

---

## Testing Strategy

### Daily Testing Checklist
Each day should include:
- ✅ Automated tests for new functions
- ✅ Manual browser testing (all levels)
- ✅ Regression testing (existing features)
- ✅ Cross-page navigation testing
- ✅ State persistence testing

### End-of-Week Integration Testing
- Full user flow as Essential user
- Full user flow as Advanced user
- Full user flow as Expert user
- Level transition testing
- Performance testing
- Analytics data validation

---

## Risk Mitigation

### Potential Issues
1. **State Management Complexity:** Multiple new state variables
   - Mitigation: Centralize in session_state.py, document thoroughly

2. **Performance Impact:** More UI elements to render
   - Mitigation: Lazy loading, conditional rendering, profiling

3. **User Confusion:** Too many hints/help elements
   - Mitigation: Dismissible UI, progressive disclosure of help

4. **Analytics Privacy:** Accidental PII collection
   - Mitigation: Code review, explicit PII checks, user transparency

### Rollback Plan
- Each day's work is independently committable
- Can deploy Days 6-10 without Days 11-12 if needed
- Feature flags for new modules (optional)

---

## Next Steps After Week 2

### Week 3 Possibilities
1. A/B testing framework
2. User preference profiles
3. Advanced keyboard navigation
4. Export/import functionality
5. Mobile optimization
6. Collaborative features
7. Integration testing suite
8. Performance optimization

---

**Ready to Start Day 6? Let's go! 🚀**
