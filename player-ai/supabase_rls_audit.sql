-- ============================================================
-- RLS Audit — run in Supabase SQL Editor
-- Coach AI uses custom auth (not Supabase Auth), so policies
-- cannot use auth.uid(). All data access is server-side via
-- server actions; the anon key client is never used for queries.
-- Goal: ensure anon key cannot read sensitive tables even if a
-- future bug bypasses the application auth layer.
-- ============================================================

-- ── 1. Check current RLS status ───────────────────────────────
SELECT
  schemaname,
  tablename,
  rowsecurity AS rls_enabled
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

-- ── 2. Check existing policies ────────────────────────────────
SELECT schemaname, tablename, policyname, roles, cmd, qual
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- ── 3. Enable RLS on all sensitive tables ─────────────────────
ALTER TABLE users     ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE drills    ENABLE ROW LEVEL SECURITY;

-- ── 4. users table — drop signup policy, lock to service_role ─
-- All user operations (login, signup, delete) go through server actions
-- using the service_role key. No anon/authenticated access needed.
DROP POLICY IF EXISTS "Allow public signup" ON users;
-- Result: no policies = service_role only

-- ── 5. user_data table — drop all policies, lock to service_role
-- Our app uses custom auth (not Supabase Auth), so auth.uid()-based
-- policies don't isolate rows. All access uses service_role server-side.
DROP POLICY IF EXISTS "Users can read own data"   ON user_data;
DROP POLICY IF EXISTS "Users can insert own data" ON user_data;
DROP POLICY IF EXISTS "Users can update own data" ON user_data;
-- Result: no policies = service_role only

-- ── 6. drills table — remove all write policies ───────────────
-- Admin content editor uses service_role (bypasses RLS).
-- Anon key should only ever read drills, never write.
DROP POLICY IF EXISTS "Allow admin drill inserts"           ON drills;
DROP POLICY IF EXISTS "Allow admin drill updates"           ON drills;
DROP POLICY IF EXISTS "Allow drill inserts"                 ON drills;
DROP POLICY IF EXISTS "Allow drill updates"                 ON drills;
DROP POLICY IF EXISTS "Allow public read access to drills"  ON drills;
DROP POLICY IF EXISTS "Drills are publicly readable"        ON drills;
DROP POLICY IF EXISTS "drills_read"                         ON drills;
-- Keep one clean read policy
CREATE POLICY "drills_read" ON drills
  FOR SELECT TO anon, authenticated USING (true);

-- ── 7. d1_coaches / d1_programs — legacy tables ───────────────
-- These appear to be old recruiting tables superseded by coaches/programs.
-- Lock writes; keep public read since the data is non-sensitive.
DROP POLICY IF EXISTS "Service role write d1_coaches"  ON d1_coaches;
DROP POLICY IF EXISTS "Service role write d1_programs" ON d1_programs;
-- Public read stays as-is (non-sensitive public data)

-- ── 8. reel_submissions — verify policy is row-isolating ──────
-- "Users can manage own submissions" — check what column it uses.
-- If it relies on auth.uid() it won't work with our custom auth.
-- All reel actions go through server actions with service_role, so
-- drop the policy and lock to service_role only.
DROP POLICY IF EXISTS "Users can manage own submissions" ON reel_submissions;
-- Result: no policies = service_role only

-- ── 9. Verify final state ─────────────────────────────────────
SELECT
  t.tablename,
  t.rowsecurity AS rls_on,
  COALESCE(
    string_agg(p.policyname || ' (' || p.roles::text || ')', ', '),
    '(no policies — service_role only)'
  ) AS policies
FROM pg_tables t
LEFT JOIN pg_policies p
  ON p.schemaname = t.schemaname AND p.tablename = t.tablename
WHERE t.schemaname = 'public'
GROUP BY t.tablename, t.rowsecurity
ORDER BY t.tablename;
