'use server'

import { createServerClient } from '../supabase/server'
import { TRACKS, TRACK_IDS } from '../data/curriculum'
import { DailyMission } from '../types'
import { getLocalDate } from '../utils/date'

export async function getTodaysMissions(kidId: string, timezone = 'America/New_York'): Promise<DailyMission[]> {
  const supabase = await createServerClient()
  const today = getLocalDate(timezone)

  const { data: existing, error: fetchError } = await supabase
    .from('h2s_daily_missions')
    .select('*')
    .eq('kid_id', kidId)
    .eq('date', today)

  if (fetchError || !existing) return []
  if (existing.length > 0) return existing as DailyMission[]

  // Get progress with ratings to drive smart mission selection
  const { data: progress } = await supabase
    .from('h2s_progress')
    .select('challenge_id, rating')
    .eq('kid_id', kidId)

  // 'tough' rated = needs more practice → resurface in rotation
  // everything else (no rating, 'easy', 'got_it') = mastered → skip
  const masteredIds = new Set(
    (progress || []).filter((p: any) => p.rating !== 'tough').map((p: any) => p.challenge_id)
  )
  const toughIds = new Set(
    (progress || []).filter((p: any) => p.rating === 'tough').map((p: any) => p.challenge_id)
  )

  const shuffled = [...TRACK_IDS].sort(() => Math.random() - 0.5)
  const picks: Array<{ challenge_id: string; track: string }> = []

  // Priority 1: one tough-rated challenge per track (kid flagged these as hard)
  for (const trackId of shuffled) {
    if (picks.length >= 3) break
    const tough = TRACKS[trackId].challenges.find((c) => toughIds.has(c.id))
    if (tough) picks.push({ challenge_id: tough.id, track: trackId })
  }

  // Priority 2: one new (never attempted) challenge per track
  for (const trackId of shuffled) {
    if (picks.length >= 3) break
    const fresh = TRACKS[trackId].challenges.find(
      (c) => !masteredIds.has(c.id) && !toughIds.has(c.id) && !picks.some((p) => p.challenge_id === c.id)
    )
    if (fresh) picks.push({ challenge_id: fresh.id, track: trackId })
  }

  // Fallback: fill from any track if still short
  if (picks.length < 3) {
    for (const trackId of shuffled) {
      for (const challenge of TRACKS[trackId].challenges) {
        if (picks.length >= 3) break
        if (!picks.some((p) => p.challenge_id === challenge.id)) {
          picks.push({ challenge_id: challenge.id, track: trackId })
        }
      }
      if (picks.length >= 3) break
    }
  }

  const rows = picks.map((p) => ({ kid_id: kidId, challenge_id: p.challenge_id, track: p.track, date: today }))

  const { data: inserted, error: insertError } = await supabase
    .from('h2s_daily_missions')
    .insert(rows)
    .select('*')

  return insertError ? [] : (inserted as DailyMission[]) || []
}

export async function completeDailyMission(kidId: string, challengeId: string, timezone = 'America/New_York') {
  const supabase = await createServerClient()
  const today = getLocalDate(timezone)

  await supabase
    .from('h2s_daily_missions')
    .update({ completed_at: new Date().toISOString() })
    .eq('kid_id', kidId)
    .eq('challenge_id', challengeId)
    .eq('date', today)
}
