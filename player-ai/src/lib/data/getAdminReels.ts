import { createServerClient } from '@/lib/supabase/server';
import type { ReelSubmission } from '@/lib/types/reel';

export async function getAllSubmittedReels(reviewerId?: string): Promise<ReelSubmission[]> {
  try {
    const supabase = await createServerClient();
    let query = supabase
      .from('reel_submissions')
      .select('*')
      .eq('submit_for_review', true)
      .order('review_status', { ascending: true })
      .order('uploaded_at', { ascending: false });

    if (reviewerId) {
      query = query.eq('reviewer_id', reviewerId);
    }

    const { data, error } = await query;
    if (error || !data) return [];
    return data as ReelSubmission[];
  } catch {
    return [];
  }
}
