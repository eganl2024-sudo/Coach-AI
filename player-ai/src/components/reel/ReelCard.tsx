'use client';

import React, { useState } from 'react';
import { Play, X, Loader2, MessageSquare, ExternalLink } from 'lucide-react';
import { deleteReelAction, submitForReviewAction } from '@/lib/actions/reel';
import type { ReelSubmission } from '@/lib/types/reel';
import { PRESENTER_MAP } from '@/lib/data/presenters';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';

interface ReelCardProps {
  reel: ReelSubmission;
  signedUrl: string | null;
}

export default function ReelCard({ reel, signedUrl }: ReelCardProps) {
  const [showPlayer, setShowPlayer] = useState(false);
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);

  // Review modal state
  const [selectedPresenter, setSelectedPresenter] = useState('KC-01');
  const [question, setQuestion] = useState('');

  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', {
        month: 'long',
        day: 'numeric',
        year: 'numeric',
      });
    } catch {
      return dateStr;
    }
  };

  const handleDelete = async () => {
    const ok = window.confirm('Are you sure you want to delete this clip?');
    if (!ok) return;

    setDeleting(true);
    try {
      const res = await deleteReelAction(reel.id);
      if (!res.success) {
        alert(res.error || 'Failed to delete clip');
      }
    } catch (err: any) {
      alert(err.message || 'An error occurred during deletion.');
    } finally {
      setDeleting(false);
    }
  };

  const handleReviewSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await submitForReviewAction(reel.id, selectedPresenter, question);
      if (res.success) {
        setShowReviewModal(false);
        setQuestion('');
      } else {
        alert(res.error || 'Failed to submit review request.');
      }
    } catch (err: any) {
      alert(err.message || 'An error occurred.');
    } finally {
      setSubmitting(false);
    }
  };

  const presenterKeys = ['KC-01', 'UNLV-01', 'TFC-01', 'YOU-01'];

  return (
    <div className="bg-card/40 border border-border/50 rounded-xl overflow-hidden shadow-md p-4 relative flex flex-col justify-between space-y-4 backdrop-blur-md transition-all hover:border-border/80">
      
      {/* Top Row: Title, Date, and Delete Button */}
      <div className="flex justify-between items-start pr-8">
        <div className="space-y-1">
          <h3 className="font-semibold text-foreground text-sm line-clamp-1">{reel.title}</h3>
          <p className="text-xs text-muted-foreground">{formatDate(reel.uploaded_at)}</p>
        </div>
        
        <button
          type="button"
          onClick={handleDelete}
          disabled={deleting}
          className="absolute top-4 right-4 p-1 rounded-md text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
          title="Delete Clip"
        >
          {deleting ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <X className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* Video Section */}
      <div className="relative aspect-video w-full overflow-hidden rounded-lg bg-black/40 border border-border/30">
        {signedUrl ? (
          showPlayer ? (
            <video
              src={signedUrl}
              controls
              autoPlay
              className="w-full h-full rounded-lg object-contain"
            />
          ) : (
            <div
              onClick={() => setShowPlayer(true)}
              className="w-full h-full flex flex-col items-center justify-center cursor-pointer group hover:bg-black/60 transition-colors relative"
            >
              <div className="w-12 h-12 rounded-full bg-primary/80 group-hover:bg-primary text-white flex items-center justify-center transition-all transform group-hover:scale-110 shadow-lg">
                <Play className="w-5 h-5 fill-current ml-0.5" />
              </div>
              <span className="absolute bottom-2 right-2 bg-black/80 px-2 py-0.5 rounded text-[10px] text-muted-foreground">
                Play Clip
              </span>
            </div>
          )
        ) : (
          <div className="w-full h-full flex items-center justify-center text-muted-foreground text-xs font-medium">
            Video unavailable
          </div>
        )}
      </div>

      {/* Notes Section */}
      {reel.notes && (
        <div className="text-xs bg-secondary/15 p-2.5 rounded-lg border border-border/20">
          <span className="font-bold text-muted-foreground block mb-0.5">Notes:</span>
          <p className="text-muted-foreground whitespace-pre-wrap leading-relaxed">{reel.notes}</p>
        </div>
      )}

      {/* Expanded Feedback Display (for reviewed status) */}
      {showFeedback && reel.review_status === 'reviewed' && (
        <div className="text-xs bg-emerald-500/10 border border-emerald-500/20 p-3 rounded-lg text-emerald-300 space-y-1.5 animate-in fade-in duration-200">
          <div className="font-semibold text-emerald-400 flex items-center gap-1.5">
            <MessageSquare className="w-3.5 h-3.5" />
            <span>Feedback from {PRESENTER_MAP[reel.reviewer_id]?.name || 'Presenter'}:</span>
          </div>
          <p className="whitespace-pre-wrap leading-relaxed">{reel.reviewer_response || 'No response provided.'}</p>
          {reel.reviewed_at && (
            <span className="block text-[10px] text-emerald-500/70 mt-1">
              Reviewed on {formatDate(reel.reviewed_at)}
            </span>
          )}
        </div>
      )}

      {/* Status Row (Bottom) */}
      <div className="flex justify-between items-center pt-2 border-t border-border/30">
        <div>
          {reel.review_status === 'pending' && (
            <Badge variant="outline" className="border-yellow-500/30 bg-yellow-500/10 text-yellow-500 gap-1 text-[10px] h-6 px-2">
              <span>⏳</span> Review Pending
            </Badge>
          )}
          {reel.review_status === 'reviewed' && (
            <Badge variant="outline" className="border-emerald-500/30 bg-emerald-500/10 text-emerald-400 gap-1 text-[10px] h-6 px-2">
              <span>✓</span> Reviewed
            </Badge>
          )}
        </div>

        <div>
          {reel.review_status === 'not_submitted' && (
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setShowReviewModal(true)}
              className="text-xs border-border/60 hover:bg-secondary/40 text-foreground"
            >
              Submit for Review →
            </Button>
          )}

          {reel.review_status === 'pending' && (
            <span className="text-xs text-muted-foreground font-medium">
              Awaiting feedback
            </span>
          )}

          {reel.review_status === 'reviewed' && (
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setShowFeedback(!showFeedback)}
              className="text-xs border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10"
            >
              {showFeedback ? 'Hide Feedback' : 'View Feedback'}
            </Button>
          )}
        </div>
      </div>

      {/* Review Submission Modal Overlay */}
      {showReviewModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
          <div className="bg-card border border-border/80 rounded-xl max-w-md w-full p-6 relative flex flex-col space-y-4 shadow-2xl animate-in zoom-in-95 duration-150">
            <div className="space-y-1">
              <h2 className="text-lg font-bold text-foreground">Submit for Athlete Review</h2>
              <p className="text-xs text-muted-foreground">
                Get professional feedback on your clip. $25–35/submission — coming soon.
              </p>
            </div>

            <form onSubmit={handleReviewSubmit} className="space-y-4">
              {/* Presenter Selector */}
              <div className="space-y-2">
                <span className="text-xs font-semibold text-muted-foreground">Select Reviewer</span>
                <div className="grid grid-cols-2 gap-2">
                  {presenterKeys.map((key) => {
                    const presenter = PRESENTER_MAP[key];
                    if (!presenter) return null;
                    const isSelected = selectedPresenter === key;
                    return (
                      <label
                        key={key}
                        className={`flex items-center gap-2.5 p-2 rounded-lg border cursor-pointer transition-all ${
                          isSelected
                            ? 'border-primary bg-primary/10 ring-1 ring-primary'
                            : 'border-border/50 bg-secondary/10 hover:border-border/80 hover:bg-secondary/20'
                        }`}
                      >
                        <input
                          type="radio"
                          name="presenter"
                          value={key}
                          checked={isSelected}
                          onChange={() => setSelectedPresenter(key)}
                          className="hidden"
                        />
                        <Avatar className="w-7 h-7 shrink-0">
                          <AvatarFallback className="bg-primary/20 text-primary text-[10px] font-bold">
                            {presenter.initials}
                          </AvatarFallback>
                        </Avatar>
                        <div className="flex flex-col text-left truncate min-w-0">
                          <span className="text-[11px] font-semibold text-foreground truncate">{presenter.name}</span>
                          <span className="text-[9px] text-muted-foreground truncate">{presenter.team}</span>
                        </div>
                      </label>
                    );
                  })}
                </div>
              </div>

              {/* Question Textarea */}
              <div className="space-y-1.5 text-left">
                <label htmlFor="question" className="text-xs font-semibold text-muted-foreground">
                  What would you like feedback on?
                </label>
                <textarea
                  id="question"
                  rows={3}
                  required
                  placeholder="e.g. Is my body shape correct when receiving? Am I too slow to release?"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  className="flex w-full rounded-lg border border-border/50 bg-secondary/20 px-3 py-2 text-xs text-foreground shadow-xs placeholder:text-muted-foreground focus-visible:outline-hidden focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 resize-none"
                />
              </div>

              {/* Yellow Waitlist Banner */}
              <div className="bg-yellow-500/10 border border-yellow-500/20 text-yellow-500 rounded-lg p-3 text-xs text-left leading-relaxed">
                <strong>Coming Soon</strong>
                <p className="mt-0.5 text-yellow-500/90">
                  Paid review submissions are coming soon. Submit now to join the waitlist.
                </p>
              </div>

              {/* Buttons */}
              <div className="flex items-center justify-end gap-2 pt-2 border-t border-border/30">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setShowReviewModal(false)}
                  disabled={submitting}
                  className="text-xs h-9 px-4"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={submitting}
                  className="text-xs h-9 px-4 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold"
                >
                  {submitting ? 'Submitting...' : 'Join Waitlist'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
