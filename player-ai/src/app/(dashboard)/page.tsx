import { redirect } from 'next/navigation';
import Link from 'next/link';
import { getCurrentUser } from '@/lib/session';
import { getUserData } from '@/lib/data/getUserData';
import { calculateRRS } from '@/lib/utils/calculateRRS';
import { getAllDrills } from '@/lib/data/getDrills';
import {
  calculateStreak,
  getLatestRRS,
  getRRSDelta,
  getNextSession,
  getTotalDrillsCompleted,
} from '@/lib/utils/training';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import RRSSparkline from '@/components/dashboard/RRSSparkline';
import type {
  AthleteProfile,
  WeeklyTrainingPlan,
  RRSHistory,
  CompletionLog,
} from '@/lib/types/player';
import { PRESENTER_MAP } from '@/lib/data/presenters';
import { SEED_POSTS } from '@/lib/data/feedPosts';

export const metadata = {
  title: 'Dashboard',
};

export default async function DashboardPage() {
  const username = await getCurrentUser();
  if (!username) {
    redirect('/login');
  }

  // Fetch Supabase data keys in parallel
  const [profile, plan, rrsHistory, completionLog, drills] = await Promise.all([
    getUserData<AthleteProfile>(username, 'athlete_profile'),
    getUserData<WeeklyTrainingPlan>(username, 'weekly_training_plan'),
    getUserData<RRSHistory>(username, 'rrs_history'),
    getUserData<CompletionLog>(username, 'completion_log'),
    getAllDrills(),
  ]);

  // Fallbacks
  const activeProfile: AthleteProfile = profile ?? {
    name: username,
    age: 14,
    preferred_foot: 'Right',
    position: 'Player',
    secondary_position: 'Midfielder',
    level: 'Club',
    target_level: 'Elite',
    sessions_per_week: 3,
    session_duration: 60,
    focus_areas: ['Dribbling', 'Passing'],
    equipment_available: ['Cones', 'Ball'],
    age_group: 'U15',
    created_date: new Date().toISOString(),
  };

  const streak = completionLog ? calculateStreak(completionLog) : 0;
  const drillsCompleted = completionLog ? getTotalDrillsCompleted(completionLog) : 0;

  const latestRRS = rrsHistory ? getLatestRRS(rrsHistory) : null;
  const rrsDelta = rrsHistory ? getRRSDelta(rrsHistory) : null;

  const nextSession = plan ? getNextSession(plan) : null;


  const rrsResult = profile && completionLog
    ? calculateRRS(profile, completionLog, plan, drills, rrsHistory)
    : null;
  const nextActions = rrsResult?.nextActions ?? [];

  // Compute milestones
  const profileComplete = !!(profile?.name);
  const planComplete = !!(plan?.weeks && plan.weeks.length > 0 && plan.weeks[0]?.sessions?.length > 0);
  const firstSessionComplete = !!(completionLog && completionLog.completions.length > 0);
  const rrsUnlocked = !!(rrsResult?.unlocked);
  const allMilestonesComplete = profileComplete && planComplete && firstSessionComplete && rrsUnlocked;
  const milestonesCompletedCount = [profileComplete, planComplete, firstSessionComplete, rrsUnlocked].filter(Boolean).length;

  const currentWeekNumber = plan?.current_week_number ?? 1;
  const currentWeek = plan ? plan.weeks?.find(w => w.week_number === currentWeekNumber) : null;
  const sessionsThisWeek = currentWeek?.sessions?.length ?? 0;
  const sessionsCompletedThisWeek = currentWeek?.sessions?.filter(s => s.completed).length ?? 0;

  const BENCHMARKS = [
    { min: 0,  max: 24,  label: 'Getting Started' },
    { min: 25, max: 44,  label: 'Recreational Player' },
    { min: 45, max: 59,  label: 'Club Level' },
    { min: 60, max: 74,  label: 'Varsity Starter' },
    { min: 75, max: 87,  label: 'College Prospect' },
    { min: 88, max: 100, label: 'D1 Ready' },
  ];

  const currentScore = rrsResult?.overall ?? 0;
  const nextBenchmark = BENCHMARKS.find(b => b.min > currentScore) ?? null;
  const pointsToNext = nextBenchmark ? nextBenchmark.min - currentScore : null;

  const feedPreviewPosts = [...SEED_POSTS]
    .sort((a, b) => b.date_posted.localeCompare(a.date_posted))
    .slice(0, 2);

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* 1. Header Section */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black text-foreground tracking-tight">
            Welcome back, {activeProfile.name} 👋
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">
            Here's where you stand today.
          </p>
        </div>
        <div className="shrink-0">
          <Badge className="bg-primary/10 text-primary border-primary/20 hover:bg-primary/20 px-3 py-1 font-semibold text-sm">
            {activeProfile.position} · {activeProfile.level}
          </Badge>
        </div>
      </div>

      {/* Onboarding Milestones Card */}
      {!allMilestonesComplete && (
        <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
          <CardHeader className="pb-3 flex flex-row items-center justify-between space-y-0">
            <CardTitle className="text-base font-bold text-white">
              🚀 Getting Started
            </CardTitle>
            <Badge className="bg-primary/10 text-primary border-primary/20 hover:bg-primary/20 font-semibold text-xs px-2 py-0.5">
              {milestonesCompletedCount} of 4 complete
            </Badge>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="w-full bg-secondary/40 rounded-full h-1.5 overflow-hidden">
              <div
                className="bg-primary h-1.5 rounded-full transition-all duration-500"
                style={{ width: `${(milestonesCompletedCount / 4) * 100}%` }}
              />
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
              {/* Milestone 1: Profile Setup */}
              <div className={`flex items-start gap-2.5 ${profileComplete ? 'opacity-60' : ''}`}>
                <span className={`text-sm font-bold shrink-0 ${profileComplete ? 'text-primary' : 'text-muted-foreground'}`}>
                  {profileComplete ? '✓' : '○'}
                </span>
                <div className="min-w-0">
                  <p className={`text-xs font-semibold leading-none ${profileComplete ? 'line-through text-muted-foreground' : 'text-white'}`}>
                    {profileComplete ? (
                      'Profile Setup'
                    ) : (
                      <Link href="/profile" className="hover:underline text-primary">
                        Profile Setup
                      </Link>
                    )}
                  </p>
                  <p className="text-[10px] text-muted-foreground mt-1.5 leading-tight">
                    Your position, level, and focus areas
                  </p>
                </div>
              </div>

              {/* Milestone 2: Plan Generated */}
              <div className={`flex items-start gap-2.5 ${planComplete ? 'opacity-60' : ''}`}>
                <span className={`text-sm font-bold shrink-0 ${planComplete ? 'text-primary' : 'text-muted-foreground'}`}>
                  {planComplete ? '✓' : '○'}
                </span>
                <div className="min-w-0">
                  <p className={`text-xs font-semibold leading-none ${planComplete ? 'line-through text-muted-foreground' : 'text-white'}`}>
                    {planComplete ? (
                      'Plan Generated'
                    ) : (
                      <Link href="/training" className="hover:underline text-primary">
                        Plan Generated
                      </Link>
                    )}
                  </p>
                  <p className="text-[10px] text-muted-foreground mt-1.5 leading-tight">
                    Your first weekly training plan is ready
                  </p>
                </div>
              </div>

              {/* Milestone 3: First Session Logged */}
              <div className={`flex items-start gap-2.5 ${firstSessionComplete ? 'opacity-60' : ''}`}>
                <span className={`text-sm font-bold shrink-0 ${firstSessionComplete ? 'text-primary' : 'text-muted-foreground'}`}>
                  {firstSessionComplete ? '✓' : '○'}
                </span>
                <div className="min-w-0">
                  <p className={`text-xs font-semibold leading-none ${firstSessionComplete ? 'line-through text-muted-foreground' : 'text-white'}`}>
                    {firstSessionComplete ? (
                      'First Session Logged'
                    ) : (
                      <Link href="/training" className="hover:underline text-primary">
                        First Session Logged
                      </Link>
                    )}
                  </p>
                  <p className="text-[10px] text-muted-foreground mt-1.5 leading-tight">
                    Complete and log your first session
                  </p>
                </div>
              </div>

              {/* Milestone 4: RRS Unlocked */}
              <div className={`flex items-start gap-2.5 ${rrsUnlocked ? 'opacity-60' : ''}`}>
                <span className={`text-sm font-bold shrink-0 ${rrsUnlocked ? 'text-primary' : 'text-muted-foreground'}`}>
                  {rrsUnlocked ? '✓' : '○'}
                </span>
                <div className="min-w-0">
                  <p className={`text-xs font-semibold leading-none ${rrsUnlocked ? 'line-through text-muted-foreground' : 'text-white'}`}>
                    {rrsUnlocked ? (
                      'RRS Unlocked'
                    ) : (
                      <Link href="/training" className="hover:underline text-primary">
                        RRS Unlocked
                      </Link>
                    )}
                  </p>
                  <p className="text-[10px] text-muted-foreground mt-1.5 leading-tight">
                    Log 5 sessions to unlock your score
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 2. Stat Cards Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {/* Card 1: RRS Score */}
        <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
              RRS Score
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex items-baseline gap-3">
              <span className="text-3xl font-black text-foreground">
                {latestRRS ? latestRRS.overall : '--'}
              </span>
              {rrsDelta !== null && rrsDelta !== 0 && (
                <Badge
                  className={
                    rrsDelta > 0
                      ? 'text-primary bg-primary/15 border-transparent text-xs font-semibold'
                      : 'text-destructive bg-destructive/15 border-transparent text-xs font-semibold'
                  }
                >
                  {rrsDelta > 0 ? `+${rrsDelta}` : rrsDelta} this week
                </Badge>
              )}
            </div>
            {rrsHistory && rrsHistory.snapshots && rrsHistory.snapshots.length >= 2 && (
              <RRSSparkline snapshots={rrsHistory.snapshots} />
            )}
            <p className="text-xs text-muted-foreground">
              Readiness & Reliability Score
            </p>
          </CardContent>
        </Card>

        {/* Card 2: Training Streak */}
        <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
              Streak
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="text-3xl font-black text-foreground">
              {streak} {streak === 1 ? 'day' : 'days'}
            </div>
            <p className="text-xs text-muted-foreground">
              Consecutive training days
            </p>
          </CardContent>
        </Card>

        {/* Card 3: Drills Completed */}
        <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
              Drills Done
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="text-3xl font-black text-foreground">
              {drillsCompleted}
            </div>
            <p className="text-xs text-muted-foreground">
              Across all sessions
            </p>
          </CardContent>
        </Card>

        {/* Card 4: This Week */}
        <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
              This Week
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="text-3xl font-black text-foreground">
              {sessionsCompletedThisWeek}/{sessionsThisWeek}
            </div>
            <p className="text-xs text-muted-foreground">
              Sessions complete
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Next Milestone Card */}
      {rrsResult?.unlocked && (
        <Card className="border-border/50 border-l-4 border-l-primary bg-card/50 backdrop-blur-sm">
          <CardContent className="p-6 space-y-4">
            <div className="space-y-1">
              <p className="text-xs uppercase tracking-widest text-muted-foreground font-semibold">
                Next Milestone
              </p>
              {pointsToNext !== null && nextBenchmark ? (
                <>
                  <h3 className="text-lg font-bold text-white">
                    {nextBenchmark.label}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {pointsToNext} {pointsToNext === 1 ? 'point' : 'points'} away
                  </p>
                </>
              ) : (
                <h3 className="text-lg font-bold text-white">
                  🏆 D1 Ready — Elite level achieved.
                </h3>
              )}
            </div>

            {nextActions.length > 0 && (
              <div className="space-y-2 pt-3 border-t border-border/20">
                <p className="text-xs uppercase tracking-widest text-muted-foreground font-semibold">
                  Recommended Actions
                </p>
                <div className="space-y-1.5">
                  {nextActions.slice(0, 2).map((action, i) => (
                    <div key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                      <span className="text-primary font-bold">→</span>
                      <span>{action}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Next Actions Section */}
      {nextActions.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-foreground tracking-tight">
            Next Actions
          </h2>
          <div className="space-y-2">
            {nextActions.map((action, i) => (
              <div key={i}
                className="flex items-start gap-3 bg-card/50 border border-border/50 rounded-lg px-4 py-3">
                <span className="text-primary font-bold mt-0.5 shrink-0">
                  →
                </span>
                <p className="text-sm text-muted-foreground">{action}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 3. Up Next Section */}
      <div className="space-y-3">
        <h2 className="text-lg font-semibold text-foreground tracking-tight">Up Next</h2>
        {nextSession ? (
          <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
            <CardContent className="p-6 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div>
                  <h3 className="text-base font-bold text-foreground">
                    {nextSession.name}
                  </h3>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    {nextSession.drills?.length ?? 0} drills · {nextSession.duration_minutes} min
                  </p>
                </div>
                <Badge className="w-fit text-primary bg-primary/15 border-transparent text-xs font-semibold">
                  Day {nextSession.day_number}
                </Badge>
              </div>

              {nextSession.drills && nextSession.drills.length > 0 && (
                <div className="space-y-2">
                  <span className="text-xs text-muted-foreground font-medium block">
                    Focus Areas:
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {Array.from(new Set(nextSession.drills.map(d => d.category))).map(cat => (
                      <Badge key={cat} variant="secondary" className="text-[10px] px-2 py-0.5">
                        {cat}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              <Button
                asChild
                className="w-full sm:w-fit font-semibold bg-primary hover:bg-primary/95 text-primary-foreground"
              >
                <Link href="/training">View Training Plan →</Link>
              </Button>
            </CardContent>
          </Card>
        ) : (
          <Card className="border-primary/20 border-dashed bg-primary/5">
            <CardContent className="py-8 text-center space-y-3">
              <div className="text-3xl">🎉</div>
              <p className="text-foreground font-bold text-base">
                Week {currentWeekNumber} Complete!
              </p>
              <p className="text-muted-foreground text-xs max-w-xs mx-auto">
                You finished all your sessions this week. Head to your Training Plan to generate next week.
              </p>
              <Button asChild size="sm" className="font-semibold mt-1">
                <Link href="/training">Generate Next Week →</Link>
              </Button>
            </CardContent>
          </Card>
        )}
      </div>

      {/* 4. Focus Areas Section */}
      {activeProfile.focus_areas && activeProfile.focus_areas.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-foreground tracking-tight">Your Focus Areas</h2>
          <div className="flex flex-wrap gap-2">
            {activeProfile.focus_areas.map((area) => (
              <Badge
                key={area}
                className="text-white bg-primary/20 hover:bg-primary/30 border-transparent px-3 py-1.5 text-xs font-semibold rounded-md"
              >
                {area}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Mentor Feed preview */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-foreground tracking-tight">
            Latest from Your Mentors
          </h2>
          <Link href="/feed" className="text-xs text-primary font-semibold hover:underline">
            View all →
          </Link>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {feedPreviewPosts.map(post => {
            const presenter = PRESENTER_MAP[post.presenter_id];
            return (
              <Link key={post.post_id} href="/feed">
                <Card className="border-border/50 bg-card/50 hover:bg-card/80 transition-colors cursor-pointer h-full">
                  <CardContent className="p-4 space-y-2">
                    <p className="text-[11px] font-bold text-primary uppercase tracking-wider">
                      {presenter?.name ?? post.presenter_id} · {presenter?.team}
                    </p>
                    <p className="text-sm font-semibold text-foreground leading-snug line-clamp-2">
                      {post.title}
                    </p>
                    <p className="text-xs text-muted-foreground line-clamp-2">
                      {post.description}
                    </p>
                  </CardContent>
                </Card>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Recruiting Hub teaser */}
      <div className="rounded-xl border border-primary/20 bg-primary/5 p-5 space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-lg">🎯</span>
            <h2 className="text-sm font-bold text-white">Recruiting Hub</h2>
          </div>
          <Badge className="bg-primary/15 text-primary border border-primary/30 text-[10px] font-bold">
            212 D1 Programs · 686 Coaches
          </Badge>
        </div>
        <p className="text-xs text-muted-foreground leading-relaxed">
          Search 212 D1 programs, find coaching staff contact info, draft personalized recruiting emails with AI, and track your entire outreach pipeline in one place.
        </p>
        <Link
          href="/recruiting"
          className="text-xs font-semibold text-primary hover:text-primary/80 transition-colors"
        >
          Open Recruiting Hub →
        </Link>
      </div>
    </div>
  );
}
