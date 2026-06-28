'use server'

import { revalidatePath } from 'next/cache'
import { createServerClient } from '../supabase/server'
import { getSession } from '../session'
import { Progress } from '../types'
import { getStreak, updateStreak } from './streaks'
import { completeDailyMission } from './missions'

export async function markChallengeComplete(challengeId: string, track: string) {
  const session = await getSession()
  if (!session.kidId) return { error: 'Not authenticated' }

  const supabase = await createServerClient()

  const { error } = await supabase.from('h2s_progress').upsert(
    { kid_id: session.kidId, challenge_id: challengeId, track, stars: 1 },
    { onConflict: 'kid_id,challenge_id' },
  )

  if (error) return { error: error.message }

  // Resolve timezone from existing streak record (default if none yet)
  const existing = await getStreak(session.kidId)
  const timezone = existing?.timezone ?? 'America/New_York'

  await Promise.all([
    updateStreak(session.kidId, timezone),
    completeDailyMission(session.kidId, challengeId, timezone),
  ])

  revalidatePath(`/skills/${track}`)
  revalidatePath('/home')
  revalidatePath('/')
  return { success: true }
}

export async function getKidProgress(kidId: string): Promise<Progress[]> {
  const supabase = await createServerClient()
  const { data } = await supabase
    .from('h2s_progress')
    .select('*')
    .eq('kid_id', kidId)
    .order('completed_at', { ascending: false })

  return (data as Progress[]) || []
}
