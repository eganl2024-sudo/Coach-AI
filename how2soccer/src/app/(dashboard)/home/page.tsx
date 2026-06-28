import type { Metadata } from 'next'
import Link from 'next/link'
import { getSession } from '@/lib/session'
import { getKidProgress } from '@/lib/actions/progress'
import { getStreak } from '@/lib/actions/streaks'
import { getTodaysMissions } from '@/lib/actions/missions'
import { TRACKS, TRACK_IDS } from '@/lib/data/curriculum'
import { TrackCard } from '@/components/skills/TrackCard'
import { StreakBanner } from '@/components/home/StreakBanner'
import { MissionCard } from '@/components/home/MissionCard'

export const metadata: Metadata = { title: 'Home' }

export default async function HomePage() {
  const session = await getSession()
  const [progress, streak] = await Promise.all([
    getKidProgress(session.kidId!),
    getStreak(session.kidId!),
  ])
  const missions = await getTodaysMissions(session.kidId!, streak?.timezone ?? 'America/New_York')

  const completedIds = new Set(progress.map((p) => p.challenge_id))
  const totalStars = completedIds.size
  const totalChallenges = TRACK_IDS.reduce((sum, id) => sum + TRACKS[id].challenges.length, 0)
  const missionsLeft = missions.filter((m) => !m.completed_at).length

  return (
    <div className="py-6 space-y-5">
      {/* Greeting hero */}
      <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-3xl p-6 text-white">
        <p className="text-green-100 text-sm font-semibold uppercase tracking-wide">Welcome back</p>
        <h1 className="text-3xl font-black mt-1">{session.kidName}! 👋</h1>
        <p className="text-green-100 mt-1">
          {missionsLeft === 0
            ? "Amazing — today's practice done! 🎉"
            : `${missionsLeft} practice drill${missionsLeft === 1 ? '' : 's'} waiting for you today`}
        </p>

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

      {/* Streak */}
      <StreakBanner streak={streak} />

      {/* Today's Practice */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xl font-black text-gray-900">Today&apos;s Practice</h2>
          {missionsLeft === 0 && (
            <span className="text-xs font-bold text-green-600 bg-green-100 px-2 py-1 rounded-full">All done!</span>
          )}
        </div>

        {missions.length > 0 ? (
          <div className="space-y-3">
            {missions.map((mission) => {
              const challenge = TRACKS[mission.track as keyof typeof TRACKS]?.challenges.find(
                (c) => c.id === mission.challenge_id,
              )
              const trackData = TRACKS[mission.track as keyof typeof TRACKS]
              if (!challenge || !trackData) return null
              return (
                <MissionCard
                  key={mission.id}
                  mission={mission}
                  challenge={challenge}
                  trackData={trackData}
                />
              )
            })}
          </div>
        ) : (
          <div className="bg-white rounded-2xl border-2 border-gray-100 p-4 text-center text-gray-400 text-sm">
            Loading your missions…
          </div>
        )}
      </div>

      {/* Track progress */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xl font-black text-gray-900">Your Skills</h2>
          <Link href="/skills" className="text-green-600 font-semibold text-sm hover:underline min-w-[52px] text-right py-2">
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
