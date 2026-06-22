'use client';

import React, { useState, useTransition } from 'react';
import { Button } from '@/components/ui/button';
import { completeDrillAction } from '@/lib/actions/training';

interface DrillCompleteButtonProps {
  drillId: string;
  drillName: string;
  initialCompleted?: boolean;
}

export default function DrillCompleteButton({
  drillId,
  drillName,
  initialCompleted = false,
}: DrillCompleteButtonProps) {
  const [completed, setCompleted] = useState<boolean>(initialCompleted);
  const [error, setError] = useState<string>('');
  const [isPending, startTransition] = useTransition();

  const handleComplete = () => {
    if (completed || isPending) return;

    startTransition(async () => {
      setError('');
      try {
        const result = await completeDrillAction(drillId, drillName);
        if (result.success || result.alreadyDone) {
          setCompleted(true);
        } else {
          setError(result.error ?? 'Failed to log completion.');
        }
      } catch (err: any) {
        setError(err.message || 'An unexpected error occurred.');
      }
    });
  };

  if (completed) {
    return (
      <div className="w-full bg-primary/10 border border-primary/30 rounded-lg py-3 text-center text-primary font-semibold text-sm select-none">
        ✓ Drill logged for today
      </div>
    );
  }

  return (
    <div className="w-full space-y-2">
      <Button
        type="button"
        disabled={isPending}
        onClick={handleComplete}
        className="w-full bg-primary text-primary-foreground font-semibold rounded-lg py-3 h-auto text-sm cursor-pointer select-none transition-all hover:bg-primary/90 disabled:opacity-50"
      >
        {isPending ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="animate-spin h-4 w-4 text-primary-foreground" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Logging completion...
          </span>
        ) : (
          'Mark Drill Complete'
        )}
      </Button>
      {error && (
        <p className="text-destructive text-xs text-center font-medium mt-1">
          {error}
        </p>
      )}
    </div>
  );
}
