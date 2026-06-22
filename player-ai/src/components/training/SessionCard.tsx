'use client';

import { useState, useEffect, useTransition } from 'react';
import Link from 'next/link';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { TrainingSession } from '@/lib/types/player';
import { cn } from '@/lib/utils';
import { completeSessionAction } from '@/lib/actions/training';

interface SessionCardProps {
  session: TrainingSession;
  isCurrent: boolean;
  isNext: boolean;
  weekNumber: number;
  forceCollapsed?: boolean;
}

export function SessionCard({ session, isCurrent, isNext, weekNumber, forceCollapsed }: SessionCardProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (forceCollapsed) {
      setIsOpen(false);
    }
  }, [forceCollapsed]);

  const totalDrills = session.drills?.length ?? 0;

  const getIntensityDotColor = (intensity: string) => {
    switch (intensity?.toLowerCase()) {
      case 'low':
        return 'bg-green-500';
      case 'medium':
      case 'moderate':
        return 'bg-yellow-400';
      case 'high':
        return 'bg-red-500';
      default:
        return 'bg-green-500';
    }
  };

  return (
    <Card className={cn(
      "border-border/50 bg-card/50 backdrop-blur-sm overflow-hidden transition-all duration-200",
      isNext && "border-primary/40 shadow-lg shadow-primary/5",
      !isCurrent && session.completed && "opacity-70"
    )}>
      <div
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between p-4 cursor-pointer hover:bg-secondary/40 select-none"
      >
        <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-widest">
              Day {session.day_number}
            </span>
            <Badge variant="secondary" className="bg-secondary/80 text-muted-foreground text-[10px] font-bold px-2 py-0.5">
              {session.duration_minutes} min
            </Badge>
          </div>
          <h3 className="font-bold text-foreground text-sm sm:text-base">
            {session.name.replace(/^.+Development Plan\s*[-–]\s*/i, '')}
          </h3>
        </div>

        <div className="flex items-center gap-3">
          {session.completed ? (
            <Badge className="text-primary bg-primary/15 hover:bg-primary/20 border-transparent text-[11px] font-semibold">
              ✓ Complete
            </Badge>
          ) : !isCurrent ? (
            <div className="flex items-center gap-1.5 shrink-0">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500/60" />
              <span className="text-xs text-muted-foreground font-semibold">Skipped</span>
            </div>
          ) : isNext ? (
            <Badge className="text-primary bg-primary/15 hover:bg-primary/20 border-transparent text-[11px] font-semibold animate-pulse">
              Up Next
            </Badge>
          ) : null}
          {isOpen ? (
            <ChevronUp className="w-4 h-4 text-muted-foreground" />
          ) : (
            <ChevronDown className="w-4 h-4 text-muted-foreground" />
          )}
        </div>
      </div>

      <div className={cn(
        "grid transition-all duration-300 ease-in-out border-t border-border/50",
        isOpen ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0 pointer-events-none"
      )}>
        <div className="overflow-hidden">
          <CardContent className="p-4 space-y-3 bg-card/30">
            {totalDrills === 0 ? (
              <p className="text-xs text-muted-foreground text-center py-4">No drills scheduled for this session.</p>
            ) : (
              <div className="divide-y divide-border/30">
                {session.drills.map((drill, idx) => (
                  <div key={drill.drill_id || idx} className="py-2.5 first:pt-0 last:pb-0 flex items-start justify-between gap-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <Link href={`/drills/${drill.drill_id}`} className="text-sm font-semibold text-foreground hover:text-primary transition-colors">
                          {drill.drill_name}
                        </Link>
                        <Badge variant="secondary" className="text-[10px] px-1.5 py-0">
                          {drill.category}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground max-w-2xl leading-relaxed">
                        {drill.description}
                      </p>
                      {drill.coaching_points && (
                        <p className="text-[11px] text-primary/80 font-medium italic">
                          Cues: {drill.coaching_points}
                        </p>
                      )}
                    </div>
                    
                    <div className="flex flex-col items-end shrink-0 gap-1">
                      <span className="text-xs text-muted-foreground font-medium">
                        {drill.allocated_time || drill.duration_minutes} min
                      </span>
                      <div className="flex items-center gap-1.5">
                        <span className="text-[10px] text-muted-foreground capitalize">
                          {drill.intensity}
                        </span>
                        <span className={cn("w-2 h-2 rounded-full", getIntensityDotColor(drill.intensity))} />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {isCurrent && !session.completed && (
              <div className="pt-3 border-t border-border/30 mt-3 flex flex-col gap-2">
                <Button
                  onClick={() => {
                    setError(null);
                    startTransition(async () => {
                      const res = await completeSessionAction(weekNumber, session.day_number);
                      if (!res.success) {
                        setError(res.error ?? 'Failed to complete session.');
                      }
                    });
                  }}
                  disabled={isPending}
                  className="w-full font-semibold text-sm py-2.5 rounded-lg bg-primary text-primary-foreground hover:bg-primary/95"
                >
                  {isPending ? 'Marking complete...' : '✓ Mark Session Complete'}
                </Button>
                {error && (
                  <p className="text-destructive text-xs text-center">{error}</p>
                )}
              </div>
            )}
          </CardContent>
        </div>
      </div>
    </Card>
  );
}
