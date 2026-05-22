# DAY 4: TROUBLESHOOTING GUIDE - CRITICAL ISSUES

**Phase 1 Pre-Launch Documentation - Day 4**  
**Date:** January 30, 2026  
**Time Allocation:** 6 hours  
**Completion Target:** 6 critical issues with solutions

---

## 📋 DAY 4 OVERVIEW

**Morning Session (3 hours):** Document issues 1-3 with solutions  
**Afternoon Session (3 hours):** Document issues 4-6, format, and deploy

**End of Day Deliverables:**
- ✅ 6 critical blocking issues solved
- ✅ Step-by-step solutions for each
- ✅ Decision tree flowcharts
- ✅ Web version (searchable, expandable)
- ✅ Printable PDF version
- ✅ Support escalation paths

---

# PART 1: IDENTIFY CRITICAL ISSUES (30 MINUTES)

## What Makes an Issue "Critical"?

**Critical issues are blocking issues** - they prevent users from accomplishing core tasks.

**Criteria:**
- ✅ Stops user from using app entirely
- ✅ Prevents core workflow (generate practice)
- ✅ Affects majority of users (not edge case)
- ✅ Has clear, testable solution
- ✅ Can be resolved in <10 minutes

**NOT critical:**
- ❌ Minor annoyances (cosmetic issues)
- ❌ Feature requests ("I wish it did X")
- ❌ Edge cases (affects <1% of users)
- ❌ Requires engineering fix (backend issues)

---

## The 6 Critical Issues

Based on common beta testing patterns and app functionality:

```
CRITICAL BLOCKING ISSUES (6 Total)
═══════════════════════════════════════════════════════════════

AUTHENTICATION ISSUES:
1. Can't Log In / Forgot Password

CORE WORKFLOW ISSUES:
2. Practice Won't Generate
3. PDF Export Blank or Not Working

FEATURE ACCESS ISSUES:
4. Drills Don't Match My Team
5. Settings Won't Save

ADVANCED FEATURE ISSUES:
6. Can't Star Drills / Features Not Responding

═══════════════════════════════════════════════════════════════
```

---

# PART 2: DOCUMENT SOLUTIONS 1-3 (HOURS 1-2)

## Issue Format Template

Each issue follows this structure:

```
═══════════════════════════════════════════════════════════════
ISSUE #X: [Problem Title]
═══════════════════════════════════════════════════════════════

🔴 PROBLEM:
Brief description of what's happening

📊 SYMPTOMS:
• Bullet list of what user experiences
• Specific error messages
• What they tried that didn't work

⚙️ COMMON CAUSES:
• List of why this happens
• Technical explanation (simple language)

✅ SOLUTION:
Step-by-step numbered instructions
Clear, actionable, tested

⏱️ TIME TO FIX: X minutes

🆘 STILL STUCK?
Escalation path to support

🔗 RELATED:
Links to FAQ, Quick Start, etc.

═══════════════════════════════════════════════════════════════
```

---

## ISSUE #1: Can't Log In / Forgot Password

### 🔴 PROBLEM:

You're trying to log in to Coach AI but cannot access your account. You see error messages like "Invalid email or password" or "Account not found."

### 📊 SYMPTOMS:

**What you're experiencing:**
- ❌ "Invalid email or password" error message
- ❌ "No account found with this email" message
- ❌ You're stuck on the login page
- ❌ Password reset email not arriving
- ❌ Email verification link not working

