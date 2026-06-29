'use client'

import { TrackCompleteInfo } from '@/lib/actions/progress'

interface Props {
  info: TrackCompleteInfo
  onDismiss: () => void
}

export function TrackCompleteCelebration({ info, onDismiss }: Props) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/70 backdrop-blur-sm">
      <div className="w-full max-w-sm bg-white rounded-3xl shadow-2xl shadow-yellow-200 overflow-hidden">
        {/* Banner */}
        <div className="bg-gradient-to-r from-yellow-400 to-amber-500 px-6 py-6 text-center">
          <div className="text-7xl mb-1">🏆</div>
          <p className="text-white font-black text-2xl tracking-tight">TRACK MASTERED!</p>
        </div>

        {/* Stars burst */}
        <div className="bg-yellow-50 px-6 py-4 text-center border-b border-yellow-100">
          <div className="text-3xl tracking-widest">
            {'⭐'.repeat(Math.min(info.totalChallenges, 12))}
          </div>
          <p className="text-yellow-700 font-black text-lg mt-1">
            {info.totalChallenges}/{info.totalChallenges} challenges complete
          </p>
        </div>

        {/* Content */}
        <div className="px-6 py-5 text-center space-y-4">
          <div>
            <p className="text-4xl mb-1">{info.trackEmoji}</p>
            <p className="text-2xl font-black text-gray-900">{info.trackName}</p>
            <p className="text-gray-500 text-sm mt-1">You mastered every challenge in this track. You&apos;re a star!</p>
          </div>

          <button
            onClick={onDismiss}
            className="w-full bg-gradient-to-r from-yellow-400 to-amber-500 hover:opacity-90 active:scale-[0.98] text-white font-black text-lg py-4 rounded-2xl transition-all"
          >
            ⭐ Awesome! Keep Going →
          </button>
        </div>
      </div>
    </div>
  )
}
