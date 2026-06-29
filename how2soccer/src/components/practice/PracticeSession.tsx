'use client'

import { useState, useTransition, useEffect } from 'react'
import Link from 'next/link'
import { markChallengeComplete, UnlockInfo, TrackCompleteInfo } from '@/lib/actions/progress'
import { ChallengeRating } from '@/lib/types'
import { DIFFICULTY_LABELS, DIFFICULTY_COLORS } from '@/lib/data/curriculum'
import { RatingPicker } from './RatingPicker'
import { UnlockCelebration } from '@/components/skills/UnlockCelebration'
import { TrackCompleteCelebration } from '@/components/skills/TrackCompleteCelebration'
import { cn } from '@/lib/utils'
import { trackEvent } from '@/lib/posthog'

interface PracticeChallenge {
  missionId: string
  challengeId: string
  track: string
  trackName: string
  trackEmoji: string
  trackColorClass: string
  trackBgClass: string
  title: string
  description: string
  tip: string
  difficulty: 1 | 2 | 3
  alreadyCompleted: boolean
  existingRating?: ChallengeRating | null
}

interface Props {
  kidName: string
  challenges: PracticeChallenge[]
  currentStreak: number
  allAlreadyDone: boolean
}

type Phase = 'ready' | 'challenge' | 'rating' | 'celebrating' | 'complete'

function StepDots({ total, current, completedInSession }: { total: number; current: number; completedInSession: number }) {
  return (
    <div className="flex items-center justify-center gap-2">
      {Array.from({ length: total }).map((_, i) => {
        const done = i < completedInSession
        const active = i === current
        return (
          <div
            key={i}
            className={cn(
              'rounded-full transition-all duration-300',
              done
                ? 'w-8 h-3 bg-green-500'
                : active
                ? 'w-8 h-3 bg-green-300'
                : 'w-3 h-3 bg-gray-200',
            )}
          />
        )
      })}
    </div>
  )
}

