'use server';

import { createServerClient } from '@/lib/supabase/server';
import { verifyPassword, generateSalt, hashPassword } from '@/lib/auth';
import { getSession, getCurrentUser } from '@/lib/session';
import { checkRateLimit } from '@/lib/rate-limit';
import type { UserRow } from '@/lib/types/database';

// 10 attempts per 15 minutes per username — brute force protection
const LOGIN_RATE_LIMIT    = { limit: 10, windowMs: 15 * 60 * 1000 };
// 5 signups per hour per origin — stops account farming
const SIGNUP_RATE_LIMIT   = { limit: 5,  windowMs: 60 * 60 * 1000 };

export async function loginAction(
  username: string,
  password: string
): Promise<{ success: boolean; error?: string }> {
  if (!process.env.NEXT_PUBLIC_SUPABASE_URL ||
      process.env.NEXT_PUBLIC_SUPABASE_URL === 'your_supabase_url_here') {
    return { success: false, error: 'Supabase credentials not configured. Fill in .env.local.' };
  }

  const normalizedLogin = username.trim().toLowerCase();
  if (!checkRateLimit(`login:${normalizedLogin}`, LOGIN_RATE_LIMIT)) {
    return { success: false, error: 'Too many login attempts. Please wait 15 minutes and try again.' };
  }

  try {
    const supabase = await createServerClient();
    const { data, error } = await supabase
      .from('users')
      .select('*')
      .eq('username', normalizedLogin)
      .single();

    if (error || !data) {
      return { success: false, error: 'Invalid username or password.' };
    }

    const user = data as UserRow;
    const valid = await verifyPassword(password, user.salt, user.password_hash);

    if (!valid) {
      return { success: false, error: 'Invalid username or password.' };
    }

    const session = await getSession();
    session.username = user.username;
    await session.save();
    // Clear login rate limit on success so legitimate users aren't penalized


    return { success: true };
  } catch {
    return { success: false, error: 'An unexpected error occurred. Please try again.' };
  }
}

export async function logoutAction(): Promise<void> {
  const session = await getSession();
  await session.destroy();
}

export async function signupAction(
  username: string,
  password: string
): Promise<{ success: boolean; error?: string }> {
  if (!process.env.NEXT_PUBLIC_SUPABASE_URL ||
      process.env.NEXT_PUBLIC_SUPABASE_URL === 'your_supabase_url_here') {
    return { success: false, error: 'Supabase credentials not configured. Fill in .env.local.' };
  }

  if (!checkRateLimit('signup:global', SIGNUP_RATE_LIMIT)) {
    return { success: false, error: 'Too many accounts created recently. Please try again later.' };
  }

  try {
    const normalizedUsername = username.trim().toLowerCase();
    const usernameRegex = /^[a-z0-9_]{3,20}$/;

    if (!usernameRegex.test(normalizedUsername)) {
      return {
        success: false,
        error: 'Username must be 3–20 characters and contain only letters, numbers, and underscores.',
      };
    }

    const RESERVED_USERNAMES = ['demo', 'admin', 'player_ai'];
    if (RESERVED_USERNAMES.includes(normalizedUsername)) {
      return { success: false, error: 'That username is reserved. Please choose another.' };
    }

    if (normalizedUsername.startsWith('g_')) {
      return {
        success: false,
        error: 'Usernames starting with "g_" are reserved for Google Sign-In.',
      };
    }

    if (!password || password.length < 8) {
      return {
        success: false,
        error: 'Password must be at least 8 characters long.',
      };
    }

    const supabase = await createServerClient();

    const { data: existingUser } = await supabase
      .from('users')
      .select('username')
      .eq('username', normalizedUsername)
      .maybeSingle();

    if (existingUser) {
      return { success: false, error: 'Username already taken.' };
    }

    const salt = generateSalt();
    const hash = await hashPassword(password, salt);

    const { error: insertError } = await supabase
      .from('users')
      .insert({
        username: normalizedUsername,
        password_hash: hash,
        salt: salt,
        created_at: new Date().toISOString(),
      });

    if (insertError) {
      return { success: false, error: 'Failed to create account. Please try again.' };
    }

    const session = await getSession();
    session.username = normalizedUsername;
    await session.save();

    return { success: true };
  } catch {
    return { success: false, error: 'An unexpected error occurred. Please try again.' };
  }
}

export async function changePasswordAction(
  currentPassword: string,
  newPassword: string
): Promise<{ success: boolean; error?: string }> {
  const username = await getCurrentUser();
  if (!username) return { success: false, error: 'Not authenticated.' };

  const supabase = await createServerClient();

  const { data: user, error } = await supabase
    .from('users')
    .select('password_hash, salt')
    .eq('username', username)
    .single();

  if (error || !user) return { success: false, error: 'User not found.' };

  if (!user.salt || user.salt === 'google_oauth' || user.password_hash.startsWith('SOCIAL_GOOGLE_')) {
    return { success: false, error: 'Password changes are not available for Google sign-in accounts.' };
  }

  const isValid = await verifyPassword(currentPassword, user.salt, user.password_hash);
  if (!isValid) return { success: false, error: 'Current password is incorrect.' };

  if (newPassword.length < 8) return { success: false, error: 'New password must be at least 8 characters.' };

  const newSalt = generateSalt();
  const newHash = await hashPassword(newPassword, newSalt);

  const { error: updateError } = await supabase
    .from('users')
    .update({ password_hash: newHash, salt: newSalt })
    .eq('username', username);

  if (updateError) return { success: false, error: 'Failed to update password.' };

  return { success: true };
}

export async function deleteAccountAction(): Promise<{ success: boolean; error?: string }> {
  const username = await getCurrentUser();
  if (!username) return { success: false, error: 'Not authenticated.' };

  if (username === 'demo') {
    return { success: false, error: 'The demo account cannot be deleted.' };
  }

  const supabase = await createServerClient();

  await supabase.from('user_data').delete().eq('username', username);
  await supabase.from('reel_submissions').delete().eq('username', username);

  const { error } = await supabase.from('users').delete().eq('username', username);

  if (error) return { success: false, error: 'Failed to delete account.' };

  const session = await getSession();
  session.destroy();

  return { success: true };
}
