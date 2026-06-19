import { getIronSession } from 'iron-session';
import { cookies } from 'next/headers';
import { adminSessionOptions } from './session-config';
import type { AdminSessionData } from './session-config';

async function getAdminIronSession() {
  return getIronSession<AdminSessionData>(await cookies(), adminSessionOptions);
}

export async function getAdminSession(): Promise<boolean> {
  try {
    const session = await getAdminIronSession();
    return session.isAdmin === true;
  } catch {
    return false;
  }
}

export async function setAdminSession(): Promise<void> {
  const session = await getAdminIronSession();
  session.isAdmin = true;
  await session.save();
}

export async function clearAdminSession(): Promise<void> {
  const session = await getAdminIronSession();
  session.destroy();
}
