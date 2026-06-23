'use client';

import { useState, useEffect } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { TrainingWeek } from '@/lib/types/player';
import { SessionCard } from './SessionCard';
import { cn } from '@/lib/utils';

function timeAgo(dateStr: string): string {
  const diffDays = Math.floor((Date.now() - new Date(dateStr).getTime()) / 86_400_000);
  if (diffDays <= 0) return 'today';
  if (diffDays === 1) return 'yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;
  const weeks = Math.floor(diffDays / 7);
  if (weeks === 1) return '1 week ago';
  if (weeks < 5) return `${weeks} weeks ago`;
  const months = Math.floor(diffDays / 30);
  return months === 1 ? '1 month ago' : `${months} months ago`;
}

interface PastWeeksAccordionProps {
  weeks: TrainingWeek[];
}

export function PastWeeksAccordion({ weeks }: PastWeeksAccordionProps) {
  const [expandedWeekNum, setExpandedWeekNum] = useState<number | null>(null);

  useEffect(() => {
    setExpandedWeekNum(null);
  }, [weeks.length]);

  if (!weeks || weeks.length === 0) return null;

  const handleToggle = (weekNum: number) => {
    setExpandedWeekNum(expandedWeekNum === weekNum ? null : weekNum);
  };

  return (
    <div className="space-y-4">
      {weeks.map((week) => {
        const isExpanded = expandedWeekNum === week.week_number;
        const totalSessions = week.sessions?.length ?? 0;
        
        return (
          <div key={week.week_number} className="border border-border/50 rounded-xl overflow-hidden bg-card/30">
            {/* Accordion trigger row */}
            <div
              onClick={() => handleToggle(week.week_number)}
              className="flex items-center justify-between p-4 cursor-pointer hover:bg-secondary/30 select-none transition-colors"
            >
              <div className="flex items-center gap-3">
                <span className="text-sm font-semibold text-foreground">
                  Week {week.week_number}
                </span>
                <span className="text-xs text-muted-foreground">
                  • {totalSessions} {totalSessions === 1 ? 'session' : 'sessions'}
                </span>
                <span className="text-xs text-muted-foreground hidden sm:inline">
                  • {timeAgo(week.generated_date)}
                </span>
              </div>
              <div>
                {isExpanded ? (
                  <ChevronUp className="w-4 h-4 text-muted-foreground" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-muted-foreground" />
                )}
              </div>
            </div>

            {/* Accordion content */}
            <div className={cn(
              "grid transition-all duration-300 ease-in-out border-t border-border/50",
              isExpanded ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0 pointer-events-none"
            )}>
              <div className="overflow-hidden bg-card/10">
                <div className="p-4 space-y-3">
                  {week.sessions.map((session, idx) => (
                    <SessionCard
                      key={session.day_number || idx}
                      session={session}
                      isCurrent={false}
                      isNext={false}
                      weekNumber={week.week_number}
                      forceCollapsed={!isExpanded}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
