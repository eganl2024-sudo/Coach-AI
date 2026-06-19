'use server';

import { revalidatePath } from 'next/cache';
import { createServerClient } from '@/lib/supabase/server';
import { getCurrentUser } from '@/lib/session';
import type { ReelSubmission } from '@/lib/types/reel';

export async function uploadReelAction(
  formData: FormData
): Promise<{ success: boolean; error?: string; id?: string }> {
  try {
    const username = await getCurrentUser();
    if (!username) {
      return { success: false, error: 'Unauthorized: No user session found.' };
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

    const supabase = await createServerClient();
    const { error } = await supabase
      .from('reel_submissions')
      .update({
        submit_for_review: true,
        reviewer_id: reviewerId,
        review_question: question,
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
  clipPath: string
): Promise<{ success: boolean; error?: string }> {
  try {
    const username = await getCurrentUser();
    if (!username) {
      return { success: false, error: 'Unauthorized: No user session found.' };
    }

    const supabase = await createServerClient();

    // Delete from storage
    const { error: storageError } = await supabase.storage
      .from('Clip Uploader')
      .remove([clipPath]);

    // Delete from reel_submissions
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
