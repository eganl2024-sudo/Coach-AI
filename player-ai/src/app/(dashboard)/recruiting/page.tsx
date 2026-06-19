import { getCurrentUser } from '@/lib/session';
import { getUserData } from '@/lib/data/getUserData';
import { createServerClient } from '@/lib/supabase/server';
import type { AthleteProfile } from '@/lib/types/player';
import type { ProgramWithCoaches, OutreachLog } from '@/lib/types/recruiting';
import { redirect } from 'next/navigation';
import RecruitingComingSoon from '@/components/recruiting/RecruitingComingSoon';

export const metadata = { title: 'Recruiting Hub' };

export default async function RecruitingPage() {
  const username = await getCurrentUser();
  if (!username) redirect('/login');

  const profile = await getUserData<AthleteProfile>(username, 'athlete_profile');
  const gender = profile?.gender ?? 'M';

  const [coachData, outreachLog] = await Promise.all([
    fetchPrograms(gender),
    getUserData<OutreachLog>(username, 'outreach_log'),
  ]);

  return (
    <RecruitingComingSoon
      profile={profile}
      programs={coachData}
      outreachLog={outreachLog ?? { entries: [] }}
    />
  );
}

async function fetchPrograms(gender: 'M' | 'W'): Promise<ProgramWithCoaches[]> {
  try {
    const supabase = await createServerClient();
    const { data, error } = await supabase
      .from('v_coaches_with_program')
      .select('*')
      .eq('gender', gender)
      .order('school_name', { ascending: true });

    if (error || !data) return [];

    // Group flat rows by program_id
    const programMap = new Map<string, ProgramWithCoaches>();

    for (const row of data) {
      if (!programMap.has(row.program_id)) {
        programMap.set(row.program_id, {
          program_id: row.program_id,
          school_name: row.school_name,
          conference: row.conference,
          region: row.region,
          state: row.state,
          division: row.division,
          program_url: row.program_url,
          coaches: [],
          head_coach: null,
          has_email: false,
          total_coaches: 0,
        });
      }

      const program = programMap.get(row.program_id)!;

      const coach = {
        coach_id: row.coach_id,
        first_name: row.first_name,
        last_name: row.last_name,
        title: row.title,
        email: row.email,
        phone: row.phone,
        position_focus: row.position_focus,
        source: row.source,
        verified_at: row.verified_at,
      };

      program.coaches.push(coach);
      if (!program.head_coach && coach.title === 'Head Coach') {
        program.head_coach = coach;
      }
      if (coach.email) program.has_email = true;
    }

    return Array.from(programMap.values()).map(p => ({
      ...p,
      total_coaches: p.coaches.length,
    }));
  } catch {
    return [];
  }
}
