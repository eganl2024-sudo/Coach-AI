'use server'

import { redirect } from 'next/navigation'
import { revalidatePath } from 'next/cache'
import { createServerClient } from '../supabase/server'
import { getSession } from '../session'
import { Kid, Parent } from '../types'
import { VALID_TIMEZONE_VALUES } from '../constants/timezones'

export async function getParentWithKids(parentId: string): Promise<Parent & { kids: Kid[] }> {
  const supabase = await createServerClient()
  const [{ data: parent }, { data: kids }] = await Promise.all([
    supabase.from('h2s_parents').select('id, username, email, created_at').eq('id', parentId).single(),
    supabase.from('h2s_kids').select('*').eq('parent_id', parentId).order('created_at', { ascending: true }),
  ])
  return { ...(parent as Parent), kids: (kids as Kid[]) || [] }
}

export async function switchKidAction(formData: FormData) {
  const session = await getSession()
  if (!session.parentId) redirect('/login')

  const kidId = formData.get('kidId') as string
  const supabase = await createServerClient()

  const { data: kid } = await supabase
    .from('h2s_kids')
    .select('id, name')
    .eq('id', kidId)
    .eq('parent_id', session.parentId)
    .maybeSingle()

  if (!kid) return { error: 'Player not found.' }

  session.kidId = kid.id
  session.kidName = kid.name
  await session.save()

  redirect('/home')
}

export async function updateTimezoneAction(formData: FormData) {
  const session = await getSession()
  if (!session.kidId) return { error: 'Not authenticated.' }

  const timezone = formData.get('timezone') as string
  if (!VALID_TIMEZONE_VALUES.has(timezone)) return { error: 'Invalid timezone.' }

  const supabase = await createServerClient()
  const { error } = await supabase
    .from('h2s_streaks')
    .upsert(
      { kid_id: session.kidId, timezone, updated_at: new Date().toISOString() },
      { onConflict: 'kid_id' },
    )

  if (error) return { error: error.message }

  revalidatePath('/home')
  revalidatePath('/settings')
  return { success: true }
}
