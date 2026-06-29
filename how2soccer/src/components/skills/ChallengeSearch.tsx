'use client'

import { useState, useMemo } from 'react'
import Link from 'next/link'
import { TRACKS, TRACK_IDS } from '@/lib/data/curriculum'

const ALL_CHALLENGES = TRACK_IDS.flatMap((trackId) => {
  const track = TRACKS[trackId]
  return track.challenges.map((c) => ({
    ...c,
    trackId,
    trackName: track.name,
    trackEmoji: track.emoji,
  }))
})

const DIFFICULTY_LABEL = ['Beginner', 'Intermediate', 'Advanced']
const DIFFICULTY_COLOR = [
  'text-green-700 bg-green-100',
  'text-orange-700 bg-orange-100',
  'text-red-700 bg-red-100',
]

export function ChallengeSearch({ completedIds }: { completedIds: string[] }) {
  const [query, setQuery] = useState('')
  const completedSet = useMemo(() => new Set(completedIds), [completedIds])

  const results = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return []
    return ALL_CHALLENGES.filter(
      (c) =>
        c.title.toLowerCase().includes(q) ||
        c.description.toLowerCase().includes(q) ||
        c.trackName.toLowerCase().includes(q),
    ).slice(0, 15)
  }, [query])

  return (
    <div className="space-y-2">
      <div className="relative">
        <input
          type="search"
          placeholder="Search all 72 challenges..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full rounded-2xl border-2 border-gray-200 bg-white px-4 py-3 pl-10 text-base focus:border-green-400 focus:outline-none"
        />
        <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400 text-lg pointer-events-none">
          🔍
        </span>
      </div>

      {query.trim() && (
        <div className="space-y-2">
          {results.length === 0 ? (
            <p className="text-center text-gray-400 text-sm py-4">
              No challenges match &ldquo;{query}&rdquo;
            </p>
          ) : (
            <>
              {results.map((c) => (
                <Link key={c.id} href={`/skills/${c.trackId}/${c.id}`} className="block">
                  <div className="flex items-center gap-3 rounded-2xl border-2 border-gray-200 bg-white p-4 hover:border-green-300 hover:shadow-sm transition-all">
                    <div className="text-2xl shrink-0">{c.trackEmoji}</div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <p className="font-bold text-gray-900 text-sm">{c.title}</p>
                        {completedSet.has(c.id) && <span className="text-yellow-500 text-xs">⭐</span>}
                        <span
                          className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${DIFFICULTY_COLOR[c.difficulty - 1]}`}
                        >
                          {DIFFICULTY_LABEL[c.difficulty - 1]}
                        </span>
                      </div>
                      <p className="text-xs text-gray-400 truncate mt-0.5">
                        {c.trackName} · {c.description.slice(0, 55)}
                        {c.description.length > 55 ? '…' : ''}
                      </p>
                    </div>
                    <span className="text-gray-300 text-lg shrink-0">›</span>
                  </div>
                </Link>
              ))}
              <p className="text-xs text-center text-gray-400 pt-1">
                {results.length} result{results.length === 1 ? '' : 's'}
              </p>
            </>
          )}
        </div>
      )}
    </div>
  )
}
