-- How 2 Soccer — streaks & daily missions
-- Run in Supabase SQL editor after 001_how2soccer_tables.sql

CREATE TABLE IF NOT EXISTS h2s_streaks (
  id                 UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  kid_id             UUID        UNIQUE NOT NULL REFERENCES h2s_kids(id) ON DELETE CASCADE,
  current_streak     INTEGER     NOT NULL DEFAULT 0,
  longest_streak     INTEGER     NOT NULL DEFAULT 0,
  last_practice_date DATE,
  timezone           TEXT        NOT NULL DEFAULT 'America/New_York',
  updated_at         TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS h2s_daily_missions (
  id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  kid_id       UUID        NOT NULL REFERENCES h2s_kids(id) ON DELETE CASCADE,
  challenge_id TEXT        NOT NULL,
  track        TEXT        NOT NULL,
  date         DATE        NOT NULL,
  completed_at TIMESTAMPTZ,
  UNIQUE (kid_id, challenge_id, date)
);

CREATE INDEX IF NOT EXISTS idx_h2s_streaks_kid        ON h2s_streaks(kid_id);
CREATE INDEX IF NOT EXISTS idx_h2s_missions_kid_date  ON h2s_daily_missions(kid_id, date);

ALTER TABLE h2s_streaks        ENABLE ROW LEVEL SECURITY;
ALTER TABLE h2s_daily_missions ENABLE ROW LEVEL SECURITY;
