import type { Metadata } from 'next'
import { getSession } from '@/lib/session'
import { getKidProgress } from '@/lib/actions/progress'
import { TRACKS, TRACK_IDS } from '@/lib/data/curriculum'
import { TrackCard } from '@/components/skills/TrackCard'
import Link from 'next/link'

export const metadata: Metadata = { title: 'Home' }

export default async function HomePage() {
  const session = await getSession()
  const progress = await getKidProgress(session.kidId!)

  const completedIds = new Set(progress.map((p) => p.challenge_id))
  const totalStars = completedIds.size
  const totalChallenges = TRACK_IDS.length * 5

  return (
    <div className="py-6 space-y-6">
      {/* Greeting */}
      <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-3xl p-6 text-white">
        <p className="text-green-100 text-sm font-semibold uppercase tracking-wide">Welcome back</p>
        <h1 className="text-3xl font-black mt-1">{session.kidName}! 👋</h1>
        <p className="text-green-100 mt-1">Ready to practice today?</p>

        <div className="flex items-center gap-3 mt-4 bg-white/20 rounded-2xl px-4 py-3">
          <span className="text-3xl">⭐</span>
          <div>
            <p className="text-2xl font-black">
              {totalStars} {totalStars === 1 ? 'star' : 'stars'} earned
            </p>
            <p className="text-green-100 text-sm">
              {totalChallenges - totalStars} challenge{totalChallenges - totalStars === 1 ? '' : 's'} left to master
            </p>
          </div>
        </div>
      </div>

      {/* Track progress */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-2xl font-black text-gray-900">Your Skills</h2>
          <Link href="/skills" className="text-green-600 font-semibold text-sm hover:underline py-2 px-1">
            See all →
          </Link>
        </div>

        <div className="grid grid-cols-1 gap-3">
          {TRACK_IDS.map((trackId) => {
            const track = TRACKS[trackId]
            const completedCount = track.challenges.filter((c) => completedIds.has(c.id)).length
            return <TrackCard key={trackId} track={track} completedCount={completedCount} />
          })}
        </div>
      </div>
    </div>
  )
}
