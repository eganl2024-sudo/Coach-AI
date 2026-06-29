import type { Metadata } from 'next'
import { getSession } from '@/lib/session'
import { getKidProgress } from '@/lib/actions/progress'
import { TRACK_IDS, TRACKS } from '@/lib/data/curriculum'
import { getLevel } from '@/lib/utils/levels'
import { logoutAction } from '@/lib/actions/auth'
import { Button } from '@/components/ui/button'

export const metadata: Metadata = { title: 'Profile' }

const TRACK_BAR_COLORS: Record<string, string> = {
  'text-green-600': 'bg-green-500',
  'text-orange-600': 'bg-orange-500',
  'text-blue-600': 'bg-blue-500',
  'text-red-600': 'bg-red-500',
  'text-purple-600': 'bg-purple-500',
  'text-pink-600': 'bg-pink-500',
}

export default async function ProfilePage() {
  const session = await getSession()
  const progress = await getKidProgress(session.kidId!)
  const completedIds = new Set(progress.map((p) => p.challenge_id))
  const totalChallenges = TRACK_IDS.reduce((sum, id) => sum + TRACKS[id].challenges.length, 0)
  const totalStars = completedIds.size
  const level = getLevel(totalStars)

  return (
    <div className="py-6 space-y-4">
      <h1 className="text-2xl font-black text-gray-900">Profile</h1>

      {/* Kid info */}
      <div className="bg-white rounded-2xl border-2 border-gray-200 p-5">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center text-3xl">
            ⚽
          </div>
          <div>
            <p className="text-xl font-black text-gray-900">{session.kidName}</p>
            <p className="text-gray-500 text-sm">Parent: @{session.parentUsername}</p>
          </div>
        </div>
      </div>

      {/* Level card */}
      <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-2xl p-5 text-white">
        <div className="flex items-center justify-between gap-2 mb-3">
          <div className="min-w-0">
            <p className="text-xs text-green-200 font-semibold uppercase tracking-wide">Current Level</p>
            <p className="text-3xl font-black flex items-center gap-2 mt-0.5 truncate">
              {level.emoji} {level.name}
            </p>
          </div>
          {level.nextLevel ? (
            <div className="text-right shrink-0">
              <p className="text-xs text-green-200 whitespace-nowrap">Next level</p>
              <p className="text-lg font-black whitespace-nowrap">{level.nextLevel.emoji} {level.nextLevel.name}</p>
              <p className="text-xs text-green-100 whitespace-nowrap">{level.starsToNext} stars away</p>
            </div>
          ) : (
            <div className="text-4xl shrink-0">👑</div>
          )}
        </div>
        <div className="h-3 bg-white/20 rounded-full overflow-hidden">
          <div
            className="h-full bg-white rounded-full transition-all duration-700"
            style={{ width: `${level.pct}%` }}
          />
        </div>
        {level.nextLevel && (
          <p className="text-xs text-green-100 mt-1.5 text-right">{level.pct}% to {level.nextLevel.name}</p>
        )}
      </div>

      {/* Stats */}
      <div className="bg-white rounded-2xl border-2 border-gray-200 p-5">
        <h2 className="font-bold text-gray-900 mb-3">Stats</h2>
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-yellow-50 rounded-xl p-3 text-center">
            <p className="text-3xl font-black text-yellow-600">{totalStars}</p>
            <p className="text-xs text-gray-500 font-semibold">Stars Earned</p>
          </div>
          <div className="bg-green-50 rounded-xl p-3 text-center">
            <p className="text-3xl font-black text-green-600">{totalChallenges - totalStars}</p>
            <p className="text-xs text-gray-500 font-semibold">Left to Go</p>
          </div>
        </div>
      </div>

      {/* Track breakdown */}
      <div className="bg-white rounded-2xl border-2 border-gray-200 p-5">
        <h2 className="font-bold text-gray-900 mb-3">Track Progress</h2>
        <div className="space-y-3">
          {TRACK_IDS.map((trackId) => {
            const track = TRACKS[trackId]
            const trackTotal = track.challenges.length
            const count = track.challenges.filter((c) => completedIds.has(c.id)).length
            const barColor = TRACK_BAR_COLORS[track.colorClass] ?? 'bg-gray-500'
            return (
              <div key={trackId} className="flex items-center gap-3">
                <span className="text-xl w-8">{track.emoji}</span>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-sm font-semibold text-gray-700">{track.name}</p>
                    <p className="text-sm text-gray-500">{count}/{trackTotal}</p>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${barColor}`}
                      style={{ width: `${(count / trackTotal) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Sign out */}
      <form action={logoutAction}>
        <Button variant="outline" className="w-full border-red-200 text-red-500 hover:bg-red-50">
          Sign Out
        </Button>
      </form>
    </div>
  )
}
