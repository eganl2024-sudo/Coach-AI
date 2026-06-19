'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface Completion {
  date: string;
  drills_completed?: string[];
}

interface ActivityHeatmapProps {
  completions: Completion[];
}

export function ActivityHeatmap({ completions }: ActivityHeatmapProps) {
  // Build 84 days (12 weeks * 7 days) ending today in local time
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const days: { dateStr: string; dayOfWeek: number; weekIndex: number; count: number }[] = [];

  for (let offset = -83; offset <= 0; offset++) {
    const d = new Date(today);
    d.setDate(d.getDate() + offset);
    const dateStr = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;

    // Day of week mapping: Mon (0) to Sun (6)
    let dayOfWeek = d.getDay() - 1; // Mon = 0, Sun = -1
    if (dayOfWeek === -1) dayOfWeek = 6;

    const dayIndex = offset + 83; // 0 to 83
    const weekIndex = Math.floor(dayIndex / 7);

    // Find all completions matching this date
    const dayCompletions = (completions || []).filter(c => c.date === dateStr);
    let drillCount = 0;
    dayCompletions.forEach(c => {
      drillCount += c.drills_completed ? c.drills_completed.length : 1;
    });

    days.push({
      dateStr,
      dayOfWeek,
      weekIndex,
      count: drillCount,
    });
  }

  // Derive month labels at the top of each week column
  const monthLabels: { text: string; x: number }[] = [];
  let lastMonth = -1;

  for (let col = 0; col < 12; col++) {
    const midDayIdx = col * 7 + 3;
    if (midDayIdx < days.length) {
      const day = days[midDayIdx];
      const [, m] = day.dateStr.split('-').map(Number);
      if (m !== lastMonth) {
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        monthLabels.push({
          text: months[m - 1],
          x: col * 12,
        });
        lastMonth = m;
      }
    }
  }

  return (
    <div className="flex items-start gap-1 py-1 max-w-full select-none">
      {/* Day of Week Labels (Mon, Wed, Fri aligned absolutely with rows) */}
      <div className="relative w-8 h-[84px] text-[8px] text-muted-foreground font-semibold tracking-wide uppercase select-none shrink-0">
        <span className="absolute top-[0px] left-0 leading-none">Mon</span>
        <span className="absolute top-[24px] left-0 leading-none">Wed</span>
        <span className="absolute top-[48px] left-0 leading-none">Fri</span>
      </div>

      {/* SVG Grid */}
      <div className="flex-1 overflow-x-auto scrollbar-none">
        <svg
          viewBox="0 -12 144 84"
          width="144"
          height="96"
          className="overflow-visible block select-none"
        >
          {/* Month labels at top */}
          {monthLabels.map((lbl, idx) => (
            <text
              key={idx}
              x={lbl.x}
              y="-4"
              fontSize="7"
              fill="hsl(0 0% 45%)"
              fontWeight="semibold"
              className="tracking-tight"
            >
              {lbl.text}
            </text>
          ))}

          {/* Grid Cells */}
          {days.map((day, idx) => {
            const x = day.weekIndex * 12;
            const y = day.dayOfWeek * 12;
            const hasActivity = day.count > 0;

            // Opacity mapping based on drill counts
            let opacity = 1.0;
            let fillClass = 'fill-secondary/80';

            if (hasActivity) {
              fillClass = 'fill-primary';
              if (day.count === 1) {
                opacity = 0.4;
              } else if (day.count <= 3) {
                opacity = 0.7;
              } else {
                opacity = 1.0;
              }
            }

            return (
              <rect
                key={idx}
                x={x}
                y={y}
                width="10"
                height="10"
                rx="2"
                className={cn("transition-all duration-300", fillClass)}
                style={{ fillOpacity: opacity }}
              >
                <title>{`${day.dateStr}: ${day.count} drills`}</title>
              </rect>
            );
          })}
        </svg>
      </div>
    </div>
  );
}
