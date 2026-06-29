import Link from 'next/link'
import { DailyMission, Track, Challenge } from '@/lib/types'
import { cn } from '@/lib/utils'

interface MissionCardProps {
  mission: DailyMission
  challenge: Challenge
  trackData: Track
}

export function MissionCard({ mission, challenge, trackData }: MissionCardProps) {
  const done = !!mission.completed_at

  return (
    <Link href={`/skills/${mission.track}/${mission.challenge_id}`} className="block">
      <div
        className={cn(
          'flex items-center gap-4 rounded-2xl border-2 p-4 transition-all active:scale-98',
          done
            ? 'border-green-200 bg-green-50'
            : 'border-gray-200 bg-white hover:shadow-md',
        )}
      >
        <div
          className={cn(
            'w-11 h-11 rounded-xl flex items-center justify-center text-xl shrink-0',
            done ? 'bg-green-100' : trackData.bgClass.split(' ')[0],
          )}
        >
          {done ? '✓' : trackData.emoji}
        </div>

        <div className="flex-1 min-w-0">
          <p className={cn('font-bold text-base leading-tight', done ? 'text-gray-500 line-through' : 'text-gray-900')}>
            {challenge.title}
          </p>
          <p className="text-xs mt-0.5 font-semibold text-gray-400">
            {trackData.emoji} {trackData.name}
          </p>
        </div>

        {done ? (
          <span className="text-xs font-bold text-green-700 bg-green-100 px-2 py-1 rounded-full shrink-0">Done</span>
        ) : (
          <span className="text-gray-300 text-lg shrink-0">›</span>
        )}
      </div>
    </Link>
  )
}
