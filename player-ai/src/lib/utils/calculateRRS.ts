import type {
  AthleteProfile,
  CompletionLog,
  CompletionEntry,
  WeeklyTrainingPlan,
  RRSHistory,
  RRSSnapshot,
  Drill,
} from '@/lib/types/player';

const BENCHMARKS = [
  { min: 0,  max: 24,  label: 'Getting Started',     color: '#94a3b8' },
  { min: 25, max: 44,  label: 'Recreational Player', color: '#60a5fa' },
  { min: 45, max: 59,  label: 'Club Level',          color: '#34d399' },
  { min: 60, max: 74,  label: 'Varsity Starter',     color: '#fbbf24' },
  { min: 75, max: 87,  label: 'College Prospect',    color: '#f97316' },
  { min: 88, max: 100, label: 'D1 Ready',            color: '#a855f7' },
];

function getBenchmark(score: number): { label: string; color: string } {
  if (score < 0) return { label: 'Getting Started', color: '#94a3b8' };
  if (score > 100) return { label: 'D1 Ready', color: '#a855f7' };
  for (const b of BENCHMARKS) {
    if (score >= b.min && score <= b.max) {
      return { label: b.label, color: b.color };
    }
  }
  return { label: 'Getting Started', color: '#94a3b8' };
}

