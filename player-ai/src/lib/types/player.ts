export interface AthleteProfile {
  name: string;
  age: number;
  email?: string;
  gender?: 'M' | 'W';      // 'M' = Men's programs, 'W' = Women's programs (recruiting filter)
  preferred_foot: string;
  position: string;
  secondary_position: string;
  level: string;
  league?: string;          // e.g. 'ECNL Girls', 'MLS Next', 'UPSL'
  club_name?: string;       // e.g. 'FC Dallas'
  grad_year?: number;       // e.g. 2027 — used in recruiting emails
  game_days?: number[];     // 0=Sun … 6=Sat — days with games, skipped in training plan
  target_level: string;
  sessions_per_week: number;
  session_duration: number;
  focus_areas: string[];
  equipment_available: string[];
  age_group: string;
  created_date: string;
  gpa?: number;
  gpa_scale?: string;
  act_score?: number;
  sat_score?: number;
}

export interface DrillInSession {
  drill_id: string;
  drill_name: string;
  category: string;
  description: string;
  duration_minutes: number;
  allocated_time: number;
  block_type: string;
  intensity: string;
  difficulty: string;
  equipment: string;
  coaching_cues: string;
  coaching_points: string;
  video_url: string;
  presenter_id: string;
  solo_possible: boolean;
}

export interface TrainingSession {
  day_number: number;
  name: string;
  duration_minutes: number;
  drills: DrillInSession[];
  completed: boolean;
  completed_date: string | null;
}

export interface TrainingWeek {
  week_number: number;
  generated_date: string;
  archived_date?: string;
  sessions: TrainingSession[];
}

export interface WeeklyTrainingPlan {
  current_week_number: number;
  generated_date: string;
  weeks: TrainingWeek[];
}

export interface RRSPillars {
  consistency: number;
  volume: number;
  coverage: number;
  progression: number;
}

export interface RRSSnapshot {
  date: string;
  overall: number;
  pillars: RRSPillars;
}

export interface RRSHistory {
  snapshots: RRSSnapshot[];
}

export interface CompletionEntry {
  session_id: string;
  timestamp: string;
  date: string;
  week: number;
  day: number;
  drills_completed: string[];
  duration_minutes: number;
  difficulty: string;
  focus_areas: string[];
}

export interface CompletionLog {
  completions: CompletionEntry[];
}

export interface Drill {
  drill_id: string;
  drill_name: string;
  category: string;
  description: string;
  players_min: number;
  players_max: number;
  duration_minutes: number;
  field_type: string;
  setup_data: string;
  equipment: string;
  coaching_points: string;
  difficulty: string;
  intensity: string;
  tags: string;
  diagram_url: string;
  position_relevance: string;
  skill_category: string;
  solo_possible: boolean;
  min_equipment: string;
  game_application: string;
  video_url: string;
  coaching_cues: string;
  drill_type: string;
  series_name: string;
  series_order: number;
  rrs_benchmark: string;
  space_required: string;
  position_primary: string;
  presenter_id: string;
  status: string;
  video_status: string;
  beta_ready: boolean;
  slug: string;
  common_mistakes: string;
}

export interface DrillCompletion {
  drill_id: string;
  drill_name: string;
  completed_at: string;
  date: string;
}

export interface DrillCompletionLog {
  completions: DrillCompletion[];
}
