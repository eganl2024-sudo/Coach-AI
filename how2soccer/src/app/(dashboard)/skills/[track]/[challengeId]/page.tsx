import type { Metadata } from 'next'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { ArrowLeft } from 'lucide-react'
import { getSession } from '@/lib/session'
import { getKidProgress } from '@/lib/actions/progress'
import { getChallenge, getTrack, getUnlockedChallengeIds } from '@/lib/data/curriculum'
import { ChallengeDetail } from '@/components/skills/ChallengeDetail'
import { cn } from '@/lib/utils'

interface Props {
  params: Promise<{ track: string; challengeId: string }>
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { track, challengeId } = await params
  const challenge = getChallenge(track, challengeId)
  return { title: challenge?.title ?? 'Challenge' }
}

export default async function ChallengePage({ params }: Props) {
  const { track, challengeId } = await params
  const challenge = getChallenge(track, challengeId)
  const trackData = getTrack(track)
  if (!challenge || !trackData) notFound()

  const session = await getSession()
  const progress = await getKidProgress(session.kidId!)
  const completedIds = new Set(progress.map((p) => p.challenge_id))
  const unlockedIds = getUnlockedChallengeIds(trackData, completedIds)

  const isLocked = !unlockedIds.has(challengeId)
  const progressEntry = progress.find((p) => p.challenge_id === challengeId)
  const isCompleted = !!progressEntry
  const existingRating = progressEntry?.rating ?? null

  if (isLocked) {
    const tierName = challenge.difficulty === 1 ? 'Beginner' : challenge.difficulty === 2 ? 'Intermediate' : 'Advanced'
    const prevTierName = challenge.difficulty === 3 ? 'Intermediate' : 'Beginner'
    return (
      <div className="py-6 space-y-4">
        <div className="flex items-center gap-2">
          <Link
            href={`/skills/${track}`}
            className="flex items-center justify-center w-9 h-9 rounded-xl text-gray-500 hover:bg-gray-100 transition-colors shrink-0"
          >
            <ArrowLeft size={20} />
          </Link>
          <h1 className="text-xl font-black text-gray-900">
            {trackData.emoji} {trackData.name}
          </h1>
        </div>

        <div className={cn('rounded-3xl border-2 p-8 text-center', trackData.bgClass)}>
          <div className="text-5xl mb-4">🔒</div>
          <h2 className={cn('text-2xl font-black mb-2', trackData.colorClass)}>{challenge.title}</h2>
          <p className="text-gray-600 mb-1">This is a <strong>{tierName}</strong> challenge.</p>
          <p className="text-gray-500 text-sm">
            Complete all <strong>{prevTierName}</strong> challenges in {trackData.name} to unlock this one!
          </p>
        </div>

        <Link
          href={`/skills/${track}`}
          className="block w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold text-center py-4 rounded-2xl transition-colors"
        >
          ← Back to {trackData.name}
        </Link>
      </div>
    )
  }

  return (
    <div className="py-6 space-y-4">
      <div className="flex items-center gap-2">
        <Link
          href={`/skills/${track}`}
          className="flex items-center justify-center w-9 h-9 rounded-xl text-gray-500 hover:bg-gray-100 transition-colors shrink-0"
        >
          <ArrowLeft size={20} />
        </Link>
        <h1 className="text-xl font-black text-gray-900">
          {trackData.emoji} {trackData.name}
        </h1>
      </div>
      <ChallengeDetail
        challenge={challenge}
        track={track}
        isCompleted={isCompleted}
        existingRating={existingRating}
        trackData={trackData}
      />
    </div>
  )
}
