# TODOS

Captured during /plan-eng-review on 2026-06-28. Each item has a why and context so future-you understands the motivation.

---

## T1 — Timezone update flow in parent settings

**What:** Add a "My timezone" field to the parent settings/profile page that saves to `h2s_parents.timezone` and re-evaluates the kid's streak on next load.

**Why:** Timezone is captured once at signup (auto-detected from browser). DST shifts and travel silently break streaks — a kid who visits grandparents in a different timezone loses their streak with no recourse or explanation.

**Pros:** Prevents invisible streak loss, builds parent trust.
**Cons:** Requires a settings page (doesn't exist yet), adds timezone reconciliation logic to streak evaluation.

**Context:** `h2s_streaks.timezone` is set at kid creation, sourced from `h2s_parents.timezone`. The streak evaluation compares `last_completed_date` to "today" in that timezone. If the timezone is wrong, the comparison produces wrong results silently. A kid who maintains a 14-day streak and then loses it to a timezone bug will churn.

**Depends on / blocked by:** Phase 1 must ship first (streak system needs to exist). Settings page needs to be built.

---

## T2 — Phase 2 COPPA video data consent

**What:** Before Phase 2 ships: update the COPPA confirmation email to explicitly mention video storage, add video deletion to the "delete my child's data" flow, and document the CSAM risk posture.

**Why:** Video data of children is a separate COPPA category from text/progress data. The Phase 1.5 email confirmation covers profile/progress data. Phase 2 introduces video clips of children — which requires explicit separate consent, a documented retention policy, and a CSAM assessment.

**Pros:** Legal compliance, avoids shutdown risk if app grows.
**Cons:** Additional legal/compliance work before Phase 2 can launch to real users.

**Context:** Phase 2 design stores videos in `h2s-videos/{kid_id}/{submission_id}.mp4` in Supabase Storage. Parent approval is required before the star unlocks, but COPPA requires consent for the storage itself, not just the approval workflow. The "delete my child's data" flow in parent settings must also delete all Supabase Storage objects.

**Depends on / blocked by:** Phase 1.5 COPPA email flow must exist first. Phase 2 implementation in progress.

---

## T3 — Add INDEX(kid_id, date) on h2s_daily_missions at 50+ users

**What:** Add a composite index on `(kid_id, date)` on the `h2s_daily_missions` table.

**Why:** Every home page load queries this table for the kid's today's missions. At 10 kids the full table scan is < 1ms. At 50+ users the unindexed query becomes noticeable on the hot path.

**Pros:** Keeps home page fast as app grows.
**Cons:** Trivial — Supabase migration, one line.

**Context:** The `kid_id` FK already gets a Supabase auto-index. Adding `date` as a second predicate turns it into a composite that eliminates the per-kid date scan. Run this before any growth campaign or when observing slow home page loads.

**Depends on / blocked by:** Phase 1 must ship first. Not needed until 50+ active users.

---

## T4 — Create DESIGN.md for component vocabulary

**What:** Write a DESIGN.md file in `how2soccer/` documenting the design system: color palette (green-500/700 gradient, gray-100 card border, white surface), component patterns (hero block, MissionCard, stat chips, bottom nav), typography scale (`font-black` for all headings, `text-sm` minimum for body), and touch target rule (44px minimum).

**Why:** Every new screen currently requires reverse-engineering tokens from existing code. The MissionCard and extended hero block added in Phase 1 are new patterns — without documentation they'll drift as the app grows.

**Pros:** New screens stay visually consistent; onboarding a second developer takes minutes not hours.
**Cons:** Takes 1-2 hours to write properly. Goes stale if not updated alongside new components.

**Context:** No DESIGN.md currently exists. Phase 1 adds `MissionCard`, an extended hero block (rounded-bottom-only, 3 stat chips), and a new progress bar sub-component. The `/plan-design-review` had to document tokens inline in the design doc as a workaround — DESIGN.md is the right permanent home.

**Depends on / blocked by:** Phase 1 must ship first (so real component code exists to document).
