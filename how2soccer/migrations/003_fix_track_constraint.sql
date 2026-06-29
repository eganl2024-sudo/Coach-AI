-- How 2 Soccer — fix h2s_progress track check constraint
-- The original constraint only included the first 4 tracks.
-- Curriculum was expanded to 6 tracks (control, tricks) but the constraint was not updated.
-- Run this in the Supabase SQL editor.

ALTER TABLE h2s_progress DROP CONSTRAINT IF EXISTS h2s_progress_track_check;
ALTER TABLE h2s_progress ADD CONSTRAINT h2s_progress_track_check
  CHECK (track IN ('juggling', 'dribbling', 'passing', 'shooting', 'control', 'tricks'));
