import { redirect } from 'next/navigation';
import Link from 'next/link';
import { getCurrentUser } from '@/lib/session';
import { getUserData } from '@/lib/data/getUserData';
import { getCurrentWeek, getNextSession } from '@/lib/utils/training';
import { SessionCard } from '@/components/training/SessionCard';
import { PastWeeksAccordion } from '@/components/training/PastWeeksAccordion';
import GenerateNextWeekButton from '@/components/training/GenerateNextWeekButton';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import type { AthleteProfile, WeeklyTrainingPlan, CompletionLog } from '@/lib/types/player';

export const metadata = {
  title: 'Training Plan',
};

export default async function TrainingPlanPage() {
  const username = await getCurrentUser();
  if (!username) {
    redirect('/login');
  }

  // Fetch Supabase data
  const [profile, plan, completionLog] = await Promise.all([
    getUserData<AthleteProfile>(username, 'athlete_profile'),
    getUserData<WeeklyTrainingPlan>(username, 'weekly_training_plan'),
    getUserData<CompletionLog>(username, 'completion_log'),
  ]);

  const activeProfileName = profile?.name ?? username;
  const currentWeekNumber = plan?.current_week_number ?? 1;
  const currentWeek = plan ? getCurrentWeek(plan) : null;
  const nextSession = plan ? getNextSession(plan) : null;

  // Filter archived weeks (all weeks except the current week)
  const archivedWeeks = plan?.weeks?.filter(w => w.week_number !== currentWeekNumber) ?? [];

  const allSessionsComplete = currentWeek
    ? currentWeek.sessions.every(s => s.completed)
    : false;

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* 1. Page Header */}
      <div>
        <h1 className="text-3xl font-black text-foreground tracking-tight">Training Plan</h1>
        <h2 className="text-base font-semibold text-primary mt-1">
          {activeProfileName}'s Week {currentWeekNumber}
        </h2>
        <p className="text-muted-foreground text-xs mt-0.5">
          Your personalized development sessions
        </p>
      </div>

      {/* 2. Current Week Sessions */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-foreground tracking-tight">Current Week</h3>
        {!plan ? (
          <Card className="border-border/50 border-dashed bg-card/10">
            <CardContent className="py-10 text-center space-y-4">
              <h3 className="text-lg font-bold text-foreground">
                Your training plan is being set up
              </h3>
              <p className="text-sm text-muted-foreground">
                Complete your profile to generate your first plan.
              </p>
              <Link href="/profile" className="inline-block">
                <Button className="font-semibold">Go to Profile</Button>
              </Link>
            </CardContent>
          </Card>
        ) : !currentWeek || !currentWeek.sessions || currentWeek.sessions.length === 0 ? (
          <Card className="border-border/50 border-dashed bg-card/10">
            <CardContent className="py-10 text-center">
              <p className="text-muted-foreground text-sm">
                No sessions available for the current week.
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {currentWeek.sessions.map((session, idx) => {
              const isNext = nextSession ? session.day_number === nextSession.day_number : false;
              return (
                <SessionCard
                  key={session.day_number || idx}
                  session={session}
                  isCurrent={true}
                  isNext={isNext}
                  weekNumber={currentWeekNumber}
                />
              );
            })}
          </div>
        )}
      </div>

      {/* Week Complete Section */}
      {allSessionsComplete && currentWeek && (
        <div className="rounded-xl border border-primary/30 bg-primary/5 p-6 space-y-4">
          <div className="text-center space-y-1">
            <h3 className="text-lg font-bold text-foreground">
              Week {currentWeekNumber} Complete
            </h3>
            <p className="text-sm text-muted-foreground">
              You finished all {currentWeek.sessions.length} sessions this week. Ready for your next challenge?
            </p>
          </div>
          <GenerateNextWeekButton
            nextWeekNumber={currentWeekNumber + 1}
          />
        </div>
      )}

      {/* 3. Past Weeks Section */}
      {archivedWeeks.length > 0 && (
        <div className="space-y-4 pt-4 border-t border-border/30">
          <h3 className="text-lg font-semibold text-foreground tracking-tight">Previous Weeks</h3>
          <PastWeeksAccordion weeks={archivedWeeks} />
        </div>
      )}
    </div>
  );
}
