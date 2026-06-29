'use server'

import { redirect } from 'next/navigation'
import { headers } from 'next/headers'
import { createServerClient } from '../supabase/server'
import { hashPassword, verifyPassword } from '../auth'
import { getSession } from '../session'
import { sendConsentEmail } from '../email/consent'

// In-memory rate limiting — persists for the lifetime of the server process.
// ponytail: per-IP map, not per-account. Fine at beta scale; swap for Redis if multi-instance.
const loginAttempts = new Map<string, { count: number; resetAt: number }>()
const MAX_ATTEMPTS = 6
const WINDOW_MS = 5 * 60 * 1000
const LOCKOUT_MS = 15 * 60 * 1000

function isRateLimited(key: string): boolean {
  const now = Date.now()
  const entry = loginAttempts.get(key)
  if (!entry || now > entry.resetAt) return false
  return entry.count >= MAX_ATTEMPTS
}

function recordFailedLogin(key: string) {
  const now = Date.now()
  const entry = loginAttempts.get(key)
  if (!entry || now > entry.resetAt) {
    loginAttempts.set(key, { count: 1, resetAt: now + WINDOW_MS })
  } else {
    entry.count++
    if (entry.count >= MAX_ATTEMPTS) entry.resetAt = now + LOCKOUT_MS
  }
}

export async function signupAction(formData: FormData) {
  const username = (formData.get('username') as string)?.trim().toLowerCase()
  const email = (formData.get('email') as string)?.trim().toLowerCase()
  const password = formData.get('password') as string
  const confirm = formData.get('confirm') as string
  const honeypot = formData.get('website') as string

  if (honeypot) return { error: 'Invalid submission.' }

  if (!username || username.length < 3 || username.length > 20) {
    return { error: 'Username must be 3–20 characters.' }
  }
  if (!/^[a-z0-9_]+$/.test(username)) {
    return { error: 'Username can only contain letters, numbers, and underscores.' }
  }
  if (!email || !email.includes('@')) {
    return { error: 'Please enter a valid email address.' }
  }
  if (!password || password.length < 8) {
    return { error: 'Password must be at least 8 characters.' }
  }
  if (password !== confirm) {
    return { error: 'Passwords do not match.' }
  }

  const supabase = await createServerClient()

  const { data: existing } = await supabase
    .from('h2s_parents')
    .select('id')
    .or(`username.eq.${username},email.eq.${email}`)
    .maybeSingle()

  if (existing) {
    return { error: 'That username or email is already taken.' }
  }

  const password_hash = await hashPassword(password)

  // COPPA: generate 24h consent token; account activated only after email click.
  const consent_token = crypto.randomUUID()
  const consent_token_exp = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()

  const { data: parent, error } = await supabase
    .from('h2s_parents')
    .insert({ username, email, password_hash, consent_token, consent_token_exp })
    .select('id, username')
    .single()

  if (error || !parent) {
    return { error: 'Could not create account. Please try again.' }
  }

  // Fire and forget — if email fails, the user can contact support.
  // Requires RESEND_API_KEY in env and the migration 20260629_coppa_consent.sql to be run.
  sendConsentEmail(email, consent_token).catch(() => null)

  redirect('/signup/check-email')
}

export async function loginAction(formData: FormData) {
  const username = (formData.get('username') as string)?.trim().toLowerCase()
  const password = formData.get('password') as string

  if (!username || !password) {
    return { error: 'Please fill in all fields.' }
  }

  const hdrs = await headers()
  const ip = hdrs.get('x-forwarded-for')?.split(',')[0]?.trim() ?? 'unknown'
  const rateKey = `login:${ip}`

  if (isRateLimited(rateKey)) {
    return { error: 'Too many login attempts. Please try again in 15 minutes.' }
  }

  const supabase = await createServerClient()

  const { data: parent } = await supabase
    .from('h2s_parents')
    .select('id, username, password_hash')
    .eq('username', username)
    .maybeSingle()

  if (!parent) {
    recordFailedLogin(rateKey)
    return { error: 'Username or password is incorrect.' }
  }

  const valid = await verifyPassword(password, parent.password_hash)
  if (!valid) {
    recordFailedLogin(rateKey)
    return { error: 'Username or password is incorrect.' }
  }

  loginAttempts.delete(rateKey)

  const { data: kid } = await supabase
    .from('h2s_kids')
    .select('id, name')
    .eq('parent_id', parent.id)
    .order('created_at', { ascending: false })
    .limit(1)
    .maybeSingle()

  const session = await getSession()
  session.parentId = parent.id
  session.parentUsername = parent.username
  if (kid) {
    session.kidId = kid.id
    session.kidName = kid.name
  }
  await session.save()

  redirect(kid ? '/' : '/onboarding')
}

export async function logoutAction() {
  const session = await getSession()
  session.destroy()
  redirect('/login')
}

function isValidTimezone(tz: string): boolean {
  try { Intl.DateTimeFormat(undefined, { timeZone: tz }); return true } catch { return false }
}

export async function addKidAction(formData: FormData) {
  const session = await getSession()
  if (!session.parentId) redirect('/login')

  // COPPA gate: parent must have confirmed email before any child data is stored.
  const supabaseCheck = await createServerClient()
  const { data: parentRow } = await supabaseCheck
    .from('h2s_parents')
    .select('consent_given_at')
    .eq('id', session.parentId)
    .maybeSingle()
  if (!parentRow?.consent_given_at) {
    return { error: 'Please confirm your email address before adding a player.' }
  }

  const name = (formData.get('name') as string)?.trim()
  const age = parseInt(formData.get('age') as string, 10)
  const skill_level = formData.get('skill_level') as string
  const rawTz = (formData.get('timezone') as string)?.trim()
  const timezone = rawTz && isValidTimezone(rawTz) ? rawTz : 'America/New_York'

  if (!name || name.length < 1) return { error: 'Please enter your player\'s name.' }
  if (!age || age < 4 || age > 13) return { error: 'Age must be between 4 and 13.' }
  if (!['beginner', 'intermediate', 'advanced'].includes(skill_level)) {
    return { error: 'Please select a skill level.' }
  }

  const supabase = supabaseCheck  // reuse the client from the consent check

  const { data: kid, error } = await supabase
    .from('h2s_kids')
    .insert({ parent_id: session.parentId, name, age, skill_level })
    .select('id, name')
    .single()

  if (error || !kid) {
    return { error: 'Could not save player profile. Please try again.' }
  }

  // Seed initial streak with browser-detected timezone so first-practice streak
  // uses the correct local date. Without this, defaults to America/New_York.
  await supabase.from('h2s_streaks').insert({
    kid_id: kid.id,
    current_streak: 0,
    longest_streak: 0,
    last_practice_date: null,
    timezone,
    updated_at: new Date().toISOString(),
  })

  session.kidId = kid.id
  session.kidName = kid.name
  await session.save()

  redirect('/')
}
