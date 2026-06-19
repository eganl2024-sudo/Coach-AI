'use server';

import { revalidatePath, revalidateTag } from 'next/cache';
import { createServerClient } from '@/lib/supabase/server';
import { getAdminSession, setAdminSession, clearAdminSession } from '@/lib/admin';
import type { Drill } from '@/lib/types/player';

const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'AdminPlayerAI2026';

export async function adminLoginAction(
  password: string
): Promise<{ success: boolean; error?: string }> {
  if (password === ADMIN_PASSWORD) {
    await setAdminSession();
    return { success: true };
  }
  return { success: false, error: 'Invalid password.' };
}

export async function adminLogoutAction(): Promise<void> {
  await clearAdminSession();
}

export async function updateDrillAction(
  drillId: string,
  updates: Partial<Drill>
): Promise<{ success: boolean; error?: string }> {
  try {
    const isAdmin = await getAdminSession();
    if (!isAdmin) {
      return { success: false, error: 'Unauthorized.' };
    }

    const supabase = await createServerClient();
    const { error } = await supabase
      .from('drills')
      .update(updates)
      .eq('drill_id', drillId);

    if (error) {
      return { success: false, error: error.message };
    }

    revalidateTag('drills', 'default');
    revalidatePath('/drills');
    revalidatePath(`/drills/${drillId}`);
    revalidatePath('/admin');

    return { success: true };
  } catch (err: any) {
    return { success: false, error: err.message || 'Failed to update drill.' };
  }
}

export async function addDrillAction(
  drill: Partial<Drill>
): Promise<{ success: boolean; error?: string; drill_id?: string }> {
  try {
    const isAdmin = await getAdminSession();
    if (!isAdmin) {
      return { success: false, error: 'Unauthorized.' };
    }

    if (!drill.drill_id || !drill.drill_name) {
      return { success: false, error: 'drill_id and drill_name are required at minimum.' };
    }

    const supabase = await createServerClient();
    const { error } = await supabase
      .from('drills')
      .insert(drill);

    if (error) {
      return { success: false, error: error.message };
    }

    revalidateTag('drills', 'default');
    revalidatePath('/drills');
    revalidatePath('/admin');

    return { success: true, drill_id: drill.drill_id };
  } catch (err: any) {
    return { success: false, error: err.message || 'Failed to add drill.' };
  }
}
