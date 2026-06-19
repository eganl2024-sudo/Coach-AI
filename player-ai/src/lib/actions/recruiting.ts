'use server';

import { revalidatePath } from 'next/cache';
import { createServerClient } from '@/lib/supabase/server';
import { getCurrentUser } from '@/lib/session';
import { getUserData } from '@/lib/data/getUserData';
import type { OutreachLog, OutreachEntry } from '@/lib/types/recruiting';

export async function saveOutreachEntryAction(
  entry: OutreachEntry
): Promise<{ success: boolean; error?: string }> {
  try {
    const username = await getCurrentUser();
    if (!username) return { success: false, error: 'Not authenticated.' };

    const existing = await getUserData<OutreachLog>(username, 'outreach_log');
    const entries = existing?.entries ?? [];

    // Upsert by id — replace if exists, append if new
    const idx = entries.findIndex(e => e.id === entry.id);
    if (idx !== -1) {
      entries[idx] = { ...entry, updated_at: new Date().toISOString() };
    } else {
      entries.push(entry);
    }

    const supabase = await createServerClient();
    const { error } = await supabase.from('user_data').upsert({
      username,
      data_key: 'outreach_log',
      data_value: JSON.stringify({ entries }),
      updated_at: new Date().toISOString(),
    }, { onConflict: 'username,data_key' });

    if (error) throw new Error(error.message);

    revalidatePath('/recruiting');
    return { success: true };
  } catch (err: any) {
    return { success: false, error: err.message };
  }
}

export async function deleteOutreachEntryAction(
  entryId: string
): Promise<{ success: boolean; error?: string }> {
  try {
    const username = await getCurrentUser();
    if (!username) return { success: false, error: 'Not authenticated.' };

    const existing = await getUserData<OutreachLog>(username, 'outreach_log');
    if (!existing) return { success: true };

    const entries = existing.entries.filter(e => e.id !== entryId);

    const supabase = await createServerClient();
    const { error } = await supabase.from('user_data').upsert({
      username,
      data_key: 'outreach_log',
      data_value: JSON.stringify({ entries }),
      updated_at: new Date().toISOString(),
    }, { onConflict: 'username,data_key' });

    if (error) throw new Error(error.message);

    revalidatePath('/recruiting');
    return { success: true };
  } catch (err: any) {
    return { success: false, error: err.message };
  }
}
