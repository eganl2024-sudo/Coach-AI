import type { Metadata } from 'next'
import { redirect } from 'next/navigation'
import { getSession } from '@/lib/session'
import { getTodaysMissions } from '@/lib/actions/missions'
import { getKidProgress } from '@/lib/actions/progress'
import { getStreak } from '@/lib/actions/streaks'
import { TRACKS } from '@/lib/data/curriculum'
import { PracticeSession } from '@/components/practice/PracticeSession'

export const metadata: Metadata = { title: 'Today\'s Practice' }

export default async function PracticePage() {
  const session = await getSession()
  const [streak, progress] = await Promise.all([
    getStreak(session.kidId!),
    getKidProgress(session.kidId!),
  ])
  const timezone = streak?.timezone ?? 'America/New_York'
  const missions = await getTodaysMissions(session.kidId!, timezone)

  if (missions.length === 0) redirect('/home')

  const progressByChallenge = Object.fromEntries(progress.map((p) => [p.challenge_id, p]))

  const challenges = missions.map((m) => {
    const trackData = TRACKS[m.track as keyof typeof TRACKS]
    const challenge = trackData?.challenges.find((c) => c.id === m.challenge_id)
    return {
      missionId: m.id,
      challengeId: m.challenge_id,
      track: m.track,
      trackName: trackData?.name ?? m.track,
      trackEmoji: trackData?.emoji ?? '⚽',
      trackColorClass: trackData?.colorClass ?? 'text-green-600',
      trackBgClass: trackData?.bgClass ?? 'bg-green-50 border-green-200',
      title: challenge?.title ?? m.challenge_id,
      description: challenge?.description ?? '',
      tip: challenge?.tip ?? '',
      difficulty: (challenge?.difficulty ?? 1) as 1 | 2 | 3,
      alreadyCompleted: !!m.completed_at,
      existingRating: progressByChallenge[m.challenge_id]?.rating ?? null,
    }
  })

  const allDone = challenges.every((c) => c.alreadyCompleted)

  return (
    <PracticeSession
      kidName={session.kidName ?? 'Champ'}
      challenges={challenges}
      currentStreak={streak?.current_streak ?? 0}
      allAlreadyDone={allDone}
    />
  )
}
