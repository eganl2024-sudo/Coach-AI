import { Streak } from '@/lib/types'

interface StreakBannerProps {
  streak: Streak | null
}

export function StreakBanner({ streak }: StreakBannerProps) {
  const count = streak?.current_streak ?? 0

  if (count === 0) {
    return (
      <div className="flex items-center gap-3 bg-white rounded-2xl border-2 border-gray-100 px-4 py-3">
        <span className="text-2xl">🔥</span>
        <div>
          <p className="font-black text-gray-900 text-sm">Start your streak today!</p>
          <p className="text-xs text-gray-400">Complete a challenge to begin</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-3 bg-orange-50 border-2 border-orange-200 rounded-2xl px-4 py-3">
      <span className="text-3xl">🔥</span>
      <div className="flex-1">
        <p className="font-black text-orange-700 text-lg leading-tight">
          {count} day{count === 1 ? '' : 's'} in a row!
        </p>
        <p className="text-xs text-orange-500">
          {streak?.longest_streak && streak.longest_streak > count
            ? `Best: ${streak.longest_streak} days`
            : 'Keep the fire going!'}
        </p>
      </div>
      {count >= 7 && <span className="text-2xl">⭐</span>}
    </div>
  )
}
