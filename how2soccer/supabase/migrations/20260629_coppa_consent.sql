-- COPPA consent columns for h2s_parents
-- Run this in Supabase SQL editor before enabling the COPPA email gate.
ALTER TABLE h2s_parents
  ADD COLUMN IF NOT EXISTS consent_token TEXT,
  ADD COLUMN IF NOT EXISTS consent_token_exp TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS consent_given_at TIMESTAMPTZ;

CREATE UNIQUE INDEX IF NOT EXISTS h2s_parents_consent_token_idx
  ON h2s_parents (consent_token)
  WHERE consent_token IS NOT NULL;
