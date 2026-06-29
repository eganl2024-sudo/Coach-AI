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

---

## T5 — Parent "delete my child's data" flow (COPPA required)

**What:** Add a "Delete [kid name]'s account and all data" button to parent account settings. Hard-deletes `h2s_kids`, `h2s_progress`, `h2s_daily_missions`, `h2s_streaks` rows for that kid.

**Why:** COPPA requires a data deletion pathway. The signup flow creates kid data before email confirmation is implemented; once COPPA email confirmation ships, the deletion flow completes the required parental control loop. Without it, a parent has no way to remove their child's data.

**Pros:** Legal compliance. Builds parent trust. Required before real cohort.
**Cons:** Irreversible — needs a confirmation dialog to prevent accidents.

**Context:** Detected during 2026-06-29 /plan-eng-review. The design doc (ljega-main-design-20260628-145953.md) section "Account & COPPA Flow" calls for "Delete my child's account and all data" in parent account settings. Not implemented or tracked until now. The settings page at `/settings` is the right location. Add a red "Delete player account" button at the bottom of the "Your Players" section, behind a confirmation modal.

**Depends on / blocked by:** COPPA email confirmation (ARCH-3) should ship first, but this can be built in parallel.

---

## T6 — Auto-detect + remember browser timezone at signup (regression guard)

**What:** In the signup form, capture `Intl.DateTimeFormat().resolvedOptions().timeZone` as a hidden field. Pass to `addKidAction`. Use as the initial `timezone` for the kid's streak record.

**Why:** Onboarding doesn't capture timezone — all kids default to `America/New_York`. A kid in California practicing at 9pm PST has their streak credited to "tomorrow" from ET perspective, breaking the streak on the next real practice day.

**Pros:** Correct streak behavior for non-ET users from day 1. One-line browser-side addition.
**Cons:** Browser timezone can be spoofed or wrong (VPN, misconfigured device). Settings page TimezoneSelector already exists as the manual override.

**Context:** Detected during 2026-06-29 /plan-eng-review outside voice. `updateStreak` in `streaks.ts` uses `getLocalDate(timezone)` correctly with the stored timezone — the bug is only in the initial default. This TODO exists as a regression guard: even after T4 (auto-detect at onboarding) ships, keep this note so future refactors to the onboarding flow don't accidentally strip the hidden timezone field.

**Depends on / blocked by:** None — can ship with or before Phase 1.
