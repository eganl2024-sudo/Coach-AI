import type { Metadata } from 'next'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { ArrowLeft } from 'lucide-react'
import { getSession } from '@/lib/session'
import { getKidProgress } from '@/lib/actions/progress'
import { getChallenge, getTrack } from '@/lib/data/curriculum'
import { ChallengeDetail } from '@/components/skills/ChallengeDetail'

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
  const progressEntry = progress.find((p) => p.challenge_id === challengeId)
  const isCompleted = !!progressEntry
  const existingRating = progressEntry?.rating ?? null

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
