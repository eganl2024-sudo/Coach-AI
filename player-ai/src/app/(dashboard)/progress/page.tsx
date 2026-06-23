import { redirect } from 'next/navigation';
import Link from 'next/link';
import { getCurrentUser } from '@/lib/session';
import { getUserData } from '@/lib/data/getUserData';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { RadarChart } from '@/components/progress/RadarChart';
import { RRSLineChart } from '@/components/progress/RRSLineChart';
import { ActivityHeatmap } from '@/components/progress/ActivityHeatmap';
import { calculateSkillRadar } from '@/lib/utils/calculateSkillRadar';
import { getAllDrills } from '@/lib/data/getDrills';
import type { AthleteProfile, RRSHistory, CompletionLog, WeeklyTrainingPlan } from '@/lib/types/player';
import { cn } from '@/lib/utils';
import { Flame, CalendarDays, Dumbbell, Trophy } from 'lucide-react';

export const metadata = {
  title: 'My Progress',
};

export default async function ProgressPage() {
  const username = await getCurrentUser();
  if (!username) {
    redirect('/login');
  }

  // Fetch all progress-related data in parallel
  const [profile, rrsHistory, completionLog, plan, drills] = await Promise.all([
    getUserData<AthleteProfile>(username, 'athlete_profile'),
    getUserData<RRSHistory>(username, 'rrs_history'),
    getUserData<CompletionLog>(username, 'completion_log'),
    getUserData<WeeklyTrainingPlan>(username, 'weekly_training_plan'),
    getAllDrills(),
  ]);

  if (!profile) {
    redirect('/onboarding');
  }

  const snapshots = rrsHistory?.snapshots || [];
  const completions = completionLog?.completions || [];

  const isNewUser = snapshots.length === 0 && completions.length === 0;

  if (isNewUser) {
    return (
      <div className="space-y-6 max-w-5xl mx-auto pb-12">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            My Progress
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            {profile.name}'s development over time
          </p>
        </div>

        <Card className="border-border/50 bg-card/40">
          <CardContent className="py-16 text-center space-y-4">
            <h2 className="text-xl font-bold text-foreground">
              No data yet
            </h2>
            <p className="text-sm text-muted-foreground max-w-sm mx-auto">
              Complete your first training session to unlock your Skill Radar, RRS Trend, and activity heatmap.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center pt-2">
              <Link href="/training">
                <Button className="font-semibold">
                  View Training Plan →
                </Button>
              </Link>
              <Link href="/drills">
                <Button variant="outline" className="font-semibold">
                  Browse Drills
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>

        <Card className="border-border/50 bg-card/40">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-bold text-white">
              Training Activity
            </CardTitle>
            <CardDescription className="text-xs text-muted-foreground">
              Your consistency over the last 12 weeks
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <ActivityHeatmap completions={[]} />
            <div className="grid grid-cols-3 gap-4 border-t border-border/30 pt-4 text-center">
              <div>
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-semibold">
                  Total Sessions
                </p>
                <p className="text-2xl font-black text-white mt-0.5">0</p>
              </div>
              <div>
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-semibold">
                  Total Drills
                </p>
                <p className="text-2xl font-black text-white mt-0.5">0</p>
              </div>
              <div>
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-semibold">
                  Active Days
                </p>
                <p className="text-2xl font-black text-white mt-0.5">0</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const skillRadar = profile
    ? calculateSkillRadar(profile, completionLog, plan ?? null, drills)
    : { axes: [], scores: [], hasData: false };

  // 1. Skill Radar prep (latest snapshot)
  const latestSnapshot = snapshots.length > 0 ? snapshots[snapshots.length - 1] : null;
  const pillars = latestSnapshot?.pillars || {
    consistency: 0,
    volume: 0,
    coverage: 0,
    progression: 0,
  };

  // 2. RRS Trend prep
  const currentRRS = latestSnapshot?.overall ?? 0;
  let rrsDelta = 0;
  if (snapshots.length >= 2) {
    const previousRRS = snapshots[snapshots.length - 2].overall;
    rrsDelta = currentRRS - previousRRS;
  }

  // 3. Activity Heatmap & Stats prep
  const totalSessions = completions.length;
  const totalDrills = completions.reduce(
    (sum, c) => sum + (c.drills_completed?.length || 0),
    0
  );
  const activeDaysCount = new Set(completions.map(c => c.date)).size;

  // 4. Focus Area Breakdown prep
  const focusCounts: Record<string, number> = {};
  completions.forEach(c => {
    if (c.focus_areas) {
      c.focus_areas.forEach(fa => {
        const name = fa.trim();
        focusCounts[name] = (focusCounts[name] || 0) + 1;
      });
    }
  });

  const focusBreakdown = Object.entries(focusCounts)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count);

  const maxFocusCount = focusBreakdown.length > 0
    ? Math.max(...focusBreakdown.map(fb => fb.count))
    : 1;

  // Personal bests computation
  const longestStreak = (() => {
    if (!completionLog?.completions?.length) return 0;
    const dates = [...new Set(completionLog.completions.map(c => c.date))].sort();
    let max = 1, cur = 1;
    for (let i = 1; i < dates.length; i++) {
      const prev = new Date(dates[i - 1]);
      const curr = new Date(dates[i]);
      const diff = (curr.getTime() - prev.getTime()) / (1000 * 60 * 60 * 24);
      if (diff === 1) { cur++; max = Math.max(max, cur); }
      else cur = 1;
    }
    return max;
  })();

  const totalDrillsAllTime = totalDrills;
  const bestWeek = (() => {
    const weekCounts: Record<number, number> = {};
    completions.forEach(c => { weekCounts[c.week] = (weekCounts[c.week] ?? 0) + 1; });
    return Math.max(0, ...Object.values(weekCounts));
  })();

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-12">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-white">My Progress</h1>
        <p className="text-sm text-muted-foreground mt-1">
          {profile.name}'s development over time
        </p>
      </div>

      {/* RRS Overview Row (Side-by-side) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Card: Skill Radar & RRS Pillars */}
        <Card className="lg:col-span-5 border-border/50 bg-card/40 backdrop-blur-sm shadow-xl flex flex-col justify-between">
          <CardHeader className="pb-4">
            <CardTitle className="text-lg font-bold text-white">Skill Radar</CardTitle>
            <CardDescription className="text-xs text-muted-foreground">
              Latest skill area development
            </CardDescription>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col justify-center space-y-4">
            {/* TOP Section: Dynamic Skill Radar */}
            {skillRadar.hasData ? (
              <div className="py-2">
                <RadarChart axes={skillRadar.axes} scores={skillRadar.scores} size={190} />
              </div>
            ) : (
              <div className="text-center py-8 text-sm text-muted-foreground">
                Complete sessions to build your skill radar
              </div>
            )}

            {/* BOTTOM Section: RRS Pillars grid */}
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground/70 mt-4 mb-2">
                RRS Pillars
              </p>
              <div className="grid grid-cols-2 gap-x-4 gap-y-3 pt-2">
                {Object.entries(pillars).map(([key, score]) => {
                  const weights: Record<string, number> = { consistency: 30, volume: 20, coverage: 25, progression: 25 };
                  return (
                  <div key={key} className="space-y-1">
                    <div className="flex justify-between items-center text-xs">
                      <div className="flex items-center gap-1 min-w-0">
                        <span className="capitalize text-muted-foreground font-medium truncate">{key}</span>
                        {weights[key] && (
                          <span className="text-muted-foreground/40 text-[10px] shrink-0">{weights[key]}%</span>
                        )}
                      </div>
                      <span className="font-bold text-white ml-1 shrink-0">{score}</span>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-1.5 overflow-hidden">
                      <div
                        className="bg-primary h-1.5 rounded-full transition-all duration-500"
                        style={{ width: `${score}%` }}
                      />
                    </div>
                  </div>
                  );
                })}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Right Card: RRS Trend */}
        <Card className="lg:col-span-7 border-border/50 bg-card/40 backdrop-blur-sm shadow-xl flex flex-col justify-between">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-bold text-white">RRS Trend</CardTitle>
            <CardDescription className="text-xs text-muted-foreground">
              Weekly overall score
            </CardDescription>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col justify-between pt-4">
            {snapshots.length > 0 ? (
              <>
                <div className="w-full py-4">
                  <RRSLineChart snapshots={snapshots} />
                </div>
                <div className="flex items-baseline gap-2 border-t border-border/30 pt-4 mt-auto">
                  <span className="text-xs text-muted-foreground uppercase font-semibold tracking-wider">
                    Current RRS:
                  </span>
                  <span className="text-3xl font-black text-white">{currentRRS}</span>
                  {rrsDelta !== 0 && (
                    <span
                      className={cn(
                        "text-xs font-extrabold px-2.5 py-0.5 rounded-full ml-1.5 select-none",
                        rrsDelta > 0
                          ? "bg-primary/10 text-primary border border-primary/20"
                          : "bg-destructive/10 text-destructive border border-destructive/20"
                      )}
                    >
                      {rrsDelta > 0 ? `+${rrsDelta}` : rrsDelta}
                    </span>
                  )}
                </div>
              </>
            ) : (
              <div className="text-center py-16 text-sm text-muted-foreground flex-1 flex items-center justify-center">
                Complete sessions to see your trend
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Training Activity Heatmap */}
      <Card className="border-border/50 bg-card/40 backdrop-blur-sm shadow-xl">
        <CardHeader className="pb-2">
          <CardTitle className="text-lg font-bold text-white">Training Activity</CardTitle>
          <CardDescription className="text-xs text-muted-foreground">
            Your consistency over the last 12 weeks
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="py-2 overflow-x-auto">
            <ActivityHeatmap completions={completions} />
          </div>

          <div className="grid grid-cols-3 gap-4 border-t border-border/30 pt-4 text-center sm:text-left">
            <div>
              <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-semibold">
                Total Sessions
              </p>
              <p className="text-2xl font-black text-white mt-0.5">{totalSessions}</p>
            </div>
            <div>
              <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-semibold">
                Total Drills
              </p>
              <p className="text-2xl font-black text-white mt-0.5">{totalDrills}</p>
            </div>
            <div>
              <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-semibold">
                Active Days
              </p>
              <p className="text-2xl font-black text-white mt-0.5">{activeDaysCount}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Focus Area Breakdown */}
      <Card className="border-border/50 bg-card/40 backdrop-blur-sm shadow-xl">
        <CardHeader className="pb-4">
          <CardTitle className="text-lg font-bold text-white">Focus Area Breakdown</CardTitle>
          <CardDescription className="text-xs text-muted-foreground">
            Drills completed by category
          </CardDescription>
        </CardHeader>
        <CardContent>
          {focusBreakdown.length > 0 ? (
            <div className="space-y-3.5 max-w-2xl max-h-72 overflow-y-auto pr-1">
              {focusBreakdown.map((item, idx) => {
                const percentage = (item.count / maxFocusCount) * 100;
                return (
                  <div key={idx} className="flex items-center gap-4">
                    <span className="w-36 text-sm text-muted-foreground font-medium truncate" title={item.name}>
                      {item.name}
                    </span>
                    <div className="flex-1 bg-secondary rounded-full h-2.5 overflow-hidden">
                      <div
                        className="bg-primary/80 h-2.5 rounded-full transition-all duration-500"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                    <span className="w-8 text-right text-xs text-white font-bold">
                      {item.count}
                    </span>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-12 text-sm text-muted-foreground">
              Complete sessions to see your breakdown
            </div>
          )}
        </CardContent>
      </Card>

      {/* Personal Bests */}
      <Card className="border-border/50 bg-card/40 backdrop-blur-sm shadow-xl">
        <CardHeader className="pb-4">
          <CardTitle className="text-lg font-bold text-white">Personal Bests</CardTitle>
          <CardDescription className="text-xs text-muted-foreground">
            Your lifetime training achievements
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[
              { label: 'Longest Streak', value: `${longestStreak}d`, Icon: Flame },
              { label: 'Total Sessions', value: totalSessions, Icon: CalendarDays },
              { label: 'Total Drills', value: totalDrillsAllTime, Icon: Dumbbell },
              { label: 'Best Week', value: `${bestWeek} sessions`, Icon: Trophy },
            ].map(stat => (
              <div key={stat.label} className="text-center space-y-1 p-3 rounded-lg bg-secondary/20">
                <stat.Icon className="w-5 h-5 text-primary mx-auto" />
                <div className="text-xl font-black text-white">{stat.value}</div>
                <div className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
