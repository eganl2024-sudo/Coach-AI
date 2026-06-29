import type { Metadata } from 'next'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { ArrowLeft } from 'lucide-react'
import { getSession } from '@/lib/session'
import { getKidProgress } from '@/lib/actions/progress'
import { getTrack, getUnlockedChallengeIds } from '@/lib/data/curriculum'
import { ChallengeCard } from '@/components/skills/ChallengeCard'
import { cn } from '@/lib/utils'

interface Props {
  params: Promise<{ track: string }>
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { track } = await params
  const trackData = getTrack(track)
  return { title: trackData?.name ?? 'Track' }
}

const TIER_CONFIG = [
  { diff: 1 as const, label: '🌱 Beginner', unlockNote: null },
  { diff: 2 as const, label: '⚡ Intermediate', unlockNote: 'Complete all Beginner to unlock' },
  { diff: 3 as const, label: '🔥 Advanced', unlockNote: 'Complete all Intermediate to unlock' },
]

export default async function TrackPage({ params }: Props) {
  const { track } = await params
  const trackData = getTrack(track)
  if (!trackData) notFound()

  const session = await getSession()
  const progress = await getKidProgress(session.kidId!)
  const completedIds = new Set(progress.map((p) => p.challenge_id))
  const unlockedIds = getUnlockedChallengeIds(trackData, completedIds)
  const completedCount = trackData.challenges.filter((c) => completedIds.has(c.id)).length

  const tiers = TIER_CONFIG.map(({ diff, label, unlockNote }) => {
    const challenges = trackData.challenges.filter((c) => c.difficulty === diff)
    const isUnlocked = challenges.every((c) => unlockedIds.has(c.id))
    return { diff, label, unlockNote, challenges, isUnlocked }
  })

  return (
    <div className="py-6 space-y-5">
      <div className="flex items-center gap-2">
        <Link
          href="/skills"
          className="flex items-center justify-center w-9 h-9 rounded-xl text-gray-500 hover:bg-gray-100 transition-colors shrink-0"
        >
          <ArrowLeft size={20} />
        </Link>
        <h1 className="text-xl font-black text-gray-900">
          {trackData.emoji} {trackData.name}
        </h1>
      </div>

      <div className={cn('rounded-2xl border-2 p-4', trackData.bgClass)}>
        <p className="text-gray-600 text-sm">{trackData.description}</p>
        <p className="font-black text-lg mt-1 text-gray-900">
          {completedCount}/{trackData.challenges.length} completed
        </p>
      </div>

      {tiers.map(({ diff, label, unlockNote, challenges, isUnlocked }) => (
        <div key={diff} className="space-y-2">
          <div className="flex items-center justify-between">
            <h2 className={cn('text-sm font-black uppercase tracking-wide', isUnlocked ? 'text-gray-700' : 'text-gray-400')}>
              {label}
            </h2>
            {!isUnlocked && unlockNote ? (
              <span className="text-xs text-gray-400 font-medium">{unlockNote}</span>
            ) : (
              <span className="text-xs text-gray-400">
                {challenges.filter((c) => completedIds.has(c.id)).length}/{challenges.length}
              </span>
            )}
          </div>
          <div className="space-y-2">
            {challenges.map((challenge, i) => (
              <ChallengeCard
                key={challenge.id}
                challenge={challenge}
                trackId={track}
                index={i}
                isCompleted={completedIds.has(challenge.id)}
                isLocked={!unlockedIds.has(challenge.id)}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
