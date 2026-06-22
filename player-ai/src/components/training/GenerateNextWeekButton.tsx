'use client';

import React, { useState, useTransition } from 'react';
import { generateNextWeekAction } from '@/lib/actions/training';

interface GenerateNextWeekButtonProps {
  nextWeekNumber: number;
}

export default function GenerateNextWeekButton({ nextWeekNumber }: GenerateNextWeekButtonProps) {
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleGenerate = () => {
    setError(null);
    setSuccess(false);
    startTransition(async () => {
      try {
        const result = await generateNextWeekAction();
        if (result.success) {
          setSuccess(true);
        } else {
          setError(result.error || 'Failed to generate the next week.');
        }
      } catch (err: any) {
        setError(err.message || 'An unexpected error occurred.');
      }
    });
  };

  return (
    <div className="w-full space-y-2">
      <button
        type="button"
        onClick={handleGenerate}
        disabled={isPending || success}
        className="w-full py-3 rounded-xl bg-primary hover:bg-primary/90 text-primary-foreground font-bold text-sm flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isPending ? (
          <>
            <span className="animate-spin inline-block border-2 border-white/30 border-t-white rounded-full w-4 h-4" />
            Generating your next week...
          </>
        ) : success ? (
          '✓ New week generated! Loading...'
        ) : (
          `Generate Week ${nextWeekNumber} →`
        )}
      </button>
      {error && <p className="text-red-500 text-xs text-center">{error}</p>}
    </div>
  );
}
