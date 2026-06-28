'use client'

import { useState, useTransition } from 'react'
import { Kid } from '@/lib/types'
import { switchKidAction } from '@/lib/actions/settings'
import { cn } from '@/lib/utils'

interface KidSwitcherProps {
  kids: Kid[]
  activeKidId: string
}

export function KidSwitcher({ kids, activeKidId }: KidSwitcherProps) {
  const [isPending, startTransition] = useTransition()
  const [error, setError] = useState<string | null>(null)

  function handleSwitch(kidId: string) {
    setError(null)
    const fd = new FormData()
    fd.set('kidId', kidId)
    startTransition(async () => {
      const result = await switchKidAction(fd)
      if (result?.error) setError(result.error)
    })
  }

  return (
    <div className="space-y-2">
      {kids.map((kid) => {
        const active = kid.id === activeKidId
        return (
          <button
            key={kid.id}
            type="button"
            onClick={() => !active && handleSwitch(kid.id)}
            disabled={active || isPending}
            className={cn(
              'w-full flex items-center gap-4 rounded-2xl border-2 p-4 text-left transition-all',
              active
                ? 'border-green-500 bg-green-50 cursor-default'
                : 'border-gray-200 bg-white hover:border-green-300 hover:shadow-sm',
            )}
          >
            <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center text-xl shrink-0">
              ⚽
            </div>
            <div className="flex-1">
              <p className="font-bold text-gray-900">{kid.name}</p>
              <p className="text-xs text-gray-400 capitalize">Age {kid.age} · {kid.skill_level}</p>
            </div>
            {active && (
              <span className="text-xs font-bold text-green-600 bg-green-100 px-2 py-1 rounded-full">Active</span>
            )}
          </button>
        )
      })}
      {error && <p className="text-sm text-red-500 font-medium">{error}</p>}
    </div>
  )
}