function getLocalDateString(d: Date): string {
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function getDaysDiff(d1: Date, d2: Date): number {
  const t1 = new Date(d1.getFullYear(), d1.getMonth(), d1.getDate()).getTime();
  const t2 = new Date(d2.getFullYear(), d2.getMonth(), d2.getDate()).getTime();
  return Math.round(Math.abs(t2 - t1) / (1000 * 60 * 60 * 24));
}

function calculateStreak(completions: CompletionEntry[]): number {
  const uniqueDates = Array.from(new Set(completions.map(c => c.date).filter(Boolean))).sort();
  if (uniqueDates.length === 0) return 0;

  const parsedDates: Date[] = [];
  for (const dStr of uniqueDates) {
    const d = new Date(dStr + 'T00:00:00');
    if (!isNaN(d.getTime())) {
      parsedDates.push(d);
    }
  }

  if (parsedDates.length === 0) return 0;

  const todayLocal = new Date();
  const lastSessionDate = parsedDates[parsedDates.length - 1];
  const daysSinceLast = getDaysDiff(lastSessionDate, todayLocal);

  if (daysSinceLast > 7) {
    return 0;
  }

  const streakPenalty = daysSinceLast > 4;
  let streak = 1;

  for (let i = parsedDates.length - 1; i > 0; i--) {
    const gap = getDaysDiff(parsedDates[i - 1], parsedDates[i]);
    if (gap <= 3) {
      streak++;
    } else {
      break;
    }
  }

  if (streakPenalty) {
    return Math.max(1, Math.floor(streak / 2));
  }
  return streak;
}

function calculateConsistency(completions: CompletionEntry[], sessionsPerWeek: number): number {
  const today = new Date();
  const dayOfWeek = today.getDay();
  // Convert Sun=0 to 6, Mon=1 to 0
  const isoWeekday = dayOfWeek === 0 ? 6 : dayOfWeek - 1;

  const monday = new Date(today);
  monday.setDate(today.getDate() - isoWeekday);
  monday.setHours(0, 0, 0, 0);

  const weeks: { start: Date; end: Date }[] = [];
  for (let i = 3; i >= 0; i--) {
    const w_monday = new Date(monday);
    w_monday.setDate(monday.getDate() - i * 7);
    w_monday.setHours(0, 0, 0, 0);

    const w_sunday = new Date(w_monday);
    w_sunday.setDate(w_monday.getDate() + 6);
    w_sunday.setHours(23, 59, 59, 999);

    weeks.push({ start: w_monday, end: w_sunday });
  }

  const weights = [0.15, 0.20, 0.30, 0.35];
  let weightedScore = 0.0;

  for (let idx = 0; idx < 4; idx++) {
    const { start, end } = weeks[idx];
    let sessionsThisWeek = 0;

    for (const entry of completions) {
      if (entry.date) {
        const c_date = new Date(entry.date + 'T00:00:00');
        if (c_date >= start && c_date <= end) {
          sessionsThisWeek++;
        }
      }
    }

    let weeklyScore = 0;
    if (idx === 3) {
      const daysElapsed = today.getDay() === 0 ? 7 : today.getDay();
      const paceFactor = Math.min(1.0, daysElapsed / 7.0);
      const expected = Math.max(1, Math.round(sessionsPerWeek * paceFactor));
      weeklyScore = Math.min(1.0, sessionsThisWeek / expected);
    } else {
      weeklyScore = Math.min(1.0, sessionsThisWeek / sessionsPerWeek);
    }
    weightedScore += weeklyScore * weights[idx];
  }

  const streak = calculateStreak(completions);
  const streakBonus = streak >= 14 ? 5 : (streak >= 7 ? 2 : 0);

  return Math.min(100, Math.round(weightedScore * 100 + streakBonus));
}

function calculateVolume(
  completions: CompletionEntry[],
  createdDateStr: string,
  sessionsPerWeek: number
): number {
  let createdDate = new Date();
  if (createdDateStr) {
    createdDate = new Date(createdDateStr + 'T00:00:00');
    if (isNaN(createdDate.getTime())) {
      createdDate = new Date();
      createdDate.setDate(createdDate.getDate() - 28);
    }
  } else {
    createdDate = new Date();
    createdDate.setDate(createdDate.getDate() - 28);
  }

  const today = new Date();
  const daysSinceCreation = getDaysDiff(createdDate, today);
  const weeksActive = Math.max(1.0, daysSinceCreation / 7.0);
  const expectedSessions = Math.max(1, Math.round(weeksActive * sessionsPerWeek));

  const rawScore = Math.min(1.0, completions.length / expectedSessions);
  const baseFloor = completions.length >= 10 ? 40 : 20;

  return Math.max(baseFloor, Math.round(rawScore * 100));
}

function getDrillInfo(drillIdOrName: string, drills: Drill[]): Drill | null {
  const clean = drillIdOrName.trim().toLowerCase();
  let matched = drills.find(d => d.drill_id?.toLowerCase() === clean);
  if (matched) return matched;
  matched = drills.find(d => d.drill_name?.toLowerCase() === clean);
  return matched || null;
}

function calculateCoverage(
  completions: CompletionEntry[],
  focusAreas: string[],
  drills: Drill[],
  plan: WeeklyTrainingPlan | null,
  primaryPosition: string,
  secondaryPosition: string
): number {
  const today = new Date();
  const fourteenDaysAgo = new Date(today);
  fourteenDaysAgo.setDate(today.getDate() - 14);
  fourteenDaysAgo.setHours(0, 0, 0, 0);

  const recentCompletions = completions.filter(c => {
    if (!c.date) return false;
    const c_date = new Date(c.date + 'T00:00:00');
    return c_date >= fourteenDaysAgo;
  });

  if (recentCompletions.length === 0) {
    return 30;
  }

  const recentDrillIdsAndNames = new Set<string>();
  for (const c of recentCompletions) {
    if (c.drills_completed) {
      for (const dId of c.drills_completed) {
        if (dId) recentDrillIdsAndNames.add(dId);
      }
    }

    const cWeek = c.week;
    const cDay = c.day;
    if (plan && plan.weeks) {
      for (const w of plan.weeks) {
        if (w.week_number === cWeek) {
          for (const s of w.sessions) {
            if (s.day_number === cDay) {
              for (const d of s.drills) {
                if (d.drill_id) {
                  recentDrillIdsAndNames.add(d.drill_id);
                } else if (d.drill_name) {
                  recentDrillIdsAndNames.add(d.drill_name);
                }
              }
            }
          }
        }
      }
    }
  }

  const recentDrillsInfo: Drill[] = [];
  for (const identifier of recentDrillIdsAndNames) {
    const drillInfo = getDrillInfo(identifier, drills);
    if (drillInfo) {
      recentDrillsInfo.push(drillInfo);
    }
  }

  if (recentDrillsInfo.length === 0) {
    return 30;
  }

  let focusRatio = 0.5;
  if (focusAreas && focusAreas.length > 0) {
    let focusAreasTrained = 0;
    for (const fa of focusAreas) {
      const faLower = fa.toLowerCase().trim();
      let trained = false;

      for (const drill of recentDrillsInfo) {
        const cat = (drill.category || '').toLowerCase();
        const skillCat = (drill.skill_category || '').toLowerCase();
        const tags = (drill.tags || '').toLowerCase();
        const tagsArray = tags.split('|').map(t => t.trim());

        if (
          cat.includes(faLower) ||
          skillCat.includes(faLower) ||
          tagsArray.some(t => t.includes(faLower)) ||
          tags.includes(faLower)
        ) {
          trained = true;
          break;
        } else {
          const faWords = faLower.split(/\s+/);
          for (const word of faWords) {
            if (word.length > 3) {
              if (
                cat.includes(word) ||
                skillCat.includes(word) ||
                tagsArray.some(t => t.includes(word)) ||
                tags.includes(word)
              ) {
                trained = true;
                break;
              }
            }
          }
          if (trained) break;
        }
      }

      if (trained) {
        focusAreasTrained++;
      }
    }
    focusRatio = focusAreasTrained / focusAreas.length;
  }

  const primaryLower = primaryPosition?.toLowerCase().trim() || '';
  let secondaryLower = secondaryPosition?.toLowerCase().trim() || '';
  if (secondaryLower === 'none') {
    secondaryLower = '';
  }

  let primaryMatches = 0;
  let secondaryMatches = 0;
  const totalDrills = recentDrillsInfo.length;

  for (const drill of recentDrillsInfo) {
    const posRelRaw = drill.position_relevance || '';
    let posRelParts: string[] = [];
    if (Array.isArray(posRelRaw)) {
      posRelParts = posRelRaw.map(p => p.toLowerCase().trim()).filter(Boolean);
    } else if (posRelRaw) {
      posRelParts = String(posRelRaw).split('|').map(p => p.toLowerCase().trim()).filter(Boolean);
    }

    if (posRelParts.length === 0) {
      primaryMatches++;
      secondaryMatches++;
    } else {
      if (primaryLower && posRelParts.includes(primaryLower)) {
        primaryMatches++;
      }
      if (secondaryLower && posRelParts.includes(secondaryLower)) {
        secondaryMatches++;
      }
    }
  }

  const primaryRatio = primaryMatches / totalDrills;
  const secondaryRatio = secondaryMatches / totalDrills;

  let positionAlignment = 0;
  if (secondaryLower) {
    positionAlignment = 0.70 * primaryRatio + 0.30 * secondaryRatio;
  } else {
    positionAlignment = primaryRatio;
  }

  let score = Math.round((0.70 * focusRatio + 0.30 * positionAlignment) * 100);

  let hasWeakFootBonus = false;
  if (focusAreas && focusAreas.includes('Weak Foot Development')) {
    for (const drill of recentDrillsInfo) {
      const tags = (drill.tags || '').toLowerCase();
      if (tags.includes('weak foot') || tags.includes('left foot') || tags.includes('right foot')) {
        hasWeakFootBonus = true;
        break;
      }
    }
  }

  if (hasWeakFootBonus) {
    score += 10;
  }

  return Math.min(100, Math.max(30, score));
}

const REWARD_MATRIX: Record<string, Record<string, number>> = {
  'Recreational':     { beginner: 1.0, intermediate: 1.0, advanced: 1.2, elite: 1.4 },
  'Competitive Club': { beginner: 0.5, intermediate: 1.0, advanced: 1.0, elite: 1.2 },
  'Academy/Select':  { beginner: 0.2, intermediate: 0.6, advanced: 1.0, elite: 1.0 },
};

function calculateProgression(
  completions: CompletionEntry[],
  level: string,
  plan: WeeklyTrainingPlan | null,
  drills: Drill[]
): number {
  const levelRewards = REWARD_MATRIX[level] || { beginner: 1.0, intermediate: 1.0, advanced: 1.0, elite: 1.0 };

  let totalDrillsChecked = 0;
  let totalPoints = 0.0;

  for (const c of completions) {
    const cWeek = c.week;
    const cDay = c.day;
    if (plan && plan.weeks) {
      for (const w of plan.weeks) {
        if (w.week_number === cWeek) {
          for (const s of w.sessions) {
            if (s.day_number === cDay) {
              for (const d of s.drills) {
                const drillInfo = getDrillInfo(d.drill_id || d.drill_name || '', drills);
                if (drillInfo) {
                  const diff = (drillInfo.difficulty || 'intermediate').toLowerCase().trim();
                  const multiplier = levelRewards[diff] !== undefined ? levelRewards[diff] : 1.0;
                  totalPoints += multiplier;
                  totalDrillsChecked++;
                }
              }
            }
          }
        }
      }
    }
  }

  if (totalDrillsChecked === 0) {
    return 50;
  }

  return Math.min(100, Math.round((totalPoints / totalDrillsChecked) * 100));
}

export function calculateRRS(
  profile: AthleteProfile,
  completionLog: CompletionLog | null,
  plan: WeeklyTrainingPlan | null,
  drills: Drill[],
  existingHistory: RRSHistory | null
): {
  overall: number;
  pillars: {
    consistency: number;
    volume: number;
    coverage: number;
    progression: number;
  };
  benchmark: { label: string; color: string };
  unlocked: boolean;
  sessionsUntilUnlock: number;
  weeklyDelta: number;
  nextActions: string[];
  snapshotDate: string;
} {
  const completions = completionLog?.completions ?? [];
  const totalSessions = completions.length;
  const unlocked = totalSessions >= 5;
  const sessionsUntilUnlock = Math.max(0, 5 - totalSessions);

  let consistency = 0;
  let volume = 0;
  let coverage = 0;
  let progression = 0;
  let overall = 0;

  if (unlocked) {
    const sessionsPerWeek = profile.sessions_per_week || 3;
    consistency = calculateConsistency(completions, sessionsPerWeek);
    volume = calculateVolume(completions, profile.created_date, sessionsPerWeek);
    coverage = calculateCoverage(completions, profile.focus_areas || [], drills, plan, profile.position, profile.secondary_position);
    progression = calculateProgression(completions, profile.level || 'Recreational', plan, drills);

    overall = Math.round(
      consistency * 0.30 +
      volume * 0.20 +
      coverage * 0.25 +
      progression * 0.25
    );

    // Momentum floor
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const sevenDaysAgo = new Date(today);
    sevenDaysAgo.setDate(today.getDate() - 7);
    sevenDaysAgo.setHours(0, 0, 0, 0);

    const recentActivity = completions.some(c => {
      if (!c.date) return false;
      const c_date = new Date(c.date + 'T00:00:00');
      return c_date >= sevenDaysAgo;
    });

    if (recentActivity && existingHistory && existingHistory.snapshots && existingHistory.snapshots.length > 0) {
      const lastScore = existingHistory.snapshots[existingHistory.snapshots.length - 1].overall;
      overall = Math.max(overall, lastScore - 3);
    }
  }

  const benchmark = getBenchmark(overall);

  // Delta calculation
  let weeklyDelta = 0;
  if (existingHistory && existingHistory.snapshots && existingHistory.snapshots.length > 0) {
    const sn = existingHistory.snapshots;
    let lastSnapshot = sn[sn.length - 1];
    if (sn.length >= 2 && lastSnapshot.overall === overall) {
      lastSnapshot = sn[sn.length - 2];
    }
    const rawDelta = overall - lastSnapshot.overall;
    weeklyDelta = Math.max(-5, Math.min(15, rawDelta));
  }

  // Next Actions
  let nextActions: string[] = [];
  if (unlocked) {
    let completedThisWeek = 0;
    if (plan) {
      const currentWeekNumber = plan.current_week_number;
      const currentWeek = plan.weeks?.find(w => w.week_number === currentWeekNumber);
      if (currentWeek && currentWeek.sessions) {
        completedThisWeek = currentWeek.sessions.filter(s => s.completed).length;
      }
    }

    const pillarScores = [
      { name: 'Consistency', score: consistency },
      { name: 'Volume', score: volume },
      { name: 'Coverage', score: coverage },
      { name: 'Progression', score: progression },
    ];
    pillarScores.sort((a, b) => a.score - b.score);

    const focusAreas = profile.focus_areas || [];

    for (const p of pillarScores) {
      if (nextActions.length >= 3) break;
      if (p.name === 'Coverage' && p.score < 60) {
        const lowestFocusArea = focusAreas[0] || 'Weak Foot Development';
        nextActions.push(`Train drills in your focus areas — especially ${lowestFocusArea}`);
      } else if (p.name === 'Consistency' && p.score < 60) {
        const sessionsPerWeek = profile.sessions_per_week || 3;
        const needed = Math.max(1, sessionsPerWeek - completedThisWeek);
        nextActions.push(`Complete ${needed} more sessions this week to build your streak`);
      } else if (p.name === 'Progression' && p.score < 60) {
        nextActions.push('Push to higher difficulty drills to accelerate your score');
      }
    }

    if (nextActions.length < 2) {
      nextActions.push('Keep completing your scheduled sessions to maintain consistency');
    }
    if (nextActions.length < 2) {
      nextActions.push('Review your athlete profile to ensure focus areas are up to date');
    }
  } else {
    nextActions = ['Complete at least 5 sessions to unlock actions and see recommendations'];
  }

  const snapshotDate = getLocalDateString(new Date());

  return {
    overall,
    pillars: {
      consistency,
      volume,
      coverage,
      progression,
    },
    benchmark,
    unlocked,
    sessionsUntilUnlock,
    weeklyDelta,
    nextActions,
    snapshotDate,
  };
}
