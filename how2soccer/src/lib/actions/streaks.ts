'use server'

import { createServerClient } from '../supabase/server'
import { Streak } from '../types'
import { getLocalDate, getLocalYesterday } from '../utils/date'

export async function getStreak(kidId: string): Promise<Streak | null> {
  const supabase = await createServerClient()
  const { data } = await supabase
    .from('h2s_streaks')
    .select('*')
    .eq('kid_id', kidId)
    .maybeSingle()
  return (data as Streak) || null
}

export async function updateStreak(kidId: string, timezone = 'America/New_York'): Promise<Streak> {
  const supabase = await createServerClient()
  const today = getLocalDate(timezone)
  const yesterday = getLocalYesterday(timezone)

  const { data: existing } = await supabase
    .from('h2s_streaks')
    .select('*')
    .eq('kid_id', kidId)
    .maybeSingle()

  const prev = existing as Streak | null

  if (prev?.last_practice_date === today) return prev!

  let current_streak: number
  let longest_streak: number

  if (prev?.last_practice_date === yesterday) {
    current_streak = (prev.current_streak ?? 0) + 1
    longest_streak = Math.max(prev.longest_streak ?? 0, current_streak)
  } else {
    current_streak = 1
    longest_streak = Math.max(prev?.longest_streak ?? 0, 1)
  }

  const { data } = await supabase
    .from('h2s_streaks')
    .upsert(
      {
        kid_id: kidId,
        current_streak,
        longest_streak,
        last_practice_date: today,
        timezone,
        updated_at: new Date().toISOString(),
      },
      { onConflict: 'kid_id' },
    )
    .select('*')
    .single()

  return data as Streak
}
