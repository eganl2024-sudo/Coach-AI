'use client';

import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { cn } from '@/lib/utils';
import type { PRESENTER_MAP } from '@/lib/data/presenters';
import type { FeedPost } from '@/lib/types/feed';

interface MentorFeedClientProps {
  posts: FeedPost[];
  presenterMap: typeof PRESENTER_MAP;
  playerPosition?: string;
}

const POSITION_OPTIONS = [
  'All Positions',
  'Goalkeeper',
  'Center Back',
  'Full Back',
  'Defensive Midfielder',
  'Central Midfielder',
  'Attacking Midfielder',
  'Winger',
  'Striker',
];

// Deterministic date formatting function to prevent hydration mismatch
function formatDate(dateStr: string): string {
  try {
    const parts = dateStr.split('-');
    if (parts.length !== 3) return dateStr;
    const year = parseInt(parts[0], 10);
    const monthIndex = parseInt(parts[1], 10) - 1;
    const day = parseInt(parts[2], 10);
    const months = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];
    if (monthIndex >= 0 && monthIndex < 12) {
      return `${months[monthIndex]} ${day}, ${year}`;
    }
    return dateStr;
  } catch {
    return dateStr;
  }
}

export function MentorFeedClient({ posts, presenterMap, playerPosition }: MentorFeedClientProps) {
  const [selectedPresenter, setSelectedPresenter] = useState<string>('All');
  const [selectedPosition, setSelectedPosition] = useState<string>(
    playerPosition ?? 'All Positions'
  );
  const [expandedPosts, setExpandedPosts] = useState<Set<string>>(new Set());

  const togglePost = (postId: string) => {
    setExpandedPosts(prev => {
      const next = new Set(prev);
      if (next.has(postId)) {
        next.delete(postId);
      } else {
        next.add(postId);
      }
      return next;
    });
  };

  // Find unique presenter IDs present in the posts
  const uniquePresenterIds = Array.from(new Set(posts.map((p) => p.presenter_id)));

  // Filter posts
  const visiblePosts = posts
    .filter(p =>
      selectedPresenter === 'All' || p.presenter_id === selectedPresenter
    )
    .filter(p => {
      if (selectedPosition === 'All Positions') return true;
      if (!p.position_tags?.trim()) return true; // universal posts
      const tags = p.position_tags.split('|').map(t => t.trim().toLowerCase());
      return tags.includes(selectedPosition.toLowerCase());
    });

  // Sort by date_posted descending
  const sortedPosts = [...visiblePosts].sort((a, b) => b.date_posted.localeCompare(a.date_posted));

  return (
    <div className="space-y-6">
      {/* Filter Tabs */}
      <div className="flex flex-wrap gap-2 pb-2 border-b border-border/30">
        {/* All Button */}
        <Button
          variant="outline"
          size="sm"
          onClick={() => setSelectedPresenter('All')}
          className={cn(
            "rounded-full transition-all text-xs font-semibold px-4 py-2 h-auto flex items-center gap-2",
            selectedPresenter === 'All'
              ? "bg-primary/15 text-primary border-primary hover:bg-primary/25 hover:text-primary"
              : "border-border/50 text-muted-foreground hover:text-foreground hover:bg-secondary/50"
          )}
        >
          All
        </Button>

        {/* Presenter Buttons */}
        {uniquePresenterIds.map((presId) => {
          const presenter = presenterMap[presId];
          const initials = presenter?.initials ?? presId.slice(0, 2);
          const name = presenter?.name ?? presId;
          const isActive = selectedPresenter === presId;

          return (
            <Button
              key={presId}
              variant="outline"
              size="sm"
              onClick={() => setSelectedPresenter(presId)}
              className={cn(
                "rounded-full transition-all text-xs font-semibold px-4 py-2 h-auto flex items-center gap-2",
                isActive
                  ? "bg-primary/15 text-primary border border-primary/30 hover:bg-primary/25 hover:text-primary"
                  : "border border-border/50 text-muted-foreground hover:text-foreground hover:bg-secondary/50"
              )}
            >
              <Avatar className="w-5 h-5 shrink-0">
                <AvatarFallback className="bg-primary/10 text-primary text-[9px] font-bold">
                  {initials}
                </AvatarFallback>
              </Avatar>
              <span className="hidden sm:inline">{name}</span>
            </Button>
          );
        })}
      </div>

      {/* Position Filter Dropdown */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-2">
        <span className="text-xs font-semibold text-muted-foreground shrink-0">
          Filter by position:
        </span>
        <div className="relative w-full sm:w-auto min-w-[180px]">
          <select
            value={selectedPosition}
            onChange={e => setSelectedPosition(e.target.value)}
            className="min-h-[44px] w-full rounded-lg border border-border/50 bg-secondary/20 px-2.5 py-1 text-sm outline-none transition-all focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-primary/20 text-foreground cursor-pointer appearance-none pr-8"
          >
            {POSITION_OPTIONS.map(pos => (
              <option key={pos} value={pos} className="bg-card text-foreground">{pos}</option>
            ))}
          </select>
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2.5 text-muted-foreground">
            <svg className="size-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
      </div>

      {/* Post cards grid */}
      <div className="max-w-3xl mx-auto space-y-4">
        {sortedPosts.length === 0 ? (
          <Card className="border-border/50 border-dashed bg-card/10">
            <CardContent className="py-12 text-center">
              <p className="text-muted-foreground text-sm">No updates in this feed.</p>
            </CardContent>
          </Card>
        ) : (
          sortedPosts.map((post) => {
            const presenter = presenterMap[post.presenter_id];
            const initials = presenter?.initials ?? post.presenter_id.slice(0, 2);
            const presenterName = presenter?.name ?? post.presenter_id;
            const presenterRole = presenter?.role ?? 'Coach';
            
            const postTags = post.tags ? post.tags.split('|').map((t) => t.trim()).filter(Boolean).slice(0, 4) : [];
            const posTags = post.position_tags ? post.position_tags.split('|').map((pt) => pt.trim()).filter(Boolean) : [];

            return (
              <Card
                key={post.post_id}
                onClick={() => post.body && !post.coming_soon && togglePost(post.post_id)}
                className={`border border-border/50 bg-card/40 hover:border-border hover:bg-card/65 transition-colors duration-150 backdrop-blur-sm overflow-hidden${post.body && !post.coming_soon ? ' cursor-pointer' : ''}`}
              >
                <CardContent className="p-5 space-y-4">
                  {/* Top Row: Presenter Info + Date */}
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-center gap-3">
                      <Avatar className="w-10 h-10">
                        <AvatarFallback className="bg-primary/20 text-primary text-xs font-bold">
                          {initials}
                        </AvatarFallback>
                      </Avatar>
                      <div className="text-left">
                        <p className="font-semibold text-sm text-foreground leading-tight">
                          {presenterName}
                        </p>
                        <p className="text-xs text-muted-foreground mt-0.5 truncate max-w-[160px]">
                          {presenterRole}
                        </p>
                      </div>
                    </div>
                    <span className="text-xs text-muted-foreground shrink-0 mt-0.5">
                      {formatDate(post.date_posted)}
                    </span>
                  </div>

                  {/* Title & Description */}
                  <div className="space-y-1.5">
                    <h3 className="font-bold text-base text-foreground tracking-tight leading-snug">
                      {post.title}
                    </h3>
                    <p className="text-sm text-muted-foreground leading-relaxed line-clamp-4">
                      {post.description}
                    </p>

                    {/* Full body text — only when expanded and body exists */}
                    {post.body && expandedPosts.has(post.post_id) && (
                      <div className="pt-2 space-y-3">
                        {post.body.split('\n\n').filter(p => p.trim()).map((paragraph, i) => (
                          <p key={i} className="text-sm text-muted-foreground leading-relaxed">
                            {paragraph.trim()}
                          </p>
                        ))}
                      </div>
                    )}

                    {/* Read more / Read less toggle */}
                    {post.body && !post.coming_soon && (
                      <button
                        onClick={(e) => { e.stopPropagation(); togglePost(post.post_id); }}
                        className="text-xs font-semibold text-primary hover:text-primary/80 transition-colors mt-1 block"
                      >
                        {expandedPosts.has(post.post_id) ? '↑ Read less' : 'Read more →'}
                      </button>
                    )}
                  </div>

                  {/* YouTube embed — only when video_url is set and post is published */}
                  {post.video_url && !post.coming_soon && (
                    <div className="rounded-xl overflow-hidden border border-border/30 bg-black/20">
                      <div className="relative w-full" style={{ paddingBottom: '56.25%' }}>
                        <iframe
                          src={post.video_url}
                          title={post.title}
                          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                          allowFullScreen
                          className="absolute inset-0 w-full h-full"
                          loading="lazy"
                        />
                      </div>
                    </div>
                  )}

                  {/* Tags Row */}
                  {postTags.length > 0 && (
                    <div className="flex flex-wrap gap-1.5">
                      {postTags.map((tag) => (
                        <Badge
                          key={tag}
                          variant="secondary"
                          className="bg-secondary text-muted-foreground text-[10px] px-2 py-0.5 rounded-md border-transparent"
                        >
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  )}

                  {/* Bottom Row: Positions + Status */}
                  <div className="flex items-center justify-between gap-4 pt-3 border-t border-border/30">
                    <div className="text-[11px] text-muted-foreground/70 font-medium truncate">
                      {posTags.length > 0 && <span className="text-muted-foreground/40 mr-1">For:</span>}
                      {posTags.join(' · ')}
                    </div>
                    
                    <div className="shrink-0">
                      {post.coming_soon ? (
                        <Badge className="bg-yellow-500/15 text-yellow-400 border border-yellow-500/30 text-[11px] font-semibold cursor-default">
                          Coming Soon
                        </Badge>
                      ) : post.video_url ? (
                        <Badge className="bg-primary/15 text-primary border border-primary/30 text-[11px] font-semibold cursor-default">
                          ▶ Video
                        </Badge>
                      ) : (
                        null
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })
        )}

        {/* Athlete2Athlete teaser banner */}
        <div className="mt-8 rounded-xl border border-primary/20 bg-primary/5 p-6 space-y-2 text-left">
          <h3 className="text-lg font-bold text-white">
            Athlete2Athlete — Coming Soon
          </h3>
          <p className="text-sm text-muted-foreground leading-relaxed max-w-2xl">
            Soon you will be able to submit your game footage directly to Mitch, Nick, or Liam 
            for a personal video review — and book a live 30-minute Q&A session with a current 
            college or professional player who plays your position.
          </p>
          <p className="text-xs text-muted-foreground/60 pt-1">
            Reel Reviews · Live Q&A · Position-Specific Mentorship
          </p>
        </div>
      </div>
    </div>
  );
}
