-- ============================================================
-- Migration 001: RLS lockdown
--
-- Coach AI uses custom auth (not Supabase Auth), so all data
-- access is server-side via server actions that use the
-- service_role key, which bypasses RLS.  Enabling RLS and
-- removing permissive anon policies means a leaked anon key
-- can never read or write sensitive rows.
--
-- Run once in the Supabase SQL Editor (Dashboard → SQL Editor).
-- ============================================================

-- ── users: no anon access ─────────────────────────────────────
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow public signup" ON users;
-- No policies added → only service_role can read/write.

-- ── user_data: no anon access ─────────────────────────────────
ALTER TABLE user_data ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users can read own data"   ON user_data;
DROP POLICY IF EXISTS "Users can insert own data" ON user_data;
DROP POLICY IF EXISTS "Users can update own data" ON user_data;
-- No policies added → only service_role can read/write.

-- ── drills: read-only for anon, no writes ─────────────────────
ALTER TABLE drills ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow admin drill inserts"          ON drills;
DROP POLICY IF EXISTS "Allow admin drill updates"          ON drills;
DROP POLICY IF EXISTS "Allow drill inserts"                ON drills;
DROP POLICY IF EXISTS "Allow drill updates"                ON drills;
DROP POLICY IF EXISTS "Allow public read access to drills" ON drills;
DROP POLICY IF EXISTS "Drills are publicly readable"       ON drills;
DROP POLICY IF EXISTS "drills_read"                        ON drills;

-- Single clean read policy: the drill library is non-sensitive public content.
CREATE POLICY "drills_read" ON drills
  FOR SELECT TO anon, authenticated USING (true);
-- Writes go through server actions (service_role), which bypass RLS.

-- ── reel_submissions: no anon access ──────────────────────────
-- All reel operations go through server actions (service_role).
-- The old policy used auth.uid() which doesn't work with custom auth.
ALTER TABLE reel_submissions ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users can manage own submissions" ON reel_submissions;
-- No policies added → only service_role can read/write.

-- ── recruiting tables: public read, no anon writes ────────────
-- d1_coaches and d1_programs hold public NCAA directory data.
-- Writes go through the enrichment scraper (service_role).
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'd1_coaches') THEN
    ALTER TABLE d1_coaches ENABLE ROW LEVEL SECURITY;
    DROP POLICY IF EXISTS "Service role write d1_coaches" ON d1_coaches;
  END IF;
  IF EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'd1_programs') THEN
    ALTER TABLE d1_programs ENABLE ROW LEVEL SECURITY;
    DROP POLICY IF EXISTS "Service role write d1_programs" ON d1_programs;
  END IF;
END $$;
