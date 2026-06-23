'use client';

import React from 'react';
import type { ReelSubmission } from '@/lib/types/reel';
import ReelCard from './ReelCard';

interface ReelGridProps {
  reels: ReelSubmission[];
  signedUrls: Record<string, string>;
}

export default function ReelGrid({ reels, signedUrls }: ReelGridProps) {
  if (reels.length === 0) {
    return (
      <div className="space-y-3">
        <p className="text-xs text-muted-foreground font-semibold uppercase tracking-wider">What college coaches want to see</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {[
            { icon: '⏱', title: 'Keep it 2–4 minutes', body: 'Coaches watch dozens of reels. Get to your best moments fast — no intros, no filler.' },
            { icon: '🎯', title: 'Lead with your best clip', body: 'Put your strongest 30 seconds first. If a coach stops watching, make sure they saw your peak.' },
            { icon: '📐', title: 'Show range', body: 'Include game footage, training drills, and set pieces. Variety shows coachability and versatility.' },
            { icon: '🎥', title: 'Landscape, steady, clear', body: 'Horizontal video from the sideline or end line. Coaches need to see your positioning and runs off the ball.' },
          ].map(tip => (
            <div key={tip.title} className="flex gap-3 p-4 rounded-xl border border-border/40 bg-card/20">
              <span className="text-xl shrink-0">{tip.icon}</span>
              <div className="space-y-0.5 min-w-0">
                <p className="text-sm font-semibold text-foreground">{tip.title}</p>
                <p className="text-xs text-muted-foreground leading-relaxed">{tip.body}</p>
              </div>
            </div>
          ))}
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
