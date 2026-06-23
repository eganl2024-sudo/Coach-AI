'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui/button';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div
      className="min-h-screen flex flex-col items-center justify-center px-4 text-center space-y-6"
      style={{ background: 'radial-gradient(ellipse at top, #0d1f0f 0%, #0f1117 60%)' }}
    >
      <div className="text-4xl font-black tracking-tight text-white select-none">
        Footy Mentor
      </div>
      <div className="space-y-2">
        <h1 className="text-xl font-bold text-white">Something went wrong</h1>
        <p className="text-sm text-muted-foreground max-w-sm">
          An unexpected error occurred. Your training data is safe — try refreshing the page.
        </p>
      </div>
      <div className="flex gap-3">
        <Button
          onClick={reset}
          className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold"
        >
          Try again
        </Button>
        <Button
          variant="outline"
          onClick={() => window.location.href = '/'}
          className="border-border text-foreground hover:bg-muted"
        >
          Go home
        </Button>
      </div>
      {error.digest && (
        <p className="text-xs text-muted-foreground/50">Error ID: {error.digest}</p>
      )}
    </div>
  );
}
