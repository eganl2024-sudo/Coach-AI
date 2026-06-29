import { KidStats } from '@/lib/actions/parent'
import { WeeklyActivity } from './WeeklyActivity'
import { cn } from '@/lib/utils'

const TRACK_BAR_COLORS: Record<string, string> = {
  'text-green-600': 'bg-green-600',
  'text-orange-600': 'bg-orange-600',
  'text-blue-600': 'bg-blue-600',
  'text-red-600': 'bg-red-600',
  'text-purple-600': 'bg-purple-600',
  'text-pink-600': 'bg-pink-600',
}

function NudgeBanner({ days, name }: { days: number | null; name: string }) {
  if (days === null) {
    return (
      <div className="rounded-xl bg-blue-50 border border-blue-100 px-3 py-2 text-xs text-blue-700 font-medium">
        {name} hasn't started yet — share the app to get them going!
      </div>
    )
  }
  if (days === 0) {
    return (
      <div className="rounded-xl bg-green-50 border border-green-100 px-3 py-2 text-xs text-green-700 font-medium">
        Practiced today!
      </div>
    )
  }
  if (days === 1) {
    return (
      <div className="rounded-xl bg-yellow-50 border border-yellow-100 px-3 py-2 text-xs text-yellow-700 font-medium">
        Last practiced yesterday — keep the streak alive!
      </div>
    )
  }
  if (days <= 3) {
    return (
      <div className="rounded-xl bg-orange-50 border border-orange-100 px-3 py-2 text-xs text-orange-700 font-medium">
        {name} hasn't practiced in {days} days — time for a nudge!
      </div>
    )
  }
  return (
    <div className="rounded-xl bg-red-50 border border-red-100 px-3 py-2 text-xs text-red-700 font-medium">
      {name} hasn't practiced in {days} days — streak reset. Help them get back on track!
    </div>
  )
}

export function KidSummaryCard({ kid }: { kid: KidStats }) {
  const totalChallenges = kid.trackProgress.reduce((sum, t) => sum + t.total, 0)
  const pct = totalChallenges > 0 ? Math.round((kid.totalStars / totalChallenges) * 100) : 0

  return (
    <div className="bg-white rounded-2xl border-2 border-gray-200 p-5 space-y-4">
      {/* Kid header */}
      <div className="flex items-center gap-3">
        <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center text-2xl shrink-0">
          ⚽
        </div>
        <div className="flex-1 min-w-0">
          <h2 className="font-black text-gray-900 text-lg leading-tight">{kid.name}</h2>
          <p className="text-xs text-gray-400 capitalize">Age {kid.age} · {kid.skill_level}</p>
        </div>
        <div className="text-right shrink-0">
          <p className="text-2xl font-black text-yellow-500">{kid.totalStars}</p>
          <p className="text-xs text-gray-400">stars</p>
        </div>
      </div>

      {/* Nudge */}
      <NudgeBanner days={kid.daysSinceLastPractice} name={kid.name} />

      {/* Stats row */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-orange-50 rounded-xl p-3 text-center">
          <p className="text-2xl font-black text-orange-500">🔥 {kid.streak.current}</p>
          <p className="text-xs text-gray-500 mt-0.5">day streak</p>
        </div>
        <div className="bg-slate-50 rounded-xl p-3 text-center">
          <p className="text-2xl font-black text-slate-600">{pct}%</p>
          <p className="text-xs text-gray-500 mt-0.5">curriculum done</p>
        </div>
      </div>

      {/* Weekly activity */}
      <WeeklyActivity practicedDates={kid.weeklyDates} timezone={kid.streak.timezone} />

      {/* Track mini-bars */}
      <div className="space-y-2">
        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Track Progress</p>
        {kid.trackProgress.map((t) => {
          const pct = t.total > 0 ? (t.completed / t.total) * 100 : 0
          return (
            <div key={t.id} className="flex items-center gap-2">
              <span className="text-sm w-4">{t.emoji}</span>
              <span className="text-xs text-gray-600 w-16 shrink-0">{t.name}</span>
              <div className="flex-1 bg-gray-100 rounded-full h-2">
                <div
                  className={cn('h-2 rounded-full transition-all', TRACK_BAR_COLORS[t.colorClass] ?? 'bg-gray-400')}
                  style={{ width: `${pct}%` }}
                />
              </div>
              <span className="text-xs text-gray-400 shrink-0 w-8 text-right">{t.completed}/{t.total}</span>
            </div>
          )
        })}
      </div>

      {/* Longest streak footnote */}
      {kid.streak.longest > 0 && (
        <p className="text-xs text-gray-400">
          Best streak: <span className="font-bold text-gray-600">{kid.streak.longest} days</span>
        </p>
      )}
    </div>
  )
}
