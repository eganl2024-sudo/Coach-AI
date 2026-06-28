import Link from 'next/link'
import { Track } from '@/lib/types'
import { cn } from '@/lib/utils'

interface TrackCardProps {
  track: Track
  completedCount: number
}

const totalChallenges = 5

export function TrackCard({ track, completedCount }: TrackCardProps) {
  const pct = Math.round((completedCount / totalChallenges) * 100)
  const allDone = completedCount === totalChallenges

  return (
    <Link href={`/skills/${track.id}`} className="block">
      <div
        className={cn(
          'rounded-2xl border-2 p-5 transition-all hover:shadow-md active:scale-98',
          track.bgClass,
        )}
      >
        <div className="flex items-start justify-between mb-3">
          <div>
            <div className="text-3xl mb-1">{track.emoji}</div>
            <h3 className={cn('text-xl font-black', track.colorClass)}>{track.name}</h3>
            <p className="text-gray-600 text-sm mt-0.5">{track.description}</p>
          </div>
          <div className="text-right">
            <span className={cn('text-2xl font-black', track.colorClass)}>
              {completedCount}
              <span className="text-lg text-gray-400">/{totalChallenges}</span>
            </span>
            {allDone && <div className="text-yellow-500 text-lg">⭐</div>}
          </div>
        </div>

        {/* Progress bar */}
        <div className="h-2.5 bg-white/60 rounded-full overflow-hidden">
          <div
            className={cn('h-full rounded-full transition-all duration-500', {
              'bg-green-500': track.id === 'juggling',
              'bg-orange-500': track.id === 'dribbling',
              'bg-blue-500': track.id === 'passing',
              'bg-red-500': track.id === 'shooting',
            })}
            style={{ width: `${pct}%` }}
          />
        </div>
        <p className="text-xs text-gray-500 mt-1.5">
          {allDone ? 'Track complete! 🎉' : `${pct}% complete`}
        </p>
      </div>
    </Link>
  )
}
