export interface CoachRecord {
  coach_id: string;
  first_name: string;
  last_name: string;
  title: 'Head Coach' | 'Assistant Coach' | 'Director of Operations';
  email: string | null;
  phone: string | null;
  position_focus: string | null;
  source: string;
  verified_at: string | null;
}

export interface ProgramWithCoaches {
  program_id: string;
  school_name: string;
  conference: string;
  region: string;
  state: string;
  division: string;
  program_url: string | null;
  coaches: CoachRecord[];
  // Computed on transform:
  head_coach: CoachRecord | null;        // first coach with title === 'Head Coach'
  has_email: boolean;                    // any coach has a non-null email
  total_coaches: number;                 // coaches.length
}

export type OutreachStatus =
  | 'emailed'        // sent an email, no response yet
  | 'responded'      // coach replied
  | 'call_scheduled' // call or meeting booked
  | 'visited'        // visited campus / attended ID camp
  | 'not_interested' // coach indicated no interest
  | 'committed';     // verbal or written commitment

export interface OutreachEntry {
  id: string;                          // uuid — client-generated via crypto.randomUUID()
  school_name: string;
  coach_name: string;                  // "First Last"
  coach_title: string;                 // 'Head Coach' | 'Assistant Coach' | 'Director of Operations'
  coach_email: string | null;
  contacted_date: string;              // ISO date string YYYY-MM-DD
  status: OutreachStatus;
  notes: string;                       // free text, player's notes
  follow_up_date: string | null;       // YYYY-MM-DD — optional reminder date
  created_at: string;                  // ISO timestamp
  updated_at: string;                  // ISO timestamp
}

export interface OutreachLog {
  entries: OutreachEntry[];
}
