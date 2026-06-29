import { NextRequest, NextResponse } from 'next/server'
import { createServerClient } from '@/lib/supabase/server'
import { getSession } from '@/lib/session'

export async function GET(req: NextRequest) {
  const token = req.nextUrl.searchParams.get('token')
  if (!token) return NextResponse.redirect(new URL('/login?error=invalid_token', req.url))

  const supabase = await createServerClient()

  const { data: parent } = await supabase
    .from('h2s_parents')
    .select('id, username, consent_token_exp')
    .eq('consent_token', token)
    .maybeSingle()

  if (!parent) return NextResponse.redirect(new URL('/login?error=invalid_token', req.url))

  if (parent.consent_token_exp && new Date(parent.consent_token_exp) < new Date()) {
    return NextResponse.redirect(new URL('/login?error=token_expired', req.url))
  }

  await supabase
    .from('h2s_parents')
    .update({ consent_given_at: new Date().toISOString(), consent_token: null, consent_token_exp: null })
    .eq('id', parent.id)

  const session = await getSession()
  session.parentId = parent.id
  session.parentUsername = parent.username
  await session.save()

  return NextResponse.redirect(new URL('/onboarding', req.url))
}
