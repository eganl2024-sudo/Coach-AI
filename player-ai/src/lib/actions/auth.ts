'use server';

import { createServerClient } from '@/lib/supabase/server';
import { verifyPassword, generateSalt, hashPassword } from '@/lib/auth';
import { getSession, getCurrentUser } from '@/lib/session';
import { checkRateLimit } from '@/lib/rate-limit';
import { sendPasswordResetEmail } from '@/lib/email/resend';
import { randomBytes } from 'crypto';
import type { UserRow } from '@/lib/types/database';

// 10 attempts per 15 minutes per username
const LOGIN_RATE_LIMIT  = { limit: 10, windowMs: 15 * 60 * 1000 };
// 5 signups per hour (global — stops account farming)
const SIGNUP_RATE_LIMIT = { limit: 5,  windowMs: 60 * 60 * 1000 };
// 3 reset requests per hour per username — stops email flooding
const RESET_RATE_LIMIT  = { limit: 3,  windowMs: 60 * 60 * 1000 };

const RESET_TOKEN_TTL_MS = 60 * 60 * 1000; // 1 hour

export async function loginAction(
  username: string,
  password: string,
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
    const { valid, needsRehash } = await verifyPassword(password, user.salt, user.password_hash);

    if (!valid) {
      return { success: false, error: 'Invalid username or password.' };
    }

    // Transparently upgrade legacy 100K-iteration hashes to 600K on successful login
    if (needsRehash) {
      const newSalt = generateSalt();
      const newHash = await hashPassword(password, newSalt);
      await supabase
        .from('users')
        .update({ password_hash: newHash, salt: newSalt })
        .eq('username', normalizedLogin);
    }

    const session = await getSession();
    session.username = user.username;
    await session.save();

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
  password: string,
  email?: string,
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
      return { success: false, error: 'Password must be at least 8 characters long.' };
    }

    const normalizedEmail = email?.trim().toLowerCase() || null;
    if (normalizedEmail && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalizedEmail)) {
      return { success: false, error: 'Invalid email address.' };
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
        salt,
        email: normalizedEmail,
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

export async function requestPasswordResetAction(
  username: string,
): Promise<{ success: boolean; error?: string }> {
  const normalizedUsername = username.trim().toLowerCase();

  if (!checkRateLimit(`reset:${normalizedUsername}`, RESET_RATE_LIMIT)) {
    // Return success to avoid revealing whether the account exists
    return { success: true };
  }

  try {
    const supabase = await createServerClient();

    const { data: user } = await supabase
      .from('users')
      .select('username, email')
      .eq('username', normalizedUsername)
      .maybeSingle();

    // Always return success — never confirm whether username exists
    if (!user || !user.email) return { success: true };

    // Block password reset for social accounts
    const { data: userData } = await supabase
      .from('users')
      .select('password_hash')
      .eq('username', normalizedUsername)
      .single();

    if (userData?.password_hash?.startsWith('SOCIAL_GOOGLE_')) return { success: true };

    const token = randomBytes(32).toString('hex');
    const expiresAt = new Date(Date.now() + RESET_TOKEN_TTL_MS).toISOString();

    await supabase
      .from('users')
      .update({ reset_token: token, reset_token_expires_at: expiresAt })
      .eq('username', normalizedUsername);

    await sendPasswordResetEmail({ email: user.email, username: normalizedUsername, token });

    return { success: true };
  } catch {
    return { success: false, error: 'An unexpected error occurred. Please try again.' };
  }
}

export async function confirmPasswordResetAction(
  token: string,
  newPassword: string,
): Promise<{ success: boolean; error?: string }> {
  if (!token || token.length !== 64 || !/^[a-f0-9]+$/.test(token)) {
    return { success: false, error: 'Invalid or expired reset link.' };
  }

  if (!newPassword || newPassword.length < 8) {
    return { success: false, error: 'Password must be at least 8 characters.' };
  }

  try {
    const supabase = await createServerClient();

    const { data: user } = await supabase
      .from('users')
      .select('username, reset_token, reset_token_expires_at')
      .eq('reset_token', token)
      .maybeSingle();

    if (!user || !user.reset_token_expires_at) {
      return { success: false, error: 'Invalid or expired reset link.' };
    }

    if (new Date(user.reset_token_expires_at) < new Date()) {
      // Clear the expired token
      await supabase
        .from('users')
        .update({ reset_token: null, reset_token_expires_at: null })
        .eq('username', user.username);
      return { success: false, error: 'This reset link has expired. Please request a new one.' };
    }

    const newSalt = generateSalt();
    const newHash = await hashPassword(newPassword, newSalt);

    await supabase
      .from('users')
      .update({
        password_hash: newHash,
        salt: newSalt,
        reset_token: null,
        reset_token_expires_at: null,
      })
      .eq('username', user.username);

    return { success: true };
  } catch {
    return { success: false, error: 'An unexpected error occurred. Please try again.' };
  }
}

export async function changePasswordAction(
  currentPassword: string,
  newPassword: string,
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

  const { valid } = await verifyPassword(currentPassword, user.salt, user.password_hash);
  if (!valid) return { success: false, error: 'Current password is incorrect.' };

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
