'use server';

import { revalidatePath } from 'next/cache';
import { createServerClient } from '@/lib/supabase/server';
import { getCurrentUser } from '@/lib/session';
import { getUserData } from '@/lib/data/getUserData';
import { getAllDrills } from '@/lib/data/getDrills';
import { generateTrainingPlan } from '@/lib/utils/generateTrainingPlan';
import { calculateRRS } from '@/lib/utils/calculateRRS';
import type { WeeklyTrainingPlan, CompletionLog, CompletionEntry, DrillCompletion, DrillCompletionLog, AthleteProfile, RRSHistory, RRSSnapshot, TrainingSession } from '@/lib/types/player';
import { sendWeeklySummaryEmail } from '@/lib/email/resend';

// Helper to format Date as YYYY-MM-DD in local time
function getLocalDateString(d: Date): string {
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

export async function completeSessionAction(
  weekNumber: number,
  dayNumber: number
): Promise<{ success: boolean; error?: string }> {
  try {
    const username = await getCurrentUser();
    if (!username) {
      return { success: false, error: 'User session not found.' };
    }

    // Fetch plan and completion log in parallel
    const [plan, completionLog] = await Promise.all([
      getUserData<WeeklyTrainingPlan>(username, 'weekly_training_plan'),
      getUserData<CompletionLog>(username, 'completion_log'),
    ]);

    if (!plan) {
      return { success: false, error: 'Training plan not found.' };
    }

    // Validate inputs
    if (!Number.isInteger(weekNumber) || weekNumber < 1 || weekNumber > 520) {
      return { success: false, error: 'Invalid week number.' };
    }
    if (!Number.isInteger(dayNumber) || dayNumber < 1 || dayNumber > 7) {
      return { success: false, error: 'Invalid day number.' };
    }

    // Find the week and session
    const week = plan.weeks?.find(w => w.week_number === weekNumber);
    if (!week) {
      return { success: false, error: `Week ${weekNumber} not found in plan.` };
    }

    const session = week.sessions?.find(s => s.day_number === dayNumber);
    if (!session) {
      return { success: false, error: `Session for day ${dayNumber} not found in week ${weekNumber}.` };
    }

    if (session.completed) {
      return { success: false, error: 'Session is already completed.' };
    }

    const todayStr = getLocalDateString(new Date());

    // Mark as completed
    session.completed = true;
    session.completed_date = todayStr;

    // Calculate most common difficulty among drills
    const diffCounts: Record<string, number> = {};
    session.drills?.forEach(drill => {
      const diff = drill.difficulty?.toLowerCase() || 'beginner';
      diffCounts[diff] = (diffCounts[diff] || 0) + 1;
    });

    let mostCommonDiff = 'beginner';
    let maxCount = 0;
    Object.entries(diffCounts).forEach(([diff, count]) => {
      if (count > maxCount) {
        maxCount = count;
        mostCommonDiff = diff;
      }
    });

    // Get deduplicated drill categories as focus areas
    const focusAreas = Array.from(
      new Set(session.drills?.map(d => d.category).filter(Boolean) ?? [])
    );

    // Build the new CompletionEntry
    const newEntry: CompletionEntry = {
      session_id: `week${weekNumber}_day${dayNumber}`,
      timestamp: new Date().toISOString(),
      date: todayStr,
      week: weekNumber,
      day: dayNumber,
      drills_completed: session.drills?.map(d => d.drill_id).filter(Boolean) ?? [],
      duration_minutes: session.duration_minutes,
      difficulty: mostCommonDiff,
      focus_areas: focusAreas,
    };

    // Update CompletionLog
    const updatedLog: CompletionLog = completionLog
      ? {
          ...completionLog,
          completions: [...(completionLog.completions ?? []), newEntry],
        }
      : {
          completions: [newEntry],
        };

    const supabase = await createServerClient();

    // Upsert both records in parallel
    const [resPlan, resLog] = await Promise.all([
      supabase.from('user_data').upsert({
        username,
        data_key: 'weekly_training_plan',
        data_value: JSON.stringify(plan),
        updated_at: new Date().toISOString(),
      }, { onConflict: 'username,data_key' }),
      supabase.from('user_data').upsert({
        username,
        data_key: 'completion_log',
        data_value: JSON.stringify(updatedLog),
        updated_at: new Date().toISOString(),
      }, { onConflict: 'username,data_key' }),
    ]);

    if (resPlan.error) {
      throw new Error(`Failed to save weekly training plan: ${resPlan.error.message}`);
    }
    if (resLog.error) {
      throw new Error(`Failed to save completion log: ${resLog.error.message}`);
    }

    // Calculate and save new RRS snapshot
    try {
      await saveRRSSnapshot(username, updatedLog, plan, supabase);
    } catch {
      // Non-fatal — RRS failure should not block session completion
    }

    // Revalidate paths to refresh page data
    revalidatePath('/training');
    revalidatePath('/');

    return { success: true };
  } catch (err: any) {
    return {
      success: false,
      error: err.message || 'An unexpected error occurred while saving completions.',
    };
  }
}

export async function completeDrillAction(
  drillId: string,
  drillName: string
): Promise<{ success: boolean; error?: string; alreadyDone?: boolean }> {
  try {
    const username = await getCurrentUser();
    if (!username) {
      return { success: false, error: 'User session not found.' };
    }

    // Fetch existing completions
    const drillCompletionLog = await getUserData<DrillCompletionLog>(username, 'drill_completions');

    const todayStr = getLocalDateString(new Date());

    // Check if already done today
    const alreadyDone = drillCompletionLog?.completions?.some(
      c => c.drill_id === drillId && c.date === todayStr
    ) ?? false;

    if (alreadyDone) {
      return { success: true, alreadyDone: true };
    }

    const newEntry: DrillCompletion = {
      drill_id: drillId,
      drill_name: drillName,
      completed_at: new Date().toISOString(),
      date: todayStr,
    };

    const updatedLog: DrillCompletionLog = drillCompletionLog
      ? {
          ...drillCompletionLog,
          completions: [...(drillCompletionLog.completions ?? []), newEntry],
        }
      : {
          completions: [newEntry],
        };

    const supabase = await createServerClient();
    const { error: upsertError } = await supabase.from('user_data').upsert({
      username,
      data_key: 'drill_completions',
      data_value: JSON.stringify(updatedLog),
      updated_at: new Date().toISOString(),
    }, { onConflict: 'username,data_key' });

    if (upsertError) {
      throw new Error(`Failed to save drill completion: ${upsertError.message}`);
    }

    revalidatePath('/drills/' + drillId);
    revalidatePath('/progress');

    return { success: true };
  } catch (err: any) {
    return {
      success: false,
      error: err.message || 'An unexpected error occurred while saving drill completion.',
    };
  }
}

export async function generateNextWeekAction(): Promise<{ success: boolean; error?: string }> {
  try {
    const username = await getCurrentUser();
    if (!username) {
      return { success: false, error: 'User session not found.' };
    }

    const [profile, plan] = await Promise.all([
      getUserData<AthleteProfile>(username, 'athlete_profile'),
      getUserData<WeeklyTrainingPlan>(username, 'weekly_training_plan'),
    ]);

    if (!profile || !plan) {
      return { success: false, error: 'Profile or training plan not found.' };
    }

    const currentWeek = plan.weeks?.find(
      w => w.week_number === plan.current_week_number
    );
    if (!currentWeek) {
      return { success: false, error: 'Current week not found.' };
    }

    const allComplete = currentWeek.sessions?.every(s => s.completed) ?? false;
    if (!allComplete) {
      return {
        success: false,
        error: 'Complete all sessions before generating next week.',
      };
    }

    const originalPlan = plan; // reference before generating next week
    const completedWeekNumber = plan.current_week_number;

    const drills = await getAllDrills();
    const updatedPlan = generateTrainingPlan(profile, drills, completedWeekNumber + 1, originalPlan);

    const supabase = await createServerClient();
    const { error: upsertError } = await supabase.from('user_data').upsert({
      username,
      data_key: 'weekly_training_plan',
      data_value: JSON.stringify(updatedPlan),
      updated_at: new Date().toISOString(),
    }, { onConflict: 'username,data_key' });

    if (upsertError) {
      throw new Error(`Failed to save next week training plan: ${upsertError.message}`);
    }

    // Send weekly summary email (non-fatal)
    try {
      const [completionLog, rrsHistory] = await Promise.all([
        getUserData<CompletionLog>(username, 'completion_log'),
        getUserData<RRSHistory>(username, 'rrs_history'),
      ]);

      if (!profile.email) {
        console.log(`[Email] Skipped for ${username} — no email address on profile.`);
      } else if (!completionLog) {
        console.log(`[Email] Skipped for ${username} — no completion log found.`);
      } else {
        await sendWeeklySummaryEmail({
          profile,
          completionLog,
          plan: originalPlan, // ← pass the original plan
          drills,
          rrsHistory: rrsHistory ?? null,
          completedWeekNumber: completedWeekNumber,
        });
        console.log(`[Email] Weekly summary sent to ${profile.email}`);
      }
    } catch (emailErr) {
      console.error('[Email] Failed to send weekly summary:', emailErr);
    }

    revalidatePath('/training');
    revalidatePath('/');

    return { success: true };
  } catch (err: any) {
    return {
      success: false,
      error: err.message || 'An unexpected error occurred while generating next week.',
    };
  }
}

export async function regenerateCurrentWeekAction(): Promise<{ success: boolean; error?: string }> {
  try {
    const username = await getCurrentUser();
    if (!username) return { success: false, error: 'User session not found.' };

    const [profile, plan] = await Promise.all([
      getUserData<AthleteProfile>(username, 'athlete_profile'),
      getUserData<WeeklyTrainingPlan>(username, 'weekly_training_plan'),
    ]);

    if (!profile || !plan) return { success: false, error: 'Profile or training plan not found.' };

    const currentWeekNum = plan.current_week_number ?? 1;
    const currentWeek = plan.weeks?.find(w => w.week_number === currentWeekNum);
    if (!currentWeek) return { success: false, error: 'Current week not found.' };

    const completedSessions = currentWeek.sessions?.filter(s => s.completed) ?? [];

    const drills = await getAllDrills();
    const freshWeekPlan = generateTrainingPlan(profile, drills, currentWeekNum, undefined);
    const freshSessions = freshWeekPlan.weeks[0]?.sessions ?? [];

    // Keep completed sessions; fill remaining slots with fresh ones
    const completedDays = new Set(completedSessions.map(s => s.day_number));
    const mergedSessions: TrainingSession[] = [...completedSessions];
    for (const session of freshSessions) {
      if (mergedSessions.length >= profile.sessions_per_week) break;
      if (!completedDays.has(session.day_number)) mergedSessions.push(session);
    }

    const updatedWeeks = plan.weeks.map(w =>
      w.week_number === currentWeekNum
        ? { ...w, sessions: mergedSessions, generated_date: new Date().toISOString() }
        : w
    );
    const updatedPlan: WeeklyTrainingPlan = { ...plan, weeks: updatedWeeks };

    const supabase = await createServerClient();
    const { error: upsertError } = await supabase.from('user_data').upsert({
      username,
      data_key: 'weekly_training_plan',
      data_value: JSON.stringify(updatedPlan),
      updated_at: new Date().toISOString(),
    }, { onConflict: 'username,data_key' });

    if (upsertError) throw new Error(upsertError.message);

    revalidatePath('/training');
    revalidatePath('/');
    return { success: true };
  } catch (err: any) {
    return { success: false, error: err.message || 'Failed to regenerate plan.' };
  }
}

export async function updateProfileAction(
  updates: Partial<AthleteProfile>,
  regeneratePlan: boolean
): Promise<{ success: boolean; error?: string }> {
  try {
    const username = await getCurrentUser();
    if (!username) {
      return { success: false, error: 'User session not found.' };
    }

    const existingProfile = await getUserData<AthleteProfile>(username, 'athlete_profile');
    if (!existingProfile) {
      return { success: false, error: 'Player profile not found.' };
    }

    const updatedProfile: AthleteProfile = {
      ...existingProfile,
      ...updates,
    };

    // Sanitize email — treat empty string as no email
    if (!updatedProfile.email?.trim()) {
      updatedProfile.email = undefined;
    }

    const supabase = await createServerClient();
    const now = new Date().toISOString();

    const { error: profileError } = await supabase.from('user_data').upsert({
      username,
      data_key: 'athlete_profile',
      data_value: JSON.stringify(updatedProfile),
      updated_at: now,
    }, { onConflict: 'username,data_key' });

    if (profileError) {
      throw new Error(`Failed to update profile: ${profileError.message}`);
    }

    if (regeneratePlan) {
      const drills = await getAllDrills();
      const existingPlan = await getUserData<WeeklyTrainingPlan>(username, 'weekly_training_plan');

      let updatedPlan: WeeklyTrainingPlan;

      if (existingPlan) {
        const currentWeekNum = existingPlan.current_week_number ?? 1;
        const currentWeek = existingPlan.weeks?.find(w => w.week_number === currentWeekNum);

        if (currentWeek) {
          const completedSessions = currentWeek.sessions?.filter(s => s.completed) ?? [];
          const incompleteSessions = currentWeek.sessions?.filter(s => !s.completed) ?? [];
          const allComplete = incompleteSessions.length === 0;

          if (allComplete) {
            // All done — archive current week and generate new week
            updatedPlan = generateTrainingPlan(updatedProfile, drills, currentWeekNum + 1, existingPlan);
          } else if (completedSessions.length === 0) {
            // Nothing done yet — regenerate all sessions in current week
            const freshWeekPlan = generateTrainingPlan(updatedProfile, drills, currentWeekNum, undefined);
            const freshSessions = freshWeekPlan.weeks[0]?.sessions ?? [];
            const updatedWeeks = existingPlan.weeks.map(w => {
              if (w.week_number === currentWeekNum) {
                return { ...w, sessions: freshSessions, generated_date: new Date().toISOString() };
              }
              return w;
            });
            updatedPlan = { ...existingPlan, weeks: updatedWeeks };
          } else {
            // Partially done — keep completed sessions, regenerate incomplete ones
            // Use new sessions_per_week count from updatedProfile, not old session count
            const freshWeekPlan = generateTrainingPlan(updatedProfile, drills, currentWeekNum, undefined);
            const freshSessions = freshWeekPlan.weeks[0]?.sessions ?? [];

            const completedSessions = currentWeek.sessions.filter(s => s.completed);

            // Build merged list: completed sessions first, then fresh sessions to fill the new count
            const newSessionCount = updatedProfile.sessions_per_week;
            const mergedSessions: TrainingSession[] = [];

            // Preserve all completed sessions
            for (const session of completedSessions) {
              mergedSessions.push(session);
            }

            // Fill remaining slots with fresh sessions (skip any that overlap day_number with completed)
            const completedDays = new Set(completedSessions.map(s => s.day_number));
            for (const freshSession of freshSessions) {
              if (mergedSessions.length >= newSessionCount) break;
              if (!completedDays.has(freshSession.day_number)) {
                mergedSessions.push(freshSession);
              }
            }

            const updatedWeeks = existingPlan.weeks.map(w => {
              if (w.week_number === currentWeekNum) {
                return { ...w, sessions: mergedSessions, generated_date: new Date().toISOString() };
              }
              return w;
            });
            updatedPlan = { ...existingPlan, weeks: updatedWeeks };
          }
        } else {
          // No current week found — generate fresh
          updatedPlan = generateTrainingPlan(updatedProfile, drills, currentWeekNum, existingPlan);
        }
      } else {
        // No existing plan — generate from scratch
        updatedPlan = generateTrainingPlan(updatedProfile, drills, 1, undefined);
      }

      const { error: planError } = await supabase.from('user_data').upsert({
        username,
        data_key: 'weekly_training_plan',
        data_value: JSON.stringify(updatedPlan),
        updated_at: now,
      }, { onConflict: 'username,data_key' });

      if (planError) {
        throw new Error(`Failed to regenerate training plan: ${planError.message}`);
      }

      revalidatePath('/training');
    }

    revalidatePath('/profile');
    revalidatePath('/');

    return { success: true };
  } catch (err: any) {
    return {
      success: false,
      error: err.message || 'An unexpected error occurred while updating the profile.',
    };
  }
}

async function saveRRSSnapshot(
  username: string,
  completionLog: CompletionLog,
  plan: WeeklyTrainingPlan,
  supabase: Awaited<ReturnType<typeof createServerClient>>
): Promise<void> {
  const [profile, rrsHistory, drills] = await Promise.all([
    getUserData<AthleteProfile>(username, 'athlete_profile'),
    getUserData<RRSHistory>(username, 'rrs_history'),
    getAllDrills(),
  ]);

  if (!profile) return;

  const result = calculateRRS(profile, completionLog, plan, drills, rrsHistory);

  const newSnapshot: RRSSnapshot = {
    date: result.snapshotDate,
    overall: result.overall,
    pillars: {
      consistency: result.pillars.consistency,
      volume: result.pillars.volume,
      coverage: result.pillars.coverage,
      progression: result.pillars.progression,
    },
  };

  const existingSnapshots = rrsHistory?.snapshots || [];
  const dateIndex = existingSnapshots.findIndex((s) => s.date === newSnapshot.date);

  let updatedSnapshots = [...existingSnapshots];
  if (dateIndex !== -1) {
    updatedSnapshots[dateIndex] = newSnapshot;
  } else {
    updatedSnapshots.push(newSnapshot);
  }

  if (updatedSnapshots.length > 52) {
    updatedSnapshots = updatedSnapshots.slice(-52);
  }

  const updatedHistory: RRSHistory = {
    snapshots: updatedSnapshots,
  };

  await supabase.from('user_data').upsert({
    username,
    data_key: 'rrs_history',
    data_value: JSON.stringify(updatedHistory),
    updated_at: new Date().toISOString(),
  }, { onConflict: 'username,data_key' });
}
