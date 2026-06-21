'use server';

import { revalidatePath } from 'next/cache';
import { createServerClient } from '@/lib/supabase/server';
import { getCurrentUser } from '@/lib/session';
import { checkRateLimit } from '@/lib/rate-limit';
import { log } from '@/lib/logger';
import type { ReelSubmission } from '@/lib/types/reel';

// 5 uploads per hour per user — prevents storage quota exhaustion
const REEL_UPLOAD_RATE_LIMIT = { limit: 5, windowMs: 60 * 60 * 1000 };
// 10 review submissions per hour per user
const REEL_SUBMIT_RATE_LIMIT = { limit: 10, windowMs: 60 * 60 * 1000 };

export async function uploadReelAction(
  formData: FormData
): Promise<{ success: boolean; error?: string; id?: string }> {
  try {
    const username = await getCurrentUser();
    if (!username) {
      return { success: false, error: 'Unauthorized: No user session found.' };
    }

    if (!checkRateLimit(`reel-upload:${username}`, REEL_UPLOAD_RATE_LIMIT)) {
      log.reelUploadRateLimited(username);
      return { success: false, error: 'Upload limit reached. You can upload up to 5 clips per hour.' };
    }

    const file = formData.get('file') as File | null;
    const title = formData.get('title') as string | null;
    const notes = formData.get('notes') as string | null;

    if (!file || !(file instanceof File) || file.size === 0) {
      return { success: false, error: 'Video file is required.' };
    }

    const acceptedTypes = ['video/mp4', 'video/mov', 'video/quicktime', 'video/webm'];
    if (!acceptedTypes.includes(file.type)) {
      return { success: false, error: 'Invalid file format. Accepted formats: MP4, MOV, WebM.' };
    }

    if (file.size > 52428800) {
      return { success: false, error: 'File size exceeds the 50MB limit.' };
    }

    if (!title || title.trim().length < 3) {
      return { success: false, error: 'Title must be at least 3 characters long.' };
    }

    const sanitizedFilename = file.name.replace(/[^a-zA-Z0-9._-]/g, '_');
    const storagePath = `${username}/${Date.now()}_${sanitizedFilename}`;

    const supabase = await createServerClient();

    const { error: uploadError } = await supabase.storage
      .from('Clip Uploader')
      .upload(storagePath, file, {
        contentType: file.type,
        upsert: false,
      });

    if (uploadError) {
      return { success: false, error: uploadError.message };
    }

    const { data: insertedRow, error: insertError } = await supabase
      .from('reel_submissions')
      .insert({
        username,
        clip_path: storagePath,
        clip_name: file.name,
        title: title.trim(),
        notes: notes?.trim() || '',
        duration_seconds: 0,
        uploaded_at: new Date().toISOString(),
        submit_for_review: false,
        reviewer_id: '',
        review_question: '',
        review_status: 'not_submitted',
        reviewer_response: '',
      })
      .select()
      .single();

    if (insertError || !insertedRow) {
      // Clean up uploaded file if DB insert fails
      await supabase.storage.from('Clip Uploader').remove([storagePath]);
      return { success: false, error: insertError?.message || 'Database insertion failed.' };
    }

    revalidatePath('/reel');
    return { success: true, id: insertedRow.id };
  } catch (err: any) {
    return { success: false, error: err.message || 'An unexpected error occurred during upload.' };
  }
}

const VALID_REVIEWER_IDS = new Set(['KC-01', 'UNLV-01', 'TFC-01', 'YOU-01']);

export async function submitForReviewAction(
  reelId: string,
  reviewerId: string,
  question: string
): Promise<{ success: boolean; error?: string }> {
  try {
    const username = await getCurrentUser();
    if (!username) {
      return { success: false, error: 'Unauthorized: No user session found.' };
    }

    if (!checkRateLimit(`reel-submit:${username}`, REEL_SUBMIT_RATE_LIMIT)) {
      log.reelSubmitRateLimited(username);
      return { success: false, error: 'Too many review submissions. Please try again later.' };
    }

    if (!VALID_REVIEWER_IDS.has(reviewerId)) {
      return { success: false, error: 'Invalid reviewer selection.' };
    }

    if (!question || question.trim().length < 10) {
      return { success: false, error: 'Please provide a question of at least 10 characters.' };
    }

    if (question.length > 1000) {
      return { success: false, error: 'Question must be under 1000 characters.' };
    }

    const supabase = await createServerClient();
    const { error } = await supabase
      .from('reel_submissions')
      .update({
        submit_for_review: true,
        reviewer_id: reviewerId,
        review_question: question.trim(),
        review_status: 'pending',
      })
      .eq('id', reelId)
      .eq('username', username);

    if (error) {
      return { success: false, error: error.message };
    }

    revalidatePath('/reel');
    return { success: true };
  } catch (err: any) {
    return { success: false, error: err.message || 'An unexpected error occurred during submission.' };
  }
}

export async function deleteReelAction(
  reelId: string,
): Promise<{ success: boolean; error?: string }> {
  try {
    const username = await getCurrentUser();
    if (!username) {
      return { success: false, error: 'Unauthorized: No user session found.' };
    }

    const supabase = await createServerClient();

    // Fetch the row first so we use the server-side clip_path, not a client-supplied value.
    // The username filter ensures we can only fetch (and therefore delete) our own reels.
    const { data: reel, error: fetchError } = await supabase
      .from('reel_submissions')
      .select('clip_path')
      .eq('id', reelId)
      .eq('username', username)
      .single();

    if (fetchError || !reel) {
      return { success: false, error: 'Reel not found or access denied.' };
    }

    // Delete from storage using the server-fetched path
    await supabase.storage
      .from('Clip Uploader')
      .remove([reel.clip_path]);

    // Delete the DB row
    const { error: dbError } = await supabase
      .from('reel_submissions')
      .delete()
      .eq('id', reelId)
      .eq('username', username);

    if (dbError) {
      return { success: false, error: dbError.message };
    }

    revalidatePath('/reel');
    return { success: true };
  } catch (err: any) {
    return { success: false, error: err.message || 'An unexpected error occurred during deletion.' };
  }
}
