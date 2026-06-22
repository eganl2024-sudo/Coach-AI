import Link from 'next/link';
import Image from 'next/image';
import { redirect } from 'next/navigation';
import { getCurrentUser } from '@/lib/session';
import { getDrillById } from '@/lib/data/getDrills';
import { PRESENTER_MAP } from '@/lib/data/presenters';
import { CATEGORY_COLORS, DIFFICULTY_COLORS, INTENSITY_COLORS } from '@/lib/data/categories';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { cn } from '@/lib/utils';
import { getUserData } from '@/lib/data/getUserData';
import type { DrillCompletionLog } from '@/lib/types/player';
import DrillCompleteButton from '@/components/drills/DrillCompleteButton';

// Helper to extract YouTube video ID
function getYouTubeId(url: string): string | null {
  if (!url) return null;
  const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
  const match = url.match(regExp);
  return (match && match[2].length === 11) ? match[2] : null;
}

interface PageProps {
  params: Promise<{
    drill_id: string;
  }>;
}

export default async function DrillDetailPage({ params }: PageProps) {
  const username = await getCurrentUser();
  if (!username) {
    redirect('/login');
  }

  const { drill_id } = await params;
  const drill = await getDrillById(drill_id);

  if (!drill) {
    return (
      <div className="max-w-2xl mx-auto text-center py-16 space-y-4">
        <h2 className="text-xl font-bold text-white">Drill not found</h2>
        <p className="text-muted-foreground text-sm">
          The drill you are looking for does not exist or has been removed.
        </p>
        <Link
          href="/drills"
          className="inline-block text-primary hover:underline text-sm font-semibold"
        >
          ← Back to Drill Library
        </Link>
      </div>
    );
  }

  const presenter = drill.presenter_id ? PRESENTER_MAP[drill.presenter_id] : null;
  const catColor = CATEGORY_COLORS[drill.category] || 'bg-secondary text-muted-foreground border-border';
  const diffColor = DIFFICULTY_COLORS[drill.difficulty?.toLowerCase()] || 'bg-secondary text-muted-foreground';
  const intensityDot = INTENSITY_COLORS[drill.intensity?.toLowerCase()] || 'bg-green-500';
  const videoId = getYouTubeId(drill.video_url);

  // Split pipe-separated coaching cues / common mistakes
  const cues = drill.coaching_cues
    ? drill.coaching_cues.split('|').map(c => c.trim()).filter(Boolean)
    : drill.coaching_points
      ? drill.coaching_points.split('|').map(c => c.trim()).filter(Boolean)
      : [];

  const mistakes = drill.common_mistakes
    ? drill.common_mistakes.split('|').map(m => m.trim()).filter(Boolean)
    : [];

  // Fetch completions for the current user
  const drillCompletionLog = await getUserData<DrillCompletionLog>(
    username,
    'drill_completions'
  );

  const todayStr = new Date().toISOString().slice(0, 10);
  const alreadyDoneToday = drillCompletionLog?.completions?.some(
    c => c.drill_id === drill_id && c.date === todayStr
  ) ?? false;

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* 1. Back Navigation */}
      <div>
        <Link
          href="/drills"
          className="text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors"
        >
          ← Back to Drill Library
        </Link>
      </div>

      {/* 2. Header Block */}
      <div className="space-y-4">
        <div className="flex flex-wrap items-center gap-3">
          <Badge className={cn("text-xs font-semibold border", catColor)}>
            {drill.category}
          </Badge>
          {drill.series_name && (
            <span className="text-xs text-muted-foreground">
              Part of: <span className="text-foreground font-semibold">{drill.series_name}</span> (Order {drill.series_order})
            </span>
          )}
        </div>
        
        <h1 className="text-3xl font-black text-foreground tracking-tight sm:text-4xl">
          {drill.drill_name}
        </h1>

        {/* Presenter Profile */}
        {presenter && (
          <div className="flex items-center gap-3 bg-card/30 p-2.5 rounded-lg border border-border/30 w-fit">
            <Avatar className="w-8 h-8">
              <AvatarFallback className="bg-primary/20 text-primary text-xs font-bold">
                {presenter.initials}
              </AvatarFallback>
            </Avatar>
            <div className="text-xs">
              <p className="font-semibold text-foreground">{presenter.name}</p>
              <p className="text-muted-foreground">{presenter.role}</p>
            </div>
          </div>
        )}
      </div>

      {/* 3. Meta Grid Row */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3 bg-card/20 border border-border/50 rounded-xl p-4">
        <div>
          <p className="text-[10px] uppercase font-semibold tracking-wider text-muted-foreground">Duration</p>
          <p className="text-sm font-bold text-foreground mt-0.5">{drill.duration_minutes} min</p>
        </div>
        <div>
          <p className="text-[10px] uppercase font-semibold tracking-wider text-muted-foreground">Difficulty</p>
          <Badge variant="secondary" className={cn("text-[10px] px-1.5 py-0 mt-1 font-semibold border-transparent", diffColor)}>
            {drill.difficulty}
          </Badge>
        </div>
        <div>
          <p className="text-[10px] uppercase font-semibold tracking-wider text-muted-foreground">Intensity</p>
          <div className="flex items-center gap-1.5 mt-1">
            <span className={cn("w-2 h-2 rounded-full", intensityDot)} />
            <span className="text-sm font-bold text-foreground capitalize">{drill.intensity}</span>
          </div>
        </div>
        <div>
          <p className="text-[10px] uppercase font-semibold tracking-wider text-muted-foreground">Players</p>
          <p className="text-sm font-bold text-foreground mt-0.5">
            {drill.solo_possible && drill.players_max === 1 ? 'Solo' : `${drill.players_min}–${drill.players_max}`}
          </p>
        </div>
        <div>
          <p className="text-[10px] uppercase font-semibold tracking-wider text-muted-foreground">Equipment</p>
          <p className="text-sm font-bold text-foreground mt-0.5 truncate" title={drill.min_equipment || drill.equipment}>
            {drill.min_equipment || drill.equipment || 'Ball'}
          </p>
        </div>
        <div>
          <p className="text-[10px] uppercase font-semibold tracking-wider text-muted-foreground">Space Required</p>
          <p className="text-sm font-bold text-foreground mt-0.5 truncate" title={drill.space_required}>
            {drill.space_required || 'Standard Grid'}
          </p>
        </div>
      </div>

      {/* 4. Two-Column Layout (Media vs Details) */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
        {/* Left: Media Embeds */}
        <div className="md:col-span-6 space-y-4">
          {videoId ? (
            <div className="aspect-video w-full rounded-lg overflow-hidden border border-border/50">
              <iframe
                src={`https://www.youtube.com/embed/${videoId}`}
                title={drill.drill_name}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                className="w-full h-full border-0"
              />
            </div>
          ) : drill.diagram_url ? (
            <div className="w-full rounded-lg overflow-hidden border border-border/50 bg-card/20 relative">
              <Image
                src={drill.diagram_url}
                alt={`${drill.drill_name} diagram`}
                width={600}
                height={400}
                className="w-full h-auto object-cover"
              />
            </div>
          ) : (
            <div className="aspect-video w-full flex flex-col items-center justify-center rounded-lg border border-border/50 bg-card/20 p-6 text-center">
              <span className="text-lg font-bold text-muted-foreground">Video coming soon</span>
              <p className="text-xs text-muted-foreground/60 mt-1">
                Visual demo is currently being processed for this drill.
              </p>
            </div>
          )}

          {/* Render diagram below if we had both video AND diagram */}
          {videoId && drill.diagram_url && (
            <div className="w-full rounded-lg overflow-hidden border border-border/50 bg-card/20 relative">
              <Image
                src={drill.diagram_url}
                alt={`${drill.drill_name} diagram`}
                width={600}
                height={400}
                className="w-full h-auto object-cover"
              />
            </div>
          )}
        </div>

        {/* Right: Written Details */}
        <div className="md:col-span-6 space-y-6">
          {/* About */}
          <div className="space-y-2">
            <h2 className="text-base font-bold text-foreground tracking-tight">About this drill</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {drill.description}
            </p>
          </div>

          {/* Setup */}
          {drill.setup_data && (
            <div className="space-y-2">
              <h2 className="text-base font-bold text-foreground tracking-tight">Setup</h2>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {drill.setup_data}
              </p>
            </div>
          )}

          {/* Equipment list */}
          {drill.equipment && (
            <div className="space-y-2">
              <h2 className="text-base font-bold text-foreground tracking-tight">Equipment</h2>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {drill.equipment}
              </p>
            </div>
          )}

          {/* Hook context (Why it matters) */}
          {drill.game_application && (
            <div className="border-l-4 border-primary pl-4 py-1.5 italic bg-primary/[0.02]">
              <h3 className="text-xs font-semibold text-primary uppercase tracking-wider not-italic mb-1">
                Why it matters
              </h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {drill.game_application}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* 5. Full-width Lists */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-6 border-t border-border/30">
        {/* Coaching Cues */}
        {cues.length > 0 && (
          <div className="space-y-3">
            <h2 className="text-base font-bold text-foreground tracking-tight">Coaching Cues</h2>
            <ul className="space-y-2.5">
              {cues.map((cue, idx) => (
                <li key={idx} className="flex items-start text-sm text-muted-foreground leading-normal">
                  <span className="text-primary font-bold mr-2.5 shrink-0 select-none">✓</span>
                  <span>{cue}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Common Mistakes */}
        {mistakes.length > 0 && (
          <div className="space-y-3">
            <h2 className="text-base font-bold text-foreground tracking-tight">Common Mistakes</h2>
            <ul className="space-y-2.5">
              {mistakes.map((mistake, idx) => (
                <li key={idx} className="flex items-start text-sm text-muted-foreground leading-normal">
                  <span className="text-destructive font-bold mr-2.5 shrink-0 select-none">✕</span>
                  <span>{mistake}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* 6. Drill Complete Action Panel */}
      <div className="pt-6 border-t border-border/30 max-w-sm">
        <p className="text-xs text-muted-foreground mb-3">
          Completed this drill today? Log it to track your progress.
        </p>
        <DrillCompleteButton
          drillId={drill_id}
          drillName={drill.drill_name}
          initialCompleted={alreadyDoneToday}
        />
      </div>
    </div>
  );
}
