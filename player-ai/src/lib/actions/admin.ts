'use server';

import { revalidatePath, revalidateTag } from 'next/cache';
import { createServerClient } from '@/lib/supabase/server';
import { getAdminSession, setAdminSession, clearAdminSession } from '@/lib/admin';
import { checkRateLimit } from '@/lib/rate-limit';
import { log } from '@/lib/logger';
import { sendReelReviewNotificationEmail } from '@/lib/email/resend';
import { PRESENTER_MAP } from '@/lib/data/presenters';
import type { Drill } from '@/lib/types/player';
import type { FeedPost } from '@/lib/types/feed';

const FEED_SYSTEM_USER = '_feed';
const FEED_DATA_KEY    = 'posts';

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

export async function submitReviewResponseAction(
  reelId: string,
  response: string
): Promise<{ success: boolean; error?: string }> {
  try {
    const isAdmin = await getAdminSession();
    if (!isAdmin) return { success: false, error: 'Unauthorized.' };

    if (!response || response.trim().length < 5) {
      return { success: false, error: 'Response must be at least 5 characters.' };
    }
    if (response.length > 5000) {
      return { success: false, error: 'Response must be under 5000 characters.' };
    }

    const supabase = await createServerClient();
    const { error } = await supabase
      .from('reel_submissions')
      .update({
        reviewer_response: response.trim(),
        review_status: 'reviewed',
        reviewed_at: new Date().toISOString(),
      })
      .eq('id', reelId)
      .eq('review_status', 'pending');

    if (error) return { success: false, error: error.message };

    revalidatePath('/admin/reels');
    revalidatePath('/reel');

    // Send notification email to player — non-fatal
    try {
      const { data: reel } = await supabase
        .from('reel_submissions')
        .select('username, title, reviewer_id')
        .eq('id', reelId)
        .single();

      if (reel) {
        const { data: user } = await supabase
          .from('users')
          .select('email')
          .eq('username', reel.username)
          .maybeSingle();

        if (user?.email) {
          const reviewer = PRESENTER_MAP[reel.reviewer_id];
          await sendReelReviewNotificationEmail({
            email: user.email,
            playerName: reel.username,
            reelTitle: reel.title,
            reviewerName: reviewer?.name ?? reel.reviewer_id,
            response: response.trim(),
          });
        }
      }
    } catch {
      // email failure never blocks the review submission
    }

    return { success: true };
  } catch (err: any) {
    return { success: false, error: err.message || 'Failed to submit review.' };
  }
}

// ── Feed post management ─────────────────────────────────────────────────────

async function getFeedPostsRaw(supabase: Awaited<ReturnType<typeof createServerClient>>): Promise<FeedPost[]> {
  const { data } = await supabase
    .from('user_data')
    .select('value')
    .eq('username', FEED_SYSTEM_USER)
    .eq('data_key', FEED_DATA_KEY)
    .maybeSingle();
  return (data?.value as FeedPost[]) ?? [];
}

async function saveFeedPosts(
  supabase: Awaited<ReturnType<typeof createServerClient>>,
  posts: FeedPost[]
): Promise<void> {
  await supabase
    .from('user_data')
    .upsert(
      { username: FEED_SYSTEM_USER, data_key: FEED_DATA_KEY, value: posts },
      { onConflict: 'username,data_key' }
    );
}

export async function createFeedPostAction(
  post: Omit<FeedPost, 'post_id' | 'date_posted'>
): Promise<{ success: boolean; error?: string }> {
  try {
    const isAdmin = await getAdminSession();
    if (!isAdmin) return { success: false, error: 'Unauthorized.' };

    if (!post.title?.trim() || !post.description?.trim()) {
      return { success: false, error: 'Title and description are required.' };
    }

    const supabase = await createServerClient();
    const existing = await getFeedPostsRaw(supabase);

    const newPost: FeedPost = {
      ...post,
      post_id: `DYN_${Date.now()}`,
      date_posted: new Date().toISOString().split('T')[0],
      title: post.title.trim(),
      description: post.description.trim(),
      body: post.body?.trim() || '',
      video_url: post.video_url?.trim() || '',
      tags: post.tags?.trim() || '',
      position_tags: post.position_tags?.trim() || '',
    };

    await saveFeedPosts(supabase, [newPost, ...existing]);
    revalidatePath('/feed');
    revalidatePath('/admin/feed');
    return { success: true };
  } catch (err: any) {
    return { success: false, error: err.message || 'Failed to create post.' };
  }
}

export async function deleteFeedPostAction(
  postId: string
): Promise<{ success: boolean; error?: string }> {
  try {
    const isAdmin = await getAdminSession();
    if (!isAdmin) return { success: false, error: 'Unauthorized.' };

    const supabase = await createServerClient();
    const existing = await getFeedPostsRaw(supabase);
    await saveFeedPosts(supabase, existing.filter(p => p.post_id !== postId));
    revalidatePath('/feed');
    revalidatePath('/admin/feed');
    return { success: true };
  } catch (err: any) {
    return { success: false, error: err.message || 'Failed to delete post.' };
  }
}

export async function getDynamicFeedPosts(): Promise<FeedPost[]> {
  try {
    const supabase = await createServerClient();
    return await getFeedPostsRaw(supabase);
  } catch {
    return [];
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
