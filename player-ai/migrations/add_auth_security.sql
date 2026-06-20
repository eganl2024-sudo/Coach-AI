-- Auth security hardening migration
-- Run once against the Supabase database (SQL editor or psql).

-- 1. Email for password reset (nullable — existing accounts opt in via Profile)
ALTER TABLE users
  ADD COLUMN IF NOT EXISTS email TEXT;

-- 2. Password reset tokens (64-char hex, 1-hour expiry enforced in application)
ALTER TABLE users
  ADD COLUMN IF NOT EXISTS reset_token            TEXT,
  ADD COLUMN IF NOT EXISTS reset_token_expires_at TIMESTAMPTZ;

-- 3. Index for O(1) token lookup during password reset
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_reset_token
  ON users (reset_token)
  WHERE reset_token IS NOT NULL;

-- 4. RLS policy — users can only read/update their own row.
--    These may already exist; IF NOT EXISTS guards make this re-runnable.
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies WHERE tablename = 'users' AND policyname = 'users_select_own'
  ) THEN
    CREATE POLICY users_select_own ON users
      FOR SELECT USING (username = current_setting('app.current_user', true));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies WHERE tablename = 'users' AND policyname = 'users_update_own'
  ) THEN
    CREATE POLICY users_update_own ON users
      FOR UPDATE USING (username = current_setting('app.current_user', true));
  END IF;
END
$$;
