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

  if (fetchError) console.error('[missions] fetch error:', fetchError)
  if (existing && existing.length > 0) return existing as DailyMission[]

  // Build pool of incomplete challenges first
  const { data: progress } = await supabase
    .from('h2s_progress')
    .select('challenge_id')
    .eq('kid_id', kidId)

  const completedIds = new Set((progress || []).map((p: { challenge_id: string }) => p.challenge_id))

  // Shuffle track order for variety
  const shuffled = [...TRACK_IDS].sort(() => Math.random() - 0.5)

  const picks: Array<{ challenge_id: string; track: string }> = []

  // One incomplete challenge per track, up to 3
  for (const trackId of shuffled) {
    if (picks.length >= 3) break
    const incomplete = TRACKS[trackId].challenges.find((c) => !completedIds.has(c.id))
    if (incomplete) picks.push({ challenge_id: incomplete.id, track: trackId })
  }

  // If still need more (kid finished some tracks), fill from any track
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

  if (insertError) console.error('[missions] insert error:', insertError)

  return (inserted as DailyMission[]) || []
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
