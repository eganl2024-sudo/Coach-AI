'use client'

import { useState, useTransition } from 'react'
import { Challenge, Track } from '@/lib/types'
import { markChallengeComplete } from '@/lib/actions/progress'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface ChallengeDetailProps {
  challenge: Challenge
  track: string
  isCompleted: boolean
  trackData: Track
}

const DIFFICULTY_LABEL = ['Beginner', 'Intermediate', 'Advanced']
const DIFFICULTY_COLOR = [
  'text-green-700 bg-green-100',
  'text-orange-700 bg-orange-100',
  'text-red-700 bg-red-100',
]

export function ChallengeDetail({
  challenge,
  track,
  isCompleted: initialCompleted,
  trackData,
}: ChallengeDetailProps) {
  const [completed, setCompleted] = useState(initialCompleted)
  const [showCelebration, setShowCelebration] = useState(false)
  const [isPending, startTransition] = useTransition()
  const [error, setError] = useState<string | null>(null)

  function handleComplete() {
    startTransition(async () => {
      const result = await markChallengeComplete(challenge.id, track)
      if (result.error) {
        setError(result.error)
      } else {
        setCompleted(true)
        setShowCelebration(true)
      }
    })
  }

  return (
    <div className="space-y-4">
      {/* Challenge card */}
      <div className={cn('rounded-3xl border-2 p-6', trackData.bgClass)}>
        <div className="flex items-center justify-between mb-3">
          <span
            className={cn(
              'text-xs font-bold px-3 py-1 rounded-full',
              DIFFICULTY_COLOR[challenge.difficulty - 1],
            )}
          >
            {DIFFICULTY_LABEL[challenge.difficulty - 1]}
          </span>
          {completed && <span className="text-2xl">⭐</span>}
        </div>

        <h2 className={cn('text-2xl font-black mb-2', trackData.colorClass)}>
          {challenge.title}
        </h2>
        <p className="text-gray-700 text-base leading-relaxed">{challenge.description}</p>
      </div>

      {/* Coach Tip */}
      <div className="bg-white rounded-2xl border-2 border-amber-200 p-5">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-xl">💡</span>
          <p className="font-bold text-amber-700 text-sm">Coach Tip</p>
        </div>
        <p className="text-gray-700 text-sm leading-relaxed">{challenge.tip}</p>
      </div>

      {/* How to practice */}
      <div className="bg-white rounded-2xl border-2 border-gray-200 p-5">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xl">📋</span>
          <p className="font-bold text-gray-900 text-sm">How to Practice</p>
        </div>
        <ol className="space-y-2 text-sm text-gray-600">
          <li className="flex gap-2">
            <span className="w-5 h-5 bg-green-100 text-green-700 rounded-full flex items-center justify-center text-xs font-bold shrink-0">1</span>
            Find an open space outside or in a gym.
          </li>
          <li className="flex gap-2">
            <span className="w-5 h-5 bg-green-100 text-green-700 rounded-full flex items-center justify-center text-xs font-bold shrink-0">2</span>
            Read the challenge and the coach tip.
          </li>
          <li className="flex gap-2">
            <span className="w-5 h-5 bg-green-100 text-green-700 rounded-full flex items-center justify-center text-xs font-bold shrink-0">3</span>
            Practice until you can do it — then tap the button!
          </li>
        </ol>
      </div>

      {/* Celebration */}
      {showCelebration && (
        <div className="bg-yellow-50 border-2 border-yellow-300 rounded-2xl p-5 text-center">
          <div className="text-4xl mb-2">🎉⭐🎉</div>
          <p className="text-xl font-black text-yellow-700">Amazing work!</p>
          <p className="text-yellow-600 text-sm mt-1">You earned a star for completing this challenge!</p>
        </div>
      )}

      {/* Complete button */}
      {error && (
        <p className="text-red-600 text-sm text-center font-medium">{error}</p>
      )}

      <Button
        onClick={handleComplete}
        disabled={completed || isPending}
        size="lg"
        className={cn('w-full text-lg', completed && 'bg-yellow-400 hover:bg-yellow-400 text-yellow-900')}
      >
        {completed ? '⭐ Challenge Complete!' : isPending ? 'Saving…' : '✅ Mark as Complete!'}
      </Button>

      {completed && !showCelebration && (
        <p className="text-center text-gray-500 text-sm">
          You already earned a star for this one! 🌟
        </p>
      )}
    </div>
  )
}
