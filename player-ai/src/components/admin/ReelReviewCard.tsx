'use client';

import { useState } from 'react';
import { submitReviewResponseAction } from '@/lib/actions/admin';
import type { ReelSubmission } from '@/lib/types/reel';

const REVIEWER_LABELS: Record<string, string> = {
  'KC-01': 'Mitch (KC)',
  'UNLV-01': 'Nick (UNLV)',
  'TFC-01': 'TFC Coach',
  'YOU-01': 'You',
};

interface Props {
  reel: ReelSubmission;
  signedUrl: string | null;
}

export default function ReelReviewCard({ reel, signedUrl }: Props) {
  const [expanded, setExpanded] = useState(reel.review_status === 'pending');
  const [response, setResponse] = useState(reel.reviewer_response ?? '');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [done, setDone] = useState(reel.review_status === 'reviewed');

  const statusColor =
    reel.review_status === 'reviewed'
      ? 'bg-primary/10 text-primary border-primary/20'
      : 'bg-yellow-500/10 text-yellow-400 border-yellow-400/20';

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    const result = await submitReviewResponseAction(reel.id, response);
    setSubmitting(false);
    if (result.success) {
      setDone(true);
    } else {
      setError(result.error ?? 'Failed to submit.');
    }
  }

  return (
    <div className="border border-border/50 rounded-xl bg-card/40 overflow-hidden">
      {/* Header row — always visible */}
      <button
        onClick={() => setExpanded(v => !v)}
        className="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-card/60 transition-colors"
      >
        <div className="flex items-center gap-4 min-w-0">
          <span
            className={`shrink-0 text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full border ${statusColor}`}
          >
            {done ? 'Reviewed' : 'Pending'}
          </span>
          <div className="min-w-0">
            <p className="text-sm font-bold text-white truncate">{reel.title}</p>
            <p className="text-xs text-muted-foreground">
              {reel.username} · {REVIEWER_LABELS[reel.reviewer_id] ?? reel.reviewer_id} ·{' '}
              {new Date(reel.uploaded_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
            </p>
          </div>
        </div>
        <span className="text-muted-foreground text-xs ml-4 shrink-0">{expanded ? '▲' : '▼'}</span>
      </button>

      {/* Expanded body */}
      {expanded && (
        <div className="px-5 pb-5 space-y-4 border-t border-border/30 pt-4">
          {/* Video */}
          {signedUrl ? (
            <video
              src={signedUrl}
              controls
              className="w-full max-h-72 rounded-lg bg-black"
              preload="metadata"
            />
          ) : (
            <div className="w-full h-32 rounded-lg bg-secondary/20 flex items-center justify-center text-sm text-muted-foreground">
              Video unavailable
            </div>
          )}

          {/* Player question */}
          <div className="space-y-1">
            <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
              Player's Question
            </p>
            <p className="text-sm text-foreground bg-secondary/20 rounded-lg px-4 py-3">
              {reel.review_question}
            </p>
          </div>

          {/* Notes */}
          {reel.notes && (
            <div className="space-y-1">
              <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                Notes
              </p>
              <p className="text-sm text-muted-foreground">{reel.notes}</p>
            </div>
          )}

          {/* Response */}
          {done ? (
            <div className="space-y-1">
              <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                Your Response
              </p>
              <p className="text-sm text-foreground bg-primary/5 border border-primary/20 rounded-lg px-4 py-3 whitespace-pre-wrap">
                {response || reel.reviewer_response}
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-3">
              <div className="space-y-1">
                <label className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                  Your Feedback
                </label>
                <textarea
                  value={response}
                  onChange={e => setResponse(e.target.value)}
                  rows={5}
                  placeholder="Write your coaching feedback here..."
                  className="w-full rounded-lg border border-border/50 bg-secondary/20 px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary/40 resize-y"
                  required
                />
              </div>
              {error && <p className="text-destructive text-xs">{error}</p>}
              <button
                type="submit"
                disabled={submitting}
                className="h-9 px-5 rounded-lg bg-primary hover:bg-primary/90 text-primary-foreground text-xs font-bold transition-colors disabled:opacity-60 cursor-pointer"
              >
                {submitting ? 'Submitting...' : 'Submit Feedback'}
              </button>
            </form>
          )}
        </div>
      )}
    </div>
  );
}