**What you tried:**
- Entered your email and password multiple times
- Tried different password variations
- Checked email for verification link
- Waited for password reset email (didn't arrive)

### ⚙️ COMMON CAUSES:

**Why this happens:**
1. **Wrong email address** - Using different email than you signed up with
2. **Typo in password** - Caps lock on, extra spaces, autocorrect changes
3. **Account not verified** - You haven't clicked email verification link
4. **Password reset email in spam** - Email filters caught it
5. **Browser autofill error** - Saved wrong credentials

### ✅ SOLUTION:

**STEP 1: Verify Your Email Address**

1. Check which email you used to sign up
2. Common mistakes:
   - Work email vs. personal email
   - Gmail vs. Yahoo vs. Outlook
   - Typos in email address (john.smith@ vs. johnsmith@)
3. Try all email addresses you commonly use

**STEP 2: Check Caps Lock and Keyboard**

1. Make sure **Caps Lock is OFF**
2. Delete any spaces before/after email or password
3. Type password carefully (don't copy/paste yet)
4. Watch for autocorrect changing your password

**STEP 3: Reset Your Password**

1. Click **"Forgot Password?"** link on login page
2. Enter your email address (the one you signed up with)
3. Click **"Send Reset Link"**
4. **Check your email** - look for "Coach AI Password Reset"
5. **Check SPAM folder** if not in inbox (within 2 minutes)
6. Click the reset link in email (expires in 1 hour)
7. Create a **new password** (8+ characters, write it down!)
8. Try logging in with new password

**STEP 4: Verify Your Account (New Users)**

If you just signed up:
1. Check email for "Verify Your Coach AI Account" message
2. **Check SPAM folder** if not in inbox
3. Click verification link
4. You'll be redirected to login page
5. Log in with your email and password

**STEP 5: Clear Browser Data (If Still Stuck)**

1. **Chrome:** Settings → Privacy → Clear browsing data → Cached images and files
2. **Firefox:** Settings → Privacy → Clear Data → Cookies and Cache
3. **Safari:** Preferences → Privacy → Manage Website Data → Remove All
4. Close browser completely
5. Reopen and try logging in again

**STEP 6: Try Different Browser**

1. If using Chrome, try Firefox or Edge
2. Use incognito/private mode to test
3. This rules out browser-specific issues

### 🔄 DECISION TREE:

```
Can't log in?
    │
    ├─ Getting "Invalid password" error?
    │   └─► Reset password (Step 3)
    │
    ├─ Getting "No account found" error?
    │   └─► Check email address (Step 1)
    │       └─► Try all email addresses you use
    │
    ├─ Just signed up today?
    │   └─► Check for verification email (Step 4)
    │       └─► Check SPAM folder
    │
    ├─ Password reset email not arriving?
    │   └─► Check SPAM folder
    │       └─► Wait 5 minutes, try again
    │       └─► Still nothing? → Contact support
    │
    └─ Everything fails?
        └─► Clear browser data (Step 5)
            └─► Try different browser (Step 6)
            └─► Still stuck? → Contact support
```

### ⏱️ TIME TO FIX: 

**2-5 minutes** (password reset)  
**10 minutes** (if trying all troubleshooting steps)

### 🆘 STILL STUCK?

**Contact Support Immediately:**
- 📧 Email: **support@coachAI.app**
- 📧 Subject: "URGENT: Cannot Log In - [Your Email]"
- Include:
  - Email address you're trying to use
  - Which error message you see (screenshot if possible)
  - What you already tried
  - Browser you're using

**Response time:** Under 4 hours for login issues (highest priority)

**Temporary workaround:** Create a new account with different email, then we'll merge your data.

### 🔗 RELATED:

- **FAQ:** Q17 - Is there a free trial?
- **FAQ:** Q19 - How do I get help if I'm stuck?
- **Quick Start Guide:** Step 1 - Create Your Account

---

## ISSUE #2: Practice Won't Generate

### 🔴 PROBLEM:

You click "Generate Practice" but nothing happens, you get an error, or the practice loads incomplete/incorrectly.

### 📊 SYMPTOMS:

**What you're experiencing:**
- ❌ Click "Generate Practice" → nothing happens
- ❌ Infinite loading spinner (spinning for 30+ seconds)
- ❌ Error message: "Failed to generate practice"
- ❌ Practice appears but has 0 drills
- ❌ Practice appears but missing key sections (no warmup, no cool down)
- ❌ Same practice generates every time (no variety)

**What you tried:**
- Clicked "Generate Practice" multiple times
- Refreshed the page
- Tried different session types
- Waited several minutes

### ⚙️ COMMON CAUSES:

**Why this happens:**
1. **No team created yet** - Can't generate without team profile
2. **Internet connection lost** - AI runs in cloud, needs connection
3. **Browser timeout** - Old browser or slow connection
4. **Invalid settings** - Conflicting options selected
5. **Server temporarily down** - Rare but possible
6. **Drill library empty** - Advanced mode with no drills available

### ✅ SOLUTION:

**STEP 1: Verify You Have a Team**

1. Look at sidebar - do you see a team name?
2. If **NO team**:
   - Click **"Create Team"** button
   - Fill in 4 basic fields (name, age, skill, roster)
   - Save team
   - Try generating practice again

**STEP 2: Check Your Internet Connection**

1. Look for WiFi/internet icon in your browser
2. Try loading another website (google.com)
3. **If internet is down:**
   - Reconnect to WiFi
   - Check if other devices have internet
   - Restart your router if needed
4. **If using cellular/mobile hotspot:**
   - May be too slow for practice generation
   - Switch to WiFi if possible

**STEP 3: Verify Practice Settings**

Settings that might cause issues:
1. **Duration:** Must be 60, 75, 90, or 120 minutes (not custom)
2. **Player count:** Must be realistic (4-30 players)
3. **Session type:** Must select one (Balanced, Technical, Game Prep, or Fitness)

**Fix:**
- Reset to defaults: Duration 90, Type Balanced
- Try generating with these settings
- Once it works, adjust settings one at a time

**STEP 4: Refresh Your Browser**

1. **Soft refresh:**
   - Press **F5** (Windows) or **Cmd+R** (Mac)
   - Try generating again

2. **Hard refresh** (if soft refresh fails):
   - Press **Ctrl+Shift+R** (Windows) or **Cmd+Shift+R** (Mac)
   - This clears cache and reloads page
   - Try generating again

**STEP 5: Clear Your Browser Session**

1. **Log out** of Coach AI
2. **Clear cookies** for coachAI.app:
   - Chrome: Settings → Privacy → Cookies → See all cookies → Search "coachAI" → Remove
   - Firefox: Settings → Privacy → Manage Data → Search "coachAI" → Remove
3. **Close browser completely**
4. **Reopen and log in**
5. Try generating practice

**STEP 6: Try Different Browser**

1. If using Chrome, try Firefox or Edge
2. Use incognito/private mode
3. If it works in different browser → browser cache issue
4. If it still fails → contact support

**STEP 7: Check Advanced Mode Settings** (Advanced/Expert users only)

If you're in Advanced or Expert mode:
1. Go to **Settings → Practice**
2. Check these settings:
   - ☑️ "Prioritize Favorites" - if ON and you have 0 favorites → turn OFF
   - ☑️ "Hide Recent Drills" - if ON and you've used all drills → turn OFF
   - Intensity levels - at least one must be checked
3. Save settings
4. Try generating again

### 🔄 DECISION TREE:

```
Practice won't generate?
    │
    ├─ No team in sidebar?
    │   └─► Create team first (Step 1)
    │
    ├─ Infinite loading spinner?
    │   └─► Check internet connection (Step 2)
    │       └─► Wait 30 seconds, then refresh (Step 4)
    │
    ├─ "Failed to generate" error?
    │   └─► Check practice settings (Step 3)
    │       └─► Reset to defaults
    │       └─► Still fails? → Clear session (Step 5)
    │
    ├─ Practice has 0 drills?
    │   └─► Check Advanced settings (Step 7)
    │       └─► Turn OFF "Prioritize Favorites"
    │       └─► Turn OFF "Hide Recent"
    │
    ├─ Same practice every time?
    │   └─► Variety management issue
    │       └─► Settings → Practice → Turn OFF "Hide Recent"
    │       └─► Star some favorite drills
    │
    └─ Everything fails?
        └─► Try different browser (Step 6)
            └─► Still stuck? → Contact support
```

### ⏱️ TIME TO FIX:

**1 minute** (no team created)  
**2-3 minutes** (settings issue)  
**5 minutes** (browser cache issue)  
**10 minutes** (all troubleshooting steps)

### 🆘 STILL STUCK?

**Contact Support:**
- 📧 Email: **support@coachAI.app**
- 📧 Subject: "Practice Generation Error - [Your Team Name]"
- Include:
  - Screenshot of error message (if any)
  - What settings you're using (duration, type, player count)
  - Browser you're using (Chrome, Firefox, Safari, Edge)
  - Experience level (Essential, Advanced, Expert)
  - When the issue started
  - What you already tried

**Response time:** Under 12 hours for practice generation issues

**Temporary workaround:** 
- Try Essential mode (if in Advanced/Expert)
- Use default settings (90 min, Balanced)
- Try with different session type

### 🔗 RELATED:

- **FAQ:** Q1 - How do I create my first practice?
- **FAQ:** Q4 - How long does it take to generate?
- **FAQ:** Q6 - How many drills for 90 minutes?
- **Quick Start Guide:** Step 3 - Generate Your First Practice

---

## ISSUE #3: PDF Export Blank or Not Working

### 🔴 PROBLEM:

You click "Download PDF" but the PDF is blank, won't download, or displays incorrectly.

### 📊 SYMPTOMS:

**What you're experiencing:**
- ❌ PDF downloads but opens to blank white pages
- ❌ Click "Download PDF" → nothing happens
- ❌ PDF has text but no formatting (jumbled text)
- ❌ PDF only shows first page (practice is cut off)
- ❌ PDF download starts but fails halfway
- ❌ "Download PDF" button is grayed out / disabled

**What you tried:**
- Clicked "Download PDF" multiple times
- Refreshed the page
- Tried downloading again
- Tried opening with different PDF reader

### ⚙️ COMMON CAUSES:

**Why this happens:**
1. **Browser popup blocker** - Blocking PDF download window
2. **PDF wasn't fully generated** - Clicked download too fast
3. **Browser extension conflict** - Ad blocker or extension interfering
4. **Download folder full** - No space on hard drive
5. **PDF reader issue** - Corrupted PDF viewer
6. **Practice not saved first** - Must save before exporting
7. **Old browser version** - Doesn't support modern PDF generation

### ✅ SOLUTION:

**STEP 1: Save Practice First**

**Critical:** You must save practice before downloading PDF!

1. Scroll to bottom of generated practice
2. Click **"Save Practice"** button
3. Wait for confirmation message: "Practice saved successfully"
4. **Now** click "Download PDF"

**Why:** PDF generation requires saved practice data. Unsaved practices can't export.

**STEP 2: Check Browser Popup Blocker**

PDF opens in new tab/window, but popup blockers prevent this:

1. Look for popup blocked icon in address bar (Chrome/Firefox)
2. Click the icon
3. Select **"Always allow popups from coachAI.app"**
4. Refresh page
5. Try "Download PDF" again

**Manual Allow (if no icon):**
- Chrome: Settings → Privacy → Site Settings → Pop-ups → Add coachAI.app to "Allowed"
- Firefox: Settings → Privacy → Permissions → Block pop-up windows → Exceptions → Add coachAI.app
- Safari: Preferences → Websites → Pop-up Windows → coachAI.app → Allow

**STEP 3: Disable Browser Extensions**

Ad blockers and privacy extensions often block PDF generation:

1. **Chrome:** Click puzzle icon → Manage extensions
2. **Disable these types:** Ad blockers, Privacy tools, PDF tools
3. Refresh Coach AI page
4. Try "Download PDF" again
5. **If it works:** Re-enable extensions one by one to find culprit

**Common culprits:**
- uBlock Origin
- AdBlock Plus
- Privacy Badger
- Ghostery
- PDF editor extensions

**STEP 4: Check Download Folder**

1. Open your default downloads folder
2. Look for: `Coach_AI_Practice_[Date].pdf`
3. **If file exists but won't open:**
   - File might be corrupted
   - Delete it
   - Download fresh copy
4. **If many files in downloads folder:**
   - Clean up old files
   - Make sure you have 50+ MB free space

**STEP 5: Try Different PDF Download Method**

If "Download PDF" fails, try manual print:

1. Click **"Download HTML"** instead
2. Practice opens in new tab
3. Press **Ctrl+P** (Windows) or **Cmd+P** (Mac)
4. In print dialog:
   - Destination: **"Save as PDF"**
   - Layout: Portrait
   - Margins: Default
5. Click **"Save"**
6. Choose location and save

**This creates a PDF manually - works when automatic download fails**

**STEP 6: Update Your Browser**

Old browsers can't generate PDFs properly:

1. **Check browser version:**
   - Chrome: Menu → Help → About Google Chrome
   - Firefox: Menu → Help → About Firefox
   - Safari: Safari → About Safari
2. **Update if needed** (usually automatic)
3. **Restart browser**
4. Try "Download PDF" again

**Minimum versions:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**STEP 7: Try Different Browser**

1. If using Chrome, try Firefox or Edge
2. **Don't use Internet Explorer** (not supported)
3. If it works in different browser:
   - Original browser has extension/setting issue
   - Use working browser for now
   - Fix original browser later

### 🔄 DECISION TREE:

```
PDF won't download?
    │
    ├─ "Download PDF" button grayed out?
    │   └─► Save practice first (Step 1)
    │
    ├─ Click "Download PDF" → nothing happens?
    │   └─► Check popup blocker (Step 2)
    │       └─► Allow popups from coachAI.app
    │
    ├─ PDF downloads but is blank?
    │   └─► Disable extensions (Step 3)
    │       └─► Especially ad blockers
    │
    ├─ PDF won't open / corrupted?
    │   └─► Try HTML + manual print (Step 5)
    │       └─► This creates PDF manually
    │
    ├─ PDF only shows partial practice?
    │   └─► Browser version too old (Step 6)
    │       └─► Update browser
    │
    └─ Everything fails?
        └─► Try different browser (Step 7)
            └─► Use HTML + manual print (Step 5)
            └─► Still stuck? → Contact support
```

### ⏱️ TIME TO FIX:

**30 seconds** (didn't save practice first)  
**1-2 minutes** (popup blocker)  
**3-5 minutes** (browser extensions)  
**10 minutes** (all troubleshooting steps)

### 🆘 STILL STUCK?

**Contact Support:**
- 📧 Email: **support@coachAI.app**
- 📧 Subject: "PDF Export Not Working - [Browser Name]"
- Include:
  - Browser and version (Chrome 120, Firefox 115, etc.)
  - Operating system (Windows 11, Mac OS, etc.)
  - What happens when you click "Download PDF"
  - Screenshot of error message (if any)
  - Have you successfully downloaded PDFs before? (Yes/No)
  - What you already tried

**Response time:** Under 24 hours for export issues

**Temporary workaround:**
- Use "Download HTML" instead
- View practice on phone/tablet during practice
- Use manual print to PDF method (Step 5)
- Screenshot practice and save as images

### 🔗 RELATED:

- **FAQ:** Q5 - Can I use Coach AI offline?
- **FAQ:** Q13 - Can I share practices with assistant coaches?
- **Quick Start Guide:** Step 5 - Export & Print

---

# PART 3: DOCUMENT SOLUTIONS 4-6 (HOURS 3-4)

## ISSUE #4: Drills Don't Match My Team

### 🔴 PROBLEM:

Generated practices include drills that don't match your team's age, skill level, focus areas, or available players.

### 📊 SYMPTOMS:

**What you're experiencing:**
- ❌ Drills are too advanced for your beginner team
- ❌ Drills require more players than you have
- ❌ No drills match your focus areas (e.g., "First touch")
- ❌ Same drills appear every practice (no variety)
- ❌ All drills are too easy for your advanced team
- ❌ Drills don't match your team's play style

**What you tried:**
- Generated multiple practices (same problem)
- Changed session type (didn't help)
- Checked drill library (drills look fine there)

### ⚙️ COMMON CAUSES:

**Why this happens:**
1. **Incomplete team profile** - Missing age/skill/roster information
2. **No focus areas set** - AI doesn't know what to prioritize
3. **Conflicting settings** - Advanced mode filters too restrictive
4. **Limited drill pool** - "Hide Recent" + "Favorites Only" = too few drills
5. **Wrong experience mode** - Need Advanced mode for smart matching
6. **Drill library cache issue** - Old data being used

### ✅ SOLUTION:

**STEP 1: Complete Your Team Profile**

AI matching requires complete team information:

1. Go to **Team Hub** (sidebar)
2. Click **"Edit Team Profile"**
3. Verify these fields:
   - ✅ **Age Group:** Correct age (U8, U10, U12, etc.)
   - ✅ **Skill Level:** Accurate (Beginner/Intermediate/Advanced)
   - ✅ **Roster Size:** Actual typical practice attendance
4. **Save profile**
5. Generate new practice
6. Check if drills match better

**STEP 2: Add Focus Areas** (Advanced/Expert mode)

Tell AI what skills you're working on:

1. **Team Hub** → **Edit Team Profile**
2. Scroll to **"Focus Areas"** section
3. **Add 3-5 focus areas** your team needs:
   - Examples: "First touch", "Quick passing", "Defending 1v1"
   - "Building from back", "Shooting accuracy"
   - "Transition play", "Finishing"
4. Press **Enter** after typing each one
5. **Save profile** (must save!)
6. **Generate new practice**
7. Look for **"Matched focus: [area]"** labels on drills

**Why this matters:** Without focus areas, AI picks randomly. With focus areas, AI prioritizes relevant drills.

**STEP 3: Check Practice Generation Settings** (Advanced/Expert)

Restrictive settings limit drill variety:

1. Go to **Settings** → **Practice** tab
2. Review these settings:

**Problem settings:**
- ☑️ **"Prioritize Favorites"** + 0 favorites starred = NO DRILLS
  - **Fix:** Turn OFF or star 10+ drills first
  
- ☑️ **"Hide Recent Drills"** + used most drills = NO VARIETY
  - **Fix:** Turn OFF temporarily or wait 7 days
  
- **Intensity levels:** Only "High" checked but beginner team
  - **Fix:** Check all three (Low, Medium, High)
  
- **Preferred categories:** Only 1-2 categories selected
  - **Fix:** Leave empty or select 3+ categories

3. **Adjust problematic settings**
4. **Save settings**
5. **Generate new practice**

**STEP 4: Upgrade to Advanced Mode** (If in Essential)

Essential mode uses basic matching only:

1. Click **"Experience Level"** dropdown (sidebar)
2. Select **"Advanced"**
3. Complete team profile with focus areas (Step 2)
4. Generate practice
5. See improved drill matching

**Advanced mode benefits:**
- ✅ AI learns your focus areas
- ✅ Better variety management
- ✅ Matches team play style
- ✅ Shows "Matched focus" labels

**STEP 5: Reset Drill Variety**

If seeing same drills repeatedly:

1. **Settings** → **Practice** tab
2. **Turn OFF** "Hide Recent Drills" (temporarily)
3. **Generate 2-3 practices** (get fresh drills)
4. **Turn ON** "Hide Recent Drills" again
5. Continue generating - should see variety now

**Why:** Sometimes variety tracking gets stuck. Resetting clears it.

**STEP 6: Verify Drill Library Access** (Advanced mode)

Make sure you can see all drills:

1. Navigate to **"Drills"** page (sidebar)
2. **Remove all filters** (click "Clear Filters")
3. Count drills shown: Should see **45+ drills**
4. **If fewer than 45 drills:**
   - Click "Refresh Library"
   - Log out and log back in
   - Clear browser cache
5. **Generate practice again**

**STEP 7: Manual Drill Selection** (Workaround)

If automatic matching fails, build practice manually:

1. Go to **Drill Library**
2. **Filter drills:**
   - Category: Select what you need
   - Intensity: Match your team
   - Players: Match your roster
   - Duration: What you have time for
3. **Star the drills** you want to use
4. **Settings** → **Practice** → Turn ON "Prioritize Favorites"
5. **Generate practice** → Uses your starred drills

**This gives you full control when AI matching isn't working**

### 🔄 DECISION TREE:

```
Drills don't match your team?
    │
    ├─ Drills too advanced/easy?
    │   └─► Check team profile (Step 1)
    │       └─► Verify skill level is correct
    │       └─► Check age group is accurate
    │
    ├─ Drills don't match focus areas?
    │   └─► In Advanced/Expert mode?
    │       ├─ Yes → Add focus areas (Step 2)
    │       └─ No → Upgrade to Advanced (Step 4)
    │
    ├─ Same drills every time?
    │   └─► Check "Hide Recent" setting (Step 5)
    │       └─► Turn OFF temporarily
    │
    ├─ Drills need more players than you have?
    │   └─► Update roster size (Step 1)
    │       └─► Set to typical attendance, not total roster
    │
    ├─ Getting very few drills to choose from?
    │   └─► Check practice settings (Step 3)
    │       └─► Turn OFF "Prioritize Favorites"
    │       └─► Turn OFF "Hide Recent"
    │
    └─ Nothing works?
        └─► Manual drill selection (Step 7)
            └─► Build practice yourself using starred drills
            └─► Contact support for AI matching fix
```

### ⏱️ TIME TO FIX:

**2 minutes** (add focus areas)  
**3 minutes** (complete team profile)  
**5 minutes** (adjust practice settings)  
**10 minutes** (all troubleshooting steps)

### 🆘 STILL STUCK?

**Contact Support:**
- 📧 Email: **support@coachAI.app**
- 📧 Subject: "Drill Matching Issue - [Team Name]"
- Include:
  - Team profile details (age, skill, roster size)
  - Focus areas you've added
  - Example of drills that don't match (screenshots)
  - What drills you expected vs. what you got
  - Experience level (Essential, Advanced, Expert)

**Response time:** Under 24 hours for matching issues

**Temporary workaround:**
- Use manual drill selection (Step 7)
- Swap individual drills that don't match
- Use "Reuse Practice" for practices that worked well

### 🔗 RELATED:

- **FAQ:** Q2 - Do I need to fill out entire team profile?
- **FAQ:** Q11 - How does AI drill matching work?
- **FAQ:** Q3 - How do I upgrade to Advanced mode?
- **User Guide:** Complete Team Management section

---

## ISSUE #5: Settings Won't Save

### 🔴 PROBLEM:

You change settings (duration, session type, display options) but they don't save or revert to defaults.

### 📊 SYMPTOMS:

**What you're experiencing:**
- ❌ Change default duration → reverts to 90 minutes
- ❌ Turn ON auto-save → turns back OFF
- ❌ Change session type → resets to Balanced
- ❌ Check/uncheck options → changes disappear
- ❌ Settings save but don't apply to practice generation
- ❌ "Settings saved successfully" message but nothing changed

**What you tried:**
- Changed settings multiple times
- Clicked save button repeatedly
- Refreshed the page
- Logged out and back in (settings still wrong)

### ⚙️ COMMON CAUSES:

**Why this happens:**
1. **Browser blocking cookies** - Settings stored in cookies/localStorage
2. **Private/Incognito mode** - Doesn't save anything
3. **Browser cache corrupted** - Old settings overwriting new
4. **Auto-save timing issue** - Saving too fast, not fully committed
5. **Multiple tabs open** - Conflicting settings between tabs
6. **Extension interference** - Privacy extension blocking storage

### ✅ SOLUTION:

**STEP 1: Check for Auto-Save Confirmation**

Settings auto-save, but you must wait for confirmation:

1. Make a setting change
2. **Wait 2-3 seconds** (don't click away immediately)
3. Look for **"Settings saved"** message (top right)
4. **If no message appears:** Settings didn't save
5. Click **anywhere outside the setting** to trigger save
6. Verify message appears

**Common mistake:** Clicking away too fast before auto-save completes

**STEP 2: Exit Private/Incognito Mode**

Private browsing doesn't save settings:

1. Check if you're in private/incognito mode
   - Chrome: Shows incognito icon (hat/glasses)
   - Firefox: Shows purple mask icon
   - Safari: Shows "Private" in address bar
2. **If in private mode:**
   - Open regular browser window
   - Log in to Coach AI
   - Change settings
   - Settings will save now

**Why:** Private mode deletes everything when you close window

**STEP 3: Enable Cookies for Coach AI**

Settings require cookies to be enabled:

1. **Chrome:**
   - Settings → Privacy → Cookies
   - Select **"Allow all cookies"** OR
   - Add exception for coachAI.app
   
2. **Firefox:**
   - Settings → Privacy → Custom
   - Uncheck "Delete cookies when Firefox closes"
   - Add exception for coachAI.app
   
3. **Safari:**
   - Preferences → Privacy
   - Uncheck "Block all cookies"

4. **After enabling cookies:**
   - Refresh Coach AI page
   - Change settings again
   - Verify they save

**STEP 4: Close Extra Tabs**

Multiple tabs can cause conflicts:

1. **Close ALL Coach AI tabs** except one
2. **Refresh the remaining tab**
3. Change settings
4. Verify save confirmation
5. **From now on:** Use only one Coach AI tab at a time

**Why:** Each tab can have different session data. Last one to save "wins" and might overwrite your changes.

**STEP 5: Clear Browser Cache**

Corrupted cache can prevent saves:

1. **Chrome:** Ctrl+Shift+Delete → Clear browsing data
   - Time range: "Last 24 hours"
   - Check: "Cookies" and "Cached files"
   - Click "Clear data"

2. **Firefox:** Ctrl+Shift+Delete → Clear Recent History
   - Time range: "Last 24 hours"
   - Check: "Cookies" and "Cache"
   - Click "Clear Now"

3. **After clearing:**
   - **Log out** of Coach AI
   - **Close browser completely**
   - **Reopen and log in**
   - Change settings
   - Should save now

**STEP 6: Disable Privacy Extensions**

Extensions can block settings storage:

1. Try browser in **incognito mode** (extensions disabled by default)
2. Log in to Coach AI
3. Change settings
4. **If settings save in incognito:**
   - You have an extension conflict
   - Exit incognito
   - Disable extensions one by one to find culprit

**Common culprits:**
- Privacy Badger
- Ghostery
- uBlock Origin (strict mode)
- Cookie AutoDelete

**STEP 7: Verify Settings Applied**

Sometimes settings save but don't apply:

1. Go to **Settings** page
2. Verify your changes are shown (not reverted)
3. **If shown correctly:** Settings are saved
4. **Navigate to Practice Generator**
5. Check if defaults match your settings
6. **If defaults don't match:**
   - Settings saved but not applying
   - Log out and log in
   - Generate practice
   - Should work now

### 🔄 DECISION TREE:

```
Settings won't save?
    │
    ├─ No "Settings saved" message appears?
    │   └─► Wait 2-3 seconds after change (Step 1)
    │       └─► Click outside setting to trigger save
    │
    ├─ In private/incognito browsing mode?
    │   └─► Exit private mode (Step 2)
    │       └─► Use regular browser window
    │
    ├─ Settings save but revert after refresh?
    │   └─► Check cookies enabled (Step 3)
    │       └─► Allow cookies for coachAI.app
    │
    ├─ Multiple Coach AI tabs open?
    │   └─► Close all but one tab (Step 4)
    │
    ├─ Settings save but don't apply?
    │   └─► Log out and log in (Step 7)
    │       └─► Clear browser cache (Step 5)
    │
    └─ Everything fails?
        └─► Disable privacy extensions (Step 6)
            └─► Try different browser
            └─► Still stuck? → Contact support
```

### ⏱️ TIME TO FIX:

**10 seconds** (waiting for auto-save)  
**1 minute** (cookies issue)  
**5 minutes** (browser cache)  
**10 minutes** (all troubleshooting steps)

### 🆘 STILL STUCK?

**Contact Support:**
- 📧 Email: **support@coachAI.app**
- 📧 Subject: "Settings Not Saving - [Browser Name]"
- Include:
  - Which specific settings won't save
  - Browser and version
  - Screenshot of Settings page
  - Are you in private/incognito mode? (Yes/No)
  - Do other websites save your preferences? (Yes/No)
  - What you already tried

**Response time:** Under 24 hours for settings issues

**Temporary workaround:**
- Set preferences manually each time you generate practice
- Use Essential mode (fewer settings to manage)
- Try different browser that saves correctly

### 🔗 RELATED:

- **FAQ:** Q6 - How many drills for 90-minute practice?
- **Quick Start Guide:** Step 3 - Configure your practice
- **User Guide:** Settings section

---

## ISSUE #6: Can't Star Drills / Features Not Responding

### 🔴 PROBLEM:

Interactive features (star drills, swap drills, expand details) don't work when you click them.

### 📊 SYMPTOMS:

**What you're experiencing:**
- ❌ Click "⭐ Star" button → nothing happens
- ❌ Click "Swap" drill → no new drill appears
- ❌ Click "↑" or "↓" to reorder → drills don't move
- ❌ Click "Details" → drill doesn't expand
- ❌ Click any button → no response, no feedback
- ❌ Buttons appear grayed out or disabled
- ❌ Features worked before but stopped working

**What you tried:**
- Clicked buttons multiple times
- Refreshed the page
- Tried different drills
- Logged out and back in (still not working)

### ⚙️ COMMON CAUSES:

**Why this happens:**
1. **JavaScript disabled** - Features require JavaScript
2. **Browser extension blocking** - Script blocker interfering
3. **Page didn't fully load** - Tried clicking too soon
4. **Network error mid-session** - Lost connection
5. **Cached old version** - Browser using outdated code
6. **Browser too old** - Doesn't support modern features
7. **Wrong experience mode** - Feature not available in Essential

### ✅ SOLUTION:

**STEP 1: Verify JavaScript is Enabled**

All interactive features require JavaScript:

1. **Test:** Can you see dropdown menus working? Can you type in search?
2. **If nothing interactive works:**
   - JavaScript is likely disabled

**Enable JavaScript:**

**Chrome:**
- Settings → Privacy and Security → Site Settings
- Scroll to "JavaScript"
- Select "Sites can use Javascript"
- Refresh Coach AI

**Firefox:**
- Type `about:config` in address bar
- Search: `javascript.enabled`
- Set to `true`
- Refresh Coach AI

**Safari:**
- Preferences → Security
- Check "Enable JavaScript"
- Refresh Coach AI

**STEP 2: Wait for Page to Fully Load**

Clicking before page loads causes issues:

1. **After navigating to a page, wait for:**
   - Loading spinner to disappear
   - All drill cards to appear
   - "Ready" or page loaded indicator
   
2. **Look for these signs page is loaded:**
   - Drill images loaded (not broken image icons)
   - All buttons visible and clickable
   - No "Loading..." text anywhere
   
3. **Then try clicking features**

**Common mistake:** Clicking "Swap" while practice is still generating

**STEP 3: Check Your Internet Connection**

Features need connection to work:

1. Look at WiFi icon in browser
2. **Test connection:**
   - Try loading another website
   - Refresh Coach AI page completely
   
3. **If connection dropped:**
   - Reconnect to WiFi
   - Refresh Coach AI
   - Try feature again

**STEP 4: Hard Refresh the Page**

Clear cached code and reload fresh:

1. **Hard refresh:**
   - Windows: **Ctrl + Shift + R**
   - Mac: **Cmd + Shift + R**
   
2. Wait for page to fully reload
3. Wait for drills to appear
4. Try clicking features

**Why:** Browser might be using old cached code that's broken

**STEP 5: Disable Browser Extensions**

Extensions can block JavaScript execution:

**Most likely culprits:**
- NoScript
- uMatrix
- ScriptSafe
- Adblock Plus (with script blocking enabled)
- Privacy Badger (strict mode)

**Test:**
1. Open Coach AI in **incognito/private mode** (extensions disabled)
2. Try starring a drill or swapping
3. **If it works in incognito:**
   - You have extension conflict
   - Disable extensions in normal browser
   - Re-enable one by one to find culprit

**STEP 6: Clear All Browser Data**

Nuclear option - clears everything:

1. **Chrome:** Ctrl+Shift+Delete
   - Time range: **"All time"**
   - Check ALL boxes
   - Click "Clear data"
   
2. **Firefox:** Ctrl+Shift+Delete
   - Time range: **"Everything"**
   - Check ALL boxes
   - Click "Clear Now"

3. **After clearing:**
   - **Close browser completely**
   - **Reopen**
   - **Log in to Coach AI**
   - Try features - should work now

**Warning:** This logs you out of all websites. Have your Coach AI password ready!

**STEP 7: Verify Experience Mode** (Feature-Specific)

Some features only available in certain modes:

**Star Drills:**
- ✅ Available: Advanced, Expert
- ❌ Not available: Essential
- **Fix:** Upgrade to Advanced mode

**Swap Drills:**
- ✅ Available: All modes
- **If not working:** Check Steps 1-6

**Drill Details:**
- ✅ Available: All modes
- **If not expanding:** JavaScript or loading issue (Steps 1, 2)

**Reorder Drills:**
- ✅ Available: All modes (generated practices)
- ❌ Not available: Practice templates (view only)

**STEP 8: Update Your Browser**

Old browsers lack modern features:

1. **Check version:**
   - Chrome: Menu → Help → About Google Chrome
   - Firefox: Menu → Help → About Firefox
   - Edge: Menu → Help → About Microsoft Edge

2. **Required minimum:**
   - Chrome 90+
   - Firefox 88+
   - Safari 14+
   - Edge 90+

3. **If outdated:**
   - Update browser (usually automatic)
   - Restart browser
   - Try features again

### 🔄 DECISION TREE:

```
Features not responding?
    │
    ├─ NOTHING interactive works (dropdowns, buttons)?
    │   └─► JavaScript disabled (Step 1)
    │       └─► Enable JavaScript in browser
    │
    ├─ Clicked immediately after page loaded?
    │   └─► Page didn't fully load (Step 2)
    │       └─► Wait for all content to appear
    │       └─► Then try clicking
    │
    ├─ Some features work, others don't?
    │   └─► Check experience mode (Step 7)
    │       └─► Feature might not be available
    │       └─► Upgrade to Advanced/Expert
    │
    ├─ Features worked before but stopped?
    │   └─► Hard refresh page (Step 4)
    │       └─► Clear browser cache (Step 6)
    │
    ├─ Works in incognito but not normal browser?
    │   └─► Extension conflict (Step 5)
    │       └─► Disable script blockers
    │
    └─ Everything fails?
        └─► Update browser (Step 8)
            └─► Try different browser
            └─► Still stuck? → Contact support
```

### ⏱️ TIME TO FIX:

**30 seconds** (waiting for page to load)  
**1 minute** (hard refresh)  
**3-5 minutes** (browser extensions)  
**10 minutes** (all troubleshooting steps)

### 🆘 STILL STUCK?

**Contact Support:**
- 📧 Email: **support@coachAI.app**
- 📧 Subject: "Interactive Features Not Working - [Specific Feature]"
- Include:
  - Which specific feature isn't working (Star, Swap, Details, etc.)
  - Browser and version
  - Experience mode (Essential, Advanced, Expert)
  - Screenshot showing the issue
  - What happens when you click (nothing, error, something else?)
  - Do dropdowns and menus work? (Yes/No)
  - What you already tried

**Response time:** Under 24 hours for functionality issues

**Temporary workaround:**
- **Can't star drills:** Write down drill names you like, filter to them manually
- **Can't swap drills:** Regenerate entire practice to get different drills
- **Can't expand details:** Click "Drills" page to view full drill info
- **Can't reorder:** Accept generated order or regenerate practice

### 🔗 RELATED:

- **FAQ:** Q3 - How do I upgrade to Advanced mode?
- **FAQ:** Q12 - Can I add my own custom drills?
- **User Guide:** Drill Library section

---

# PART 4: FORMAT & DEPLOY (HOURS 5-6)

## Web Version Format

### Searchable Troubleshooting Page

**Features:**

```html
TROUBLESHOOTING GUIDE - WEB VERSION
═══════════════════════════════════════════════════════════════

🔍 SEARCH: [                                    ]
    "Search by keyword or error message..."

📋 QUICK NAVIGATION:
    ├─ 🔐 Can't Log In
    ├─ ⚡ Practice Won't Generate
    ├─ 📄 PDF Export Issues
    ├─ 🎯 Drills Don't Match Team
    ├─ ⚙️ Settings Won't Save
    └─ 🖱️ Features Not Responding

═══════════════════════════════════════════════════════════════

For each issue:
    [+] ISSUE TITLE (click to expand)
        └─ Problem description
        └─ Symptoms (with ❌ marks)
        └─ Step-by-step solution (numbered)
        └─ Decision tree (visual flowchart)
        └─ Time estimate
        └─ Support escalation
        └─ Related links

═══════════════════════════════════════════════════════════════
```

### Interactive Elements:

**□ Search Functionality**
- Searches problem titles, symptoms, and solutions
- Highlights matching text
- Real-time filtering

**□ Expandable Sections**
- Issues collapsed by default
- Click to expand
- Expand All / Collapse All buttons

**□ Decision Trees**
- Visual flowcharts
- Clickable decision points
- "Show me next step" buttons

**□ Progress Tracking**
- Checkboxes next to each troubleshooting step
- "I tried this - didn't work" button → shows next step
- "This worked!" button → marks issue resolved

---

## Print Version Format

### PDF Layout:

**Page 1: Table of Contents**
```
COACH AI TROUBLESHOOTING GUIDE
═══════════════════════════════════════════════════════════════

Quick Issue Finder:

Issue 1: Can't Log In / Forgot Password ................ Page 2
Issue 2: Practice Won't Generate ...................... Page 4
Issue 3: PDF Export Blank or Not Working .............. Page 6
Issue 4: Drills Don't Match My Team ................... Page 8
Issue 5: Settings Won't Save .......................... Page 10
Issue 6: Can't Star Drills / Features Not Responding .. Page 12

General Support Information ........................... Page 14

═══════════════════════════════════════════════════════════════

FOR IMMEDIATE HELP: support@coachAI.app
```

**Pages 2-13: Issues (2 pages each)**
- Page 1: Problem, Symptoms, Solution steps 1-4
- Page 2: Solution steps 5+, Decision tree, Support info

**Page 14: Support Resources**
- Email: support@coachAI.app
- Discord: discord.gg/coachAI
- Help Center: www.coachAI.app/help
- FAQ: www.coachAI.app/faq
- Quick Start Guide link
- Response time expectations

---

## Cross-Reference Matrix

**Link Issues to FAQ:**

```
Issue 1 (Can't Log In) → FAQ Q17, Q19
Issue 2 (Practice Won't Generate) → FAQ Q1, Q4, Q6
Issue 3 (PDF Export) → FAQ Q5, Q13
Issue 4 (Drills Don't Match) → FAQ Q2, Q11, Q3
Issue 5 (Settings Won't Save) → FAQ Q6
Issue 6 (Features Not Responding) → FAQ Q3, Q12
```

**Link Issues to Quick Start Guide:**

```
Issue 1 → Quick Start Step 1 (Create Account)
Issue 2 → Quick Start Step 3 (Generate Practice)
Issue 3 → Quick Start Step 5 (Export & Print)
Issue 4 → Quick Start Step 2 (Create Team)
Issue 5 → Quick Start Step 3 (Configure)
Issue 6 → Quick Start Step 4 (Review)
```

---

## Quality Assurance Checklist

```
TROUBLESHOOTING GUIDE - FINAL QA
═══════════════════════════════════════════════════════════════

Content Quality:
□ All 6 issues documented
□ Solutions are step-by-step (numbered)
□ Each step is actionable and clear
□ Decision trees are logical
□ Time estimates are realistic
□ Support escalation paths clear

Solution Accuracy:
□ Each solution tested and verified
□ Steps work in actual browser
□ Screenshots accurate (if included)
□ Links work correctly
□ Cross-references accurate

Web Version:
□ Search functionality works
□ Expand/collapse works
□ Mobile-responsive
□ All links functional
□ Decision trees interactive (optional)

Print Version:
□ PDF exports correctly
□ Table of contents page numbers accurate
□ Page breaks logical (not mid-solution)
□ All text readable when printed
□ Footer on every page

User Testing:
□ 2 people tested 3 different issues
□ Users could follow solutions
□ Time estimates verified
□ Users reached resolution or support

Integration:
□ Links to FAQ work
□ Links to Quick Start work
□ Terminology consistent
□ Contact info correct

Deployment:
□ Web version live at /troubleshooting
□ PDF downloadable from Help Center
□ Linked from error messages in app
□ Linked from FAQ when relevant
□ Support team has access

═══════════════════════════════════════════════════════════════
```

---

## Testing Protocol

**Test Each Issue with Real User:**

**Issue Selection:**
- Pick 3 different issues
- Mix difficulty levels (easy, medium, hard)
- Test with 2 different people

**Testing Process:**

1. **Give user the scenario:**
   - "Pretend you're experiencing [issue]"
   - "Use the Troubleshooting Guide to fix it"

2. **Watch them work through solution:**
   - Time how long it takes
   - Note where they get confused
   - Note if solution works

3. **Debrief:**
   - Was solution clear?
   - Did they get stuck anywhere?
   - How could it be improved?

4. **Fix any issues found:**
   - Rewrite confusing steps
   - Add missing information
   - Adjust time estimates

---

# END OF DAY 4 DELIVERABLES

## ✅ COMPLETION CHECKLIST

### Content Complete
- [ ] 6 critical issues identified
- [ ] All 6 solutions written and tested
- [ ] Step-by-step instructions clear and actionable
- [ ] Decision trees created for each issue
- [ ] Time estimates realistic and verified
- [ ] Support escalation paths defined

### Web Version Complete
- [ ] HTML file with search functionality
- [ ] Expandable/collapsible sections
- [ ] Mobile-responsive design
- [ ] Decision trees (visual or text)
- [ ] All links tested and working

### Print Version Complete
- [ ] PDF with table of contents
- [ ] Page numbers accurate
- [ ] 2 pages per issue (14 pages total)
- [ ] Coach AI branding present
- [ ] Prints clearly on standard paper

### Quality Assurance
- [ ] Each solution tested by 2 different people
- [ ] Users successfully resolved issues
- [ ] Time estimates verified
- [ ] No broken links
- [ ] Terminology consistent with other docs
- [ ] Cross-references accurate

### Deployment Ready
- [ ] Files backed up (cloud + local)
- [ ] Ready to upload to website
- [ ] In-app error message links prepared
- [ ] Support team trained on guide

---

## 📊 SUCCESS METRICS

**After Day 4:**

Troubleshooting Quality:
- [ ] 6 critical issues covered (100% of blocking issues)
- [ ] Solutions work for 90%+ of users
- [ ] Average resolution time: <10 minutes
- [ ] Users can follow steps independently

Usability:
- [ ] Users find relevant issue in <30 seconds
- [ ] Instructions clear to non-technical users
- [ ] Decision trees easy to follow
- [ ] Support escalation clear

Integration:
- [ ] Links to FAQ work bidirectionally
- [ ] Links to Quick Start Guide work
- [ ] Referenced from in-app error messages
- [ ] Searchable from Help Center

Support Impact:
- [ ] 60%+ of issues self-resolved (no support ticket)
- [ ] Support tickets include "I tried steps 1-5"
- [ ] Average support time reduced by 50%

---

## 🚀 WHAT'S NEXT?

**Day 4 Complete!** You now have:
1. ✅ Quick Start Guide (tested and polished)
2. ✅ Onboarding Checklist (in-app + standalone)
3. ✅ FAQ with 20 core questions
4. ✅ Troubleshooting Guide with 6 critical issues

**Ready for Day 5:** Review, Test & Deploy Everything!

Day 5 will:
- Cross-check all 4 documents for consistency
- User flow testing (simulate new user journey)
- Final QA across all docs
- Deploy to website
- Create welcome email template
- Prepare support team

---

**Created:** January 30, 2026  
**Phase 1 Pre-Launch Documentation**  
**Status:** Day 4 Complete - Ready for Day 5

**File:** Coach_AI_Troubleshooting_DAY4_COMPLETE.md
