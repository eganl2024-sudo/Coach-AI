-- How 2 Soccer — initial schema
-- Run this in the Supabase SQL editor for your project

CREATE TABLE IF NOT EXISTS h2s_parents (
  id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  username      TEXT        UNIQUE NOT NULL,
  email         TEXT        UNIQUE NOT NULL,
  password_hash TEXT        NOT NULL,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS h2s_kids (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  parent_id   UUID        NOT NULL REFERENCES h2s_parents(id) ON DELETE CASCADE,
  name        TEXT        NOT NULL,
  age         INTEGER     NOT NULL CHECK (age >= 4 AND age <= 13),
  skill_level TEXT        NOT NULL DEFAULT 'beginner'
                          CHECK (skill_level IN ('beginner', 'intermediate', 'advanced')),
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS h2s_progress (
  id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  kid_id       UUID        NOT NULL REFERENCES h2s_kids(id) ON DELETE CASCADE,
  challenge_id TEXT        NOT NULL,
  track        TEXT        NOT NULL CHECK (track IN ('juggling', 'dribbling', 'passing', 'shooting')),
  completed_at TIMESTAMPTZ DEFAULT NOW(),
  stars        INTEGER     NOT NULL DEFAULT 1 CHECK (stars >= 1 AND stars <= 3),
  UNIQUE (kid_id, challenge_id)
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_h2s_kids_parent     ON h2s_kids(parent_id);
CREATE INDEX IF NOT EXISTS idx_h2s_progress_kid    ON h2s_progress(kid_id);

-- RLS: enable but allow service-role full access (all ops go through server actions)
ALTER TABLE h2s_parents  ENABLE ROW LEVEL SECURITY;
ALTER TABLE h2s_kids     ENABLE ROW LEVEL SECURITY;
ALTER TABLE h2s_progress ENABLE ROW LEVEL SECURITY;
