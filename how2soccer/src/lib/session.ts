import { getIronSession } from 'iron-session'
import { cookies } from 'next/headers'
import { SessionData, sessionOptions } from './session-config'

export async function getSession() {
  const cookieStore = await cookies()
  return getIronSession<SessionData>(cookieStore, sessionOptions)
}

export async function getCurrentParent() {
  const session = await getSession()
  if (!session.parentId) return null
  return { id: session.parentId, username: session.parentUsername! }
}

export async function getSessionKid() {
  const session = await getSession()
  if (!session.kidId) return null
  return { id: session.kidId, name: session.kidName! }
}
