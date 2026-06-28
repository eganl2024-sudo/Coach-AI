'use client'

import { useState, useTransition } from 'react'
import { TIMEZONES } from '@/lib/constants/timezones'
import { updateTimezoneAction } from '@/lib/actions/settings'
import { cn } from '@/lib/utils'

interface TimezoneSelectorProps {
  currentTimezone: string
}

export function TimezoneSelector({ currentTimezone }: TimezoneSelectorProps) {
  const [selected, setSelected] = useState(currentTimezone)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isPending, startTransition] = useTransition()

  function handleChange(value: string) {
    setSelected(value)
    setSaved(false)
    setError(null)
  }

  function handleSave() {
    const fd = new FormData()
    fd.set('timezone', selected)
    startTransition(async () => {
      const result = await updateTimezoneAction(fd)
      if (result?.error) {
        setError(result.error)
      } else {
        setSaved(true)
      }
    })
  }

  const changed = selected !== currentTimezone

  return (
    <div className="space-y-2">
      <select
        value={selected}
        onChange={(e) => handleChange(e.target.value)}
        className="w-full rounded-xl border-2 border-gray-200 bg-white px-4 py-3 text-sm font-semibold text-gray-900 focus:outline-none focus:border-green-500 transition-colors"
      >
        {TIMEZONES.map((tz) => (
          <option key={tz.value} value={tz.value}>
            {tz.label}
          </option>
        ))}
      </select>

      {(changed || saved) && (
        <button
          onClick={handleSave}
          disabled={isPending || saved}
          className={cn(
            'w-full py-3 rounded-xl font-bold text-sm transition-colors',
            saved
              ? 'bg-green-100 text-green-700 cursor-default'
              : 'bg-green-500 text-white hover:bg-green-600 active:scale-98',
          )}
        >
          {isPending ? 'Saving…' : saved ? '✓ Saved!' : 'Save Timezone'}
        </button>
      )}

      {error && <p className="text-sm text-red-500 font-medium">{error}</p>}

      <p className="text-xs text-gray-400">
        Affects when your daily streak resets. Update this if you travel.
      </p>
    </div>
  )
}
