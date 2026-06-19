import { createServerClient } from '@/lib/supabase/server';
import type { ReelSubmission } from '@/lib/types/reel';

export async function getUserReels(username: string): Promise<ReelSubmission[]> {
  try {
    const supabase = await createServerClient();
    const { data, error } = await supabase
      .from('reel_submissions')
      .select('*')
      .eq('username', username)
      .order('uploaded_at', { ascending: false });

    if (error || !data) return [];
    return data as ReelSubmission[];
  } catch {
    return [];
  }
}

export async function getSignedUrl(clipPath: string): Promise<string | null> {
  try {
    const supabase = await createServerClient();
    const { data, error } = await supabase.storage
      .from('Clip Uploader')
      .createSignedUrl(clipPath, 3600);

    if (error || !data) return null;
    return data.signedUrl;
  } catch {
    return null;
  }
}
