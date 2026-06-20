import type { SessionOptions } from 'iron-session';

export interface SessionData {
  username?: string;
}

export interface AdminSessionData {
  isAdmin?: boolean;
}

function requireSessionSecret(): string {
  const secret = process.env.SESSION_SECRET;
  if (!secret) {
    throw new Error(
      'SESSION_SECRET environment variable is not set. ' +
      'Generate one with: openssl rand -hex 32',
    );
  }
  if (secret.length < 32) {
    throw new Error(
      'SESSION_SECRET must be at least 32 characters. ' +
      'Generate a strong one with: openssl rand -hex 32',
    );
  }
  return secret;
}

export const sessionOptions: SessionOptions = {
  password: requireSessionSecret(),
  cookieName: 'player_ai_session',
  cookieOptions: {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 7, // 7 days
    path: '/',
  },
};

export const adminSessionOptions: SessionOptions = {
  password: requireSessionSecret(),
  cookieName: 'player_ai_admin_session',
  cookieOptions: {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 60 * 4, // 4 hours
    path: '/',
  },
};
