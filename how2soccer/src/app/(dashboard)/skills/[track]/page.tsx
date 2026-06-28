import type { Metadata } from 'next'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { ArrowLeft } from 'lucide-react'
import { getSession } from '@/lib/session'
import { getKidProgress } from '@/lib/actions/progress'
import { getTrack } from '@/lib/data/curriculum'
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

export default async function TrackPage({ params }: Props) {
  const { track } = await params
  const trackData = getTrack(track)
  if (!trackData) notFound()

  const session = await getSession()
  const progress = await getKidProgress(session.kidId!)
  const completedIds = new Set(progress.map((p) => p.challenge_id))
  const completedCount = trackData.challenges.filter((c) => completedIds.has(c.id)).length

  return (
    <div className="py-6 space-y-4">
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
        <p className={cn('font-black text-lg mt-1', trackData.colorClass)}>
          {completedCount}/5 completed
        </p>
      </div>

      <div className="space-y-3">
        {trackData.challenges.map((challenge, i) => (
          <ChallengeCard
            key={challenge.id}
            challenge={challenge}
            trackId={track}
            index={i}
            isCompleted={completedIds.has(challenge.id)}
          />
        ))}
      </div>
    </div>
  )
}
