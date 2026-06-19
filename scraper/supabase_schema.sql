-- ============================================================
-- Coach AI — Recruiting Database Schema
-- Run this in Supabase SQL Editor before importing data
-- ============================================================

-- Programs table (one row per NCAA D1 men's soccer program)
CREATE TABLE IF NOT EXISTS programs (
  program_id    TEXT PRIMARY KEY,          -- slug: school_name lowercased, spaces→dashes
  school_name   TEXT NOT NULL UNIQUE,
  conference    TEXT NOT NULL DEFAULT '',
  region        TEXT NOT NULL DEFAULT '',
  state         TEXT NOT NULL DEFAULT '',
  division      TEXT NOT NULL DEFAULT 'D1',
  program_url   TEXT,
  ncaa_id       TEXT,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Coaches table (many per program)
CREATE TABLE IF NOT EXISTS coaches (
  coach_id        TEXT PRIMARY KEY,         -- slug: school + first + last
  program_id      TEXT NOT NULL REFERENCES programs(program_id) ON DELETE CASCADE,
  school_name     TEXT NOT NULL,            -- denormalized for simpler queries
  first_name      TEXT NOT NULL DEFAULT '',
  last_name       TEXT NOT NULL DEFAULT '',
  title           TEXT NOT NULL CHECK (title IN ('Head Coach','Assistant Coach','Director of Operations')),
  email           TEXT,
  phone           TEXT,
  position_focus  TEXT,
  twitter_handle  TEXT,
  source          TEXT NOT NULL DEFAULT 'scrape',
  verified_at     TIMESTAMPTZ,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for the recruiting page filter queries
CREATE INDEX IF NOT EXISTS idx_coaches_program_id   ON coaches(program_id);
CREATE INDEX IF NOT EXISTS idx_coaches_school_name  ON coaches(school_name);
CREATE INDEX IF NOT EXISTS idx_coaches_title        ON coaches(title);
CREATE INDEX IF NOT EXISTS idx_programs_conference  ON programs(conference);
CREATE INDEX IF NOT EXISTS idx_programs_region      ON programs(region);
CREATE INDEX IF NOT EXISTS idx_programs_state       ON programs(state);

-- View used by the recruiting page (v_coaches_with_program)
-- Joins coaches with their program metadata in one flat row per coach
DROP VIEW IF EXISTS v_coaches_with_program;
CREATE VIEW v_coaches_with_program AS
SELECT
  p.program_id,
  p.school_name,
  p.conference,
  p.region,
  p.state,
  p.division,
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
ORDER BY p.school_name,
         CASE c.title WHEN 'Head Coach' THEN 0 WHEN 'Assistant Coach' THEN 1 ELSE 2 END,
         c.last_name;

-- Row Level Security — data is read-only for all authenticated users
ALTER TABLE programs ENABLE ROW LEVEL SECURITY;
ALTER TABLE coaches  ENABLE ROW LEVEL SECURITY;

-- Any authenticated user can read (needed for the recruiting page)
CREATE POLICY "programs_read" ON programs FOR SELECT TO authenticated USING (true);
CREATE POLICY "coaches_read"  ON coaches  FOR SELECT TO authenticated USING (true);

-- Only service role can write (imports, admin updates)
-- No INSERT/UPDATE/DELETE policies → only service_role key can mutate
