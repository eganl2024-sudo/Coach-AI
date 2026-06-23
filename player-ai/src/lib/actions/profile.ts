'use server';

import { revalidatePath } from 'next/cache';
import { createServerClient } from '@/lib/supabase/server';
import { getCurrentUser } from '@/lib/session';

const AVATAR_MAX_BYTES = 150_000; // 150KB limit on server

export async function saveAvatarAction(
  dataUrl: string
): Promise<{ success: boolean; error?: string }> {
  try {
    const username = await getCurrentUser();
    if (!username) return { success: false, error: 'Not authenticated.' };

    if (!dataUrl.startsWith('data:image/jpeg;base64,') && !dataUrl.startsWith('data:image/png;base64,') && !dataUrl.startsWith('data:image/webp;base64,')) {
      return { success: false, error: 'Invalid image format.' };
    }

    const base64 = dataUrl.split(',')[1] ?? '';
    const byteLength = Math.ceil(base64.length * 0.75);
    if (byteLength > AVATAR_MAX_BYTES) {
      return { success: false, error: 'Image too large. Please use a smaller photo.' };
    }

    const supabase = await createServerClient();
    const { error } = await supabase
      .from('user_data')
      .upsert(
        { username, data_key: 'avatar', data_value: JSON.stringify({ dataUrl }) },
        { onConflict: 'username,data_key' }
      );

    if (error) return { success: false, error: error.message };

    revalidatePath('/profile');
    revalidatePath('/');
    return { success: true };
  } catch (err: any) {
    return { success: false, error: err.message || 'Failed to save avatar.' };
  }
}

export async function removeAvatarAction(): Promise<{ success: boolean; error?: string }> {
  try {
    const username = await getCurrentUser();
    if (!username) return { success: false, error: 'Not authenticated.' };

    const supabase = await createServerClient();
    await supabase
      .from('user_data')
      .delete()
      .eq('username', username)
      .eq('data_key', 'avatar');

    revalidatePath('/profile');
    revalidatePath('/');
    return { success: true };
  } catch (err: any) {
    return { success: false, error: err.message || 'Failed to remove avatar.' };
  }
}
