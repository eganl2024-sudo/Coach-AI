# Walkthrough — D1 Soccer Coach Scraper & Coach Finder UI

We have implemented a two-pass coaching staff data scraping pipeline to seed and enrich the NCAA Division I Men's Soccer coach database and integrated a client-side searchable, filterable Coach Finder UI within the Next.js application at `/recruiting`.

---

## Part 1 — Master Program and Coach Scraper (First Pass)

The first-pass scraper ([scrape_coaches.py](file:///C:/Users/ljega/Downloads/Coach%20AI/scraper/scrape_coaches.py)) seeds the master list of 212 programs from Wikipedia, resolves their athletic domains using a local CSV file, and parses coaching staff overview pages.

### Architecture & Logic
1. **Program Seeding**: Seeds 212 D1 programs from Wikipedia, normalizing states to two-letter abbreviations and mapping them to one of five geographic regions (`Northeast`, `Southeast`, `Midwest`, `West`, `Southwest`).
2. **Domain Resolution**: Uses the hardcoded, resolved athletic website domains in [domains.csv](file:///C:/Users/ljega/Downloads/Coach%20AI/scraper/data/domains.csv).
3. **Overview Parsing**: Scrapes athletic websites attempting multiple common subpaths (`/coaches`, `/roster`, etc.) to find the staff overview page.
4. **Unified Coach Extraction**:
   - Parses modern table grids, card layouts, and roster-style coach lists.
   - Maps titles to exactly `Head Coach`, `Assistant Coach`, or `Director of Operations` (skipping others).
   - Extracts Name, Title, Email, Phone, Twitter, and GK/position focus keywords.
   - Deduplicates coach rows (keeping the first occurrence per school + name).

### Part 1 Results
* **Total NCAA D1 Programs Attempted**: 212
* **Domain Resolution Success**: **212 / 212 (100%)**
* **Successfully Scraped Overview Pages**: 192 (90.6%)
* **Failed Scrapes**: 20 (9.4% due to non-standard athletics CMS structures/page layouts, logged to `scraper/output/scrape_errors.log`).
* **Coaches Discovered**: 686 coaches.

---

## Part 2 — Coach Email Enrichment Scraper (Second Pass)

To fill in missing coach emails (representing 55% of the initial overview scrape), the second-pass scraper ([scrape_enrich.py](file:///C:/Users/ljega/Downloads/Coach%20AI/scraper/scrape_enrich.py)) discovers and fetches individual coach bio pages to extract direct email addresses and phone numbers.

### Architecture & Logic
1. **Target Identification**: Identifies target schools where either all coaches have blank email fields OR the Head Coach specifically has a blank email field in `coaches.csv`.
2. **Bio Link Discovery**: Re-fetches the roster/staff overview page and searches for `<a>` tags leading to coach bios:
   - Matches a coach's name (first name and last name) against the link's `href` or text using a robust scoring system.
   - Requires containing the coach's last name plus either the coach's first name or typical bio path patterns (e.g. `/coach/`, `/coaches/`, `/staff/`, `/bio/`, `/profile/`, `/roster/`).
3. **Bio Page Fetching & Extraction**:
   - Fetches the matched bio page URL.
   - **Email**: Extracts `mailto:` links first, falling back to a standard email regex. Demotes and filters out generic emails (e.g. `msoccer@`, `athletics@`, `info@`) in favor of personal/individual emails where available.
   - **Phone**: Extracts `tel:` links first, falling back to a US phone format regex.
   - **Social Media (Constraint)**: In accordance with constraints, all Twitter/X, Instagram, LinkedIn, and Facebook parsing logic has been completely removed to avoid adding noise (e.g. school athletics handles).
4. **Merging & Output**: Updates blank email and phone fields in a new `coaches_enriched.csv` file without overwriting existing data. All other columns, including `twitter_handle`, are carried over unchanged.

### Part 2 Results
* **Enrichment Target Schools (Zero/Missing Head Coach Emails)**: 125 schools
* **Bio Pages Discovered & Fetched**: 435 individual bio pages
* **New Direct Emails Found**: **364 emails**
* **New Direct Phones Found**: **187 phones**
* **Remaining Schools with Zero Emails**: **Only 2 schools** (Liberty University, Long Island University)

### Final Enrichment Output
* **[coaches_enriched.csv](file:///C:/Users/ljega/Downloads/Coach%20AI/scraper/output/coaches_enriched.csv)**: Contains all 686 original coaches with direct email/phone fields filled in.
* **[enrichment_log.txt](file:///C:/Users/ljega/Downloads/Coach%20AI/scraper/output/enrichment_log.txt)**: Contains the summary stats and lists the remaining 2 schools that still lack emails.

---

## Part 3 — Coach Finder UI Sprint (Next.js Application Integration)

We integrated the scraped coaching staff data into the main Next.js player application under `/recruiting`, replacing the static "Coming Soon" page with a fully interactive searchable database.

### Files Created & Modified
*   **[src/lib/types/recruiting.ts](file:///C:/Users/ljega/Downloads/Coach%20AI/player-ai/src/lib/types/recruiting.ts)**: Types representing `CoachRecord` and `ProgramWithCoaches`.
*   **[src/components/ui/dialog.tsx](file:///C:/Users/ljega/Downloads/Coach%20AI/player-ai/src/components/ui/dialog.tsx)**: Named `Dialog` component that handles escape key listeners and overlay close click triggers.
*   **[src/app/(dashboard)/recruiting/page.tsx](file:///C:/Users/ljega/Downloads/Coach%20AI/player-ai/src/app/(dashboard)/recruiting/page.tsx)**: Server component that pulls the coaching data view (`v_coaches_with_program`), aggregates flat rows into structured programs, and returns them as page props.
*   **[src/components/recruiting/RecruitingComingSoon.tsx](file:///C:/Users/ljega/Downloads/Coach%20AI/player-ai/src/components/recruiting/RecruitingComingSoon.tsx)**: React client component containing the Coach Finder UI grid, search input, native selectors for Region and Conference, an Email Available toggle button, and a detail Dialog modal with clipboard email copy functions. Keeps the existing email preview, steps, and CTA cards at the bottom.

### Build Verification Results
We ran the Next.js Turbopack compiler build task to verify that everything compiles cleanly:
```bash
npm run build
```
**Result**: Build succeeded with zero errors or warnings:
```text
✓ Compiled successfully in 14.1s
  Running TypeScript ...
  Finished TypeScript in 10.1s ...
  Collecting page data using 19 workers ...
  Generating static pages using 19 workers (23/23) ...
✓ Generating static pages using 19 workers (23/23) in 1035ms
  Finalizing page optimization ...
Route (app)
├ ƒ /recruiting
├ ƒ /api/draft-email
```
The `/recruiting` page and `/api/draft-email` api route successfully build as dynamic server-rendered routes (`ƒ`).

---

## Part 4 — AI Email Drafter Integration

We successfully implemented the multi-step AI Recruiting Email Drafter directly inside the program details modal, enabling soccer players to securely generate highly personalized emails to coaches based on their profile data and custom interest statements.

### Files Created & Modified
*   **[src/lib/types/player.ts](file:///C:/Users/ljega/Downloads/Coach%20AI/player-ai/src/lib/types/player.ts)**: Extended `AthleteProfile` with optional academic parameters (`gpa`, `gpa_scale`, `act_score`, and `sat_score`).
*   **[src/app/api/draft-email/route.ts](file:///C:/Users/ljega/Downloads/Coach%20AI/player-ai/src/app/api/draft-email/route.ts)**: Secure POST API endpoint that aggregates athlete credentials and custom parameters, executes a structured instruction prompt against Anthropic's Claude API using the `claude-opus-4-5` model, and returns a JSON payload containing `{ subject, body }`. A robust offline **mock fallback** generates high-quality recruiting email drafts locally if `ANTHROPIC_API_KEY` is not present in `.env.local`.
*   **[src/components/recruiting/RecruitingComingSoon.tsx](file:///C:/Users/ljega/Downloads/Coach%20AI/player-ai/src/components/recruiting/RecruitingComingSoon.tsx)**: Fully implemented the drafting states, back-navigation handlers, loader screen, custom academic forms, and a `CopyEmailButton` copy-to-clipboard component.

### API Integration Verification
The API endpoint has been verified using a local script. In the absence of an API key, the mock fallback correctly executes:
```json
{
  "subject": "Goalkeeper Prospect | Liam Jegan | Class of 2027 | University of Notre Dame",
  "body": "Coach Clark,\n\nMy name is Liam Jegan, and I am a Competitive Club Goalkeeper graduating in the Class of 2027..."
}
```
All static pages, scripts, and API routes compile flawlessly without typescript or bundler issues.

---

## Part 5 — Academic Profile Integration

We implemented the client-facing Academic Profile features on the user profile page at `/profile`, exposing academic credentials (`gpa`, `gpa_scale`, `act_score`, and `sat_score`) in the user interface and connecting them to the form actions.

### Files Modified
*   **[src/components/profile/ProfileEditForm.tsx](file:///C:/Users/ljega/Downloads/Coach%20AI/player-ai/src/components/profile/ProfileEditForm.tsx)**:
    - Extended the local edit form state `formData` to capture GPA, scale, ACT, and SAT.
    - Implemented validation rules (GPA `0.0–5.0`, ACT `1–36`, SAT `400–1600`) inside `handleSaveClick`.
    - Added the **Academic Profile Card** to the form layout under the "Development Goals" section.
    - Kept academic fields out of `PLAN_AFFECTING_FIELDS` to avoid triggering the plan-regeneration confirmation dialog.
*   **[src/app/(dashboard)/profile/page.tsx](file:///C:/Users/ljega/Downloads/Coach%20AI/player-ai/src/app/(dashboard)/profile/page.tsx)**:
    - Integrated a read-only **Academic Profile Section** card group directly below the Equipment list, displaying active test scores and GPA with their respective scales.
    - Added conditional render gates so the section remains hidden until at least one academic field is populated.

### Verification Results
1. **Compilation Check**: `npm run build` compiled successfully without any errors or warnings.
2. **Range Verification**: Correctly rejects out-of-bounds inputs (e.g. GPA `5.5`) on save attempt.
3. **Draft Prefill**: Saved academic attributes automatically prefill the AI recruiting email drafter inside the recruiting hub modal on `/recruiting`.

---

## Part 6 — Outreach Tracker Integration

We implemented the Outreach Tracker, enabling players to track every coach they've contacted, log response status, edit records, and delete entries within the `/recruiting` hub.

### Files Created & Modified
*   **[src/lib/types/recruiting.ts](file:///C:/Users/ljega/Downloads/Coach%20AI/player-ai/src/lib/types/recruiting.ts)**: Added `OutreachStatus` union type, `OutreachEntry` interface, and `OutreachLog` interface.
*   **[src/lib/actions/recruiting.ts](file:///C:/Users/ljega/Downloads/Coach%20AI/player-ai/src/lib/actions/recruiting.ts)**: Created Next.js server actions `saveOutreachEntryAction` and `deleteOutreachEntryAction` to safely upsert and remove outreach data entries from Supabase.
*   **[src/app/(dashboard)/recruiting/page.tsx](file:///C:/Users/ljega/Downloads/Coach%20AI/player-ai/src/app/(dashboard)/recruiting/page.tsx)**: Fetches `outreach_log` on load and passes it to `RecruitingComingSoon` component props.
*   **[src/components/recruiting/RecruitingComingSoon.tsx](file:///C:/Users/ljega/Downloads/Coach%20AI/player-ai/src/components/recruiting/RecruitingComingSoon.tsx)**:
    - Added the `Track Outreach` button in the program detail modal footer.
    - Rendered `<OutreachTracker />` directly below the program grid.
*   **[src/components/recruiting/OutreachTracker.tsx](file:///C:/Users/ljega/Downloads/Coach%20AI/player-ai/src/components/recruiting/OutreachTracker.tsx)**:
    - Designed a responsive grid-based form supporting manual entries or pre-filled values.
    - Added summary stats calculations for contacted schools and response counts.
    - Added sorting order (by contacted date descending), visual warning badges for overdue follow-up dates, and quick edit/delete buttons for logged entries.

### Verification Results
1. **Compilation Check**: `npm run build` compiled successfully with zero compilation warnings or typescript errors.
2. **Database Integration**: Saves, updates, and deletes entries securely under `data_key: 'outreach_log'` in the Supabase user data model.
3. **Modal Flow**: Modal click handler closes modal, smooth-scrolls the browser view down, and pre-populates coach details in the tracker form.

