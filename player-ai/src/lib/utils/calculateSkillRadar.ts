import type {
  AthleteProfile,
  CompletionLog,
  WeeklyTrainingPlan,
  Drill,
} from '@/lib/types/player';

export interface SkillRadarResult {
  axes: string[];     // skill area names
  scores: number[];   // 0-100 score per axis, same order as axes
  hasData: boolean;
}

function getDrillInfo(drillIdOrName: string, drills: Drill[]): Drill | null {
  const clean = drillIdOrName.trim().toLowerCase();
  let matched = drills.find((d) => d.drill_id?.toLowerCase() === clean);
  if (matched) return matched;
  matched = drills.find((d) => d.drill_name?.toLowerCase() === clean);
  return matched || null;
}

function drillMatchesAxis(drill: Drill, axis: string): boolean {
  const axisLower = axis.toLowerCase().trim();
  const cat = (drill.skill_category || '').toLowerCase().trim();
  const series = (drill.series_name || '').toLowerCase().trim();
  const name = (drill.drill_name || '').toLowerCase().trim();
  const tags = (drill.tags || '').toLowerCase().trim();
  const tagsArray = tags.split('|').map((t) => t.trim());

  if (
    cat.includes(axisLower) ||
    series.includes(axisLower) ||
    name.includes(axisLower) ||
    tagsArray.some((t) => t.includes(axisLower)) ||
    tags.includes(axisLower)
  ) {
    return true;
  }

  // Any word in axis (>3 chars) appears in any of the above
  const axisWords = axisLower.split(/\s+/);
  for (const word of axisWords) {
    if (word.length > 3) {
      if (
        cat.includes(word) ||
        series.includes(word) ||
        name.includes(word) ||
        tagsArray.some((t) => t.includes(word)) ||
        tags.includes(word)
      ) {
        return true;
      }
    }
  }

  return false;
}

export function calculateSkillRadar(
  profile: AthleteProfile,
  completionLog: CompletionLog | null,
  plan: WeeklyTrainingPlan | null,
  drills: Drill[]
): SkillRadarResult {
  const completions = completionLog?.completions ?? [];
  if (completions.length < 2) {
    return { axes: [], scores: [], hasData: false };
  }

  // Start axes from focus_areas (copy, max 6 total)
  const axes = [...(profile.focus_areas || [])].slice(0, 6);

  // Get recent completions in last 28 days
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const twentyEightDaysAgo = new Date(today);
  twentyEightDaysAgo.setDate(today.getDate() - 28);
  twentyEightDaysAgo.setHours(0, 0, 0, 0);

  const recentCompletions = completions.filter((c) => {
    if (!c.date) return false;
    const cDate = new Date(c.date + 'T00:00:00');
    return cDate >= twentyEightDaysAgo;
  });

  // Collect unique skill_category values from recent completed drills
  for (const c of recentCompletions) {
    if (axes.length >= 6) break;

    const sessionDrills: Drill[] = [];
    const sessionDrillIdsOrNames = new Set<string>();

    if (c.drills_completed) {
      for (const dId of c.drills_completed) {
        if (dId && !sessionDrillIdsOrNames.has(dId)) {
          const dInfo = getDrillInfo(dId, drills);
          if (dInfo) {
            sessionDrills.push(dInfo);
            sessionDrillIdsOrNames.add(dId);
          }
        }
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
                const identifier = d.drill_id || d.drill_name;
                if (identifier && !sessionDrillIdsOrNames.has(identifier)) {
                  const dInfo = getDrillInfo(identifier, drills);
                  if (dInfo) {
                    sessionDrills.push(dInfo);
                    sessionDrillIdsOrNames.add(identifier);
                  }
                }
              }
            }
          }
        }
      }
    }

    for (const drill of sessionDrills) {
      if (axes.length >= 6) break;
      const cat = drill.skill_category?.trim();
      if (cat && !axes.some((a) => a.toLowerCase() === cat.toLowerCase())) {
        axes.push(cat);
      }
    }
  }

  // Positional defaults if fewer than 4 axes
  if (axes.length < 4) {
    const position = (profile.position || '').toLowerCase();
    let defaults: string[] = [];

    if (position.includes('striker') || position.includes('forward')) {
      defaults = ['Finishing', 'Movement', 'First Touch'];
    } else if (position.includes('winger')) {
      defaults = ['Dribbling', 'Crossing', 'Speed'];
    } else if (position.includes('midfielder') || position.includes('midfield')) {
      defaults = ['Passing', 'Pressing', 'Ball Control'];
    } else if (
      position.includes('center back') ||
      position.includes('cb') ||
      position.includes('defender')
    ) {
      defaults = ['Defending', 'Aerial', 'Distribution'];
    } else if (
      position.includes('full back') ||
      position.includes('fb') ||
      position.includes('fullback')
    ) {
      defaults = ['Defending', 'Overlapping', 'Crossing'];
    } else if (
      position.includes('goalkeeper') ||
      position.includes('gk') ||
      position.includes('keeper')
    ) {
      defaults = ['Shot Stopping', 'Distribution', 'Positioning'];
    } else {
      defaults = ['Finishing', 'Movement', 'First Touch'];
    }

    for (const d of defaults) {
      if (axes.length >= 4) break;
      if (!axes.some((a) => a.toLowerCase() === d.toLowerCase())) {
        axes.push(d);
      }
    }
  }

  // Level-based skill ceiling — players should always feel
  // there is more to achieve, scaled to their ambition
  const levelCeilings: Record<string, number> = {
    'Recreational':       65,
    'Competitive Club':   72,
    'Academy/Select':     78,
    'Varsity High School': 80,
    'College':            83,
    'Professional':       87,
  };
  const skillCeiling = levelCeilings[profile.level] ?? 75;

  // Calculate scores per axis
  const scores: number[] = [];
  const focusAreas = profile.focus_areas || [];

  for (const axis of axes) {
    let matchingDrillsCount = 0;

    for (const c of recentCompletions) {
      const sessionDrills: Drill[] = [];
      const sessionDrillIdsOrNames = new Set<string>();

      if (c.drills_completed) {
        for (const dId of c.drills_completed) {
          if (dId && !sessionDrillIdsOrNames.has(dId)) {
            const dInfo = getDrillInfo(dId, drills);
            if (dInfo) {
              sessionDrills.push(dInfo);
              sessionDrillIdsOrNames.add(dId);
            }
          }
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
                  const identifier = d.drill_id || d.drill_name;
                  if (identifier && !sessionDrillIdsOrNames.has(identifier)) {
                    const dInfo = getDrillInfo(identifier, drills);
                    if (dInfo) {
                      sessionDrills.push(dInfo);
                      sessionDrillIdsOrNames.add(identifier);
                    }
                  }
                }
              }
            }
          }
        }
      }

      for (const drill of sessionDrills) {
        if (drillMatchesAxis(drill, axis)) {
          matchingDrillsCount++;
        }
      }
    }

    let score = 20;
    if (matchingDrillsCount > 0) {
      score = matchingDrillsCount * 15;
    }

    if (focusAreas.includes(axis)) {
      // Focus areas get a floor of 50 — a stated priority should never look neglected
      score = Math.max(50, score + 10);
    }

    // Cap at level-based ceiling — no youth player should feel "done"
    score = Math.min(skillCeiling, score);
    scores.push(score);
  }

  return { axes, scores, hasData: true };
}
