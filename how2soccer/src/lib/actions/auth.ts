'use server'

import { redirect } from 'next/navigation'
import { createServerClient } from '../supabase/server'
import { hashPassword, verifyPassword } from '../auth'
import { getSession } from '../session'

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

  const { data: parent, error } = await supabase
    .from('h2s_parents')
    .insert({ username, email, password_hash })
    .select('id, username')
    .single()

  if (error || !parent) {
    return { error: 'Could not create account. Please try again.' }
  }

  const session = await getSession()
  session.parentId = parent.id
  session.parentUsername = parent.username
  await session.save()

  redirect('/onboarding')
}

export async function loginAction(formData: FormData) {
  const username = (formData.get('username') as string)?.trim().toLowerCase()
  const password = formData.get('password') as string

  if (!username || !password) {
    return { error: 'Please fill in all fields.' }
  }

  const supabase = await createServerClient()

  const { data: parent } = await supabase
    .from('h2s_parents')
    .select('id, username, password_hash')
    .eq('username', username)
    .maybeSingle()

  if (!parent) {
    return { error: 'Username or password is incorrect.' }
  }

  const valid = await verifyPassword(password, parent.password_hash)
  if (!valid) {
    return { error: 'Username or password is incorrect.' }
  }

  const { data: kid } = await supabase
    .from('h2s_kids')
    .select('id, name')
    .eq('parent_id', parent.id)
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

export async function addKidAction(formData: FormData) {
  const session = await getSession()
  if (!session.parentId) redirect('/login')

  const name = (formData.get('name') as string)?.trim()
  const age = parseInt(formData.get('age') as string, 10)
  const skill_level = formData.get('skill_level') as string

  if (!name || name.length < 1) return { error: 'Please enter your player\'s name.' }
  if (!age || age < 4 || age > 13) return { error: 'Age must be between 4 and 13.' }
  if (!['beginner', 'intermediate', 'advanced'].includes(skill_level)) {
    return { error: 'Please select a skill level.' }
  }

  const supabase = await createServerClient()

  const { data: kid, error } = await supabase
    .from('h2s_kids')
    .insert({ parent_id: session.parentId, name, age, skill_level })
    .select('id, name')
    .single()

  if (error || !kid) {
    return { error: 'Could not save player profile. Please try again.' }
  }

  session.kidId = kid.id
  session.kidName = kid.name
  await session.save()

  redirect('/')
}
