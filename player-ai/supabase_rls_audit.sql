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
  rowsecurity AS rls_enabled,
  forcerowsecurity AS rls_forced
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
-- programs and coaches already have RLS from supabase_schema.sql

-- ── 4. users table — anon and authenticated cannot read ───────
-- Only service_role (server actions) can access this table.
-- Drop any existing permissive policies first.
DROP POLICY IF EXISTS "users_read"   ON users;
DROP POLICY IF EXISTS "users_insert" ON users;
DROP POLICY IF EXISTS "users_update" ON users;
DROP POLICY IF EXISTS "users_delete" ON users;
-- No policies = only service_role can access (RLS blocks all other roles)

-- ── 5. user_data table — anon cannot read any row ─────────────
-- All user_data access goes through server actions with service_role key.
-- Lock out anon key entirely.
DROP POLICY IF EXISTS "user_data_read"   ON user_data;
DROP POLICY IF EXISTS "user_data_insert" ON user_data;
DROP POLICY IF EXISTS "user_data_update" ON user_data;
DROP POLICY IF EXISTS "user_data_delete" ON user_data;
-- No policies = only service_role can access

-- ── 6. drills table — read-only for authenticated ─────────────
DROP POLICY IF EXISTS "drills_read"   ON drills;
DROP POLICY IF EXISTS "drills_insert" ON drills;
DROP POLICY IF EXISTS "drills_update" ON drills;
DROP POLICY IF EXISTS "drills_delete" ON drills;

-- Admin content editor uses service_role, so no write policy needed.
-- Anon key should be able to read drills (future: client-side drill browser).
-- For now, lock to authenticated only since we have no anon users.
CREATE POLICY "drills_read" ON drills
  FOR SELECT TO authenticated USING (true);

-- ── 7. Verify final state ─────────────────────────────────────
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
