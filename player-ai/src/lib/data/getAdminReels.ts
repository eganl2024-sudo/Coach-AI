import { createServerClient } from '@/lib/supabase/server';
import type { ReelSubmission } from '@/lib/types/reel';

export async function getAllSubmittedReels(): Promise<ReelSubmission[]> {
  try {
    const supabase = await createServerClient();
    const { data, error } = await supabase
      .from('reel_submissions')
      .select('*')
      .eq('submit_for_review', true)
      .order('review_status', { ascending: true })   // pending before reviewed
      .order('uploaded_at', { ascending: false });

    if (error || !data) return [];
    return data as ReelSubmission[];
  } catch {
    return [];
  }
}
