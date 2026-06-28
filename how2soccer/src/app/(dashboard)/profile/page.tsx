import type { Metadata } from 'next'
import { getSession } from '@/lib/session'
import { getKidProgress } from '@/lib/actions/progress'
import { TRACK_IDS, TRACKS } from '@/lib/data/curriculum'
import { logoutAction } from '@/lib/actions/auth'
import { Button } from '@/components/ui/button'

export const metadata: Metadata = { title: 'Profile' }

export default async function ProfilePage() {
  const session = await getSession()
  const progress = await getKidProgress(session.kidId!)
  const completedIds = new Set(progress.map((p) => p.challenge_id))
  const totalStars = completedIds.size

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

      {/* Stats */}
      <div className="bg-white rounded-2xl border-2 border-gray-200 p-5">
        <h2 className="font-bold text-gray-900 mb-3">Stats</h2>
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-yellow-50 rounded-xl p-3 text-center">
            <p className="text-3xl font-black text-yellow-600">{totalStars}</p>
            <p className="text-xs text-gray-500 font-semibold">Stars Earned</p>
          </div>
          <div className="bg-green-50 rounded-xl p-3 text-center">
            <p className="text-3xl font-black text-green-600">{20 - totalStars}</p>
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
            const count = track.challenges.filter((c) => completedIds.has(c.id)).length
            return (
              <div key={trackId} className="flex items-center gap-3">
                <span className="text-xl w-8">{track.emoji}</span>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-sm font-semibold text-gray-700">{track.name}</p>
                    <p className="text-sm text-gray-500">{count}/5</p>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className={[
                        'h-full rounded-full',
                        trackId === 'juggling' ? 'bg-green-500' :
                        trackId === 'dribbling' ? 'bg-orange-500' :
                        trackId === 'passing' ? 'bg-blue-500' : 'bg-red-500',
                      ].join(' ')}
                      style={{ width: `${(count / 5) * 100}%` }}
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
