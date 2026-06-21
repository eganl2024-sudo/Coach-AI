'use server';

import { revalidatePath } from 'next/cache';
import { createServerClient } from '@/lib/supabase/server';
import { getCurrentUser } from '@/lib/session';
import { getAllDrills } from '@/lib/data/getDrills';
import { generateTrainingPlan } from '@/lib/utils/generateTrainingPlan';
import type {
  AthleteProfile,
  WeeklyTrainingPlan,
  CompletionLog,
  RRSHistory
} from '@/lib/types/player';
import { getUserData } from '@/lib/data/getUserData';

export interface OnboardingFormData {
  name: string;
  age: number;
  email: string;
  gender: 'M' | 'W';
  position: string;
  secondary_position: string;
  preferred_foot: string;
  age_group: string;
  level: string;
  league: string;
  club_name: string;
  grad_year: number;
  game_days: number[];
  target_level: string;
  focus_areas: string[];
  equipment_available: string[];
  sessions_per_week: number;
  session_duration: number;
}

export async function saveOnboardingAction(
  formData: OnboardingFormData
): Promise<{ success: boolean; error?: string }> {
  try {
    // 1. Get current user session
    const username = await getCurrentUser();
    if (!username) {
      return { success: false, error: 'User session not found.' };
    }

    // 2. Guard against re-onboarding an existing user (would wipe training history)
    const existingProfile = await getUserData<AthleteProfile>(username, 'athlete_profile');
    if (existingProfile) {
      return { success: false, error: 'Profile already exists. Use the profile settings page to make changes.' };
    }

    // 3. Validate required fields
    if (!formData.email?.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      return { success: false, error: 'A valid email address is required.' };
    }

    if (formData.sessions_per_week < 1 || formData.sessions_per_week > 7) {
      return { success: false, error: 'Sessions per week must be between 1 and 7.' };
    }
    if (formData.session_duration < 15 || formData.session_duration > 180) {
      return { success: false, error: 'Session duration must be between 15 and 180 minutes.' };
    }
    if (formData.age < 10 || formData.age > 40) {
      return { success: false, error: 'Invalid age.' };
    }

    // Build AthleteProfile object
    const profile: AthleteProfile = {
      name: formData.name,
      age: formData.age,
      email: formData.email || undefined,
      gender: formData.gender,
      preferred_foot: formData.preferred_foot,
      position: formData.position,
      secondary_position: formData.secondary_position,
      level: formData.level,
      league: formData.league || undefined,
      club_name: formData.club_name.trim() || undefined,
      grad_year: formData.grad_year || undefined,
      game_days: formData.game_days.length > 0 ? formData.game_days : undefined,
      target_level: formData.target_level,
      sessions_per_week: formData.sessions_per_week,
      session_duration: formData.session_duration,
      focus_areas: formData.focus_areas,
      equipment_available: formData.equipment_available,
      age_group: formData.age_group,
      created_date: new Date().toISOString(),
    };

    // 3. Fetch all drills
    const drills = await getAllDrills();
    if (!drills || drills.length === 0) {
      return { success: false, error: 'No drills found in the system to generate a plan.' };
    }

    // 4. Generate the training plan
    const plan = generateTrainingPlan(profile, drills, 1);

    // 5. Initialize completion log
    const completionLog: CompletionLog = {
      completions: [],
    };

    // 6. Initialize RRS history
    const rrsHistory: RRSHistory = {
      snapshots: [],
    };

    // 7. Upsert all 4 keys to user_data in parallel
    const supabase = await createServerClient();
    const now = new Date().toISOString();

    const [profileRes, planRes, logRes, historyRes] = await Promise.all([
      supabase.from('user_data').upsert({
        username,
        data_key: 'athlete_profile',
        data_value: JSON.stringify(profile),
        updated_at: now,
      }, { onConflict: 'username,data_key' }),

      supabase.from('user_data').upsert({
        username,
        data_key: 'weekly_training_plan',
        data_value: JSON.stringify(plan),
        updated_at: now,
      }, { onConflict: 'username,data_key' }),

      supabase.from('user_data').upsert({
        username,
        data_key: 'completion_log',
        data_value: JSON.stringify(completionLog),
        updated_at: now,
      }, { onConflict: 'username,data_key' }),

      supabase.from('user_data').upsert({
        username,
        data_key: 'rrs_history',
        data_value: JSON.stringify(rrsHistory),
        updated_at: now,
      }, { onConflict: 'username,data_key' }),
    ]);

    if (profileRes.error) {
      throw new Error(`Failed to save athlete profile: ${profileRes.error.message}`);
    }
    if (planRes.error) {
      throw new Error(`Failed to save training plan: ${planRes.error.message}`);
    }
    if (logRes.error) {
      throw new Error(`Failed to save completion log: ${logRes.error.message}`);
    }
    if (historyRes.error) {
      throw new Error(`Failed to save RRS history: ${historyRes.error.message}`);
    }

    // 8. Revalidate paths to refresh page data
    revalidatePath('/');
    revalidatePath('/training');

    return { success: true };
  } catch (err: any) {
    return {
      success: false,
      error: err.message || 'An unexpected error occurred during onboarding.',
    };
  }
}
