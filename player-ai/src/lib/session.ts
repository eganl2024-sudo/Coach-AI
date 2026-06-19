import { getIronSession } from 'iron-session';
import { cookies } from 'next/headers';
import { sessionOptions } from './session-config';

export type { SessionData } from './session-config';
export { sessionOptions } from './session-config';

export async function getSession() {
  return getIronSession<import('./session-config').SessionData>(await cookies(), sessionOptions);
}

export async function getCurrentUser(): Promise<string | null> {
  const session = await getSession();
  return session.username ?? null;
}
