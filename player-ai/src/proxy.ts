import { NextResponse, type NextRequest } from 'next/server';
import { getIronSession } from 'iron-session';
import type { SessionData, AdminSessionData } from '@/lib/session-config';
import { sessionOptions, adminSessionOptions } from '@/lib/session-config';

const PUBLIC_USER_PATHS = new Set(['/login', '/signup', '/onboarding']);

export async function proxy(request: NextRequest) {
  // Enforce HTTPS in production (Railway/Vercel set x-forwarded-proto)
  if (process.env.NODE_ENV === 'production') {
    const proto = request.headers.get('x-forwarded-proto');
    if (proto && proto !== 'https') {
      const url = request.nextUrl.clone();
      url.protocol = 'https:';
      return NextResponse.redirect(url, { status: 301 });
    }
  }

  const { pathname } = request.nextUrl;

  // Admin login is always public
  if (pathname === '/admin/login') {
    return NextResponse.next({ request });
  }

  // Admin routes require admin session
  if (pathname.startsWith('/admin')) {
    const res = NextResponse.next({ request });
    const adminSession = await getIronSession<AdminSessionData>(request, res, adminSessionOptions);
    if (!adminSession.isAdmin) {
      return NextResponse.redirect(new URL('/admin/login', request.url));
    }
    return res;
  }

  // OAuth callback and other auth API routes are always public
  if (pathname.startsWith('/api/auth/')) {
    return NextResponse.next({ request });
  }

  // Public user pages — bounce logged-in users away from login/signup
  if (PUBLIC_USER_PATHS.has(pathname)) {
    if (pathname === '/login' || pathname === '/signup') {
      const res = NextResponse.next({ request });
      const session = await getIronSession<SessionData>(request, res, sessionOptions);
      if (session.username) {
        return NextResponse.redirect(new URL('/', request.url));
      }
    }
    return NextResponse.next({ request });
  }

  // Everything else requires a valid user session
  const res = NextResponse.next({ request });
  const session = await getIronSession<SessionData>(request, res, sessionOptions);

  if (!session.username) {
    // API routes get a 401 JSON response; page routes get a login redirect
    if (pathname.startsWith('/api/')) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }
    const loginUrl = new URL('/login', request.url);
    if (pathname !== '/') {
      loginUrl.searchParams.set('next', pathname);
    }
    return NextResponse.redirect(loginUrl);
  }

  return res;
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon\\.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
};
