interface WeeklyActivityProps {
  practicedDates: string[]
  timezone: string
}

function getLast7Days(timezone: string): { date: string; label: string }[] {
  const days = []
  for (let i = 6; i >= 0; i--) {
    const d = new Date()
    d.setDate(d.getDate() - i)
    const date = d.toLocaleDateString('en-CA', { timeZone: timezone })
    const label = d.toLocaleDateString('en-US', { timeZone: timezone, weekday: 'short' }).slice(0, 1)
    days.push({ date, label })
  }
  return days
}

export function WeeklyActivity({ practicedDates, timezone }: WeeklyActivityProps) {
  const days = getLast7Days(timezone)
  const practicedSet = new Set(practicedDates)
  const practicedCount = days.filter((d) => practicedSet.has(d.date)).length

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">This week</span>
        <span className="text-xs font-bold text-gray-700">{practicedCount}/7 days</span>
      </div>
      <div className="flex gap-1.5">
        {days.map(({ date, label }) => {
          const practiced = practicedSet.has(date)
          const isToday = date === days[days.length - 1].date
          return (
            <div key={date} className="flex flex-col items-center gap-1 flex-1">
              <div
                className={`w-full aspect-square rounded-lg ${
                  practiced
                    ? 'bg-green-500'
                    : isToday
                    ? 'bg-gray-100 border-2 border-dashed border-gray-300'
                    : 'bg-gray-100'
                }`}
              />
              <span className={`text-[10px] font-bold ${isToday ? 'text-gray-700' : 'text-gray-400'}`}>
                {label}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
