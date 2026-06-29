import type { Metadata } from 'next'
import Link from 'next/link'
import { getSession } from '@/lib/session'
import { getKidProgress, getWeekActivity } from '@/lib/actions/progress'
import { getStreak } from '@/lib/actions/streaks'
import { getTodaysMissions } from '@/lib/actions/missions'
import { TRACKS, TRACK_IDS } from '@/lib/data/curriculum'
import { getLevel } from '@/lib/utils/levels'
import { TrackCard } from '@/components/skills/TrackCard'
import { StreakBanner } from '@/components/home/StreakBanner'
import { WeeklyStrip } from '@/components/home/WeeklyStrip'
import { MissionCard } from '@/components/home/MissionCard'

export const metadata: Metadata = { title: 'Home' }

export default async function HomePage() {
  const session = await getSession()
  // Flatten 3-waterfall to 2: pass safe default TZ for missions/activity;
  // streak.timezone corrects it for non-ET users on next session.
  const DEFAULT_TZ = 'America/New_York'
  const [progress, streak, missions, weekActivity] = await Promise.all([
    getKidProgress(session.kidId!),
    getStreak(session.kidId!),
    getTodaysMissions(session.kidId!, DEFAULT_TZ),
    getWeekActivity(session.kidId!, DEFAULT_TZ),
  ])

  const completedIds = new Set(progress.map((p) => p.challenge_id))
  const totalStars = completedIds.size
  const totalChallenges = TRACK_IDS.reduce((sum, id) => sum + TRACKS[id].challenges.length, 0)
  const missionsLeft = missions.filter((m) => !m.completed_at).length
  const level = getLevel(totalStars)

  return (
    <div className="py-6 space-y-5">
      {/* Greeting hero */}
      <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-3xl p-6 text-white">
        <p className="text-green-200 text-xs font-bold uppercase tracking-widest">Hey {session.kidName}!</p>
        <h1 className="text-3xl font-black mt-0.5">
          {missionsLeft === 0 ? 'All Done Today!' : 'Time to Practice'}
        </h1>
        <p className="text-green-100 text-sm mt-1">
          {missionsLeft === 0
            ? 'Amazing work — come back tomorrow!'
            : `${missionsLeft} challenge${missionsLeft === 1 ? '' : 's'} waiting for you`}
        </p>

        {/* Level card */}
        <div className="mt-4 bg-white/20 rounded-2xl px-4 py-3 space-y-2">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2 min-w-0">
              <span className="text-2xl shrink-0">{level.emoji}</span>
              <div className="min-w-0">
                <p className="text-lg font-black leading-none truncate">{level.name}</p>
                <p className="text-green-100 text-xs mt-0.5">{totalStars} star{totalStars === 1 ? '' : 's'} earned</p>
              </div>
            </div>
            {level.nextLevel ? (
              <div className="text-right shrink-0">
                <p className="text-xs text-green-200 font-semibold whitespace-nowrap">
                  {level.starsToNext} to {level.nextLevel.name}
                </p>
                <p className="text-xs text-green-100 whitespace-nowrap">{totalChallenges - totalStars} left</p>
              </div>
            ) : (
              <span className="text-2xl shrink-0">👑</span>
            )}
          </div>
          <div className="h-2 bg-white/20 rounded-full overflow-hidden">
            <div
              className="h-full bg-white rounded-full transition-all duration-700"
              style={{ width: `${level.pct}%` }}
            />
          </div>
        </div>
      </div>

      {/* Streak */}
      <StreakBanner streak={streak} />

      {/* Weekly activity */}
      <WeeklyStrip days={weekActivity} />

      {/* Today's Practice */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xl font-black text-gray-900">Today&apos;s Practice</h2>
          {missionsLeft === 0 && (
            <span className="text-xs font-bold text-green-600 bg-green-100 px-2 py-1 rounded-full">All done!</span>
          )}
        </div>

        {missionsLeft > 0 && (
          <Link
            href="/practice"
            className="flex items-center justify-between w-full bg-green-500 hover:bg-green-600 active:scale-[0.99] text-white font-black text-lg px-5 py-4 rounded-2xl mb-3 transition-all shadow-md shadow-green-200"
          >
            <span>Start Today&apos;s Practice</span>
            <span className="text-green-200 text-sm font-semibold">~{missionsLeft * 5} min</span>
          </Link>
        )}

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
