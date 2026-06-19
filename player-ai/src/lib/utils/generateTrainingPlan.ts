import type {
  AthleteProfile,
  WeeklyTrainingPlan,
  TrainingWeek,
  TrainingSession,
  DrillInSession,
  Drill
} from '@/lib/types/player';

export function generateTrainingPlan(
  profile: AthleteProfile,
  drills: Drill[],
  weekNumber: number = 1,
  existingPlan?: WeeklyTrainingPlan
): WeeklyTrainingPlan {
  // Step 1 — Derive week number
  let currentWeekNumber = weekNumber;
  if (existingPlan && existingPlan.weeks && existingPlan.weeks.length > 0) {
    currentWeekNumber = Math.max(...existingPlan.weeks.map(w => w.week_number || 1)) + 1;
  }

  // Step 2 — Filter published drills only
  const publishedDrills = drills.filter(
    d => (d.status || 'Published').toLowerCase().trim() === 'published'
  );

  // Step 3 — Read profile parameters
  const sessionsPerWeek = Number(profile.sessions_per_week ?? 3);
  const sessionDuration = Number(profile.session_duration ?? 30);
  const position = profile.position || '';
  const secondaryPosition = profile.secondary_position || '';
  const level = profile.level || 'Recreational';
  const league = profile.league || '';
  const gameDays = new Set(profile.game_days ?? []);
  const equipmentAvailable = (profile.equipment_available || []).map(e => e.toLowerCase());
  const focusAreas = (profile.focus_areas || []).map(f => f.toLowerCase());

  // Step 4 — Difficulty mapping (league refines level)
  const eliteLeagues = new Set(['ECNL', 'MLS Next', 'Girls Academy', 'USL Championship', 'MLS Next Pro', 'MLS', 'USL Super League']);
  const advancedLeagues = new Set(['UPSL', 'USL League Two', 'USL1', 'State Cup', 'ECNL Regional']);

  let allowedDifficulties: string[];
  if (level === 'Recreational') {
    allowedDifficulties = ['beginner', 'intermediate'];
  } else if (level === 'Competitive Club') {
    if (eliteLeagues.has(league)) {
      allowedDifficulties = ['advanced', 'elite'];
    } else if (advancedLeagues.has(league)) {
      allowedDifficulties = ['intermediate', 'advanced', 'elite'];
    } else {
      allowedDifficulties = ['intermediate', 'advanced'];
    }
  } else if (level === 'Academy/Select') {
    allowedDifficulties = ['advanced', 'elite'];
  } else if (['College', 'Professional'].includes(level)) {
    allowedDifficulties = ['elite'];
  } else {
    allowedDifficulties = ['beginner', 'intermediate', 'advanced', 'elite'];
  }

  const hasPartner = equipmentAvailable.some(e => e.includes('partner'));

  // Step 5 — Filter drills
  let filteredDrills = publishedDrills.filter(drill => {
    const catLower = (drill.category || '').toLowerCase().trim();
    const isWarmupOrCooldown = catLower === 'warmup' || catLower === 'cool down' || catLower === 'cooldown';

    // A. Difficulty check
    if (!isWarmupOrCooldown) {
      const difficultyLower = (drill.difficulty || 'intermediate').toLowerCase().trim();
      if (!allowedDifficulties.includes(difficultyLower)) {
        return false;
      }
    }

    // B. Solo possibility check
    const soloPossible = drill.solo_possible !== false;
    if (!hasPartner && !soloPossible) {
      return false;
    }

    // C. Equipment check
    const minEquipment = (drill.min_equipment || 'Ball only').toLowerCase().trim();
    if (minEquipment.includes('cones')) {
      if (!equipmentAvailable.some(e => e.includes('cone'))) {
        return false;
      }
    }
    if (minEquipment.includes('goal')) {
      if (!equipmentAvailable.some(e => e.includes('goal'))) {
        return false;
      }
    }
    if (minEquipment.includes('rebounder') || minEquipment.includes('wall')) {
      if (!equipmentAvailable.some(e => e.includes('rebounder') || e.includes('wall'))) {
        return false;
      }
    }
    if (minEquipment.includes('partner')) {
      if (!hasPartner) {
        return false;
      }
    }

    return true;
  });

  if (filteredDrills.length === 0) {
    filteredDrills = publishedDrills;
  }

  // Step 6 — Bucket drills
  let warmups: Drill[] = [];
  let cooldownsPool: Drill[] = [];
  let gameApps: Drill[] = [];
  let mainDrills: Drill[] = [];

  for (const drill of filteredDrills) {
    const cat = (drill.category || '').toLowerCase().trim();
    const drillTypeVal = (drill.drill_type || '').toLowerCase().trim();

    if (cat === 'warmup') {
      warmups.push(drill);
    } else if (cat === 'cool down' || cat === 'cooldown') {
      cooldownsPool.push(drill);
    } else if (cat === 'game application' || drillTypeVal === 'game application') {
      gameApps.push(drill);
    } else {
      mainDrills.push(drill);
    }
  }

  // Fallback empty buckets gracefully
  if (warmups.length === 0) {
    const lowIntensity = filteredDrills.filter(d => (d.intensity || '').toLowerCase().trim() === 'low');
    warmups = lowIntensity.length > 0 ? lowIntensity : filteredDrills;
  }

  if (mainDrills.length === 0) {
    const nonAuxiliary = filteredDrills.filter(d => {
      const c = (d.category || '').toLowerCase().trim();
      return c !== 'warmup' && c !== 'cool down' && c !== 'cooldown' && c !== 'game application';
    });
    mainDrills = nonAuxiliary.length > 0 ? nonAuxiliary : filteredDrills;
  }

  if (gameApps.length === 0) {
    if (cooldownsPool.length > 0) {
      gameApps = cooldownsPool;
    } else {
      const highIntensity = filteredDrills.filter(d => (d.intensity || '').toLowerCase().trim() === 'high');
      gameApps = highIntensity.length > 0 ? highIntensity : filteredDrills;
    }
  }

  // Step 7 — selectBestDrills function
  function selectBestDrills(
    candidates: Drill[],
    count: number,
    excludeNames: Set<string>,
    preferredType?: string,
    preferredIntensity?: string
  ): Drill[] {
    const scoredCandidates = candidates
      .filter(c => !excludeNames.has(c.drill_name))
      .map(c => {
        let score = 0.0;

        // Position relevance
        const posRelParts = c.position_relevance
          ? c.position_relevance.split('|').map(p => p.toLowerCase().trim()).filter(Boolean)
          : [];

        const playerPositions = [position, secondaryPosition]
          .filter(p => p && p.toLowerCase() !== 'none')
          .map(p => p.toLowerCase());

        if (posRelParts.length === 0) {
          score += 1.0;
        } else if (playerPositions.some(p => posRelParts.includes(p))) {
          score += 6.0;
        } else {
          score -= 4.0;
        }

        // Focus areas boost
        const cCat = (c.category || '').toLowerCase();
        const cSkill = (c.skill_category || '').toLowerCase();
        const cTags = c.tags
          ? c.tags.split('|').map(t => t.toLowerCase().trim()).filter(Boolean)
          : [];

        for (const fa of focusAreas) {
          if (cCat.includes(fa) || cSkill.includes(fa) || cTags.some(t => t.includes(fa))) {
            score += 5.0;
          }
        }

        // Preferred type boost
        if (preferredType) {
          const cType = (c.drill_type || '').toLowerCase().trim();
          if (cType === preferredType.toLowerCase().trim()) {
            score += 10.0;
          }
        }

        // Preferred intensity boost
        if (preferredIntensity) {
          const cIntensity = (c.intensity || '').toLowerCase().trim();
          if (cIntensity === preferredIntensity.toLowerCase().trim()) {
            score += 8.0;
          }
        }

        // Random slight variance
        score += Math.random();

        return { score, drill: c };
      });

    scoredCandidates.sort((a, b) => b.score - a.score);
    const selected = scoredCandidates.slice(0, count).map(x => x.drill);

    for (const s of selected) {
      excludeNames.add(s.drill_name);
    }

    return selected;
  }

  // Step 8 — Duration bucketing
  let warmupDur = 5;
  let mainCount = 2;
  let mainDur = 10;
  let coolDur = 5;
  let includeGameApp = false;

  if (sessionDuration <= 20) {
    warmupDur = 5;
    mainCount = 2;
    mainDur = 5;
    coolDur = 5;
    includeGameApp = false;
  } else if (sessionDuration <= 30) {
    warmupDur = 5;
    mainCount = 2;
    mainDur = 10;
    coolDur = 5;
    includeGameApp = false;
  } else if (sessionDuration <= 45) {
    warmupDur = 5;
    mainCount = 3;
    mainDur = 10;
    coolDur = 10;
    includeGameApp = true;
  } else if (sessionDuration <= 60) {
    warmupDur = 10;
    mainCount = 3;
    mainDur = 15;
    coolDur = 5;
    includeGameApp = true;
  } else if (sessionDuration <= 75) {
    warmupDur = 10;
    mainCount = 3;
    mainDur = 18;
    coolDur = 11;
    includeGameApp = true;
  } else if (sessionDuration <= 90) {
    warmupDur = 15;
    mainCount = 3;
    mainDur = 20;
    coolDur = 15;
    includeGameApp = true;
  } else {
    warmupDur = 15;
    mainCount = 4;
    mainDur = 22;
    coolDur = 17;
    includeGameApp = true;
  }

  // Helper to map Drill to DrillInSession
  const mapToSessionDrill = (
    d: Drill,
    allocatedTime: number,
    blockType: string
  ): DrillInSession => {
    return {
      drill_id: d.drill_id,
      drill_name: d.drill_name,
      category: d.category,
      description: d.description,
      duration_minutes: d.duration_minutes,
      allocated_time: allocatedTime,
      block_type: blockType,
      intensity: d.intensity,
      difficulty: d.difficulty,
      equipment: d.equipment,
      coaching_cues: d.coaching_cues || '',
      coaching_points: d.coaching_points || '',
      video_url: d.video_url || '',
      presenter_id: d.presenter_id || '',
      solo_possible: d.solo_possible !== false,
    };
  };

  // Step 9 — Build sessions
  // If game_days are set, pick training days that avoid game days and the day after
  // (recovery day). Spread sessions through the week where possible.
  const availableWeekDays: number[] = [];
  if (gameDays.size > 0) {
    const recoveryDays = new Set([...gameDays].map(d => (d + 1) % 7));
    const blocked = new Set([...gameDays, ...recoveryDays]);
    for (let d = 0; d < 7; d++) {
      if (!blocked.has(d)) availableWeekDays.push(d);
    }
  }

  const sessions: TrainingSession[] = [];
  const usedDrillNames = new Set<string>();

  for (let day = 1; day <= sessionsPerWeek; day++) {
    const prefIntensity = level === 'Recreational' ? 'medium' : 'high';
    const prefType = day <= 2 ? 'Isolation' : 'Pressure';

    // Warmup selection
    let dayWarmups = selectBestDrills(warmups, 1, usedDrillNames, undefined, 'low');
    if (dayWarmups.length === 0) {
      dayWarmups = selectBestDrills(warmups, 1, new Set<string>(), undefined, 'low');
    }

    // Main technical drills selection
    let dayMains = selectBestDrills(mainDrills, mainCount, usedDrillNames, prefType, prefIntensity);
    if (dayMains.length < mainCount) {
      const needed = mainCount - dayMains.length;
      const additionalMains = selectBestDrills(mainDrills, needed, new Set<string>(), prefType, prefIntensity);
      dayMains = [...dayMains, ...additionalMains];
    }

    // Cooldown/Game App selection
    let dayCools: Drill[] = [];
    if (includeGameApp) {
      dayCools = selectBestDrills(gameApps, 1, usedDrillNames, undefined, 'low');
      if (dayCools.length === 0) {
        dayCools = selectBestDrills(gameApps, 1, new Set<string>(), undefined, 'low');
      }
    }
    if (dayCools.length === 0) {
      dayCools = selectBestDrills(cooldownsPool, 1, usedDrillNames, undefined, 'low');
      if (dayCools.length === 0) {
        dayCools = selectBestDrills(cooldownsPool, 1, new Set<string>(), undefined, 'low');
      }
    }
    if (dayCools.length === 0) {
      dayCools = selectBestDrills(warmups, 1, usedDrillNames, undefined, 'low');
      if (dayCools.length === 0) {
        dayCools = selectBestDrills(warmups, 1, new Set<string>(), undefined, 'low');
      }
    }

    const sessionDrills: DrillInSession[] = [];
    if (dayWarmups.length > 0) {
      sessionDrills.push(mapToSessionDrill(dayWarmups[0], warmupDur, 'warmup'));
    }
    dayMains.forEach((dm) => {
      sessionDrills.push(mapToSessionDrill(dm, mainDur, 'technical'));
    });
    if (dayCools.length > 0) {
      sessionDrills.push(mapToSessionDrill(dayCools[0], coolDur, 'cooldown'));
    }

    // Adjust total to match sessionDuration
    const allocatedTotal = sessionDrills.reduce((sum, d) => sum + d.allocated_time, 0);
    const diff = sessionDuration - allocatedTotal;
    if (diff !== 0 && sessionDrills.length > 0) {
      const technicalDrills = sessionDrills.filter(d => d.block_type === 'technical');
      if (technicalDrills.length > 0) {
        const baseDiff = Math.trunc(diff / technicalDrills.length);
        const rem = diff % technicalDrills.length;
        technicalDrills.forEach((sd, idx) => {
          sd.allocated_time += baseDiff;
          if (rem > 0 && idx < rem) {
            sd.allocated_time += 1;
          } else if (rem < 0 && idx < Math.abs(rem)) {
            sd.allocated_time -= 1;
          }
        });
      } else {
        sessionDrills[0].allocated_time += diff;
      }
    }

    // Session focus theme
    let focusTheme = 'Development Focus';
    if (profile.focus_areas && profile.focus_areas[day - 1]) {
      focusTheme = `${profile.focus_areas[day - 1]} Focus`;
    } else {
      if (day === 1) {
        focusTheme = profile.focus_areas && profile.focus_areas[0] ? `${profile.focus_areas[0]} Focus` : 'Technical Focus';
      } else if (day === 2) {
        focusTheme = profile.focus_areas && profile.focus_areas[1] ? `${profile.focus_areas[1]} Focus` : 'Technical Focus';
      } else if (day === 3) {
        focusTheme = profile.focus_areas && profile.focus_areas[2] ? `${profile.focus_areas[2]} Focus` : '1v1 Attacking';
      } else if (day === 4) {
        focusTheme = 'Weak Foot & Technical Focus';
      }
    }

    const sessionName = `Session ${day}: ${profile.name}'s Development Plan - ${focusTheme}`;

    // Assign a calendar day_number (1=Mon … 7=Sun) avoiding game/recovery days
    // Falls back to sequential 1-7 if no game_days are configured
    const calendarDay = availableWeekDays.length >= sessionsPerWeek
      ? (availableWeekDays[day - 1] === 0 ? 7 : availableWeekDays[day - 1]) // 0=Sun→7
      : day;

    sessions.push({
      day_number: calendarDay,
      name: sessionName,
      duration_minutes: sessionDuration,
      drills: sessionDrills,
      completed: false,
      completed_date: null,
    });
  }

  // Step 10 — Assemble and return
  const nowIso = new Date().toISOString();
  const newWeek: TrainingWeek = {
    week_number: currentWeekNumber,
    generated_date: nowIso,
    archived_date: undefined,
    sessions,
  };

  if (existingPlan && existingPlan.weeks && existingPlan.weeks.length > 0) {
    const currentNum = existingPlan.current_week_number ?? 1;
    const updatedWeeks = existingPlan.weeks.map(w => {
      if (w.week_number === currentNum && !w.archived_date) {
        return {
          ...w,
          archived_date: nowIso,
        };
      }
      return w;
    });
    updatedWeeks.push(newWeek);
    return {
      current_week_number: currentWeekNumber,
      generated_date: nowIso,
      weeks: updatedWeeks,
    };
  }

  return {
    current_week_number: currentWeekNumber,
    generated_date: nowIso,
    weeks: [newWeek],
  };
}
