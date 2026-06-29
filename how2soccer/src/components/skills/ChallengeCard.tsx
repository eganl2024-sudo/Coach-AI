import Link from 'next/link'
import { Challenge } from '@/lib/types'
import { cn } from '@/lib/utils'

interface ChallengeCardProps {
  challenge: Challenge
  trackId: string
  index: number
  isCompleted: boolean
  isLocked?: boolean
}

const DIFFICULTY_LABEL = ['Beginner', 'Intermediate', 'Advanced']
const DIFFICULTY_COLOR = ['text-green-600 bg-green-100', 'text-orange-600 bg-orange-100', 'text-red-600 bg-red-100']

export function ChallengeCard({ challenge, trackId, index, isCompleted, isLocked = false }: ChallengeCardProps) {
  const card = (
    <div
      className={cn(
        'flex items-center gap-4 rounded-2xl border-2 p-4 transition-all',
        isLocked
          ? 'border-gray-100 bg-gray-50 opacity-50 cursor-not-allowed'
          : isCompleted
          ? 'border-yellow-300 bg-yellow-50 hover:shadow-md active:scale-98'
          : 'border-gray-200 bg-white hover:shadow-md active:scale-98',
      )}
    >
      <div
        className={cn(
          'w-10 h-10 rounded-full flex items-center justify-center text-lg font-black shrink-0',
          isLocked
            ? 'bg-gray-200 text-gray-400'
            : isCompleted
            ? 'bg-yellow-400 text-white'
            : 'bg-gray-100 text-gray-500',
        )}
      >
        {isLocked ? '🔒' : isCompleted ? '⭐' : index + 1}
      </div>

      <div className="flex-1 min-w-0">
        <p className={cn('font-bold text-base', isLocked ? 'text-gray-400' : isCompleted ? 'text-gray-700' : 'text-gray-900')}>
          {challenge.title}
        </p>
        <p className={cn('text-sm truncate', isLocked ? 'text-gray-300' : 'text-gray-500')}>
          {isLocked ? 'Complete previous tier to unlock' : challenge.description}
        </p>
      </div>

      <span
        className={cn(
          'text-xs font-semibold px-2 py-1 rounded-full shrink-0',
          isLocked ? 'text-gray-400 bg-gray-100' : DIFFICULTY_COLOR[challenge.difficulty - 1],
        )}
      >
        {DIFFICULTY_LABEL[challenge.difficulty - 1]}
      </span>
    </div>
  )

  if (isLocked) return card
  return (
    <Link href={`/skills/${trackId}/${challenge.id}`} className="block">
      {card}
    </Link>
  )
}
