'use client';

import React from 'react';
import { Timer, Target, Film, Camera } from 'lucide-react';
import type { ReelSubmission } from '@/lib/types/reel';
import ReelCard from './ReelCard';

interface ReelGridProps {
  reels: ReelSubmission[];
  signedUrls: Record<string, string>;
}

const TIPS = [
  { icon: Timer,  title: 'Keep it 2–4 minutes',      body: 'Coaches watch dozens of reels. Get to your best moments fast — no intros, no filler.' },
  { icon: Target, title: 'Lead with your best clip',  body: 'Put your strongest 30 seconds first. If a coach stops watching, make sure they saw your peak.' },
  { icon: Film,   title: 'Show range',                body: 'Include game footage, training drills, and set pieces. Variety shows coachability and versatility.' },
  { icon: Camera, title: 'Landscape, steady, clear',  body: 'Horizontal video from the sideline or end line. Coaches need to see your positioning and runs off the ball.' },
];

export default function ReelGrid({ reels, signedUrls }: ReelGridProps) {
  if (reels.length === 0) {
    return (
      <div className="space-y-3">
        <p className="text-xs text-muted-foreground font-semibold uppercase tracking-wider">What college coaches want to see</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {TIPS.map(tip => (
            <div key={tip.title} className="flex gap-3 p-4 rounded-xl border border-border/40 bg-card/20">
              <tip.icon className="w-4 h-4 shrink-0 text-primary mt-0.5" />
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
