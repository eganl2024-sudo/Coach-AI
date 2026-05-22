# Day 8: Contextual Onboarding System - Architecture

## 🎯 System Overview

### Purpose
Create a reusable hint/tooltip system that provides contextual help throughout the app.

### Design Principles
1. **Progressive Disclosure:** Show hints only when relevant
2. **User Control:** All hints dismissible, never annoying
3. **Persistence:** Remember which hints user has seen
4. **Context-Aware:** Different hints for different experience levels
5. **Lightweight:** Minimal performance impact

---

## 🏗️ Architecture

### Core Module: `src/onboarding.py`

**Components:**
1. Hint rendering functions
2. State management (dismissed hints)
3. Hint catalog (HINTS constant)
4. Helper functions for context detection

### Hint Types

#### 1. Feature Spotlight 🎯
**Purpose:** Highlight new or important features  
**Style:** Blue info box with icon  
**Use:** First-time feature introduction  
**Example:** "Quick Filters let you search drills instantly!"

#### 2. Quick Tip 💡
**Purpose:** Short, actionable advice  
**Style:** Yellow/gold tip box  
**Use:** Contextual suggestions  
**Example:** "Pro tip: Use 'Hide Recent' to ensure variety"

#### 3. Walkthrough Step 📋
**Purpose:** Multi-step guided process  
**Style:** Numbered steps with progress  
**Use:** Complex workflows  
**Example:** "Step 1/3: Create your first team"

#### 4. Success Message 🎉
**Purpose:** Positive reinforcement  
**Style:** Green success box  
**Use:** After completing action  
**Example:** "Great! You've created your first practice"

---

## 📊 State Management

### Session State Structure
```python
{
    "dismissed_hints": {
        "hint_id_1": True,
        "hint_id_2": True,
        ...
    },
    "completed_walkthroughs": {
        "walkthrough_id_1": 3,  # Completed step 3
        ...
    }
}
```

### Hint Lifecycle
1. Check if hint should show (context + dismissed status)
2. Render hint with dismiss button
3. On dismiss: Save to session state
4. Never show again (unless user resets)

---

## 🎨 Hint Catalog Structure

```python
HINTS = {
    "hint_id": {
        "type": "feature_spotlight",  # or quick_tip, walkthrough_step, success
        "title": "Feature Name",
        "message": "Description text",
        "icon": "🎯",
        "level": "advanced",  # essential, advanced, expert, all
        "pages": ["Practice_Generator", "Drill_Library"],  # or ["all"]
        "show_when": "first_visit",  # first_visit, always, conditional
        "condition_fn": optional_function,  # For complex logic
    }
}
```

---

## 🔧 Implementation Plan

### Phase 1: Core Module (60 min)
1. Create `src/onboarding.py`
2. Implement hint rendering functions
3. Add state management
4. Create hint catalog structure

### Phase 2: Hint Catalog (45 min)
5. Define 15+ hints for key features
6. Map hints to pages and contexts
7. Set experience level visibility

### Phase 3: Integration (45 min)
8. Add hints to Coach Home
9. Add hints to Practice Generator
10. Add hints to Drill Library
11. Add hints to Team Hub

### Phase 4: Testing (30 min)
12. Test hint display at each level
13. Test dismiss functionality
14. Verify persistence
15. Check performance

---

## 📝 Hint Inventory (Planned)

### Coach Home
- `home_welcome_essential` - Welcome message for Essential users
- `home_generate_cta` - First practice guidance
- `home_upgrade_advanced` - Advanced features available

### Practice Generator
- `generator_session_types` - Explains session type presets (Essential)
- `generator_categories` - Category selection tips (Advanced)
- `generator_templates` - Template usage (Expert)
- `generator_first_success` - Celebrate first practice

### Drill Library
- `library_filters` - How to use filters (Advanced)
- `library_quick_filters` - Quick filter buttons (Advanced)
- `library_favorites` - Starring favorites (Advanced)

### Team Hub
- `team_create_first` - First team creation (Advanced)
- `team_focus_areas` - Focus area importance (Advanced)
- `team_schedule` - Schedule integration (Expert)

### General
- `upgrade_prompt_advanced` - Benefits of Advanced mode
- `upgrade_prompt_expert` - Benefits of Expert mode

**Total Planned:** 15 hints across 4 pages

---

## 🎯 Success Criteria

### Functional
- ✅ Hints render correctly on all pages
- ✅ Dismiss button works
- ✅ Dismissed hints don't reappear
- ✅ State persists across sessions
- ✅ Context detection works

### User Experience
- ✅ Hints are helpful, not annoying
- ✅ Minimal visual clutter
- ✅ Clear, concise messaging
- ✅ Easy to dismiss
- ✅ No performance impact

### Code Quality
- ✅ Reusable components
- ✅ Clean separation of concerns
- ✅ Well-documented
- ✅ Easy to add new hints
- ✅ Zero breaking changes

---

## 🔄 Future Enhancements

### Phase 2 (Later)
- Hint analytics (track which hints are helpful)
- User-triggered hints (? icon to show dismissed hints)
- Hint scheduling (show after N sessions)
- A/B testing for hint effectiveness
- Animated hints (subtle entrance)
- Hint categories/filtering

---

## 📐 Technical Decisions

### Why Streamlit Native Components?
- Consistent with app styling
- No external dependencies
- Fast rendering
- Easy to customize

### Why Session State?
- Persists during session
- Easy to implement
- No database needed
- User can reset by refreshing

### Why Catalog Approach?
- Centralized management
- Easy to add/remove hints
- Consistent structure
- Self-documenting

---

## 🎨 Visual Design

### Feature Spotlight
```
┌─────────────────────────────────────┐
│ 🎯 Feature Name                     │
│ ────────────────────────────────── │
│ Description of the feature and how │
│ it helps the user accomplish their │
│ goals.                             │
│                                     │
│              [Got it!]  [✕ Dismiss] │
└─────────────────────────────────────┘
```

### Quick Tip
```
┌─────────────────────────────────────┐
│ 💡 Quick Tip                        │
│ ────────────────────────────────── │
│ Short, actionable advice for the   │
│ current context.        [✕ Dismiss] │
└─────────────────────────────────────┘
```

### Walkthrough Step
```
┌─────────────────────────────────────┐
│ 📋 Step 2 of 3: Configure Settings  │
│ ────────────────────────────────── │
│ Follow these steps to complete     │
│ setup.                             │
│                                     │
│ [◀ Back]  [Continue ▶]  [✕ Skip]   │
└─────────────────────────────────────┘
```

### Success Message
```
┌─────────────────────────────────────┐
│ 🎉 Congratulations!                 │
│ ────────────────────────────────── │
│ You've completed your first        │
│ practice!                          │
│                                     │
│                    [Awesome! ✓]    │
└─────────────────────────────────────┘
```

---

## 💡 Key Insights

### Why This Matters
1. **Reduces support burden** - Users self-serve
2. **Improves retention** - Users discover features
3. **Enhances UX** - Contextual help when needed
4. **Scales easily** - Add hints without code changes

### What Makes It Great
- **Reusable** - Works on any page
- **Flexible** - Multiple hint types
- **User-friendly** - Always dismissible
- **Lightweight** - Minimal overhead

---

**Ready to build!** 🚀
