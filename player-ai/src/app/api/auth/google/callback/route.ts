import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { createServerClient } from '@/lib/supabase/server';
import { generateSalt } from '@/lib/auth';
import { getSession } from '@/lib/session';
import { randomBytes, createHash } from 'crypto';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const code = searchParams.get('code');
  const state = searchParams.get('state');

  const appUrl = process.env.NEXT_PUBLIC_APP_URL
    || (process.env.RAILWAY_PUBLIC_DOMAIN ? `https://${process.env.RAILWAY_PUBLIC_DOMAIN}` : 'http://localhost:3000');

  const cookieStore = await cookies();
  const savedState = cookieStore.get('google_oauth_state')?.value;
  cookieStore.delete('google_oauth_state');

  if (!state || !savedState || state !== savedState) {
    return NextResponse.redirect(new URL('/login?error=Sign-in+failed.+Please+try+again.', appUrl));
  }

  if (!code) {
    return NextResponse.redirect(new URL('/login?error=Sign-in+was+cancelled.', appUrl));
  }

  const clientId = process.env.GOOGLE_CLIENT_ID;
  const clientSecret = process.env.GOOGLE_CLIENT_SECRET;
  const redirectUri = `${appUrl}/api/auth/google/callback`;

  try {
    const tokenRes = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        code,
        client_id: clientId!,
        client_secret: clientSecret!,
        redirect_uri: redirectUri,
        grant_type: 'authorization_code',
      }),
    });

    if (!tokenRes.ok) {
      console.error('Failed to exchange authorization code:', await tokenRes.text());
      return NextResponse.redirect(new URL('/login?error=Google+sign-in+failed.+Please+try+again.', appUrl));
    }

    const tokenData = await tokenRes.json();
    const accessToken = tokenData.access_token;

    if (!accessToken) {
      return NextResponse.redirect(new URL('/login?error=Google+sign-in+failed.+Please+try+again.', appUrl));
    }

    const profileRes = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
      headers: { Authorization: `Bearer ${accessToken}` },
    });

    if (!profileRes.ok) {
      console.error('Failed to fetch Google user profile:', await profileRes.text());
      return NextResponse.redirect(new URL('/login?error=Could+not+retrieve+your+Google+profile.', appUrl));
    }

    const profile = await profileRes.json();
    const googleId = profile.sub;
    const email = typeof profile.email === 'string' ? profile.email : '';
    const name  = typeof profile.name  === 'string' ? profile.name  : '';

    if (!googleId) {
      return NextResponse.redirect(new URL('/login?error=Google+sign-in+failed.+Please+try+again.', appUrl));
    }

    const sha = createHash('sha256').update(googleId).digest('hex');
    const googleUsername = `g_${sha.substring(0, 15)}`;

    const supabase = await createServerClient();

    const { data: user, error: userError } = await supabase
      .from('users')
      .select('username')
      .eq('username', googleUsername)
      .maybeSingle();

    if (userError) {
      // Log the real error server-side; never expose DB details to the client
      console.error('Error checking user existence:', userError);
      return NextResponse.redirect(new URL('/login?error=Sign-in+failed.+Please+try+again.', appUrl));
    }

    if (!user) {
      const salt = generateSalt();
      const socialPasswordHash = `SOCIAL_GOOGLE_${randomBytes(16).toString('hex')}`;

      const { error: insertError } = await supabase
        .from('users')
        .insert({
          username: googleUsername,
          password_hash: socialPasswordHash,
          salt,
          email: email || null,
          created_at: new Date().toISOString(),
        });

      if (insertError) {
        console.error('Failed to provision Google user:', insertError);
        return NextResponse.redirect(new URL('/login?error=Could+not+create+account.+Please+try+again.', appUrl));
      }
    }

    const session = await getSession();
    session.username = googleUsername;
    await session.save();

    const { data: profileData, error: profileError } = await supabase
      .from('user_data')
      .select('data_value')
      .eq('username', googleUsername)
      .eq('data_key', 'athlete_profile')
      .maybeSingle();

    if (profileError) {
      console.error('Error fetching athlete profile:', profileError);
    }

    if (profileData?.data_value) {
      return NextResponse.redirect(new URL('/', appUrl));
    }

    // Pass Google profile data to onboarding using only safe, validated values
    const onboardingUrl = new URL('/onboarding', appUrl);
    if (email) onboardingUrl.searchParams.set('email', email);
    if (name)  onboardingUrl.searchParams.set('name',  name);
    return NextResponse.redirect(onboardingUrl.toString());

  } catch (err) {
    console.error('Unexpected error in Google OAuth callback:', err);
    return NextResponse.redirect(new URL('/login?error=An+unexpected+error+occurred.', appUrl));
  }
}
