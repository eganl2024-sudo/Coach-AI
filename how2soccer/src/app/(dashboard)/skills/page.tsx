import type { Metadata } from 'next'
import { getSession } from '@/lib/session'
import { getKidProgress } from '@/lib/actions/progress'
import { TRACKS, TRACK_IDS } from '@/lib/data/curriculum'
import { TrackCard } from '@/components/skills/TrackCard'

export const metadata: Metadata = { title: 'Skills' }

export default async function SkillsPage() {
  const session = await getSession()
  const progress = await getKidProgress(session.kidId!)
  const completedIds = new Set(progress.map((p) => p.challenge_id))

  return (
    <div className="py-6 space-y-4">
      <div>
        <h1 className="text-2xl font-black text-gray-900">Pick a Skill</h1>
        <p className="text-gray-500 mt-1">Tap a track to start practicing!</p>
      </div>

      <div className="space-y-3">
        {TRACK_IDS.map((trackId) => {
          const track = TRACKS[trackId]
          const completedCount = track.challenges.filter((c) => completedIds.has(c.id)).length
          return <TrackCard key={trackId} track={track} completedCount={completedCount} />
        })}
      </div>

      <div className="bg-white rounded-2xl border-2 border-gray-100 p-4 text-center">
        <p className="text-gray-500 text-sm">
          Complete all {TRACK_IDS.reduce((sum, id) => sum + TRACKS[id].challenges.length, 0)} challenges to become a{' '}
          <span className="font-bold text-yellow-500">⭐ Soccer Star!</span>
        </p>
      </div>
    </div>
  )
}
