'use client'

import { useState, useTransition } from 'react'
import { saveRating } from '@/lib/actions/progress'
import { ChallengeRating } from '@/lib/types'
import { cn } from '@/lib/utils'

const RATINGS: { value: ChallengeRating; emoji: string; label: string; classes: string }[] = [
  {
    value: 'tough',
    emoji: '😅',
    label: 'Tough',
    classes: 'border-red-200 bg-red-50 text-red-700 hover:bg-red-100 active:bg-red-200',
  },
  {
    value: 'got_it',
    emoji: '✅',
    label: 'Got it',
    classes: 'border-green-200 bg-green-50 text-green-700 hover:bg-green-100 active:bg-green-200',
  },
  {
    value: 'easy',
    emoji: '⚡',
    label: 'Easy',
    classes: 'border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100 active:bg-blue-200',
  },
]

interface Props {
  challengeId: string
  track: string
  existingRating?: ChallengeRating | null
  onRated?: (rating: ChallengeRating) => void
  onSkip?: () => void
}

export function RatingPicker({ challengeId, track, existingRating, onRated, onSkip }: Props) {
  const [selected, setSelected] = useState<ChallengeRating | null>(existingRating ?? null)
  const [isPending, startTransition] = useTransition()

  function handleRate(rating: ChallengeRating) {
    if (isPending) return
    setSelected(rating)
    startTransition(async () => {
      await saveRating(challengeId, track, rating)
      onRated?.(rating)
    })
  }

  return (
    <div className="space-y-3">
      <p className="text-center font-bold text-gray-700 text-sm">How did that feel?</p>
      <div className="grid grid-cols-3 gap-2">
        {RATINGS.map((r) => (
          <button
            key={r.value}
            onClick={() => handleRate(r.value)}
            disabled={isPending}
            className={cn(
              'flex flex-col items-center gap-1 rounded-2xl border-2 py-3 px-2 font-bold text-xs transition-all active:scale-95 disabled:opacity-60',
              r.classes,
              selected === r.value && 'ring-2 ring-offset-1 ring-current scale-105',
            )}
          >
            <span className="text-2xl">{r.emoji}</span>
            <span>{r.label}</span>
          </button>
        ))}
      </div>
      {onSkip && !selected && (
        <button
          onClick={onSkip}
          className="block w-full text-center text-xs text-gray-400 hover:text-gray-600 py-1"
        >
          Skip
        </button>
      )}
    </div>
  )
}
