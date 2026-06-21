'use server';

import { revalidatePath, revalidateTag } from 'next/cache';
import { createServerClient } from '@/lib/supabase/server';
import { getAdminSession, setAdminSession, clearAdminSession } from '@/lib/admin';
import { checkRateLimit } from '@/lib/rate-limit';
import { log } from '@/lib/logger';
import type { Drill } from '@/lib/types/player';

// 5 attempts per 15 minutes — single shared key since there is only one admin
const ADMIN_LOGIN_RATE_LIMIT = { limit: 5, windowMs: 15 * 60 * 1000 };

function getAdminPassword(): string {
  const pwd = process.env.ADMIN_PASSWORD;
  if (!pwd) throw new Error('ADMIN_PASSWORD environment variable is not set.');
  return pwd;
}

export async function adminLoginAction(
  password: string
): Promise<{ success: boolean; error?: string }> {
  if (!checkRateLimit('admin-login', ADMIN_LOGIN_RATE_LIMIT)) {
    log.adminLoginRateLimited();
    return { success: false, error: 'Too many login attempts. Please wait 15 minutes.' };
  }

  let adminPassword: string;
  try {
    adminPassword = getAdminPassword();
  } catch {
    return { success: false, error: 'Admin access is not configured.' };
  }
  if (password === adminPassword) {
    await setAdminSession();
    log.adminLoginSuccess();
    return { success: true };
  }
  log.adminLoginFailure();
  return { success: false, error: 'Invalid password.' };
}

export async function adminLogoutAction(): Promise<void> {
  await clearAdminSession();
}

// Fields that identify a drill record — must never be changed via an update.
const DRILL_IMMUTABLE_FIELDS = ['drill_id', 'slug'] as const;

export async function updateDrillAction(
  drillId: string,
  updates: Partial<Drill>
): Promise<{ success: boolean; error?: string }> {
  try {
    const isAdmin = await getAdminSession();
    if (!isAdmin) {
      return { success: false, error: 'Unauthorized.' };
    }

    // Strip identity fields so they can never be overwritten through this action.
    const safeUpdates = { ...updates };
    for (const field of DRILL_IMMUTABLE_FIELDS) {
      delete safeUpdates[field];
    }

    if (Object.keys(safeUpdates).length === 0) {
      return { success: false, error: 'No updatable fields provided.' };
    }

    const supabase = await createServerClient();
    const { error } = await supabase
      .from('drills')
      .update(safeUpdates)
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
