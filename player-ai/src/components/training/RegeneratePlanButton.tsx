'use client';

import { useState, useTransition } from 'react';
import { regenerateCurrentWeekAction } from '@/lib/actions/training';

export default function RegeneratePlanButton() {
  const [isPending, startTransition] = useTransition();
  const [step, setStep] = useState<'idle' | 'confirm'>('idle');
  const [error, setError] = useState<string | null>(null);

  const handleConfirm = () => {
    setError(null);
    startTransition(async () => {
      const result = await regenerateCurrentWeekAction();
      if (result.success) {
        // Server revalidated — page will refresh automatically
        setStep('idle');
      } else {
        setError(result.error || 'Failed to regenerate plan.');
        setStep('idle');
      }
    });
  };

  if (step === 'confirm') {
    return (
      <div className="flex items-center gap-3 text-xs flex-wrap">
        <span className="text-muted-foreground">Completed sessions stay. Regenerate the rest?</span>
        <button
          onClick={handleConfirm}
          disabled={isPending}
          className="text-primary font-semibold hover:text-primary/80 transition-colors disabled:opacity-50 min-h-[44px] px-1"
        >
          {isPending ? 'Regenerating...' : 'Yes, regenerate'}
        </button>
        <button
          onClick={() => setStep('idle')}
          disabled={isPending}
          className="text-muted-foreground hover:text-foreground transition-colors min-h-[44px] px-1"
        >
          Cancel
        </button>
        {error && <p className="text-destructive text-xs">{error}</p>}
      </div>
    );
  }

  return (
    <button
      onClick={() => setStep('confirm')}
      className="text-xs text-muted-foreground/50 hover:text-muted-foreground transition-colors font-medium min-h-[44px] px-1"
    >
      Regenerate plan →
    </button>
  );
}