export function PracticeSession({ kidName, challenges, currentStreak, allAlreadyDone }: Props) {
  const [phase, setPhase] = useState<Phase>('ready')
  const [currentIndex, setCurrentIndex] = useState(0)
  const [completedInSession, setCompletedInSession] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [isPending, startTransition] = useTransition()
  const [pendingUnlock, setPendingUnlock] = useState<UnlockInfo | null>(null)
  const [pendingTrackComplete, setPendingTrackComplete] = useState<TrackCompleteInfo | null>(null)

  const current = challenges[currentIndex]
  const isLast = currentIndex === challenges.length - 1
  const total = challenges.length

  function handleStart() {
    if (allAlreadyDone) return
    trackEvent('practice_session_started', { challengeCount: total })
    const firstIncomplete = challenges.findIndex((c) => !c.alreadyCompleted)
    setCurrentIndex(firstIncomplete >= 0 ? firstIncomplete : 0)
    setPhase('challenge')
  }

  function handleDone() {
    if (current.alreadyCompleted) {
      advance()
      return
    }
    setError(null)
    startTransition(async () => {
      const result = await markChallengeComplete(current.challengeId, current.track)
      if ('error' in result) {
        setError('Something went wrong saving your progress. Try again!')
        return
      }
      setCompletedInSession((n) => n + 1)
      trackEvent('challenge_completed', {
        challengeId: current.challengeId,
        track: current.track,
        difficulty: current.difficulty,
        source: 'practice_session',
      })
      if (result.trackComplete) {
        setPendingTrackComplete(result.trackComplete)
        trackEvent('track_mastered', { track: current.track, trackName: result.trackComplete.trackName })
      } else if (result.unlockInfo) {
        setPendingUnlock(result.unlockInfo)
        trackEvent('tier_unlocked', { tier: result.unlockInfo.tier, track: current.track })
      } else {
        setPhase('rating')
      }
    })
  }

  function advance() {
    if (isLast) {
      setPhase('complete')
    } else {
      setCurrentIndex((i) => i + 1)
      setPhase('challenge')
    }
  }

  // ── TRACK COMPLETE OVERLAY ────────────────────────────────────────
  if (pendingTrackComplete) {
    return (
      <TrackCompleteCelebration
        info={pendingTrackComplete}
        onDismiss={() => {
          setPendingTrackComplete(null)
          setPhase('rating')
        }}
      />
    )
  }

  // ── UNLOCK OVERLAY ────────────────────────────────────────────────
  if (pendingUnlock) {
    return (
      <UnlockCelebration
        unlock={pendingUnlock}
        onDismiss={() => {
          setPendingUnlock(null)
          setPhase('rating')
        }}
      />
    )
  }

  useEffect(() => {
    if (phase === 'complete') {
      trackEvent('practice_session_completed', { completedInSession, totalChallenges: total })
    }
  }, [phase]) // eslint-disable-line react-hooks/exhaustive-deps

  // ── COMPLETE (client-reached — takes priority over allAlreadyDone) ──
  if (phase === 'complete') {
    const newStreak = currentStreak > 0 ? currentStreak : completedInSession > 0 ? 1 : 0
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center gap-6 py-8 text-center">
        <div className="text-6xl">🎉</div>
        <div>
          <h1 className="text-2xl font-black text-gray-900">Practice Complete!</h1>
          <p className="text-gray-500 mt-1">Great work today, {kidName}!</p>
        </div>

        <div className="w-full space-y-3">
          {completedInSession > 0 && (
            <div className="bg-yellow-50 border-2 border-yellow-200 rounded-2xl px-6 py-4">
              <p className="text-2xl font-black text-yellow-700">+{completedInSession} ⭐</p>
              <p className="text-yellow-600 text-sm">star{completedInSession === 1 ? '' : 's'} earned today</p>
            </div>
          )}
          {newStreak > 0 && (
            <div className="bg-orange-50 border-2 border-orange-100 rounded-2xl px-6 py-4">
              <p className="text-2xl font-black text-orange-500">🔥 {newStreak} day streak</p>
              <p className="text-orange-400 text-sm">Keep showing up!</p>
            </div>
          )}
        </div>

        <Link
          href="/home"
          className="w-full bg-green-500 text-white font-black text-lg py-4 rounded-2xl text-center hover:bg-green-600 transition-colors"
        >
          Back to Home
        </Link>
      </div>
    )
  }

  // ── ALREADY DONE (server says all done before session started) ──
  if (allAlreadyDone) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center gap-6 py-8 text-center">
        <div className="text-6xl">🎉</div>
        <div>
          <h1 className="text-2xl font-black text-gray-900">Practice Complete!</h1>
          <p className="text-gray-500 mt-1">You already finished today's session. Come back tomorrow!</p>
        </div>
        {currentStreak > 0 && (
          <div className="bg-orange-50 border-2 border-orange-100 rounded-2xl px-6 py-3">
            <p className="text-orange-600 font-bold">🔥 {currentStreak} day streak — keep it up!</p>
          </div>
        )}
        <Link
          href="/home"
          className="w-full max-w-xs bg-green-500 text-white font-bold text-lg py-4 rounded-2xl text-center hover:bg-green-600 transition-colors"
        >
          Back to Home
        </Link>
      </div>
    )
  }

  // ── READY ─────────────────────────────────────────────────────
  if (phase === 'ready') {
    return (
      <div className="py-6 space-y-6">
        <div className="text-center space-y-2">
          <p className="text-green-600 font-bold text-sm">Ready, {kidName}?</p>
          <h1 className="text-3xl font-black text-gray-900">Today&apos;s Practice</h1>
          <p className="text-gray-500">{total} challenge{total === 1 ? '' : 's'} · about {total * 5} min</p>
        </div>

        <div className="space-y-3">
          {challenges.map((c, i) => (
            <div
              key={c.missionId}
              className={cn(
                'flex items-center gap-4 rounded-2xl border-2 p-4',
                c.alreadyCompleted ? 'border-green-200 bg-green-50' : 'border-gray-200 bg-white',
              )}
            >
              <div className={cn('w-10 h-10 rounded-full flex items-center justify-center text-xl font-black shrink-0', c.alreadyCompleted ? 'bg-green-200 text-green-700' : 'bg-gray-100 text-gray-500')}>
                {c.alreadyCompleted ? '⭐' : i + 1}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-bold text-gray-900 truncate">{c.title}</p>
                <p className="text-xs text-gray-400">{c.trackEmoji} {c.trackName}</p>
              </div>
              {c.alreadyCompleted && (
                <span className="text-xs font-bold text-green-600 bg-green-100 px-2 py-1 rounded-full shrink-0">Done</span>
              )}
            </div>
          ))}
        </div>

        <button
          onClick={handleStart}
          className="w-full bg-green-500 hover:bg-green-600 active:scale-[0.98] text-white font-black text-xl py-5 rounded-2xl transition-all shadow-lg shadow-green-200"
        >
          ▶ Start Practice
        </button>

        <Link href="/home" className="block text-center text-sm text-gray-400 hover:text-gray-600">
          ← Back to home
        </Link>
      </div>
    )
  }

  // ── RATING ────────────────────────────────────────────────────
  if (phase === 'rating') {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center gap-8 py-8">
        <StepDots total={total} current={currentIndex} completedInSession={completedInSession} />

        <div className="text-center space-y-1">
          <div className="text-5xl mb-3">⭐</div>
          <h2 className="text-xl font-black text-gray-900">Nice work on {current.title}!</h2>
          <p className="text-gray-500 text-sm">Rate it so your coach can help you improve</p>
        </div>

        <div className="w-full">
          <RatingPicker
            challengeId={current.challengeId}
            track={current.track}
            existingRating={current.existingRating}
            onRated={() => setPhase('celebrating')}
            onSkip={() => setPhase('celebrating')}
          />
        </div>
      </div>
    )
  }

  // ── CELEBRATING ───────────────────────────────────────────────
  if (phase === 'celebrating') {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center gap-6 py-8 text-center">
        <StepDots total={total} current={currentIndex} completedInSession={completedInSession} />

        <div className="text-7xl animate-bounce">⭐</div>
        <div>
          <h2 className="text-2xl font-black text-gray-900">Challenge done!</h2>
          <p className="text-gray-500 mt-1">
            {isLast ? 'That was the last one!' : `${total - currentIndex - 1} more to go`}
          </p>
        </div>

        <button
          onClick={advance}
          className="w-full max-w-xs bg-green-500 hover:bg-green-600 text-white font-black text-lg py-4 rounded-2xl transition-colors"
        >
          {isLast ? 'See Results →' : 'Next Challenge →'}
        </button>
      </div>
    )
  }

  // ── CHALLENGE ─────────────────────────────────────────────────
  return (
    <div className="py-6 space-y-4">
      {/* Progress */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="font-bold text-gray-500">Challenge {currentIndex + 1} of {total}</span>
          <Link href="/home" className="text-gray-400 hover:text-gray-600 text-xs">✕ Exit</Link>
        </div>
        <StepDots total={total} current={currentIndex} completedInSession={completedInSession} />
      </div>

      {/* Challenge card */}
      <div className={cn('rounded-3xl border-2 p-6', current.trackBgClass)}>
        <div className="flex items-center justify-between mb-3">
          <span className={cn('text-xs font-bold px-3 py-1 rounded-full', DIFFICULTY_COLORS[current.difficulty - 1])}>
            {DIFFICULTY_LABELS[current.difficulty - 1]}
          </span>
          <span className="text-sm font-bold text-gray-400">{current.trackEmoji} {current.trackName}</span>
        </div>
        <h2 className="text-2xl font-black mb-2 text-gray-900">{current.title}</h2>
        <p className="text-gray-700 text-base leading-relaxed">{current.description}</p>
      </div>

      {/* Coach tip */}
      <div className="bg-gray-50 rounded-2xl p-5">
        <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Coach Tip</p>
        <p className="text-gray-700 text-sm leading-relaxed">{current.tip}</p>
      </div>

      {/* Already completed notice */}
      {current.alreadyCompleted && (
        <div className="bg-green-50 border-2 border-green-200 rounded-2xl p-4 text-center">
          <p className="text-green-700 font-bold text-sm">⭐ You already earned a star for this one!</p>
        </div>
      )}

      {error && <p className="text-red-600 text-sm text-center font-medium">{error}</p>}

      <button
        onClick={handleDone}
        disabled={isPending}
        className="w-full bg-green-500 hover:bg-green-600 active:scale-[0.98] disabled:opacity-60 text-white font-black text-xl py-5 rounded-2xl transition-all shadow-lg shadow-green-200"
      >
        {isPending
          ? 'Saving…'
          : current.alreadyCompleted
          ? `Next Challenge →`
          : isLast
          ? 'Finish Practice'
          : 'Done! Next Challenge →'}
      </button>
    </div>
  )
}
