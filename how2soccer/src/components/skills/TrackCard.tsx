import Link from 'next/link'
import { Track } from '@/lib/types'
import { cn } from '@/lib/utils'

interface TrackCardProps {
  track: Track
  completedCount: number
}

const TRACK_BAR_COLORS: Record<string, string> = {
  juggling: 'bg-green-500',
  dribbling: 'bg-orange-500',
  passing: 'bg-blue-500',
  shooting: 'bg-red-500',
  control: 'bg-purple-500',
  tricks: 'bg-pink-500',
}

export function TrackCard({ track, completedCount }: TrackCardProps) {
  const totalChallenges = track.challenges.length
  const pct = Math.round((completedCount / totalChallenges) * 100)
  const allDone = completedCount === totalChallenges
  const barColor = TRACK_BAR_COLORS[track.id] ?? 'bg-gray-500'

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
            <h3 className="text-xl font-black text-gray-900">{track.name}</h3>
            <p className="text-gray-500 text-sm mt-0.5">{track.description}</p>
          </div>
          <div className="text-right">
            <span className="text-2xl font-black text-gray-900">
              {completedCount}
              <span className="text-lg text-gray-400">/{totalChallenges}</span>
            </span>
            {allDone && <div className="text-yellow-400 text-xl mt-0.5">★</div>}
          </div>
        </div>

        {/* Progress bar */}
        <div className="h-2.5 bg-white/60 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${barColor}`}
            style={{ width: `${pct}%` }}
          />
        </div>
        <p className="text-xs text-gray-400 mt-1.5">
          {allDone ? 'Track complete!' : pct > 0 ? `${pct}% done` : 'Not started'}
        </p>
      </div>
    </Link>
  )
}
