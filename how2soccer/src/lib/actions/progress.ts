'use server'

import { revalidatePath } from 'next/cache'
import { createServerClient } from '../supabase/server'
import { getSession } from '../session'
import { Progress } from '../types'
import { getStreak, updateStreak } from './streaks'
import { completeDailyMission } from './missions'
import { getTrack, getUnlockedChallengeIds } from '../data/curriculum'
import { getLocalDate } from '../utils/date'

export interface UnlockInfo {
  tier: 2 | 3
  tierName: 'Intermediate' | 'Advanced'
  trackName: string
  trackEmoji: string
  newChallengeCount: number
}

export interface TrackCompleteInfo {
  trackName: string
  trackEmoji: string
  totalChallenges: number
}

export async function markChallengeComplete(challengeId: string, track: string): Promise<
  { success: true; unlockInfo: UnlockInfo | null; trackComplete: TrackCompleteInfo | null } | { error: string }
> {
  const session = await getSession()
  if (!session.kidId) return { error: 'Not authenticated' }

  const supabase = await createServerClient()

  // Fetch current progress for unlock detection
  const { data: currentProgress } = await supabase
    .from('h2s_progress')
    .select('challenge_id')
    .eq('kid_id', session.kidId)

  const alreadyDone = (currentProgress || []).some((p: any) => p.challenge_id === challengeId)

  // Compute unlock delta and track completion before saving
  let unlockInfo: UnlockInfo | null = null
  let trackComplete: TrackCompleteInfo | null = null
  if (!alreadyDone) {
    const trackData = getTrack(track)
    if (trackData) {
      const completedBefore = new Set((currentProgress || []).map((p: any) => p.challenge_id))
      const completedAfter = new Set([...completedBefore, challengeId])

      // Track complete check (all challenges done)
      const wasComplete = trackData.challenges.every((c) => completedBefore.has(c.id))
      const nowComplete = trackData.challenges.every((c) => completedAfter.has(c.id))
      if (!wasComplete && nowComplete) {
        trackComplete = {
          trackName: trackData.name,
          trackEmoji: trackData.emoji,
          totalChallenges: trackData.challenges.length,
        }
      }

      // Tier unlock check (only if track isn't fully done — they're mutually exclusive)
      if (!trackComplete) {
        const unlockedBefore = getUnlockedChallengeIds(trackData, completedBefore)
        const unlockedAfter = getUnlockedChallengeIds(trackData, completedAfter)
        if (unlockedAfter.size > unlockedBefore.size) {
          const newlyUnlocked = [...unlockedAfter].filter((id) => !unlockedBefore.has(id))
          const firstNew = trackData.challenges.find((c) => newlyUnlocked.includes(c.id))
          if (firstNew && firstNew.difficulty > 1) {
            const tier = firstNew.difficulty as 2 | 3
            unlockInfo = {
              tier,
              tierName: tier === 2 ? 'Intermediate' : 'Advanced',
              trackName: trackData.name,
              trackEmoji: trackData.emoji,
              newChallengeCount: newlyUnlocked.length,
            }
          }
        }
      }
    }
  }

  const { error } = await supabase.from('h2s_progress').upsert(
    { kid_id: session.kidId, challenge_id: challengeId, track, stars: 1 },
    { onConflict: 'kid_id,challenge_id' },
  )

  if (error) return { error: error.message }

  const existing = await getStreak(session.kidId)
  const timezone = existing?.timezone ?? 'America/New_York'

  await Promise.all([
    updateStreak(session.kidId, timezone),
    completeDailyMission(session.kidId, challengeId, timezone),
  ])

  revalidatePath(`/skills/${track}`)
  revalidatePath('/home')
  revalidatePath('/')
  return { success: true, unlockInfo, trackComplete }
}

export async function saveRating(challengeId: string, track: string, rating: 'easy' | 'got_it' | 'tough') {
  const session = await getSession()
  if (!session.kidId) return { error: 'Not authenticated' }

  const supabase = await createServerClient()
  const { error } = await supabase
    .from('h2s_progress')
    .update({ rating })
    .eq('kid_id', session.kidId)
    .eq('challenge_id', challengeId)

  if (error) return { error: error.message }
  revalidatePath('/home')
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

export async function getWeekActivity(kidId: string, timezone = 'America/New_York') {
  const supabase = await createServerClient()
  const today = getLocalDate(timezone)

  const days: string[] = []
  for (let i = 6; i >= 0; i--) {
    const d = new Date(today + 'T12:00:00')
    d.setDate(d.getDate() - i)
    days.push(d.toISOString().split('T')[0])
  }

  const { data } = await supabase
    .from('h2s_daily_missions')
    .select('date')
    .eq('kid_id', kidId)
    .gte('date', days[0])
    .not('completed_at', 'is', null)

  const activeDates = new Set((data || []).map((m: any) => m.date))

  return days.map((date) => ({
    date,
    active: activeDates.has(date),
    isToday: date === today,
  }))
}
