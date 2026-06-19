import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { createServerClient } from '@/lib/supabase/server';
import { generateSalt } from '@/lib/auth';
import { getSession } from '@/lib/session';
import crypto from 'crypto';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const code = searchParams.get('code');
  const state = searchParams.get('state');

  const appUrl = process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000';

  const cookieStore = await cookies();
  const savedState = cookieStore.get('google_oauth_state')?.value;

  // Clear state cookie
  cookieStore.delete('google_oauth_state');

  if (!state || !savedState || state !== savedState) {
    return NextResponse.redirect(new URL('/login?error=Invalid state parameter (CSRF protection failed).', appUrl));
  }

  if (!code) {
    return NextResponse.redirect(new URL('/login?error=Authorization code not provided by Google.', appUrl));
  }

  const clientId = process.env.GOOGLE_CLIENT_ID;
  const clientSecret = process.env.GOOGLE_CLIENT_SECRET;
  const redirectUri = `${appUrl}/api/auth/google/callback`;

  try {
    // Exchange authorization code for token
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
      const errorText = await tokenRes.text();
      console.error('Failed to exchange authorization code:', errorText);
      return NextResponse.redirect(new URL('/login?error=Failed to exchange authorization code for access token.', appUrl));
    }

    const tokenData = await tokenRes.json();
    const accessToken = tokenData.access_token;

    if (!accessToken) {
      return NextResponse.redirect(new URL('/login?error=No access token returned by Google.', appUrl));
    }

    // Fetch user profile from Google UserInfo endpoint
    const profileRes = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
      headers: { Authorization: `Bearer ${accessToken}` },
    });

    if (!profileRes.ok) {
      console.error('Failed to fetch user profile:', await profileRes.text());
      return NextResponse.redirect(new URL('/login?error=Failed to fetch user profile from Google.', appUrl));
    }

    const profile = await profileRes.json();
    const googleId = profile.sub; // Google ID
    const email = profile.email;
    const name = profile.name || profile.given_name || '';

    if (!googleId) {
      return NextResponse.redirect(new URL('/login?error=Google account is missing unique identifier.', appUrl));
    }

    // Derive a unique and deterministic username
    const sha = crypto.createHash('sha256').update(googleId).digest('hex');
    const googleUsername = `g_${sha.substring(0, 15)}`; // e.g. g_7a8b9c0d1e2f3a4 (17 characters)

    const supabase = await createServerClient();

    // Check if the user already exists in the users table
    const { data: user, error: userError } = await supabase
      .from('users')
      .select('username')
      .eq('username', googleUsername)
      .maybeSingle();

    if (userError) {
      console.error('Error checking user existence:', userError);
      const detail = encodeURIComponent(userError.message ?? 'Unknown error');
      return NextResponse.redirect(
        new URL(`/login?error=Database error: ${detail}`, appUrl)
      );
    }

    if (!user) {
      // Create user
      const salt = generateSalt();
      const socialPasswordHash = `SOCIAL_GOOGLE_${crypto.randomBytes(16).toString('hex')}`;
      
      const { error: insertError } = await supabase
        .from('users')
        .insert({
          username: googleUsername,
          password_hash: socialPasswordHash,
          salt: salt,
          created_at: new Date().toISOString(),
        });

      if (insertError) {
        console.error('Failed to provision user:', insertError);
        const detail = encodeURIComponent(insertError.message ?? 'Unknown error');
        return NextResponse.redirect(
          new URL(`/login?error=Failed to provision account: ${detail}`, appUrl)
        );
      }
    }

    // Log the user in
    const session = await getSession();
    session.username = googleUsername;
    await session.save();

    // Check if user has completed onboarding (athlete_profile exists in user_data)
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
      // User has already completed onboarding
      return NextResponse.redirect(new URL('/', appUrl));
    } else {
      // Redirect new user to onboarding with pre-populated query parameters
      const onboardingUrl = new URL('/onboarding', appUrl);
      if (email) onboardingUrl.searchParams.set('email', email);
      if (name) onboardingUrl.searchParams.set('name', name);
      return NextResponse.redirect(onboardingUrl.toString());
    }

  } catch (err) {
    console.error('Unexpected error in Google OAuth callback:', err);
    return NextResponse.redirect(new URL('/login?error=An unexpected error occurred during Google Sign-in.', appUrl));
  }
}
