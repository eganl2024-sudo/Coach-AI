-- ============================================================
-- Migration: add gender column to programs table
-- Run in Supabase SQL Editor BEFORE importing women's data
-- ============================================================

-- 1. Add gender column (all existing rows → 'M')
ALTER TABLE programs
  ADD COLUMN IF NOT EXISTS gender TEXT NOT NULL DEFAULT 'M'
  CHECK (gender IN ('M', 'W'));

-- 2. Drop the old unique constraint on school_name alone
ALTER TABLE programs
  DROP CONSTRAINT IF EXISTS programs_school_name_key;

-- 3. Composite unique: same school can have one M and one W program
ALTER TABLE programs
  ADD CONSTRAINT programs_school_name_gender_key UNIQUE (school_name, gender);

-- 4. Index for the gender filter on the recruiting page
CREATE INDEX IF NOT EXISTS idx_programs_gender ON programs(gender);

-- 5. Rebuild view to expose gender column
DROP VIEW IF EXISTS v_coaches_with_program;
CREATE VIEW v_coaches_with_program AS
SELECT
  p.program_id,
  p.school_name,
  p.conference,
  p.region,
  p.state,
  p.division,
  p.gender,
  p.program_url,
  c.coach_id,
  c.first_name,
  c.last_name,
  c.title,
  c.email,
  c.phone,
  c.position_focus,
  c.source,
  c.verified_at
FROM programs p
JOIN coaches c ON c.program_id = p.program_id
ORDER BY
  p.school_name,
  CASE c.title WHEN 'Head Coach' THEN 0 WHEN 'Assistant Coach' THEN 1 ELSE 2 END,
  c.last_name;
