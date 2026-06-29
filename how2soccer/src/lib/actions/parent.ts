'use server'

import { createServerClient } from '../supabase/server'
import { getSession } from '../session'
import { TRACKS, TRACK_IDS } from '../data/curriculum'
import { getLocalDate } from '../utils/date'

export interface KidStats {
  id: string
  name: string
  age: number
  skill_level: string
  streak: { current: number; longest: number; lastDate: string | null; timezone: string }
  totalStars: number
  trackProgress: { id: string; name: string; emoji: string; colorClass: string; completed: number; total: number }[]
  weeklyDates: string[]
  daysSinceLastPractice: number | null
}

export async function getParentDashboard(parentId: string): Promise<KidStats[]> {
  const session = await getSession()
  if (!session.parentId || session.parentId !== parentId) return []

  const supabase = await createServerClient()

  const { data: kids } = await supabase
    .from('h2s_kids')
    .select('*')
    .eq('parent_id', parentId)
    .order('created_at', { ascending: true })

  if (!kids || kids.length === 0) return []

  const kidIds = kids.map((k: { id: string }) => k.id)

  const sevenDaysAgo = (() => {
    const d = new Date()
    d.setDate(d.getDate() - 6)
    return d.toLocaleDateString('en-CA')
  })()

  const [streaksRes, progressRes, missionsRes] = await Promise.all([
    supabase.from('h2s_streaks').select('*').in('kid_id', kidIds),
    supabase
      .from('h2s_progress')
      .select('kid_id, challenge_id, track, completed_at')
      .in('kid_id', kidIds),
    supabase
      .from('h2s_daily_missions')
      .select('kid_id, date')
      .in('kid_id', kidIds)
      .not('completed_at', 'is', null)
      .gte('date', sevenDaysAgo),
  ])

  const streaksByKid = Object.fromEntries(
    (streaksRes.data || []).map((s: any) => [s.kid_id, s])
  ) as Record<string, { current_streak: number; longest_streak: number; last_practice_date: string | null; timezone: string }>

  const progressByKid: Record<string, { track: string }[]> = {}
  for (const p of progressRes.data || []) {
    if (!progressByKid[p.kid_id]) progressByKid[p.kid_id] = []
    progressByKid[p.kid_id].push(p)
  }

  const missionDatesByKid: Record<string, Set<string>> = {}
  for (const m of missionsRes.data || []) {
    if (!missionDatesByKid[m.kid_id]) missionDatesByKid[m.kid_id] = new Set()
    missionDatesByKid[m.kid_id].add(m.date)
  }

  return kids.map((kid: { id: string; name: string; age: number; skill_level: string }) => {
    const streak = streaksByKid[kid.id]
    const progress = progressByKid[kid.id] || []
    const weeklyDates = Array.from(missionDatesByKid[kid.id] || []).sort()

    const completedByTrack: Record<string, number> = {}
    for (const p of progress) {
      completedByTrack[p.track] = (completedByTrack[p.track] || 0) + 1
    }

    const trackProgress = TRACK_IDS.map((id) => ({
      id,
      name: TRACKS[id].name,
      emoji: TRACKS[id].emoji,
      colorClass: TRACKS[id].colorClass,
      completed: completedByTrack[id] || 0,
      total: TRACKS[id].challenges.length,
    }))

    let daysSinceLastPractice: number | null = null
    if (streak?.last_practice_date) {
      const tz = streak.timezone || 'America/New_York'
      const today = getLocalDate(tz)
      const diffMs = new Date(today).getTime() - new Date(streak.last_practice_date).getTime()
      daysSinceLastPractice = Math.floor(diffMs / (1000 * 60 * 60 * 24))
    }

    return {
      id: kid.id,
      name: kid.name,
      age: kid.age,
      skill_level: kid.skill_level,
      streak: {
        current: streak?.current_streak ?? 0,
        longest: streak?.longest_streak ?? 0,
        lastDate: streak?.last_practice_date ?? null,
        timezone: streak?.timezone ?? 'America/New_York',
      },
      totalStars: progress.length,
      trackProgress,
      weeklyDates,
      daysSinceLastPractice,
    }
  })
}
