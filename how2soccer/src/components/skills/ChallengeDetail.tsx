'use client'

import { useState, useTransition } from 'react'
import { Challenge, ChallengeRating, Track } from '@/lib/types'
import { markChallengeComplete, UnlockInfo, TrackCompleteInfo } from '@/lib/actions/progress'
import { DIFFICULTY_LABELS, DIFFICULTY_COLORS } from '@/lib/data/curriculum'
import { RatingPicker } from '@/components/practice/RatingPicker'
import { UnlockCelebration } from '@/components/skills/UnlockCelebration'
import { TrackCompleteCelebration } from '@/components/skills/TrackCompleteCelebration'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { trackEvent } from '@/lib/posthog'

interface ChallengeDetailProps {
  challenge: Challenge
  track: string
  isCompleted: boolean
  existingRating?: ChallengeRating | null
  trackData: Track
}

export function ChallengeDetail({
  challenge,
  track,
  isCompleted: initialCompleted,
  existingRating,
  trackData,
}: ChallengeDetailProps) {
  const [completed, setCompleted] = useState(initialCompleted)
  const [showCelebration, setShowCelebration] = useState(false)
  const [showRating, setShowRating] = useState(initialCompleted)
  const [pendingUnlock, setPendingUnlock] = useState<UnlockInfo | null>(null)
  const [pendingTrackComplete, setPendingTrackComplete] = useState<TrackCompleteInfo | null>(null)
  const [isPending, startTransition] = useTransition()
  const [error, setError] = useState<string | null>(null)

  function handleComplete() {
    startTransition(async () => {
      const result = await markChallengeComplete(challenge.id, track)
      if ('error' in result) {
        setError('Something went wrong. Please try again!')
      } else {
        setCompleted(true)
        setShowCelebration(true)
        setShowRating(true)
        trackEvent('challenge_completed', { challengeId: challenge.id, track, difficulty: challenge.difficulty })
        if (result.trackComplete) {
          setPendingTrackComplete(result.trackComplete)
          trackEvent('track_mastered', { track, trackName: result.trackComplete.trackName })
        } else if (result.unlockInfo) {
          setPendingUnlock(result.unlockInfo)
          trackEvent('tier_unlocked', { tier: result.unlockInfo.tier, track, trackName: result.unlockInfo.trackName })
        }
      }
    })
  }

  return (
    <>
      {pendingTrackComplete && (
        <TrackCompleteCelebration
          info={pendingTrackComplete}
          onDismiss={() => setPendingTrackComplete(null)}
        />
      )}
      {pendingUnlock && (
        <UnlockCelebration
          unlock={pendingUnlock}
          onDismiss={() => setPendingUnlock(null)}
        />
      )}

      <div className="space-y-4">
        {/* Challenge card */}
        <div className={cn('rounded-3xl border-2 p-6', trackData.bgClass)}>
          <div className="flex items-center justify-between mb-3">
            <span
              className={cn(
                'text-xs font-bold px-3 py-1 rounded-full',
                DIFFICULTY_COLORS[challenge.difficulty - 1],
              )}
            >
              {DIFFICULTY_LABELS[challenge.difficulty - 1]}
            </span>
            {completed && <span className="text-2xl">⭐</span>}
          </div>

          <h2 className="text-2xl font-black mb-2 text-gray-900">
            {challenge.title}
          </h2>
          <p className="text-gray-700 text-base leading-relaxed">{challenge.description}</p>
        </div>

        {/* Coach Tip */}
        <div className="bg-gray-50 rounded-2xl p-5">
          <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Coach Tip</p>
          <p className="text-gray-700 text-sm leading-relaxed">{challenge.tip}</p>
        </div>

        {/* Celebration */}
        {showCelebration && (
          <div className="bg-white border-2 border-gray-100 rounded-2xl p-5 text-center">
            <div className="text-4xl mb-2">⭐</div>
            <p className="text-xl font-black text-gray-900">Amazing work!</p>
            <p className="text-gray-500 text-sm mt-1">You earned a star for completing this challenge!</p>
          </div>
        )}

        {/* Rating */}
        {showRating && (
          <div className="bg-white rounded-2xl border-2 border-gray-100 p-5">
            <RatingPicker
              challengeId={challenge.id}
              track={track}
              existingRating={existingRating}
            />
          </div>
        )}

        {error && (
          <p className="text-red-600 text-sm text-center font-medium">{error}</p>
        )}

        <Button
          onClick={handleComplete}
          disabled={completed || isPending}
          size="lg"
          className={cn('w-full text-lg', completed && 'bg-yellow-400 hover:bg-yellow-400 text-yellow-900')}
        >
          {completed ? 'Challenge Complete!' : isPending ? 'Saving…' : 'Mark as Complete'}
        </Button>

        {completed && !showCelebration && (
          <p className="text-center text-gray-500 text-sm">
            You already earned a star for this one! 🌟
          </p>
        )}
      </div>
    </>
  )
}
