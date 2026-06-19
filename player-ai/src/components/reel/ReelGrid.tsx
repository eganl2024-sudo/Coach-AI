'use client';

import React from 'react';
import { Upload } from 'lucide-react';
import type { ReelSubmission } from '@/lib/types/reel';
import ReelCard from './ReelCard';

interface ReelGridProps {
  reels: ReelSubmission[];
  signedUrls: Record<string, string>;
}

export default function ReelGrid({ reels, signedUrls }: ReelGridProps) {
  if (reels.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 px-4 rounded-xl border border-dashed border-border/40 bg-card/20 text-center space-y-3">
        <div className="p-3 bg-secondary/30 rounded-full text-muted-foreground">
          <Upload className="w-6 h-6" />
        </div>
        <div className="space-y-1">
          <h3 className="font-semibold text-foreground text-sm">No clips yet</h3>
          <p className="text-xs text-muted-foreground">Upload your first clip above</p>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {reels.map((reel) => (
        <ReelCard
          key={reel.id}
          reel={reel}
          signedUrl={signedUrls[reel.id] ?? null}
        />
      ))}
    </div>
  );
}
