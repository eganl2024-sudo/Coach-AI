import { CompletionLog, RRSHistory, RRSSnapshot, WeeklyTrainingPlan, TrainingWeek, TrainingSession } from '../types/player';

// Helper to format Date as YYYY-MM-DD in local time
function getLocalDateString(d: Date): string {
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

export function calculateStreak(log: CompletionLog): number {
  if (!log || !log.completions || log.completions.length === 0) return 0;
  const completedDates = new Set(
    log.completions
      .map(c => c.date)
      .filter(Boolean)
  );

  const today = new Date();
  const todayStr = getLocalDateString(today);

  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  const yesterdayStr = getLocalDateString(yesterday);

  let currentCheckDate = new Date();
  let streak = 0;

  if (completedDates.has(todayStr)) {
    streak = 1;
    currentCheckDate.setDate(currentCheckDate.getDate() - 1);
  } else if (completedDates.has(yesterdayStr)) {
    streak = 1;
    currentCheckDate = yesterday;
    currentCheckDate.setDate(currentCheckDate.getDate() - 1);
  } else {
    return 0;
  }

  while (true) {
    const checkStr = getLocalDateString(currentCheckDate);
    if (completedDates.has(checkStr)) {
      streak++;
      currentCheckDate.setDate(currentCheckDate.getDate() - 1);
    } else {
      break;
    }
  }

  return streak;
}

export function getLatestRRS(history: RRSHistory): RRSSnapshot | null {
  if (!history || !history.snapshots || history.snapshots.length === 0) return null;
  const sorted = [...history.snapshots].sort((a, b) => b.date.localeCompare(a.date));
  return sorted[0];
}

export function getRRSDelta(history: RRSHistory): number | null {
  if (!history || !history.snapshots || history.snapshots.length < 2) return null;
  const sorted = [...history.snapshots].sort((a, b) => a.date.localeCompare(b.date));
  const latest = sorted[sorted.length - 1];
  const previous = sorted[sorted.length - 2];
  return latest.overall - previous.overall;
}

export function getCurrentWeek(plan: WeeklyTrainingPlan): TrainingWeek | null {
  if (!plan || !plan.weeks || typeof plan.current_week_number !== 'number') return null;
  return plan.weeks.find(w => w.week_number === plan.current_week_number) ?? null;
}

export function getNextSession(plan: WeeklyTrainingPlan): TrainingSession | null {
  const currentWeek = getCurrentWeek(plan);
  if (!currentWeek || !currentWeek.sessions || currentWeek.sessions.length === 0) return null;
  const sorted = [...currentWeek.sessions].sort((a, b) => a.day_number - b.day_number);
  return sorted.find(s => !s.completed) ?? null;
}

export function getTotalDrillsCompleted(log: CompletionLog): number {
  if (!log || !log.completions) return 0;
  return log.completions.reduce((acc, entry) => acc + (entry.drills_completed?.length ?? 0), 0);
}
