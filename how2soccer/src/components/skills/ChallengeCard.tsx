import Link from 'next/link'
import { Challenge } from '@/lib/types'
import { cn } from '@/lib/utils'

interface ChallengeCardProps {
  challenge: Challenge
  trackId: string
  index: number
  isCompleted: boolean
}

const DIFFICULTY_LABEL = ['Beginner', 'Intermediate', 'Advanced']
const DIFFICULTY_COLOR = ['text-green-600 bg-green-100', 'text-orange-600 bg-orange-100', 'text-red-600 bg-red-100']

export function ChallengeCard({ challenge, trackId, index, isCompleted }: ChallengeCardProps) {
  return (
    <Link href={`/skills/${trackId}/${challenge.id}`} className="block">
      <div
        className={cn(
          'flex items-center gap-4 rounded-2xl border-2 p-4 bg-white transition-all hover:shadow-md active:scale-98',
          isCompleted ? 'border-yellow-300 bg-yellow-50' : 'border-gray-200',
        )}
      >
        <div
          className={cn(
            'w-10 h-10 rounded-full flex items-center justify-center text-lg font-black shrink-0',
            isCompleted
              ? 'bg-yellow-400 text-white'
              : 'bg-gray-100 text-gray-500',
          )}
        >
          {isCompleted ? '⭐' : index + 1}
        </div>

        <div className="flex-1 min-w-0">
          <p className={cn('font-bold text-base', isCompleted ? 'text-gray-700' : 'text-gray-900')}>
            {challenge.title}
          </p>
          <p className="text-sm text-gray-500 truncate">{challenge.description}</p>
        </div>

        <span
          className={cn(
            'text-xs font-semibold px-2 py-1 rounded-full shrink-0',
            DIFFICULTY_COLOR[challenge.difficulty - 1],
          )}
        >
          {DIFFICULTY_LABEL[challenge.difficulty - 1]}
        </span>
      </div>
    </Link>
  )
}
