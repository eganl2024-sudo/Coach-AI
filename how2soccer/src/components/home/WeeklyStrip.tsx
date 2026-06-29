import { cn } from '@/lib/utils'

interface DayActivity {
  date: string
  active: boolean
  isToday: boolean
}

interface Props {
  days: DayActivity[]
}

const DAY_LABELS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

export function WeeklyStrip({ days }: Props) {
  return (
    <div className="bg-white rounded-2xl border-2 border-gray-100 p-4">
      <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">This Week</p>
      <div className="flex items-end justify-between gap-1">
        {days.map(({ date, active, isToday }) => {
          const dayName = DAY_LABELS[new Date(date + 'T12:00:00').getDay()]
          return (
            <div key={date} className="flex flex-col items-center gap-1.5 flex-1">
              <div
                className={cn(
                  'w-full aspect-square rounded-xl transition-all',
                  active
                    ? 'bg-green-500'
                    : isToday
                    ? 'bg-gray-100 border-2 border-green-300 border-dashed'
                    : 'bg-gray-100',
                )}
              />
              <span
                className={cn(
                  'text-[10px] font-bold',
                  isToday ? 'text-green-600' : active ? 'text-gray-600' : 'text-gray-300',
                )}
              >
                {dayName}
              </span>
            </div>
          )
        })}
      </div>
      {(() => {
        const count = days.filter((d) => d.active).length
        const label =
          count === 0 ? 'Start your streak today!' :
          count === 7 ? 'Perfect week!' :
          `${count} day${count === 1 ? '' : 's'} this week — keep it up!`
        return <p className="text-xs text-gray-400 text-center mt-2">{label}</p>
      })()}
    </div>
  )
}
