'use client'

import { UnlockInfo } from '@/lib/actions/progress'

interface Props {
  unlock: UnlockInfo
  onDismiss: () => void
}

const TIER_CONFIG = {
  2: {
    banner: '⚡ Intermediate Unlocked!',
    bg: 'bg-orange-500',
    ring: 'border-orange-300',
    text: 'text-orange-600',
    badgeBg: 'bg-orange-100',
    glow: 'shadow-orange-200',
  },
  3: {
    banner: '🔥 Advanced Unlocked!',
    bg: 'bg-red-500',
    ring: 'border-red-300',
    text: 'text-red-600',
    badgeBg: 'bg-red-100',
    glow: 'shadow-red-200',
  },
}

export function UnlockCelebration({ unlock, onDismiss }: Props) {
  const cfg = TIER_CONFIG[unlock.tier]

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/60 backdrop-blur-sm">
      <div className={`w-full max-w-sm bg-white rounded-3xl shadow-2xl ${cfg.glow} overflow-hidden`}>
        {/* Banner */}
        <div className={`${cfg.bg} px-6 py-5 text-center`}>
          <div className="text-6xl mb-2 animate-bounce">🔓</div>
          <p className="text-white font-black text-xl tracking-tight">{cfg.banner}</p>
        </div>

        {/* Content */}
        <div className="px-6 py-5 text-center space-y-4">
          <div>
            <p className="text-2xl mb-1">{unlock.trackEmoji}</p>
            <p className="text-lg font-black text-gray-900">{unlock.trackName}</p>
            <p className="text-gray-500 text-sm mt-1">
              {unlock.newChallengeCount} new challenge{unlock.newChallengeCount === 1 ? '' : 's'} just unlocked!
            </p>
          </div>

          <div className={`${cfg.badgeBg} ${cfg.ring} border-2 rounded-2xl px-4 py-3`}>
            <p className={`${cfg.text} font-bold text-sm`}>
              You mastered the basics — now the real training begins!
            </p>
          </div>

          <button
            onClick={onDismiss}
            className={`w-full ${cfg.bg} hover:opacity-90 active:scale-[0.98] text-white font-black text-lg py-4 rounded-2xl transition-all`}
          >
            Let&apos;s Go! →
          </button>
        </div>
      </div>
    </div>
  )
}
